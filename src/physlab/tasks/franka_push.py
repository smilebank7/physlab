"""Franka push manipulation variant."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import mujoco
import numpy as np

from physlab.protocols import ActionSpec, Env, Info, ModelHandle, ObsSpec
from physlab.registry import register_task


@dataclass
class FrankaPushTask:
    """State-vector Franka object-pushing target."""

    asset_path: Path | None = None
    _initial_distance: float = field(default=0.25, init=False)

    name = "franka_push"
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
        """Return the MJCF asset path for the push task."""

        if self.asset_path is not None:
            return self.asset_path
        return Path(__file__).resolve().parents[1] / "assets" / "franka_push.xml"

    def make_env(self) -> Env:
        """Create a default MuJoCo environment for Franka pushing."""

        from physlab.registry import make

        return make(self.name)

    def on_reset(self, handle: ModelHandle, seed: int | None) -> None:
        """Randomize cube and target positions for a seeded push episode."""

        model, data = _mujoco(handle)
        rng = np.random.default_rng(seed)
        cube_xy = np.array([0.54, -0.08]) + rng.uniform(-0.05, 0.05, size=2)
        target_xy = cube_xy + np.array([0.16, 0.14]) + rng.uniform(-0.03, 0.03, size=2)
        cube_z = 0.405

        data.qpos[:7] = np.array([0.0, -0.35, 0.0, -1.2, 0.0, 1.0, 0.0], dtype=np.float64)
        data.qvel[:7] = 0.0
        cube_qpos = _joint_qpos_addr(model, "cube_free")
        data.qpos[cube_qpos : cube_qpos + 7] = np.array(
            [cube_xy[0], cube_xy[1], cube_z, 1.0, 0.0, 0.0, 0.0],
            dtype=np.float64,
        )
        cube_qvel = _joint_dof_addr(model, "cube_free")
        data.qvel[cube_qvel : cube_qvel + 6] = 0.0
        if model.nmocap > 0:
            data.mocap_pos[0] = np.array([target_xy[0], target_xy[1], cube_z], dtype=np.float64)
            data.mocap_quat[0] = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
        self._initial_distance = float(np.linalg.norm(cube_xy - target_xy))
        mujoco.mj_forward(model, data)

    def observe(
        self,
        handle: ModelHandle,
        backend_observation: np.ndarray[Any, Any],
        info: Info,
    ) -> np.ndarray[Any, Any]:
        """Build the compact push observation from MuJoCo state."""

        del backend_observation, info
        model, data = _mujoco(handle)
        cube_body = _body_id(model, "cube")
        gripper_site = _site_id(model, "gripper_site")
        target_site = _site_id(model, "target_site")
        distance = np.array(
            [np.linalg.norm(data.xpos[cube_body, :2] - data.site_xpos[target_site, :2])],
            dtype=np.float64,
        )
        return np.concatenate(
            (
                data.qpos[:7],
                data.qvel[:7],
                data.site_xpos[gripper_site],
                data.xpos[cube_body],
                data.site_xpos[target_site],
                distance,
            )
        ).astype(np.float64, copy=False)

    def info(self, handle: ModelHandle, observation: np.ndarray[Any, Any]) -> Info:
        """Return distance, contact, progress, and success metrics."""

        del handle
        gripper_pos = observation[14:17].copy()
        cube_pos = observation[17:20].copy()
        target_pos = observation[20:23].copy()
        distance = float(observation[23])
        gripper_distance = float(np.linalg.norm(gripper_pos - cube_pos))
        contact = bool(gripper_distance < 0.09)
        progress = self._initial_distance - distance
        success = bool(distance < 0.04 and cube_pos[2] < 0.46)
        return {
            "gripper_pos": gripper_pos,
            "cube_pos": cube_pos,
            "target_pos": target_pos,
            "distance_to_target": distance,
            "progress": progress,
            "contact": contact,
            "success": success,
        }

    def reward(
        self,
        observation: np.ndarray[Any, Any],
        action: np.ndarray[Any, Any],
        info: Info,
    ) -> float:
        """Reward pushing progress, contact, and success with action cost."""

        del observation
        distance = _float_info(info, "distance_to_target", 1.0)
        progress = _float_info(info, "progress", 0.0)
        contact_bonus = 0.1 if bool(info.get("contact", False)) else 0.0
        success_bonus = 1.0 if bool(info.get("success", False)) else 0.0
        control_cost = 0.01 * float(np.square(action).sum())
        return progress - distance + contact_bonus + success_bonus - control_cost

    def terminate(self, observation: np.ndarray[Any, Any], info: Info) -> bool:
        """End the episode when the cube reaches its target."""

        del observation
        return bool(info.get("success", False))

    def success_metric(self, rollout: object) -> float:
        """Compute the fraction of rollout records marked successful."""

        if not isinstance(rollout, list) or not rollout:
            return 0.0
        successes = [bool(step.get("success", False)) for step in rollout if isinstance(step, dict)]
        return float(sum(successes) / max(len(successes), 1))

    def reward_signature(self) -> str:
        """Describe the Franka push reward contract."""

        return "reward=progress-distance+0.1_contact+1_success-0.01_control"


def _mujoco(handle: ModelHandle) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if not isinstance(handle.model, mujoco.MjModel) or not isinstance(handle.data, mujoco.MjData):
        raise TypeError("franka_push requires a MuJoCo handle")
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


def _body_id(model: mujoco.MjModel, name: str) -> int:
    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
    if body_id < 0:
        raise ValueError(f"missing body {name!r}")
    return int(body_id)


def _site_id(model: mujoco.MjModel, name: str) -> int:
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, name)
    if site_id < 0:
        raise ValueError(f"missing site {name!r}")
    return int(site_id)


def _float_info(info: Info, key: str, default: float) -> float:
    value = info.get(key, default)
    if isinstance(value, int | float | str):
        return float(value)
    return default


register_task("franka_push", FrankaPushTask)

__all__ = ["FrankaPushTask"]
