from dataclasses import replace
import inspect

import pytest

from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    ClassificationReference,
)
from guardian_understanding.answer_foundation import AnswerFoundationIntegrationError
from guardian_understanding.answer_reference_journey import (
    AnswerFoundationReference,
    AnswerReferenceJourneyStepType,
    AnswerReferenceJourneyValidationError,
    GuardianAnswerReferenceJourneyValidator,
)
from guardian_understanding import answer_reference_journey as module
from guardian_understanding.controlled_orientation import ControlledOrientationValidationError
from guardian_understanding.source_chain import SourceChainReference
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_answer_reference_journey_end_to_end import (
    b1_stage,
    b2_stage,
    b3_stage,
    journey_envelope,
)


VALIDATOR = GuardianAnswerReferenceJourneyValidator()


def complete():
    b1 = b1_stage()
    b2 = b2_stage(b1)
    b3 = b3_stage(b1, b2)
    return journey_envelope(b1=b1, b2=b2, b3=b3)


def test_classification_boundary_and_foundation_references_must_match_terminal_stage():
    value = complete()
    with pytest.raises(AnswerReferenceJourneyValidationError) as classification:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(
                    value.journey,
                    classification_reference=replace(
                        value.journey.classification_reference,
                        classification_id="classification-foreign",
                    ),
                ),
            )
        )
    assert classification.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"
    with pytest.raises(AnswerReferenceJourneyValidationError) as boundary:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(
                    value.journey,
                    boundary_reference=replace(
                        value.journey.boundary_reference,
                        boundary_id="boundary-foreign",
                    ),
                ),
            )
        )
    assert boundary.value.code == "BOUNDARY_REFERENCE_MISMATCH"
    foreign = AnswerFoundationReference(
        classification_id=value.journey.foundation_reference.classification_id,
        boundary_id=value.journey.foundation_reference.boundary_id,
        source_chain_ids=("source-foreign",),
    )
    with pytest.raises(AnswerReferenceJourneyValidationError) as foundation:
        VALIDATOR.validate(
            replace(value, journey=replace(value.journey, foundation_reference=foreign))
        )
    assert foundation.value.code == "FOUNDATION_REFERENCE_MISMATCH"


def test_missing_or_wrong_optional_stage_references_are_rejected():
    value = complete()
    with pytest.raises(AnswerReferenceJourneyValidationError) as missing:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(value.journey, personal_preparation_reference=None),
            )
        )
    assert missing.value.code == "UNREFERENCED_PERSONAL_PREPARATION"
    wrong = replace(
        value.journey.personal_preparation_reference,
        preparation_id="preparation-foreign",
    )
    with pytest.raises(AnswerReferenceJourneyValidationError) as mismatch:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(value.journey, personal_preparation_reference=wrong),
            )
        )
    assert mismatch.value.code == "PERSONAL_PREPARATION_REFERENCE_MISMATCH"


def test_independent_or_foreign_nested_stage_objects_are_not_mixed():
    value = complete()
    foreign_b1 = b1_stage("other-b1")
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(replace(value, general_orientation=foreign_b1))
    assert error.value.code in {
        "B1_OBJECT_IDENTITY_MISMATCH",
        "B3_B1_OBJECT_IDENTITY_MISMATCH",
    }


def test_terminal_foundation_must_retain_exact_object_identity():
    value = complete()
    copied_foundation = replace(value.current_foundation)
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(replace(value, current_foundation=copied_foundation))
    assert error.value.code == "CURRENT_FOUNDATION_IDENTITY_MISMATCH"


def test_stage_classification_boundary_and_artifact_ids_are_unique():
    value = complete()
    duplicate_classification = replace(
        value.personal_preparation.foundation.classification_contract,
        classification_id=value.general_orientation.foundation.classification_contract.classification_id,
    )
    duplicate_boundary = replace(
        value.personal_preparation.foundation.boundary_contract,
        classification_reference=replace(
            value.personal_preparation.foundation.boundary_contract.classification_reference,
            classification_id=duplicate_classification.classification_id,
        ),
    )
    duplicate_foundation = replace(
        value.personal_preparation.foundation,
        classification_contract=duplicate_classification,
        boundary_contract=duplicate_boundary,
    )
    duplicate_preparation = replace(
        value.personal_preparation.preparation,
        classification_reference=replace(
            value.personal_preparation.preparation.classification_reference,
            classification_id=duplicate_classification.classification_id,
        ),
    )
    duplicate_b2 = replace(
        value.personal_preparation,
        foundation=duplicate_foundation,
        preparation=duplicate_preparation,
    )
    duplicate_b3 = replace(
        value.professional_boundary,
        personal_preparation=duplicate_b2,
    )
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(
            replace(
                value,
                personal_preparation=duplicate_b2,
                professional_boundary=duplicate_b3,
            )
        )
    assert error.value.code == "DUPLICATE_CLASSIFICATION_ID"


def test_context_and_source_context_must_remain_consistent():
    value = complete()
    changed_classification = replace(
        value.current_foundation.classification_contract,
        conversation_context_reference="conversation:foreign",
    )
    changed_foundation = replace(
        value.current_foundation,
        classification_contract=changed_classification,
    )
    changed_b3 = replace(value.professional_boundary, foundation=changed_foundation)
    broken = replace(value, current_foundation=changed_foundation, professional_boundary=changed_b3)
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(broken)
    assert error.value.code == "CONVERSATION_CONTEXT_MISMATCH"


def test_incomplete_sources_and_mode_mismatch_are_rejected_by_existing_validators():
    direct = journey_envelope(b1=b1_stage())
    partial_foundation = replace(
        direct.current_foundation,
        require_complete_source_chain_set=False,
    )
    partial_b1 = replace(direct.general_orientation, foundation=partial_foundation)
    with pytest.raises(ControlledOrientationValidationError):
        VALIDATOR.validate(
            replace(direct, current_foundation=partial_foundation, general_orientation=partial_b1)
        )
    wrong_mode = replace(
        direct.journey.steps[0],
        protection_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    )
    with pytest.raises(AnswerReferenceJourneyValidationError) as step:
        VALIDATOR.validate(
            replace(
                direct,
                journey=replace(
                    direct.journey,
                    steps=(wrong_mode,) + direct.journey.steps[1:],
                ),
            )
        )
    assert step.value.code == "STEP_PROTECTION_DOWNGRADE"


def test_contradictory_classification_boundary_and_incomplete_sources_are_rejected():
    direct = journey_envelope(b1=b1_stage())
    contradictory_boundary = boundary(
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        boundary_id=direct.current_foundation.boundary_contract.boundary_id,
        classification_reference=ClassificationReference(
            direct.current_foundation.classification_contract.classification_id
        ),
    )
    contradictory_foundation = replace(
        direct.current_foundation,
        boundary_contract=contradictory_boundary,
    )
    contradictory_b1 = replace(
        direct.general_orientation,
        foundation=contradictory_foundation,
    )
    with pytest.raises(ControlledOrientationValidationError) as mismatch:
        VALIDATOR.validate(
            replace(
                direct,
                current_foundation=contradictory_foundation,
                general_orientation=contradictory_b1,
            )
        )
    assert mismatch.value.code == "BOUNDARY_NOT_B1"

    incomplete_classification = replace(
        direct.current_foundation.classification_contract,
        source_chain_references=(
            direct.current_foundation.classification_contract.source_chain_references[0],
            SourceChainReference("source-missing"),
        ),
    )
    incomplete_foundation = replace(
        direct.current_foundation,
        classification_contract=incomplete_classification,
    )
    incomplete_b1 = replace(direct.general_orientation, foundation=incomplete_foundation)
    with pytest.raises(AnswerFoundationIntegrationError) as sources:
        VALIDATOR.validate(
            replace(
                direct,
                current_foundation=incomplete_foundation,
                general_orientation=incomplete_b1,
            )
        )
    assert sources.value.code == "INCOMPLETE_SOURCE_CHAIN_SET"


def test_current_and_highest_protection_are_not_automatically_repaired():
    value = complete()
    with pytest.raises(AnswerReferenceJourneyValidationError) as current:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(
                    value.journey,
                    current_protection_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                ),
            )
        )
    assert current.value.code == "CURRENT_PROTECTION_MISMATCH"
    with pytest.raises(AnswerReferenceJourneyValidationError) as highest:
        VALIDATOR.validate(
            replace(
                value,
                journey=replace(
                    value.journey,
                    highest_protection_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                ),
            )
        )
    assert highest.value.code == "HIGHEST_PROTECTION_MISMATCH"


def test_no_parallel_mode_order_runtime_or_semantic_power_exists():
    source = inspect.getsource(module)
    assert "class AnswerOperatingMode" not in source
    assert "_PROTECTION_LEVEL" not in source
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
        "state_machine",
    ):
        assert forbidden not in source
    assert AnswerReferenceJourneyStepType.JOURNEY_STOPPED in tuple(
        AnswerReferenceJourneyStepType
    )
