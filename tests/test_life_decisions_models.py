from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from typing import Tuple, get_type_hints

import pytest

from life_decisions import (
    CaseStatus,
    ChecksumAlgorithm,
    DecisionRecord,
    DecisionReviewStatus,
    DocumentReference,
    DocumentType,
    FactConfirmationStatus,
    LifeDecisionCase,
    LifeDecisionTopic,
    OpenQuestion,
    OpenQuestionStatus,
    Participant,
    ParticipantRole,
    ProfessionalField,
    ProfessionalReviewRequirement,
    ProfessionalReviewStatus,
    ReviewSchedule,
    ReviewScheduleStatus,
    Uncertainty,
    UncertaintySeverity,
    VerifiedFact,
)


NOW = datetime(2026, 7, 26, 10, 0, tzinfo=timezone.utc)


def fact(identifier="fact-1"):
    return VerifiedFact(
        id=identifier,
        statement="A named document exists.",
        source="document-reference-1",
        confirmation_status=FactConfirmationStatus.SOURCE_CONFIRMED,
        confirmed_at=NOW,
    )


def uncertainty(identifier="uncertainty-1"):
    return Uncertainty(
        id=identifier,
        description="The document may be outdated.",
        severity=UncertaintySeverity.HIGH,
        cause="No recent professional review is documented.",
        possible_impact="A future decision may rely on stale information.",
    )


def review(
    status=ProfessionalReviewStatus.OPEN,
    identifier="review-1",
):
    return ProfessionalReviewRequirement(
        id=identifier,
        field=ProfessionalField.LEGAL,
        reason="Legal effect requires independent professional review.",
        status=status,
    )


def decision(
    review_status=DecisionReviewStatus.REVIEW_REQUIRED,
    identifier="decision-1",
):
    return DecisionRecord(
        id=identifier,
        decision="Prepare the available information for professional review.",
        rationale="The source is confirmed but its current effect is uncertain.",
        used_fact_ids=("fact-1",),
        open_uncertainty_ids=("uncertainty-1",),
        professional_review_ids=("review-1",),
        review_status=review_status,
        decided_at=NOW,
        version="1",
    )


def complete_case(**changes):
    values = {
        "id": "case-1",
        "title": "Family continuity planning",
        "topic": LifeDecisionTopic.ESTATE,
        "status": CaseStatus.ACTIVE,
        "owner": "participant-1",
        "created_at": NOW,
        "updated_at": NOW,
        "participants": (
            Participant(
                "participant-1",
                "Case owner",
                ParticipantRole.CASE_OWNER,
            ),
        ),
        "document_references": (
            DocumentReference(
                "document-1",
                DocumentType.TESTAMENT,
                "user-storage://documents/testament-1",
                False,
            ),
        ),
        "verified_facts": (fact(),),
        "open_questions": (
            OpenQuestion(
                "question-1",
                "When was the document last reviewed?",
                "participant-1",
                OpenQuestionStatus.OPEN,
                "Confirm the review date with the document owner.",
            ),
        ),
        "uncertainties": (uncertainty(),),
        "professional_reviews": (review(),),
        "decisions": (decision(),),
        "review_schedules": (
            ReviewSchedule(
                "schedule-1",
                NOW,
                "Annual review",
                ReviewScheduleStatus.SCHEDULED,
            ),
        ),
    }
    values.update(changes)
    return LifeDecisionCase(**values)


def test_valid_life_decision_case_keeps_explicit_domain_objects():
    case = complete_case()

    assert case.owner == "participant-1"
    assert case.decisions[0].used_fact_ids == ("fact-1",)
    assert case.review_schedules[0].id == "schedule-1"


@pytest.mark.parametrize(
    "enum_type, values",
    [
        (
            LifeDecisionTopic,
            {
                "estate", "power_of_attorney", "advance_directive",
                "guardianship", "emergency_responsibilities",
                "family_assets", "succession", "digital_legacy",
                "personal_wishes",
            },
        ),
        (CaseStatus, {"draft", "active", "on_hold", "completed", "archived"}),
        (
            ParticipantRole,
            {
                "case_owner", "family_member", "trusted_contact",
                "professional_contact", "other",
            },
        ),
        (
            DocumentType,
            {
                "testament", "power_of_attorney", "advance_directive",
                "guardianship_directive", "emergency_information",
                "asset_overview", "succession_document", "digital_legacy",
                "personal_wishes", "other",
            },
        ),
        (ChecksumAlgorithm, {"sha256", "sha512"}),
        (
            FactConfirmationStatus,
            {"user_confirmed", "source_confirmed", "professionally_confirmed"},
        ),
        (OpenQuestionStatus, {"open", "in_clarification", "resolved"}),
        (UncertaintySeverity, {"low", "medium", "high", "critical"}),
        (
            ProfessionalField,
            {"legal", "notarial", "tax", "medical", "financial", "other"},
        ),
        (
            DecisionReviewStatus,
            {
                "unreviewed", "review_required",
                "professional_reviews_completed",
            },
        ),
        (
            ProfessionalReviewStatus,
            {"open", "in_progress", "completed"},
        ),
        (
            ReviewScheduleStatus,
            {"scheduled", "due", "completed", "cancelled"},
        ),
    ],
)
def test_public_enum_values_are_stable_and_have_no_additional_members(
    enum_type,
    values,
):
    assert {member.value for member in enum_type} == values


@pytest.mark.parametrize(
    "model",
    [
        Participant("p1", "Owner", ParticipantRole.CASE_OWNER),
        DocumentReference("d1", DocumentType.OTHER, "vault:document-1", False),
        fact(),
        OpenQuestion(
            "q1", "Question?", "p1", OpenQuestionStatus.OPEN, "Clarify."
        ),
        uncertainty(),
        review(),
        decision(),
        ReviewSchedule(
            "s1", NOW, "Annual review", ReviewScheduleStatus.SCHEDULED
        ),
        LifeDecisionCase(
            "c1", "Case", LifeDecisionTopic.PERSONAL_WISHES,
            CaseStatus.DRAFT, "p1", NOW, NOW,
        ),
    ],
)
def test_models_are_immutable(model):
    with pytest.raises(FrozenInstanceError):
        setattr(model, fields(model)[0].name, "changed")


@pytest.mark.parametrize(
    "storage_reference",
    [
        "vault:record-42\nembedded document",
        "data:text/plain;base64,SGVsbG8=",
        "A" * 256,
        "-----BEGIN DOCUMENT-----",
        " vault:record-42",
        "vault:record-42 ",
    ],
)
def test_document_reference_rejects_embedded_content(
    storage_reference,
):
    with pytest.raises(ValueError):
        DocumentReference(
            "d1", DocumentType.OTHER, storage_reference, False
        )


@pytest.mark.parametrize(
    "storage_reference",
    [
        "user-storage://documents/testament-1",
        "vault:record-42",
        "logical-reference/owner-controlled-item",
    ],
)
def test_document_reference_accepts_neutral_logical_references(
    storage_reference,
):
    reference = DocumentReference(
        "d1", DocumentType.OTHER, storage_reference, False
    )
    assert reference.storage_reference == storage_reference


def test_document_reference_has_no_document_content_field():
    assert {field.name for field in fields(DocumentReference)} == {
        "id", "document_type", "storage_reference", "analysis_authorized",
        "checksum", "checksum_algorithm",
    }


def test_document_integrity_metadata_must_be_complete():
    with pytest.raises(ValueError, match="provided together"):
        DocumentReference(
            "d1", DocumentType.OTHER, "vault:document", False,
            checksum="abc123",
        )


@pytest.mark.parametrize(
    "checksum, algorithm",
    [
        ("full document text", ChecksumAlgorithm.SHA256),
        ("a" * 63, ChecksumAlgorithm.SHA256),
        ("a" * 127, ChecksumAlgorithm.SHA512),
    ],
)
def test_checksum_accepts_only_matching_hexadecimal_digest(
    checksum,
    algorithm,
):
    with pytest.raises(ValueError, match="hexadecimal digest"):
        DocumentReference(
            "d1",
            DocumentType.OTHER,
            "vault:document",
            False,
            checksum=checksum,
            checksum_algorithm=algorithm,
        )


def test_valid_checksum_is_preserved():
    checksum = "a" * 64
    reference = DocumentReference(
        "d1",
        DocumentType.OTHER,
        "vault:document",
        False,
        checksum=checksum,
        checksum_algorithm=ChecksumAlgorithm.SHA256,
    )
    assert reference.checksum == checksum


@pytest.mark.parametrize(
    "field_name, replacement",
    [
        ("participants", lambda items: (items[0], items[0])),
        (
            "document_references",
            lambda items: (items[0], items[0]),
        ),
        ("verified_facts", lambda items: (items[0], fact())),
        (
            "open_questions",
            lambda items: (items[0], items[0]),
        ),
        ("uncertainties", lambda items: (items[0], uncertainty())),
        (
            "professional_reviews",
            lambda items: (items[0], review()),
        ),
        ("decisions", lambda items: (items[0], decision())),
        (
            "review_schedules",
            lambda items: (items[0], items[0]),
        ),
    ],
)
def test_duplicate_ids_are_rejected_per_collection(field_name, replacement):
    original = getattr(complete_case(), field_name)
    with pytest.raises(ValueError, match="unique ids"):
        complete_case(**{field_name: replacement(original)})


def test_same_id_is_allowed_in_distinct_domain_collections():
    case = complete_case(
        verified_facts=(fact("shared-id"),),
        uncertainties=(uncertainty("shared-id"),),
        decisions=(
            DecisionRecord(
                "decision-1",
                "Decision",
                "Rationale",
                ("shared-id",),
                ("shared-id",),
                ("review-1",),
                DecisionReviewStatus.REVIEW_REQUIRED,
                NOW,
                "1",
            ),
        ),
    )
    assert case.verified_facts[0].id == case.uncertainties[0].id


@pytest.mark.parametrize(
    "decision_value, message",
    [
        (
            DecisionRecord(
                "d2", "Decision", "Reason", ("foreign-fact",),
                ("uncertainty-1",), ("review-1",),
                DecisionReviewStatus.REVIEW_REQUIRED, NOW, "1",
            ),
            "facts outside",
        ),
        (
            DecisionRecord(
                "d2", "Decision", "Reason", ("fact-1",),
                ("foreign-uncertainty",), ("review-1",),
                DecisionReviewStatus.REVIEW_REQUIRED, NOW, "1",
            ),
            "uncertainties outside",
        ),
        (
            DecisionRecord(
                "d2", "Decision", "Reason", ("fact-1",),
                ("uncertainty-1",), ("foreign-review",),
                DecisionReviewStatus.REVIEW_REQUIRED, NOW, "1",
            ),
            "professional reviews outside",
        ),
    ],
)
def test_decision_references_must_belong_to_case(decision_value, message):
    with pytest.raises(ValueError, match=message):
        complete_case(decisions=(decision_value,))


def test_professional_review_completion_does_not_resolve_uncertainties():
    completed_review = review(ProfessionalReviewStatus.COMPLETED)
    completed = decision(
        DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
    )
    case = complete_case(
        professional_reviews=(completed_review,),
        decisions=(completed,),
    )

    assert case.decisions[0].review_status is (
        DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
    )
    assert case.decisions[0].open_uncertainty_ids == ("uncertainty-1",)


def test_open_review_cannot_be_recorded_as_completed():
    with pytest.raises(ValueError, match="referenced reviews are open"):
        complete_case(
            decisions=(
                decision(
                    DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
                ),
            ),
        )


def test_verified_fact_requires_traceable_source():
    with pytest.raises(ValueError, match="source"):
        VerifiedFact(
            "f1", "statement", " ",
            FactConfirmationStatus.USER_CONFIRMED, NOW,
        )


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: VerifiedFact(
            "f1", "statement", "source",
            FactConfirmationStatus.USER_CONFIRMED,
            datetime(2026, 7, 26, 10, 0),
        ),
        lambda: DecisionRecord(
            "d1", "decision", "reason", (), (), (),
            DecisionReviewStatus.UNREVIEWED,
            datetime(2026, 7, 26, 10, 0), "1",
        ),
        lambda: ReviewSchedule(
            "s1", datetime(2026, 7, 26, 10, 0),
            "trigger", ReviewScheduleStatus.SCHEDULED,
        ),
        lambda: LifeDecisionCase(
            "c1", "Case", LifeDecisionTopic.ESTATE, CaseStatus.DRAFT,
            "owner", datetime(2026, 7, 26, 10, 0), NOW,
        ),
    ],
)
def test_naive_timestamps_are_rejected(constructor):
    with pytest.raises(ValueError, match="timezone"):
        constructor()


def test_professional_review_never_claims_zonvaa_is_a_replacement():
    with pytest.raises(ValueError, match="must not be represented"):
        ProfessionalReviewRequirement(
            "r1", ProfessionalField.MEDICAL,
            "A clinician must review the information.",
            ProfessionalReviewStatus.OPEN,
            zonvaa_does_not_replace_review=False,
        )


def test_roles_and_facts_are_never_derived_by_the_case():
    case = LifeDecisionCase(
        "case-1", "Unclassified case",
        LifeDecisionTopic.PERSONAL_WISHES, CaseStatus.DRAFT,
        "owner-reference", NOW, NOW,
    )
    assert case.participants == ()
    assert case.verified_facts == ()
    assert case.decisions == ()


def test_core_collections_use_python_39_compatible_typing():
    hints = get_type_hints(LifeDecisionCase)
    assert hints["participants"] == Tuple[Participant, ...]
    assert hints["document_references"] == Tuple[DocumentReference, ...]
    assert hints["verified_facts"] == Tuple[VerifiedFact, ...]
    assert hints["review_schedules"] == Tuple[ReviewSchedule, ...]
