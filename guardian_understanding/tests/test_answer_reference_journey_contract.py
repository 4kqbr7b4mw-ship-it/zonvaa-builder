from dataclasses import FrozenInstanceError, replace

import pytest

from guardian_understanding.answer_reference_journey import (
    AnswerReferenceJourneyCapability,
    AnswerReferenceJourneyCompletionReason,
    AnswerReferenceJourneyOrigin,
    AnswerReferenceJourneyStatus,
    AnswerReferenceJourneyStopReason,
    AnswerReferenceJourneyValidationError,
    GuardianAnswerReferenceJourneyContractValidator,
)
from guardian_understanding.tests.test_answer_reference_journey_end_to_end import (
    b1_stage,
    journey_envelope,
)


VALIDATOR = GuardianAnswerReferenceJourneyContractValidator()


def journey():
    return journey_envelope(b1=b1_stage()).journey


def test_complete_contract_is_immutable_and_returned_unchanged():
    value = journey()
    assert VALIDATOR.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.journey_id = "changed"


@pytest.mark.parametrize(
    "field",
    (
        "journey_id",
        "conversation_context_reference",
        "provider_reference",
        "provenance",
    ),
)
def test_required_text_is_non_empty(field):
    with pytest.raises(ValueError, match=field):
        replace(journey(), **{field: ""})


@pytest.mark.parametrize("origin", tuple(AnswerReferenceJourneyOrigin))
def test_every_typed_origin_is_declarative(origin):
    value = replace(journey(), origin=origin)
    assert VALIDATOR.validate(value) is value


def test_step_ids_and_order_are_unique_and_contiguous():
    value = journey()
    duplicate = replace(value.steps[1], step_id=value.steps[0].step_id)
    with pytest.raises(AnswerReferenceJourneyValidationError) as ids:
        VALIDATOR.validate(replace(value, steps=(value.steps[0], duplicate) + value.steps[2:]))
    assert ids.value.code == "DUPLICATE_STEP_ID"
    reordered = replace(value.steps[1], order=9)
    with pytest.raises(AnswerReferenceJourneyValidationError) as order:
        VALIDATOR.validate(replace(value, steps=(value.steps[0], reordered) + value.steps[2:]))
    assert order.value.code == "INVALID_STEP_ORDER"


def test_completed_and_stopped_status_fields_are_structurally_consistent():
    value = journey()
    with pytest.raises(AnswerReferenceJourneyValidationError) as completed:
        VALIDATOR.validate(
            replace(
                value,
                stop_reason=AnswerReferenceJourneyStopReason.MISSING_REFERENCE,
            )
        )
    assert completed.value.code == "UNEXPECTED_STOP_REASON"
    with pytest.raises(AnswerReferenceJourneyValidationError) as stopped:
        VALIDATOR.validate(
            replace(
                value,
                status=AnswerReferenceJourneyStatus.STOPPED,
                completion_reason=AnswerReferenceJourneyCompletionReason.CONTROLLED_STOP,
                stop_reason=None,
            )
        )
    assert stopped.value.code == "STOP_REASON_REQUIRED"


def test_previous_journey_reference_is_declarative_and_not_self_referential():
    value = replace(journey(), previous_journey_id="journey:previous")
    assert VALIDATOR.validate(value) is value
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(replace(value, previous_journey_id=value.journey_id))
    assert error.value.code == "SELF_PREDECESSOR"


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in AnswerReferenceJourneyCapability
        if item is not AnswerReferenceJourneyCapability.RECORD_PROVIDED_JOURNEY
    ),
)
def test_every_executing_capability_is_rejected(capability):
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(
            replace(
                journey(),
                capabilities=(
                    AnswerReferenceJourneyCapability.RECORD_PROVIDED_JOURNEY,
                    capability,
                ),
            )
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"
