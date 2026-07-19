from typing import Any


class DecisionEngine:
    """Trifft einfache, deterministische Entscheidungen aus Projektkontext."""

    def decide(
        self,
        goal: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
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
