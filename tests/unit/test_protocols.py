from __future__ import annotations

import unittest

import numpy as np

from physlab.protocols import (
    ActionSpec,
    Backend,
    Env,
    ModelHandle,
    ObsSpec,
    PolicyServer,
    RewardFunction,
    StepResult,
    Task,
)


class ProtocolTests(unittest.TestCase):
    def test_backend_protocol_accepts_structural_match(self) -> None:
        class DummyBackend:
            def load_model(self, spec: object) -> ModelHandle:
                return ModelHandle(model_id="dummy", model=None, data=None, spec_hash="hash")

            def step(self, handle: ModelHandle, action: np.ndarray) -> StepResult:
                return StepResult(observation=np.array([0.0]), reward=0.0, terminated=False)

            def reset(self, handle: ModelHandle, seed: int | None = None) -> np.ndarray:
                return np.array([0.0])

            def close(self, handle: ModelHandle) -> None:
                return None

            def name(self) -> str:
                return "dummy"

            def is_deterministic_for(self, device: str) -> bool:
                return device == "cpu"

        self.assertIsInstance(DummyBackend(), Backend)

    def test_backend_protocol_rejects_incomplete_match(self) -> None:
        class IncompleteBackend:
            pass

        self.assertNotIsInstance(IncompleteBackend(), Backend)

    def test_env_protocol_accepts_structural_match(self) -> None:
        class DummyEnv:
            action_space = ActionSpec(shape=(1,), dtype=np.float64)
            observation_space = ObsSpec(shape=(1,), dtype=np.float64)

            def reset(self, seed: int | None = None) -> tuple[np.ndarray, dict[str, object]]:
                return np.array([0.0]), {"seed": seed}

            def step(
                self,
                action: np.ndarray,
            ) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
                return action, 0.0, False, False, {}

            def close(self) -> None:
                return None

        self.assertIsInstance(DummyEnv(), Env)

    def test_task_protocol_accepts_structural_match(self) -> None:
        class DummyTask:
            name = "dummy"

            def make_env(self) -> Env:
                raise NotImplementedError

            def success_metric(self, rollout: object) -> float:
                return 1.0 if rollout else 0.0

            def reward_signature(self) -> str:
                return "reward(obs, action, next_obs) -> float"

        self.assertIsInstance(DummyTask(), Task)

    def test_reward_function_protocol_accepts_callable(self) -> None:
        class DenseReward:
            def __call__(
                self,
                observation: np.ndarray,
                action: np.ndarray,
                next_observation: np.ndarray,
                info: dict[str, object],
            ) -> float:
                del observation, action, info
                return float(next_observation.sum())

        self.assertIsInstance(DenseReward(), RewardFunction)

    def test_policy_server_protocol_accepts_act_boundary(self) -> None:
        class ConstantPolicy:
            def act(
                self,
                observation: np.ndarray,
                info: dict[str, object] | None = None,
            ) -> np.ndarray:
                del info
                return np.zeros_like(observation)

        self.assertIsInstance(ConstantPolicy(), PolicyServer)

    def test_spec_shape_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            ObsSpec(shape=(0,), dtype=np.float64)

    def test_spec_bounds_match_shape(self) -> None:
        with self.assertRaises(ValueError):
            ActionSpec(shape=(2,), dtype=np.float64, low=np.array([-1.0]))

    def test_spec_contains_array_checks_shape_and_bounds(self) -> None:
        spec = ActionSpec(
            shape=(2,),
            dtype=np.float64,
            low=np.array([-1.0, -1.0]),
            high=np.array([1.0, 1.0]),
        )
        self.assertTrue(spec.contains(np.array([0.0, 1.0])))
        self.assertFalse(spec.contains(np.array([0.0, 2.0])))
        self.assertFalse(spec.contains(np.array([0.0], dtype=np.float64)))


if __name__ == "__main__":
    unittest.main()
