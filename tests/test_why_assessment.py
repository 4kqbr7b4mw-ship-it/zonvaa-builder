from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from pathlib import Path

import pytest

from brain.decision_engine import DecisionEngine
from goal import WhyAssessment, WhyAssessmentReason, WhyAssessmentStatus
from goal.models import Goal
from identity.models import IdentityContext


def create_goal():
    return Goal(
        id="goal-why-assessment",
        title="Represent a WHY assessment",
        description="Keep assessment data deterministic.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="architect",
        created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )


VALID_COMBINATIONS = [
    (
        WhyAssessmentStatus.ALIGNED,
        WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    ),
    (
        WhyAssessmentStatus.CONFLICTING,
        WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
    ),
    (
        WhyAssessmentStatus.NOT_EVALUABLE,
        WhyAssessmentReason.INSUFFICIENT_ASSESSMENT_BASIS,
    ),
]


INVALID_COMBINATIONS = [
    (
        WhyAssessmentStatus.ALIGNED,
        WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
    ),
    (
        WhyAssessmentStatus.ALIGNED,
        WhyAssessmentReason.INSUFFICIENT_ASSESSMENT_BASIS,
    ),
    (
        WhyAssessmentStatus.CONFLICTING,
        WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    ),
    (
        WhyAssessmentStatus.CONFLICTING,
        WhyAssessmentReason.INSUFFICIENT_ASSESSMENT_BASIS,
    ),
    (
        WhyAssessmentStatus.NOT_EVALUABLE,
        WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    ),
    (
        WhyAssessmentStatus.NOT_EVALUABLE,
        WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
    ),
]


def create_assessment(**overrides):
    values = {
        "goal": create_goal(),
        "identity_version": "identity-version",
        "status": WhyAssessmentStatus.ALIGNED,
        "reason": WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    }
    values.update(overrides)
    return WhyAssessment(**values)


def test_status_enum_has_exact_values():
    assert list(WhyAssessmentStatus.__members__) == [
        "ALIGNED",
        "CONFLICTING",
        "NOT_EVALUABLE",
    ]
    assert [status.value for status in WhyAssessmentStatus] == [
        "aligned",
        "conflicting",
        "not_evaluable",
    ]


def test_reason_enum_has_exact_values():
    assert list(WhyAssessmentReason.__members__) == [
        "EXPLICIT_ALIGNMENT_CONFIRMED",
        "EXPLICIT_CONFLICT_CONFIRMED",
        "INSUFFICIENT_ASSESSMENT_BASIS",
    ]
    assert [reason.value for reason in WhyAssessmentReason] == [
        "explicit_alignment_confirmed",
        "explicit_conflict_confirmed",
        "insufficient_assessment_basis",
    ]


@pytest.mark.parametrize(
    "enum_type, invalid_value",
    [
        (WhyAssessmentStatus, "unknown"),
        (WhyAssessmentReason, "unknown_reason"),
    ],
)
def test_enums_reject_unknown_values(enum_type, invalid_value):
    with pytest.raises(ValueError):
        enum_type(invalid_value)


@pytest.mark.parametrize("status, reason", VALID_COMBINATIONS)
def test_valid_status_reason_combinations(status, reason):
    assessment = create_assessment(status=status, reason=reason)

    assert assessment.status is status
    assert assessment.reason is reason


@pytest.mark.parametrize("status, reason", INVALID_COMBINATIONS)
def test_all_invalid_status_reason_combinations_are_rejected(status, reason):
    with pytest.raises(ValueError, match="status/reason combination"):
        create_assessment(status=status, reason=reason)


def test_default_evidence_is_empty_immutable_tuple():
    assessment = create_assessment()

    assert assessment.evidence == ()
    assert isinstance(assessment.evidence, tuple)


def test_evidence_is_preserved_unchanged():
    evidence = ("Goal reviewed", "WHY version confirmed")

    assessment = create_assessment(evidence=evidence)

    assert assessment.evidence is evidence


def test_assessment_references_exact_goal_without_changes():
    goal = create_goal()
    original_fields = tuple(getattr(goal, field.name) for field in fields(Goal))

    assessment = create_assessment(goal=goal)

    assert assessment.goal is goal
    assert tuple(getattr(goal, field.name) for field in fields(Goal)) == original_fields


def test_identity_version_is_preserved_without_normalization():
    identity_version = " identity-version "

    assessment = create_assessment(identity_version=identity_version)

    assert assessment.identity_version == identity_version


def test_identical_assessments_are_value_equal():
    goal = create_goal()
    values = {
        "goal": goal,
        "identity_version": "identity-version",
        "status": WhyAssessmentStatus.ALIGNED,
        "reason": WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    }

    assert WhyAssessment(**values) == WhyAssessment(**values)


def test_assessment_is_immutable():
    assessment = create_assessment()

    with pytest.raises(FrozenInstanceError):
        assessment.identity_version = "changed"


@pytest.mark.parametrize("invalid_goal", [None, "goal-id", {}])
def test_invalid_goal_types_are_rejected(invalid_goal):
    with pytest.raises(TypeError, match="goal"):
        create_assessment(goal=invalid_goal)


def test_empty_identity_version_is_rejected():
    with pytest.raises(ValueError, match="identity_version"):
        create_assessment(identity_version="")


@pytest.mark.parametrize("identity_version", [None, 123, b"version"])
def test_non_string_identity_version_is_rejected(identity_version):
    with pytest.raises(TypeError, match="identity_version"):
        create_assessment(identity_version=identity_version)


def test_raw_string_status_is_rejected():
    with pytest.raises(TypeError, match="status"):
        create_assessment(status="aligned")


def test_raw_string_reason_is_rejected():
    with pytest.raises(TypeError, match="reason"):
        create_assessment(reason="explicit_alignment_confirmed")


@pytest.mark.parametrize("evidence", [[], "evidence", {"evidence"}])
def test_non_tuple_evidence_is_rejected(evidence):
    with pytest.raises(TypeError, match="evidence"):
        create_assessment(evidence=evidence)


def test_non_string_evidence_item_is_rejected():
    with pytest.raises(TypeError, match="evidence items"):
        create_assessment(evidence=("valid", 123))


def test_assessment_contains_only_contract_fields():
    assert [field.name for field in fields(WhyAssessment)] == [
        "goal",
        "identity_version",
        "status",
        "reason",
        "evidence",
    ]


def test_existing_models_and_decision_engine_remain_usable():
    goal = create_goal()
    identity = IdentityContext(
        content="# WHY",
        source=Path(__file__),
        version="identity-version",
    )
    decision = DecisionEngine().decide(
        goal=goal.title,
        context={"summary": {"git_dirty": False}, "risks": []},
    )

    assert goal.title == "Represent a WHY assessment"
    assert identity.version == "identity-version"
    assert decision["status"] == "approved"
