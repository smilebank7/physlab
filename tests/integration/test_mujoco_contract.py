from __future__ import annotations

import numpy as np

from physlab.backends.mujoco import MuJoCoBackend
from tests.integration.test_backend_contract import (
    FIXTURE,
    BackendCase,
    test_action_shape_validation,
    test_close_releases,
    test_reset_determinism,
    test_step_monotonic_time,
)

MUJOCO_CASE = BackendCase(
    name="MuJoCoBackend",
    factory=MuJoCoBackend,
    spec=FIXTURE,
    action=np.array([0.1], dtype=np.float64),
)


def test_mujoco_reset_determinism() -> None:
    test_reset_determinism(MUJOCO_CASE)


def test_mujoco_action_shape_validation() -> None:
    test_action_shape_validation(MUJOCO_CASE)


def test_mujoco_step_monotonic_time() -> None:
    test_step_monotonic_time(MUJOCO_CASE)


def test_mujoco_close_releases() -> None:
    test_close_releases(MUJOCO_CASE)
