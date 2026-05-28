from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_hardware_matrix import HardwareMatrixError, check_workflow

ROOT = Path(__file__).resolve().parents[2]


def test_ci_workflow_declares_hardware_freedom_gate() -> None:
    check_workflow((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))


def test_hardware_freedom_gate_rejects_missing_os() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    broken = workflow.replace("macos-15, ", "")

    with pytest.raises(HardwareMatrixError, match="macos-15"):
        check_workflow(broken)
