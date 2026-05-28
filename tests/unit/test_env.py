from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physlab.backends.mock import MockBackend
from physlab.env import Environment
from physlab.protocols import ActionSpec, Env, ObsSpec


@dataclass
class DummyTask:
    name: str = "test_task"
    model_spec: object = None
    action_space: ActionSpec = ActionSpec(shape=(1,), dtype=np.float64)
    observation_space: ObsSpec = ObsSpec(shape=(2,), dtype=np.float64)
    max_steps: int = 5

    def __post_init__(self) -> None:
        if self.model_spec is None:
            self.model_spec = {"nq": 1, "nv": 1, "nu": 1}

    def make_env(self) -> Env:
        raise NotImplementedError

    def reward(self, observation: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
        del observation, action, info
        return 1.0

    def terminate(self, observation: np.ndarray, info: dict[str, object]) -> bool:
        del observation, info
        return False

    def success_metric(self, rollout: object) -> float:
        return 1.0 if rollout else 0.0

    def reward_signature(self) -> str:
        return "reward=1"


def test_environment_implements_protocol_and_runs_steps() -> None:
    env = Environment(MockBackend(), DummyTask(), seed=42)
    try:
        assert isinstance(env, Env)
        obs, info = env.reset(seed=42)
        assert env.observation_space.contains(obs)
        assert info["step_count"] == 0
        for step in range(1, 4):
            obs, reward, terminated, truncated, info = env.step(np.array([0.0], dtype=np.float64))
            assert env.observation_space.contains(obs)
            assert reward == 1.0
            assert not terminated
            assert not truncated
            assert info["step_count"] == step
    finally:
        env.close()


def test_environment_truncates_at_task_max_steps() -> None:
    env = Environment(MockBackend(), DummyTask(max_steps=2), seed=0)
    try:
        env.reset(seed=0)
        _, _, _, truncated, _ = env.step(np.array([0.0], dtype=np.float64))
        assert not truncated
        _, _, _, truncated, _ = env.step(np.array([0.0], dtype=np.float64))
        assert truncated
    finally:
        env.close()


def test_environment_rejects_action_outside_spec() -> None:
    env = Environment(MockBackend(), DummyTask(), seed=0)
    try:
        env.reset(seed=0)
        with np.testing.assert_raises_regex(ValueError, "action does not match"):
            env.step(np.array([0.0, 1.0], dtype=np.float64))
    finally:
        env.close()


def test_environment_observe_and_closed_errors() -> None:
    env = Environment(MockBackend(), DummyTask())
    obs, info = env.observe()
    assert env.observation_space.contains(obs)
    assert info["step_count"] == 0
    env.close()
    with np.testing.assert_raises_regex(RuntimeError, "closed"):
        env.observe()


def test_environment_supports_callable_specs_and_fallback_reward() -> None:
    class MinimalTask:
        name = "minimal"

        def model_spec(self) -> object:
            return {"nq": 1, "nv": 1, "nu": 1}

        def max_steps(self) -> int:
            return 1

        def make_env(self) -> Env:
            raise NotImplementedError

        def success_metric(self, rollout: object) -> float:
            return 0.0 if rollout is None else 1.0

        def reward_signature(self) -> str:
            return "backend reward"

    env = Environment(MockBackend(), MinimalTask())
    try:
        obs, _ = env.reset(seed=0)
        assert env.observation_space.contains(obs)
        _, reward, terminated, truncated, _ = env.step(np.array([0.0], dtype=np.float64))
        assert reward == 0.0
        assert not terminated
        assert truncated
    finally:
        env.close()


def test_environment_requires_model_spec_and_positive_max_steps() -> None:
    class NoModelSpecTask:
        name = "no_model"

        def make_env(self) -> Env:
            raise NotImplementedError

        def success_metric(self, rollout: object) -> float:
            return 0.0 if rollout is None else 1.0

        def reward_signature(self) -> str:
            return "missing"

    with np.testing.assert_raises_regex(ValueError, "model_spec"):
        Environment(MockBackend(), NoModelSpecTask())

    with np.testing.assert_raises_regex(ValueError, "max_steps"):
        Environment(MockBackend(), DummyTask(max_steps=0))
