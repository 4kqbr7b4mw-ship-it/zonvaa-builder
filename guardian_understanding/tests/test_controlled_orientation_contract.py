from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from guardian_understanding import (
    B1OrientationContract,
    B1OrientationContractValidator,
    BoundaryReference,
    ClassificationReference,
    ControlledOrientationCapability,
    ControlledOrientationValidationError,
    OrientationProviderType,
    ProfessionalReviewStatus,
    SourceChainReference,
)


VALIDATOR = B1OrientationContractValidator()


def orientation(**changes):
    values = {
        "orientation_id": "orientation-1",
        "classification_reference": ClassificationReference("classification-1"),
        "boundary_reference": BoundaryReference("boundary-1"),
        "source_chain_references": (SourceChainReference("source-chain-1"),),
        "orientation_summary": "Allgemeine Orientierung zum Thema.",
        "general_information": "Bereits bereitgestellte allgemeine Information.",
        "uncertainty_notice": "Die Aktualität einzelner Angaben ist zu prüfen.",
        "source_notice": "Die Aussage ist mit einer Quellenkette verknüpft.",
        "limitations": "Keine fachliche Einzelfallentscheidung.",
        "created_at": datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
        "provider_type": OrientationProviderType.TYPED_INPUT_ADAPTER,
        "provider_reference": "adapter:orientation-1",
        "professional_review_status": ProfessionalReviewStatus.NOT_DECLARED,
        "professional_review_reference": None,
        "capabilities": (
            ControlledOrientationCapability.RECORD_PROVIDED_ORIENTATION,
        ),
    }
    values.update(changes)
    return B1OrientationContract(**values)


def test_complete_immutable_orientation_contract_is_valid_and_returned_unchanged():
    value = orientation()
    assert VALIDATOR.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.orientation_summary = "Geändert"


@pytest.mark.parametrize(
    "field",
    (
        "orientation_id",
        "orientation_summary",
        "general_information",
        "uncertainty_notice",
        "source_notice",
        "limitations",
        "provider_reference",
    ),
)
def test_empty_required_text_is_rejected(field):
    with pytest.raises(ValueError, match=field):
        orientation(**{field: ""})


def test_empty_classification_reference_is_rejected():
    with pytest.raises(ValueError, match="classification_id"):
        ClassificationReference("")


def test_empty_boundary_reference_is_rejected():
    with pytest.raises(ValueError, match="boundary_id"):
        BoundaryReference("")


def test_at_least_one_unique_non_empty_source_chain_reference_is_required():
    with pytest.raises(ControlledOrientationValidationError) as empty:
        VALIDATOR.validate(orientation(source_chain_references=()))
    assert empty.value.code == "SOURCE_CHAIN_REFERENCE_REQUIRED"
    with pytest.raises(ValueError, match="source_chain_id"):
        SourceChainReference("")
    repeated = SourceChainReference("source-chain-1")
    with pytest.raises(ControlledOrientationValidationError) as duplicate:
        VALIDATOR.validate(
            orientation(source_chain_references=(repeated, repeated))
        )
    assert duplicate.value.code == "DUPLICATE_SOURCE_CHAIN_REFERENCE"


def test_timezone_aware_creation_time_is_required():
    assert VALIDATOR.validate(orientation()).created_at.utcoffset() is not None
    with pytest.raises(ValueError, match="timezone-aware"):
        orientation(created_at=datetime(2026, 8, 1, 12, 0))


@pytest.mark.parametrize("provider", tuple(OrientationProviderType))
def test_every_provider_type_only_records_origin(provider):
    value = orientation(provider_type=provider)
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
def test_each_professional_review_status_has_a_consistent_shape(status, reference):
    value = orientation(
        professional_review_status=status,
        professional_review_reference=reference,
    )
    assert VALIDATOR.validate(value) is value


def test_completed_review_requires_a_reference_without_confirming_correctness():
    value = orientation(
        professional_review_status=ProfessionalReviewStatus.COMPLETED_DECLARED,
    )
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "PROFESSIONAL_REVIEW_REFERENCE_REQUIRED"
    assert not hasattr(value, "professionally_correct")


def test_other_review_statuses_cannot_carry_an_invented_review_reference():
    value = orientation(professional_review_reference="review:not-performed")
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "UNEXPECTED_PROFESSIONAL_REVIEW_REFERENCE"


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in ControlledOrientationCapability
        if item is not ControlledOrientationCapability.RECORD_PROVIDED_ORIENTATION
    ),
)
def test_every_executing_capability_is_rejected(capability):
    value = orientation(
        capabilities=(
            ControlledOrientationCapability.RECORD_PROVIDED_ORIENTATION,
            capability,
        )
    )
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_supplied_text_is_preserved_without_normalization_or_semantic_analysis():
    value = orientation(
        general_information="Für deinen Fall gilt angeblich etwas Konkretes.",
    )
    assert VALIDATOR.validate(value) is value
    assert value.general_information == "Für deinen Fall gilt angeblich etwas Konkretes."
