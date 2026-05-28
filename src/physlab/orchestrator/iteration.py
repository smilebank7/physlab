"""Iteration records for orchestrated research loops."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Iteration:
    """One persisted reward-generation iteration."""

    idx: int
    prompt: str
    llm_response: str
    artifact_path: str
    eval_metrics: dict[str, float]
    status: str
    reflection: str
    metadata: dict[str, object] = field(default_factory=dict)

    def manifest_record(self) -> dict[str, object]:
        """Return the JSONL-safe manifest payload for this iteration."""

        record = {
            "idx": self.idx,
            "status": self.status,
            "artifact_path": self.artifact_path,
            "eval": self.eval_metrics,
            "reflection": self.reflection,
            "llm_response_length": len(self.llm_response),
        }
        record.update(self.metadata)
        return record
