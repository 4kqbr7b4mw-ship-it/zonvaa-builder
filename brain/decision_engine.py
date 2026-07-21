from typing import Any, Optional

from goal.models import GoalContext


class DecisionEngine:
    """Trifft einfache, deterministische Entscheidungen aus Projektkontext."""

    def decide(
        self,
        goal: str,
        context: dict[str, Any],
        goal_context: Optional[GoalContext] = None,
    ) -> dict[str, Any]:
        # Reserved for the structured hand-off defined by ADR-0010.
        # Existing decision behavior intentionally remains unchanged.
        _ = goal_context
        summary = context.get("summary", {})
        risks = context.get("risks", [])

        if summary.get("git_dirty", False):
            return {
                "goal": goal,
                "status": "blocked",
                "next_action": "clean_repository",
                "reasons": risks or [
                    "Das Repository enthält unversionierte Änderungen."
                ],
            }

        return {
            "goal": goal,
            "status": "approved",
            "next_action": "plan",
            "reasons": [],
        }
