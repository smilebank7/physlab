"""Filesystem artifact store for orchestrator runs."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from json import JSONDecodeError
from pathlib import Path

from physlab.orchestrator.iteration import Iteration
from physlab.orchestrator.run import Run


class RunStoreError(RuntimeError):
    """Raised when a run cannot be stored or read safely."""


class RunStore:
    """Filesystem-backed storage for orchestrator run artifacts."""

    def __init__(self, root: Path | str = "runs") -> None:
        self.root = Path(root)

    def path_for(self, run_id: str) -> Path:
        """Return the directory path for a run id."""

        return self.root / run_id

    def create(
        self,
        *,
        run_id: str,
        task: str,
        config: dict[str, object],
        started_at: str | None = None,
    ) -> Run:
        """Create a new run directory and write its config manifest."""

        run_dir = self.path_for(run_id)
        if run_dir.exists() and any(run_dir.iterdir()):
            raise RunStoreError(f"run {run_id!r} already exists")
        run_dir.mkdir(parents=True, exist_ok=True)
        run = Run(
            run_id=run_id,
            started_at=started_at or _utc_stamp(),
            task=task,
            config=config,
        )
        _write_json(run_dir / "config.json", run.config_payload())
        (run_dir / "manifest.jsonl").touch()
        return run

    def write_iteration(self, run: Run, iteration: Iteration, reward_code: str) -> None:
        """Persist one iteration directory and append the run manifest."""

        run_dir = self.path_for(run.run_id)
        if not run_dir.exists():
            raise RunStoreError(f"run {run.run_id!r} does not exist")
        iter_dir = run_dir / f"iter_{iteration.idx}"
        iter_dir.mkdir()
        (iter_dir / "prompt.md").write_text(iteration.prompt, encoding="utf-8")
        (iter_dir / "reward.py").write_text(reward_code, encoding="utf-8")
        _write_json(iter_dir / "eval.json", iteration.eval_metrics)
        (iter_dir / "reflection.md").write_text(iteration.reflection, encoding="utf-8")
        with (run_dir / "manifest.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(iteration.manifest_record(), sort_keys=True) + "\n")

    def read(self, run_id: str) -> Run:
        """Read a stored run and reconstruct its iteration records."""

        run_dir = self.path_for(run_id)
        try:
            raw_config = _read_json(run_dir / "config.json")
        except FileNotFoundError as exc:
            raise RunStoreError(f"run {run_id!r} is missing config.json") from exc
        run = Run(
            run_id=str(raw_config.get("run_id", run_id)),
            started_at=str(raw_config.get("started_at", "")),
            task=str(raw_config.get("task", "")),
            config=_as_dict(raw_config.get("config", {})),
        )
        manifest = run_dir / "manifest.jsonl"
        if not manifest.exists():
            return run
        for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
            try:
                record = json.loads(line)
            except JSONDecodeError as exc:
                raise RunStoreError(
                    f"JSON parse error in {manifest} line {line_number}: {exc.msg}"
                ) from exc
            run.iterations.append(_iteration_from_record(run_dir, _as_dict(record)))
        return run


def default_run_id(task: str) -> str:
    """Return a timestamped run id scoped to a task name."""

    return f"{_utc_stamp()}_{_slug(task)}"


def _iteration_from_record(run_dir: Path, record: dict[str, object]) -> Iteration:
    raw_idx = record["idx"]
    if not isinstance(raw_idx, int):
        raise RunStoreError("manifest idx must be an integer")
    idx = raw_idx
    iter_dir = run_dir / f"iter_{idx}"
    return Iteration(
        idx=idx,
        prompt=_read_optional(iter_dir / "prompt.md"),
        llm_response="",
        artifact_path=str(record.get("artifact_path", f"iter_{idx}/reward.py")),
        eval_metrics=_float_dict(record.get("eval", {})),
        status=str(record.get("status", "")),
        reflection=_read_optional(iter_dir / "reflection.md"),
    )


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        raise RunStoreError(f"JSON parse error in {path}: {exc.msg}") from exc
    return _as_dict(value)


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _as_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    raise RunStoreError("expected JSON object")


def _float_dict(value: object) -> dict[str, float]:
    payload = _as_dict(value)
    return {key: float(item) for key, item in payload.items() if isinstance(item, int | float)}


def _utc_stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
