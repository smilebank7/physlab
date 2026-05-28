"""LLM client integrations."""

from typing import Any

__all__ = ["LLMClient", "MockLLMClient", "OpencodeClient"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from physlab.llm import client

        return getattr(client, name)
    raise AttributeError(f"module 'physlab.llm' has no attribute {name!r}")
