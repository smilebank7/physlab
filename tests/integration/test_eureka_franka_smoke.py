from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from examples.eureka_franka import TimeoutLLM

ROOT = Path(__file__).resolve().parents[2]


def test_eureka_franka_mock_smoke(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "examples/eureka_franka.py",
            "--iterations=1",
            "--llm=mock",
            "--seed=42",
            "--run-id=smoke",
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "iteration | success_rate | wall_clock | reward_signature" in result.stdout
    assert (tmp_path / "runs" / "smoke" / "SUMMARY.md").exists()
    assert (tmp_path / "runs" / "smoke" / "BEST_REWARD.py").exists()


def test_eureka_franka_missing_opencode_reports_path_error(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "examples/eureka_franka.py",
            "--iterations=1",
            "--llm=opencode",
            "--seed=42",
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
        cwd=ROOT,
        env={"PATH": "/nonexistent"},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "opencode not found on PATH" in result.stderr


def test_timeout_wrapper_passes_timeout_to_live_llm() -> None:
    class DummyLLM:
        def __init__(self) -> None:
            self.kwargs: dict[str, object] = {}

        def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
            del prompt, system
            self.kwargs = kwargs
            return "ok"

        def name(self) -> str:
            return "dummy"

    dummy = DummyLLM()
    wrapped = TimeoutLLM(dummy, timeout_s=600.0)

    assert wrapped.complete("prompt", seed=42) == "ok"
    assert dummy.kwargs["timeout"] == 600.0
    assert dummy.kwargs["seed"] == 42
