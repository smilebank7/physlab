# T21 Feasibility Gate

VERDICT: FAIL

Date: 2026-05-28
Run id: feas-gate-1
Command: `python examples/eureka_franka.py --iterations=5 --llm=opencode --seed=42 --train-steps-per-iter=30000 --run-id=feas-gate-1`

## Measurements

- Wall-clock: 120s
- Exit status: 1
- Best success_rate: 0.0
- Completed iterations: 0
- Crash/error count: 1
- Cost/token spend: not surfaced; opencode timed out before returning a completion

## Failure Mode

The live opencode call for iteration 0 timed out after the client timeout of 120s.
No reward code was returned and no PPO evaluation began. Raw traceback is captured in
`.sisyphus/evidence/task-21-feasibility-gate.raw.log`.

## Gate Criteria

- Pass requires best success_rate >= 0.40, wall_clock <= 60min, and <=2 errored iterations.
- Fail applies because best success_rate is below 0.30 and no live LLM completion was obtained.

## Proposed Cuts

- Increase opencode client timeout and rerun T21 once to distinguish slow local model startup from reward quality failure.
- Reduce the live gate to 3 iterations only if the rerun reaches PPO evaluation but exceeds time budget.
- Keep Franka as the anchor unless a rerun reaches PPO and still scores below 0.30.
- Do not proceed to T22 until the gate decision is explicitly accepted.

## Decision Log

- 2026-05-28: FAIL recorded. Awaiting explicit user decision before proceeding past T21, per plan.
