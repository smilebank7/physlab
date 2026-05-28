You are writing one dense reward function for a local MuJoCo physical AI task.

Task:
Franka pick-place anchor task. State-vector Franka pick-place target for Eureka-style reward search.

Reward signature:
reward=-distance(cube,target)+1_success; success=cube_z>0.5 and distance<0.1

Observation spec:
observation_space: ObsSpec(shape=(24,), dtype=dtype('float64'), low=None, high=None)

Action spec:
action_space: ActionSpec(shape=(7,), dtype=dtype('float64'), low=array([-1., -1., -1., -1., -1., -1., -1.]), high=array([1., 1., 1., 1., 1., 1., 1.]))

Prior attempts:
- attempt 0: metrics(mean_episode_reward=1, success_rate=1); reflection: The initial reward function for `franka_pick` succeeded on iteration 0 with a perfect 1. 000 success rate and no evaluation errors, meaning the agent reliably solves the pick task as specified. What worked: the reward signal was well-shaped enough out of the gate to drive the policy to convergence without any compile/runtime issues. Nothing meaningful failed - there's no error to debug and no performance gap to close. Since the task is already saturated at 100%, further reward iteration on success rate alone has nothing to optimize.
- attempt 1: metrics(mean_episode_reward=1, success_rate=1); reflection: Iteration 1 of `franka_pick` hit a perfect 1. 000 success rate on the first try, with no reward-shaping errors and no evaluation failures — the reward function compiled, ran, and drove the policy to solve the task end-to-end. Since this is also the running best, the current reward formulation is already at the ceiling for this benchmark and there is no failure mode to diagnose. What worked: the reward signal was dense and well-aligned enough that the policy converged without any tuning passes. What did not: nothing measurable — there is no shortfall to attribute to reward design.
- attempt 2: metrics(mean_episode_reward=1, success_rate=1); reflection: Iteration 2 of `franka_pick` converged to a perfect 1. 000 success rate with a clean reward (no compile/runtime errors) and no evaluation faults, matching the best-so-far score. The reward shaping clearly produced a learnable gradient end-to-end — approach, grasp, and lift were all consistently rewarded enough for the policy to solve every rollout. Nothing measurable failed this iteration, so there is no defect to diagnose. Since the task is already saturated at ceiling, further reward edits risk regressing a working solution; the next "attempt" should either lock in this reward as the final accepted version, or move to a harder evaluation (more object variants, perturbed initial poses, stricter success criteria) to expose remaining weaknesses before tuning again.

Context seed:
45

Emit exactly one fenced Python code block containing:

```python
def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    ...
```

Use only numpy, math, and physlab imports. Do not perform file, network, process, or random
side effects. The reward should be shaped for learning and return a finite float.
