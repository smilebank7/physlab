from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TOOLS = {"ping", "sim.make", "sim.reset", "sim.step", "sim.observe", "task.list"}


def test_python_mcp_client_protocol_compliance() -> None:
    with _running_server() as url:
        transcript: list[dict[str, Any]] = []
        tools_response = _rpc(url, {"jsonrpc": "2.0", "method": "tools/list", "id": 1})
        transcript.append(tools_response)
        tools = cast(list[dict[str, Any]], cast(dict[str, Any], tools_response["result"])["tools"])
        names = {str(tool["name"]) for tool in tools}
        assert len(tools) >= 6
        assert names >= REQUIRED_TOOLS
        for tool in tools:
            assert len(str(tool["description"])) >= 20
            assert isinstance(tool["inputSchema"], dict)

        unknown = _rpc(url, {"jsonrpc": "2.0", "method": "tools/unknown", "id": 2})
        transcript.append(unknown)
        assert cast(dict[str, Any], unknown["error"])["code"] == -32601

        invalid_params = _rpc(
            url,
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "ping", "arguments": {}},
                "id": 3,
            },
        )
        transcript.append(invalid_params)
        assert cast(dict[str, Any], invalid_params["error"])["code"] == -32602

        ping = _rpc(
            url,
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "ping", "arguments": {"msg": "python-client"}},
                "id": 4,
            },
        )
        transcript.append(ping)
        content = cast(list[dict[str, str]], cast(dict[str, Any], ping["result"])["content"])
        assert content[0]["text"] == "pong: python-client"


def test_typescript_mcp_client_protocol_compliance() -> None:
    env = os.environ.copy()
    env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{env['PATH']}"
    result = subprocess.run(
        ["bun", "test", "tests/protocol_compliance.test.ts"],
        cwd=ROOT / "mcp-server",
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@contextmanager
def _running_server() -> Iterator[str]:
    port = _free_port()
    env = os.environ.copy()
    env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{env['PATH']}"
    env["PHYSLAB_MCP_PORT"] = str(port)
    server = subprocess.Popen(
        ["bun", "mcp-server/src/server.ts"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        url = f"http://127.0.0.1:{port}"
        _wait_until_healthy(server, url)
        yield url
    finally:
        _stop(server)


def _rpc(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    return cast(dict[str, Any], json.loads(urllib.request.urlopen(request, timeout=3).read()))


def _wait_until_healthy(server: subprocess.Popen[str], url: str) -> None:
    for _ in range(50):
        if server.poll() is not None:
            stdout, stderr = server.communicate()
            raise RuntimeError(f"MCP server exited early\nstdout={stdout}\nstderr={stderr}")
        try:
            urllib.request.urlopen(f"{url}/healthz", timeout=0.2).read()
            return
        except urllib.error.URLError:
            time.sleep(0.1)
    raise TimeoutError("MCP server did not become healthy")


def _stop(server: subprocess.Popen[str]) -> None:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=5)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
