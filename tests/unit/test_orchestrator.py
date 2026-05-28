from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from physlab.llm.client import MockLLMClient
from physlab.orchestrator.loop import MockEvaluator, MockRewardGenerator, OrchestratorLoop
from physlab.orchestrator.store import RunStore, RunStoreError

ROOT = Path(__file__).resolve().parents[2]


def test_orchestrator_loop_with_mocks_writes_three_iterations(tmp_path: Path) -> None:
    store = RunStore(tmp_path / "runs")
    client = MockLLMClient(canned="mock response", cache_dir=tmp_path / "cache")
    loop = OrchestratorLoop(
        task_name="franka_pick",
        llm_client=client,
        num_iterations=3,
        store=store,
        reward_generator=MockRewardGenerator(),
        evaluator=MockEvaluator(),
        seed=42,
    )

    run = loop.run(run_id="test-run")

    run_dir = tmp_path / "runs" / "test-run"
    manifest_lines = (run_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
    assert run.run_id == "test-run"
    assert len(run.iterations) == 3
    assert len(manifest_lines) == 3
    for idx, line in enumerate(manifest_lines):
        record = json.loads(line)
        assert record["idx"] == idx
        assert record["status"] == "completed"
        assert isinstance(record["eval"]["success_rate"], float)
        assert (run_dir / f"iter_{idx}" / "prompt.md").exists()
        assert (run_dir / f"iter_{idx}" / "reward.py").exists()
        assert (run_dir / f"iter_{idx}" / "eval.json").exists()
        assert (run_dir / f"iter_{idx}" / "reflection.md").exists()


def test_run_store_rejects_corrupted_manifest(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "half-baked"
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text("{}", encoding="utf-8")
    (run_dir / "manifest.jsonl").write_text('{"idx":0,"status":"in_progress"', encoding="utf-8")

    with pytest.raises(RunStoreError, match="JSON parse error"):
        RunStore(tmp_path / "runs").read("half-baked")


def test_orchestrator_outputs_are_deterministic_with_run_id(tmp_path: Path) -> None:
    first = _run_mock_loop(tmp_path / "first")
    second = _run_mock_loop(tmp_path / "second")

    assert _tree_bytes(first) == _tree_bytes(second)


def test_cli_mock_happy_path_and_bad_resume(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "physlab.orchestrator",
            "--task=franka_pick",
            "--iterations=3",
            "--llm=mock",
            "--run-id=test-run",
            "--runs-dir",
            str(run_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (run_root / "test-run" / "manifest.jsonl").exists()
    assert len((run_root / "test-run" / "manifest.jsonl").read_text().splitlines()) == 3

    bad_run = run_root / "half-baked"
    bad_run.mkdir()
    (bad_run / "config.json").write_text("{}", encoding="utf-8")
    (bad_run / "manifest.jsonl").write_text('{"idx":0,"status":"in_progress"', encoding="utf-8")
    bad = subprocess.run(
        [
            sys.executable,
            "-m",
            "physlab.orchestrator",
            "--task=franka_pick",
            "--resume=half-baked",
            "--runs-dir",
            str(run_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert bad.returncode != 0
    assert "JSON parse error" in bad.stderr


def _run_mock_loop(root: Path) -> Path:
    store = RunStore(root)
    client = MockLLMClient(canned="same response", cache_dir=root / "cache")
    loop = OrchestratorLoop(
        task_name="franka_pick",
        llm_client=client,
        num_iterations=3,
        store=store,
        reward_generator=MockRewardGenerator(),
        evaluator=MockEvaluator(),
        seed=42,
    )
    loop.run(run_id="deterministic")
    return root / "deterministic"


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
