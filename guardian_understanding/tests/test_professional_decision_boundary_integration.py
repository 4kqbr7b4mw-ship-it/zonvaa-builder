import inspect

import pytest

from guardian_understanding import (
    AnswerFoundationIntegrationError,
    AnswerOperatingMode,
    ClassificationReference,
    GeneralOrientationReference,
    GuardianAnswerFoundationIntegration,
    PersonalPreparationReference,
    ProfessionalDecisionBoundaryEnvelope,
    ProfessionalDecisionBoundaryEnvelopeValidator,
    ProfessionalDecisionBoundaryValidationError,
    SourceChainReference,
)
from guardian_understanding import professional_decision_boundary as module
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_controlled_orientation_integration import (
    envelope as b1_envelope,
)
from guardian_understanding.tests.test_personal_preparation_integration import (
    envelope as b2_envelope,
)
from guardian_understanding.tests.test_professional_decision_boundary_contract import (
    professional_boundary,
)
from guardian_understanding.tests.test_source_chain import source_chain


VALIDATOR = ProfessionalDecisionBoundaryEnvelopeValidator()


def envelope(
    *,
    classification_id="classification-1",
    professional_classification_id="classification-1",
    boundary_id="boundary-1",
    professional_boundary_reference="boundary-1",
    referenced_source_ids=("source-chain-1",),
    professional_source_ids=("source-chain-1",),
    supplied_source_ids=("source-chain-1",),
    complete=True,
    mode=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    professional_decision_requested=True,
    boundary_classification_reference=True,
    general_orientation_reference=None,
    general_orientation=None,
    personal_preparation_reference=None,
    personal_preparation=None,
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
            source_chain(source_chain_id=item) for item in supplied_source_ids
        ),
        require_complete_source_chain_set=complete,
    )
    professional_value = professional_boundary(
        classification_reference=ClassificationReference(
            professional_classification_id
        ),
        boundary_reference=module.BoundaryReference(
            professional_boundary_reference
        ),
        source_chain_references=tuple(
            SourceChainReference(item) for item in professional_source_ids
        ),
        general_orientation_reference=general_orientation_reference,
        personal_preparation_reference=personal_preparation_reference,
    )
    return ProfessionalDecisionBoundaryEnvelope(
        foundation=foundation,
        professional_boundary=professional_value,
        general_orientation=general_orientation,
        personal_preparation=personal_preparation,
    )


def test_complete_b3_flow_returns_same_envelope_and_all_objects():
    value = envelope()
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.foundation is value.foundation
    assert result.professional_boundary is value.professional_boundary
    assert result.foundation.boundary_contract is value.foundation.boundary_contract
    assert result.foundation.classification_contract is value.foundation.classification_contract
    assert result.foundation.source_chain_contracts is value.foundation.source_chain_contracts


def test_classification_and_boundary_references_must_match():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as classification_error:
        VALIDATOR.validate(envelope(professional_classification_id="other"))
    assert classification_error.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as boundary_error:
        VALIDATOR.validate(envelope(professional_boundary_reference="other"))
    assert boundary_error.value.code == "BOUNDARY_REFERENCE_MISMATCH"


def test_boundary_must_reference_the_integrated_classification():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(envelope(boundary_classification_reference=False))
    assert error.value.code == "BOUNDARY_CLASSIFICATION_REFERENCE_REQUIRED"


def test_contract_classification_and_supplied_source_sets_match_exactly():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as classification:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1", "source-chain-2"),
                professional_source_ids=("source-chain-1",),
                supplied_source_ids=("source-chain-1", "source-chain-2"),
            )
        )
    assert classification.value.code == "CLASSIFICATION_SOURCE_CHAIN_SET_MISMATCH"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as supplied:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1",),
                professional_source_ids=("source-chain-1", "source-chain-extra"),
                supplied_source_ids=("source-chain-1",),
            )
        )
    assert supplied.value.code == "CLASSIFICATION_SOURCE_CHAIN_SET_MISMATCH"


def test_missing_additional_and_duplicate_supplied_sources_are_rejected():
    with pytest.raises(AnswerFoundationIntegrationError) as missing:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1", "source-chain-2"),
                professional_source_ids=("source-chain-1", "source-chain-2"),
                supplied_source_ids=("source-chain-1",),
            )
        )
    assert missing.value.code == "INCOMPLETE_SOURCE_CHAIN_SET"
    with pytest.raises(AnswerFoundationIntegrationError) as additional:
        VALIDATOR.validate(
            envelope(
                referenced_source_ids=("source-chain-1",),
                professional_source_ids=("source-chain-1",),
                supplied_source_ids=("source-chain-1", "source-chain-extra"),
            )
        )
    assert additional.value.code == "UNREFERENCED_SOURCE_CHAIN"
    with pytest.raises(AnswerFoundationIntegrationError) as duplicate:
        VALIDATOR.validate(
            envelope(supplied_source_ids=("source-chain-1", "source-chain-1"))
        )
    assert duplicate.value.code == "DUPLICATE_SOURCE_CHAIN_ID"


def test_partial_foundation_and_non_b3_or_false_decision_are_rejected():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as partial:
        VALIDATOR.validate(envelope(complete=False))
    assert partial.value.code == "COMPLETE_SOURCE_CHAIN_SET_REQUIRED"
    for mode in (
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    ):
        with pytest.raises(ProfessionalDecisionBoundaryValidationError):
            VALIDATOR.validate(
                envelope(mode=mode, professional_decision_requested=False)
            )
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as flag:
        VALIDATOR.validate(envelope(professional_decision_requested=False))
    assert flag.value.code == "PROFESSIONAL_DECISION_NOT_REQUESTED"


def test_optional_b1_is_validated_by_reference_only():
    b1 = b1_envelope()
    value = envelope(
        general_orientation_reference=GeneralOrientationReference("orientation-1"),
        general_orientation=b1,
    )
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.general_orientation is b1
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as missing:
        VALIDATOR.validate(
            envelope(
                general_orientation_reference=GeneralOrientationReference(
                    "orientation-1"
                )
            )
        )
    assert missing.value.code == "GENERAL_ORIENTATION_REQUIRED"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as mismatch:
        VALIDATOR.validate(
            envelope(
                general_orientation_reference=GeneralOrientationReference("other"),
                general_orientation=b1,
            )
        )
    assert mismatch.value.code == "GENERAL_ORIENTATION_REFERENCE_MISMATCH"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as extra:
        VALIDATOR.validate(envelope(general_orientation=b1))
    assert extra.value.code == "UNREFERENCED_GENERAL_ORIENTATION"


def test_optional_b2_is_validated_by_reference_only():
    b2 = b2_envelope()
    value = envelope(
        personal_preparation_reference=PersonalPreparationReference("preparation-1"),
        personal_preparation=b2,
    )
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.personal_preparation is b2
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as missing:
        VALIDATOR.validate(
            envelope(
                personal_preparation_reference=PersonalPreparationReference(
                    "preparation-1"
                )
            )
        )
    assert missing.value.code == "PERSONAL_PREPARATION_REQUIRED"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as mismatch:
        VALIDATOR.validate(
            envelope(
                personal_preparation_reference=PersonalPreparationReference("other"),
                personal_preparation=b2,
            )
        )
    assert mismatch.value.code == "PERSONAL_PREPARATION_REFERENCE_MISMATCH"
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as extra:
        VALIDATOR.validate(envelope(personal_preparation=b2))
    assert extra.value.code == "UNREFERENCED_PERSONAL_PREPARATION"


def test_complete_flow_may_reference_b1_and_b2_together_without_copying_them():
    b1 = b1_envelope()
    b2 = b2_envelope()
    value = envelope(
        general_orientation_reference=GeneralOrientationReference("orientation-1"),
        general_orientation=b1,
        personal_preparation_reference=PersonalPreparationReference("preparation-1"),
        personal_preparation=b2,
    )
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.general_orientation is b1
    assert result.personal_preparation is b2


def test_integration_has_no_decision_generation_interpretation_or_activation():
    source = inspect.getsource(module)
    for forbidden in (
        "subprocess",
        "requests",
        "urllib",
        "open(",
        "generate(",
        "classify(",
        "decide(",
        "activate(",
        "route(",
        "persist(",
        "provider_hook",
    ):
        assert forbidden not in source
    value = envelope()
    before = (
        value.foundation,
        value.professional_boundary,
        value.general_orientation,
        value.personal_preparation,
    )
    VALIDATOR.validate(value)
    assert before == (
        value.foundation,
        value.professional_boundary,
        value.general_orientation,
        value.personal_preparation,
    )
