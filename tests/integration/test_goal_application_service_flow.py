from datetime import datetime, timezone

from builder.goal_application_service import GoalApplicationService
from builder.preflight import PreflightService
from builder.runtime import RuntimeManager
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)


def test_booted_runtime_reaches_pending_execution(monkeypatch):
    runtime = RuntimeManager().boot()
    goal = Goal(
        id="goal-application-integration",
        title="Run the complete application flow",
        description="Compose the booted runtime and existing engines.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )
    assessment = WhyAssessment(
        goal=goal,
        identity_version=runtime.identity_context.version,
        status=WhyAssessmentStatus.ALIGNED,
        reason=WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    )
    service = GoalApplicationService(
        runtime,
        mission_context=PreflightService(runtime).build(),
    )

    def clean_git(command):
        if command[:2] == ["git", "status"]:
            return "Keine Ausgabe."
        if command[:2] == ["git", "log"]:
            return "d6c2f08 Integrate goal-aware orchestration"
        raise AssertionError("Unexpected command: {}".format(command))

    monkeypatch.setattr(service.context_collector, "_run_command", clean_git)

    result = service.run(
        goal=goal,
        role="architect",
        memory_types=["project_memory"],
        constitution_rules=["Follow the WHY"],
        why_assessment=assessment,
    )

    assert service.context_collector.runtime is runtime
    assert result["decision"]["status"] == "approved"
    assert result["decision"]["why_status"] == "aligned"
    assert len(result["plan"]) == 2
    assert all(step["execution_status"] == "pending" for step in result["execution"])
