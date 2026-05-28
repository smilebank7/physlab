# ruff: noqa: E702,I001
"""Tiny third-party Backend tutorial: implement load/reset/step/close/name."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from physlab.protocols import Action, ModelHandle, StepResult

@dataclass(slots=True, weakref_slot=True)
class _Model:
    nq: int
    nv: int
    nu: int

@dataclass(slots=True, weakref_slot=True)
class _Data:
    obs: np.ndarray
    time: float = 0.0

class TutorialBackend:
    def __init__(self) -> None:
        self._closed: set[str] = set()
    def load_model(self, spec: object) -> ModelHandle:
        cfg = spec if isinstance(spec, dict) else {}
        model = _Model(int(cfg.get("nq", 1)), int(cfg.get("nv", 1)), int(cfg.get("nu", 1)))
        return ModelHandle("tutorial-1", model, _Data(np.zeros(model.nq + model.nv)), "tutorial")
    def reset(self, handle: ModelHandle, seed: int | None = None) -> np.ndarray:
        self._ensure_open(handle); data = _data(handle)
        data.obs = np.random.default_rng(seed).uniform(-0.001, 0.001, size=data.obs.shape)
        data.time = 0.0
        return data.obs.copy()
    def step(self, handle: ModelHandle, action: Action) -> StepResult:
        self._ensure_open(handle); model, data = _model(handle), _data(handle)
        action_array = np.asarray(action, dtype=np.float64)
        if action_array.shape != (model.nu,):
            raise ValueError(f"expected shape {(model.nu,)}, got {action_array.shape}")
        data.obs[: model.nu] += 0.01 * action_array; data.time = round(data.time + 0.01, 12)
        return StepResult(data.obs.copy(), info={"time": data.time})
    def close(self, handle: ModelHandle) -> None:
        self._closed.add(handle.model_id)
    def name(self) -> str:
        return "tutorial"
    def is_deterministic_for(self, device: str) -> bool:
        return device == "cpu"
    def _ensure_open(self, handle: ModelHandle) -> None:
        if handle.model_id in self._closed:
            raise RuntimeError("closed handle")
def _model(handle: ModelHandle) -> _Model:
    assert isinstance(handle.model, _Model); return handle.model
def _data(handle: ModelHandle) -> _Data:
    assert isinstance(handle.data, _Data); return handle.data
