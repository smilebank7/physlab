# Examples

## Eureka Franka

`python examples/eureka_franka.py --seed=42` runs the local Eureka-style Franka
pick-place anchor demo. On the reference M5 Pro feasibility run, live opencode
completed in 14m25s with best success_rate 1.0 and 0 errored iterations.

Use the committed cache for deterministic offline replay:

```bash
python examples/eureka_franka.py --seed=42 --iterations=5 --llm=opencode --use-cache
```

Use `--llm=mock` for the fast deterministic smoke path used by CI.
