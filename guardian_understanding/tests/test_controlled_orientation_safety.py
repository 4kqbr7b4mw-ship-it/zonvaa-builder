import inspect

import pytest

from guardian_understanding import (
    AnswerOperatingMode,
    B1OrientationSafetyValidator,
    ControlledOrientationValidationError,
)
from guardian_understanding import controlled_orientation
from guardian_understanding.answer_boundary import answer_mode_protection_level
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_controlled_orientation_contract import orientation


VALIDATOR = B1OrientationSafetyValidator()


def evidence(mode=AnswerOperatingMode.B1_GENERAL_ORIENTATION, **classification_changes):
    classification_value = classification(
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        **classification_changes
    )
    boundary_value = boundary(mode)
    return classification_value, boundary_value


def test_exact_b1_classification_and_boundary_are_valid():
    classification_value, boundary_value = evidence()
    value = orientation()
    assert VALIDATOR.validate(value, classification_value, boundary_value) is value


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_b2_or_b3_classification_is_rejected(mode):
    classification_value, _ = evidence(
        mode,
        professional_decision_requested=(
            mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        ),
    )
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(
            orientation(),
            classification_value,
            boundary(AnswerOperatingMode.B1_GENERAL_ORIENTATION),
        )
    assert error.value.code == "CLASSIFICATION_NOT_B1"


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_b2_or_b3_boundary_is_rejected(mode):
    classification_value, _ = evidence()
    with pytest.raises(ControlledOrientationValidationError) as error:
        VALIDATOR.validate(orientation(), classification_value, boundary(mode))
    assert error.value.code == "BOUNDARY_NOT_B1"


def test_professional_decision_request_cannot_be_a_b1_orientation():
    classification_value = classification(
        provided_minimum_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        candidate_levels=(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,),
        effective_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=True,
    )
    with pytest.raises(ControlledOrientationValidationError):
        VALIDATOR.validate(
            orientation(),
            classification_value,
            boundary(AnswerOperatingMode.B1_GENERAL_ORIENTATION),
        )


def test_safety_module_reuses_canonical_mode_without_a_second_protection_order():
    source = inspect.getsource(controlled_orientation)
    assert controlled_orientation.AnswerOperatingMode is AnswerOperatingMode
    assert (
        controlled_orientation.answer_mode_protection_level
        is answer_mode_protection_level
    )
    assert "_PROTECTION_LEVEL" not in source
    assert "class AnswerOperatingMode" not in source
    assert "def analyze" not in source
    assert "def evaluate_source" not in source.lower()


def test_reference_mismatches_are_rejected_without_loading_contracts():
    classification_value, boundary_value = evidence()
    with pytest.raises(ControlledOrientationValidationError) as classification_error:
        VALIDATOR.validate(
            orientation(
                classification_reference=type(
                    orientation().classification_reference
                )("classification-other")
            ),
            classification_value,
            boundary_value,
        )
    assert classification_error.value.code == "CLASSIFICATION_REFERENCE_MISMATCH"
