import numpy as np


def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    distance = float(info.get('distance_to_target', np.linalg.norm(obs[14:17] - obs[21:24])))
    lift = max(float(obs[16]) - 0.42, 0.0)
    return -distance + 0.25 * lift
