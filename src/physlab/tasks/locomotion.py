"""Small quadruped standing task."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import mujoco
import numpy as np

from physlab.protocols import ActionSpec, Env, Info, ModelHandle, ObsSpec
from physlab.registry import register_task


@dataclass
class AntStandTask:
    """MuJoCo quadruped stand task for breadth testing."""

    asset_path: Path | None = None

    name = "ant_stand"
    action_space = ActionSpec(
        shape=(8,),
        dtype=np.float64,
        low=np.full(8, -1.0, dtype=np.float64),
        high=np.full(8, 1.0, dtype=np.float64),
    )
    observation_space = ObsSpec(shape=(29,), dtype=np.float64)
    max_steps = 200

    @property
    def model_spec(self) -> Path:
        if self.asset_path is not None:
            return self.asset_path
        return Path(__file__).resolve().parents[1] / "assets" / "ant_stand.xml"

    def make_env(self) -> Env:
        from physlab.registry import make

        return make(self.name)

    def on_reset(self, handle: ModelHandle, seed: int | None) -> None:
        model, data = _mujoco(handle)
        rng = np.random.default_rng(seed)
        data.qpos[:] = 0.0
        data.qvel[:] = 0.0
        data.qpos[:7] = np.array([0.0, 0.0, 0.34, 1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        data.qpos[7:] = rng.uniform(-0.02, 0.02, size=model.nq - 7)
        mujoco.mj_forward(model, data)

    def observe(
        self,
        handle: ModelHandle,
        backend_observation: np.ndarray[Any, Any],
        info: Info,
    ) -> np.ndarray[Any, Any]:
        del backend_observation, info
        _, data = _mujoco(handle)
        return np.concatenate((data.qpos, data.qvel)).astype(np.float64, copy=False)

    def info(self, handle: ModelHandle, observation: np.ndarray[Any, Any]) -> Info:
        del observation
        model, data = _mujoco(handle)
        torso = _body_id(model, "torso")
        upright = float(data.xmat[torso, 8])
        height = float(data.xpos[torso, 2])
        speed = float(np.linalg.norm(data.qvel[:3]))
        drift = float(np.linalg.norm(data.qpos[:2]))
        step_count = int(round(float(data.time / model.opt.timestep)))
        success = bool(
            step_count >= self.max_steps
            and height > 0.30
            and upright > 0.98
            and speed < 0.05
            and drift < 0.05
        )
        return {
            "torso_height": height,
            "upright": upright,
            "forward_velocity": float(data.qvel[0]),
            "drift": drift,
            "success": success,
        }

    def reward(
        self,
        observation: np.ndarray[Any, Any],
        action: np.ndarray[Any, Any],
        info: Info,
    ) -> float:
        del observation
        upright = _float_info(info, "upright")
        height = _float_info(info, "torso_height")
        forward = _float_info(info, "forward_velocity")
        control_cost = 0.02 * float(np.square(action).sum())
        return forward + upright + 0.5 * height - control_cost

    def terminate(self, observation: np.ndarray[Any, Any], info: Info) -> bool:
        del observation
        return bool(_float_info(info, "torso_height") < 0.16 or _float_info(info, "upright") < 0.2)

    def success_metric(self, rollout: object) -> float:
        if not isinstance(rollout, list) or not rollout:
            return 0.0
        successes = [bool(step.get("success", False)) for step in rollout if isinstance(step, dict)]
        return float(sum(successes) / max(len(successes), 1))

    def reward_signature(self) -> str:
        return "reward=forward_velocity+upright+0.5*height-0.02*control_cost"


def _mujoco(handle: ModelHandle) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if not isinstance(handle.model, mujoco.MjModel) or not isinstance(handle.data, mujoco.MjData):
        raise TypeError("ant_stand requires a MuJoCo handle")
    return handle.model, handle.data


def _body_id(model: mujoco.MjModel, name: str) -> int:
    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
    if body_id < 0:
        raise ValueError(f"missing body {name!r}")
    return int(body_id)


def _float_info(info: Info, key: str) -> float:
    value = info.get(key, 0.0)
    if isinstance(value, int | float | str):
        return float(value)
    return 0.0


register_task("ant_stand", AntStandTask)

__all__ = ["AntStandTask"]
