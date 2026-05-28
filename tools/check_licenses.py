#!/usr/bin/env python3
"""Audit Python and npm dependency licenses.

Allowed SPDX families: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause,
BSD-3-Clause-Clear, MPL-2.0, Python-2.0, PSF-2.0, ISC, Unlicense, CC0-1.0.

Rejected families: GPL, AGPL, LGPL, proprietary, unknown, and unlicensed
packages. The checker delegates dependency discovery to pip-licenses and
license-checker-rseidelsohn/license-checker, then applies this policy.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER = ROOT / "mcp-server"

ALLOWED_MARKERS = (
    "mit",
    "apache",
    "bsd",
    "mpl-2.0",
    "mozilla public license 2.0",
    "python software foundation",
    "python-2.0",
    "psf-2.0",
    "isc",
    "unlicense",
    "cc0",
)
REJECTED_MARKERS = (
    "agpl",
    "lgpl",
    "gpl",
    "proprietary",
    "commercial",
    "unknown",
    "unlicensed",
)


@dataclass(frozen=True)
class PackageLicense:
    name: str
    license: str
    source: str


def run_json(command: list[str], cwd: Path = ROOT) -> Any:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def normalize(value: object) -> str:
    if isinstance(value, list):
        return " OR ".join(str(item) for item in value)
    return str(value or "").strip()


def is_allowed(license_text: str) -> bool:
    normalized = license_text.lower()
    if not normalized:
        return False
    if any(marker in normalized for marker in REJECTED_MARKERS):
        return False
    return any(marker in normalized for marker in ALLOWED_MARKERS)


def package_from_pip(record: dict[str, Any], source: str) -> PackageLicense:
    return PackageLicense(
        name=normalize(record.get("Name") or record.get("name")),
        license=normalize(record.get("License") or record.get("license")),
        source=source,
    )


def packages_from_fixture(path: Path) -> list[PackageLicense]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [package_from_pip(record, "fixture") for record in raw]
    if isinstance(raw, dict):
        return [
            PackageLicense(
                name=name,
                license=normalize(record.get("licenses") or record.get("license")),
                source="fixture",
            )
            for name, record in raw.items()
        ]
    raise ValueError("fixture must be a pip-licenses list or license-checker object")


def scan_python() -> list[PackageLicense]:
    raw = run_json(["pip-licenses", "--format=json"])
    return [package_from_pip(record, "python") for record in raw]


def license_checker_command() -> list[str]:
    binary = shutil.which("license-checker-rseidelsohn") or shutil.which("license-checker")
    if binary is None:
        raise RuntimeError("license-checker-rseidelsohn or license-checker not found on PATH")
    return [binary, "--json", "--production", "--start", str(MCP_SERVER)]


def scan_npm() -> list[PackageLicense]:
    raw = run_json(license_checker_command())
    packages: list[PackageLicense] = []
    for name, record in raw.items():
        if record.get("private") is True:
            continue
        packages.append(
            PackageLicense(
                name=name,
                license=normalize(record.get("licenses") or record.get("license")),
                source="npm",
            )
        )
    return packages


def find_violations(packages: list[PackageLicense]) -> list[PackageLicense]:
    return [package for package in packages if not is_allowed(package.license)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit dependency licenses.")
    parser.add_argument("--fixture", type=Path, help="Read dependency records from JSON fixture")
    args = parser.parse_args()

    packages = packages_from_fixture(args.fixture) if args.fixture else scan_python() + scan_npm()
    violations = find_violations(packages)
    if violations:
        for package in violations:
            print(
                f"{package.source}:{package.name}: rejected license {package.license}",
                file=sys.stderr,
            )
        return 1

    print(f"Scanned {len(packages)} dependencies; 0 violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
