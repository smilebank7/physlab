"""JSONL worker used by the TypeScript MCP server."""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass
from typing import Any

import numpy as np

from physlab import list_tasks, make
from physlab.env import Environment
from physlab.protocols import ActionSpec, ObsSpec


@dataclass
class WorkerState:
    """Mutable handle registry for one JSONL worker process."""

    handles: dict[str, Environment]


STATE = WorkerState(handles={})


def main() -> int:
    """Read JSONL MCP worker requests from stdin and write responses."""

    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        response = _dispatch(request)
        sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
        sys.stdout.flush()
    return 0


def _dispatch(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("id")
    command = request.get("command")
    args = request.get("args") or {}
    try:
        result = _handle(str(command), args)
        return {"id": request_id, "ok": True, "result": _jsonable(result)}
    except Exception as exc:  # noqa: BLE001 - worker boundary returns typed JSON errors.
        return {"id": request_id, "ok": False, "code": -32602, "message": str(exc)}


def _handle(command: str, args: dict[str, Any]) -> dict[str, Any]:
    match command:
        case "task.list":
            return {"tasks": list_tasks()}
        case "sim.make":
            task = str(args["task"])
            backend = str(args.get("backend", "mujoco"))
            seed = _optional_int(args.get("seed"))
            env = make(task, backend, seed=seed)
            handle_id = f"env-{uuid.uuid4().hex}"
            STATE.handles[handle_id] = env
            return {
                "handle_id": handle_id,
                "obs_spec": _spec(env.observation_space),
                "action_spec": _spec(env.action_space),
            }
        case "sim.reset":
            env = _env(str(args["handle_id"]))
            observation, info = env.reset(seed=_optional_int(args.get("seed")))
            return {"observation": observation, "info": info}
        case "sim.step":
            env = _env(str(args["handle_id"]))
            observation, reward, terminated, truncated, info = env.step(
                np.asarray(args["action"], dtype=np.float64)
            )
            return {
                "observation": observation,
                "reward": reward,
                "terminated": terminated,
                "truncated": truncated,
                "info": info,
            }
        case "sim.observe":
            env = _env(str(args["handle_id"]))
            observation, info = env.observe()
            return {"observation": observation, "info": info}
        case _:
            raise ValueError(f"unknown worker command {command!r}")


def _env(handle_id: str) -> Environment:
    try:
        return STATE.handles[handle_id]
    except KeyError as exc:
        raise ValueError(f"unknown handle_id {handle_id!r}") from exc


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int | float | str):
        return int(value)
    raise TypeError(f"expected integer-compatible value, got {type(value).__name__}")


def _spec(spec: ActionSpec | ObsSpec) -> dict[str, Any]:
    return {
        "shape": list(spec.shape),
        "dtype": str(np.dtype(spec.dtype)),
        "low": None if spec.low is None else spec.low,
        "high": None if spec.high is None else spec.high,
    }


def _jsonable(value: object) -> object:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
