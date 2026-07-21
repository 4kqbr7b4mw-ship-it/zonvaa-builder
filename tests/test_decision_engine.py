from datetime import datetime, timezone
from pathlib import Path

import pytest

from brain.decision_engine import DecisionEngine, DecisionStatus
from goal.engine import GoalEngine
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)
from identity.models import IdentityContext


def create_goal(goal_id="goal-decision-context"):
    return Goal(
        id=goal_id,
        title="Preserve Decision Engine behavior",
        description="Pass structured goal context without semantic evaluation.",
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


def decide_with_goal(
    goal_context,
    identity_context,
    why_assessment=None,
    git_dirty=False,
    risks=None,
):
    return DecisionEngine().decide(
        goal=goal_context.goal.title,
        context={
            "summary": {"git_dirty": git_dirty},
            "risks": risks or [],
        },
        goal_context=goal_context,
        identity_context=identity_context,
        why_assessment=why_assessment,
    )


def test_decision_engine_returns_decision():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": False,
        },
        "risks": [],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision == {
        "goal": "Decision Engine entwickeln",
        "status": "approved",
        "next_action": "plan",
        "reasons": [],
    }


def test_decision_engine_blocks_dirty_repository():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": True,
        },
        "risks": [
            "Der aktuelle Arbeitsstand ist noch nicht vollständig versioniert."
        ],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision["status"] == "blocked"
    assert decision["next_action"] == "clean_repository"
    assert decision["reasons"]


def test_decision_status_has_exact_values():
    assert [status.value for status in DecisionStatus] == [
        "blocked",
        "needs_review",
        "approved",
    ]


def test_goal_context_requires_identity_context():
    goal_context = create_goal_context()

    with pytest.raises(ValueError, match="identity_context"):
        DecisionEngine().decide(
            goal=goal_context.goal.title,
            context={"summary": {"git_dirty": False}, "risks": []},
            goal_context=goal_context,
        )


def test_goal_context_without_assessment_needs_review():
    result = decide_with_goal(create_goal_context(), create_identity())

    assert result["status"] == "needs_review"
    assert result["why_status"] is None
    assert result["why_reason"] is None


@pytest.mark.parametrize(
    "status, reason, expected_status",
    [
        (
            WhyAssessmentStatus.ALIGNED,
            WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
            "approved",
        ),
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
def test_why_status_determines_clean_goal_decision(status, reason, expected_status):
    goal_context = create_goal_context()
    assessment = create_assessment(goal_context.goal, status, reason)

    result = decide_with_goal(goal_context, create_identity(), assessment)

    assert result["status"] == expected_status
    assert result["why_status"] == status.value
    assert result["why_reason"] == reason.value


@pytest.mark.parametrize(
    "status, reason",
    [
        (
            WhyAssessmentStatus.ALIGNED,
            WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
        ),
        (
            WhyAssessmentStatus.CONFLICTING,
            WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
        ),
    ],
)
def test_git_dirty_blocks_regardless_of_why_status(status, reason):
    goal_context = create_goal_context()
    assessment = create_assessment(goal_context.goal, status, reason)
    technical_reason = "Repository ist nicht sauber."

    result = decide_with_goal(
        goal_context,
        create_identity(),
        assessment,
        git_dirty=True,
        risks=[technical_reason],
    )

    assert result["status"] == "blocked"
    assert result["reasons"] == [technical_reason]
    assert result["technical_reasons"] == [technical_reason]
    assert result["why_status"] == status.value
    assert result["why_reason"] == reason.value


def test_assessment_with_different_goal_is_rejected():
    goal_context = create_goal_context()
    assessment = create_assessment(create_goal("different-goal"))

    with pytest.raises(ValueError, match="goal"):
        decide_with_goal(goal_context, create_identity(), assessment)


def test_assessment_with_different_identity_version_is_rejected():
    goal_context = create_goal_context()
    assessment = create_assessment(
        goal_context.goal,
        identity_version="old-identity-version",
    )

    with pytest.raises(ValueError, match="identity_version"):
        decide_with_goal(goal_context, create_identity(), assessment)


def test_assessment_without_goal_context_is_rejected():
    assessment = create_assessment(create_goal())

    with pytest.raises(ValueError, match="goal_context"):
        DecisionEngine().decide(
            goal=assessment.goal.title,
            context={"summary": {"git_dirty": False}, "risks": []},
            why_assessment=assessment,
        )


def test_identity_without_goal_context_is_rejected():
    with pytest.raises(ValueError, match="goal_context"):
        DecisionEngine().decide(
            goal="Goal",
            context={"summary": {"git_dirty": False}, "risks": []},
            identity_context=create_identity(),
        )


def test_evidence_does_not_influence_decision():
    goal_context = create_goal_context()
    without_evidence = create_assessment(goal_context.goal)
    with_evidence = create_assessment(
        goal_context.goal,
        evidence=("First statement", "Second statement"),
    )

    first_result = decide_with_goal(
        goal_context,
        create_identity(),
        without_evidence,
    )
    second_result = decide_with_goal(
        goal_context,
        create_identity(),
        with_evidence,
    )

    assert first_result == second_result


def test_goal_mode_preserves_machine_readable_result_structure():
    goal_context = create_goal_context()
    assessment = create_assessment(goal_context.goal)

    decision = DecisionEngine().decide(
        goal=goal_context.goal.title,
        context={"summary": {"git_dirty": False}, "risks": []},
        goal_context=goal_context,
        identity_context=create_identity(),
        why_assessment=assessment,
    )

    assert decision == {
        "goal": goal_context.goal.title,
        "status": "approved",
        "next_action": "plan",
        "reasons": [],
        "technical_reasons": [],
        "why_status": "aligned",
        "why_reason": "explicit_alignment_confirmed",
    }
