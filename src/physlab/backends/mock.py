"""Deterministic in-memory backend used as the contract-test substrate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import numpy as np

from physlab.protocols import Action, ModelHandle, Observation, StepResult


@dataclass(slots=True, weakref_slot=True)
class _MockModel:
    nq: int
    nv: int
    nu: int
    dt: float
    initial_qpos: np.ndarray
    initial_qvel: np.ndarray
    ctrl_low: np.ndarray
    ctrl_high: np.ndarray


@dataclass(slots=True, weakref_slot=True)
class _MockData:
    qpos: np.ndarray
    qvel: np.ndarray
    time: float = 0.0


class MockBackend:
    """Tiny deterministic backend with linear dynamics."""

    def __init__(self, dt: float = 0.01) -> None:
        self._dt = float(dt)
        self._counter = 0
        self._closed: set[str] = set()

    def load_model(self, spec: object) -> ModelHandle:
        """Create a deterministic linear model from a dictionary spec."""

        config = dict(spec) if isinstance(spec, dict) else {}
        nq = int(config.get("nq", 1))
        nv = int(config.get("nv", nq))
        nu = int(config.get("nu", nv))
        if nq <= 0 or nv <= 0 or nu <= 0:
            raise ValueError("nq, nv, and nu must be positive")

        initial_qpos = _array_from_config(config, "initial_qpos", nq)
        initial_qvel = _array_from_config(config, "initial_qvel", nv)
        ctrl_low, ctrl_high = _ctrl_range(config, nu)
        model = _MockModel(
            nq=nq,
            nv=nv,
            nu=nu,
            dt=float(config.get("dt", self._dt)),
            initial_qpos=initial_qpos,
            initial_qvel=initial_qvel,
            ctrl_low=ctrl_low,
            ctrl_high=ctrl_high,
        )
        data = _MockData(qpos=initial_qpos.copy(), qvel=initial_qvel.copy())
        spec_hash = _hash_config(config | {"nq": nq, "nv": nv, "nu": nu})
        self._counter += 1
        return ModelHandle(
            model_id=f"mock-{self._counter}",
            model=model,
            data=data,
            spec_hash=spec_hash,
        )

    def reset(self, handle: ModelHandle, seed: int | None = None) -> Observation:
        """Reset mock state, optionally adding deterministic seed jitter."""

        self._ensure_open(handle)
        model = _as_model(handle.model)
        data = _as_data(handle.data)
        if seed is None:
            data.qpos = model.initial_qpos.copy()
            data.qvel = model.initial_qvel.copy()
        else:
            rng = np.random.default_rng(seed)
            data.qpos = model.initial_qpos + rng.uniform(-0.001, 0.001, size=model.nq)
            data.qvel = model.initial_qvel + rng.uniform(-0.001, 0.001, size=model.nv)
        data.time = 0.0
        return _observation(data)

    def step(self, handle: ModelHandle, action: Action) -> StepResult:
        """Advance the linear mock dynamics by one fixed time step."""

        self._ensure_open(handle)
        model = _as_model(handle.model)
        data = _as_data(handle.data)
        action_array = np.asarray(action, dtype=np.float64)
        expected_shape = (model.nu,)
        if action_array.shape != expected_shape:
            raise ValueError(f"expected shape {expected_shape}, got {action_array.shape}")
        applied = np.clip(action_array, model.ctrl_low, model.ctrl_high)
        old_qvel = data.qvel.copy()
        data.qpos = data.qpos + model.dt * old_qvel[: model.nq]
        data.qvel = data.qvel + model.dt * applied[: model.nv]
        data.time = round(data.time + model.dt, 12)
        return StepResult(
            observation=_observation(data),
            info={
                "time": data.time,
                "action_clipped": bool(np.any(applied != action_array)),
                "applied_action": applied.copy(),
            },
        )

    def close(self, handle: ModelHandle) -> None:
        """Mark a model handle closed for future safety checks."""

        self._closed.add(handle.model_id)

    def name(self) -> str:
        """Return the backend registry name."""

        return "mock"

    def is_deterministic_for(self, device: str) -> bool:
        """Report deterministic support for CPU execution."""

        return device == "cpu"

    def _ensure_open(self, handle: ModelHandle) -> None:
        if handle.model_id in self._closed:
            raise RuntimeError(f"model handle {handle.model_id!r} is closed")


def _array_from_config(config: dict[str, Any], key: str, size: int) -> np.ndarray:
    value = config.get(key)
    if value is None:
        return np.zeros(size, dtype=np.float64)
    array = np.asarray(value, dtype=np.float64)
    if array.shape != (size,):
        raise ValueError(f"{key} expected shape {(size,)}, got {array.shape}")
    return array


def _ctrl_range(config: dict[str, Any], size: int) -> tuple[np.ndarray, np.ndarray]:
    value = config.get("ctrlrange")
    if value is None:
        return (
            np.full(size, -np.inf, dtype=np.float64),
            np.full(size, np.inf, dtype=np.float64),
        )
    array = np.asarray(value, dtype=np.float64)
    if array.shape != (size, 2):
        raise ValueError(f"ctrlrange expected shape {(size, 2)}, got {array.shape}")
    return array[:, 0], array[:, 1]


def _hash_config(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, default=list).encode()
    return hashlib.sha256(payload).hexdigest()


def _as_model(value: object) -> _MockModel:
    if not isinstance(value, _MockModel):
        raise TypeError("handle does not contain a Mock model")
    return value


def _as_data(value: object) -> _MockData:
    if not isinstance(value, _MockData):
        raise TypeError("handle does not contain Mock data")
    return value


def _observation(data: _MockData) -> Observation:
    return np.concatenate((data.qpos, data.qvel)).astype(np.float64, copy=False)


__all__ = ["MockBackend"]
