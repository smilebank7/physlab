from __future__ import annotations

import numpy as np

from physlab import register_task
from physlab.protocols import ActionSpec, ObsSpec

XML = """
<mujoco model="hello_task">
  <option timestep="0.01"/>
  <worldbody>
    <body name="point">
      <joint name="x" type="slide" axis="1 0 0" damping="0.1"/>
      <geom type="sphere" size="0.03" mass="1"/>
    </body>
  </worldbody>
  <actuator>
    <motor joint="x" ctrlrange="-1 1" ctrllimited="true"/>
  </actuator>
</mujoco>
"""


class HelloTask:
    name = "hello_task"
    model_spec = XML
    action_space = ActionSpec(
        shape=(1,),
        dtype=np.float64,
        low=np.array([-1.0], dtype=np.float64),
        high=np.array([1.0], dtype=np.float64),
    )
    observation_space = ObsSpec(shape=(2,), dtype=np.float64)
    max_steps = 25

    def reward(self, observation: np.ndarray, action: np.ndarray, info: dict[str, object]) -> float:
        del action, info
        return 1.0 - min(abs(float(observation[0])), 1.0)

    def terminate(self, observation: np.ndarray, info: dict[str, object]) -> bool:
        return bool(abs(float(observation[0])) < 0.01 and int(info.get("step_count", 0)) > 0)

    def success_metric(self, rollout: object) -> float:
        return 1.0 if isinstance(rollout, list) and rollout else 0.0

    def reward_signature(self) -> str:
        return "reward=1-min(abs(x),1); terminate near x=0 after first step"


register_task("hello_task", HelloTask)
