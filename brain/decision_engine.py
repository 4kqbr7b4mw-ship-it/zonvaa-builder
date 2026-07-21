from enum import Enum
from typing import Any, Optional

from goal.models import GoalContext
from goal.why_assessment import WhyAssessment, WhyAssessmentStatus
from identity.models import IdentityContext


class DecisionStatus(str, Enum):
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"


class DecisionEngine:
    """Trifft einfache, deterministische Entscheidungen aus Projektkontext."""

    def decide(
        self,
        goal: str,
        context: dict[str, Any],
        goal_context: Optional[GoalContext] = None,
        identity_context: Optional[IdentityContext] = None,
        why_assessment: Optional[WhyAssessment] = None,
    ) -> dict[str, Any]:
        summary = context.get("summary", {})
        risks = context.get("risks", [])

        if goal_context is None:
            if identity_context is not None or why_assessment is not None:
                raise ValueError(
                    "identity_context and why_assessment require goal_context"
                )
            return self._legacy_decision(goal, summary, risks)

        if identity_context is None:
            raise ValueError("goal_context requires identity_context")

        if why_assessment is not None:
            if why_assessment.goal != goal_context.goal:
                raise ValueError("why_assessment goal does not match goal_context")
            if why_assessment.identity_version != identity_context.version:
                raise ValueError(
                    "why_assessment identity_version does not match identity_context"
                )

        technical_reasons = self._technical_reasons(summary, risks)
        why_status = (
            why_assessment.status.value if why_assessment is not None else None
        )
        why_reason = (
            why_assessment.reason.value if why_assessment is not None else None
        )

        if technical_reasons:
            status = DecisionStatus.BLOCKED
            next_action = "clean_repository"
        elif why_assessment is None:
            status = DecisionStatus.NEEDS_REVIEW
            next_action = "review"
        elif why_assessment.status is WhyAssessmentStatus.CONFLICTING:
            status = DecisionStatus.BLOCKED
            next_action = "review"
        elif why_assessment.status is WhyAssessmentStatus.NOT_EVALUABLE:
            status = DecisionStatus.NEEDS_REVIEW
            next_action = "review"
        else:
            status = DecisionStatus.APPROVED
            next_action = "plan"

        return {
            "goal": goal,
            "status": status.value,
            "next_action": next_action,
            "reasons": technical_reasons,
            "technical_reasons": technical_reasons,
            "why_status": why_status,
            "why_reason": why_reason,
        }

    def _legacy_decision(
        self,
        goal: str,
        summary: dict[str, Any],
        risks: list[Any],
    ) -> dict[str, Any]:
        technical_reasons = self._technical_reasons(summary, risks)
        if technical_reasons:
            return {
                "goal": goal,
                "status": DecisionStatus.BLOCKED.value,
                "next_action": "clean_repository",
                "reasons": technical_reasons,
            }

        return {
            "goal": goal,
            "status": DecisionStatus.APPROVED.value,
            "next_action": "plan",
            "reasons": [],
        }

    def _technical_reasons(
        self,
        summary: dict[str, Any],
        risks: list[Any],
    ) -> list[Any]:
        if not summary.get("git_dirty", False):
            return []
        return risks or ["Das Repository enthält unversionierte Änderungen."]
