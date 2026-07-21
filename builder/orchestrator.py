from typing import Any, Optional

from brain.decision_engine import DecisionEngine
from builder.planner import Planner
from execution.engine import ExecutionEngine
from goal.models import GoalContext
from goal.why_assessment import WhyAssessment
from identity.models import IdentityContext


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
        goal_context: Optional[GoalContext] = None,
        identity_context: Optional[IdentityContext] = None,
        why_assessment: Optional[WhyAssessment] = None,
    ) -> dict[str, Any]:
        decision = self.decision_engine.decide(
            goal=goal,
            context=context,
            goal_context=goal_context,
            identity_context=identity_context,
            why_assessment=why_assessment,
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
