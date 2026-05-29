"""Check the external release prerequisites for v0.1 publishing."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

REQUIRED_ENVIRONMENTS = frozenset({"pypi", "npm"})
MANUAL_PUBLISH_CONDITION = (
    "if: github.event_name == 'workflow_dispatch' && startsWith(github.ref, 'refs/tags/v')"
)
ROOT = Path(__file__).resolve().parents[1]


class ReleaseReadinessError(ValueError):
    """Raised when a release prerequisite is missing."""


def check_release_workflow(text: str) -> None:
    if "NODE_AUTH_TOKEN" in text:
        raise ReleaseReadinessError("release workflow must not use NODE_AUTH_TOKEN")
    if "--provenance" in text:
        raise ReleaseReadinessError("npm trusted publishing must not use --provenance")
    required_snippets = (
        "workflow_dispatch:",
        "id-token: write",
        'node-version: "24"',
    )
    missing = [snippet for snippet in required_snippets if snippet not in text]
    if text.count(MANUAL_PUBLISH_CONDITION) < 2:
        missing.append(MANUAL_PUBLISH_CONDITION)
    missing.extend(
        f"environment: {name}" for name in REQUIRED_ENVIRONMENTS if not _has_environment(text, name)
    )
    if missing:
        raise ReleaseReadinessError(f"release workflow missing: {missing}")


def check_gpg_ready(signing_key: str, secret_keys: str) -> None:
    key = signing_key.strip()
    if not key:
        raise ReleaseReadinessError(
            "git user.signingkey is not configured; secret key cannot be verified"
        )
    compact_secret_keys = secret_keys.replace(" ", "")
    if key.replace(" ", "") not in compact_secret_keys:
        raise ReleaseReadinessError(f"GPG secret key for git user.signingkey {key!r} not found")


def parse_approved_environment_names(payload: str) -> set[str]:
    data = json.loads(payload)
    environments = data.get("environments")
    if not isinstance(environments, list):
        raise ReleaseReadinessError("GitHub environments payload missing environments list")
    names: set[str] = set()
    for environment in environments:
        if (
            isinstance(environment, dict)
            and isinstance(environment.get("name"), str)
            and _has_required_reviewers(environment)
        ):
            names.add(environment["name"])
    return names


def check_github_environments(names: set[str]) -> None:
    missing = sorted(REQUIRED_ENVIRONMENTS.difference(names))
    if missing:
        raise ReleaseReadinessError(f"GitHub release environments missing: {missing}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="smilebank7/physlab", help="GitHub owner/repo")
    args = parser.parse_args(argv)

    errors: list[str] = []
    workflow = ROOT / ".github" / "workflows" / "release.yml"
    _collect(errors, "release workflow", lambda: check_release_workflow(workflow.read_text()))
    _collect(errors, "GPG signing", lambda: check_gpg_ready(_git_signing_key(), _gpg_secret_keys()))
    _collect(
        errors,
        "GitHub environments",
        lambda: check_github_environments(
            parse_approved_environment_names(_github_environments(args.repo))
        ),
    )

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("release readiness ok")
    return 0


def _collect(errors: list[str], label: str, check: Callable[[], None]) -> None:
    try:
        check()
    except (OSError, ReleaseReadinessError, subprocess.CalledProcessError) as exc:
        errors.append(f"{label}: {exc}")


def _git_signing_key() -> str:
    result = subprocess.run(
        ["git", "config", "--get", "user.signingkey"],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return result.stdout.strip()


def _has_environment(text: str, name: str) -> bool:
    return f"environment: {name}" in text or f"name: {name}" in text


def _has_required_reviewers(environment: dict[object, object]) -> bool:
    protection_rules = environment.get("protection_rules")
    if not isinstance(protection_rules, list):
        return False
    return any(
        isinstance(rule, dict) and rule.get("type") == "required_reviewers"
        for rule in protection_rules
    )


def _gpg_secret_keys() -> str:
    if shutil.which("gpg") is None:
        raise ReleaseReadinessError("gpg executable not found")
    result = subprocess.run(
        ["gpg", "--list-secret-keys", "--keyid-format=long"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _github_environments(repo: str) -> str:
    if shutil.which("gh") is None:
        raise ReleaseReadinessError("gh executable not found")
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/environments"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return result.stdout


if __name__ == "__main__":
    raise SystemExit(main())
