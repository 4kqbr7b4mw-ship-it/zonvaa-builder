import inspect

import pytest

from guardian_understanding import (
    AnswerFoundationIntegrationError,
    AnswerOperatingMode,
    ClassificationReference,
    ControlledOrientationEnvelope,
    ControlledOrientationEnvelopeValidator,
    ControlledOrientationValidationError,
    GuardianAnswerFoundationIntegration,
    SourceChainReference,
)
from guardian_understanding import controlled_orientation
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_controlled_orientation_contract import orientation
from guardian_understanding.tests.test_source_chain import source_chain


VALIDATOR = ControlledOrientationEnvelopeValidator()


def envelope(
    *,
    classification_id="classification-1",
    orientation_classification_id="classification-1",
    boundary_id="boundary-1",
    orientation_boundary_id="boundary-1",
    referenced_source_ids=("source-chain-1",),
    orientation_source_ids=("source-chain-1",),
    supplied_source_ids=("source-chain-1",),
    complete=True,
    mode=AnswerOperatingMode.B1_GENERAL_ORIENTATION,
    professional_decision_requested=False,
):
    classification_value = classification(
        classification_id=classification_id,
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        professional_decision_requested=professional_decision_requested,
        source_chain_references=tuple(
            SourceChainReference(item) for item in referenced_source_ids
        ),
    )
    boundary_value = boundary(
        mode,
        boundary_id=boundary_id,
        classification_reference=ClassificationReference(classification_id),
    )
    foundation = GuardianAnswerFoundationIntegration(
        boundary_contract=boundary_value,
        classification_contract=classification_value,
        source_chain_contracts=tuple(
            source_chain(source_chain_id=item) for item in supplied_source_ids
        ),
        require_complete_source_chain_set=complete,
    )
    orientation_value = orientation(
        classification_reference=ClassificationReference(
            orientation_classification_id
        ),
        boundary_reference=controlled_orientation.BoundaryReference(
            orientation_boundary_id
        ),
        source_chain_references=tuple(
            SourceChainReference(item) for item in orientation_source_ids
        ),
    )
    return ControlledOrientationEnvelope(
        foundation=foundation,
        orientation=orientation_value,
    )


def test_complete_b1_evidence_flow_returns_same_objects_unchanged():
    value = envelope()
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.foundation is value.foundation
    assert result.orientation is value.orientation
    assert result.foundation.boundary_contract is value.foundation.boundary_contract
    assert result.foundation.classification_contract is value.foundation.classification_contract
    assert result.foundation.source_chain_contracts is value.foundation.source_chain_contracts


def test_classification_and_boundary_references_must_match():
    with pytest.raises(ControlledOrientationValidationError) as classification_error:
        VALIDATOR.validate(envelope(orientation_classification_id="other"))
    assert classification_error.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"
    with pytest.raises(ControlledOrientationValidationError) as boundary_error:
        VALIDATOR.validate(envelope(orientation_boundary_id="other"))
    assert boundary_error.value.code == "BOUNDARY_REFERENCE_MISMATCH"


def test_boundary_must_reference_the_same_classification():
    value = envelope()
    foundation = GuardianAnswerFoundationIntegration(
        boundary_contract=boundary(
            AnswerOperatingMode.B1_GENERAL_ORIENTATION,
            boundary_id="boundary-1",
            classification_reference=None,
        ),
        classification_contract=value.foundation.classification_contract,
        source_chain_contracts=value.foundation.source_chain_contracts,
        require_complete_source_chain_set=True,
    )
    broken = ControlledOrientationEnvelope(foundation, value.orientation)
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(broken)
    assert error.value.code == "BOUNDARY_CLASSIFICATION_REFERENCE_REQUIRED"


def test_orientation_classification_and_supplied_source_sets_must_match_exactly():
    with pytest.raises(ControlledOrientationValidationError) as missing:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1", "source-chain-2"),
                orientation_source_ids=("source-chain-1",),
                supplied_source_ids=("source-chain-1", "source-chain-2"),
            )
        )
    assert missing.value.code == "ORIENTATION_SOURCE_CHAIN_SET_MISMATCH"
    with pytest.raises(ControlledOrientationValidationError) as additional:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1",),
                orientation_source_ids=("source-chain-1", "source-chain-extra"),
                supplied_source_ids=("source-chain-1",),
            )
        )
    assert additional.value.code == "ORIENTATION_SOURCE_CHAIN_SET_MISMATCH"


def test_missing_additional_or_duplicate_supplied_source_chains_are_rejected():
    with pytest.raises(AnswerFoundationIntegrationError) as missing:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1", "source-chain-2"),
                orientation_source_ids=("source-chain-1", "source-chain-2"),
                supplied_source_ids=("source-chain-1",),
            )
        )
    assert missing.value.code == "INCOMPLETE_SOURCE_CHAIN_SET"
    with pytest.raises(AnswerFoundationIntegrationError) as additional:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1",),
                orientation_source_ids=("source-chain-1",),
                supplied_source_ids=("source-chain-1", "source-chain-extra"),
            )
        )
    assert additional.value.code == "UNREFERENCED_SOURCE_CHAIN"
    with pytest.raises(AnswerFoundationIntegrationError) as duplicate:
        VALIDATOR.validate(
            envelope(supplied_source_ids=("source-chain-1", "source-chain-1"))
        )
    assert duplicate.value.code == "DUPLICATE_SOURCE_CHAIN_ID"


def test_partial_foundation_validation_is_not_enough_for_visible_orientation():
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(envelope(complete=False))
    assert error.value.code == "COMPLETE_SOURCE_CHAIN_SET_REQUIRED"


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_only_exact_b1_foundation_is_accepted(mode):
    with pytest.raises(ControlledOrientationValidationError):
        VALIDATOR.validate(
            envelope(
                mode=mode,
                professional_decision_requested=(
                    mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
                ),
            )
        )


def test_integration_has_no_generation_interpretation_activation_or_state_change():
    source = inspect.getsource(controlled_orientation)
    for forbidden in (
        "subprocess",
        "requests",
        "urllib",
        "open(",
        "generate(",
        "classify(",
        "activate(",
        "route(",
        "persist(",
        "provider_hook",
    ):
        assert forbidden not in source
    value = envelope()
    before = (value.foundation, value.orientation)
    VALIDATOR.validate(value)
    assert (value.foundation, value.orientation) == before
