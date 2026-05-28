"""Cartpole smoke-test task."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from physlab.protocols import ActionSpec, Env, ObsSpec
from physlab.registry import register_task


class CartpoleTask:
    """Classic cartpole task backed by a small owned MJCF model."""

    name = "cartpole"
    model_spec = Path(__file__).resolve().parents[1] / "assets" / "cartpole.xml"
    action_space = ActionSpec(
        shape=(1,),
        dtype=np.float64,
        low=np.array([-1.0], dtype=np.float64),
        high=np.array([1.0], dtype=np.float64),
    )
    observation_space = ObsSpec(shape=(4,), dtype=np.float64)
    max_steps = 500

    def make_env(self) -> Env:
        from physlab.registry import make

        return make(self.name)

    def reward(self, observation: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
        del action, info
        pole_angle = float(observation[1])
        return 1.0 if abs(pole_angle) < 0.2 else 0.0

    def terminate(self, observation: np.ndarray, info: dict[str, object]) -> bool:
        del info
        cart_x = float(observation[0])
        pole_angle = float(observation[1])
        return abs(pole_angle) > 0.2 or abs(cart_x) > 2.4

    def success_metric(self, rollout: object) -> float:
        if not isinstance(rollout, list) or not rollout:
            return 0.0
        return min(len(rollout) / self.max_steps, 1.0)

    def reward_signature(self) -> str:
        return "reward=1 if abs(pole_angle)<0.2 else 0; terminate at angle/cart bounds"


register_task("cartpole", CartpoleTask)

__all__ = ["CartpoleTask"]
