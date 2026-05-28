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
None.

Context seed:
42

Emit exactly one fenced Python code block containing:

```python
def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    ...
```

Use only numpy, math, and physlab imports. Do not perform file, network, process, or random
side effects. The reward should be shaped for learning and return a finite float.
