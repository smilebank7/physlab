"""physlab package."""

from typing import Any

__version__ = "0.0.0"

__all__ = ["Environment", "__version__", "list_tasks", "make", "register_task"]


def __getattr__(name: str) -> Any:
    if name == "Environment":
        from physlab.env import Environment

        return Environment
    if name in {"list_tasks", "make", "register_task"}:
        from physlab import registry

        return getattr(registry, name)
    raise AttributeError(f"module 'physlab' has no attribute {name!r}")
