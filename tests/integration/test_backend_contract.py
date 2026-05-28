from __future__ import annotations

import gc
import weakref
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest

from physlab.backends.mock import MockBackend
from physlab.backends.mujoco import MuJoCoBackend
from physlab.protocols import Backend, ModelHandle

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "pendulum.xml"


@dataclass(frozen=True)
class BackendCase:
    name: str
    factory: Callable[[], Backend]
    spec: object
    action: np.ndarray[Any, Any]

    def __str__(self) -> str:
        return self.name


CASES = [
    BackendCase(
        name="MuJoCoBackend",
        factory=MuJoCoBackend,
        spec=FIXTURE,
        action=np.array([0.1], dtype=np.float64),
    ),
    BackendCase(
        name="MockBackend",
        factory=MockBackend,
        spec={"nq": 1, "nv": 1, "nu": 1},
        action=np.array([0.1], dtype=np.float64),
    ),
]


def _load(case: BackendCase) -> tuple[Backend, ModelHandle]:
    backend = case.factory()
    return backend, backend.load_model(case.spec)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_reset_determinism(case: BackendCase) -> None:
    backend, handle = _load(case)
    try:
        first = backend.reset(handle, seed=42).copy()
        backend.step(handle, case.action)
        second = backend.reset(handle, seed=42).copy()
        assert first.tobytes() == second.tobytes()
    finally:
        backend.close(handle)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_action_shape_validation(case: BackendCase) -> None:
    backend, handle = _load(case)
    try:
        backend.reset(handle, seed=0)
        with pytest.raises(ValueError, match=r"expected shape"):
            backend.step(handle, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    finally:
        backend.close(handle)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_step_monotonic_time(case: BackendCase) -> None:
    backend, handle = _load(case)
    try:
        backend.reset(handle, seed=0)
        first = backend.step(handle, case.action)
        second = backend.step(handle, case.action)
        assert cast(float, second.info["time"]) > cast(float, first.info["time"])
    finally:
        backend.close(handle)


@pytest.mark.parametrize("case", CASES, ids=str)
def test_close_releases(case: BackendCase) -> None:
    backend, handle = _load(case)
    model_ref = weakref.ref(handle.model)
    backend.close(handle)
    del handle
    gc.collect()
    assert model_ref() is None
