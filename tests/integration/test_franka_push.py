from __future__ import annotations

from pathlib import Path

import numpy as np

from physlab import list_tasks, make
from physlab.backends.mujoco import MuJoCoBackend
from physlab.env import Environment
from physlab.registry import UnknownBackendError
from physlab.tasks.franka_push import FrankaPushTask


def test_franka_push_registered() -> None:
    assert "franka_push" in list_tasks()


def test_franka_push_random_policy_runs_200_steps() -> None:
    env = make("franka_push", "mujoco", seed=42)
    rng = np.random.default_rng(42)
    try:
        obs, info = env.reset(seed=42)
        assert env.observation_space.contains(obs)
        assert "distance_to_target" in info
        for _ in range(200):
            obs, _, terminated, truncated, info = env.step(env.action_space.sample(rng))
            assert env.observation_space.contains(obs)
            assert "contact" in info
            if terminated or truncated:
                break
    finally:
        env.close()


def test_franka_push_random_policy_success_rate_is_low() -> None:
    env = make("franka_push", "mujoco", seed=0)
    rng = np.random.default_rng(0)
    successes = 0
    try:
        for episode in range(50):
            env.reset(seed=episode)
            for _ in range(200):
                _, _, terminated, truncated, info = env.step(env.action_space.sample(rng))
                if bool(info.get("success")):
                    successes += 1
                    break
                if terminated or truncated:
                    break
    finally:
        env.close()
    assert successes / 50 < 0.05


def test_franka_push_reset_seed_is_cpu_deterministic() -> None:
    first_env = make("franka_push", "mujoco", seed=42)
    second_env = make("franka_push", "mujoco", seed=42)
    try:
        _, first_info = first_env.reset(seed=42)
        _, second_info = second_env.reset(seed=42)
        first_cube = np.asarray(first_info["cube_pos"], dtype=np.float64)
        second_cube = np.asarray(second_info["cube_pos"], dtype=np.float64)
        assert first_cube.tobytes() == second_cube.tobytes()
    finally:
        first_env.close()
        second_env.close()


def test_franka_push_missing_asset_fails_clearly(tmp_path: Path) -> None:
    task = FrankaPushTask(asset_path=tmp_path / "missing.xml")
    with np.testing.assert_raises_regex((FileNotFoundError, TypeError), "missing"):
        Environment(MuJoCoBackend(), task, seed=0)


def test_franka_push_invalid_backend_fails_clearly() -> None:
    with np.testing.assert_raises_regex(UnknownBackendError, "invalid_backend"):
        make("franka_push", "invalid_backend")
