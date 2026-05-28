from __future__ import annotations

import sys

import numpy as np

from physlab.backends.mock import MockBackend
from physlab.protocols import Backend


def test_mock_backend_implements_protocol() -> None:
    assert isinstance(MockBackend(), Backend)


def test_mock_backend_does_not_import_mujoco() -> None:
    sys.modules.pop("mujoco", None)
    backend = MockBackend()
    handle = backend.load_model({"nq": 2, "nv": 2, "nu": 2})
    backend.reset(handle, seed=1)
    assert "mujoco" not in sys.modules


def test_mock_backend_linear_dynamics_are_deterministic() -> None:
    backend = MockBackend(dt=0.1)
    handle = backend.load_model(
        {"nq": 1, "nv": 1, "nu": 1, "initial_qpos": [0.0], "initial_qvel": [1.0]}
    )
    backend.reset(handle)
    result = backend.step(handle, np.array([2.0], dtype=np.float64))
    assert np.allclose(result.observation, np.array([0.1, 1.2]))
    assert result.info["time"] == 0.1
