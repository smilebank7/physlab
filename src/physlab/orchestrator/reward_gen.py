"""Eureka-style reward prompt construction and AST-validated code extraction."""

from __future__ import annotations

import ast
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from physlab.llm.client import LLMClient
from physlab.protocols import Task

RewardStatus = Literal["ok", "parse_error", "forbidden_import"]

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "reward_gen.md"
_PYTHON_BLOCK = re.compile(r"```(?:python|py)\s*\n(?P<code>.*?)```", re.DOTALL | re.IGNORECASE)
_ALLOWED_IMPORT_ROOTS = frozenset({"numpy", "math", "physlab"})
_SIGNATURE = "reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float"


@dataclass(frozen=True)
class Attempt:
    """Prior reward attempt summary used as prompt context."""

    eval_metrics: dict[str, float]
    reflection: str


@dataclass(frozen=True)
class RewardCode:
    """Parsed reward code plus validation status."""

    code: str
    signature: str
    hash: str
    status: RewardStatus
    raw_response: str = ""


def generate_reward(
    task: Task,
    llm: LLMClient,
    prior_attempts: list[Attempt],
    ctx_seed: int,
) -> RewardCode:
    """Ask an LLM for reward code and validate only syntax/import safety."""

    prompt = build_reward_prompt(task, prior_attempts, ctx_seed)
    response = llm.complete(prompt, seed=ctx_seed)
    code = _extract_python(response)
    if code is None:
        return _reward_code(response, "parse_error", raw_response=response)

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _reward_code(code, "parse_error", raw_response=response)

    if _has_forbidden_import(tree):
        return _reward_code(code, "forbidden_import", raw_response=response)
    if not _has_reward_fn(tree):
        return _reward_code(code, "parse_error", raw_response=response)
    return _reward_code(code, "ok", raw_response=response)


def build_reward_prompt(task: Task, prior_attempts: list[Attempt], ctx_seed: int) -> str:
    """Render the reward-generation prompt for a task and previous attempts."""

    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(
        task_description=_task_description(task),
        reward_signature=task.reward_signature(),
        obs_spec=_spec_text(task, "observation_space"),
        action_spec=_spec_text(task, "action_space"),
        prior_attempts=_attempts_text(prior_attempts),
        ctx_seed=ctx_seed,
    )


def _extract_python(response: str) -> str | None:
    match = _PYTHON_BLOCK.search(response)
    if match is None:
        return None
    code = match.group("code").strip()
    return code or None


def _has_forbidden_import(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(_import_root(alias.name) not in _ALLOWED_IMPORT_ROOTS for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level != 0 or _import_root(module) not in _ALLOWED_IMPORT_ROOTS:
                return True
    return False


def _has_reward_fn(tree: ast.Module) -> bool:
    return any(isinstance(node, ast.FunctionDef) and node.name == "reward_fn" for node in tree.body)


def _import_root(module: str) -> str:
    return module.split(".", maxsplit=1)[0]


def _reward_code(code: str, status: RewardStatus, *, raw_response: str) -> RewardCode:
    return RewardCode(
        code=code,
        signature=_SIGNATURE,
        hash=hashlib.sha256(code.encode("utf-8")).hexdigest(),
        status=status,
        raw_response=raw_response,
    )


def _task_description(task: Task) -> str:
    parts: list[str] = []
    module = sys.modules.get(type(task).__module__)
    module_doc = getattr(module, "__doc__", None)
    if isinstance(module_doc, str) and module_doc.strip():
        parts.append(" ".join(module_doc.split()))
    doc = getattr(type(task), "__doc__", None)
    if isinstance(doc, str) and doc.strip():
        parts.append(" ".join(doc.split()))
    return " ".join(parts) if parts else task.name


def _spec_text(task: Task, attr: str) -> str:
    spec = getattr(task, attr, None)
    return f"{attr}: {spec!r}"


def _attempts_text(prior_attempts: list[Attempt]) -> str:
    if not prior_attempts:
        return "None."
    lines: list[str] = []
    for idx, attempt in enumerate(prior_attempts):
        metrics = ", ".join(
            f"{key}={value:.6g}" for key, value in sorted(attempt.eval_metrics.items())
        )
        lines.append(f"- attempt {idx}: metrics({metrics}); reflection: {attempt.reflection}")
    return "\n".join(lines)


__all__ = ["Attempt", "RewardCode", "build_reward_prompt", "generate_reward"]
