#!/usr/bin/env python3
"""Generate JSON Schemas for MCP sim tools."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMAS: dict[str, object] = {
    "sim.make": {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "backend": {"type": "string", "enum": ["mujoco", "mock"]},
            "seed": {"type": "integer"},
        },
        "required": ["task"],
        "additionalProperties": False,
    },
    "sim.reset": {
        "type": "object",
        "properties": {
            "handle_id": {"type": "string"},
            "seed": {"type": "integer"},
        },
        "required": ["handle_id"],
        "additionalProperties": False,
    },
    "sim.step": {
        "type": "object",
        "properties": {
            "handle_id": {"type": "string"},
            "action": {"type": "array", "items": {"type": "number"}},
        },
        "required": ["handle_id", "action"],
        "additionalProperties": False,
    },
    "sim.observe": {
        "type": "object",
        "properties": {"handle_id": {"type": "string"}},
        "required": ["handle_id"],
        "additionalProperties": False,
    },
    "task.list": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

TARGET = Path("mcp-server/src/generated/schemas.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(SCHEMAS, indent=2, sort_keys=False) + "\n"
    if args.check:
        current = json.loads(TARGET.read_text())
        if current != SCHEMAS:
            print(f"{TARGET} is stale")
            return 1
        print(f"{TARGET} is up to date")
        return 0
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(rendered)
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
