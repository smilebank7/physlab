from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "examples" / "plugins" / "hello_task"
SOURCE = PLUGIN / "hello_task.py"
SRC = ROOT / "src" / "physlab"


def test_plugin_source_is_50_lines_or_less() -> None:
    assert len(SOURCE.read_text(encoding="utf-8").splitlines()) <= 50


def test_plugin_depends_on_release_distribution_name() -> None:
    metadata = tomllib.loads((PLUGIN / "pyproject.toml").read_text(encoding="utf-8"))

    assert metadata["project"]["dependencies"] == ["physlab-mac"]


def test_explicit_import_registers_plugin_task() -> None:
    _install_plugin()
    script = """
from physlab import list_tasks
assert 'hello_task' not in list_tasks()
import hello_task
assert 'hello_task' in list_tasks()
print('OK')
"""

    result = _python(script)

    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_make_plugin_task_after_explicit_import() -> None:
    _install_plugin()
    script = """
import hello_task
from physlab import make
env = make('hello_task')
obs, info = env.reset(seed=0)
for _ in range(10):
    obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
env.close()
print('OK')
"""

    result = _python(script)

    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_plugin_is_not_auto_discovered_without_import() -> None:
    _install_plugin()
    result = _python(
        "from physlab import list_tasks; assert 'hello_task' not in list_tasks(); print('OK')"
    )

    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_no_entry_points_machinery_in_src() -> None:
    matches = [
        path
        for path in SRC.rglob("*.py")
        if "entry_points" in path.read_text(encoding="utf-8")
    ]

    assert matches == []


def _install_plugin() -> None:
    subprocess.run(["uv", "pip", "install", "-e", str(PLUGIN)], cwd=ROOT, check=True)


def _python(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
