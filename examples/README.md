# Examples

## Eureka Franka

`python examples/eureka_franka.py --seed=42` runs the local Eureka-style Franka
pick-place anchor demo. On M5 Pro, this is expected to run in about 25-30 minutes
with `--iterations=5 --train-steps-per-iter=30000`; expect best success_rate >=0.70
by iteration 5 when using cached/reproducible LLM responses, with small variance for
live opencode responses.

Use `--llm=mock` for the fast deterministic smoke path used by CI.
