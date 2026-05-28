"""MuJoCo CPU backend."""

from __future__ import annotations

import hashlib
import threading
import weakref
from pathlib import Path

import mujoco
import numpy as np

from physlab.protocols import Action, ModelHandle, Observation, StepResult


class MuJoCoBackend:
    """Small MuJoCo wrapper implementing the backend protocol."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._model_cache: weakref.WeakValueDictionary[str, mujoco.MjModel] = (
            weakref.WeakValueDictionary()
        )
        self._counter = 0
        self._closed: set[str] = set()

    def load_model(self, spec: object) -> ModelHandle:
        source = _model_source(spec)
        with self._lock:
            model = self._model_cache.get(source.cache_key)
            if model is None:
                model = source.load()
                self._model_cache[source.cache_key] = model
            data = mujoco.MjData(model)
            self._counter += 1
            return ModelHandle(
                model_id=f"mujoco-{self._counter}",
                model=model,
                data=data,
                spec_hash=source.spec_hash,
            )

    def reset(self, handle: ModelHandle, seed: int | None = None) -> Observation:
        self._ensure_open(handle)
        model, data = _as_mujoco(handle)
        mujoco.mj_resetData(model, data)
        if seed is not None:
            rng = np.random.default_rng(seed)
            data.qpos[:] = data.qpos + rng.uniform(-0.001, 0.001, size=model.nq)
            data.qvel[:] = data.qvel + rng.uniform(-0.001, 0.001, size=model.nv)
        mujoco.mj_forward(model, data)
        return _observation(data)

    def step(self, handle: ModelHandle, action: Action) -> StepResult:
        self._ensure_open(handle)
        model, data = _as_mujoco(handle)
        action_array = np.asarray(action, dtype=np.float64)
        expected_shape = (model.nu,)
        if action_array.shape != expected_shape:
            raise ValueError(f"expected shape {expected_shape}, got {action_array.shape}")

        applied = action_array.copy()
        if model.nu > 0:
            limited = np.asarray(model.actuator_ctrllimited, dtype=bool)
            ranges = np.asarray(model.actuator_ctrlrange, dtype=np.float64)
            applied[limited] = np.clip(
                applied[limited],
                ranges[limited, 0],
                ranges[limited, 1],
            )
            data.ctrl[:] = applied

        mujoco.mj_step(model, data)
        return StepResult(
            observation=_observation(data),
            info={
                "time": float(data.time),
                "action_clipped": bool(np.any(applied != action_array)),
                "applied_action": applied.copy(),
            },
        )

    def close(self, handle: ModelHandle) -> None:
        self._closed.add(handle.model_id)

    def name(self) -> str:
        return "mujoco"

    def is_deterministic_for(self, device: str) -> bool:
        return device == "cpu"

    def _ensure_open(self, handle: ModelHandle) -> None:
        if handle.model_id in self._closed:
            raise RuntimeError(f"model handle {handle.model_id!r} is closed")


class _ModelSource:
    def __init__(self, spec: object) -> None:
        self._spec = spec
        self.cache_key, self.spec_hash = self._hashes(spec)

    def load(self) -> mujoco.MjModel:
        if isinstance(self._spec, Path):
            return mujoco.MjModel.from_xml_path(str(self._spec.expanduser().resolve()))
        if isinstance(self._spec, str):
            path = Path(self._spec).expanduser()
            if path.exists():
                return mujoco.MjModel.from_xml_path(str(path.resolve()))
            if self._spec.lstrip().startswith("<"):
                return mujoco.MjModel.from_xml_string(self._spec)
        raise TypeError("spec must be a path to an MJCF file or an MJCF XML string")

    @staticmethod
    def _hashes(spec: object) -> tuple[str, str]:
        if isinstance(spec, Path):
            path = spec.expanduser().resolve()
            body = path.read_bytes()
            path_hash = hashlib.sha256(str(path).encode()).hexdigest()
            spec_hash = hashlib.sha256(body).hexdigest()
            return path_hash, spec_hash
        if isinstance(spec, str):
            path = Path(spec).expanduser()
            if path.exists():
                resolved = path.resolve()
                body = resolved.read_bytes()
                path_hash = hashlib.sha256(str(resolved).encode()).hexdigest()
                spec_hash = hashlib.sha256(body).hexdigest()
                return path_hash, spec_hash
            if spec.lstrip().startswith("<"):
                xml_hash = hashlib.sha256(spec.encode()).hexdigest()
                return xml_hash, xml_hash
        raise TypeError("spec must be a path to an MJCF file or an MJCF XML string")


def _model_source(spec: object) -> _ModelSource:
    return _ModelSource(spec)


def _as_mujoco(handle: ModelHandle) -> tuple[mujoco.MjModel, mujoco.MjData]:
    if not isinstance(handle.model, mujoco.MjModel) or not isinstance(handle.data, mujoco.MjData):
        raise TypeError("handle does not contain MuJoCo model/data")
    return handle.model, handle.data


def _observation(data: mujoco.MjData) -> Observation:
    return np.concatenate((data.qpos, data.qvel)).astype(np.float64, copy=False)


__all__ = ["MuJoCoBackend"]
