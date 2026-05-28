from __future__ import annotations

import importlib
import pkgutil
import subprocess
import sys
from pathlib import Path

import physlab

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_GUI_MODULES = ("tkinter", "matplotlib.pyplot", "mujoco.viewer")


def forbidden_loaded_modules() -> list[str]:
    return [name for name in FORBIDDEN_GUI_MODULES if name in sys.modules]


def test_importing_physlab_modules_does_not_pull_gui_modules() -> None:
    for module in pkgutil.walk_packages(physlab.__path__, prefix="physlab."):
        importlib.import_module(module.name)

    assert forbidden_loaded_modules() == []


def test_hello_cartpole_headless_without_display() -> None:
    result = _run_without_display(["examples/hello_cartpole.py", "--headless", "--seed=42"])

    assert result.returncode == 0, result.stderr
    assert "episode_reward=" in result.stdout
    assert "DISPLAY" not in result.stdout


def test_anchor_demo_headless_cached_without_display(tmp_path: Path) -> None:
    result = _run_without_display(
        [
            "examples/eureka_franka.py",
            "--headless",
            "--use-cache",
            "--iterations=1",
            "--seed=42",
            "--run-id=headless-anchor",
            "--runs-dir",
            str(tmp_path / "runs"),
        ]
    )

    assert result.returncode == 0, result.stderr
    assert "best_success_rate=1.0000" in result.stdout


def test_forbidden_module_detector_catches_injected_viewer() -> None:
    sys.modules["mujoco.viewer"] = object()  # type: ignore[assignment]
    try:
        assert forbidden_loaded_modules() == ["mujoco.viewer"]
    finally:
        sys.modules.pop("mujoco.viewer", None)


def _run_without_display(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in __import__("os").environ.items() if key != "DISPLAY"}
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
