from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone

import pytest

from guardian_understanding.source_chain import (
    DeclaredSourceContradiction,
    GuardianAnswerContextReference,
    GuardianSourceChainContract,
    GuardianSourceChainValidator,
    SourceChainCapability,
    SourceChainValidationError,
    SourceKind,
    SourceProvenanceCategory,
    SourceRecheckKind,
    SourceRecheckRequirement,
    SourceUncertaintyStatus,
)


VALIDATOR = GuardianSourceChainValidator()


def source_chain(**changes):
    values = {
        "source_chain_id": "source-chain-official-guidance-1",
        "source_name": "Amtliche Orientierung",
        "publisher": "Beispielbehörde",
        "source_kind": SourceKind.PRIMARY,
        "source_authority": "Amtliche Veröffentlichung",
        "source_reference": "https://example.invalid/official-guidance",
        "retrieved_at": datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc),
        "publication_or_version": "Fassung 2026-07",
        "supported_statement": "Die bereitgestellte Aussage gilt allgemein.",
        "jurisdiction_or_scope": "Deutschland",
        "declared_contradictions": (
            DeclaredSourceContradiction(
                conflicting_source_chain_id="source-chain-commentary-2",
                declaration_reference="declaration:contradiction-1",
            ),
        ),
        "uncertainty_status": SourceUncertaintyStatus.CONFIRMED,
        "recheck_requirement": SourceRecheckRequirement(
            kind=SourceRecheckKind.DATE_BASED,
            recheck_on=date(2027, 8, 1),
        ),
        "answer_context_reference": GuardianAnswerContextReference(
            guardian_answer_id="answer-1",
            conversation_context_id="conversation-1",
        ),
        "provenance_category": SourceProvenanceCategory.PROVIDED_SOURCE_RECORD,
        "provenance_reference": "provenance:provided-source-1",
        "capabilities": (SourceChainCapability.ACCEPT_TYPED_SOURCE_INFORMATION,),
    }
    values.update(changes)
    return GuardianSourceChainContract(**values)


def test_complete_contract_maps_all_twelve_adr_required_fields():
    value = source_chain()
    assert value.source_name == "Amtliche Orientierung"
    assert value.publisher == "Beispielbehörde"
    assert value.source_kind is SourceKind.PRIMARY
    assert value.source_authority == "Amtliche Veröffentlichung"
    assert value.source_reference == "https://example.invalid/official-guidance"
    assert value.retrieved_at.tzinfo is not None
    assert value.publication_or_version == "Fassung 2026-07"
    assert value.supported_statement
    assert value.jurisdiction_or_scope == "Deutschland"
    assert value.declared_contradictions
    assert value.uncertainty_status is SourceUncertaintyStatus.CONFIRMED
    assert value.recheck_requirement.kind is SourceRecheckKind.DATE_BASED
    assert value.answer_context_reference.guardian_answer_id == "answer-1"
    assert value.answer_context_reference.conversation_context_id == "conversation-1"
    assert value.provenance_category is SourceProvenanceCategory.PROVIDED_SOURCE_RECORD
    assert value.provenance_reference == "provenance:provided-source-1"


def test_successful_validation_returns_the_same_unchanged_contract():
    value = source_chain()
    assert VALIDATOR.validate(value) is value


@pytest.mark.parametrize("status", tuple(SourceUncertaintyStatus))
def test_every_adr_uncertainty_status_is_valid(status):
    value = source_chain(uncertainty_status=status)
    assert VALIDATOR.validate(value).uncertainty_status is status


@pytest.mark.parametrize(
    "field",
    (
        "source_chain_id",
        "source_name",
        "publisher",
        "source_authority",
        "source_reference",
        "supported_statement",
        "jurisdiction_or_scope",
        "provenance_reference",
    ),
)
def test_missing_required_text_is_rejected(field):
    with pytest.raises(ValueError, match=field):
        source_chain(**{field: ""})


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("source_kind", "PRIMARY"),
        ("uncertainty_status", "bestätigt"),
        ("provenance_category", "PROVIDED_SOURCE_RECORD"),
    ),
)
def test_untyped_enum_values_are_rejected(field, value):
    with pytest.raises(TypeError, match=field):
        source_chain(**{field: value})


def test_self_reference_in_declared_contradiction_is_rejected():
    value = source_chain(
        declared_contradictions=(
            DeclaredSourceContradiction(
                conflicting_source_chain_id="source-chain-official-guidance-1",
                declaration_reference="declaration:self-reference",
            ),
        )
    )
    with pytest.raises(SourceChainValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "SELF_CONTRADICTION"


def test_declared_contradiction_is_preserved_without_automatic_assessment():
    value = source_chain()
    result = VALIDATOR.validate(value)
    assert result.declared_contradictions == value.declared_contradictions
    assert result.uncertainty_status is SourceUncertaintyStatus.CONFIRMED


def test_newer_retrieval_does_not_replace_an_older_contract():
    older = source_chain(source_chain_id="source-chain-old")
    newer = source_chain(
        source_chain_id="source-chain-new",
        retrieved_at=datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc),
    )
    assert VALIDATOR.validate(older) is older
    assert VALIDATOR.validate(newer) is newer
    assert older.source_chain_id == "source-chain-old"
    assert not hasattr(newer, "predecessor_id")
    assert not hasattr(older, "successor_id")


def test_version_labels_do_not_create_priority_or_outdated_status():
    first = source_chain(publication_or_version="Version 1")
    second = source_chain(
        source_chain_id="source-chain-version-2",
        publication_or_version="Version 2",
    )
    assert VALIDATOR.validate(first).uncertainty_status is SourceUncertaintyStatus.CONFIRMED
    assert VALIDATOR.validate(second).uncertainty_status is SourceUncertaintyStatus.CONFIRMED


def test_date_based_recheck_is_structurally_validated_without_current_date_logic():
    requirement = SourceRecheckRequirement(
        kind=SourceRecheckKind.DATE_BASED,
        recheck_on=date(2000, 1, 1),
    )
    value = source_chain(recheck_requirement=requirement)
    assert VALIDATOR.validate(value).recheck_requirement is requirement
    assert value.uncertainty_status is SourceUncertaintyStatus.CONFIRMED


def test_event_based_recheck_is_structurally_validated():
    requirement = SourceRecheckRequirement(
        kind=SourceRecheckKind.EVENT_BASED,
        event_reference="event:material-primary-source-change",
    )
    value = source_chain(recheck_requirement=requirement)
    assert VALIDATOR.validate(value).recheck_requirement is requirement


@pytest.mark.parametrize(
    "requirement",
    (
        SourceRecheckRequirement(kind=SourceRecheckKind.DATE_BASED),
        SourceRecheckRequirement(kind=SourceRecheckKind.EVENT_BASED),
        SourceRecheckRequirement(
            kind=SourceRecheckKind.DATE_BASED,
            recheck_on=date(2027, 1, 1),
            event_reference="event:unexpected",
        ),
    ),
)
def test_invalid_recheck_shape_is_rejected(requirement):
    with pytest.raises(SourceChainValidationError):
        VALIDATOR.validate(source_chain(recheck_requirement=requirement))


@pytest.mark.parametrize(
    "capability",
    tuple(
        capability
        for capability in SourceChainCapability
        if capability is not SourceChainCapability.ACCEPT_TYPED_SOURCE_INFORMATION
    ),
)
def test_every_executing_capability_is_rejected(capability):
    value = source_chain(
        capabilities=(
            SourceChainCapability.ACCEPT_TYPED_SOURCE_INFORMATION,
            capability,
        )
    )
    with pytest.raises(SourceChainValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_source_chain_contract_and_nested_values_are_immutable():
    value = source_chain()
    with pytest.raises(FrozenInstanceError):
        value.publisher = "Anderer Herausgeber"
    with pytest.raises(FrozenInstanceError):
        value.recheck_requirement.recheck_on = date(2028, 1, 1)


def test_identical_typed_input_is_deterministic():
    first = source_chain()
    second = source_chain()
    assert first == second
    assert VALIDATOR.validate(first) == VALIDATOR.validate(second)


def test_validation_does_not_change_answer_boundary_contracts():
    from guardian_understanding.tests.test_answer_boundary import (
        VALIDATOR as BOUNDARY_VALIDATOR,
        contract as answer_boundary,
    )
    from guardian_understanding import AnswerOperatingMode

    before = answer_boundary(AnswerOperatingMode.B2_PERSONAL_PREPARATION)
    VALIDATOR.validate(source_chain())
    after = answer_boundary(AnswerOperatingMode.B2_PERSONAL_PREPARATION)
    assert after == before
    assert BOUNDARY_VALIDATOR.validate(after) is after


def test_replace_creates_a_separate_contract_without_mutating_history():
    original = source_chain()
    changed = replace(
        original,
        source_chain_id="source-chain-separate-record",
        uncertainty_status=SourceUncertaintyStatus.DISPUTED,
    )
    assert original.uncertainty_status is SourceUncertaintyStatus.CONFIRMED
    assert changed.uncertainty_status is SourceUncertaintyStatus.DISPUTED

