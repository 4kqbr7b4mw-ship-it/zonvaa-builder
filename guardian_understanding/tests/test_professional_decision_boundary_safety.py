import inspect

import pytest

from guardian_understanding import (
    AnswerOperatingMode,
    B3ProfessionalDecisionBoundarySafetyValidator,
    ProfessionalDecisionBoundaryValidationError,
)
from guardian_understanding import professional_decision_boundary as module
from guardian_understanding.answer_boundary import answer_mode_protection_level
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_professional_decision_boundary_contract import professional_boundary


VALIDATOR = B3ProfessionalDecisionBoundarySafetyValidator()


def classified(mode, requested):
    return classification(
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        professional_decision_requested=requested,
    )


def test_exact_b3_with_professional_decision_request_is_valid():
    value = professional_boundary()
    assert VALIDATOR.validate(
        value,
        classified(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, True),
        boundary(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED),
    ) is value


@pytest.mark.parametrize("mode", (AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B2_PERSONAL_PREPARATION))
def test_b1_or_b2_classification_is_rejected(mode):
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(
            professional_boundary(),
            classified(mode, False),
            boundary(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED),
        )
    assert error.value.code == "CLASSIFICATION_NOT_B3"


@pytest.mark.parametrize("mode", (AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B2_PERSONAL_PREPARATION))
def test_b1_or_b2_boundary_is_rejected(mode):
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(
            professional_boundary(),
            classified(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, True),
            boundary(mode),
        )
    assert error.value.code == "BOUNDARY_NOT_B3"


def test_false_professional_decision_flag_is_rejected():
    invalid = classification(
        provided_minimum_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        candidate_levels=(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,),
        effective_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=False,
    )
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(
            professional_boundary(),
            invalid,
            boundary(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED),
        )
    assert error.value.code == "PROFESSIONAL_DECISION_NOT_REQUESTED"


def test_canonical_mode_and_order_are_reused_without_text_or_source_analysis():
    source = inspect.getsource(module)
    assert module.AnswerOperatingMode is AnswerOperatingMode
    assert module.answer_mode_protection_level is answer_mode_protection_level
    assert "_PROTECTION_LEVEL" not in source
    assert "class AnswerOperatingMode" not in source
    assert "def analyze" not in source
    assert "def evaluate_source" not in source
