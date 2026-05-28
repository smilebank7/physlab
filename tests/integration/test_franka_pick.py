from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from physlab import list_tasks, make
from physlab.backends.mujoco import MuJoCoBackend
from physlab.env import Environment
from physlab.tasks.franka_pick import FrankaPickTask


def test_franka_pick_registered() -> None:
    assert "franka_pick" in list_tasks()


def test_franka_pick_random_policy_runs_200_steps_quickly() -> None:
    env = make("franka_pick", "mujoco", seed=42)
    rng = np.random.default_rng(42)
    start = time.perf_counter()
    try:
        obs, info = env.reset(seed=42)
        assert env.observation_space.contains(obs)
        assert obs.shape == (24,)
        assert "cube_pos" in info
        for _ in range(200):
            obs, _, terminated, truncated, info = env.step(env.action_space.sample(rng))
            assert env.observation_space.contains(obs)
            assert "success" in info
            if terminated or truncated:
                break
    finally:
        env.close()
    assert time.perf_counter() - start < 2.0


def test_franka_pick_random_policy_success_rate_is_low() -> None:
    env = make("franka_pick", "mujoco", seed=0)
    rng = np.random.default_rng(0)
    successes = 0
    try:
        for episode in range(100):
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
    assert successes / 100 < 0.05


def test_franka_pick_reset_seed_is_cpu_deterministic() -> None:
    first_env = make("franka_pick", "mujoco", seed=42)
    second_env = make("franka_pick", "mujoco", seed=42)
    try:
        _, first_info = first_env.reset(seed=42)
        _, second_info = second_env.reset(seed=42)
        first_cube = np.asarray(first_info["cube_pos"], dtype=np.float64)
        second_cube = np.asarray(second_info["cube_pos"], dtype=np.float64)
        assert first_cube.tobytes() == second_cube.tobytes()
    finally:
        first_env.close()
        second_env.close()


def test_franka_pick_missing_asset_fails_clearly(tmp_path: Path) -> None:
    task = FrankaPickTask(asset_path=tmp_path / "missing.xml")
    assert not Path(task.model_spec).exists()
    with np.testing.assert_raises_regex((FileNotFoundError, TypeError), "missing"):
        Environment(MuJoCoBackend(), task, seed=0)
