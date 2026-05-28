from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cold_start_script_quick_mode_records_timing(tmp_path: Path) -> None:
    evidence = tmp_path / "cold-start.txt"
    result = subprocess.run(
        [
            "bash",
            "scripts/cold_start_bench.sh",
            "--quick",
            "--threshold",
            "300",
            "--evidence",
            str(evidence),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    text = evidence.read_text(encoding="utf-8")
    assert "mode=quick" in text
    assert "total_seconds=" in text
    assert "result=ok" in text


def test_cold_start_threshold_regression_fails(tmp_path: Path) -> None:
    evidence = tmp_path / "cold-start-fail.txt"
    result = subprocess.run(
        [
            "bash",
            "scripts/cold_start_bench.sh",
            "--quick",
            "--threshold",
            "-1",
            "--evidence",
            str(evidence),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "cold start exceeded threshold" in result.stderr
    assert "result=fail" in evidence.read_text(encoding="utf-8")
