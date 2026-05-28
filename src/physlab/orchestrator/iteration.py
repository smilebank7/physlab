"""Iteration records for orchestrated research loops."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Iteration:
    idx: int
    prompt: str
    llm_response: str
    artifact_path: str
    eval_metrics: dict[str, float]
    status: str
    reflection: str

    def manifest_record(self) -> dict[str, object]:
        return {
            "idx": self.idx,
            "status": self.status,
            "artifact_path": self.artifact_path,
            "eval": self.eval_metrics,
            "reflection": self.reflection,
            "llm_response_length": len(self.llm_response),
        }
