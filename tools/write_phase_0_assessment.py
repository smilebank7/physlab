#!/usr/bin/env python3
"""Write the Phase 0 assessment from explicit human-provided scores."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".sisyphus" / "evidence" / "phase-0-assessment.md"


def score(value: str) -> int:
    parsed = int(value)
    if parsed < 0 or parsed > 3:
        raise argparse.ArgumentTypeError("score must be between 0 and 3")
    return parsed


def scope_adjustments(scores: dict[str, int]) -> list[str]:
    adjustments: list[str] = []
    if scores["mujoco"] <= 1:
        adjustments.append("MuJoCo: extend Wave 1 by 1 week and cut Task 31.")
    else:
        adjustments.append("MuJoCo: no additional cut triggered.")

    if scores["mcp"] <= 1:
        adjustments.append("MCP: extend Tasks 10-11 by 3 days and cut Task 41.")
    else:
        adjustments.append("MCP: no additional cut triggered.")

    if scores["isaaclab"] <= 1:
        adjustments.append("IsaacLab: drop Task 42 entirely.")
    else:
        adjustments.append("IsaacLab: no additional cut triggered.")

    if scores["oss"] <= 1:
        adjustments.append("OSS launch: cut Task 43 polish and reduce Task 32 scope by 30%.")
    else:
        adjustments.append("OSS launch: no additional cut triggered.")

    robotics_score = scores["robotics"]
    adjustments.append(f"Robotics control: score {robotics_score}; no automatic cut rule in Phase 0.")
    return adjustments


def render(args: argparse.Namespace) -> str:
    scores = {
        "mujoco": args.mujoco,
        "mcp": args.mcp,
        "isaaclab": args.isaaclab,
        "oss": args.oss,
        "robotics": args.robotics,
    }
    adjustment_lines = "\n".join(f"- {item}" for item in scope_adjustments(scores))
    return f"""# Phase 0 Assessment

## Fluency Scores

MuJoCo Python: {args.mujoco}
MCP server building: {args.mcp}
IsaacLab internals: {args.isaaclab}
OSS framework launch experience: {args.oss}
Robotics control fundamentals: {args.robotics}

## Ship Name

{args.ship_name}

## First User

The first user is a solo Apple Silicon robotics researcher building local, reproducible physical AI experiments. They are comfortable reading code and running command-line workflows, but they need the framework to make the first end-to-end episode fast and boring. Their highest-value moment is seeing a local opencode-driven reward iteration improve a MuJoCo task without CUDA or cloud infrastructure.

## Success Metric

The v0.1 success metric is `python examples/eureka_franka.py --seed=42` achieving Franka pick-place >=70% success in <=30 minutes wall-clock on the target M5 Pro machine, with evidence captured under `.sisyphus/evidence/`.

## Kill-Switch

Week 6: abandon or pivot v0.1 if T21 feasibility evidence shows the Franka anchor cannot reach >=50% pick-place success within 30 minutes after the reward-iteration loop is implemented and benchmarked.

## Scope Adjustments

{adjustment_lines}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Phase 0 assessment markdown.")
    parser.add_argument("--mujoco", required=True, type=score, help="MuJoCo Python score, 0-3")
    parser.add_argument("--mcp", required=True, type=score, help="MCP server building score, 0-3")
    parser.add_argument("--isaaclab", required=True, type=score, help="IsaacLab internals score, 0-3")
    parser.add_argument("--oss", required=True, type=score, help="OSS framework launch score, 0-3")
    parser.add_argument("--robotics", required=True, type=score, help="Robotics control fundamentals score, 0-3")
    parser.add_argument("--ship-name", default="physlab", help="Chosen non-forbidden ship name")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Assessment output path")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
