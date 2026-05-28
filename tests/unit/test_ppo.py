from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import torch

from physlab.training.ppo import ActorCritic, PPOConfig, train

ROOT = Path(__file__).resolve().parents[2]


def test_actor_critic_shapes_cpu() -> None:
    model = ActorCritic(obs_dim=4, action_dim=1)
    mean, value = model(torch.zeros((3, 4), dtype=torch.float32))

    assert mean.shape == (3, 1)
    assert value.shape == (3,)
    assert bool(torch.all(mean <= 1.0))
    assert bool(torch.all(mean >= -1.0))


def test_train_writes_jsonl_and_is_seed_deterministic(tmp_path: Path) -> None:
    config = PPOConfig(
        task="cartpole",
        total_steps=32,
        n_steps=16,
        eval_every=16,
        eval_episodes=1,
        seed=42,
        device="cpu",
        run_dir=tmp_path / "first",
        update_epochs=1,
        minibatch_size=16,
    )
    first = train(config)
    second = train(config.with_run_dir(tmp_path / "second"))

    records = [json.loads(line) for line in first.log_path.read_text(encoding="utf-8").splitlines()]
    assert records
    assert records[-1]["eval"]["success_rate"] >= 0.0
    assert "policy_loss" in records[-1]["train"]
    assert "value_loss" in records[-1]["train"]
    assert first.eval_curve == pytest.approx(second.eval_curve, abs=0.10)


def test_invalid_task_cli_mentions_registry_error() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "physlab.training.ppo",
            "--task=nope",
            "--total-steps=16",
            "--device=cpu",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "TaskNotRegisteredError" in result.stderr


def test_mps_run_does_not_crash_when_available(tmp_path: Path) -> None:
    if not torch.backends.mps.is_available():
        pytest.skip("MPS is unavailable on this runner")
    try:
        torch.empty(1, device="mps")
    except RuntimeError as exc:
        pytest.skip(f"MPS is reported available but not usable: {exc}")

    result = train(
        PPOConfig(
            task="cartpole",
            total_steps=16,
            n_steps=8,
            eval_every=8,
            eval_episodes=1,
            seed=42,
            device="mps",
            run_dir=tmp_path / "mps",
            update_epochs=1,
            minibatch_size=8,
        )
    )

    assert result.log_path.exists()


@pytest.mark.slow
def test_ppo_cartpole_converges_within_200k_steps(tmp_path: Path) -> None:
    result = train(
        PPOConfig(
            task="cartpole",
            total_steps=200_000,
            eval_every=20_000,
            target_success_rate=0.80,
            seed=42,
            device="cpu",
            run_dir=tmp_path / "solve",
        )
    )

    assert result.final_success_rate >= 0.80
