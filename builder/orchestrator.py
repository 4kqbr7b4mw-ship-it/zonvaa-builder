from typing import Any

from brain.decision_engine import DecisionEngine
from builder.planner import Planner
from execution.engine import ExecutionEngine


class Orchestrator:
    """Verbindet Entscheidung, Planung und Ausführungsvorbereitung."""

    def __init__(self) -> None:
        self.decision_engine = DecisionEngine()
        self.planner = Planner()
        self.execution_engine = ExecutionEngine()

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
                "execution": [],
            }

        plan = self.planner.create_plan(goal)

        return {
            "decision": decision,
            "plan": plan,
            "execution": self.execution_engine.prepare(plan),
        }
