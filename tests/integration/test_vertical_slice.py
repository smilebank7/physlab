from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def test_vertical_slice_cli() -> None:
    result = subprocess.run(
        [sys.executable, "examples/hello_cartpole.py", "--seed=42"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "episode_reward=" in result.stdout


def test_vertical_slice_via_mcp() -> None:
    server = _start_server()
    try:
        result = subprocess.run(
            ["bun", "examples/hello_cartpole_via_mcp.ts", "42"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        assert "episode_reward=" in result.stdout
    finally:
        server.terminate()
        server.wait(timeout=5)


def test_mcp_server_killed_mid_episode_surfaces_connection_error() -> None:
    server = _start_server()
    made = _call_tool("sim.make", {"task": "cartpole", "backend": "mujoco", "seed": 42}, 1)
    handle_id = str(made["handle_id"])
    server.terminate()
    server.wait(timeout=5)
    try:
        _call_tool("sim.step", {"handle_id": handle_id, "action": [0]}, 2)
    except urllib.error.URLError as exc:
        assert "Connection refused" in str(exc) or "Remote end closed" in str(exc)
    else:
        raise AssertionError("expected a clean connection error after server termination")


def _start_server() -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{env['PATH']}"
    server = subprocess.Popen(
        ["bun", "mcp-server/src/server.ts"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    for _ in range(50):
        if server.poll() is not None:
            stdout, stderr = server.communicate()
            raise RuntimeError(f"MCP server exited early\nstdout={stdout}\nstderr={stderr}")
        try:
            urllib.request.urlopen("http://127.0.0.1:8765/healthz", timeout=0.2).read()
            return server
        except urllib.error.URLError:
            time.sleep(0.1)
    server.terminate()
    raise TimeoutError("MCP server did not become healthy")


def _call_tool(name: str, arguments: dict[str, Any], request_id: int) -> dict[str, Any]:
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": request_id,
        }
    ).encode()
    request = urllib.request.Request(
        "http://127.0.0.1:8765",
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    response = json.loads(urllib.request.urlopen(request, timeout=3).read())
    if "error" in response:
        raise RuntimeError(response["error"])
    return dict(response["result"])
