"""Built-in task namespace."""

from physlab.tasks.cartpole import CartpoleTask
from physlab.tasks.franka_pick import FrankaPickTask
from physlab.tasks.locomotion import AntStandTask

__all__ = ["AntStandTask", "CartpoleTask", "FrankaPickTask"]
