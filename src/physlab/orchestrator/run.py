"""Run records for orchestrated experiments."""

from __future__ import annotations

from dataclasses import dataclass, field

from physlab.orchestrator.iteration import Iteration


@dataclass
class Run:
    run_id: str
    started_at: str
    task: str
    config: dict[str, object]
    iterations: list[Iteration] = field(default_factory=list)

    def config_payload(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "task": self.task,
            "config": self.config,
        }
