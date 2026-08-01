import inspect

import pytest

from guardian_understanding import (
    AnswerFoundationIntegrationError,
    AnswerOperatingMode,
    ClassificationReference,
    GuardianAnswerFoundationIntegration,
    GuardianAnswerFoundationIntegrationValidator,
    SourceChainReference,
)
from guardian_understanding import answer_foundation
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_source_chain import source_chain


VALIDATOR = GuardianAnswerFoundationIntegrationValidator()


def integrated(
    *,
    boundary_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    classification_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    classification_id="classification-1",
    boundary_classification_id="classification-1",
    referenced_source_ids=("source-chain-1",),
    supplied_source_ids=("source-chain-1",),
    complete=True,
    professional_decision_requested=False,
):
    classification_value = classification(
        classification_id=classification_id,
        provided_minimum_level=classification_level,
        candidate_levels=(classification_level,),
        effective_level=classification_level,
        professional_decision_requested=professional_decision_requested,
        source_chain_references=tuple(
            SourceChainReference(item) for item in referenced_source_ids
        ),
    )
    boundary_value = boundary(
        boundary_level,
        classification_reference=(
            ClassificationReference(boundary_classification_id)
            if boundary_classification_id is not None
            else None
        ),
    )
    source_values = tuple(
        source_chain(source_chain_id=item) for item in supplied_source_ids
    )
    return GuardianAnswerFoundationIntegration(
        boundary_contract=boundary_value,
        classification_contract=classification_value,
        source_chain_contracts=source_values,
        require_complete_source_chain_set=complete,
    )


def test_all_three_contract_families_integrate_consistently():
    value = integrated()
    assert VALIDATOR.validate(value) is value


def test_success_returns_the_exact_same_contract_objects():
    value = integrated()
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.boundary_contract is value.boundary_contract
    assert result.classification_contract is value.classification_contract
    assert result.source_chain_contracts is value.source_chain_contracts


def test_equal_boundary_and_classification_protection_is_valid():
    assert VALIDATOR.validate(integrated())


def test_more_protective_boundary_is_valid():
    value = integrated(
        boundary_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        classification_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    )
    assert VALIDATOR.validate(value) is value


def test_less_protective_boundary_is_rejected():
    value = integrated(
        boundary_level=AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        classification_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "BOUNDARY_PROTECTION_TOO_LOW"


def test_matching_classification_reference_is_valid():
    value = integrated(classification_id="classification-match")
    value = GuardianAnswerFoundationIntegration(
        boundary_contract=boundary(
            AnswerOperatingMode.B2_PERSONAL_PREPARATION,
            classification_reference=ClassificationReference(
                "classification-match"
            ),
        ),
        classification_contract=value.classification_contract,
        source_chain_contracts=value.source_chain_contracts,
        require_complete_source_chain_set=True,
    )
    assert VALIDATOR.validate(value) is value


def test_optional_boundary_classification_reference_may_be_absent():
    value = integrated(boundary_classification_id=None)
    assert VALIDATOR.validate(value) is value


def test_mismatching_classification_reference_is_rejected():
    value = integrated(boundary_classification_id="classification-other")
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"


def test_all_referenced_source_chain_ids_match_in_complete_mode():
    value = integrated(
        referenced_source_ids=("source-chain-1", "source-chain-2"),
        supplied_source_ids=("source-chain-1", "source-chain-2"),
    )
    assert VALIDATOR.validate(value) is value


def test_missing_source_chain_is_rejected_in_complete_mode():
    value = integrated(
        referenced_source_ids=("source-chain-1", "source-chain-2"),
        supplied_source_ids=("source-chain-1",),
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "INCOMPLETE_SOURCE_CHAIN_SET"


def test_additional_unreferenced_source_chain_is_rejected():
    value = integrated(
        referenced_source_ids=("source-chain-1",),
        supplied_source_ids=("source-chain-1", "source-chain-extra"),
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "UNREFERENCED_SOURCE_CHAIN"


def test_duplicate_supplied_source_chain_ids_are_rejected():
    value = integrated(
        referenced_source_ids=("source-chain-1",),
        supplied_source_ids=("source-chain-1", "source-chain-1"),
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "DUPLICATE_SOURCE_CHAIN_ID"


def test_partial_mode_allows_missing_but_not_additional_sources():
    value = integrated(
        referenced_source_ids=("source-chain-1", "source-chain-2"),
        supplied_source_ids=("source-chain-1",),
        complete=False,
    )
    assert VALIDATOR.validate(value) is value


def test_professional_decision_remains_b3_and_structurally_consistent():
    value = integrated(
        boundary_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        classification_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=True,
    )
    assert VALIDATOR.validate(value) is value


def test_professional_decision_cannot_integrate_with_lower_boundary():
    value = integrated(
        boundary_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        classification_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=True,
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "BOUNDARY_PROTECTION_TOO_LOW"


def test_integration_has_no_runtime_classification_interpretation_or_activation():
    source = inspect.getsource(answer_foundation)
    for forbidden in (
        "subprocess",
        "requests",
        "urllib",
        "open(",
        "classify(",
        "activate(",
        "route(",
        "persist(",
        "provider_hook",
    ):
        assert forbidden not in source
    value = integrated()
    before = (
        value.boundary_contract,
        value.classification_contract,
        value.source_chain_contracts,
    )
    VALIDATOR.validate(value)
    assert before == (
        value.boundary_contract,
        value.classification_contract,
        value.source_chain_contracts,
    )
