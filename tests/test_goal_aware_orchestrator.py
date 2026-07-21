from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

from builder.orchestrator import Orchestrator
from goal.engine import GoalEngine
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)
from identity.models import IdentityContext


def create_goal(goal_id="goal-orchestration"):
    return Goal(
        id=goal_id,
        title="Integrate goal-aware orchestration",
        description="Pass explicit evaluation inputs through the orchestrator.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )


def create_goal_context(goal=None):
    return GoalEngine().create_context(
        goal=goal or create_goal(),
        role="architect",
        memory_types=["project_memory"],
        constitution_rules=["Follow the WHY"],
        verified_facts={"tests": "passing"},
        project_state={"git_clean": True},
    )


def create_identity(version="identity-version"):
    return IdentityContext(
        content="# WHY",
        source=Path("WHY.md"),
        version=version,
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


def goal_run(
    status=WhyAssessmentStatus.ALIGNED,
    reason=WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    assessment=True,
    git_dirty=False,
    evidence=(),
):
    goal_context = create_goal_context()
    identity_context = create_identity()
    why_assessment = None
    if assessment:
        why_assessment = create_assessment(
            goal_context.goal,
            status=status,
            reason=reason,
            evidence=evidence,
        )
    result = Orchestrator().run(
        goal=goal_context.goal.title,
        context={
            "summary": {"git_dirty": git_dirty},
            "risks": ["Repository ist nicht sauber."] if git_dirty else [],
        },
        goal_context=goal_context,
        identity_context=identity_context,
        why_assessment=why_assessment,
    )
    return result


def test_legacy_approved_call_keeps_existing_result_and_plan():
    result = Orchestrator().run(
        goal="Legacy goal",
        context={"summary": {"git_dirty": False}, "risks": []},
    )

    assert result["decision"] == {
        "goal": "Legacy goal",
        "status": "approved",
        "next_action": "plan",
        "reasons": [],
    }
    assert result["plan"]
    assert result["execution"]


def test_legacy_technical_blocker_creates_no_plan_or_execution():
    result = Orchestrator().run(
        goal="Legacy goal",
        context={
            "summary": {"git_dirty": True},
            "risks": ["Repository ist nicht sauber."],
        },
    )

    assert result["decision"]["status"] == "blocked"
    assert result["plan"] == []
    assert result["execution"] == []


def test_goal_inputs_are_forwarded_unchanged_to_decision_engine():
    orchestrator = Orchestrator()
    goal_context = create_goal_context()
    identity_context = create_identity()
    assessment = create_assessment(goal_context.goal)
    context = {"summary": {"git_dirty": False}, "risks": []}
    orchestrator.decision_engine = Mock()
    orchestrator.decision_engine.decide.return_value = {
        "status": "needs_review"
    }

    orchestrator.run(
        goal=goal_context.goal.title,
        context=context,
        goal_context=goal_context,
        identity_context=identity_context,
        why_assessment=assessment,
    )

    orchestrator.decision_engine.decide.assert_called_once_with(
        goal=goal_context.goal.title,
        context=context,
        goal_context=goal_context,
        identity_context=identity_context,
        why_assessment=assessment,
    )


def test_aligned_goal_creates_plan_and_pending_execution():
    result = goal_run()

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
def test_non_approved_why_status_creates_no_plan_or_execution(
    status,
    reason,
    expected_status,
):
    result = goal_run(status=status, reason=reason)

    assert result["decision"]["status"] == expected_status
    assert result["plan"] == []
    assert result["execution"] == []


def test_missing_assessment_remains_needs_review_without_plan_or_execution():
    result = goal_run(assessment=False)

    assert result["decision"]["status"] == "needs_review"
    assert result["decision"]["why_status"] is None
    assert result["plan"] == []
    assert result["execution"] == []


def test_needs_review_remains_distinct_from_blocked():
    review = goal_run(assessment=False)
    blocked = goal_run(
        status=WhyAssessmentStatus.CONFLICTING,
        reason=WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
    )

    assert review["decision"]["status"] == "needs_review"
    assert blocked["decision"]["status"] == "blocked"


def test_git_dirty_overrides_alignment_and_preserves_both_results():
    result = goal_run(git_dirty=True)

    assert result["decision"]["status"] == "blocked"
    assert result["decision"]["technical_reasons"] == [
        "Repository ist nicht sauber."
    ]
    assert result["decision"]["why_status"] == "aligned"
    assert result["decision"]["why_reason"] == "explicit_alignment_confirmed"
    assert result["plan"] == []
    assert result["execution"] == []


def test_mismatched_assessment_goal_is_rejected_by_decision_engine():
    goal_context = create_goal_context()
    assessment = create_assessment(create_goal("different-goal"))

    with pytest.raises(ValueError, match="goal"):
        Orchestrator().run(
            goal=goal_context.goal.title,
            context={"summary": {"git_dirty": False}, "risks": []},
            goal_context=goal_context,
            identity_context=create_identity(),
            why_assessment=assessment,
        )


def test_mismatched_identity_version_is_rejected_by_decision_engine():
    goal_context = create_goal_context()
    assessment = create_assessment(
        goal_context.goal,
        identity_version="different-version",
    )

    with pytest.raises(ValueError, match="identity_version"):
        Orchestrator().run(
            goal=goal_context.goal.title,
            context={"summary": {"git_dirty": False}, "risks": []},
            goal_context=goal_context,
            identity_context=create_identity(),
            why_assessment=assessment,
        )


def test_evidence_does_not_change_plan_or_execution():
    without_evidence = goal_run()
    with_evidence = goal_run(evidence=("First statement", "Second statement"))

    assert without_evidence == with_evidence


def test_orchestrator_does_not_create_an_assessment():
    result = goal_run(assessment=False)

    assert result["decision"]["why_status"] is None
    assert result["decision"]["why_reason"] is None


@pytest.mark.parametrize("decision_status", ["blocked", "needs_review"])
def test_planner_and_execution_are_not_called_without_approval(decision_status):
    orchestrator = Orchestrator()
    orchestrator.decision_engine = Mock()
    orchestrator.decision_engine.decide.return_value = {
        "status": decision_status
    }
    orchestrator.planner = Mock()
    orchestrator.execution_engine = Mock()

    result = orchestrator.run(
        goal="Goal",
        context={"summary": {"git_dirty": False}, "risks": []},
    )

    orchestrator.planner.create_plan.assert_not_called()
    orchestrator.execution_engine.prepare.assert_not_called()
    assert result["plan"] == []
    assert result["execution"] == []


def test_complete_goal_aware_flow_uses_existing_components():
    result = goal_run()

    assert result["decision"]["status"] == "approved"
    assert result["decision"]["why_status"] == "aligned"
    assert len(result["plan"]) == 2
    assert len(result["execution"]) == 2
    assert all(step["execution_status"] == "pending" for step in result["execution"])
