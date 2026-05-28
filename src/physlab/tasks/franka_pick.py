"""Franka pick-place anchor task."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import mujoco
import numpy as np

from physlab.protocols import ActionSpec, Env, Info, ModelHandle, ObsSpec
from physlab.registry import register_task


@dataclass
class FrankaPickTask:
    """State-vector Franka pick-place target for Eureka-style reward search."""

    asset_path: Path | None = None

    name = "franka_pick"
    action_space = ActionSpec(
        shape=(7,),
        dtype=np.float64,
        low=np.full(7, -1.0, dtype=np.float64),
        high=np.full(7, 1.0, dtype=np.float64),
    )
    observation_space = ObsSpec(shape=(24,), dtype=np.float64)
    max_steps = 200

    @property
    def model_spec(self) -> Path:
        if self.asset_path is not None:
            return self.asset_path
        return Path(__file__).resolve().parents[1] / "assets" / "franka_pick.xml"

    def make_env(self) -> Env:
        from physlab.registry import make

        return make(self.name)

    def on_reset(self, handle: ModelHandle, seed: int | None) -> None:
        model, data = _mujoco(handle)
        rng = np.random.default_rng(seed)
        cube_xy = np.array([0.55, 0.0]) + rng.uniform(-0.15, 0.15, size=2)
        target_xy = np.array([0.65, 0.10]) + rng.uniform(-0.15, 0.15, size=2)
        cube_z = 0.405 + float(rng.uniform(0.0, 0.05))
        target_z = 0.42 + float(rng.uniform(0.0, 0.05))

        joint_qpos = np.array([0.0, -0.35, 0.0, -1.2, 0.0, 1.0, 0.0], dtype=np.float64)
        data.qpos[:7] = joint_qpos
        data.qvel[:7] = 0.0
        cube_qpos = _joint_qpos_addr(model, "cube_free")
        data.qpos[cube_qpos : cube_qpos + 7] = np.array(
            [cube_xy[0], cube_xy[1], cube_z, 1.0, 0.0, 0.0, 0.0],
            dtype=np.float64,
        )
        cube_qvel = _joint_dof_addr(model, "cube_free")
        data.qvel[cube_qvel : cube_qvel + 6] = 0.0
        if model.nmocap > 0:
            data.mocap_pos[0] = np.array([target_xy[0], target_xy[1], target_z], dtype=np.float64)
            data.mocap_quat[0] = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        mujoco.mj_forward(model, data)

    def observe(
        self,
        handle: ModelHandle,
        backend_observation: np.ndarray[Any, Any],
        info: Info,
    ) -> np.ndarray[Any, Any]:
        del backend_observation, info
        model, data = _mujoco(handle)
        cube_body = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "cube")
        target_site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "target_site")
        return np.concatenate(
            (
                data.qpos[:7],
                data.qvel[:7],
                data.xpos[cube_body],
                data.xquat[cube_body],
                data.site_xpos[target_site],
            )
        ).astype(np.float64, copy=False)

    def info(self, handle: ModelHandle, observation: np.ndarray[Any, Any]) -> Info:
        del handle
        cube_pos = observation[14:17].copy()
        target_pos = observation[21:24].copy()
        distance = float(np.linalg.norm(cube_pos - target_pos))
        success = bool(cube_pos[2] > 0.5 and distance < 0.1)
        return {
            "cube_pos": cube_pos,
            "target_pos": target_pos,
            "success": success,
            "distance_to_target": distance,
        }

    def reward(
        self,
        observation: np.ndarray[Any, Any],
        action: np.ndarray[Any, Any],
        info: Info,
    ) -> float:
        del action
        raw_distance = info.get("distance_to_target", 1.0)
        distance = float(raw_distance) if isinstance(raw_distance, int | float | str) else 1.0
        success = bool(info.get("success", False))
        return (1.0 if success else 0.0) - distance

    def terminate(self, observation: np.ndarray[Any, Any], info: Info) -> bool:
        del observation
        return bool(info.get("success", False))

    def success_metric(self, rollout: object) -> float:
        if not isinstance(rollout, list) or not rollout:
            return 0.0
        successes = [bool(step.get("success", False)) for step in rollout if isinstance(step, dict)]
        return float(sum(successes) / max(len(successes), 1))

    def reward_signature(self) -> str:
        return "reward=-distance(cube,target)+1_success; success=cube_z>0.5 and distance<0.1"


def _mujoco(handle: ModelHandle) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if not isinstance(handle.model, mujoco.MjModel) or not isinstance(handle.data, mujoco.MjData):
        raise TypeError("franka_pick requires a MuJoCo handle")
    return handle.model, handle.data


def _joint_qpos_addr(model: mujoco.MjModel, name: str) -> int:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if joint_id < 0:
        raise ValueError(f"missing joint {name!r}")
    return int(model.jnt_qposadr[joint_id])


def _joint_dof_addr(model: mujoco.MjModel, name: str) -> int:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if joint_id < 0:
        raise ValueError(f"missing joint {name!r}")
    return int(model.jnt_dofadr[joint_id])


register_task("franka_pick", FrankaPickTask)

__all__ = ["FrankaPickTask"]
