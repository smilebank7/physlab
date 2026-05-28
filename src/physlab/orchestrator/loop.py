"""Sequential research orchestrator loop skeleton."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from physlab.llm.client import LLMClient
from physlab.orchestrator.iteration import Iteration
from physlab.orchestrator.run import Run
from physlab.orchestrator.store import RunStore, default_run_id
from physlab.registry import list_tasks


class RewardGenerator(Protocol):
    def generate(
        self,
        *,
        task_name: str,
        iteration_idx: int,
        prompt: str,
        llm_response: str,
    ) -> str: ...


class Evaluator(Protocol):
    def evaluate(
        self,
        *,
        task_name: str,
        artifact_path: Path,
        iteration_idx: int,
    ) -> dict[str, float]: ...


class MockRewardGenerator:
    def generate(
        self,
        *,
        task_name: str,
        iteration_idx: int,
        prompt: str,
        llm_response: str,
    ) -> str:
        del prompt, llm_response
        return (
            f"# mock reward for {task_name}, iteration {iteration_idx}\n"
            "def reward(observation, action, next_observation, info):\n"
            "    return 0.0\n"
        )


class MockEvaluator:
    def evaluate(
        self,
        *,
        task_name: str,
        artifact_path: Path,
        iteration_idx: int,
    ) -> dict[str, float]:
        del task_name, artifact_path
        return {"success_rate": round(float(iteration_idx) * 0.1, 6)}


class OrchestratorLoop:
    def __init__(
        self,
        *,
        task_name: str,
        llm_client: LLMClient,
        num_iterations: int,
        store: RunStore | None = None,
        reward_generator: RewardGenerator | None = None,
        evaluator: Evaluator | None = None,
        seed: int = 42,
    ) -> None:
        if num_iterations <= 0:
            raise ValueError("num_iterations must be positive")
        if task_name not in list_tasks():
            available = ", ".join(list_tasks())
            raise ValueError(f"task {task_name!r} is not registered; available: {available}")
        self.task_name = task_name
        self.llm_client = llm_client
        self.num_iterations = num_iterations
        self.store = store or RunStore()
        self.reward_generator = reward_generator or MockRewardGenerator()
        self.evaluator = evaluator or MockEvaluator()
        self.seed = seed

    def run(self, run_id: str | None = None) -> Run:
        resolved_run_id = run_id or default_run_id(self.task_name)
        started_at = resolved_run_id if run_id is not None else None
        run = self.store.create(
            run_id=resolved_run_id,
            task=self.task_name,
            config={
                "iterations": self.num_iterations,
                "llm": self.llm_client.name(),
                "seed": self.seed,
            },
            started_at=started_at,
        )

        for idx in range(self.num_iterations):
            prompt = _prompt_for(self.task_name, idx, self.seed)
            llm_response = self.llm_client.complete(prompt, iteration=idx, seed=self.seed)
            artifact_relpath = f"iter_{idx}/reward.py"
            reward_code = self.reward_generator.generate(
                task_name=self.task_name,
                iteration_idx=idx,
                prompt=prompt,
                llm_response=llm_response,
            )
            artifact_path = self.store.path_for(run.run_id) / artifact_relpath
            eval_metrics = self.evaluator.evaluate(
                task_name=self.task_name,
                artifact_path=artifact_path,
                iteration_idx=idx,
            )
            reflection = (
                f"Iteration {idx} completed with success_rate="
                f"{eval_metrics.get('success_rate', 0.0):.6f}."
            )
            iteration = Iteration(
                idx=idx,
                prompt=prompt,
                llm_response=llm_response,
                artifact_path=artifact_relpath,
                eval_metrics=eval_metrics,
                status="completed",
                reflection=reflection,
            )
            self.store.write_iteration(run, iteration, reward_code)
            run.iterations.append(iteration)

        return run


def _prompt_for(task_name: str, iteration_idx: int, seed: int) -> str:
    return (
        f"# Reward research iteration {iteration_idx}\n\n"
        f"Task: {task_name}\n"
        f"Seed: {seed}\n"
        "Propose a reward function candidate. This skeleton stores the response only.\n"
    )
