"""Research-agent role facade."""

from __future__ import annotations

from typing import Optional

from .backends import AgentBackend
from .schemas import ContextBundle, ResearchReport, UsageRecord, WorkRequest


class ResearchAgent:
    def __init__(self, backend: AgentBackend) -> None:
        self.backend = backend

    def run(
        self,
        request: WorkRequest,
        context: ContextBundle,
        revision_feedback: Optional[list[str]] = None,
    ) -> tuple[ResearchReport, UsageRecord, Optional[str]]:
        result = self.backend.research(request, context, revision_feedback)
        return (
            ResearchReport.model_validate(result.output),
            result.usage,
            result.trace_id,
        )
