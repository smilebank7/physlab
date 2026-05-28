from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

from physlab.llm.client import LLMClient, MockLLMClient, OpencodeClient
from physlab.llm.client import main as llm_main


def test_mock_llm_client_round_trip_and_protocol(tmp_path: Path) -> None:
    client = MockLLMClient(canned="hello", cache_dir=tmp_path / "cache", run_dir=tmp_path / "run")
    assert isinstance(client, LLMClient)
    assert client.complete("test prompt", system="sys") == "hello"
    assert client.name() == "mock"


def test_cache_hit_uses_file_and_does_not_invoke_twice(tmp_path: Path) -> None:
    client = MockLLMClient(canned="hello", cache_dir=tmp_path / "cache", run_dir=tmp_path / "run")
    assert client.complete("same prompt", temperature=0) == "hello"
    assert client.complete("same prompt", temperature=0) == "hello"
    assert client.call_count == 1
    cache_files = list((tmp_path / "cache").glob("*.json"))
    assert len(cache_files) == 1
    payload = json.loads(cache_files[0].read_text())
    assert payload["completion"] == "hello"


def test_telemetry_records_metadata_without_prompt_text(tmp_path: Path) -> None:
    client = MockLLMClient(
        canned="sensitive response",
        cache_dir=tmp_path / "cache",
        run_dir=tmp_path / "run",
    )
    client.complete("secret prompt")
    telemetry = (tmp_path / "run" / "llm.jsonl").read_text().strip().splitlines()
    event = json.loads(telemetry[-1])
    assert event["prompt_length"] == len("secret prompt")
    assert event["response_length"] == len("sensitive response")
    assert "secret prompt" not in telemetry[-1]


def test_opencode_client_subprocess_is_mocked(tmp_path: Path) -> None:
    completed = subprocess.CompletedProcess(
        args=["opencode"],
        returncode=0,
        stdout="opencode hello\n",
        stderr="",
    )
    with patch("subprocess.run", return_value=completed) as run:
        client = OpencodeClient(
            executable="opencode",
            cache_dir=tmp_path / "cache",
            run_dir=tmp_path / "run",
        )
        assert client.complete("say hi", model="local") == "opencode hello"
    run.assert_called_once()
    kwargs = run.call_args.kwargs
    assert run.call_args.args[0] == ["opencode", "run", "--format", "default"]
    assert kwargs["input"] == "say hi"
    assert kwargs["text"] is True


def test_probe_missing_opencode_returns_nonzero(capsys: Any) -> None:
    with patch("shutil.which", return_value=None):
        assert llm_main(["--probe"]) == 1
    err = capsys.readouterr().err
    assert "opencode not found" in err


def test_probe_success_uses_opencode_client(tmp_path: Path, capsys: Any) -> None:
    with (
        patch("shutil.which", return_value="/bin/opencode"),
        patch.object(OpencodeClient, "complete", return_value="hi") as complete,
    ):
        assert llm_main(["--probe", "--cache-dir", str(tmp_path / "cache")]) == 0
    complete.assert_called_once()
    out = capsys.readouterr().out
    assert "opencode probe OK" in out
