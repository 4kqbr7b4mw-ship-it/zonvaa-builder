import inspect
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from guardian_understanding import classification as classification_module
from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    answer_mode_protection_level,
    most_protective_answer_mode,
)
from guardian_understanding.classification import (
    ClassificationCapability,
    ClassificationProviderType,
    ClassificationReason,
    ClassificationUncertaintyStatus,
    ClassificationValidationError,
    GuardianClassificationContract,
    GuardianClassificationValidator,
)


VALIDATOR = GuardianClassificationValidator()


def classification(**changes):
    values = {
        "classification_id": "classification-1",
        "provided_minimum_level": AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        "candidate_levels": (
            AnswerOperatingMode.B1_GENERAL_ORIENTATION,
            AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        ),
        "effective_level": AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        "classification_reason": ClassificationReason.PROTECTIVE_ESCALATION,
        "professional_decision_requested": False,
        "provider_type": ClassificationProviderType.TYPED_INPUT_ADAPTER,
        "provider_reference": "adapter:typed-classification-1",
        "classified_at": datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc),
        "uncertainty_status": ClassificationUncertaintyStatus.UNCERTAIN,
        "conversation_context_reference": "conversation:context-1",
        "previous_classification_id": None,
        "capabilities": (
            ClassificationCapability.RECORD_PROVIDED_CLASSIFICATION,
        ),
    }
    values.update(changes)
    return GuardianClassificationContract(**values)


def test_complete_provided_classification_contract_is_valid():
    value = classification()
    assert VALIDATOR.validate(value) is value
    assert value.candidate_levels == (
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
    )


def test_successful_validation_returns_the_same_unchanged_contract():
    value = classification()
    assert VALIDATOR.validate(value) is value


def test_classification_reuses_the_canonical_answer_operating_modes():
    assert classification_module.AnswerOperatingMode is AnswerOperatingMode
    assert set(classification().candidate_levels) <= set(AnswerOperatingMode)


def test_classification_module_has_no_second_protection_order():
    source = inspect.getsource(classification_module)
    assert "_PROTECTION_LEVEL" not in source
    assert "class AnswerOperatingMode" not in source
    assert classification_module.most_protective_answer_mode is most_protective_answer_mode
    assert classification_module.answer_mode_protection_level is answer_mode_protection_level


def test_empty_candidate_levels_are_rejected():
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(classification(candidate_levels=()))
    assert error.value.code == "EMPTY_CANDIDATES"


def test_duplicate_candidate_levels_are_rejected():
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(
            classification(
                candidate_levels=(
                    AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                    AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                )
            )
        )
    assert error.value.code == "DUPLICATE_CANDIDATES"


def test_untyped_candidate_level_is_rejected():
    with pytest.raises(TypeError, match="candidate_levels"):
        classification(candidate_levels=("B2_PERSONAL_PREPARATION",))


@pytest.mark.parametrize(
    ("candidates", "effective"),
    (
        (
            (
                AnswerOperatingMode.B1_GENERAL_ORIENTATION,
                AnswerOperatingMode.B2_PERSONAL_PREPARATION,
            ),
            AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        ),
        (
            (
                AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
            ),
            AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        ),
    ),
)
def test_effective_level_is_the_canonical_highest_candidate(candidates, effective):
    value = classification(
        candidate_levels=candidates,
        effective_level=effective,
        professional_decision_requested=(
            effective is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        ),
    )
    assert VALIDATOR.validate(value).effective_level is effective


def test_non_maximum_effective_level_is_rejected():
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(
            classification(effective_level=AnswerOperatingMode.B1_GENERAL_ORIENTATION)
        )
    assert error.value.code == "EFFECTIVE_LEVEL_NOT_PROTECTIVE_MAXIMUM"


def test_provided_minimum_level_cannot_be_undercut():
    value = classification(
        provided_minimum_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    )
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "MINIMUM_LEVEL_NOT_MET"


def test_protective_escalation_above_minimum_is_valid():
    value = classification(
        provided_minimum_level=AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        candidate_levels=(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,),
        effective_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=True,
    )
    assert VALIDATOR.validate(value) is value


def test_provided_professional_decision_with_b3_is_valid():
    value = classification(
        candidate_levels=(
            AnswerOperatingMode.B2_PERSONAL_PREPARATION,
            AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        ),
        effective_level=AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        professional_decision_requested=True,
    )
    assert VALIDATOR.validate(value) is value


def test_provided_professional_decision_without_b3_is_rejected():
    value = classification(
        candidate_levels=(AnswerOperatingMode.B2_PERSONAL_PREPARATION,),
        effective_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        professional_decision_requested=True,
    )
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "PROFESSIONAL_DECISION_REQUIRES_B3"


@pytest.mark.parametrize("reason", tuple(ClassificationReason))
def test_every_classification_reason_is_valid(reason):
    provider = (
        ClassificationProviderType.HUMAN_OPERATOR
        if reason is ClassificationReason.MANUAL_ASSIGNMENT
        else ClassificationProviderType.TYPED_INPUT_ADAPTER
    )
    assert VALIDATOR.validate(
        classification(classification_reason=reason, provider_type=provider)
    ).classification_reason is reason


@pytest.mark.parametrize("provider", tuple(ClassificationProviderType))
def test_every_provider_type_is_valid_and_only_records_origin(provider):
    value = classification(provider_type=provider)
    assert VALIDATOR.validate(value).provider_type is provider
    assert not hasattr(value, "provider_authorized")


def test_manual_assignment_by_human_operator_is_valid():
    value = classification(
        classification_reason=ClassificationReason.MANUAL_ASSIGNMENT,
        provider_type=ClassificationProviderType.HUMAN_OPERATOR,
    )
    assert VALIDATOR.validate(value) is value


@pytest.mark.parametrize(
    "provider",
    (
        ClassificationProviderType.TYPED_INPUT_ADAPTER,
        ClassificationProviderType.CLASSIFIER_MODEL,
    ),
)
def test_manual_assignment_by_adapter_or_model_is_rejected(provider):
    value = classification(
        classification_reason=ClassificationReason.MANUAL_ASSIGNMENT,
        provider_type=provider,
    )
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "MANUAL_ASSIGNMENT_REQUIRES_HUMAN"


@pytest.mark.parametrize("status", tuple(ClassificationUncertaintyStatus))
def test_every_classification_uncertainty_status_is_valid(status):
    value = classification(uncertainty_status=status)
    assert VALIDATOR.validate(value).uncertainty_status is status


def test_timezone_naive_classification_time_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        classification(classified_at=datetime(2026, 8, 1, 10, 0))


@pytest.mark.parametrize(
    "field",
    (
        "classification_id",
        "provider_reference",
        "conversation_context_reference",
    ),
)
def test_empty_required_reference_is_rejected(field):
    with pytest.raises(ValueError, match=field):
        classification(**{field: ""})


def test_empty_optional_previous_reference_is_rejected_when_present():
    with pytest.raises(ValueError, match="previous_classification_id"):
        classification(previous_classification_id="")


def test_previous_classification_cannot_reference_itself():
    value = classification(previous_classification_id="classification-1")
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "SELF_PREDECESSOR"


def test_previous_classification_is_declarative_without_history_logic():
    value = classification(previous_classification_id="classification-not-loaded")
    assert VALIDATOR.validate(value) is value
    assert value.previous_classification_id == "classification-not-loaded"
    assert not hasattr(value, "next_classification_id")


@pytest.mark.parametrize(
    "capability",
    tuple(
        capability
        for capability in ClassificationCapability
        if capability is not ClassificationCapability.RECORD_PROVIDED_CLASSIFICATION
    ),
)
def test_every_executing_capability_is_rejected(capability):
    value = classification(
        capabilities=(
            ClassificationCapability.RECORD_PROVIDED_CLASSIFICATION,
            capability,
        )
    )
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_missing_record_capability_is_rejected():
    with pytest.raises(ClassificationValidationError) as error:
        VALIDATOR.validate(classification(capabilities=()))
    assert error.value.code == "RECORD_CAPABILITY_MISSING"


def test_contract_is_immutable_and_deterministic():
    first = classification()
    second = classification()
    with pytest.raises(FrozenInstanceError):
        first.effective_level = AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
    assert first == second
    assert VALIDATOR.validate(first) == VALIDATOR.validate(second)
