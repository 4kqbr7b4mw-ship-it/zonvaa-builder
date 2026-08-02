from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from guardian_understanding import (
    B3ProfessionalDecisionBoundaryContract,
    B3ProfessionalDecisionBoundaryContractValidator,
    BoundaryReference,
    ClassificationReference,
    NonConfirmationCode,
    OrientationProviderType,
    ProfessionalBoundaryCapability,
    ProfessionalBoundaryReviewTopic,
    ProfessionalDecisionBoundaryValidationError,
    ProfessionalReviewStatus,
    SourceChainReference,
    UrgencyStatus,
)


VALIDATOR = B3ProfessionalDecisionBoundaryContractValidator()


def professional_boundary(**changes):
    values = {
        "professional_boundary_id": "professional-boundary-1",
        "classification_reference": ClassificationReference("classification-1"),
        "boundary_reference": BoundaryReference("boundary-1"),
        "source_chain_references": (SourceChainReference("source-chain-1"),),
        "general_orientation_reference": None,
        "personal_preparation_reference": None,
        "acknowledgement": "Die Bedeutung der Frage wurde sachlich anerkannt.",
        "non_confirmation_code": NonConfirmationCode.LEGAL_CASE_DECISION_NOT_CONFIRMABLE,
        "non_confirmation_text": "Diese konkrete Entscheidung kann nicht bestätigt werden.",
        "professional_boundary": "Die konkrete rechtliche Bewertung bleibt einer Fachperson vorbehalten.",
        "safe_general_orientation": "Allgemeine Orientierung wurde bereitgestellt.",
        "preparation_guidance": "Vorhandene Angaben können für die Prüfung geordnet werden.",
        "professional_review_topics": (
            ProfessionalBoundaryReviewTopic(
                "topic-1",
                "Dokumentprüfung",
                "Die konkrete Dokumentfassung fachlich prüfen.",
                (SourceChainReference("source-chain-1"),),
            ),
        ),
        "urgency_status": UrgencyStatus.NOT_DECLARED_URGENT,
        "urgent_help_notice": None,
        "provider_type": OrientationProviderType.TYPED_INPUT_ADAPTER,
        "provider_reference": "adapter:b3-1",
        "professional_review_status": ProfessionalReviewStatus.REQUIRED,
        "professional_review_reference": None,
        "created_at": datetime(2026, 8, 2, 8, 0, tzinfo=timezone.utc),
        "capabilities": (
            ProfessionalBoundaryCapability.RECORD_PROVIDED_BOUNDARY,
        ),
    }
    values.update(changes)
    return B3ProfessionalDecisionBoundaryContract(**values)


def test_complete_immutable_contract_is_returned_unchanged():
    value = professional_boundary()
    assert VALIDATOR.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.non_confirmation_text = "Geändert"


@pytest.mark.parametrize(
    "field",
    (
        "professional_boundary_id",
        "acknowledgement",
        "non_confirmation_text",
        "professional_boundary",
        "safe_general_orientation",
        "preparation_guidance",
        "provider_reference",
    ),
)
def test_required_text_must_not_be_empty(field):
    with pytest.raises(ValueError, match=field):
        professional_boundary(**{field: ""})


def test_required_references_are_non_empty():
    with pytest.raises(ValueError, match="classification_id"):
        ClassificationReference("")
    with pytest.raises(ValueError, match="boundary_id"):
        BoundaryReference("")
    with pytest.raises(ValueError, match="source_chain_id"):
        SourceChainReference("")


def test_source_chains_are_required_and_unique():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as missing:
        VALIDATOR.validate(professional_boundary(source_chain_references=()))
    assert missing.value.code == "SOURCE_CHAIN_REFERENCE_REQUIRED"
    ref = SourceChainReference("source-chain-1")
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as duplicate:
        VALIDATOR.validate(
            professional_boundary(source_chain_references=(ref, ref))
        )
    assert duplicate.value.code == "DUPLICATE_SOURCE_CHAIN_REFERENCE"


@pytest.mark.parametrize("code", tuple(NonConfirmationCode))
def test_every_non_confirmation_code_is_valid_without_text_matching(code):
    value = professional_boundary(
        non_confirmation_code=code,
        non_confirmation_text="Unverändert bereitgestellter sichtbarer Text.",
    )
    assert VALIDATOR.validate(value) is value


def test_at_least_one_unique_review_topic_with_declared_sources_is_required():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as missing:
        VALIDATOR.validate(professional_boundary(professional_review_topics=()))
    assert missing.value.code == "PROFESSIONAL_REVIEW_TOPIC_REQUIRED"
    first = ProfessionalBoundaryReviewTopic("same", "A", "A")
    second = ProfessionalBoundaryReviewTopic("same", "B", "B")
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as duplicate:
        VALIDATOR.validate(
            professional_boundary(professional_review_topics=(first, second))
        )
    assert duplicate.value.code == "DUPLICATE_REVIEW_TOPIC_ID"
    foreign = ProfessionalBoundaryReviewTopic(
        "topic-1",
        "Titel",
        "Beschreibung",
        (SourceChainReference("source-chain-foreign"),),
    )
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as source:
        VALIDATOR.validate(
            professional_boundary(professional_review_topics=(foreign,))
        )
    assert source.value.code == "TOPIC_SOURCE_CHAIN_NOT_DECLARED"


@pytest.mark.parametrize("field", ("topic_id", "title", "description"))
def test_review_topic_required_content_must_not_be_empty(field):
    values = {
        "topic_id": "topic-1",
        "title": "Titel",
        "description": "Beschreibung",
    }
    values[field] = ""
    with pytest.raises(ValueError, match=field):
        ProfessionalBoundaryReviewTopic(**values)


def test_created_at_is_timezone_aware():
    assert VALIDATOR.validate(professional_boundary()).created_at.utcoffset() is not None
    with pytest.raises(ValueError, match="timezone-aware"):
        professional_boundary(created_at=datetime(2026, 8, 2, 8, 0))


@pytest.mark.parametrize("provider", tuple(OrientationProviderType))
def test_every_provider_only_records_origin(provider):
    value = professional_boundary(provider_type=provider)
    assert VALIDATOR.validate(value).provider_type is provider
    assert not hasattr(value, "provider_authorized")


@pytest.mark.parametrize(
    ("status", "reference"),
    (
        (ProfessionalReviewStatus.NOT_DECLARED, None),
        (ProfessionalReviewStatus.REQUIRED, None),
        (ProfessionalReviewStatus.COMPLETED_DECLARED, "review:1"),
    ),
)
def test_review_status_is_declarative_and_structurally_consistent(status, reference):
    value = professional_boundary(
        professional_review_status=status,
        professional_review_reference=reference,
    )
    assert VALIDATOR.validate(value) is value


def test_completed_review_requires_reference_and_other_statuses_reject_it():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as missing:
        VALIDATOR.validate(
            professional_boundary(
                professional_review_status=ProfessionalReviewStatus.COMPLETED_DECLARED
            )
        )
    assert missing.value.code == "PROFESSIONAL_REVIEW_REFERENCE_REQUIRED"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as unexpected:
        VALIDATOR.validate(
            professional_boundary(professional_review_reference="review:unexpected")
        )
    assert unexpected.value.code == "UNEXPECTED_PROFESSIONAL_REVIEW_REFERENCE"


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in ProfessionalBoundaryCapability
        if item is not ProfessionalBoundaryCapability.RECORD_PROVIDED_BOUNDARY
    ),
)
def test_every_executing_capability_is_rejected(capability):
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(
            professional_boundary(
                capabilities=(
                    ProfessionalBoundaryCapability.RECORD_PROVIDED_BOUNDARY,
                    capability,
                )
            )
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"
