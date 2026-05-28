from __future__ import annotations

from pathlib import Path

from tools import check_licenses


def test_project_license_requires_mit_text(tmp_path: Path) -> None:
    (tmp_path / "LICENSE").write_text("Apache License\n", encoding="utf-8")

    failures = check_licenses.check_project_license(tmp_path)

    assert failures
    assert "LICENSE must be MIT" in failures[0]


def test_notice_requires_core_attributions(tmp_path: Path) -> None:
    (tmp_path / "NOTICE").write_text("MuJoCo\n", encoding="utf-8")

    failures = check_licenses.check_notice(tmp_path)

    assert "NOTICE missing required attribution: DeepMind Control Suite" in failures
    assert "NOTICE missing required attribution: BSD-3-Clause" in failures


def test_gpl_fixture_is_rejected() -> None:
    packages = check_licenses.packages_from_fixture(Path("tests/fixtures/gpl_violator.json"))

    violations = check_licenses.find_violations(packages)

    assert violations[0].name == "bad-copyleft-lib"


def test_markdown_summary_lists_sources() -> None:
    packages = [
        check_licenses.PackageLicense("numpy", "BSD License", "python"),
        check_licenses.PackageLicense("zod", "MIT", "npm"),
    ]

    summary = check_licenses.render_summary(packages, policy_failures=[])

    assert "| Source | Package | License | Status |" in summary
    assert "| python | numpy | BSD License | ok |" in summary
    assert "| npm | zod | MIT | ok |" in summary
