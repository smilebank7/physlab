from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from physlab import list_tasks, make
from physlab.backends.mujoco import MuJoCoBackend
from physlab.env import Environment
from physlab.tasks.locomotion import AntStandTask


def test_ant_stand_registered() -> None:
    assert "ant_stand" in list_tasks()


def test_ant_stand_runs_200_steps_quickly() -> None:
    env = make("ant_stand", "mujoco", seed=42)
    rng = np.random.default_rng(42)
    start = time.perf_counter()
    try:
        obs, info = env.reset(seed=42)
        assert env.observation_space.contains(obs)
        assert "upright" in info
        for _ in range(200):
            obs, _, terminated, truncated, info = env.step(env.action_space.sample(rng))
            assert env.observation_space.contains(obs)
            assert "torso_height" in info
            if terminated or truncated:
                break
    finally:
        env.close()
    assert time.perf_counter() - start < 3.0


def test_ant_stand_random_policy_success_rate_is_low() -> None:
    env = make("ant_stand", "mujoco", seed=0)
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


def test_ant_stand_reset_seed_is_cpu_deterministic() -> None:
    first_env = make("ant_stand", "mujoco", seed=42)
    second_env = make("ant_stand", "mujoco", seed=42)
    try:
        first, _ = first_env.reset(seed=42)
        second, _ = second_env.reset(seed=42)
        assert first.tobytes() == second.tobytes()
    finally:
        first_env.close()
        second_env.close()


def test_ant_stand_missing_asset_fails_clearly(tmp_path: Path) -> None:
    task = AntStandTask(asset_path=tmp_path / "missing.xml")
    with np.testing.assert_raises_regex((FileNotFoundError, TypeError), "missing"):
        Environment(MuJoCoBackend(), task, seed=0)
