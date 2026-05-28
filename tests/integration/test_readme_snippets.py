from __future__ import annotations

import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
TUTORIAL = ROOT / "docs" / "tutorial-eureka-franka.md"


def test_readme_bash_snippets_execute() -> None:
    failures = run_document_snippets(README, languages=("bash",))
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

    failures = run_document_snippets(broken, languages=("bash",))

    assert len(failures) == 1
    assert "bash block 1" in failures[0]
    assert "returncode=7" in failures[0]


def test_tutorial_snippets() -> None:
    failures = run_document_snippets(TUTORIAL, languages=("bash", "python"))
    assert failures == []


def test_tutorial_length_matches_reading_time_target() -> None:
    words = re.findall(r"\b[\w'-]+\b", TUTORIAL.read_text(encoding="utf-8"))
    assert 1500 <= len(words) <= 2500


def test_tutorial_snippet_executor_cites_stale_python_import(tmp_path: Path) -> None:
    broken = tmp_path / "tutorial.md"
    broken.write_text(
        "# Broken\n\n```python\nimport physlab.removed_module\n```\n",
        encoding="utf-8",
    )

    failures = run_document_snippets(broken, languages=("python",))

    assert len(failures) == 1
    assert "python block 1" in failures[0]
    assert "ModuleNotFoundError" in failures[0]


def run_document_snippets(path: Path, *, languages: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for language in languages:
        for index, block in enumerate(_fenced_blocks(text, language), start=1):
            result = _run_block(language, block)
            if result.returncode != 0:
                failures.append(
                    f"{language} block {index} returncode={result.returncode}\n"
                    f"stdout={result.stdout}\nstderr={result.stderr}\nblock=\n{block}"
                )
    return failures


def _fenced_blocks(text: str, language: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(rf"```{re.escape(language)}\n(.*?)\n```", text, re.S)
    ]


def _run_block(language: str, block: str) -> subprocess.CompletedProcess[str]:
    match language:
        case "bash":
            args = ["bash", "-euo", "pipefail", "-c", block]
        case "python":
            args = ["uv", "run", "python", "-c", block]
        case _:
            raise ValueError(f"unsupported snippet language {language!r}")
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
