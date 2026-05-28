from __future__ import annotations

from pathlib import Path

from physlab.llm.client import MockLLMClient
from physlab.orchestrator.reward_gen import Attempt, generate_reward
from physlab.tasks.franka_pick import FrankaPickTask

GOOD_RESPONSE = """
Here's a reward:

```python
import numpy as np

def reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float:
    return -float(np.linalg.norm(obs[14:17] - obs[21:24]))
```
"""


class RecordingMockLLMClient(MockLLMClient):
    def __init__(self, canned: str, cache_dir: Path) -> None:
        super().__init__(canned=canned, cache_dir=cache_dir)
        self.prompts: list[str] = []

    def _complete_uncached(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        self.prompts.append(prompt)
        return super()._complete_uncached(prompt, system=system, **kwargs)


def test_generate_reward_extracts_good_python_block(tmp_path: Path) -> None:
    llm = MockLLMClient(canned=GOOD_RESPONSE, cache_dir=tmp_path / "cache")

    result = generate_reward(FrankaPickTask(), llm, [], 42)

    assert result.status == "ok"
    assert result.signature == "reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float"
    assert "def reward_fn" in result.code
    assert "np.linalg.norm" in result.code
    assert len(result.hash) == 64


def test_generate_reward_rejects_forbidden_import(tmp_path: Path) -> None:
    llm = MockLLMClient(
        canned="""
```python
import os

def reward_fn(obs, action, info):
    os.system("echo should-not-run")
    return 0.0
```
""",
        cache_dir=tmp_path / "cache",
    )

    result = generate_reward(FrankaPickTask(), llm, [], 42)

    assert result.status == "forbidden_import"
    assert "import os" in result.code


def test_generate_reward_reports_parse_error_for_malformed_response(tmp_path: Path) -> None:
    llm = MockLLMClient(canned="no fenced code", cache_dir=tmp_path / "cache")

    result = generate_reward(FrankaPickTask(), llm, [], 42)

    assert result.status == "parse_error"
    assert result.code == "no fenced code"


def test_prompt_includes_task_specs_and_prior_attempts(tmp_path: Path) -> None:
    llm = RecordingMockLLMClient(canned=GOOD_RESPONSE, cache_dir=tmp_path / "cache")
    task = FrankaPickTask()
    prior = [
        Attempt(
            eval_metrics={"success_rate": 0.25, "mean_reward": -1.0},
            reflection="distance term improved early contact.",
        )
    ]

    generate_reward(task, llm, prior, 42)

    prompt = llm.prompts[0]
    assert "Franka pick-place anchor task" in prompt
    assert "observation_space" in prompt
    assert "shape=(24,)" in prompt
    assert "action_space" in prompt
    assert "shape=(7,)" in prompt
    assert "success_rate" in prompt
    assert "distance term improved early contact" in prompt
