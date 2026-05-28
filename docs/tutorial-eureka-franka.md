# Eureka-on-Franka Walkthrough

This tutorial walks through the v0.1 anchor demo: local, cached
Eureka-style reward iteration for the `franka_pick` task. Start with
[Getting Started](getting-started.md) if you have not installed the editable
package yet, and keep the [README](../README.md) open for the supported
platform and roadmap boundaries.

The goal is not to teach all of reinforcement learning. The goal is to make the
physlab pipeline legible enough that you can run it, inspect a previous run, and
know where to change one piece at a time.

## What You Will Run

The full live anchor command is:

```text
python examples/eureka_franka.py --seed=42
```

That path expects `opencode` on `PATH` and can take several minutes because it
does local LLM calls plus policy evaluation. For a first pass, use the mock LLM
smoke path. It exercises the same controller/storage shape without spending a
long run:

```bash
rm -rf runs/tutorial-smoke
uv run python examples/eureka_franka.py --headless --iterations=1 --llm=mock --seed=42 --run-id=tutorial-smoke
```

For a deterministic replay of the reference anchor run, use the committed cache
from `examples/anchor_demo_cache/seed42`. The cache stands in for local opencode
responses so CI and docs can replay the run without network or model drift.

```text
python examples/eureka_franka.py --headless --seed=42 --iterations=5 --llm=opencode --use-cache
```

The canonical reference output is committed under
[`runs/anchor-v0.1-canonical`](../runs/anchor-v0.1-canonical). Treat that
directory as a downloadable run bundle: it contains config, prompts, generated
reward candidates, eval metrics, reflections, `SUMMARY.md`, and
`BEST_REWARD.py`.

```bash
test -f runs/anchor-v0.1-canonical/SUMMARY.md
sed -n '1,18p' runs/anchor-v0.1-canonical/SUMMARY.md
```

## The Five Moving Parts

The anchor loop is intentionally plain. The parts are:

| Piece | Module | Job |
| --- | --- | --- |
| Task | `physlab.tasks.franka_pick` | Defines the MuJoCo model, observation, action bounds, baseline reward, success signal. |
| Reward generator | `physlab.orchestrator.reward_gen` | Builds the prompt, calls an LLM, extracts a Python reward function, rejects unsafe imports. |
| Evaluator | `physlab.orchestrator.evaluator` | Runs generated reward code in a subprocess and returns metrics. |
| Controller | `physlab.orchestrator.controller` | Chooses whether to continue, records best reward so far, asks for reflection. |
| Store | `physlab.orchestrator.store` | Writes prompts, rewards, eval JSON, reflections, and summaries into `runs/<run-id>/`. |

You can inspect the task contract without touching MuJoCo internals:

```python
from physlab.tasks.franka_pick import FrankaPickTask

task = FrankaPickTask()
print(task.name)
print(task.observation_space.shape)
print(task.action_space.shape)
```

For `franka_pick`, the observation is a compact state vector: Franka joint
positions and velocities, cube pose, and target position. The action is seven
bounded joint controls. That state-vector surface keeps the v0.1 reward-search
loop small, headless, and deterministic enough for CI.

## One Iteration, Annotated

A single iteration has this shape:

```text
1. Build prompt from task description, specs, prior metrics, and seed.
2. Ask the LLM for a Python reward function.
3. Parse the response and keep only a safe `reward_fn`.
4. Evaluate that reward in a subprocess with PPO.
5. Record metrics and reflection.
6. Keep the best reward candidate so far.
```

The prompt is dense on purpose. It gives the model the task description,
observation/action shapes, the existing task reward signature, prior attempts,
and a seed. A shortened prompt looks like this:

```text
You are writing one dense reward function for a local MuJoCo physical AI task.

Task description:
Franka pick-place anchor task. State-vector Franka pick-place target for
Eureka-style reward search.

Reward signature:
reward=-distance(cube,target)+1_success; success=cube_z>0.5 and distance<0.1

Return one Python function:
reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float
```

The LLM is expected to answer with a Python block. The parser does not trust the
whole message; it extracts a fenced Python block and checks syntax, imports, and
function name. A minimal acceptable shape is:

```python
import numpy as np


def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    distance = float(info.get("distance_to_target", 1.0))
    success = 1.0 if bool(info.get("success", False)) else 0.0
    control = 0.01 * float(np.square(action).sum())
    return success - distance - control


print(round(reward_fn(np.zeros(24), np.zeros(7), {"distance_to_target": 0.2}), 3))
```

Imports are deliberately narrow: `numpy`, `math`, and `physlab` are allowed.
Filesystem, subprocess, network, and hidden evaluator hooks are not part of the
reward function surface.

## What The Evaluator Produces

Each iteration writes an `eval.json`. The exact values depend on mode. In live
mode the evaluator trains and measures policy performance. In mock mode the
metrics are deterministic and cheap. A typical record contains:

```text
{
  "success_rate": 0.7,
  "mean_episode_reward": 0.7,
  "train_steps_used": 30000,
  "wall_clock_s": 120.5,
  "error": null
}
```

The controller does not need a perfect reward. It needs a measurable improvement
signal and a best-so-far artifact. At the end of the run, `SUMMARY.md` gives a
table of iterations and `BEST_REWARD.py` copies the best candidate with a small
attribution header.

Here is the terminal shape you should expect from the smoke command:

```text
| iter | status | success_rate | error |
| ---: | --- | ---: | --- |
| 0 | completed | 0.1200 |  |
run_dir=runs/tutorial-smoke
best_iteration=0 best_success_rate=0.1200
```

The cached reference run is more interesting because it replays five reward
candidates. On the reference M5 Pro feasibility run, live local opencode
completed in 14m25s with 0 errored iterations, and the cached replay completed
in 35s with best `success_rate=1.0`.

## Reading The Run Directory

Open `runs/anchor-v0.1-canonical` like a lab notebook:

```text
runs/anchor-v0.1-canonical/
  config.json
  manifest.jsonl
  SUMMARY.md
  BEST_REWARD.py
  iter_0/
    prompt.md
    reward.py
    eval.json
    reflection.md
  ...
```

`prompt.md` is the exact model input for that iteration. `reward.py` is the
candidate extracted from the LLM response. `eval.json` is the metric record.
`reflection.md` is a short controller-facing summary of what improved, what
failed, and what to try next. When debugging, compare `iter_N/reward.py` with
`iter_N/eval.json` first; that is usually where a bad reward shape becomes
obvious.

## How To Read A Reward Candidate

A generated reward is not judged by whether it looks elegant. It is judged by
whether it creates a training signal that moves the policy toward the task
success condition. For Franka pick-place, useful candidates usually combine a
few ingredients: distance from gripper to cube, distance from cube to target,
cube height, a small control penalty, and a terminal bonus for success.

The most common failure is over-rewarding only one subgoal. A reward that pays
only for approaching the cube can learn a policy that hovers near the cube but
never lifts. A reward that pays only for cube height can learn noisy motions
that lift briefly without moving toward the target. A reward that pays only for
target distance may be too sparse until the policy accidentally touches the
object. The iteration loop exists to surface those failures quickly: metrics
stay flat, reflection describes the bottleneck, and the next prompt includes
that context.

When inspecting `BEST_REWARD.py`, ask three practical questions:

1. Does every term correspond to an observable value in `obs` or `info`?
2. Does the reward provide dense shaping before success is reached?
3. Is the control penalty small enough to allow motion but large enough to
   discourage violent actions?

Those questions are intentionally concrete. v0.1 is a framework demo, not an
automatic reward scientist. The LLM proposes reward code; the sandbox and tests
keep it inside a small contract; the evaluator supplies evidence; the developer
still reads the artifacts.

## Cache Mode Versus Live Mode

Cache mode and live mode share the same storage and controller path, but they
answer different questions. Cache mode answers: can this repository replay the
known anchor behavior deterministically on a fresh machine? Live mode answers:
can a local opencode run produce and refine reward candidates within the wall
clock target?

Use cache mode when you are checking installation, CI behavior, docs snippets,
or run-directory readers. Use live mode only when you are intentionally testing
the local LLM loop. Live mode should produce new evidence, because the exact LLM
text can vary even when the seed and prompt are stable. That is why CI uses mock
or cached responses and why the feasibility gate records raw logs rather than
pretending live LLM output is bit-exact.

The seed still matters in both modes. It controls task reset state, evaluator
training setup, and cache selection. If two runs differ, first compare the
`config.json` files, then compare prompts, then compare generated reward code.
That order usually tells you whether the change came from configuration, prompt
context, or model output.

## Making A Small Change

The safest first modification is not a new robot. Change the number of
iterations, run with `--llm=mock`, and inspect the resulting `runs/<id>`
directory. Next, try cache mode with a fresh run id and confirm `SUMMARY.md` and
`BEST_REWARD.py` match your expectations. Only after those paths are boring
should you edit task rewards, evaluator settings, or live LLM prompts.

If you do change task code, rerun the task-specific integration test first. For
Franka pick-place that means checking reset determinism, random-policy behavior,
and 200-step rollout health. Then rerun the anchor smoke path. This keeps the
debug loop short: a broken MuJoCo asset should fail in the task test, while a
bad generated reward should fail in the orchestrator/evaluator layer.

## Common Gotchas

`opencode not found on PATH` means you are on the live path without the canonical
local LLM driver installed. Use `--llm=mock` for a smoke test or `--use-cache`
for the reference replay.

`run '<id>' already exists` means the store is protecting a previous result.
Use a new `--run-id`, or remove the old `runs/<id>` directory when you truly want
to rerun it.

CPU MuJoCo is the deterministic path. MPS-accelerated training should be treated
as epsilon-close, not bit-exact. The cached LLM responses are the CI path because
live LLM output is intentionally not deterministic enough for tests.

If reward parsing fails, check whether the LLM returned a fenced Python block
with a top-level `reward_fn`. If evaluation crashes, inspect `stderr` in
`eval.json` and simplify the reward.

## What To Try Next

Try the breadth tasks:

```text
python -c "from physlab import make; print(make('ant_stand', 'mujoco').reset(seed=0)[0].shape)"
python -c "from physlab import make; print(make('franka_push', 'mujoco').reset(seed=0)[0].shape)"
```

Then write a small task with the explicit registration pattern in
[`examples/plugins/hello_task`](../examples/plugins/hello_task). In v0.1,
extension freedom means import-and-register: user code imports a module, and
that module calls `register_task(...)` at top level. There is no plugin
auto-discovery machinery yet.
