# T21 Feasibility Gate

VERDICT: PASS

Date: 2026-05-28
Final run id: feas-gate-3
Final command: `python examples/eureka_franka.py --iterations=5 --llm=opencode --llm-timeout=600 --seed=42 --train-steps-per-iter=30000 --run-id=feas-gate-3`

## Final Measurements

- Wall-clock: 865s (14m25s)
- Exit status: 0
- Best success_rate: 1.0
- Best iteration: 0
- Completed iterations: 5
- Crash/error count: 0
- LLM cache hits: 0/10
- Cost/token spend: not surfaced by opencode; telemetry records `cost_tokens_stubbed=0`

## Gate Criteria

- Pass requires best success_rate >= 0.40, wall_clock <= 60min, and <=2 errored iterations.
- Final run passes: best success_rate 1.0, wall_clock 14m25s, and 0 errored iterations.

## Measurement History

### feas-gate-1

Command: `python examples/eureka_franka.py --iterations=5 --llm=opencode --seed=42 --train-steps-per-iter=30000 --run-id=feas-gate-1`

- Result: FAIL
- Wall-clock: 120s
- Exit status: 1
- Best success_rate: 0.0
- Completed iterations: 0
- Error: opencode timed out before returning iteration 0 reward code.
- Raw log: `.sisyphus/evidence/task-21-feasibility-gate.raw.log`

### feas-gate-2

Command: `python examples/eureka_franka.py --iterations=5 --llm=opencode --llm-timeout=600 --seed=42 --train-steps-per-iter=30000 --run-id=feas-gate-2`

- Result: FAIL
- Wall-clock: 931s
- Exit status: 0
- Best success_rate: 1.0
- Completed iterations: 5
- Crash/error count: 4
- Reason: pass threshold was not met because errored iterations exceeded 2.
- Raw log: `.sisyphus/evidence/task-21-feasibility-gate-rerun.raw.log`
- Run archive: `.sisyphus/evidence/task-21-feas-gate-2.tar.gz`

### feas-gate-3

Command: `python examples/eureka_franka.py --iterations=5 --llm=opencode --llm-timeout=600 --seed=42 --train-steps-per-iter=30000 --run-id=feas-gate-3`

- Result: PASS
- Wall-clock: 865s
- Exit status: 0
- Best success_rate: 1.0
- Completed iterations: 5
- Crash/error count: 0
- Raw log: `.sisyphus/evidence/task-21-feasibility-gate-rerun2.raw.log`
- Run archive: `.sisyphus/evidence/task-21-feas-gate-3.tar.gz`

## Tuning Applied

- Added `--llm-timeout` to `examples/eureka_franka.py` and set the live default to 600s.
- Expanded the evaluator subprocess safe builtins to include common side-effect-free Python helpers used by generated reward code, such as `isinstance`, `Exception`, `all`, `any`, `enumerate`, `zip`, `getattr`, and `hasattr`.
- Added regression tests for both changes.

## Decision Log

- 2026-05-28: Initial FAIL recorded for 120s opencode timeout.
- 2026-05-28: Continued per active goal instruction and applied the documented timeout tuning.
- 2026-05-28: Second run reached PPO but failed the error-count criterion because sandbox builtins were too narrow.
- 2026-05-28: Applied sandbox safe-builtins fix and reran live opencode without cache.
- 2026-05-28: Final rerun PASS. T22 is unblocked.
