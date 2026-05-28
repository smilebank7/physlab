from __future__ import annotations

import gc
import weakref
from pathlib import Path
from typing import Any, cast

import numpy as np

from physlab.backends.mujoco import MuJoCoBackend
from physlab.protocols import Backend, ModelHandle, StepResult

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "pendulum.xml"


def test_mujoco_backend_implements_protocol() -> None:
    backend = MuJoCoBackend()
    assert isinstance(backend, Backend)
    assert backend.name() == "mujoco"
    assert backend.is_deterministic_for("cpu")
    assert not backend.is_deterministic_for("mps")


def test_loads_from_string_path_and_xml_string() -> None:
    backend = MuJoCoBackend()
    path_handle = backend.load_model(str(FIXTURE))
    xml_handle = backend.load_model(FIXTURE.read_text())
    try:
        assert path_handle.spec_hash == xml_handle.spec_hash
    finally:
        backend.close(path_handle)
        backend.close(xml_handle)


def test_invalid_model_spec_raises_type_error() -> None:
    backend = MuJoCoBackend()
    with np.testing.assert_raises_regex(TypeError, "MJCF"):
        backend.load_model({"not": "a model"})


def test_step_100() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    try:
        backend.reset(handle, seed=42)
        result = StepResult(observation=np.array([], dtype=np.float64))
        for _ in range(100):
            result = backend.step(handle, np.array([0.0], dtype=np.float64))
        assert result.observation.shape == (2,)
        assert np.isfinite(result.observation).all()
    finally:
        backend.close(handle)


def test_reset_determinism() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    try:
        first = backend.reset(handle, seed=42).copy()
        for _ in range(10):
            backend.step(handle, np.array([0.25], dtype=np.float64))
        second = backend.reset(handle, seed=42).copy()
        assert first.tobytes() == second.tobytes()
    finally:
        backend.close(handle)


def test_action_clipping_respects_ctrlrange() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    try:
        backend.reset(handle, seed=0)
        result = backend.step(handle, np.array([100.0], dtype=np.float64))
        assert result.info["action_clipped"] is True
        applied = cast(np.ndarray[Any, Any], result.info["applied_action"])
        assert np.array_equal(applied, np.array([1.0]))
    finally:
        backend.close(handle)


def test_invalid_action_shape_raises_helpful_error() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    try:
        backend.reset(handle, seed=0)
        with np.testing.assert_raises_regex(ValueError, r"expected shape \(1,\), got \(3,\)"):
            backend.step(handle, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    finally:
        backend.close(handle)


def test_close_releases_model_memory() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    model_ref = weakref.ref(handle.model)
    backend.close(handle)
    del handle
    gc.collect()
    assert model_ref() is None


def test_closed_handle_and_wrong_handle_type_raise() -> None:
    backend = MuJoCoBackend()
    handle = backend.load_model(FIXTURE)
    backend.close(handle)
    with np.testing.assert_raises_regex(RuntimeError, "closed"):
        backend.reset(handle)

    wrong = ModelHandle(model_id="wrong", model=object(), data=object(), spec_hash="x")
    with np.testing.assert_raises_regex(TypeError, "MuJoCo"):
        backend.step(wrong, np.array([0.0], dtype=np.float64))
