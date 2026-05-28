"""Iteration controller for reward generation, evaluation, and reflection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from physlab.llm.client import LLMClient
from physlab.orchestrator.evaluator import EvalResult, evaluate_reward
from physlab.orchestrator.iteration import Iteration
from physlab.orchestrator.reward_gen import (
    Attempt,
    RewardCode,
    RewardStatus,
    build_reward_prompt,
    generate_reward,
)
from physlab.orchestrator.run import Run
from physlab.orchestrator.store import RunStore, default_run_id
from physlab.protocols import Task

_REFLECTION_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "reflection.md"
_FAILURE_ERRORS = {
    "parse_error",
    "forbidden_import",
    "nan_reward",
    "timeout",
    "crash",
}


class RewardGeneratorFn(Protocol):
    def __call__(
        self,
        task: Task,
        llm: LLMClient,
        prior_attempts: list[Attempt],
        ctx_seed: int,
    ) -> RewardCode: ...


class EvaluatorFn(Protocol):
    def __call__(
        self,
        reward_code: RewardCode,
        task: Task,
        num_rollouts: int,
        train_steps: int,
        seed: int,
    ) -> EvalResult: ...


class IterationAbort(RuntimeError):
    """Raised when the controller aborts a run after repeated failures."""


@dataclass(frozen=True)
class ControllerResult:
    run: Run
    best_iteration: int | None
    best_success_rate: float
    aborted: bool = False
    reason: str | None = None
    warnings: list[str] = field(default_factory=list)


class IterationController:
    def __init__(
        self,
        *,
        task: Task,
        llm: LLMClient,
        store: RunStore | None = None,
        iterations: int = 5,
        reward_generator: RewardGeneratorFn = generate_reward,
        evaluator: EvaluatorFn | None = None,
        num_rollouts: int = 5,
        train_steps: int = 20_000,
        seed: int = 42,
    ) -> None:
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        self.task = task
        self.llm = llm
        self.store = store or RunStore()
        self.iterations = iterations
        self.reward_generator = reward_generator
        self.evaluator = evaluator or _evaluate_default
        self.num_rollouts = num_rollouts
        self.train_steps = train_steps
        self.seed = seed
        self.best_reward_so_far: RewardCode | None = None
        self.best_success_rate = 0.0
        self.best_iteration: int | None = None
        self.failure_streak_count = 0
        self._below_half_streak = 0
        self.warnings: list[str] = []

    def run(self, run_id: str | None = None) -> ControllerResult:
        resolved_run_id = run_id or default_run_id(self.task.name)
        run = self.store.create(
            run_id=resolved_run_id,
            task=self.task.name,
            config={
                "controller": "iteration",
                "iterations": self.iterations,
                "llm": self.llm.name(),
                "num_rollouts": self.num_rollouts,
                "seed": self.seed,
                "train_steps": self.train_steps,
            },
            started_at=resolved_run_id if run_id is not None else None,
        )
        prior_attempts: list[Attempt] = []

        for idx in range(self.iterations):
            prompt = build_reward_prompt(self.task, prior_attempts, self.seed + idx)
            reward_code = self.reward_generator(
                self.task,
                self.llm,
                prior_attempts,
                self.seed + idx,
            )
            eval_result = self._evaluate(idx, reward_code)
            error = reward_code.status if reward_code.status != "ok" else eval_result.error
            success_rate = 0.0 if error is not None else eval_result.success_rate
            self._update_best(idx, reward_code, success_rate, error)
            self._update_failure_state(error, success_rate)
            reflection = self._reflect(
                iteration_idx=idx,
                reward_status=reward_code.status,
                error=error,
                success_rate=success_rate,
            )
            prior_attempts.append(
                Attempt(
                    eval_metrics={
                        "success_rate": success_rate,
                        "mean_episode_reward": eval_result.mean_episode_reward,
                    },
                    reflection=reflection,
                )
            )
            status = "accepted" if error is None else "rejected"
            reason = None
            if self.failure_streak_count >= 5:
                status = "aborted"
                reason = "5_consecutive_failures"
            iteration = self._iteration_record(
                idx=idx,
                prompt=prompt,
                reward_code=reward_code,
                eval_result=eval_result,
                status=status,
                reflection=reflection,
                reason=reason,
            )
            self.store.write_iteration(run, iteration, reward_code.code)
            run.iterations.append(iteration)
            if reason is not None:
                raise IterationAbort(reason)

        return ControllerResult(
            run=run,
            best_iteration=self.best_iteration,
            best_success_rate=self.best_success_rate,
            warnings=list(self.warnings),
        )

    def _evaluate(self, idx: int, reward_code: RewardCode) -> EvalResult:
        if reward_code.status != "ok":
            return EvalResult(
                success_rate=0.0,
                mean_episode_reward=0.0,
                train_steps_used=0,
                wall_clock_s=0.0,
                error=reward_code.status,
            )
        return self.evaluator(
            reward_code,
            self.task,
            self.num_rollouts,
            self.train_steps,
            self.seed + idx,
        )

    def _update_best(
        self,
        idx: int,
        reward_code: RewardCode,
        success_rate: float,
        error: str | None,
    ) -> None:
        if error is not None:
            return
        if self.best_iteration is None or success_rate > self.best_success_rate:
            self.best_reward_so_far = reward_code
            self.best_success_rate = success_rate
            self.best_iteration = idx

    def _update_failure_state(self, error: str | None, success_rate: float) -> None:
        if error in _FAILURE_ERRORS:
            self.failure_streak_count += 1
        else:
            self.failure_streak_count = 0
        if self.best_success_rate > 0 and success_rate < self.best_success_rate * 0.5:
            self._below_half_streak += 1
            if self._below_half_streak == 3:
                self.warnings.append("3_iterations_below_half_best")
        else:
            self._below_half_streak = 0

    def _reflect(
        self,
        *,
        iteration_idx: int,
        reward_status: str,
        error: str | None,
        success_rate: float,
    ) -> str:
        template = _REFLECTION_PROMPT_PATH.read_text(encoding="utf-8")
        prompt = template.format(
            task_name=self.task.name,
            iteration_idx=iteration_idx,
            reward_status=reward_status,
            error=error or "none",
            success_rate=f"{success_rate:.6f}",
            best_success_rate=f"{self.best_success_rate:.6f}",
        )
        raw = self.llm.complete(
            prompt,
            purpose="reflection",
            iteration=iteration_idx,
            seed=self.seed,
        )
        return _limit_sentences(raw)

    def _iteration_record(
        self,
        *,
        idx: int,
        prompt: str,
        reward_code: RewardCode,
        eval_result: EvalResult,
        status: str,
        reflection: str,
        reason: str | None,
    ) -> Iteration:
        metadata: dict[str, object] = {
            "best_iteration": self.best_iteration,
            "best_success_rate": self.best_success_rate,
            "failure_streak": self.failure_streak_count,
            "reward_status": reward_code.status,
            "reward_hash": reward_code.hash,
        }
        if eval_result.error is not None:
            metadata["error"] = eval_result.error
        if reason is not None:
            metadata["reason"] = reason
        return Iteration(
            idx=idx,
            prompt=prompt,
            llm_response=reward_code.raw_response,
            artifact_path=f"iter_{idx}/reward.py",
            eval_metrics={
                "success_rate": eval_result.success_rate,
                "mean_episode_reward": eval_result.mean_episode_reward,
                "train_steps_used": float(eval_result.train_steps_used),
                "wall_clock_s": eval_result.wall_clock_s,
            },
            status=status,
            reflection=reflection,
            metadata=metadata,
        )


def _evaluate_default(
    reward_code: RewardCode,
    task: Task,
    num_rollouts: int,
    train_steps: int,
    seed: int,
) -> EvalResult:
    return evaluate_reward(
        reward_code,
        task,
        num_rollouts=num_rollouts,
        train_steps=train_steps,
        seed=seed,
    )


def _limit_sentences(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "No reflection produced."
    sentences = [part.strip() for part in cleaned.split(".") if part.strip()]
    if not sentences:
        return cleaned
    return ". ".join(sentences[:5]) + "."


def scripted_components(
    entries: list[dict[str, object]],
) -> tuple[RewardGeneratorFn, EvaluatorFn]:
    generator = _ScriptedRewardGenerator(entries)
    evaluator = _ScriptedEvaluator(entries)
    return generator, evaluator


class _ScriptedRewardGenerator:
    def __init__(self, entries: list[dict[str, object]]) -> None:
        self.entries = entries
        self.index = 0

    def __call__(
        self,
        task: Task,
        llm: LLMClient,
        prior_attempts: list[Attempt],
        ctx_seed: int,
    ) -> RewardCode:
        del task, llm, prior_attempts, ctx_seed
        entry = self.entries[self.index]
        self.index += 1
        status = str(entry.get("status", "ok"))
        return RewardCode(
            code=str(entry.get("code", "def reward_fn(obs, action, info):\n    return 0.0\n")),
            signature="reward_fn(obs, action, info)",
            hash=f"scripted-{self.index}",
            status=_status(status),
            raw_response=str(entry.get("raw_response", "")),
        )


class _ScriptedEvaluator:
    def __init__(self, entries: list[dict[str, object]]) -> None:
        self.entries = entries
        self.index = 0

    def __call__(
        self,
        reward_code: RewardCode,
        task: Task,
        num_rollouts: int,
        train_steps: int,
        seed: int,
    ) -> EvalResult:
        del reward_code, task, num_rollouts, train_steps, seed
        entry = self.entries[self.index]
        self.index += 1
        error = entry.get("error")
        return EvalResult(
            success_rate=_as_float(entry.get("success_rate", 0.0)),
            mean_episode_reward=_as_float(
                entry.get("mean_episode_reward", entry.get("success_rate", 0.0))
            ),
            train_steps_used=_as_int(entry.get("train_steps_used", 0)),
            wall_clock_s=_as_float(entry.get("wall_clock_s", 0.0)),
            error=str(error) if error is not None else None,
        )


def _status(value: str) -> RewardStatus:
    if value == "ok":
        return "ok"
    if value == "forbidden_import":
        return "forbidden_import"
    return "parse_error"


def _as_float(value: object) -> float:
    return float(value) if isinstance(value, int | float | str) else 0.0


def _as_int(value: object) -> int:
    return int(value) if isinstance(value, int | float | str) else 0


__all__ = [
    "ControllerResult",
    "EvaluatorFn",
    "IterationAbort",
    "IterationController",
    "RewardGeneratorFn",
    "scripted_components",
]
