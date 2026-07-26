from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

import brain.context_collector as collector_module
from brain.context_analyzer import ContextAnalyzer
from brain.context_collector import ContextCollector
from builder.goal_application_service import GoalApplicationService
from builder.preflight import (
    PreflightError,
    PreflightService,
    WorkflowContext,
)
from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)
from identity.models import IdentityContext
from identity.loader import IdentityLoader
from knowledge.memory import MemoryType


def create_goal(goal_id="goal-application-service"):
    return Goal(
        id=goal_id,
        title="Run the goal application service",
        description="Compose existing application components.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )


def create_runtime(git_clean=True):
    runtime = RuntimeManager()
    runtime.identity_context = IdentityContext(
        content="# WHY",
        source=Path("WHY.md"),
        version="identity-version",
    )
    runtime.constitution = "Full constitution text that must not be parsed."
    runtime.verified_facts = {"tests": "passing"}
    runtime.knowledge = {
        "adr": [],
        "protocols": [],
        "handovers": [],
        "project": [],
        "sessions": [],
        "sources": [],
        "verified_facts": runtime.verified_facts,
    }
    runtime.latest_context = None
    runtime.project_state = {
        "python_version": "3.9.6",
        "pytest_version": "8.4.2",
        "git_branch": "feature",
        "git_commit": "abc1234",
        "git_clean": git_clean,
        "verified_facts": runtime.verified_facts,
    }
    runtime.goal_engine = GoalEngine()
    return runtime


def create_project_context(runtime, git_dirty=False):
    return {
        "project_root": "/project",
        "files": [],
        "important_files": {},
        "sessions": {},
        "latest_session": {"path": "Nicht vorhanden", "content": ""},
        "verified_facts": runtime.verified_facts,
        "project_state": runtime.project_state,
        "git": {
            "status": " M file.py" if git_dirty else "Keine Ausgabe.",
            "recent_commits": "commit",
        },
    }


def create_service(runtime, git_dirty=False, **overrides):
    collector = Mock()
    collector.runtime = runtime
    collector.collect.return_value = create_project_context(runtime, git_dirty)
    return GoalApplicationService(
        runtime=runtime,
        mission_context=PreflightService(runtime).build(),
        context_collector=collector,
        **overrides,
    )


def create_assessment(
    goal,
    status=WhyAssessmentStatus.ALIGNED,
    reason=WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    identity_version="identity-version",
    evidence=(),
):
    return WhyAssessment(
        goal=goal,
        identity_version=identity_version,
        status=status,
        reason=reason,
        evidence=evidence,
    )


def run_service(service, goal, assessment=None):
    return service.run(
        goal=goal,
        role="architect",
        memory_types=["project_memory", MemoryType.KNOWLEDGE],
        constitution_rules=["Follow the WHY"],
        why_assessment=assessment,
    )


def test_context_collector_uses_injected_runtime(tmp_path, monkeypatch):
    runtime = create_runtime()
    collector = ContextCollector(runtime)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collector, "_run_command", lambda command: "Keine Ausgabe.")
    monkeypatch.setattr(
        collector_module,
        "get_runtime",
        lambda: pytest.fail("global runtime must not be used"),
    )

    context = collector.collect()

    assert collector.runtime is runtime
    assert context["verified_facts"] is runtime.verified_facts
    assert context["project_state"] is runtime.project_state


def test_context_collector_without_injection_uses_singleton(monkeypatch, tmp_path):
    runtime = create_runtime()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(collector_module, "get_runtime", lambda: runtime)
    collector = ContextCollector()
    monkeypatch.setattr(collector, "_run_command", lambda command: "Keine Ausgabe.")

    context = collector.collect()

    assert collector.runtime is None
    assert context["verified_facts"] is runtime.verified_facts


def test_default_service_collector_uses_exact_runtime(monkeypatch):
    runtime = create_runtime()
    monkeypatch.setattr(
        collector_module,
        "get_runtime",
        lambda: pytest.fail("global runtime must not be used"),
    )

    service = GoalApplicationService(
        runtime,
        mission_context=PreflightService(runtime).build(),
    )

    assert service.runtime is runtime
    assert service.context_collector.runtime is runtime


def test_service_passes_invocation_and_runtime_data_to_goal_engine():
    runtime = create_runtime()
    goal = create_goal()
    role = "reviewer"
    memory_types = [MemoryType.PROJECT, "knowledge_memory"]
    rules = ["Rule one", "Rule two"]
    goal_engine = Mock(wraps=runtime.goal_engine)
    orchestrator = Mock()
    orchestrator.run.return_value = {"sentinel": True}
    service = create_service(
        runtime,
        goal_engine=goal_engine,
        orchestrator=orchestrator,
    )

    result = service.run(goal, role, memory_types, rules)

    goal_engine.create_context.assert_called_once_with(
        goal=goal,
        role=role,
        memory_types=memory_types,
        constitution_rules=rules,
        verified_facts=runtime.verified_facts,
        project_state=runtime.project_state,
    )
    goal_context = orchestrator.run.call_args.kwargs["goal_context"]
    workflow_context = orchestrator.run.call_args.kwargs["workflow_context"]
    assert goal_context.goal is goal
    assert goal_context.role == role
    assert goal_context.memory_types == (
        MemoryType.PROJECT,
        MemoryType.KNOWLEDGE,
    )
    assert goal_context.constitution_rules == tuple(rules)
    assert goal_context.verified_facts == runtime.verified_facts
    assert goal_context.project_state == runtime.project_state
    assert isinstance(workflow_context, WorkflowContext)
    assert workflow_context.git_commit == "abc1234"
    assert orchestrator.run.call_args.kwargs["identity_context"] is runtime.identity_context
    assert result is orchestrator.run.return_value


def test_service_does_not_extract_rules_from_runtime_constitution():
    runtime = create_runtime()
    rules = ["Explicit invocation rule"]
    goal_engine = Mock(wraps=runtime.goal_engine)
    service = create_service(runtime, goal_engine=goal_engine)

    service.run(create_goal(), "architect", ["project_memory"], rules)

    assert goal_engine.create_context.call_args.kwargs["constitution_rules"] is rules
    assert runtime.constitution not in rules


def test_service_rejects_non_goal_value():
    service = create_service(create_runtime())

    with pytest.raises(TypeError, match="Goal instance"):
        service.run("goal", "architect", ["project_memory"], [])


def test_service_rejects_unbooted_runtime():
    with pytest.raises(RuntimeError, match="booted runtime"):
        GoalApplicationService(RuntimeManager())


def test_service_rejects_booted_runtime_without_preflight():
    with pytest.raises(PreflightError, match="MissionContext"):
        GoalApplicationService(create_runtime())


def test_service_rejects_invalid_mandatory_mission_context():
    runtime = create_runtime()
    context = PreflightService(runtime).build()
    invalid = replace(
        context,
        constitution={"status": "missing"},
    )

    with pytest.raises(PreflightError, match="validated MissionContext"):
        GoalApplicationService(runtime, mission_context=invalid)


def test_service_revalidates_context_before_each_run():
    runtime = create_runtime()
    context = PreflightService(runtime).build()
    service = create_service(runtime)
    service.mission_context = context
    service.preflight.clock = lambda: (
        context.generated_at + timedelta(minutes=6)
    )

    with pytest.raises(PreflightError, match="stale"):
        run_service(service, create_goal())


def test_service_passes_only_minimal_workflow_context_to_orchestrator():
    runtime = create_runtime()
    context = PreflightService(runtime).build()
    orchestrator = Mock()
    orchestrator.run.return_value = {
        "decision": {},
        "plan": [],
        "execution": [],
    }
    service = GoalApplicationService(
        runtime,
        mission_context=context,
        context_collector=create_service(runtime).context_collector,
        orchestrator=orchestrator,
    )

    run_service(service, create_goal())

    assert service.mission_context is context
    assert "mission_context" not in orchestrator.run.call_args.kwargs
    workflow_context = orchestrator.run.call_args.kwargs["workflow_context"]
    assert workflow_context == context.for_workflow()
    assert not hasattr(workflow_context, "verified_facts")
    assert not hasattr(workflow_context, "knowledge")
    with pytest.raises(TypeError):
        context.project_state["git_clean"] = False


def test_without_assessment_needs_review_without_plan_or_execution():
    result = run_service(create_service(create_runtime()), create_goal())

    assert result["decision"]["status"] == "needs_review"
    assert result["decision"]["why_status"] is None
    assert result["plan"] == []
    assert result["execution"] == []


def test_aligned_assessment_approves_plan_and_pending_execution():
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(goal)

    result = run_service(create_service(runtime), goal, assessment)

    assert result["decision"]["status"] == "approved"
    assert result["plan"]
    assert result["execution"]
    assert all(step["execution_status"] == "pending" for step in result["execution"])


@pytest.mark.parametrize(
    "status, reason, expected_status",
    [
        (
            WhyAssessmentStatus.CONFLICTING,
            WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
            "blocked",
        ),
        (
            WhyAssessmentStatus.NOT_EVALUABLE,
            WhyAssessmentReason.INSUFFICIENT_ASSESSMENT_BASIS,
            "needs_review",
        ),
    ],
)
def test_non_approved_assessment_creates_no_plan_or_execution(
    status,
    reason,
    expected_status,
):
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(goal, status=status, reason=reason)

    result = run_service(create_service(runtime), goal, assessment)

    assert result["decision"]["status"] == expected_status
    assert result["plan"] == []
    assert result["execution"] == []


def test_git_dirty_overrides_aligned_assessment():
    runtime = create_runtime(git_clean=False)
    goal = create_goal()
    assessment = create_assessment(goal)

    result = run_service(create_service(runtime, git_dirty=True), goal, assessment)

    assert result["decision"]["status"] == "blocked"
    assert result["decision"]["why_status"] == "aligned"
    assert result["plan"] == []
    assert result["execution"] == []


def test_assessment_with_other_goal_error_is_forwarded():
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(create_goal("other-goal"))

    with pytest.raises(ValueError, match="goal"):
        run_service(create_service(runtime), goal, assessment)


def test_assessment_with_other_identity_version_error_is_forwarded():
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(goal, identity_version="other-version")

    with pytest.raises(ValueError, match="identity_version"):
        run_service(create_service(runtime), goal, assessment)


def test_evidence_does_not_change_service_result():
    runtime = create_runtime()
    goal = create_goal()
    without_evidence = create_assessment(goal)
    with_evidence = create_assessment(goal, evidence=("Evidence",))

    first = run_service(create_service(runtime), goal, without_evidence)
    second = run_service(create_service(runtime), goal, with_evidence)

    assert first == second


def test_service_forwards_assessment_and_orchestrator_result_unchanged():
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(goal)
    orchestrator = Mock()
    expected = {"decision": object(), "plan": object(), "execution": object()}
    orchestrator.run.return_value = expected
    service = create_service(runtime, orchestrator=orchestrator)

    result = run_service(service, goal, assessment)

    assert orchestrator.run.call_args.kwargs["why_assessment"] is assessment
    assert result is expected


def test_service_does_not_create_goal_assessment_or_identity():
    runtime = create_runtime()
    goal = create_goal()
    identity = runtime.identity_context
    service = create_service(runtime)

    result = run_service(service, goal)

    assert result["decision"]["goal"] == goal.title
    assert result["decision"]["why_status"] is None
    assert runtime.identity_context is identity


def test_service_does_not_reload_identity(monkeypatch):
    runtime = create_runtime()
    service = create_service(runtime)
    monkeypatch.setattr(
        IdentityLoader,
        "load",
        lambda self: pytest.fail("identity must not be loaded by the service"),
    )

    result = run_service(service, create_goal())

    assert result["decision"]["status"] == "needs_review"


def test_complete_flow_from_booted_runtime():
    runtime = create_runtime()
    goal = create_goal()
    assessment = create_assessment(goal)
    service = create_service(runtime)

    result = service.run(
        goal=goal,
        role="architect",
        memory_types=["project_memory"],
        constitution_rules=["Follow the WHY"],
        why_assessment=assessment,
    )

    assert result["decision"]["status"] == "approved"
    assert result["decision"]["why_status"] == "aligned"
    assert len(result["plan"]) == 2
    assert all(step["execution_status"] == "pending" for step in result["execution"])
