from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from physlab.orchestrator.evaluator import evaluate_reward
from physlab.orchestrator.reward_gen import RewardCode
from physlab.tasks.cartpole import CartpoleTask

BASELINE_CODE = """
import numpy as np

def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    return 1.0 if abs(float(obs[1])) < 0.2 else 0.0
"""


def _reward(code: str) -> RewardCode:
    return RewardCode(code=code, signature="reward_fn(obs, action, info)", hash="test", status="ok")


@pytest.mark.slow
def test_evaluate_cartpole_baseline_reward_smoke() -> None:
    result = evaluate_reward(
        _reward(BASELINE_CODE),
        CartpoleTask(),
        num_rollouts=5,
        train_steps=20_000,
        seed=42,
    )

    assert result.error is None
    assert result.success_rate > 0.50
    assert result.training_curve


def test_evaluate_nan_reward_returns_error() -> None:
    result = evaluate_reward(
        _reward(
            """
def reward_fn(obs, action, info):
    return float("nan")
"""
        ),
        CartpoleTask(),
        num_rollouts=1,
        train_steps=16,
        seed=42,
    )

    assert result.error == "nan_reward"
    assert result.success_rate == 0.0


def test_evaluate_forbidden_import_rejected_before_training() -> None:
    result = evaluate_reward(
        _reward(
            """
import os

def reward_fn(obs, action, info):
    return 0.0
"""
        ),
        CartpoleTask(),
        num_rollouts=1,
        train_steps=16,
        seed=42,
    )

    assert result.error == "forbidden_import"


def test_evaluate_timeout_kills_subprocess() -> None:
    result = evaluate_reward(
        _reward(BASELINE_CODE),
        CartpoleTask(),
        num_rollouts=1,
        train_steps=99_999_999,
        seed=42,
        timeout_s=0.1,
    )

    assert result.error == "timeout"
    assert result.wall_clock_s < 5.0


def test_reward_code_never_executes_in_main_process(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_exec(*args: object, **kwargs: object) -> None:
        raise AssertionError("main process exec called")

    monkeypatch.setattr(builtins, "exec", fail_exec)

    result = evaluate_reward(
        _reward(BASELINE_CODE),
        CartpoleTask(),
        num_rollouts=1,
        train_steps=16,
        seed=42,
    )

    assert result.error is None


def test_baseline_reward_file_matches_expected_contract() -> None:
    path = Path("src/physlab/tasks/cartpole_baseline_reward.py")
    assert "def reward_fn" in path.read_text(encoding="utf-8")
