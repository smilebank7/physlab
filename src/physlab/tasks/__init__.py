"""Built-in task namespace."""

from physlab.tasks.cartpole import CartpoleTask
from physlab.tasks.franka_pick import FrankaPickTask

__all__ = ["CartpoleTask", "FrankaPickTask"]
