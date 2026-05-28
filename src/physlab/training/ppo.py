"""Small single-environment PPO trainer."""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import traceback
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal, Self, TextIO, cast

import numpy as np
import torch
from numpy.typing import NDArray
from torch import Tensor, nn
from torch.distributions import Normal

from physlab.registry import TaskNotRegisteredError, make

DeviceName = Literal["auto", "cpu", "mps"]
FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class PPOConfig:
    """Configuration for single-environment PPO training."""

    task: str = "cartpole"
    total_steps: int = 100_000
    n_steps: int = 2_048
    eval_every: int = 10_000
    eval_episodes: int = 5
    seed: int = 42
    device: DeviceName = "cpu"
    target_success_rate: float | None = None
    run_dir: Path | None = None
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_ratio: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    learning_rate: float = 3e-4
    update_epochs: int = 4
    minibatch_size: int = 64
    reward_scale: float = 0.01

    def with_run_dir(self, run_dir: Path) -> Self:
        """Return a copy of this config with a concrete run directory."""

        return replace(self, run_dir=run_dir)


@dataclass(frozen=True)
class TrainingResult:
    """Summary produced by a PPO training run."""

    log_path: Path
    eval_curve: list[float]
    final_success_rate: float
    total_steps: int
    device: str


class ActorCritic(nn.Module):
    """Small Gaussian actor-critic network for continuous actions."""

    def __init__(self, obs_dim: int, action_dim: int) -> None:
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
        )
        self.policy_mean = nn.Linear(64, action_dim)
        self.value_head = nn.Linear(64, 1)
        self.log_std = nn.Parameter(torch.full((action_dim,), -0.7))

    def forward(self, obs: Tensor) -> tuple[Tensor, Tensor]:
        """Return bounded policy mean and scalar value predictions."""

        hidden = self.trunk(obs)
        mean = torch.tanh(self.policy_mean(hidden))
        value = self.value_head(hidden).squeeze(-1)
        return mean, value

    def distribution(self, obs: Tensor) -> tuple[Normal, Tensor]:
        """Return the Gaussian policy distribution and value estimate."""

        mean, value = self(obs)
        std = torch.exp(self.log_std).expand_as(mean)
        return Normal(mean, std), value


def train(config: PPOConfig) -> TrainingResult:
    """Train a PPO policy for one registered task."""

    _validate_config(config)
    _seed_everything(config.seed)
    device = select_device(config.device)
    run_dir = _resolve_run_dir(config.run_dir)
    log_path = run_dir / "train.jsonl"

    env = make(config.task, "mujoco", seed=config.seed)
    try:
        obs_dim = int(np.prod(env.observation_space.shape))
        action_dim = int(np.prod(env.action_space.shape))
        low = np.asarray(env.action_space.low, dtype=np.float32)
        high = np.asarray(env.action_space.high, dtype=np.float32)
        model = ActorCritic(obs_dim, action_dim).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

        obs, _ = env.reset(seed=config.seed)
        global_step = 0
        next_eval_step = config.eval_every
        eval_curve: list[float] = []
        final_success_rate = 0.0

        with log_path.open("w", encoding="utf-8") as log_file:
            while global_step < config.total_steps:
                rollout = _collect_rollout(
                    env=env,
                    model=model,
                    start_obs=obs,
                    global_step=global_step,
                    config=config,
                    device=device,
                    action_low=low,
                    action_high=high,
                )
                obs = rollout.next_obs
                global_step = rollout.global_step
                losses = _update_model(model, optimizer, rollout, config)

                if global_step >= next_eval_step or global_step >= config.total_steps:
                    final_success_rate = evaluate(
                        model=model,
                        task=config.task,
                        seed=config.seed,
                        episodes=config.eval_episodes,
                        device=device,
                        action_low=low,
                        action_high=high,
                    )
                    eval_curve.append(final_success_rate)
                    _write_record(
                        log_file,
                        {
                            "step": global_step,
                            "device": str(device),
                            "train/policy_loss": losses["policy_loss"],
                            "train/value_loss": losses["value_loss"],
                            "eval/success_rate": final_success_rate,
                            "train": losses,
                            "eval": {"success_rate": final_success_rate},
                        },
                    )
                    next_eval_step += config.eval_every
                    if (
                        config.target_success_rate is not None
                        and final_success_rate >= config.target_success_rate
                    ):
                        break

        return TrainingResult(
            log_path=log_path,
            eval_curve=eval_curve,
            final_success_rate=final_success_rate,
            total_steps=global_step,
            device=str(device),
        )
    finally:
        env.close()


@dataclass(frozen=True)
class _Rollout:
    obs: Tensor
    actions: Tensor
    log_probs: Tensor
    returns: Tensor
    advantages: Tensor
    values: Tensor
    next_obs: FloatArray
    global_step: int


def _collect_rollout(
    *,
    env: object,
    model: ActorCritic,
    start_obs: FloatArray,
    global_step: int,
    config: PPOConfig,
    device: torch.device,
    action_low: NDArray[np.float32],
    action_high: NDArray[np.float32],
) -> _Rollout:
    obs_values: list[FloatArray] = []
    action_values: list[FloatArray] = []
    log_probs: list[float] = []
    rewards: list[float] = []
    dones: list[float] = []
    values: list[float] = []
    obs = start_obs

    for _ in range(min(config.n_steps, config.total_steps - global_step)):
        obs_tensor = _obs_tensor(obs, device).unsqueeze(0)
        with torch.no_grad():
            dist, value = model.distribution(obs_tensor)
            raw_action = _sample(dist)
            log_prob = _log_prob(dist, raw_action)
        action = _bounded_action(raw_action.squeeze(0), action_low, action_high, device)
        policy_action = raw_action.squeeze(0).cpu().numpy().astype(np.float64, copy=False)
        next_obs, reward, terminated, truncated, _ = env.step(action)  # type: ignore[attr-defined]
        done = terminated or truncated

        obs_values.append(np.asarray(obs, dtype=np.float64))
        action_values.append(policy_action)
        log_probs.append(float(log_prob.cpu().item()))
        rewards.append(float(reward) * config.reward_scale)
        dones.append(float(done))
        values.append(float(value.squeeze(0).cpu().item()))
        global_step += 1

        if done:
            obs, _ = env.reset(seed=config.seed + global_step)  # type: ignore[attr-defined]
        else:
            obs = np.asarray(next_obs, dtype=np.float64)

    with torch.no_grad():
        next_value = float(model(_obs_tensor(obs, device).unsqueeze(0))[1].cpu().item())

    returns, advantages = _gae(rewards, dones, values, next_value, config.gamma, config.gae_lambda)
    return _Rollout(
        obs=torch.as_tensor(np.asarray(obs_values), dtype=torch.float32, device=device),
        actions=torch.as_tensor(np.asarray(action_values), dtype=torch.float32, device=device),
        log_probs=torch.as_tensor(log_probs, dtype=torch.float32, device=device),
        returns=torch.as_tensor(returns, dtype=torch.float32, device=device),
        advantages=torch.as_tensor(advantages, dtype=torch.float32, device=device),
        values=torch.as_tensor(values, dtype=torch.float32, device=device),
        next_obs=np.asarray(obs, dtype=np.float64),
        global_step=global_step,
    )


def _update_model(
    model: ActorCritic,
    optimizer: torch.optim.Optimizer,
    rollout: _Rollout,
    config: PPOConfig,
) -> dict[str, float]:
    advantages = (rollout.advantages - rollout.advantages.mean()) / (
        rollout.advantages.std(unbiased=False) + 1e-8
    )
    batch_size = rollout.obs.shape[0]
    minibatch_size = min(config.minibatch_size, batch_size)
    last_policy_loss = torch.tensor(0.0, device=rollout.obs.device)
    last_value_loss = torch.tensor(0.0, device=rollout.obs.device)
    last_entropy = torch.tensor(0.0, device=rollout.obs.device)

    for _ in range(config.update_epochs):
        for start in range(0, batch_size, minibatch_size):
            end = start + minibatch_size
            index = slice(start, end)
            dist, value = model.distribution(rollout.obs[index])
            new_log_prob = _log_prob(dist, rollout.actions[index])
            ratio = torch.exp(new_log_prob - rollout.log_probs[index])
            clipped_ratio = torch.clamp(ratio, 1.0 - config.clip_ratio, 1.0 + config.clip_ratio)
            policy_loss = -torch.min(
                ratio * advantages[index],
                clipped_ratio * advantages[index],
            ).mean()
            value_loss = torch.mean((rollout.returns[index] - value) ** 2)
            entropy = _entropy(dist)
            loss = policy_loss + config.value_coef * value_loss - config.entropy_coef * entropy

            optimizer.zero_grad()
            loss.backward()  # type: ignore[no-untyped-call]
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
            optimizer.step()
            last_policy_loss = policy_loss.detach()
            last_value_loss = value_loss.detach()
            last_entropy = entropy.detach()

    return {
        "policy_loss": float(last_policy_loss.cpu().item()),
        "value_loss": float(last_value_loss.cpu().item()),
        "entropy": float(last_entropy.cpu().item()),
    }


def evaluate(
    *,
    model: ActorCritic,
    task: str,
    seed: int,
    episodes: int,
    device: torch.device,
    action_low: NDArray[np.float32],
    action_high: NDArray[np.float32],
) -> float:
    """Evaluate a trained policy with deterministic mean actions."""

    lengths: list[int] = []
    env = make(task, "mujoco", seed=seed)
    try:
        max_steps = int(getattr(env.task, "max_steps", 500))
        for episode in range(episodes):
            obs, _ = env.reset(seed=seed + episode)
            length = 0
            while length < max_steps:
                with torch.no_grad():
                    mean, _ = model(_obs_tensor(obs, device).unsqueeze(0))
                action = _bounded_action(mean.squeeze(0), action_low, action_high, device)
                obs, _, terminated, truncated, _ = env.step(action)
                length += 1
                if terminated or truncated:
                    break
            lengths.append(length)
    finally:
        env.close()
    success_rate = float(np.mean(np.asarray(lengths, dtype=np.float64))) / float(max_steps)
    return min(success_rate, 1.0)


def select_device(name: DeviceName) -> torch.device:
    """Resolve an execution device name to a Torch device."""

    if name == "mps":
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS requested but torch.backends.mps is unavailable")
        return torch.device("mps")
    if name == "auto" and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _sample(dist: Normal) -> Tensor:
    return cast(Tensor, dist.sample())  # type: ignore[no-untyped-call]


def _log_prob(dist: Normal, value: Tensor) -> Tensor:
    result: Tensor = dist.log_prob(value).sum(dim=-1)  # type: ignore[no-untyped-call]
    return result


def _entropy(dist: Normal) -> Tensor:
    result: Tensor = dist.entropy().sum(dim=-1).mean()  # type: ignore[no-untyped-call]
    return result


def _bounded_action(
    raw_action: Tensor,
    action_low: NDArray[np.float32],
    action_high: NDArray[np.float32],
    device: torch.device,
) -> FloatArray:
    low = torch.as_tensor(action_low, dtype=torch.float32, device=device)
    high = torch.as_tensor(action_high, dtype=torch.float32, device=device)
    squashed = torch.tanh(raw_action)
    scaled = low + 0.5 * (squashed + 1.0) * (high - low)
    return scaled.cpu().numpy().astype(np.float64, copy=False)


def _gae(
    rewards: list[float],
    dones: list[float],
    values: list[float],
    next_value: float,
    gamma: float,
    gae_lambda: float,
) -> tuple[list[float], list[float]]:
    advantages = [0.0 for _ in rewards]
    last_gae = 0.0
    for step in reversed(range(len(rewards))):
        next_non_terminal = 1.0 - dones[step]
        next_values = next_value if step == len(rewards) - 1 else values[step + 1]
        delta = rewards[step] + gamma * next_values * next_non_terminal - values[step]
        last_gae = delta + gamma * gae_lambda * next_non_terminal * last_gae
        advantages[step] = last_gae
    returns = [advantage + value for advantage, value in zip(advantages, values, strict=True)]
    return returns, advantages


def _obs_tensor(obs: FloatArray, device: torch.device) -> Tensor:
    return torch.as_tensor(obs, dtype=torch.float32, device=device)


def _resolve_run_dir(run_dir: Path | None) -> Path:
    path = run_dir if run_dir is not None else Path("runs") / time.strftime("%Y%m%d-%H%M%S")
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_record(log_file: TextIO, record: dict[str, object]) -> None:
    line = json.dumps(record, sort_keys=True)
    log_file.write(f"{line}\n")
    log_file.flush()


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def _validate_config(config: PPOConfig) -> None:
    if config.total_steps <= 0:
        raise ValueError("total_steps must be positive")
    if config.n_steps <= 0:
        raise ValueError("n_steps must be positive")
    if config.eval_every <= 0:
        raise ValueError("eval_every must be positive")
    if config.eval_episodes <= 0:
        raise ValueError("eval_episodes must be positive")
    if config.minibatch_size <= 0:
        raise ValueError("minibatch_size must be positive")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for PPO training."""

    parser = argparse.ArgumentParser(description="Train a small PPO policy.")
    parser.add_argument("--task", default="cartpole")
    parser.add_argument("--total-steps", type=int, default=100_000)
    parser.add_argument("--eval-every", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--target-success-rate", type=float, default=None)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="cpu")
    parser.add_argument("--run-dir", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run PPO training from the command line."""

    args = build_parser().parse_args(argv)
    try:
        result = train(
            PPOConfig(
                task=args.task,
                total_steps=args.total_steps,
                eval_every=args.eval_every,
                seed=args.seed,
                target_success_rate=args.target_success_rate,
                device=args.device,
                run_dir=args.run_dir,
            )
        )
    except TaskNotRegisteredError:
        traceback.print_exc(file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "log_path": str(result.log_path),
                "success_rate": result.final_success_rate,
                "total_steps": result.total_steps,
                "device": result.device,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
