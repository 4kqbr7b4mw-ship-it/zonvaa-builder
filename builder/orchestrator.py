from typing import Any, Iterable, Optional

from brain.decision_engine import DecisionEngine
from builder.planner import Planner
from execution.engine import ExecutionEngine, ExecutionError
from execution.models import DocumentArtifact
from goal.models import GoalContext
from goal.why_assessment import WhyAssessment
from identity.models import IdentityContext


class GoalApplyError(RuntimeError):
    """An approved goal failed during document application."""

    def __init__(self, message: str, result: dict[str, Any]) -> None:
        super().__init__(message)
        self.result = result


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
        document_artifacts: Optional[Iterable[DocumentArtifact]] = None,
        apply: bool = False,
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

        artifacts = list(document_artifacts or [])
        if artifacts:
            plan = self.planner.create_plan(
                goal,
                document_artifacts=artifacts,
            )
        else:
            plan = self.planner.create_plan(goal)

        if apply and artifacts:
            try:
                execution = self.execution_engine.execute(plan)
            except ExecutionError as exc:
                result = {
                    "decision": decision,
                    "plan": plan,
                    "execution": exc.as_execution_result(),
                }
                raise GoalApplyError(str(exc), result) from exc
            except (ValueError, RuntimeError) as exc:
                result = {
                    "decision": decision,
                    "plan": plan,
                    "execution": {
                        "status": "failed",
                        "completed_steps": [],
                        "rolled_back_steps": [],
                        "remaining_resources": [],
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                            "rollback_errors": [],
                        },
                    },
                }
                raise GoalApplyError(str(exc), result) from exc
        else:
            execution = self.execution_engine.prepare(plan)

        return {
            "decision": decision,
            "plan": plan,
            "execution": execution,
        }
