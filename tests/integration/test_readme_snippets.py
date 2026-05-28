from __future__ import annotations

import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"


def test_readme_bash_snippets_execute() -> None:
    failures = run_readme_bash_snippets(README)
    assert failures == []


def test_readme_badges_resolve() -> None:
    text = README.read_text(encoding="utf-8")
    badge_urls = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", text)
    assert badge_urls
    for url in badge_urls:
        request = urllib.request.Request(url, headers={"User-Agent": "physlab-ci"})
        with urllib.request.urlopen(request, timeout=10) as response:
            assert response.status != 404


def test_readme_mentions_deferred_features_only_in_roadmap() -> None:
    before_roadmap = README.read_text(encoding="utf-8").split("## Roadmap", maxsplit=1)[0]
    deferred_terms = ("Drake", "Taichi", "VLA", "USD", "plugin machinery", "multi-LLM")

    assert not [term for term in deferred_terms if term in before_roadmap]


def test_readme_snippet_executor_cites_broken_block(tmp_path: Path) -> None:
    broken = tmp_path / "README.md"
    broken.write_text(
        "# Broken\n\n```bash\npython -c \"raise SystemExit(7)\"\n```\n",
        encoding="utf-8",
    )

    failures = run_readme_bash_snippets(broken)

    assert len(failures) == 1
    assert "bash block 1" in failures[0]
    assert "returncode=7" in failures[0]


def run_readme_bash_snippets(path: Path) -> list[str]:
    failures: list[str] = []
    for index, block in enumerate(_bash_blocks(path.read_text(encoding="utf-8")), start=1):
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", block],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            failures.append(
                f"bash block {index} returncode={result.returncode}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}\nblock=\n{block}"
            )
    return failures


def _bash_blocks(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"```bash\n(.*?)\n```", text, re.S)]
