from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "eureka_franka_seed42_mock_llm.json"
ANCHOR_CACHE_ROOT = Path(__file__).resolve().parent / "anchor_demo_cache"


class FixtureLLM:
    def __init__(self, fixture_path: Path = FIXTURE_PATH) -> None:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        rewards = payload.get("rewards", [])
        if not isinstance(rewards, list) or not rewards:
            raise ValueError("mock LLM fixture must contain reward responses")
        self._rewards = [str(item) for item in rewards]
        self._reflection = str(payload.get("reflection", "mock reflection."))
        self._reward_idx = 0

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        del prompt, system
        if kwargs.get("purpose") == "reflection":
            return self._reflection
        response = self._rewards[min(self._reward_idx, len(self._rewards) - 1)]
        self._reward_idx += 1
        return response

    def name(self) -> str:
        return "mock"


class TimeoutLLM:
    def __init__(self, inner: object, timeout_s: float) -> None:
        self._inner = inner
        self._timeout_s = timeout_s

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        kwargs.setdefault("timeout", self._timeout_s)
        return str(self._inner.complete(prompt, system=system, **kwargs))

    def name(self) -> str:
        return str(self._inner.name())


class AnchorCacheLLM:
    def __init__(self, cache_root: Path, seed: int) -> None:
        cache_dir = cache_root / f"seed{seed}"
        manifest_path = cache_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        responses = manifest.get("responses", [])
        if not isinstance(responses, list) or not responses:
            raise ValueError(f"anchor cache {manifest_path} must contain responses")
        self._cache_dir = cache_dir
        self._responses = [item for item in responses if isinstance(item, dict)]
        self._reward_idx = 0
        self._reflection_idx = 0

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        del prompt, system
        if kwargs.get("purpose") == "reflection":
            entry = self._entry(self._reflection_idx)
            self._reflection_idx += 1
            return (self._cache_dir / str(entry["reflection"])).read_text(encoding="utf-8")
        entry = self._entry(self._reward_idx)
        self._reward_idx += 1
        code = (self._cache_dir / str(entry["reward"])).read_text(encoding="utf-8").strip()
        return f"```python\n{code}\n```"

    def name(self) -> str:
        return "anchor-cache"

    def _entry(self, idx: int) -> dict[str, object]:
        return self._responses[min(idx, len(self._responses) - 1)]


class MockFrankaEvaluator:
    def __init__(self) -> None:
        self._idx = 0

    def __call__(
        self,
        reward_code: object,
        task: object,
        num_rollouts: int,
        train_steps: int,
        seed: int,
    ) -> object:
        from physlab.orchestrator.evaluator import EvalResult

        del reward_code, task, num_rollouts, train_steps, seed
        curve = [0.12, 0.24, 0.38, 0.55, 0.70]
        success_rate = curve[min(self._idx, len(curve) - 1)]
        self._idx += 1
        return EvalResult(
            success_rate=success_rate,
            mean_episode_reward=success_rate,
            train_steps_used=0,
            wall_clock_s=0.01,
            error=None,
            training_curve=[success_rate],
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Franka Eureka-style anchor demo.")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--llm", choices=["opencode", "mock"], default="opencode")
    parser.add_argument("--llm-timeout", type=float, default=600.0)
    parser.add_argument("--use-cache", nargs="?", const=True, default=False, type=_parse_bool)
    parser.add_argument("--train-steps-per-iter", type=int, default=30_000)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    use_cache = bool(args.use_cache)

    if args.llm == "opencode" and not use_cache and shutil.which("opencode") is None:
        print(
            "opencode not found on PATH; install opencode or rerun with --llm=mock",
            file=sys.stderr,
        )
        return 1

    from physlab.llm.client import OpencodeClient
    from physlab.orchestrator.controller import IterationAbort, IterationController
    from physlab.orchestrator.store import RunStore, default_run_id
    from physlab.tasks.franka_pick import FrankaPickTask

    run_id = str(args.run_id) if args.run_id is not None else default_run_id("franka_pick")
    store = RunStore(args.runs_dir)
    run_dir = store.path_for(run_id)

    evaluator = None
    if use_cache:
        llm = AnchorCacheLLM(ANCHOR_CACHE_ROOT, seed=int(args.seed))
    elif args.llm == "mock":
        llm = FixtureLLM()
        evaluator = MockFrankaEvaluator()
    else:
        executable = str(shutil.which("opencode"))
        llm = TimeoutLLM(
            OpencodeClient(executable=executable, run_dir=run_dir),
            timeout_s=float(args.llm_timeout),
        )

    controller = IterationController(
        task=FrankaPickTask(),
        llm=llm,
        store=store,
        iterations=int(args.iterations),
        evaluator=evaluator,
        train_steps=int(args.train_steps_per_iter),
        seed=int(args.seed),
    )
    try:
        result = controller.run(run_id=run_id)
    except (IterationAbort, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    _write_outputs(
        run_dir,
        controller,
        result.run.iterations,
        result.best_iteration,
        result.best_success_rate,
    )
    print(_summary_table(result.run.iterations))
    print(f"run_dir={run_dir}")
    print(
        f"best_iteration={result.best_iteration} "
        f"best_success_rate={result.best_success_rate:.4f}"
    )
    return 0


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def _write_outputs(
    run_dir: Path,
    controller: object,
    iterations: object,
    best_iteration: int | None,
    best_success_rate: float,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    summary = [
        "# Eureka Franka Run",
        "",
        f"- best_iteration: {best_iteration}",
        f"- best_success_rate: {best_success_rate:.6f}",
        "",
        _summary_table(iterations),
        "",
    ]
    (run_dir / "SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
    best = controller.best_reward_so_far
    best_code = "" if best is None else _attributed_reward(best.code)
    (run_dir / "BEST_REWARD.py").write_text(best_code, encoding="utf-8")
    for reward_path in sorted(run_dir.glob("iter_*/reward.py")):
        reward_path.write_text(_artifact_reward(reward_path.read_text(encoding="utf-8")))


def _summary_table(iterations: object) -> str:
    rows = [
        "| iteration | success_rate | wall_clock | reward_signature |",
        "| --- | ---: | ---: | --- |",
    ]
    for iteration in iterations:
        success_rate = iteration.eval_metrics.get("success_rate", 0.0)
        wall_clock = iteration.eval_metrics.get("wall_clock_s", 0.0)
        signature = str(iteration.metadata.get("reward_hash", ""))
        rows.append(f"| {iteration.idx} | {success_rate:.4f} | {wall_clock:.2f}s | `{signature}` |")
    return "\n".join(rows)


def _attributed_reward(code: str) -> str:
    return (
        "# Generated by physlab anchor demo from local opencode reward search.\n"
        "# Source: examples/eureka_franka.py, seed=42.\n"
        "# ruff: noqa\n\n"
        f"{code.rstrip()}\n"
    )


def _artifact_reward(code: str) -> str:
    if code.startswith("# ruff: noqa"):
        return code
    return f"# ruff: noqa\n{code.rstrip()}\n"


if __name__ == "__main__":
    raise SystemExit(main())
