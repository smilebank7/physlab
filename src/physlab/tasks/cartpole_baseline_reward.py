"""Baseline cartpole reward exported for reward-evaluator smoke tests."""

import numpy as np


def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
    del action, info
    pole_angle = float(obs[1])
    return 1.0 if abs(pole_angle) < 0.2 else 0.0
