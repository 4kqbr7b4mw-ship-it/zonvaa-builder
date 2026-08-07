"""Deterministic manager for the Research -> Review v1 workflow."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .backends import AgentBackend
from .boundary import BoundaryGuard, BoundaryViolation, WorkspaceWriter
from .context_loader import ProjectContextLoader
from .cost_guard import BudgetExceeded, CostUsageGuard
from .persistence import RunWorkspace, new_run_id
from .policies import EXPECTED_ARTIFACTS, requested_forbidden_git_action
from .research_agent import ResearchAgent
from .review_agent import ReviewAgent
from .routing import build_plan
from .schemas import (
    DecisionBrief,
    ResearchReport,
    ReviewOutcome,
    ReviewReport,
    RunStatus,
    UsageRecord,
    WorkRequest,
)


class DevelopmentOrchestrator:
    def __init__(
        self,
        repository_root: Path,
        tool_root: Path,
        backend: AgentBackend,
    ) -> None:
        self.guard = BoundaryGuard(repository_root, tool_root)
        self.writer = WorkspaceWriter(self.guard)
        self.loader = ProjectContextLoader(self.guard)
        self.research_agent = ResearchAgent(backend)
        self.review_agent = ReviewAgent(backend)

    def run(
        self,
        request: WorkRequest,
        run_id: Optional[str] = None,
    ) -> DecisionBrief:
        run_id = run_id or new_run_id()
        workspace = RunWorkspace(self.writer, run_id)
        plan = build_plan(run_id, request, self.research_agent.backend.model_configuration)
        workspace.json("request.json", request)
        workspace.json("plan.json", plan)

        guard = CostUsageGuard(
            max_iterations=request.max_iterations,
            max_steps=request.max_iterations * 2,
            max_cost=request.max_cost,
        )
        traces: List[str] = []
        research: Optional[ResearchReport] = None
        reviews: List[ReviewReport] = []

        try:
            self.guard.assert_repository_changes_within_boundary()
        except BoundaryViolation as error:
            review = self._failure_review(str(error))
            brief = self._brief(
                run_id,
                request,
                RunStatus.FAILED,
                None,
                review,
                guard.snapshot(),
                traces,
                str(error),
            )
            return self._persist_final(
                workspace, brief, None, [review], verify_boundary=False
            )

        forbidden = requested_forbidden_git_action(
            [request.goal, *request.scope, *request.approval_constraints]
        )
        if forbidden:
            brief = self._brief(
                run_id,
                request,
                RunStatus.ESCALATED,
                None,
                ReviewReport(
                    outcome=ReviewOutcome.ESCALATE,
                    answered_goal=False,
                    evidence_based=False,
                    scope_respected=True,
                    facts_separated_from_uncertainty=True,
                    complexity_appropriate=True,
                    product_principle_respected=True,
                    founder_decision_required=True,
                    feedback=["Git actions are outside v1 and require a separate human workflow."],
                ),
                guard.snapshot(),
                traces,
                "forbidden Git action requested",
            )
            return self._persist_final(workspace, brief, None, reviews)

        try:
            context = self.loader.load(request.goal, request.allowed_context)
            feedback: Optional[list[str]] = None
            for _ in range(request.max_iterations):
                guard.start_iteration()
                guard.start_step()
                research, usage, trace_id = self.research_agent.run(
                    request, context, feedback
                )
                guard.add_usage(usage)
                if trace_id:
                    traces.append(trace_id)

                guard.start_step()
                review, usage, trace_id = self.review_agent.run(
                    request, context, research
                )
                guard.add_usage(usage)
                reviews.append(review)
                if trace_id:
                    traces.append(trace_id)

                if review.outcome is ReviewOutcome.ACCEPT:
                    brief = self._brief(
                        run_id,
                        request,
                        RunStatus.COMPLETED,
                        research,
                        review,
                        guard.snapshot(),
                        traces,
                    )
                    return self._persist_final(workspace, brief, research, reviews)
                if review.outcome is ReviewOutcome.ESCALATE:
                    brief = self._brief(
                        run_id,
                        request,
                        RunStatus.ESCALATED,
                        research,
                        review,
                        guard.snapshot(),
                        traces,
                    )
                    return self._persist_final(workspace, brief, research, reviews)
                feedback = review.feedback

            final_review = reviews[-1]
            exhausted = final_review.model_copy(
                update={
                    "outcome": ReviewOutcome.ESCALATE,
                    "founder_decision_required": True,
                    "feedback": [
                        *final_review.feedback,
                        "Maximum review iterations reached.",
                    ],
                }
            )
            reviews[-1] = exhausted
            brief = self._brief(
                run_id,
                request,
                RunStatus.ESCALATED,
                research,
                exhausted,
                guard.snapshot(),
                traces,
                "maximum review iterations reached",
            )
            return self._persist_final(workspace, brief, research, reviews)
        except BudgetExceeded as error:
            review = reviews[-1] if reviews else self._failure_review(str(error))
            brief = self._brief(
                run_id,
                request,
                RunStatus.BUDGET_EXCEEDED,
                research,
                review,
                guard.snapshot(),
                traces,
                str(error),
            )
            return self._persist_final(workspace, brief, research, reviews)
        except BoundaryViolation as error:
            review = self._failure_review(str(error))
            brief = self._brief(
                run_id,
                request,
                RunStatus.FAILED,
                research,
                review,
                guard.snapshot(),
                traces,
                str(error),
            )
            return self._persist_final(
                workspace, brief, research, reviews, verify_boundary=False
            )

    @staticmethod
    def _failure_review(reason: str) -> ReviewReport:
        return ReviewReport(
            outcome=ReviewOutcome.ESCALATE,
            answered_goal=False,
            evidence_based=False,
            scope_respected=False,
            facts_separated_from_uncertainty=True,
            complexity_appropriate=True,
            product_principle_respected=True,
            founder_decision_required=True,
            feedback=[reason],
        )

    @staticmethod
    def _brief(
        run_id: str,
        request: WorkRequest,
        status: RunStatus,
        research: Optional[ResearchReport],
        review: ReviewReport,
        usage: UsageRecord,
        traces: List[str],
        failure_reason: Optional[str] = None,
    ) -> DecisionBrief:
        return DecisionBrief(
            run_id=run_id,
            status=status,
            goal=request.goal,
            key_results=(research.confirmed_findings[:3] if research else []),
            confirmed_findings=(research.confirmed_findings if research else []),
            refuted_findings=(research.refuted_findings if research else []),
            open_risks=(research.risks if research else []),
            open_questions=(research.open_questions if research else []),
            review_outcome=review.outcome,
            founder_decision_required=review.founder_decision_required,
            recommended_next_step=(
                "Founder review is required."
                if review.founder_decision_required
                else "Use the reviewed decision brief; no automatic repository action follows."
            ),
            generated_files=[str(Path("runs") / run_id / name) for name in EXPECTED_ARTIFACTS],
            usage=usage,
            trace_ids=traces,
            failure_reason=failure_reason,
        )

    def _persist_final(
        self,
        workspace: RunWorkspace,
        brief: DecisionBrief,
        research: Optional[ResearchReport],
        reviews: List[ReviewReport],
        verify_boundary: bool = True,
    ) -> DecisionBrief:
        workspace.markdown("research.md", self._research_markdown(research))
        workspace.markdown("review.md", self._review_markdown(reviews, brief))
        workspace.markdown("handover.md", self._handover_markdown(brief))
        workspace.json("usage.json", brief.usage)
        workspace.json("result.json", brief)
        if verify_boundary:
            self.guard.assert_repository_changes_within_boundary()
        return brief

    @staticmethod
    def _research_markdown(research: Optional[ResearchReport]) -> str:
        if research is None:
            return "# Research\n\nNo research agent run occurred."
        lines = ["# Research", "", research.summary, "", "## Confirmed findings", ""]
        lines.extend("- {}".format(item) for item in research.confirmed_findings)
        lines.extend(["", "## Evidence", ""])
        lines.extend("- `{}`".format(path) for path in research.evidence_paths)
        lines.extend(["", "## Open questions", ""])
        lines.extend("- {}".format(item) for item in research.open_questions)
        return "\n".join(lines)

    @staticmethod
    def _review_markdown(reviews: List[ReviewReport], brief: DecisionBrief) -> str:
        if not reviews:
            return "# Review\n\nNo review agent run occurred.\n\nStatus: {}".format(
                brief.review_outcome.value
            )
        lines = ["# Review", ""]
        for index, review in enumerate(reviews, 1):
            lines.extend(
                [
                    "## Cycle {}".format(index),
                    "",
                    "Outcome: `{}`".format(review.outcome.value),
                    "",
                    *["- {}".format(item) for item in review.feedback],
                    "",
                ]
            )
        return "\n".join(lines)

    @staticmethod
    def _handover_markdown(brief: DecisionBrief) -> str:
        lines = [
            "# Decision brief",
            "",
            "- Run ID: `{}`".format(brief.run_id),
            "- Status: `{}`".format(brief.status.value),
            "- Review: `{}`".format(brief.review_outcome.value),
            "- Founder decision required: `{}`".format(
                str(brief.founder_decision_required).lower()
            ),
            "",
            "## Key results",
            "",
            *["- {}".format(item) for item in brief.key_results],
            "",
            "## Next step",
            "",
            brief.recommended_next_step,
        ]
        return "\n".join(lines)
