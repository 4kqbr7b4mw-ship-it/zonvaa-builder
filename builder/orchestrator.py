from typing import Any

from brain.decision_engine import DecisionEngine
from builder.planner import Planner


class Orchestrator:
    """Verbindet Entscheidung und Planung zu einem kontrollierten Ablauf."""

    def __init__(self) -> None:
        self.decision_engine = DecisionEngine()
        self.planner = Planner()

    def run(
        self,
        goal: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        decision = self.decision_engine.decide(
            goal=goal,
            context=context,
        )

        if decision["status"] != "approved":
            return {
                "decision": decision,
                "plan": [],
            }

        return {
            "decision": decision,
            "plan": self.planner.create_plan(goal),
        }
