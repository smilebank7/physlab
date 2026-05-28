"""Explicit task registry and backend resolution."""

from __future__ import annotations

from collections.abc import Callable

from physlab.backends.mock import MockBackend
from physlab.backends.mujoco import MuJoCoBackend
from physlab.env import Environment
from physlab.protocols import Backend, Task

TaskFactory = Callable[[], Task]

_TASKS: dict[str, TaskFactory] = {}


class TaskNotRegisteredError(KeyError):
    """Raised when a task name is not present in the explicit registry."""


class UnknownBackendError(ValueError):
    """Raised when a backend string cannot be resolved."""


def register_task(name: str, task_factory: TaskFactory) -> None:
    if not name:
        raise ValueError("task name must be non-empty")
    _TASKS[name] = task_factory


def list_tasks() -> list[str]:
    _load_builtin_tasks()
    return sorted(_TASKS)


def make(name: str, backend: Backend | str = "mujoco", seed: int | None = None) -> Environment:
    _load_builtin_tasks()
    if name not in _TASKS:
        available = ", ".join(sorted(_TASKS)) or "<none>"
        raise TaskNotRegisteredError(f"task {name!r} is not registered; available: {available}")
    return Environment(_resolve_backend(backend), _TASKS[name](), seed=seed)


def _resolve_backend(backend: Backend | str) -> Backend:
    if not isinstance(backend, str):
        return backend
    match backend:
        case "mock":
            return MockBackend()
        case "mujoco":
            return MuJoCoBackend()
        case _:
            raise UnknownBackendError(f"unknown backend {backend!r}; expected 'mujoco' or 'mock'")


def _load_builtin_tasks() -> None:
    import physlab.tasks  # noqa: F401


__all__ = [
    "TaskFactory",
    "TaskNotRegisteredError",
    "UnknownBackendError",
    "list_tasks",
    "make",
    "register_task",
]
