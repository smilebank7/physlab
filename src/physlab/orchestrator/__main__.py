"""Command-line entry point for the research orchestrator skeleton."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from physlab.llm.client import LLMClient, MockLLMClient, OpencodeClient
from physlab.orchestrator.controller import (
    IterationAbort,
    IterationController,
    scripted_components,
)
from physlab.orchestrator.loop import MockEvaluator, MockRewardGenerator, OrchestratorLoop
from physlab.orchestrator.store import RunStore, RunStoreError, default_run_id
from physlab.protocols import Task
from physlab.tasks.cartpole import CartpoleTask
from physlab.tasks.franka_pick import FrankaPickTask


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for orchestrator runs."""

    parser = argparse.ArgumentParser(description="Run the physlab research orchestrator skeleton.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--llm", choices=["mock", "opencode"], default="opencode")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mock-script", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run or resume an orchestrator experiment from the CLI."""

    args = build_parser().parse_args(argv)
    store = RunStore(args.runs_dir)

    if args.resume is not None:
        try:
            resumed = store.read(str(args.resume))
        except RunStoreError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps({"resume": resumed.run_id, "iterations": len(resumed.iterations)}))
        return 0

    run_id = str(args.run_id) if args.run_id is not None else default_run_id(str(args.task))
    run_dir = store.path_for(run_id)
    client: LLMClient
    if args.llm == "mock":
        client = MockLLMClient(canned="mock llm response", run_dir=run_dir)
    else:
        executable = shutil.which("opencode")
        if executable is None:
            print("opencode not found on PATH", file=sys.stderr)
            return 1
        client = OpencodeClient(executable=executable, run_dir=run_dir)

    if args.mock_script is not None:
        entries = json.loads(args.mock_script.read_text(encoding="utf-8"))
        if not isinstance(entries, list):
            print("--mock-script must contain a JSON list", file=sys.stderr)
            return 2
        reward_generator, evaluator = scripted_components(
            [entry for entry in entries if isinstance(entry, dict)]
        )
        controller = IterationController(
            task=_task_object(str(args.task)),
            llm=client,
            store=store,
            iterations=int(args.iterations),
            reward_generator=reward_generator,
            evaluator=evaluator,
            train_steps=16,
            seed=int(args.seed),
        )
        try:
            result = controller.run(run_id=run_id)
        except (IterationAbort, RunStoreError, ValueError, IndexError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(
            json.dumps(
                {
                    "best_iteration": result.best_iteration,
                    "best_success_rate": result.best_success_rate,
                    "run_id": result.run.run_id,
                    "run_dir": str(store.path_for(result.run.run_id)),
                },
                sort_keys=True,
            )
        )
        return 0

    loop = OrchestratorLoop(
        task_name=str(args.task),
        llm_client=client,
        num_iterations=int(args.iterations),
        store=store,
        reward_generator=MockRewardGenerator(),
        evaluator=MockEvaluator(),
        seed=int(args.seed),
    )
    try:
        run = loop.run(run_id=run_id)
    except (RunStoreError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps({"run_id": run.run_id, "run_dir": str(store.path_for(run.run_id))}))
    return 0


def _task_object(name: str) -> Task:
    match name:
        case "cartpole":
            return CartpoleTask()
        case "franka_pick":
            return FrankaPickTask()
        case _:
            raise ValueError(f"unsupported task {name!r}")


if __name__ == "__main__":
    raise SystemExit(main())
