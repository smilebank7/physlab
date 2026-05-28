"""Training entry points."""

from typing import Any

__all__ = ["ActorCritic", "PPOConfig", "TrainingResult", "train"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from physlab.training import ppo

        return getattr(ppo, name)
    raise AttributeError(f"module 'physlab.training' has no attribute {name!r}")
