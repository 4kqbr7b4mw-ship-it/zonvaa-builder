"""Immutable reference journey and UI-neutral projection for Guardian answers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.answer_boundary import (
    AnswerBoundaryContract,
    AnswerOperatingMode,
    ClassificationReference,
    answer_mode_protection_level,
    most_protective_answer_mode,
)
from guardian_understanding.answer_foundation import (
    GuardianAnswerFoundationIntegration,
    GuardianAnswerFoundationIntegrationValidator,
)
from guardian_understanding.classification import ClassificationUncertaintyStatus
from guardian_understanding.controlled_orientation import (
    B1OrientationContract,
    BoundaryReference,
    ControlledOrientationEnvelope,
    ControlledOrientationEnvelopeValidator,
    OrientationProviderType,
    ProfessionalReviewStatus,
)
from guardian_understanding.personal_preparation import (
    B2PersonalPreparationContract,
    GeneralOrientationReference,
    KnownFactEntry,
    OpenQuestionEntry,
    OptionForConsiderationEntry,
    PersonalPreparationEnvelope,
    PersonalPreparationEnvelopeValidator,
    ProfessionalReviewTopicEntry,
    UncertaintyEntry,
)
from guardian_understanding.professional_decision_boundary import (
    B3ProfessionalDecisionBoundaryContract,
    PersonalPreparationReference,
    ProfessionalBoundaryReviewTopic,
    ProfessionalDecisionBoundaryEnvelope,
    ProfessionalDecisionBoundaryEnvelopeValidator,
    UrgencyStatus,
)
from guardian_understanding.source_chain import GuardianSourceChainContract


class AnswerReferenceJourneyOrigin(str, Enum):
    PROVIDED_REFERENCE = "PROVIDED_REFERENCE"
    PROVIDED_VALIDATION_SCENARIO = "PROVIDED_VALIDATION_SCENARIO"
    HUMAN_REVIEW_RECORD = "HUMAN_REVIEW_RECORD"


class AnswerReferenceJourneyStepType(str, Enum):
    CLASSIFICATION_PROVIDED = "CLASSIFICATION_PROVIDED"
    ANSWER_BOUNDARY_VALIDATED = "ANSWER_BOUNDARY_VALIDATED"
    SOURCE_CHAINS_BOUND = "SOURCE_CHAINS_BOUND"
    ANSWER_FOUNDATION_VALIDATED = "ANSWER_FOUNDATION_VALIDATED"
    B1_ORIENTATION_PROVIDED = "B1_ORIENTATION_PROVIDED"
    B2_PREPARATION_PROVIDED = "B2_PREPARATION_PROVIDED"
    B3_PROFESSIONAL_BOUNDARY_PROVIDED = "B3_PROFESSIONAL_BOUNDARY_PROVIDED"
    JOURNEY_COMPLETED = "JOURNEY_COMPLETED"
    JOURNEY_STOPPED = "JOURNEY_STOPPED"


class AnswerReferenceJourneyStepResult(str, Enum):
    PROVIDED = "PROVIDED"
    VALIDATED = "VALIDATED"
    BOUND = "BOUND"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


class AnswerReferenceJourneyStatus(str, Enum):
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


class AnswerReferenceJourneyCompletionReason(str, Enum):
    GENERAL_ORIENTATION_COMPLETE = "GENERAL_ORIENTATION_COMPLETE"
    PERSONAL_PREPARATION_COMPLETE = "PERSONAL_PREPARATION_COMPLETE"
    PROFESSIONAL_BOUNDARY_COMPLETE = "PROFESSIONAL_BOUNDARY_COMPLETE"
    CONTROLLED_STOP = "CONTROLLED_STOP"


class AnswerReferenceJourneyStopReason(str, Enum):
    MISSING_REFERENCE = "MISSING_REFERENCE"
    CONTRADICTORY_REFERENCE = "CONTRADICTORY_REFERENCE"
    PROTECTION_DOWNGRADE = "PROTECTION_DOWNGRADE"
    INCOMPLETE_SOURCE_BINDING = "INCOMPLETE_SOURCE_BINDING"
    OBJECT_IDENTITY_MISMATCH = "OBJECT_IDENTITY_MISMATCH"
    MODE_CONTRACT_MISMATCH = "MODE_CONTRACT_MISMATCH"
    REQUIRED_URGENT_HELP_NOTICE_MISSING = (
        "REQUIRED_URGENT_HELP_NOTICE_MISSING"
    )
    REFERENCED_VALIDATOR_REJECTED = "REFERENCED_VALIDATOR_REJECTED"


class AnswerReferenceJourneyCapability(str, Enum):
    RECORD_PROVIDED_JOURNEY = "RECORD_PROVIDED_JOURNEY"
    GENERATE_CONTENT = "GENERATE_CONTENT"
    INTERPRET_NATURAL_LANGUAGE = "INTERPRET_NATURAL_LANGUAGE"
    CLASSIFY_REQUEST = "CLASSIFY_REQUEST"
    ACTIVATE_ANSWER_MODE = "ACTIVATE_ANSWER_MODE"
    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    EVALUATE_SOURCE = "EVALUATE_SOURCE"
    DETECT_DANGER = "DETECT_DANGER"
    TRIAGE = "TRIAGE"
    SELECT_PROFESSIONAL = "SELECT_PROFESSIONAL"
    CONTACT_PROVIDER = "CONTACT_PROVIDER"
    TRIGGER_EMERGENCY_CALL = "TRIGGER_EMERGENCY_CALL"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    PERSIST_JOURNEY = "PERSIST_JOURNEY"


NON_EXECUTING_JOURNEY_CAPABILITIES = (
    AnswerReferenceJourneyCapability.RECORD_PROVIDED_JOURNEY,
)


class GuardianAnswerExperienceAction(str, Enum):
    VIEW_GENERAL_ORIENTATION = "VIEW_GENERAL_ORIENTATION"
    VIEW_PERSONAL_PREPARATION = "VIEW_PERSONAL_PREPARATION"
    VIEW_PROFESSIONAL_BOUNDARY = "VIEW_PROFESSIONAL_BOUNDARY"
    VIEW_SOURCES = "VIEW_SOURCES"
    VIEW_UNCERTAINTIES = "VIEW_UNCERTAINTIES"
    VIEW_PROFESSIONAL_REVIEW_TOPICS = "VIEW_PROFESSIONAL_REVIEW_TOPICS"
    ACKNOWLEDGE_BOUNDARY = "ACKNOWLEDGE_BOUNDARY"


@dataclass(frozen=True)
class AnswerFoundationReference:
    classification_id: str
    boundary_id: str
    source_chain_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.classification_id, "classification_id")
        _text(self.boundary_id, "boundary_id")
        _strings(self.source_chain_ids, "source_chain_ids")


def answer_foundation_reference(
    foundation: GuardianAnswerFoundationIntegration,
) -> AnswerFoundationReference:
    """Project an immutable composite reference without assigning a new ID."""

    if not isinstance(foundation, GuardianAnswerFoundationIntegration):
        raise TypeError("foundation must be a GuardianAnswerFoundationIntegration")
    return AnswerFoundationReference(
        classification_id=foundation.classification_contract.classification_id,
        boundary_id=foundation.boundary_contract.boundary_id,
        source_chain_ids=tuple(
            source.source_chain_id for source in foundation.source_chain_contracts
        ),
    )


@dataclass(frozen=True)
class ProfessionalBoundaryReference:
    professional_boundary_id: str

    def __post_init__(self) -> None:
        _text(self.professional_boundary_id, "professional_boundary_id")


@dataclass(frozen=True)
class AnswerReferenceJourneyStep:
    step_id: str
    step_type: AnswerReferenceJourneyStepType
    referenced_contract_ids: Tuple[str, ...]
    protection_level: AnswerOperatingMode
    order: int
    result_status: AnswerReferenceJourneyStepResult
    stop_reason: Optional[AnswerReferenceJourneyStopReason]
    provenance: str

    def __post_init__(self) -> None:
        _text(self.step_id, "step_id")
        _enum(self.step_type, AnswerReferenceJourneyStepType, "step_type")
        _strings(self.referenced_contract_ids, "referenced_contract_ids")
        _enum(self.protection_level, AnswerOperatingMode, "protection_level")
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 1:
            raise ValueError("order must be a positive integer")
        _enum(self.result_status, AnswerReferenceJourneyStepResult, "result_status")
        if self.stop_reason is not None:
            _enum(self.stop_reason, AnswerReferenceJourneyStopReason, "stop_reason")
        _text(self.provenance, "provenance")


@dataclass(frozen=True)
class GuardianAnswerReferenceJourney:
    journey_id: str
    conversation_context_reference: str
    origin: AnswerReferenceJourneyOrigin
    current_protection_level: AnswerOperatingMode
    highest_protection_level: AnswerOperatingMode
    classification_reference: ClassificationReference
    boundary_reference: BoundaryReference
    foundation_reference: AnswerFoundationReference
    general_orientation_reference: Optional[GeneralOrientationReference]
    personal_preparation_reference: Optional[PersonalPreparationReference]
    professional_boundary_reference: Optional[ProfessionalBoundaryReference]
    steps: Tuple[AnswerReferenceJourneyStep, ...]
    status: AnswerReferenceJourneyStatus
    completion_reason: AnswerReferenceJourneyCompletionReason
    stop_reason: Optional[AnswerReferenceJourneyStopReason]
    uncertainty_status: ClassificationUncertaintyStatus
    provider_type: OrientationProviderType
    provider_reference: str
    professional_review_status: ProfessionalReviewStatus
    provenance: str
    previous_journey_id: Optional[str]
    capabilities: Tuple[AnswerReferenceJourneyCapability, ...] = (
        AnswerReferenceJourneyCapability.RECORD_PROVIDED_JOURNEY,
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.journey_id, "journey_id"),
            (self.conversation_context_reference, "conversation_context_reference"),
            (self.provenance, "provenance"),
            (self.provider_reference, "provider_reference"),
        ):
            _text(value, name)
        _enum(self.origin, AnswerReferenceJourneyOrigin, "origin")
        _enum(
            self.current_protection_level,
            AnswerOperatingMode,
            "current_protection_level",
        )
        _enum(
            self.highest_protection_level,
            AnswerOperatingMode,
            "highest_protection_level",
        )
        if not isinstance(self.classification_reference, ClassificationReference):
            raise TypeError("classification_reference must be a ClassificationReference")
        if not isinstance(self.boundary_reference, BoundaryReference):
            raise TypeError("boundary_reference must be a BoundaryReference")
        if not isinstance(self.foundation_reference, AnswerFoundationReference):
            raise TypeError("foundation_reference must be an AnswerFoundationReference")
        _optional_reference(
            self.general_orientation_reference,
            GeneralOrientationReference,
            "general_orientation_reference",
        )
        _optional_reference(
            self.personal_preparation_reference,
            PersonalPreparationReference,
            "personal_preparation_reference",
        )
        _optional_reference(
            self.professional_boundary_reference,
            ProfessionalBoundaryReference,
            "professional_boundary_reference",
        )
        _typed_tuple(self.steps, AnswerReferenceJourneyStep, "steps")
        _enum(self.status, AnswerReferenceJourneyStatus, "status")
        _enum(
            self.completion_reason,
            AnswerReferenceJourneyCompletionReason,
            "completion_reason",
        )
        if self.stop_reason is not None:
            _enum(self.stop_reason, AnswerReferenceJourneyStopReason, "stop_reason")
        _enum(
            self.uncertainty_status,
            ClassificationUncertaintyStatus,
            "uncertainty_status",
        )
        _enum(self.provider_type, OrientationProviderType, "provider_type")
        _enum(
            self.professional_review_status,
            ProfessionalReviewStatus,
            "professional_review_status",
        )
        if self.previous_journey_id is not None:
            _text(self.previous_journey_id, "previous_journey_id")
        _typed_tuple(
            self.capabilities,
            AnswerReferenceJourneyCapability,
            "capabilities",
        )


@dataclass(frozen=True)
class GuardianAnswerReferenceJourneyEnvelope:
    journey: GuardianAnswerReferenceJourney
    current_foundation: GuardianAnswerFoundationIntegration
    general_orientation: Optional[ControlledOrientationEnvelope] = None
    personal_preparation: Optional[PersonalPreparationEnvelope] = None
    professional_boundary: Optional[ProfessionalDecisionBoundaryEnvelope] = None

    def __post_init__(self) -> None:
        if not isinstance(self.journey, GuardianAnswerReferenceJourney):
            raise TypeError("journey must be a GuardianAnswerReferenceJourney")
        if not isinstance(
            self.current_foundation,
            GuardianAnswerFoundationIntegration,
        ):
            raise TypeError(
                "current_foundation must be a GuardianAnswerFoundationIntegration"
            )
        _optional_reference(
            self.general_orientation,
            ControlledOrientationEnvelope,
            "general_orientation",
        )
        _optional_reference(
            self.personal_preparation,
            PersonalPreparationEnvelope,
            "personal_preparation",
        )
        _optional_reference(
            self.professional_boundary,
            ProfessionalDecisionBoundaryEnvelope,
            "professional_boundary",
        )


class AnswerReferenceJourneyValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianAnswerReferenceJourneyContractValidator:
    """Validate only the supplied immutable journey record structure."""

    def validate(
        self,
        journey: GuardianAnswerReferenceJourney,
    ) -> GuardianAnswerReferenceJourney:
        if not isinstance(journey, GuardianAnswerReferenceJourney):
            raise TypeError("journey must be a GuardianAnswerReferenceJourney")
        if not journey.steps:
            _invalid("JOURNEY_STEPS_REQUIRED", "at least one journey step is required")
        step_ids = tuple(step.step_id for step in journey.steps)
        if len(step_ids) != len(set(step_ids)):
            _invalid("DUPLICATE_STEP_ID", "journey step IDs must be unique")
        orders = tuple(step.order for step in journey.steps)
        if orders != tuple(range(1, len(journey.steps) + 1)):
            _invalid("INVALID_STEP_ORDER", "journey step order must be contiguous")
        if journey.previous_journey_id == journey.journey_id:
            _invalid("SELF_PREDECESSOR", "previous journey must not reference itself")
        if not journey.capabilities:
            _invalid(
                "RECORD_CAPABILITY_MISSING",
                "recording the provided journey must remain explicit",
            )
        if set(journey.capabilities) - set(NON_EXECUTING_JOURNEY_CAPABILITIES):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "reference journey cannot possess executing capabilities",
            )
        if journey.status is AnswerReferenceJourneyStatus.COMPLETED:
            if journey.stop_reason is not None:
                _invalid("UNEXPECTED_STOP_REASON", "completed journey cannot have stop reason")
            if (
                journey.completion_reason
                is AnswerReferenceJourneyCompletionReason.CONTROLLED_STOP
            ):
                _invalid(
                    "INVALID_COMPLETION_REASON",
                    "completed journey requires a completed endpoint reason",
                )
        else:
            if journey.stop_reason is None:
                _invalid("STOP_REASON_REQUIRED", "stopped journey requires a stop reason")
            if (
                journey.completion_reason
                is not AnswerReferenceJourneyCompletionReason.CONTROLLED_STOP
            ):
                _invalid(
                    "INVALID_STOP_COMPLETION_REASON",
                    "stopped journey requires controlled stop completion reason",
                )
        return journey


class GuardianAnswerReferenceJourneyValidator:
    """Validate supplied B1/B2/B3 evidence without activating a journey."""

    def validate(
        self,
        envelope: GuardianAnswerReferenceJourneyEnvelope,
    ) -> GuardianAnswerReferenceJourneyEnvelope:
        if not isinstance(envelope, GuardianAnswerReferenceJourneyEnvelope):
            raise TypeError(
                "envelope must be a GuardianAnswerReferenceJourneyEnvelope"
            )
        journey = GuardianAnswerReferenceJourneyContractValidator().validate(
            envelope.journey
        )
        self._validate_nested_stage_identity(envelope)
        stages = self._validated_stages(envelope)
        if not stages:
            _invalid("ANSWER_STAGE_REQUIRED", "at least one answer stage is required")
        self._validate_cross_stage_ids(stages)
        modes = tuple(stage[0] for stage in stages)
        levels = tuple(answer_mode_protection_level(mode) for mode in modes)
        if any(current <= previous for previous, current in zip(levels, levels[1:])):
            _invalid(
                "PROTECTION_DOWNGRADE_OR_DUPLICATE",
                "journey stages must increase protection strictly",
            )

        current_mode, current_foundation, current_artifact = stages[-1]
        if envelope.current_foundation is not current_foundation:
            _invalid(
                "CURRENT_FOUNDATION_IDENTITY_MISMATCH",
                "current foundation must be the exact terminal foundation object",
            )
        GuardianAnswerFoundationIntegrationValidator().validate(
            envelope.current_foundation
        )
        if not envelope.current_foundation.require_complete_source_chain_set:
            _invalid(
                "COMPLETE_SOURCE_CHAIN_SET_REQUIRED",
                "reference journey requires a complete terminal source set",
            )

        self._validate_context(journey, stages)
        self._validate_current_references(journey, envelope.current_foundation)
        self._validate_optional_references(journey, envelope)

        if journey.current_protection_level is not current_mode:
            _invalid(
                "CURRENT_PROTECTION_MISMATCH",
                "current protection must match the terminal stage",
            )
        if journey.highest_protection_level is not most_protective_answer_mode(modes):
            _invalid(
                "HIGHEST_PROTECTION_MISMATCH",
                "highest protection must match the most protective stage",
            )
        current_classification = current_foundation.classification_contract
        if journey.uncertainty_status is not current_classification.uncertainty_status:
            _invalid(
                "UNCERTAINTY_STATUS_MISMATCH",
                "journey uncertainty must match the terminal classification",
            )
        if journey.professional_review_status is not current_artifact.professional_review_status:
            _invalid(
                "PROFESSIONAL_REVIEW_STATUS_MISMATCH",
                "journey review status must match the terminal artifact",
            )
        self._validate_completion(journey, current_mode)
        self._validate_step_protection(journey)
        self._validate_steps(journey, stages)
        return envelope

    @staticmethod
    def _validate_cross_stage_ids(stages) -> None:
        classification_ids = tuple(
            foundation.classification_contract.classification_id
            for _, foundation, _ in stages
        )
        boundary_ids = tuple(
            foundation.boundary_contract.boundary_id
            for _, foundation, _ in stages
        )
        artifact_ids = tuple(_artifact_id(artifact) for _, _, artifact in stages)
        for values, code in (
            (classification_ids, "DUPLICATE_CLASSIFICATION_ID"),
            (boundary_ids, "DUPLICATE_BOUNDARY_ID"),
            (artifact_ids, "DUPLICATE_ANSWER_ARTIFACT_ID"),
        ):
            if len(values) != len(set(values)):
                _invalid(code, "journey stage IDs must be unique")
        source_by_id = {}
        for _, foundation, _ in stages:
            for source in foundation.source_chain_contracts:
                existing = source_by_id.get(source.source_chain_id)
                if existing is not None and existing is not source:
                    _invalid(
                        "SOURCE_CHAIN_OBJECT_IDENTITY_MISMATCH",
                        "reused source-chain IDs must retain object identity",
                    )
                source_by_id[source.source_chain_id] = source

    @staticmethod
    def _validate_nested_stage_identity(envelope) -> None:
        if envelope.personal_preparation is not None:
            nested_b1 = envelope.personal_preparation.general_orientation
            if nested_b1 is not envelope.general_orientation:
                _invalid(
                    "B1_OBJECT_IDENTITY_MISMATCH",
                    "B2 must retain the exact journey B1 envelope when present",
                )
        if envelope.professional_boundary is not None:
            nested_b1 = envelope.professional_boundary.general_orientation
            nested_b2 = envelope.professional_boundary.personal_preparation
            if nested_b1 is not envelope.general_orientation:
                _invalid(
                    "B3_B1_OBJECT_IDENTITY_MISMATCH",
                    "B3 must retain the exact journey B1 envelope when present",
                )
            if nested_b2 is not envelope.personal_preparation:
                _invalid(
                    "B3_B2_OBJECT_IDENTITY_MISMATCH",
                    "B3 must retain the exact journey B2 envelope when present",
                )

    @staticmethod
    def _validated_stages(
        envelope: GuardianAnswerReferenceJourneyEnvelope,
    ) -> Tuple[Tuple[AnswerOperatingMode, GuardianAnswerFoundationIntegration, object], ...]:
        stages = []
        if envelope.general_orientation is not None:
            ControlledOrientationEnvelopeValidator().validate(
                envelope.general_orientation
            )
            stages.append(
                (
                    AnswerOperatingMode.B1_GENERAL_ORIENTATION,
                    envelope.general_orientation.foundation,
                    envelope.general_orientation.orientation,
                )
            )
        if envelope.personal_preparation is not None:
            PersonalPreparationEnvelopeValidator().validate(
                envelope.personal_preparation
            )
            stages.append(
                (
                    AnswerOperatingMode.B2_PERSONAL_PREPARATION,
                    envelope.personal_preparation.foundation,
                    envelope.personal_preparation.preparation,
                )
            )
        if envelope.professional_boundary is not None:
            ProfessionalDecisionBoundaryEnvelopeValidator().validate(
                envelope.professional_boundary
            )
            stages.append(
                (
                    AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
                    envelope.professional_boundary.foundation,
                    envelope.professional_boundary.professional_boundary,
                )
            )
        return tuple(stages)

    @staticmethod
    def _validate_context(journey, stages) -> None:
        for _, foundation, _ in stages:
            classification = foundation.classification_contract
            if (
                classification.conversation_context_reference
                != journey.conversation_context_reference
            ):
                _invalid(
                    "CONVERSATION_CONTEXT_MISMATCH",
                    "all classifications must share the journey context",
                )
            for source in foundation.source_chain_contracts:
                if (
                    source.answer_context_reference.conversation_context_id
                    != journey.conversation_context_reference
                ):
                    _invalid(
                        "SOURCE_CONTEXT_MISMATCH",
                        "all source chains must share the journey context",
                    )

    @staticmethod
    def _validate_current_references(journey, foundation) -> None:
        if (
            journey.classification_reference.classification_id
            != foundation.classification_contract.classification_id
        ):
            _invalid(
                "CLASSIFICATION_REFERENCE_MISMATCH",
                "journey classification reference must match current foundation",
            )
        if journey.boundary_reference.boundary_id != foundation.boundary_contract.boundary_id:
            _invalid(
                "BOUNDARY_REFERENCE_MISMATCH",
                "journey boundary reference must match current foundation",
            )
        if journey.foundation_reference != answer_foundation_reference(foundation):
            _invalid(
                "FOUNDATION_REFERENCE_MISMATCH",
                "journey foundation reference must match current foundation",
            )

    @staticmethod
    def _validate_optional_references(journey, envelope) -> None:
        pairs = (
            (
                journey.general_orientation_reference,
                envelope.general_orientation,
                lambda value: value.orientation.orientation_id,
                "GENERAL_ORIENTATION",
            ),
            (
                journey.personal_preparation_reference,
                envelope.personal_preparation,
                lambda value: value.preparation.preparation_id,
                "PERSONAL_PREPARATION",
            ),
            (
                journey.professional_boundary_reference,
                envelope.professional_boundary,
                lambda value: value.professional_boundary.professional_boundary_id,
                "PROFESSIONAL_BOUNDARY",
            ),
        )
        for reference, value, identifier, label in pairs:
            if reference is None and value is not None:
                _invalid("UNREFERENCED_{}".format(label), "supplied stage is not referenced")
            if reference is not None and value is None:
                _invalid("{}_REQUIRED".format(label), "referenced stage is missing")
            if reference is not None:
                reference_id = _stage_reference_id(reference)
                if reference_id != identifier(value):
                    _invalid(
                        "{}_REFERENCE_MISMATCH".format(label),
                        "stage reference does not match supplied artifact",
                    )

    @staticmethod
    def _validate_completion(journey, current_mode) -> None:
        expected = {
            AnswerOperatingMode.B1_GENERAL_ORIENTATION: (
                AnswerReferenceJourneyCompletionReason.GENERAL_ORIENTATION_COMPLETE
            ),
            AnswerOperatingMode.B2_PERSONAL_PREPARATION: (
                AnswerReferenceJourneyCompletionReason.PERSONAL_PREPARATION_COMPLETE
            ),
            AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: (
                AnswerReferenceJourneyCompletionReason.PROFESSIONAL_BOUNDARY_COMPLETE
            ),
        }[current_mode]
        if (
            journey.status is AnswerReferenceJourneyStatus.COMPLETED
            and journey.completion_reason is not expected
        ):
            _invalid(
                "COMPLETION_REASON_MISMATCH",
                "completion reason must match the terminal stage",
            )

    @staticmethod
    def _validate_step_protection(journey) -> None:
        levels = tuple(
            answer_mode_protection_level(step.protection_level)
            for step in journey.steps
        )
        if any(current < previous for previous, current in zip(levels, levels[1:])):
            _invalid(
                "STEP_PROTECTION_DOWNGRADE",
                "journey steps must never lower protection",
            )

    @staticmethod
    def _validate_steps(journey, stages) -> None:
        expected = []
        for mode, foundation, artifact in stages:
            source_ids = tuple(
                source.source_chain_id for source in foundation.source_chain_contracts
            )
            expected.extend(
                (
                    (
                        AnswerReferenceJourneyStepType.CLASSIFICATION_PROVIDED,
                        (foundation.classification_contract.classification_id,),
                        mode,
                        AnswerReferenceJourneyStepResult.PROVIDED,
                    ),
                    (
                        AnswerReferenceJourneyStepType.ANSWER_BOUNDARY_VALIDATED,
                        (foundation.boundary_contract.boundary_id,),
                        mode,
                        AnswerReferenceJourneyStepResult.VALIDATED,
                    ),
                    (
                        AnswerReferenceJourneyStepType.SOURCE_CHAINS_BOUND,
                        source_ids,
                        mode,
                        AnswerReferenceJourneyStepResult.BOUND,
                    ),
                    (
                        AnswerReferenceJourneyStepType.ANSWER_FOUNDATION_VALIDATED,
                        (
                            foundation.classification_contract.classification_id,
                            foundation.boundary_contract.boundary_id,
                        ),
                        mode,
                        AnswerReferenceJourneyStepResult.VALIDATED,
                    ),
                    (
                        _artifact_step_type(mode),
                        (_artifact_id(artifact),),
                        mode,
                        AnswerReferenceJourneyStepResult.PROVIDED,
                    ),
                )
            )
        final_type = (
            AnswerReferenceJourneyStepType.JOURNEY_COMPLETED
            if journey.status is AnswerReferenceJourneyStatus.COMPLETED
            else AnswerReferenceJourneyStepType.JOURNEY_STOPPED
        )
        final_result = (
            AnswerReferenceJourneyStepResult.COMPLETED
            if journey.status is AnswerReferenceJourneyStatus.COMPLETED
            else AnswerReferenceJourneyStepResult.STOPPED
        )
        expected.append(
            (
                final_type,
                (journey.journey_id,),
                journey.current_protection_level,
                final_result,
            )
        )
        actual = tuple(
            (
                step.step_type,
                step.referenced_contract_ids,
                step.protection_level,
                step.result_status,
            )
            for step in journey.steps
        )
        if actual != tuple(expected):
            _invalid(
                "INVALID_STEP_SEQUENCE",
                "journey steps must exactly document the supplied stages",
            )
        for step in journey.steps[:-1]:
            if step.stop_reason is not None:
                _invalid(
                    "EARLY_STOP_REASON",
                    "only the final stopped step may contain a stop reason",
                )
        final_step = journey.steps[-1]
        if journey.status is AnswerReferenceJourneyStatus.STOPPED:
            if final_step.stop_reason is not journey.stop_reason:
                _invalid(
                    "STEP_STOP_REASON_MISMATCH",
                    "final step and journey stop reasons must match",
                )
        elif final_step.stop_reason is not None:
            _invalid(
                "UNEXPECTED_STEP_STOP_REASON",
                "completed journey final step cannot contain a stop reason",
            )


@dataclass(frozen=True)
class GuardianAnswerExperience:
    experience_id: str
    journey: GuardianAnswerReferenceJourney
    current_protection_level: AnswerOperatingMode
    highest_protection_level: AnswerOperatingMode
    journey_status: AnswerReferenceJourneyStatus
    general_orientation: Optional[B1OrientationContract]
    personal_preparation: Optional[B2PersonalPreparationContract]
    professional_boundary: Optional[B3ProfessionalDecisionBoundaryContract]
    known_facts: Tuple[KnownFactEntry, ...]
    open_questions: Tuple[OpenQuestionEntry, ...]
    options_for_consideration: Tuple[OptionForConsiderationEntry, ...]
    uncertainties: Tuple[UncertaintyEntry, ...]
    preparation_review_topics: Tuple[ProfessionalReviewTopicEntry, ...]
    boundary_review_topics: Tuple[ProfessionalBoundaryReviewTopic, ...]
    answer_boundaries: Tuple[AnswerBoundaryContract, ...]
    source_chain_contracts: Tuple[GuardianSourceChainContract, ...]
    limitations: Tuple[str, ...]
    urgency_status: Optional[UrgencyStatus]
    urgent_help_notice: Optional[str]
    professional_review_status: ProfessionalReviewStatus
    provider_type: OrientationProviderType
    provider_reference: str
    provenance: str
    available_actions: Tuple[GuardianAnswerExperienceAction, ...]

    def __post_init__(self) -> None:
        _text(self.experience_id, "experience_id")
        if not isinstance(self.journey, GuardianAnswerReferenceJourney):
            raise TypeError("journey must be a GuardianAnswerReferenceJourney")
        _enum(
            self.current_protection_level,
            AnswerOperatingMode,
            "current_protection_level",
        )
        _enum(
            self.highest_protection_level,
            AnswerOperatingMode,
            "highest_protection_level",
        )
        _enum(self.journey_status, AnswerReferenceJourneyStatus, "journey_status")
        _optional_reference(
            self.general_orientation,
            B1OrientationContract,
            "general_orientation",
        )
        _optional_reference(
            self.personal_preparation,
            B2PersonalPreparationContract,
            "personal_preparation",
        )
        _optional_reference(
            self.professional_boundary,
            B3ProfessionalDecisionBoundaryContract,
            "professional_boundary",
        )
        for values, item_type, name in (
            (self.known_facts, KnownFactEntry, "known_facts"),
            (self.open_questions, OpenQuestionEntry, "open_questions"),
            (
                self.options_for_consideration,
                OptionForConsiderationEntry,
                "options_for_consideration",
            ),
            (self.uncertainties, UncertaintyEntry, "uncertainties"),
            (
                self.preparation_review_topics,
                ProfessionalReviewTopicEntry,
                "preparation_review_topics",
            ),
            (
                self.boundary_review_topics,
                ProfessionalBoundaryReviewTopic,
                "boundary_review_topics",
            ),
            (self.answer_boundaries, AnswerBoundaryContract, "answer_boundaries"),
            (
                self.source_chain_contracts,
                GuardianSourceChainContract,
                "source_chain_contracts",
            ),
        ):
            _typed_tuple(values, item_type, name)
        if not isinstance(self.limitations, tuple):
            raise TypeError("limitations must be a tuple")
        for value in self.limitations:
            _text(value, "limitations")
        if self.urgency_status is not None:
            _enum(self.urgency_status, UrgencyStatus, "urgency_status")
        if self.urgent_help_notice is not None:
            _text(self.urgent_help_notice, "urgent_help_notice")
        _enum(
            self.professional_review_status,
            ProfessionalReviewStatus,
            "professional_review_status",
        )
        _enum(self.provider_type, OrientationProviderType, "provider_type")
        _text(self.provider_reference, "provider_reference")
        _text(self.provenance, "provenance")
        _typed_tuple(
            self.available_actions,
            GuardianAnswerExperienceAction,
            "available_actions",
        )
        if len(self.available_actions) != len(set(self.available_actions)):
            raise ValueError("available_actions must not contain duplicates")


class GuardianAnswerExperienceProjector:
    """Project references and supplied content without rewriting any value."""

    def project(
        self,
        envelope: GuardianAnswerReferenceJourneyEnvelope,
        *,
        experience_id: str,
    ) -> GuardianAnswerExperience:
        _text(experience_id, "experience_id")
        GuardianAnswerReferenceJourneyValidator().validate(envelope)
        b1 = (
            envelope.general_orientation.orientation
            if envelope.general_orientation is not None
            else None
        )
        b2 = (
            envelope.personal_preparation.preparation
            if envelope.personal_preparation is not None
            else None
        )
        b3 = (
            envelope.professional_boundary.professional_boundary
            if envelope.professional_boundary is not None
            else None
        )
        sources = _unique_sources(envelope)
        actions = []
        if b1 is not None:
            actions.append(GuardianAnswerExperienceAction.VIEW_GENERAL_ORIENTATION)
        if b2 is not None:
            actions.append(GuardianAnswerExperienceAction.VIEW_PERSONAL_PREPARATION)
        if b3 is not None:
            actions.extend(
                (
                    GuardianAnswerExperienceAction.VIEW_PROFESSIONAL_BOUNDARY,
                    GuardianAnswerExperienceAction.ACKNOWLEDGE_BOUNDARY,
                )
            )
        actions.append(GuardianAnswerExperienceAction.VIEW_SOURCES)
        if b2 is not None and b2.uncertainties:
            actions.append(GuardianAnswerExperienceAction.VIEW_UNCERTAINTIES)
        if (b2 is not None and b2.professional_review_topics) or (
            b3 is not None and b3.professional_review_topics
        ):
            actions.append(
                GuardianAnswerExperienceAction.VIEW_PROFESSIONAL_REVIEW_TOPICS
            )
        limitations = tuple(
            value
            for value in (
                b1.limitations if b1 is not None else None,
                b3.professional_boundary if b3 is not None else None,
            )
            if value is not None
        )
        return GuardianAnswerExperience(
            experience_id=experience_id,
            journey=envelope.journey,
            current_protection_level=envelope.journey.current_protection_level,
            highest_protection_level=envelope.journey.highest_protection_level,
            journey_status=envelope.journey.status,
            general_orientation=b1,
            personal_preparation=b2,
            professional_boundary=b3,
            known_facts=b2.known_facts if b2 is not None else (),
            open_questions=b2.open_questions if b2 is not None else (),
            options_for_consideration=(
                b2.options_for_consideration if b2 is not None else ()
            ),
            uncertainties=b2.uncertainties if b2 is not None else (),
            preparation_review_topics=(
                b2.professional_review_topics if b2 is not None else ()
            ),
            boundary_review_topics=(
                b3.professional_review_topics if b3 is not None else ()
            ),
            answer_boundaries=tuple(
                item.foundation.boundary_contract
                for item in (
                    envelope.general_orientation,
                    envelope.personal_preparation,
                    envelope.professional_boundary,
                )
                if item is not None
            ),
            source_chain_contracts=sources,
            limitations=limitations,
            urgency_status=b3.urgency_status if b3 is not None else None,
            urgent_help_notice=b3.urgent_help_notice if b3 is not None else None,
            professional_review_status=envelope.journey.professional_review_status,
            provider_type=envelope.journey.provider_type,
            provider_reference=envelope.journey.provider_reference,
            provenance=envelope.journey.provenance,
            available_actions=tuple(actions),
        )


def _unique_sources(
    envelope: GuardianAnswerReferenceJourneyEnvelope,
) -> Tuple[GuardianSourceChainContract, ...]:
    result = []
    by_id = {}
    foundations = []
    for item in (
        envelope.general_orientation,
        envelope.personal_preparation,
        envelope.professional_boundary,
    ):
        if item is not None:
            foundations.append(item.foundation)
    for foundation in foundations:
        for source in foundation.source_chain_contracts:
            existing = by_id.get(source.source_chain_id)
            if existing is not None and existing != source:
                _invalid(
                    "DUPLICATE_SOURCE_ID_WITH_DIFFERENT_CONTENT",
                    "same source-chain ID cannot carry different content",
                )
            if existing is None:
                by_id[source.source_chain_id] = source
                result.append(source)
    return tuple(result)


def _artifact_step_type(mode: AnswerOperatingMode) -> AnswerReferenceJourneyStepType:
    return {
        AnswerOperatingMode.B1_GENERAL_ORIENTATION: (
            AnswerReferenceJourneyStepType.B1_ORIENTATION_PROVIDED
        ),
        AnswerOperatingMode.B2_PERSONAL_PREPARATION: (
            AnswerReferenceJourneyStepType.B2_PREPARATION_PROVIDED
        ),
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: (
            AnswerReferenceJourneyStepType.B3_PROFESSIONAL_BOUNDARY_PROVIDED
        ),
    }[mode]


def _artifact_id(artifact: object) -> str:
    if isinstance(artifact, B1OrientationContract):
        return artifact.orientation_id
    if isinstance(artifact, B2PersonalPreparationContract):
        return artifact.preparation_id
    if isinstance(artifact, B3ProfessionalDecisionBoundaryContract):
        return artifact.professional_boundary_id
    raise TypeError("unsupported answer artifact")


def _stage_reference_id(reference: object) -> str:
    if isinstance(reference, GeneralOrientationReference):
        return reference.orientation_id
    if isinstance(reference, PersonalPreparationReference):
        return reference.preparation_id
    if isinstance(reference, ProfessionalBoundaryReference):
        return reference.professional_boundary_id
    raise TypeError("unsupported answer-stage reference")


def _invalid(code: str, message: str) -> None:
    raise AnswerReferenceJourneyValidationError(code, message)


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("{} must be non-empty trimmed text".format(name))
    if "\x00" in value:
        raise ValueError("{} must not contain null bytes".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value: object, name: str) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("{} must be a non-empty tuple".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_tuple(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid items".format(name))


def _optional_reference(value: object, item_type: type, name: str) -> None:
    if value is not None and not isinstance(value, item_type):
        raise TypeError("{} is invalid".format(name))
