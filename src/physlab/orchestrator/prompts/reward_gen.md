You are writing one dense reward function for a local MuJoCo physical AI task.

Task:
{task_description}

Reward signature:
{reward_signature}

Observation spec:
{obs_spec}

Action spec:
{action_spec}

Prior attempts:
{prior_attempts}

Context seed:
{ctx_seed}

Emit exactly one fenced Python code block containing:

```python
def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    ...
```

Use only numpy, math, and physlab imports. Do not perform file, network, process, or random
side effects. The reward should be shaped for learning and return a finite float.
