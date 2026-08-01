from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from guardian_understanding import (
    B2PersonalPreparationContract,
    B2PersonalPreparationContractValidator,
    BoundaryReference,
    ClassificationReference,
    GeneralOrientationReference,
    KnownFactEntry,
    OpenQuestionEntry,
    OptionForConsiderationEntry,
    OrientationProviderType,
    PersonalContextReference,
    PersonalPreparationCapability,
    PersonalPreparationValidationError,
    ProfessionalReviewStatus,
    ProfessionalReviewTopicEntry,
    SourceChainReference,
    UncertaintyEntry,
)


VALIDATOR = B2PersonalPreparationContractValidator()


def preparation(**changes):
    values = {
        "preparation_id": "preparation-1",
        "classification_reference": ClassificationReference("classification-1"),
        "boundary_reference": BoundaryReference("boundary-1"),
        "source_chain_references": (SourceChainReference("source-chain-1"),),
        "personal_context_reference": PersonalContextReference("context-personal-1"),
        "preparation_goal": "Ein Fachgespräch vorbereitet führen.",
        "known_facts": (
            KnownFactEntry(
                "fact-1",
                "Ein Dokument wurde ausdrücklich referenziert.",
                (SourceChainReference("source-chain-1"),),
            ),
        ),
        "open_questions": (),
        "options_for_consideration": (),
        "uncertainties": (),
        "professional_review_topics": (
            ProfessionalReviewTopicEntry(
                "review-topic-1",
                "Die bestehende Dokumentfassung fachlich prüfen lassen.",
            ),
        ),
        "general_orientation_reference": None,
        "created_at": datetime(2026, 8, 1, 14, 0, tzinfo=timezone.utc),
        "provider_type": OrientationProviderType.TYPED_INPUT_ADAPTER,
        "provider_reference": "adapter:preparation-1",
        "professional_review_status": ProfessionalReviewStatus.REQUIRED,
        "professional_review_reference": None,
        "capabilities": (
            PersonalPreparationCapability.RECORD_PROVIDED_PREPARATION,
        ),
    }
    values.update(changes)
    return B2PersonalPreparationContract(**values)


def test_complete_immutable_contract_is_returned_unchanged():
    value = preparation()
    assert VALIDATOR.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.preparation_goal = "Geändert"


def test_empty_required_ids_and_references_are_rejected():
    with pytest.raises(ValueError, match="preparation_id"):
        preparation(preparation_id="")
    with pytest.raises(ValueError, match="classification_id"):
        ClassificationReference("")
    with pytest.raises(ValueError, match="boundary_id"):
        BoundaryReference("")
    with pytest.raises(ValueError, match="personal_context_id"):
        PersonalContextReference("")


def test_source_chain_references_are_required_non_empty_and_unique():
    with pytest.raises(PersonalPreparationValidationError) as absent:
        VALIDATOR.validate(preparation(source_chain_references=()))
    assert absent.value.code == "SOURCE_CHAIN_REFERENCE_REQUIRED"
    with pytest.raises(ValueError, match="source_chain_id"):
        SourceChainReference("")
    reference = SourceChainReference("source-chain-1")
    with pytest.raises(PersonalPreparationValidationError) as duplicate:
        VALIDATOR.validate(
            preparation(source_chain_references=(reference, reference))
        )
    assert duplicate.value.code == "DUPLICATE_SOURCE_CHAIN_REFERENCE"


def test_goal_known_content_and_review_topic_minimums_are_enforced():
    with pytest.raises(ValueError, match="preparation_goal"):
        preparation(preparation_goal="")
    with pytest.raises(PersonalPreparationValidationError) as content:
        VALIDATOR.validate(preparation(known_facts=(), open_questions=()))
    assert content.value.code == "PREPARATION_CONTENT_REQUIRED"
    with pytest.raises(PersonalPreparationValidationError) as review:
        VALIDATOR.validate(preparation(professional_review_topics=()))
    assert review.value.code == "PROFESSIONAL_REVIEW_TOPIC_REQUIRED"


@pytest.mark.parametrize(
    "entry",
    (
        KnownFactEntry("fact-2", "Bereitgestellte Tatsache."),
        OpenQuestionEntry("question-1", "Welche Unterlage liegt vor?"),
        OptionForConsiderationEntry("option-1", "Eine ausdrücklich genannte Option."),
        UncertaintyEntry("uncertainty-1", "Der Dokumentstand ist unbekannt."),
        ProfessionalReviewTopicEntry("review-2", "Dokument fachlich prüfen."),
    ),
)
def test_each_typed_entry_preserves_provided_content(entry):
    assert entry.entry_id
    assert entry.content
    with pytest.raises(FrozenInstanceError):
        entry.content = "Geändert"


@pytest.mark.parametrize(
    "entry_type",
    (
        KnownFactEntry,
        OpenQuestionEntry,
        OptionForConsiderationEntry,
        UncertaintyEntry,
        ProfessionalReviewTopicEntry,
    ),
)
def test_entry_ids_and_content_must_not_be_empty(entry_type):
    with pytest.raises(ValueError, match="entry_id"):
        entry_type("", "Inhalt")
    with pytest.raises(ValueError, match="content"):
        entry_type("entry-1", "")


def test_duplicate_entry_ids_are_rejected_within_each_list():
    first = KnownFactEntry("duplicate", "Erster Inhalt.")
    second = KnownFactEntry("duplicate", "Zweiter Inhalt.")
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(preparation(known_facts=(first, second)))
    assert error.value.code == "DUPLICATE_ENTRY_ID"


def test_entry_source_references_are_unique_and_part_of_total_set():
    reference = SourceChainReference("source-chain-1")
    duplicate = KnownFactEntry("fact-1", "Inhalt.", (reference, reference))
    with pytest.raises(PersonalPreparationValidationError) as duplicate_error:
        VALIDATOR.validate(preparation(known_facts=(duplicate,)))
    assert duplicate_error.value.code == "DUPLICATE_ENTRY_SOURCE_CHAIN_REFERENCE"
    foreign = KnownFactEntry(
        "fact-1",
        "Inhalt.",
        (SourceChainReference("source-chain-foreign"),),
    )
    with pytest.raises(PersonalPreparationValidationError) as foreign_error:
        VALIDATOR.validate(preparation(known_facts=(foreign,)))
    assert foreign_error.value.code == "ENTRY_SOURCE_CHAIN_NOT_DECLARED"


def test_options_and_uncertainties_may_be_empty_or_explicitly_present():
    assert VALIDATOR.validate(preparation())
    value = preparation(
        options_for_consideration=(
            OptionForConsiderationEntry("option-1", "Bereitgestellte Option."),
        ),
        uncertainties=(
            UncertaintyEntry("uncertainty-1", "Bereitgestellte Unsicherheit."),
        ),
    )
    assert VALIDATOR.validate(value) is value


def test_general_orientation_reference_is_optional_and_non_empty_when_present():
    assert VALIDATOR.validate(preparation()).general_orientation_reference is None
    reference = GeneralOrientationReference("orientation-1")
    assert VALIDATOR.validate(
        preparation(general_orientation_reference=reference)
    ).general_orientation_reference is reference
    with pytest.raises(ValueError, match="orientation_id"):
        GeneralOrientationReference("")


def test_created_at_must_be_timezone_aware():
    assert VALIDATOR.validate(preparation()).created_at.utcoffset() is not None
    with pytest.raises(ValueError, match="timezone-aware"):
        preparation(created_at=datetime(2026, 8, 1, 14, 0))


@pytest.mark.parametrize("provider", tuple(OrientationProviderType))
def test_provider_type_only_records_origin(provider):
    value = preparation(provider_type=provider)
    assert VALIDATOR.validate(value).provider_type is provider
    assert not hasattr(value, "provider_authorized")


@pytest.mark.parametrize(
    ("status", "reference"),
    (
        (ProfessionalReviewStatus.NOT_DECLARED, None),
        (ProfessionalReviewStatus.REQUIRED, None),
        (ProfessionalReviewStatus.COMPLETED_DECLARED, "review:completed-1"),
    ),
)
def test_review_status_and_reference_are_structurally_consistent(status, reference):
    value = preparation(
        professional_review_status=status,
        professional_review_reference=reference,
    )
    assert VALIDATOR.validate(value) is value


def test_completed_review_requires_reference_and_other_statuses_reject_it():
    with pytest.raises(PersonalPreparationValidationError) as missing:
        VALIDATOR.validate(
            preparation(
                professional_review_status=ProfessionalReviewStatus.COMPLETED_DECLARED,
            )
        )
    assert missing.value.code == "PROFESSIONAL_REVIEW_REFERENCE_REQUIRED"
    with pytest.raises(PersonalPreparationValidationError) as unexpected:
        VALIDATOR.validate(
            preparation(professional_review_reference="review:not-completed")
        )
    assert unexpected.value.code == "UNEXPECTED_PROFESSIONAL_REVIEW_REFERENCE"


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in PersonalPreparationCapability
        if item is not PersonalPreparationCapability.RECORD_PROVIDED_PREPARATION
    ),
)
def test_all_executing_capabilities_are_rejected(capability):
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(
            preparation(
                capabilities=(
                    PersonalPreparationCapability.RECORD_PROVIDED_PREPARATION,
                    capability,
                )
            )
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_text_is_preserved_without_semantic_validation_or_option_selection():
    option = OptionForConsiderationEntry("option-1", "Die vermeintlich beste Option.")
    value = preparation(options_for_consideration=(option,))
    assert VALIDATOR.validate(value) is value
    assert value.options_for_consideration == (option,)
    assert not hasattr(value, "selected_option_id")
