"""Review-agent role facade."""

from __future__ import annotations

from typing import Optional

from .backends import AgentBackend
from .schemas import (
    ContextBundle,
    ResearchReport,
    ReviewReport,
    UsageRecord,
    WorkRequest,
)


class ReviewAgent:
    def __init__(self, backend: AgentBackend) -> None:
        self.backend = backend

    def run(
        self,
        request: WorkRequest,
        context: ContextBundle,
        research: ResearchReport,
    ) -> tuple[ReviewReport, UsageRecord, Optional[str]]:
        result = self.backend.review(request, context, research)
        return ReviewReport.model_validate(result.output), result.usage, result.trace_id
