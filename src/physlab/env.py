"""Environment API wrapping a backend and an explicitly registered task."""

from __future__ import annotations

from typing import Any, Protocol, cast

import numpy as np

from physlab.protocols import Action, ActionSpec, Backend, Info, ModelHandle, ObsSpec, Task


class _RewardTask(Protocol):
    def reward(self, observation: np.ndarray[Any, Any], action: Action, info: Info) -> float: ...


class _TerminateTask(Protocol):
    def terminate(self, observation: np.ndarray[Any, Any], info: Info) -> bool: ...


class Environment:
    """Gymnasium-shaped environment built from a backend and task object."""

    action_space: ActionSpec
    observation_space: ObsSpec

    def __init__(self, backend: Backend, task: Task, seed: int | None = None) -> None:
        self.backend = backend
        self.task = task
        self._handle = self.backend.load_model(_task_model_spec(task))
        self.action_space = _task_action_space(task, self._handle)
        self.observation_space = _task_observation_space(task, self._handle)
        self._step_count = 0
        self._max_steps = _task_max_steps(task)
        self._closed = False
        self._last_observation: np.ndarray[Any, Any] | None = None
        if seed is not None:
            self.reset(seed=seed)

    def reset(self, seed: int | None = None) -> tuple[np.ndarray[Any, Any], Info]:
        self._ensure_open()
        self._step_count = 0
        observation = self.backend.reset(self._handle, seed=seed)
        self._last_observation = observation
        if not self.observation_space.contains(observation):
            raise ValueError("backend observation does not match task observation_space")
        return observation, {
            "seed": seed,
            "step_count": self._step_count,
            "backend": self.backend.name(),
        }

    def step(self, action: Action) -> tuple[np.ndarray[Any, Any], float, bool, bool, Info]:
        self._ensure_open()
        action_array = np.asarray(action, dtype=np.float64)
        if not self.action_space.contains(action_array):
            raise ValueError("action does not match task action_space")
        result = self.backend.step(self._handle, action_array)
        self._step_count += 1
        info: Info = dict(result.info)
        info["step_count"] = self._step_count
        observation = result.observation
        if not self.observation_space.contains(observation):
            raise ValueError("backend observation does not match task observation_space")
        reward = _task_reward(self.task, observation, action_array, info, result.reward)
        terminated = result.terminated or _task_terminated(self.task, observation, info)
        truncated = result.truncated or self._step_count >= self._max_steps
        self._last_observation = observation
        return observation, reward, terminated, truncated, info

    def close(self) -> None:
        if not self._closed:
            self.backend.close(self._handle)
            self._closed = True

    def observe(self) -> tuple[np.ndarray[Any, Any], Info]:
        self._ensure_open()
        if self._last_observation is None:
            return self.reset()
        return self._last_observation.copy(), {"step_count": self._step_count}

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("environment is closed")


def _task_model_spec(task: Task) -> object:
    model_spec = getattr(task, "model_spec", None)
    if callable(model_spec):
        return model_spec()
    if model_spec is not None:
        return model_spec
    raise ValueError(f"task {task.name!r} must define model_spec")


def _task_action_space(task: Task, handle: ModelHandle) -> ActionSpec:
    action_space = getattr(task, "action_space", None)
    if isinstance(action_space, ActionSpec):
        return action_space
    model = handle.model
    nu = int(getattr(model, "nu", 1))
    return ActionSpec(shape=(nu,), dtype=np.float64)


def _task_observation_space(task: Task, handle: ModelHandle) -> ObsSpec:
    observation_space = getattr(task, "observation_space", None)
    if isinstance(observation_space, ObsSpec):
        return observation_space
    model = handle.model
    nq = int(getattr(model, "nq", 1))
    nv = int(getattr(model, "nv", nq))
    return ObsSpec(shape=(nq + nv,), dtype=np.float64)


def _task_max_steps(task: Task) -> int:
    value = getattr(task, "max_steps", 1000)
    max_steps = int(value() if callable(value) else value)
    if max_steps <= 0:
        raise ValueError("task max_steps must be positive")
    return max_steps


def _task_reward(
    task: Task,
    observation: np.ndarray[Any, Any],
    action: Action,
    info: Info,
    fallback: float,
) -> float:
    if hasattr(task, "reward"):
        return float(cast(_RewardTask, task).reward(observation, action, info))
    return float(fallback)


def _task_terminated(task: Task, observation: np.ndarray[Any, Any], info: Info) -> bool:
    if hasattr(task, "terminate"):
        return bool(cast(_TerminateTask, task).terminate(observation, info))
    return False


assert isinstance(Environment, type)

__all__ = ["Environment"]
