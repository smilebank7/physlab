from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from physlab.llm.client import LLMClient
from physlab.orchestrator.controller import IterationAbort, IterationController
from physlab.orchestrator.evaluator import EvalResult
from physlab.orchestrator.reward_gen import Attempt, RewardCode
from physlab.orchestrator.store import RunStore
from physlab.tasks.cartpole import CartpoleTask


@dataclass
class _Candidate:
    status: str
    success_rate: float


class RecordingLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        del system, kwargs
        self.prompts.append(prompt)
        return "worked: reward became denser. failed: none. next: keep shaping."

    def name(self) -> str:
        return "recording"


class SequenceGenerator:
    def __init__(self, candidates: list[_Candidate]) -> None:
        self.candidates = candidates
        self.prior_reflections: list[list[str]] = []

    def __call__(
        self,
        task: object,
        llm: LLMClient,
        prior_attempts: list[Attempt],
        ctx_seed: int,
    ) -> RewardCode:
        del task, llm, ctx_seed
        self.prior_reflections.append([attempt.reflection for attempt in prior_attempts])
        candidate = self.candidates[len(self.prior_reflections) - 1]
        return RewardCode(
            code=f"def reward_fn(obs, action, info):\n    return {candidate.success_rate}\n",
            signature="reward_fn(obs, action, info)",
            hash=str(len(self.prior_reflections)),
            status=candidate.status,  # type: ignore[arg-type]
        )


class SequenceEvaluator:
    def __init__(self, candidates: list[_Candidate]) -> None:
        self.candidates = candidates
        self.calls = 0

    def __call__(
        self,
        reward_code: RewardCode,
        task: object,
        num_rollouts: int,
        train_steps: int,
        seed: int,
    ) -> EvalResult:
        del reward_code, task, num_rollouts, train_steps, seed
        candidate = self.candidates[self.calls]
        self.calls += 1
        return EvalResult(
            success_rate=candidate.success_rate,
            mean_episode_reward=candidate.success_rate,
            train_steps_used=16,
            wall_clock_s=0.01,
            error=None,
        )


def test_controller_tracks_and_persists_best_iteration(tmp_path: Path) -> None:
    candidates = [
        _Candidate("ok", 0.10),
        _Candidate("ok", 0.25),
        _Candidate("ok", 0.40),
        _Candidate("ok", 0.65),
        _Candidate("ok", 0.80),
    ]
    controller = IterationController(
        task=CartpoleTask(),
        llm=RecordingLLM(),
        store=RunStore(tmp_path / "runs"),
        iterations=5,
        reward_generator=SequenceGenerator(candidates),
        evaluator=SequenceEvaluator(candidates),
        train_steps=16,
    )

    result = controller.run(run_id="improving")

    assert result.best_iteration == 4
    assert result.best_success_rate == pytest.approx(0.80)
    manifest = (tmp_path / "runs" / "improving" / "manifest.jsonl").read_text()
    assert '"best_iteration": 4' in manifest.splitlines()[-1]


def test_controller_aborts_after_five_consecutive_failures(tmp_path: Path) -> None:
    candidates = [_Candidate("parse_error", 0.0) for _ in range(5)]
    controller = IterationController(
        task=CartpoleTask(),
        llm=RecordingLLM(),
        store=RunStore(tmp_path / "runs"),
        iterations=10,
        reward_generator=SequenceGenerator(candidates),
        evaluator=SequenceEvaluator(candidates),
        train_steps=16,
    )

    with pytest.raises(IterationAbort, match="5_consecutive_failures"):
        controller.run(run_id="abort")

    manifest = (tmp_path / "runs" / "abort" / "manifest.jsonl").read_text()
    assert '"status": "aborted"' in manifest
    assert '"reason": "5_consecutive_failures"' in manifest


def test_reflection_is_invoked_and_fed_to_next_prompt(tmp_path: Path) -> None:
    candidates = [_Candidate("ok", 0.1), _Candidate("ok", 0.2)]
    generator = SequenceGenerator(candidates)
    llm = RecordingLLM()
    controller = IterationController(
        task=CartpoleTask(),
        llm=llm,
        store=RunStore(tmp_path / "runs"),
        iterations=2,
        reward_generator=generator,
        evaluator=SequenceEvaluator(candidates),
        train_steps=16,
    )

    controller.run(run_id="reflections")

    assert len(llm.prompts) == 2
    assert generator.prior_reflections[0] == []
    assert "worked: reward became denser" in generator.prior_reflections[1][0]
