from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

from physlab import make
from physlab.backends.mujoco import MuJoCoBackend
from physlab.orchestrator.controller import IterationController, scripted_components
from physlab.orchestrator.reward_gen import generate_reward
from physlab.orchestrator.store import RunStore
from physlab.tasks.cartpole import CartpoleTask

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "physlab"
DOC = ROOT / "docs" / "extension-points.md"
PLUGIN = ROOT / "examples" / "plugins" / "hello_task"

FUTURE_MODULE_NAMES = {
    "drake.py",
    "env_generator.py",
    "gensim.py",
    "plugin_manager.py",
    "plugins.py",
    "robogen.py",
    "serving.py",
    "taichi.py",
    "vla.py",
}
FUTURE_CLASS_NAMES = {
    "DrakeBackend",
    "EnvGenerator",
    "GenSim",
    "PluginManager",
    "RoboGen",
    "TaichiBackend",
    "VLAServer",
}


def test_extension_points_doc_has_required_sections() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "# Extension Points" in text
    assert "## Current Extension Points" in text
    assert "## Future Roadmap" in text
    assert "## Design Principles" in text
    assert "Coverage Map" in text


def test_current_task_extension_requires_explicit_import() -> None:
    script = f"""
import sys
sys.path.insert(0, {str(PLUGIN)!r})
from physlab import list_tasks, make
assert "hello_task" not in list_tasks()
import hello_task
assert "hello_task" in list_tasks()
env = make("hello_task")
obs, info = env.reset(seed=0)
assert obs.shape == env.observation_space.shape
env.close()
print("OK")
"""

    result = _python(script)

    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_current_backend_extension_accepts_backend_instance() -> None:
    class UserBackend(MuJoCoBackend):
        def name(self) -> str:
            return "user-mujoco"

    env = make("cartpole", backend=UserBackend(), seed=0)
    try:
        _, info = env.reset(seed=0)
    finally:
        env.close()

    assert info["backend"] == "user-mujoco"


def test_current_llm_client_extension_runs_controller(tmp_path: Path) -> None:
    class LocalClient:
        def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
            del prompt, system, kwargs
            return "Reflection for local client."

        def name(self) -> str:
            return "local"

    reward_generator, evaluator = scripted_components(
        [
            {
                "code": "def reward_fn(obs, action, info):\n    return 0.0\n",
                "success_rate": 0.5,
                "mean_episode_reward": 0.5,
            }
        ]
    )
    controller = IterationController(
        task=CartpoleTask(),
        llm=LocalClient(),
        store=RunStore(tmp_path),
        iterations=1,
        reward_generator=reward_generator,
        evaluator=evaluator,
        train_steps=16,
        seed=7,
    )

    result = controller.run(run_id="extension-llm")

    assert result.best_success_rate == 0.5
    assert result.run.config["llm"] == "local"


def test_current_reward_generation_accepts_code_string() -> None:
    class RewardClient:
        def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
            del prompt, system, kwargs
            return "```python\ndef reward_fn(obs, action, info):\n    return 0.0\n```"

        def name(self) -> str:
            return "reward-client"

    reward = generate_reward(CartpoleTask(), RewardClient(), prior_attempts=[], ctx_seed=3)

    assert reward.status == "ok"
    assert "reward_fn" in reward.code


def test_no_policy_server_or_future_extension_impls_exist() -> None:
    violations = _future_class_violations() + _future_module_violations()

    assert violations == []


def test_no_auto_discovery_or_entry_points_walk_in_src() -> None:
    needles = ("entry_points", "importlib.metadata", "from importlib import metadata")
    violations = [
        str(path.relative_to(ROOT))
        for path in SRC.rglob("*.py")
        if any(needle in path.read_text(encoding="utf-8") for needle in needles)
    ]

    assert violations == []


def test_extension_points_doc_python_snippets_execute() -> None:
    failures = []
    for index, block in enumerate(_python_blocks(DOC.read_text(encoding="utf-8")), start=1):
        result = _python(block)
        if result.returncode != 0:
            failures.append(
                f"python block {index} returncode={result.returncode}\n"
                f"stdout={result.stdout}\nstderr={result.stderr}\nblock=\n{block}"
            )

    assert failures == []


def _future_class_violations() -> list[str]:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and _is_forbidden_future_class(path, node):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:{node.name}")
    return violations


def _future_module_violations() -> list[str]:
    return [
        str(path.relative_to(ROOT))
        for path in SRC.rglob("*.py")
        if path.name in FUTURE_MODULE_NAMES
    ]


def _is_forbidden_future_class(path: Path, node: ast.ClassDef) -> bool:
    if node.name == "PolicyServer":
        bases = {_base_name(base) for base in node.bases}
        return path.name != "protocols.py" or "Protocol" not in bases
    return node.name in FUTURE_CLASS_NAMES


def _base_name(base: ast.expr) -> str:
    match base:
        case ast.Name(id=name):
            return name
        case ast.Attribute(attr=name):
            return name
        case _:
            return ""


def _python_blocks(text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"```python\n(.*?)\n```", text, re.S)
    ]


def _python(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
