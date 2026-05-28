from __future__ import annotations

from pathlib import Path

import numpy as np

from physlab import list_tasks, make, register_task
from physlab.backends.mock import MockBackend
from physlab.env import Environment
from physlab.protocols import ActionSpec, Env, ObsSpec
from physlab.registry import TaskNotRegisteredError, UnknownBackendError


class DummyTask:
    name = "test_task"
    model_spec = {"nq": 1, "nv": 1, "nu": 1}
    action_space = ActionSpec(shape=(1,), dtype=np.float64)
    observation_space = ObsSpec(shape=(2,), dtype=np.float64)
    max_steps = 100

    def make_env(self) -> Env:
        raise NotImplementedError

    def reward(self, observation: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
        del observation, action, info
        return 0.0

    def success_metric(self, rollout: object) -> float:
        return 0.0 if rollout is None else 1.0

    def reward_signature(self) -> str:
        return "r=0"


class PendulumTask:
    name = "pendulum_task"
    model_spec = "tests/fixtures/pendulum.xml"
    action_space = ActionSpec(shape=(1,), dtype=np.float64)
    observation_space = ObsSpec(shape=(2,), dtype=np.float64)
    max_steps = 100

    def make_env(self) -> Env:
        raise NotImplementedError

    def reward(self, observation: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
        del observation, action, info
        return 0.0

    def success_metric(self, rollout: object) -> float:
        return 0.0 if rollout is None else 1.0

    def reward_signature(self) -> str:
        return "r=0"


def test_register_make_and_list_tasks() -> None:
    register_task("test_task", DummyTask)
    assert "test_task" in list_tasks()
    env = make("test_task", "mock", seed=42)
    try:
        assert isinstance(env, Environment)
        obs, _ = env.reset(seed=42)
        for _ in range(100):
            obs, _, _, truncated, _ = env.step(np.array([0.0], dtype=np.float64))
            if truncated:
                break
        assert env.observation_space.contains(obs)
    finally:
        env.close()


def test_unknown_task_lists_available_tasks() -> None:
    register_task("test_task", DummyTask)
    try:
        make("does_not_exist", "mock")
    except TaskNotRegisteredError as exc:
        message = str(exc)
        assert "does_not_exist" in message
        assert "test_task" in message
    else:
        raise AssertionError("TaskNotRegisteredError was not raised")


def test_backend_string_and_instance_resolution() -> None:
    register_task("test_task", DummyTask)
    mock_env = make("test_task", "mock", seed=0)
    instance_env = make("test_task", MockBackend(), seed=0)
    try:
        assert isinstance(mock_env, Environment)
        assert isinstance(instance_env, Environment)
    finally:
        mock_env.close()
        instance_env.close()


def test_unknown_backend_raises_typed_error() -> None:
    register_task("test_task", DummyTask)
    with np.testing.assert_raises_regex(UnknownBackendError, "invalid_backend"):
        make("test_task", "invalid_backend")


def test_register_task_rejects_empty_name_and_mujoco_resolves() -> None:
    with np.testing.assert_raises_regex(ValueError, "non-empty"):
        register_task("", DummyTask)
    register_task("pendulum_task", PendulumTask)
    env = make("pendulum_task", "mujoco", seed=0)
    try:
        assert isinstance(env, Environment)
    finally:
        env.close()


def test_registry_has_no_automatic_discovery() -> None:
    registry_source = Path("src/physlab/registry.py").read_text()
    forbidden = ["entry" + "_points", "importlib" + ".metadata"]
    assert all(token not in registry_source for token in forbidden)
