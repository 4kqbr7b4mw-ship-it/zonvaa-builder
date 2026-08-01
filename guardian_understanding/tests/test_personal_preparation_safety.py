import inspect

import pytest

from guardian_understanding import (
    AnswerOperatingMode,
    B2PersonalPreparationSafetyValidator,
    PersonalPreparationValidationError,
)
from guardian_understanding import personal_preparation
from guardian_understanding.answer_boundary import answer_mode_protection_level
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_personal_preparation_contract import preparation


VALIDATOR = B2PersonalPreparationSafetyValidator()


def classified(mode, professional_decision_requested=False):
    return classification(
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        professional_decision_requested=professional_decision_requested,
    )


def test_exact_b2_classification_and_boundary_are_valid_and_unchanged():
    value = preparation()
    assert VALIDATOR.validate(
        value,
        classified(AnswerOperatingMode.B2_PERSONAL_PREPARATION),
        boundary(AnswerOperatingMode.B2_PERSONAL_PREPARATION),
    ) is value


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_b1_or_b3_classification_is_rejected(mode):
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(
            preparation(),
            classified(
                mode,
                professional_decision_requested=(
                    mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
                ),
            ),
            boundary(AnswerOperatingMode.B2_PERSONAL_PREPARATION),
        )
    assert error.value.code == "CLASSIFICATION_NOT_B2"


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_b1_or_b3_boundary_is_rejected(mode):
    with pytest.raises(PersonalPreparationValidationError) as error:
        VALIDATOR.validate(
            preparation(),
            classified(AnswerOperatingMode.B2_PERSONAL_PREPARATION),
            boundary(mode),
        )
    assert error.value.code == "BOUNDARY_NOT_B2"


def test_professional_decision_request_cannot_be_personal_preparation():
    with pytest.raises(PersonalPreparationValidationError):
        VALIDATOR.validate(
            preparation(),
            classified(
                AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
                professional_decision_requested=True,
            ),
            boundary(AnswerOperatingMode.B2_PERSONAL_PREPARATION),
        )


def test_canonical_mode_and_protection_order_are_reused_without_text_analysis():
    source = inspect.getsource(personal_preparation)
    assert personal_preparation.AnswerOperatingMode is AnswerOperatingMode
    assert (
        personal_preparation.answer_mode_protection_level
        is answer_mode_protection_level
    )
    assert "_PROTECTION_LEVEL" not in source
    assert "class AnswerOperatingMode" not in source
    assert "def analyze" not in source
    assert "selected_option" not in source
