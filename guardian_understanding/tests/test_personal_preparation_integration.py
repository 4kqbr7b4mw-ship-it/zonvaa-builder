import inspect

import pytest

from guardian_understanding import (
    AnswerFoundationIntegrationError,
    AnswerOperatingMode,
    ClassificationReference,
    ControlledOrientationEnvelope,
    GeneralOrientationReference,
    GuardianAnswerFoundationIntegration,
    PersonalPreparationEnvelope,
    PersonalPreparationEnvelopeValidator,
    PersonalPreparationValidationError,
    SourceChainReference,
)
from guardian_understanding import personal_preparation
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_controlled_orientation_integration import (
    envelope as b1_envelope,
)
from guardian_understanding.tests.test_personal_preparation_contract import preparation
from guardian_understanding.tests.test_source_chain import source_chain


VALIDATOR = PersonalPreparationEnvelopeValidator()


def envelope(
    *,
    classification_id="classification-1",
    preparation_classification_id="classification-1",
    boundary_id="boundary-1",
    preparation_boundary_id="boundary-1",
    source_ids=("source-chain-1",),
    preparation_source_ids=("source-chain-1",),
    complete=True,
    mode=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    professional_decision_requested=False,
    orientation_reference=None,
    orientation_value=None,
    boundary_classification_reference=True,
):
    classification_value = classification(
        classification_id=classification_id,
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        professional_decision_requested=professional_decision_requested,
        source_chain_references=tuple(SourceChainReference(item) for item in source_ids),
    )
    boundary_value = boundary(
        mode,
        boundary_id=boundary_id,
        classification_reference=(
            ClassificationReference(classification_id)
            if boundary_classification_reference
            else None
        ),
    )
    foundation = GuardianAnswerFoundationIntegration(
        boundary_contract=boundary_value,
        classification_contract=classification_value,
        source_chain_contracts=tuple(
            source_chain(source_chain_id=item) for item in source_ids
        ),
        require_complete_source_chain_set=complete,
    )
    preparation_value = preparation(
        classification_reference=ClassificationReference(
            preparation_classification_id
        ),
        boundary_reference=personal_preparation.BoundaryReference(
            preparation_boundary_id
        ),
        source_chain_references=tuple(
            SourceChainReference(item) for item in preparation_source_ids
        ),
        general_orientation_reference=orientation_reference,
    )
    return PersonalPreparationEnvelope(
        foundation=foundation,
        preparation=preparation_value,
        general_orientation=orientation_value,
    )


def test_complete_b2_flow_returns_same_envelope_and_objects():
    value = envelope()
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.foundation is value.foundation
    assert result.preparation is value.preparation
    assert result.foundation.boundary_contract is value.foundation.boundary_contract
    assert result.foundation.classification_contract is value.foundation.classification_contract
    assert result.foundation.source_chain_contracts is value.foundation.source_chain_contracts


def test_classification_and_boundary_ids_must_match():
    with pytest.raises(PersonalPreparationValidationError) as classification_error:
        VALIDATOR.validate(envelope(preparation_classification_id="other"))
    assert classification_error.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"
    with pytest.raises(PersonalPreparationValidationError) as boundary_error:
        VALIDATOR.validate(envelope(preparation_boundary_id="other"))
    assert boundary_error.value.code == "BOUNDARY_REFERENCE_MISMATCH"


def test_boundary_must_reference_same_classification():
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(envelope(boundary_classification_reference=False))
    assert error.value.code == "BOUNDARY_CLASSIFICATION_REFERENCE_REQUIRED"


def test_source_chain_set_must_match_fully_without_missing_or_extra_values():
    with pytest.raises(PersonalPreparationValidationError) as missing:
        VALIDATOR.validate(
            envelope(
                source_ids=("source-chain-1", "source-chain-2"),
                preparation_source_ids=("source-chain-1",),
            )
        )
    assert missing.value.code == "SOURCE_CHAIN_SET_MISMATCH"
    with pytest.raises(PersonalPreparationValidationError) as extra:
        VALIDATOR.validate(
            envelope(
                source_ids=("source-chain-1",),
                preparation_source_ids=("source-chain-1", "source-chain-extra"),
            )
        )
    assert extra.value.code == "SOURCE_CHAIN_SET_MISMATCH"


def test_partial_foundation_is_rejected():
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(envelope(complete=False))
    assert error.value.code == "COMPLETE_SOURCE_CHAIN_SET_REQUIRED"


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_only_b2_b2_is_accepted(mode):
    with pytest.raises(PersonalPreparationValidationError):
        VALIDATOR.validate(
            envelope(
                mode=mode,
                professional_decision_requested=(
                    mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
                ),
            )
        )


def test_valid_optional_b1_orientation_is_only_referenced_and_preserved():
    b1 = b1_envelope()
    value = envelope(
        orientation_reference=GeneralOrientationReference("orientation-1"),
        orientation_value=b1,
    )
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.general_orientation is b1
    assert result.general_orientation.orientation is b1.orientation


def test_referenced_b1_orientation_must_be_supplied_and_match_id():
    reference = GeneralOrientationReference("orientation-1")
    with pytest.raises(PersonalPreparationValidationError) as missing:
        VALIDATOR.validate(envelope(orientation_reference=reference))
    assert missing.value.code == "GENERAL_ORIENTATION_REQUIRED"
    with pytest.raises(PersonalPreparationValidationError) as mismatch:
        VALIDATOR.validate(
            envelope(
                orientation_reference=GeneralOrientationReference("other"),
                orientation_value=b1_envelope(),
            )
        )
    assert mismatch.value.code == "GENERAL_ORIENTATION_REFERENCE_MISMATCH"


def test_unreferenced_b1_orientation_is_rejected():
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(envelope(orientation_value=b1_envelope()))
    assert error.value.code == "UNREFERENCED_GENERAL_ORIENTATION"


def test_foundation_rejects_duplicate_source_ids_before_preparation_integration():
    value = envelope()
    duplicate_foundation = GuardianAnswerFoundationIntegration(
        boundary_contract=value.foundation.boundary_contract,
        classification_contract=value.foundation.classification_contract,
        source_chain_contracts=(
            source_chain(source_chain_id="source-chain-1"),
            source_chain(source_chain_id="source-chain-1"),
        ),
        require_complete_source_chain_set=True,
    )
    with pytest.raises(AnswerFoundationIntegrationError) as error:
        VALIDATOR.validate(
            PersonalPreparationEnvelope(duplicate_foundation, value.preparation)
        )
    assert error.value.code == "DUPLICATE_SOURCE_CHAIN_ID"


def test_no_generation_priority_decision_activation_or_state_change_exists():
    source = inspect.getsource(personal_preparation)
    for forbidden in (
        "subprocess",
        "requests",
        "urllib",
        "open(",
        "generate(",
        "prioritize(",
        "decide(",
        "activate(",
        "route(",
        "persist(",
        "provider_hook",
    ):
        assert forbidden not in source
    value = envelope()
    before = (value.foundation, value.preparation, value.general_orientation)
    VALIDATOR.validate(value)
    assert before == (value.foundation, value.preparation, value.general_orientation)
