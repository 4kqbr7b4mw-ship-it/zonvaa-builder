from dataclasses import FrozenInstanceError, replace

import pytest

from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    ClassificationReference,
)
from guardian_understanding.answer_foundation import (
    AnswerFoundationIntegrationError,
    GuardianAnswerFoundationIntegration,
)
from guardian_understanding.answer_reference_journey import (
    AnswerReferenceJourneyCompletionReason,
    AnswerReferenceJourneyOrigin,
    AnswerReferenceJourneyStatus,
    AnswerReferenceJourneyStep,
    AnswerReferenceJourneyStepResult,
    AnswerReferenceJourneyStepType,
    AnswerReferenceJourneyStopReason,
    AnswerReferenceJourneyValidationError,
    GuardianAnswerReferenceJourney,
    GuardianAnswerReferenceJourneyEnvelope,
    GuardianAnswerReferenceJourneyValidator,
    ProfessionalBoundaryReference,
    answer_foundation_reference,
)
from guardian_understanding.classification import ClassificationUncertaintyStatus
from guardian_understanding.controlled_orientation import (
    BoundaryReference,
    ControlledOrientationEnvelope,
    ControlledOrientationValidationError,
    OrientationProviderType,
)
from guardian_understanding.personal_preparation import (
    GeneralOrientationReference,
    KnownFactEntry,
    PersonalPreparationEnvelope,
)
from guardian_understanding.professional_decision_boundary import (
    PersonalPreparationReference,
    ProfessionalDecisionBoundaryEnvelope,
    ProfessionalDecisionBoundaryValidationError,
    UrgencyStatus,
)
from guardian_understanding.source_chain import (
    GuardianAnswerContextReference,
    SourceChainReference,
)
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_controlled_orientation_contract import orientation
from guardian_understanding.tests.test_personal_preparation_contract import preparation
from guardian_understanding.tests.test_professional_decision_boundary_contract import (
    professional_boundary,
)
from guardian_understanding.tests.test_source_chain import source_chain


CONTEXT = "conversation:answer-reference-1"
VALIDATOR = GuardianAnswerReferenceJourneyValidator()


def foundation(mode, suffix, *, decision=False, source_ids=None):
    source_ids = source_ids or ("source-{}".format(suffix),)
    classification_id = "classification-{}".format(suffix)
    boundary_id = "boundary-{}".format(suffix)
    classification_value = classification(
        classification_id=classification_id,
        provided_minimum_level=mode,
        candidate_levels=(mode,),
        effective_level=mode,
        professional_decision_requested=decision,
        conversation_context_reference=CONTEXT,
        uncertainty_status=ClassificationUncertaintyStatus.UNCERTAIN,
        source_chain_references=tuple(
            SourceChainReference(item) for item in source_ids
        ),
    )
    boundary_value = boundary(
        mode,
        boundary_id=boundary_id,
        classification_reference=ClassificationReference(classification_id),
    )
    sources = tuple(
        source_chain(
            source_chain_id=item,
            declared_contradictions=(),
            answer_context_reference=GuardianAnswerContextReference(
                guardian_answer_id="answer-{}".format(suffix),
                conversation_context_id=CONTEXT,
            ),
        )
        for item in source_ids
    )
    return GuardianAnswerFoundationIntegration(
        boundary_contract=boundary_value,
        classification_contract=classification_value,
        source_chain_contracts=sources,
        require_complete_source_chain_set=True,
    )


def b1_stage(suffix="b1"):
    value = foundation(AnswerOperatingMode.B1_GENERAL_ORIENTATION, suffix)
    return ControlledOrientationEnvelope(
        foundation=value,
        orientation=orientation(
            orientation_id="orientation-{}".format(suffix),
            classification_reference=ClassificationReference(
                value.classification_contract.classification_id
            ),
            boundary_reference=BoundaryReference(
                value.boundary_contract.boundary_id
            ),
            source_chain_references=tuple(
                SourceChainReference(item.source_chain_id)
                for item in value.source_chain_contracts
            ),
        ),
    )


def b2_stage(b1=None, suffix="b2"):
    value = foundation(AnswerOperatingMode.B2_PERSONAL_PREPARATION, suffix)
    return PersonalPreparationEnvelope(
        foundation=value,
        preparation=preparation(
            preparation_id="preparation-{}".format(suffix),
            classification_reference=ClassificationReference(
                value.classification_contract.classification_id
            ),
            boundary_reference=BoundaryReference(
                value.boundary_contract.boundary_id
            ),
            source_chain_references=tuple(
                SourceChainReference(item.source_chain_id)
                for item in value.source_chain_contracts
            ),
            known_facts=(
                KnownFactEntry(
                    "fact-{}".format(suffix),
                    "Bereitgestellte Tatsache für die Referenzreise.",
                    (
                        SourceChainReference(
                            value.source_chain_contracts[0].source_chain_id
                        ),
                    ),
                ),
            ),
            general_orientation_reference=(
                GeneralOrientationReference(b1.orientation.orientation_id)
                if b1 is not None
                else None
            ),
        ),
        general_orientation=b1,
    )


def b3_stage(
    b1=None,
    b2=None,
    suffix="b3",
    *,
    urgency=UrgencyStatus.NOT_DECLARED_URGENT,
    urgent_help_notice=None,
):
    value = foundation(
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        suffix,
        decision=True,
    )
    return ProfessionalDecisionBoundaryEnvelope(
        foundation=value,
        professional_boundary=professional_boundary(
            professional_boundary_id="professional-boundary-{}".format(suffix),
            classification_reference=ClassificationReference(
                value.classification_contract.classification_id
            ),
            boundary_reference=BoundaryReference(
                value.boundary_contract.boundary_id
            ),
            source_chain_references=tuple(
                SourceChainReference(item.source_chain_id)
                for item in value.source_chain_contracts
            ),
            professional_review_topics=tuple(
                replace(
                    item,
                    source_chain_references=(
                        SourceChainReference(value.source_chain_contracts[0].source_chain_id),
                    ),
                )
                for item in professional_boundary().professional_review_topics
            ),
            general_orientation_reference=(
                GeneralOrientationReference(b1.orientation.orientation_id)
                if b1 is not None
                else None
            ),
            personal_preparation_reference=(
                PersonalPreparationReference(b2.preparation.preparation_id)
                if b2 is not None
                else None
            ),
            urgency_status=urgency,
            urgent_help_notice=urgent_help_notice,
        ),
        general_orientation=b1,
        personal_preparation=b2,
    )


def supplied_stages(b1=None, b2=None, b3=None):
    result = []
    if b1 is not None:
        result.append(
            (
                AnswerOperatingMode.B1_GENERAL_ORIENTATION,
                b1.foundation,
                b1.orientation.orientation_id,
                AnswerReferenceJourneyStepType.B1_ORIENTATION_PROVIDED,
                b1.orientation.professional_review_status,
            )
        )
    if b2 is not None:
        result.append(
            (
                AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                b2.foundation,
                b2.preparation.preparation_id,
                AnswerReferenceJourneyStepType.B2_PREPARATION_PROVIDED,
                b2.preparation.professional_review_status,
            )
        )
    if b3 is not None:
        result.append(
            (
                AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
                b3.foundation,
                b3.professional_boundary.professional_boundary_id,
                AnswerReferenceJourneyStepType.B3_PROFESSIONAL_BOUNDARY_PROVIDED,
                b3.professional_boundary.professional_review_status,
            )
        )
    return tuple(result)


def journey_steps(stages, *, stopped=False, stop_reason=None):
    steps = []

    def add(step_type, references, mode, result):
        steps.append(
            AnswerReferenceJourneyStep(
                step_id="step-{:02d}".format(len(steps) + 1),
                step_type=step_type,
                referenced_contract_ids=references,
                protection_level=mode,
                order=len(steps) + 1,
                result_status=result,
                stop_reason=None,
                provenance="provenance:reference-scenario",
            )
        )

    for mode, value, artifact_id, artifact_type, _ in stages:
        add(
            AnswerReferenceJourneyStepType.CLASSIFICATION_PROVIDED,
            (value.classification_contract.classification_id,),
            mode,
            AnswerReferenceJourneyStepResult.PROVIDED,
        )
        add(
            AnswerReferenceJourneyStepType.ANSWER_BOUNDARY_VALIDATED,
            (value.boundary_contract.boundary_id,),
            mode,
            AnswerReferenceJourneyStepResult.VALIDATED,
        )
        add(
            AnswerReferenceJourneyStepType.SOURCE_CHAINS_BOUND,
            tuple(item.source_chain_id for item in value.source_chain_contracts),
            mode,
            AnswerReferenceJourneyStepResult.BOUND,
        )
        add(
            AnswerReferenceJourneyStepType.ANSWER_FOUNDATION_VALIDATED,
            (
                value.classification_contract.classification_id,
                value.boundary_contract.boundary_id,
            ),
            mode,
            AnswerReferenceJourneyStepResult.VALIDATED,
        )
        add(
            artifact_type,
            (artifact_id,),
            mode,
            AnswerReferenceJourneyStepResult.PROVIDED,
        )
    final_mode = stages[-1][0]
    steps.append(
        AnswerReferenceJourneyStep(
            step_id="step-{:02d}".format(len(steps) + 1),
            step_type=(
                AnswerReferenceJourneyStepType.JOURNEY_STOPPED
                if stopped
                else AnswerReferenceJourneyStepType.JOURNEY_COMPLETED
            ),
            referenced_contract_ids=("answer-journey-1",),
            protection_level=final_mode,
            order=len(steps) + 1,
            result_status=(
                AnswerReferenceJourneyStepResult.STOPPED
                if stopped
                else AnswerReferenceJourneyStepResult.COMPLETED
            ),
            stop_reason=stop_reason if stopped else None,
            provenance="provenance:reference-scenario",
        )
    )
    return tuple(steps)


def journey_envelope(b1=None, b2=None, b3=None, *, stopped=False, stop_reason=None):
    stages = supplied_stages(b1, b2, b3)
    mode, current, _, _, review_status = stages[-1]
    completion = {
        AnswerOperatingMode.B1_GENERAL_ORIENTATION: (
            AnswerReferenceJourneyCompletionReason.GENERAL_ORIENTATION_COMPLETE
        ),
        AnswerOperatingMode.B2_PERSONAL_PREPARATION: (
            AnswerReferenceJourneyCompletionReason.PERSONAL_PREPARATION_COMPLETE
        ),
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: (
            AnswerReferenceJourneyCompletionReason.PROFESSIONAL_BOUNDARY_COMPLETE
        ),
    }[mode]
    journey = GuardianAnswerReferenceJourney(
        journey_id="answer-journey-1",
        conversation_context_reference=CONTEXT,
        origin=AnswerReferenceJourneyOrigin.PROVIDED_VALIDATION_SCENARIO,
        current_protection_level=mode,
        highest_protection_level=mode,
        classification_reference=ClassificationReference(
            current.classification_contract.classification_id
        ),
        boundary_reference=BoundaryReference(current.boundary_contract.boundary_id),
        foundation_reference=answer_foundation_reference(current),
        general_orientation_reference=(
            GeneralOrientationReference(b1.orientation.orientation_id)
            if b1 is not None
            else None
        ),
        personal_preparation_reference=(
            PersonalPreparationReference(b2.preparation.preparation_id)
            if b2 is not None
            else None
        ),
        professional_boundary_reference=(
            ProfessionalBoundaryReference(
                b3.professional_boundary.professional_boundary_id
            )
            if b3 is not None
            else None
        ),
        steps=journey_steps(stages, stopped=stopped, stop_reason=stop_reason),
        status=(
            AnswerReferenceJourneyStatus.STOPPED
            if stopped
            else AnswerReferenceJourneyStatus.COMPLETED
        ),
        completion_reason=(
            AnswerReferenceJourneyCompletionReason.CONTROLLED_STOP
            if stopped
            else completion
        ),
        stop_reason=stop_reason if stopped else None,
        uncertainty_status=current.classification_contract.uncertainty_status,
        provider_type=OrientationProviderType.TYPED_INPUT_ADAPTER,
        provider_reference="adapter:answer-reference-journey-1",
        professional_review_status=review_status,
        provenance="provenance:reference-journey-1",
        previous_journey_id=None,
    )
    return GuardianAnswerReferenceJourneyEnvelope(
        journey=journey,
        current_foundation=current,
        general_orientation=b1,
        personal_preparation=b2,
        professional_boundary=b3,
    )


def test_valid_b1_reference_journey():
    b1 = b1_stage()
    value = journey_envelope(b1=b1)
    assert VALIDATOR.validate(value) is value


def test_valid_b1_to_b2_and_direct_b2_journeys():
    b1 = b1_stage()
    b2 = b2_stage(b1)
    assert VALIDATOR.validate(journey_envelope(b1=b1, b2=b2))
    direct_b2 = b2_stage()
    assert VALIDATOR.validate(journey_envelope(b2=direct_b2))


def test_valid_complete_b1_b2_b3_and_direct_b3_journeys():
    b1 = b1_stage()
    b2 = b2_stage(b1)
    b3 = b3_stage(b1, b2)
    value = journey_envelope(b1=b1, b2=b2, b3=b3)
    assert VALIDATOR.validate(value) is value
    assert value.journey.highest_protection_level is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
    direct_b3 = b3_stage()
    assert VALIDATOR.validate(journey_envelope(b3=direct_b3))


def test_immediate_help_b3_requires_and_preserves_supplied_notice():
    b3 = b3_stage(
        urgency=UrgencyStatus.IMMEDIATE_HELP_REQUIRED,
        urgent_help_notice="Bereitgestellter Soforthilfehinweis.",
    )
    value = journey_envelope(b3=b3)
    assert VALIDATOR.validate(value) is value
    invalid_contract = replace(
        b3.professional_boundary,
        urgent_help_notice=None,
    )
    invalid = replace(b3, professional_boundary=invalid_contract)
    with pytest.raises(
        ProfessionalDecisionBoundaryValidationError,
        match="supplied help notice",
    ):
        VALIDATOR.validate(journey_envelope(b3=invalid))


def test_controlled_stop_is_final_and_requires_the_same_typed_reason():
    b1 = b1_stage()
    value = journey_envelope(
        b1=b1,
        stopped=True,
        stop_reason=AnswerReferenceJourneyStopReason.MISSING_REFERENCE,
    )
    assert VALIDATOR.validate(value) is value
    final = value.journey.steps[-1]
    extra = replace(
        final,
        step_id="step-extra",
        order=final.order + 1,
        step_type=AnswerReferenceJourneyStepType.JOURNEY_COMPLETED,
        result_status=AnswerReferenceJourneyStepResult.COMPLETED,
        stop_reason=None,
    )
    with pytest.raises(AnswerReferenceJourneyValidationError) as error:
        VALIDATOR.validate(
            replace(value, journey=replace(value.journey, steps=value.journey.steps + (extra,)))
        )
    assert error.value.code == "INVALID_STEP_SEQUENCE"


def test_contract_and_input_objects_are_immutable_and_returned_unchanged():
    b1 = b1_stage()
    b2 = b2_stage(b1)
    b3 = b3_stage(b1, b2)
    value = journey_envelope(b1=b1, b2=b2, b3=b3)
    result = VALIDATOR.validate(value)
    assert result is value
    assert result.general_orientation is b1
    assert result.personal_preparation is b2
    assert result.professional_boundary is b3
    assert result.current_foundation is b3.foundation
    with pytest.raises(FrozenInstanceError):
        value.journey.status = AnswerReferenceJourneyStatus.STOPPED
