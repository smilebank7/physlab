from __future__ import annotations

import numpy as np

from physlab import list_tasks, make


def test_cartpole_registered() -> None:
    assert "cartpole" in list_tasks()


def test_cartpole_mujoco_random_policy_smoke() -> None:
    env = make("cartpole", "mujoco", seed=42)
    try:
        obs, _ = env.reset(seed=42)
        steps = 0
        rng = np.random.default_rng(42)
        while steps < 100:
            obs, _, terminated, truncated, _ = env.step(env.action_space.sample(rng))
            steps += 1
            if terminated or truncated:
                obs, _ = env.reset(seed=42 + steps)
        assert env.observation_space.contains(obs)
        assert steps == 100
    finally:
        env.close()


def test_cartpole_episode_finishes_within_500_steps() -> None:
    env = make("cartpole", "mujoco", seed=7)
    try:
        env.reset(seed=7)
        finished = False
        for _ in range(500):
            _, _, terminated, truncated, _ = env.step(env.action_space.sample())
            if terminated or truncated:
                finished = True
                break
        assert finished
    finally:
        env.close()


def test_cartpole_reset_is_cpu_deterministic() -> None:
    first_env = make("cartpole", "mujoco", seed=42)
    second_env = make("cartpole", "mujoco", seed=42)
    try:
        first, _ = first_env.reset(seed=42)
        second, _ = second_env.reset(seed=42)
        assert first.tobytes() == second.tobytes()
    finally:
        first_env.close()
        second_env.close()
