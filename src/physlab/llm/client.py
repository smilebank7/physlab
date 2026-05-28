"""opencode LLM client wrapper with deterministic file caching."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Minimal completion interface used by local reward orchestration."""

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        """Return a completion for a prompt and optional system text."""
        ...

    def name(self) -> str:
        """Return the stable client name recorded in run artifacts."""
        ...


class _CachedClient:
    def __init__(
        self,
        cache_dir: Path | str = ".physlab_cache/llm",
        run_dir: Path | str | None = None,
        model_id: str | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = Path(run_dir) if run_dir is not None else _default_run_dir()
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.model_id = model_id or self.name()

    def name(self) -> str:
        raise NotImplementedError

    def complete(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        start = time.perf_counter()
        key = self._cache_key(prompt, system, kwargs)
        cache_path = self.cache_dir / f"{key}.json"
        cache_hit = cache_path.exists()
        if cache_hit:
            completion = str(json.loads(cache_path.read_text())["completion"])
        else:
            completion = self._complete_uncached(prompt, system=system, **kwargs).strip()
            cache_path.write_text(
                json.dumps(
                    {
                        "client": self.name(),
                        "model_id": self.model_id,
                        "completion": completion,
                    },
                    sort_keys=True,
                )
            )
        self._record_call(prompt, completion, start, cache_hit)
        return completion

    def _complete_uncached(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        raise NotImplementedError

    def _cache_key(self, prompt: str, system: str | None, kwargs: dict[str, object]) -> str:
        payload = {
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
            "system_hash": None if system is None else hashlib.sha256(system.encode()).hexdigest(),
            "model_id": self.model_id,
            "params": kwargs,
        }
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _record_call(self, prompt: str, completion: str, start: float, cache_hit: bool) -> None:
        event = {
            "client": self.name(),
            "model_id": self.model_id,
            "prompt_length": len(prompt),
            "response_length": len(completion),
            "latency_ms": round((time.perf_counter() - start) * 1000, 3),
            "cache_hit": cache_hit,
            "cost_tokens_stubbed": 0,
        }
        with (self.run_dir / "llm.jsonl").open("a") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


class MockLLMClient(_CachedClient):
    """Deterministic cached LLM client for CI and local smoke tests."""

    def __init__(
        self,
        canned: str,
        cache_dir: Path | str = ".physlab_cache/llm",
        run_dir: Path | str | None = None,
    ) -> None:
        self.canned = canned
        self.call_count = 0
        canned_hash = hashlib.sha256(canned.encode()).hexdigest()[:16]
        super().__init__(cache_dir=cache_dir, run_dir=run_dir, model_id=f"mock:{canned_hash}")

    def name(self) -> str:
        """Return the mock client name."""

        return "mock"

    def _complete_uncached(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        del prompt, system, kwargs
        self.call_count += 1
        return self.canned


class OpencodeClient(_CachedClient):
    """Cached wrapper around the opencode CLI."""

    def __init__(
        self,
        executable: str = "opencode",
        cache_dir: Path | str = ".physlab_cache/llm",
        run_dir: Path | str | None = None,
    ) -> None:
        self.executable = executable
        super().__init__(cache_dir=cache_dir, run_dir=run_dir, model_id="opencode")

    def name(self) -> str:
        """Return the canonical local-agent client name."""

        return "opencode"

    def _complete_uncached(self, prompt: str, system: str | None = None, **kwargs: object) -> str:
        full_prompt = prompt if system is None else f"{system}\n\n{prompt}"
        timeout_value = kwargs.get("timeout", 120)
        timeout = float(timeout_value) if isinstance(timeout_value, int | float | str) else 120.0
        result = subprocess.run(
            [self.executable, "run", "--format", "default"],
            input=full_prompt,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "opencode failed")
        return str(result.stdout)


def main(argv: list[str] | None = None) -> int:
    """Run a tiny command-line probe for the configured opencode client."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--cache-dir", default=".physlab_cache/llm")
    args = parser.parse_args(argv)
    if args.probe:
        executable = shutil.which("opencode")
        if executable is None:
            print("opencode not found on PATH", file=sys.stderr)
            return 1
        client = OpencodeClient(executable=executable, cache_dir=args.cache_dir)
        client.complete("say hi", timeout=120)
        print("opencode probe OK")
        return 0
    parser.print_help()
    return 0


def _default_run_dir() -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path("runs") / stamp


if __name__ == "__main__":
    raise SystemExit(main())
