"""Subprocess reward evaluator for generated reward functions."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field

from physlab.orchestrator.reward_gen import RewardCode
from physlab.protocols import Task

_ALLOWED_IMPORT_ROOTS = frozenset({"numpy", "math", "physlab"})


@dataclass(frozen=True)
class EvalResult:
    """Structured result from evaluating generated reward code."""

    success_rate: float
    mean_episode_reward: float
    train_steps_used: int
    wall_clock_s: float
    error: str | None = None
    training_curve: list[float] = field(default_factory=list)
    episode_lengths: list[int] = field(default_factory=list)
    stderr: str = ""


def evaluate_reward(
    reward_code: RewardCode,
    task: Task,
    num_rollouts: int,
    train_steps: int,
    seed: int,
    timeout_s: float = 300.0,
) -> EvalResult:
    """Evaluate generated reward code in an isolated Python subprocess."""

    start = time.perf_counter()
    if reward_code.status != "ok":
        return _error_result(reward_code.status, start)
    validation_error = _validate_reward_code(reward_code.code)
    if validation_error is not None:
        return _error_result(validation_error, start)
    if num_rollouts <= 0:
        raise ValueError("num_rollouts must be positive")
    if train_steps <= 0:
        raise ValueError("train_steps must be positive")

    payload = {
        "code": reward_code.code,
        "task_module": type(task).__module__,
        "task_qualname": type(task).__qualname__,
        "task_name": task.name,
        "num_rollouts": num_rollouts,
        "train_steps": train_steps,
        "seed": seed,
    }
    with tempfile.TemporaryDirectory(prefix="physlab-eval-") as tmp:
        payload["run_dir"] = tmp
        try:
            completed = subprocess.run(
                [sys.executable, "-c", _SANDBOX_SCRIPT],
                input=json.dumps(payload, sort_keys=True),
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            return EvalResult(
                success_rate=0.0,
                mean_episode_reward=0.0,
                train_steps_used=0,
                wall_clock_s=time.perf_counter() - start,
                error="timeout",
                stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            )

    result = _parse_child_result(completed.stdout, completed.stderr, completed.returncode)
    return EvalResult(
        success_rate=result.success_rate,
        mean_episode_reward=result.mean_episode_reward,
        train_steps_used=result.train_steps_used,
        wall_clock_s=time.perf_counter() - start,
        error=result.error,
        training_curve=result.training_curve,
        episode_lengths=result.episode_lengths,
        stderr=result.stderr,
    )


def _validate_reward_code(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "parse_error"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _import_root(alias.name) not in _ALLOWED_IMPORT_ROOTS:
                    return "forbidden_import"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level != 0 or _import_root(module) not in _ALLOWED_IMPORT_ROOTS:
                return "forbidden_import"
    has_reward_fn = any(
        isinstance(node, ast.FunctionDef) and node.name == "reward_fn" for node in tree.body
    )
    if not has_reward_fn:
        return "parse_error"
    return None


def _parse_child_result(stdout: str, stderr: str, returncode: int) -> EvalResult:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        return EvalResult(
            success_rate=0.0,
            mean_episode_reward=0.0,
            train_steps_used=0,
            wall_clock_s=0.0,
            error="crash",
            stderr=stderr,
        )
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError:
        return EvalResult(
            success_rate=0.0,
            mean_episode_reward=0.0,
            train_steps_used=0,
            wall_clock_s=0.0,
            error="crash",
            stderr=stderr or stdout,
        )
    error = payload.get("error")
    if returncode != 0 and error is None:
        error = "crash"
    return EvalResult(
        success_rate=_float(payload.get("success_rate", 0.0)),
        mean_episode_reward=_float(payload.get("mean_episode_reward", 0.0)),
        train_steps_used=int(payload.get("train_steps_used", 0)),
        wall_clock_s=0.0,
        error=str(error) if error is not None else None,
        training_curve=_float_list(payload.get("training_curve", [])),
        episode_lengths=_int_list(payload.get("episode_lengths", [])),
        stderr=stderr,
    )


def _error_result(error: str, start: float) -> EvalResult:
    return EvalResult(
        success_rate=0.0,
        mean_episode_reward=0.0,
        train_steps_used=0,
        wall_clock_s=time.perf_counter() - start,
        error=error,
    )


def _import_root(module: str) -> str:
    return module.split(".", maxsplit=1)[0]


def _float(value: object) -> float:
    return float(value) if isinstance(value, int | float | str) else 0.0


def _float_list(value: object) -> list[float]:
    if not isinstance(value, list):
        return []
    return [_float(item) for item in value]


def _int_list(value: object) -> list[int]:
    if not isinstance(value, list):
        return []
    return [int(item) for item in value if isinstance(item, int | float | str)]


_SANDBOX_SCRIPT = r"""
from __future__ import annotations

import ast
import importlib
import json
import math
import traceback
from pathlib import Path

import numpy as np

from physlab.registry import register_task
from physlab.training.ppo import PPOConfig, train

ALLOWED_IMPORT_ROOTS = frozenset({"numpy", "math", "physlab"})


def main() -> int:
    payload = json.loads(sys_stdin())
    code = str(payload["code"])
    validation_error = validate_reward_code(code)
    if validation_error is not None:
        print_json({"error": validation_error})
        return 0

    namespace = load_reward_namespace(code)
    reward_fn = namespace.get("reward_fn")
    if not callable(reward_fn):
        print_json({"error": "parse_error"})
        return 0

    task_cls = resolve_class(str(payload["task_module"]), str(payload["task_qualname"]))
    base_for_specs = task_cls()
    action_shape = getattr(base_for_specs, "action_space").shape
    obs_shape = getattr(base_for_specs, "observation_space").shape
    preflight = reward_fn(np.zeros(obs_shape), np.zeros(action_shape), {"step_count": 0})
    if not np.isfinite(float(preflight)):
        print_json({"error": "nan_reward"})
        return 0

    task_name = str(payload["task_name"])

    class GeneratedRewardTask:
        name = task_name

        def __init__(self) -> None:
            self._base = task_cls()

        def __getattr__(self, name: str):
            return getattr(self._base, name)

        def reward(self, observation, action, info) -> float:
            value = reward_fn(np.asarray(observation), np.asarray(action), dict(info))
            reward = float(value)
            if not np.isfinite(reward):
                raise ValueError("nan_reward")
            return reward

    register_task(task_name, GeneratedRewardTask)
    train_steps = int(payload["train_steps"])
    run_dir = Path(str(payload["run_dir"]))
    try:
        result = train(
            PPOConfig(
                task=task_name,
                total_steps=train_steps,
                n_steps=min(2048, train_steps),
                eval_every=max(1, train_steps),
                eval_episodes=int(payload["num_rollouts"]),
                seed=int(payload["seed"]),
                device="cpu",
                run_dir=run_dir,
                minibatch_size=min(64, max(1, train_steps)),
            )
        )
    except Exception as exc:
        error = "nan_reward" if "nan_reward" in f"{exc}\n{traceback.format_exc()}" else "crash"
        print_json({"error": error, "stderr": traceback.format_exc()})
        return 0

    curve = read_curve(result.log_path)
    print_json(
        {
            "error": None,
            "success_rate": result.final_success_rate,
            "mean_episode_reward": float(np.mean(curve)) if curve else 0.0,
            "train_steps_used": result.total_steps,
            "training_curve": curve[-20:],
            "episode_lengths": [],
        }
    )
    return 0


def validate_reward_code(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "parse_error"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if import_root(alias.name) not in ALLOWED_IMPORT_ROOTS:
                    return "forbidden_import"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level != 0 or import_root(module) not in ALLOWED_IMPORT_ROOTS:
                return "forbidden_import"
    has_reward_fn = any(
        isinstance(node, ast.FunctionDef) and node.name == "reward_fn" for node in tree.body
    )
    if not has_reward_fn:
        return "parse_error"
    return None


def load_reward_namespace(code: str) -> dict[str, object]:
    safe_builtins = {
        "Exception": Exception,
        "TypeError": TypeError,
        "ValueError": ValueError,
        "__import__": safe_import,
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "getattr": getattr,
        "hasattr": hasattr,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "range": range,
        "repr": repr,
        "set": set,
        "slice": slice,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }
    namespace = {"__builtins__": safe_builtins, "math": math, "np": np}
    exec(compile(code, "<reward_fn>", "exec"), namespace)
    return namespace


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    del globals, locals
    if level != 0 or import_root(str(name)) not in ALLOWED_IMPORT_ROOTS:
        raise ImportError(f"forbidden import: {name}")
    return __import__(name, globals=None, locals=None, fromlist=fromlist, level=level)


def resolve_class(module_name: str, qualname: str):
    value = importlib.import_module(module_name)
    for part in qualname.split("."):
        value = getattr(value, part)
    return value


def read_curve(path: Path) -> list[float]:
    curve = []
    if not path.exists():
        return curve
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        value = record.get("eval/success_rate", 0.0)
        curve.append(float(value))
    return curve


def import_root(module: str) -> str:
    return module.split(".", maxsplit=1)[0]


def print_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True), flush=True)


def sys_stdin() -> str:
    import sys

    return sys.stdin.read()


raise SystemExit(main())
"""


__all__ = ["EvalResult", "evaluate_reward"]
