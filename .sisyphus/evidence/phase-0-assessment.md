# Phase 0 Assessment

## Fluency Scores

MuJoCo Python: 0
MCP server building: 0
IsaacLab internals: 0
OSS framework launch experience: 0
Robotics control fundamentals: 0

## Ship Name

physlab

## First User

The first user is a solo Apple Silicon robotics researcher building local, reproducible physical AI experiments. They are comfortable reading code and running command-line workflows, but they need the framework to make the first end-to-end episode fast and boring. Their highest-value moment is seeing a local opencode-driven reward iteration improve a MuJoCo task without CUDA or cloud infrastructure.

## Success Metric

The v0.1 success metric is `python examples/eureka_franka.py --seed=42` achieving Franka pick-place >=70% success in <=30 minutes wall-clock on the target M5 Pro machine, with evidence captured under `.sisyphus/evidence/`.

## Kill-Switch

Week 6: abandon or pivot v0.1 if T21 feasibility evidence shows the Franka anchor cannot reach >=50% pick-place success within 30 minutes after the reward-iteration loop is implemented and benchmarked.

## Scope Adjustments

- MuJoCo: extend Wave 1 by 1 week and cut Task 31.
- MCP: extend Tasks 10-11 by 3 days and cut Task 41.
- IsaacLab: drop Task 42 entirely.
- OSS launch: cut Task 43 polish and reduce Task 32 scope by 30%.
- Robotics control: score 0; no automatic cut rule in Phase 0.
