"""Public type contracts for backends, envs, tasks, and agent boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import numpy as np
from numpy.typing import DTypeLike, NDArray

Array = NDArray[Any]
Observation = Array
Action = Array
Info = dict[str, object]


@dataclass(frozen=True)
class ArraySpec:
    """Shape, dtype, and optional bounds for NumPy arrays."""

    shape: tuple[int, ...]
    dtype: DTypeLike = np.float64
    low: Array | None = None
    high: Array | None = None

    def __post_init__(self) -> None:
        if not self.shape or any(dimension <= 0 for dimension in self.shape):
            raise ValueError("shape must contain positive dimensions")
        dtype = np.dtype(self.dtype)
        object.__setattr__(self, "dtype", dtype)
        for name, value in (("low", self.low), ("high", self.high)):
            if value is not None and value.shape != self.shape:
                raise ValueError(f"{name} must match shape {self.shape}")

    def contains(self, value: Array) -> bool:
        """Return true when an array matches shape, dtype kind, and bounds."""

        candidate = np.asarray(value)
        if candidate.shape != self.shape:
            return False
        if not np.can_cast(candidate.dtype, np.dtype(self.dtype), casting="same_kind"):
            return False
        if self.low is not None and bool(np.any(candidate < self.low)):
            return False
        return not (self.high is not None and bool(np.any(candidate > self.high)))

    def sample(self, rng: np.random.Generator | None = None) -> Array:
        """Draw a sample respecting finite bounds when they are present."""

        generator = rng if rng is not None else np.random.default_rng()
        low = self.low if self.low is not None else np.full(self.shape, -1.0)
        high = self.high if self.high is not None else np.full(self.shape, 1.0)
        if bool(np.all(np.isfinite(low))) and bool(np.all(np.isfinite(high))):
            return generator.uniform(low, high).astype(np.dtype(self.dtype), copy=False)
        return generator.normal(size=self.shape).astype(np.dtype(self.dtype), copy=False)


@dataclass(frozen=True)
class ObsSpec(ArraySpec):
    """Observation array specification."""


@dataclass(frozen=True)
class ActionSpec(ArraySpec):
    """Action array specification."""


@dataclass(frozen=True)
class ModelHandle:
    """Opaque model/data holder returned by a backend."""

    model_id: str
    model: object
    data: object
    spec_hash: str


@dataclass(frozen=True)
class StepResult:
    """Backend step result before Env API adaptation."""

    observation: Observation
    reward: float = 0.0
    terminated: bool = False
    truncated: bool = False
    info: Info = field(default_factory=dict)


@runtime_checkable
class Backend(Protocol):
    """Simulation backend contract."""

    def load_model(self, spec: object) -> ModelHandle:
        """Load a backend-specific model from a task model specification."""
        ...

    def step(self, handle: ModelHandle, action: Action) -> StepResult:
        """Advance one simulation step with a validated action."""
        ...

    def reset(self, handle: ModelHandle, seed: int | None = None) -> Observation:
        """Reset backend state and return the initial observation."""
        ...

    def close(self, handle: ModelHandle) -> None:
        """Release or invalidate resources associated with a model handle."""
        ...

    def name(self) -> str:
        """Return the stable backend name used in diagnostics."""
        ...

    def is_deterministic_for(self, device: str) -> bool:
        """Return whether the backend is deterministic for a device label."""
        ...


@runtime_checkable
class Env(Protocol):
    """Gymnasium-shaped environment contract."""

    action_space: ActionSpec
    observation_space: ObsSpec

    def reset(self, seed: int | None = None) -> tuple[Observation, Info]:
        """Reset the environment and return observation plus info."""
        ...

    def step(self, action: Action) -> tuple[Observation, float, bool, bool, Info]:
        """Apply one action and return the Gymnasium-shaped transition."""
        ...

    def close(self) -> None:
        """Close the environment and release backend resources."""
        ...


@runtime_checkable
class Task(Protocol):
    """Named task factory plus evaluation hooks."""

    name: str

    def make_env(self) -> Env:
        """Create a default environment for this task."""
        ...

    def success_metric(self, rollout: object) -> float:
        """Compute a normalized success score from a rollout payload."""
        ...

    def reward_signature(self) -> str:
        """Describe the task reward contract in a compact text form."""
        ...


@runtime_checkable
class RewardFunction(Protocol):
    """Callable reward contract for generated reward functions."""

    def __call__(
        self,
        observation: Observation,
        action: Action,
        next_observation: Observation,
        info: Info,
    ) -> float: ...


@runtime_checkable
class PolicyServer(Protocol):
    """Minimal policy-serving boundary; implementation is deferred."""

    def act(self, observation: Observation, info: Info | None = None) -> Action:
        """Return one action for an observation at the policy boundary."""
        ...


__all__ = [
    "Action",
    "ActionSpec",
    "Array",
    "ArraySpec",
    "Backend",
    "Env",
    "Info",
    "ModelHandle",
    "ObsSpec",
    "Observation",
    "PolicyServer",
    "RewardFunction",
    "StepResult",
    "Task",
]
