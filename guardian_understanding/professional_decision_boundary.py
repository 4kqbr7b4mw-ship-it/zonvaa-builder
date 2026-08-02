"""Immutable evidence for an already provided B3 professional boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.answer_boundary import (
    AnswerBoundaryContract,
    AnswerOperatingMode,
    ClassificationReference,
    GuardianAnswerBoundaryValidator,
    answer_mode_protection_level,
)
from guardian_understanding.answer_foundation import (
    GuardianAnswerFoundationIntegration,
    GuardianAnswerFoundationIntegrationValidator,
)
from guardian_understanding.classification import (
    GuardianClassificationContract,
    GuardianClassificationValidator,
)
from guardian_understanding.controlled_orientation import (
    BoundaryReference,
    ControlledOrientationEnvelope,
    ControlledOrientationEnvelopeValidator,
    OrientationProviderType,
    ProfessionalReviewStatus,
)
from guardian_understanding.personal_preparation import (
    GeneralOrientationReference,
    PersonalPreparationEnvelope,
    PersonalPreparationEnvelopeValidator,
)
from guardian_understanding.source_chain import SourceChainReference


class NonConfirmationCode(str, Enum):
    GENERAL_NON_CONFIRMATION = "GENERAL_NON_CONFIRMATION"
    LEGAL_CASE_DECISION_NOT_CONFIRMABLE = "LEGAL_CASE_DECISION_NOT_CONFIRMABLE"
    TAX_CASE_DECISION_NOT_CONFIRMABLE = "TAX_CASE_DECISION_NOT_CONFIRMABLE"
    FINANCIAL_CASE_DECISION_NOT_CONFIRMABLE = "FINANCIAL_CASE_DECISION_NOT_CONFIRMABLE"
    MEDICAL_CASE_DECISION_NOT_CONFIRMABLE = "MEDICAL_CASE_DECISION_NOT_CONFIRMABLE"
    OTHER_PROFESSIONAL_CASE_DECISION_NOT_CONFIRMABLE = (
        "OTHER_PROFESSIONAL_CASE_DECISION_NOT_CONFIRMABLE"
    )


class UrgencyStatus(str, Enum):
    NOT_DECLARED_URGENT = "NOT_DECLARED_URGENT"
    URGENT_PROFESSIONAL_REVIEW = "URGENT_PROFESSIONAL_REVIEW"
    IMMEDIATE_HELP_REQUIRED = "IMMEDIATE_HELP_REQUIRED"


class ProfessionalBoundaryCapability(str, Enum):
    RECORD_PROVIDED_BOUNDARY = "RECORD_PROVIDED_BOUNDARY"
    MAKE_PROFESSIONAL_DECISION = "MAKE_PROFESSIONAL_DECISION"
    INTERPRET_NATURAL_LANGUAGE = "INTERPRET_NATURAL_LANGUAGE"
    DETECT_DANGER = "DETECT_DANGER"
    TRIAGE = "TRIAGE"
    SELECT_PROFESSIONAL = "SELECT_PROFESSIONAL"
    ARRANGE_APPOINTMENT = "ARRANGE_APPOINTMENT"
    CONTACT_PROVIDER = "CONTACT_PROVIDER"
    TRIGGER_EMERGENCY_CALL = "TRIGGER_EMERGENCY_CALL"
    DETERMINE_LOCATION = "DETERMINE_LOCATION"
    GENERATE_CONTENT = "GENERATE_CONTENT"
    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    ACTIVATE_ANSWER_MODE = "ACTIVATE_ANSWER_MODE"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    PERSIST_BOUNDARY = "PERSIST_BOUNDARY"


NON_EXECUTING_PROFESSIONAL_BOUNDARY_CAPABILITIES = (
    ProfessionalBoundaryCapability.RECORD_PROVIDED_BOUNDARY,
)


@dataclass(frozen=True)
class PersonalPreparationReference:
    preparation_id: str

    def __post_init__(self) -> None:
        _text(self.preparation_id, "preparation_id")


@dataclass(frozen=True)
class ProfessionalBoundaryReviewTopic:
    topic_id: str
    title: str
    description: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _text(self.topic_id, "topic_id")
        _text(self.title, "title")
        _text(self.description, "description")
        _typed_tuple(
            self.source_chain_references,
            SourceChainReference,
            "source_chain_references",
        )


@dataclass(frozen=True)
class B3ProfessionalDecisionBoundaryContract:
    professional_boundary_id: str
    classification_reference: ClassificationReference
    boundary_reference: BoundaryReference
    source_chain_references: Tuple[SourceChainReference, ...]
    general_orientation_reference: Optional[GeneralOrientationReference]
    personal_preparation_reference: Optional[PersonalPreparationReference]
    acknowledgement: str
    non_confirmation_code: NonConfirmationCode
    non_confirmation_text: str
    professional_boundary: str
    safe_general_orientation: str
    preparation_guidance: str
    professional_review_topics: Tuple[ProfessionalBoundaryReviewTopic, ...]
    urgency_status: UrgencyStatus
    urgent_help_notice: Optional[str]
    provider_type: OrientationProviderType
    provider_reference: str
    professional_review_status: ProfessionalReviewStatus
    professional_review_reference: Optional[str]
    created_at: datetime
    capabilities: Tuple[ProfessionalBoundaryCapability, ...] = (
        ProfessionalBoundaryCapability.RECORD_PROVIDED_BOUNDARY,
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.professional_boundary_id, "professional_boundary_id"),
            (self.acknowledgement, "acknowledgement"),
            (self.non_confirmation_text, "non_confirmation_text"),
            (self.professional_boundary, "professional_boundary"),
            (self.safe_general_orientation, "safe_general_orientation"),
            (self.preparation_guidance, "preparation_guidance"),
            (self.provider_reference, "provider_reference"),
        ):
            _text(value, name)
        if not isinstance(self.classification_reference, ClassificationReference):
            raise TypeError(
                "classification_reference must be a ClassificationReference"
            )
        if not isinstance(self.boundary_reference, BoundaryReference):
            raise TypeError("boundary_reference must be a BoundaryReference")
        _typed_tuple(
            self.source_chain_references,
            SourceChainReference,
            "source_chain_references",
        )
        if self.general_orientation_reference is not None and not isinstance(
            self.general_orientation_reference,
            GeneralOrientationReference,
        ):
            raise TypeError(
                "general_orientation_reference must be a GeneralOrientationReference"
            )
        if self.personal_preparation_reference is not None and not isinstance(
            self.personal_preparation_reference,
            PersonalPreparationReference,
        ):
            raise TypeError(
                "personal_preparation_reference must be a PersonalPreparationReference"
            )
        _enum(self.non_confirmation_code, NonConfirmationCode, "non_confirmation_code")
        _typed_tuple(
            self.professional_review_topics,
            ProfessionalBoundaryReviewTopic,
            "professional_review_topics",
        )
        _enum(self.urgency_status, UrgencyStatus, "urgency_status")
        if self.urgent_help_notice is not None:
            _text(self.urgent_help_notice, "urgent_help_notice")
        _enum(self.provider_type, OrientationProviderType, "provider_type")
        _enum(
            self.professional_review_status,
            ProfessionalReviewStatus,
            "professional_review_status",
        )
        if self.professional_review_reference is not None:
            _text(
                self.professional_review_reference,
                "professional_review_reference",
            )
        _aware_datetime(self.created_at, "created_at")
        _typed_tuple(
            self.capabilities,
            ProfessionalBoundaryCapability,
            "capabilities",
        )


class ProfessionalDecisionBoundaryValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B3ProfessionalDecisionBoundaryContractValidator:
    """Validate supplied B3 structure without interpreting its text."""

    def validate(
        self,
        contract: B3ProfessionalDecisionBoundaryContract,
    ) -> B3ProfessionalDecisionBoundaryContract:
        if not isinstance(contract, B3ProfessionalDecisionBoundaryContract):
            raise TypeError(
                "contract must be a B3ProfessionalDecisionBoundaryContract"
            )
        source_ids = _unique_source_ids(
            contract.source_chain_references,
            required=True,
            duplicate_code="DUPLICATE_SOURCE_CHAIN_REFERENCE",
        )
        if not contract.professional_review_topics:
            _invalid(
                "PROFESSIONAL_REVIEW_TOPIC_REQUIRED",
                "at least one professional review topic is required",
            )
        topic_ids = tuple(topic.topic_id for topic in contract.professional_review_topics)
        if len(topic_ids) != len(set(topic_ids)):
            _invalid("DUPLICATE_REVIEW_TOPIC_ID", "review topic IDs must be unique")
        for topic in contract.professional_review_topics:
            topic_source_ids = _unique_source_ids(
                topic.source_chain_references,
                required=False,
                duplicate_code="DUPLICATE_TOPIC_SOURCE_CHAIN_REFERENCE",
            )
            if not set(topic_source_ids) <= set(source_ids):
                _invalid(
                    "TOPIC_SOURCE_CHAIN_NOT_DECLARED",
                    "review topic source chains must belong to the B3 contract",
                )

        if (
            contract.urgency_status is UrgencyStatus.IMMEDIATE_HELP_REQUIRED
            and contract.urgent_help_notice is None
        ):
            _invalid(
                "URGENT_HELP_NOTICE_REQUIRED",
                "immediate help status requires a supplied help notice",
            )

        review_completed = (
            contract.professional_review_status
            is ProfessionalReviewStatus.COMPLETED_DECLARED
        )
        if review_completed and contract.professional_review_reference is None:
            _invalid(
                "PROFESSIONAL_REVIEW_REFERENCE_REQUIRED",
                "a declared completed review requires its reference",
            )
        if not review_completed and contract.professional_review_reference is not None:
            _invalid(
                "UNEXPECTED_PROFESSIONAL_REVIEW_REFERENCE",
                "only a declared completed review may carry a review reference",
            )
        if not contract.capabilities:
            _invalid(
                "RECORD_CAPABILITY_MISSING",
                "recording the supplied B3 boundary must remain explicit",
            )
        if set(contract.capabilities) - set(
            NON_EXECUTING_PROFESSIONAL_BOUNDARY_CAPABILITIES
        ):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "professional boundary cannot possess executing capabilities",
            )
        return contract


class B3ProfessionalDecisionBoundarySafetyValidator:
    """Require exact supplied B3 classification, boundary and decision flag."""

    def validate(
        self,
        professional_boundary: B3ProfessionalDecisionBoundaryContract,
        classification: GuardianClassificationContract,
        boundary: AnswerBoundaryContract,
    ) -> B3ProfessionalDecisionBoundaryContract:
        professional_boundary = B3ProfessionalDecisionBoundaryContractValidator().validate(
            professional_boundary
        )
        classification = GuardianClassificationValidator().validate(classification)
        boundary = GuardianAnswerBoundaryValidator().validate(boundary)
        if (
            professional_boundary.classification_reference.classification_id
            != classification.classification_id
        ):
            _invalid(
                "CLASSIFICATION_REFERENCE_MISMATCH",
                "B3 classification reference does not match",
            )
        if professional_boundary.boundary_reference.boundary_id != boundary.boundary_id:
            _invalid("BOUNDARY_REFERENCE_MISMATCH", "B3 boundary reference does not match")
        b3_level = answer_mode_protection_level(
            AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        )
        if answer_mode_protection_level(classification.effective_level) != b3_level:
            _invalid("CLASSIFICATION_NOT_B3", "B3 classification is required")
        if answer_mode_protection_level(boundary.effective_mode) != b3_level:
            _invalid("BOUNDARY_NOT_B3", "B3 boundary is required")
        if not classification.professional_decision_requested:
            _invalid(
                "PROFESSIONAL_DECISION_NOT_REQUESTED",
                "B3 requires a supplied professional decision request",
            )
        return professional_boundary


@dataclass(frozen=True)
class ProfessionalDecisionBoundaryEnvelope:
    foundation: GuardianAnswerFoundationIntegration
    professional_boundary: B3ProfessionalDecisionBoundaryContract
    general_orientation: Optional[ControlledOrientationEnvelope] = None
    personal_preparation: Optional[PersonalPreparationEnvelope] = None


class ProfessionalDecisionBoundaryEnvelopeValidator:
    """Validate complete B3 evidence without producing or acting on content."""

    def validate(
        self,
        envelope: ProfessionalDecisionBoundaryEnvelope,
    ) -> ProfessionalDecisionBoundaryEnvelope:
        if not isinstance(envelope, ProfessionalDecisionBoundaryEnvelope):
            raise TypeError(
                "envelope must be a ProfessionalDecisionBoundaryEnvelope"
            )
        foundation = GuardianAnswerFoundationIntegrationValidator().validate(
            envelope.foundation
        )
        if not foundation.require_complete_source_chain_set:
            _invalid(
                "COMPLETE_SOURCE_CHAIN_SET_REQUIRED",
                "B3 requires complete source-chain validation",
            )
        B3ProfessionalDecisionBoundarySafetyValidator().validate(
            envelope.professional_boundary,
            foundation.classification_contract,
            foundation.boundary_contract,
        )
        boundary_classification = foundation.boundary_contract.classification_reference
        if (
            boundary_classification is None
            or boundary_classification.classification_id
            != foundation.classification_contract.classification_id
        ):
            _invalid(
                "BOUNDARY_CLASSIFICATION_REFERENCE_REQUIRED",
                "B3 boundary must reference the integrated classification",
            )
        contract_source_ids = tuple(
            reference.source_chain_id
            for reference in envelope.professional_boundary.source_chain_references
        )
        classification_source_ids = tuple(
            reference.source_chain_id
            for reference in foundation.classification_contract.source_chain_references
        )
        supplied_source_ids = tuple(
            contract.source_chain_id for contract in foundation.source_chain_contracts
        )
        if contract_source_ids != classification_source_ids:
            _invalid(
                "CLASSIFICATION_SOURCE_CHAIN_SET_MISMATCH",
                "B3 and classification source-chain references must match exactly",
            )
        if contract_source_ids != supplied_source_ids:
            _invalid(
                "SUPPLIED_SOURCE_CHAIN_SET_MISMATCH",
                "B3 references and supplied source chains must match exactly",
            )
        self._validate_optional_references(envelope)
        return envelope

    @staticmethod
    def _validate_optional_references(
        envelope: ProfessionalDecisionBoundaryEnvelope,
    ) -> None:
        contract = envelope.professional_boundary
        if contract.general_orientation_reference is None:
            if envelope.general_orientation is not None:
                _invalid(
                    "UNREFERENCED_GENERAL_ORIENTATION",
                    "unreferenced B1 orientation cannot be supplied",
                )
        else:
            if envelope.general_orientation is None:
                _invalid("GENERAL_ORIENTATION_REQUIRED", "referenced B1 is missing")
            ControlledOrientationEnvelopeValidator().validate(envelope.general_orientation)
            if (
                envelope.general_orientation.orientation.orientation_id
                != contract.general_orientation_reference.orientation_id
            ):
                _invalid(
                    "GENERAL_ORIENTATION_REFERENCE_MISMATCH",
                    "supplied B1 orientation ID does not match",
                )
        if contract.personal_preparation_reference is None:
            if envelope.personal_preparation is not None:
                _invalid(
                    "UNREFERENCED_PERSONAL_PREPARATION",
                    "unreferenced B2 preparation cannot be supplied",
                )
        else:
            if envelope.personal_preparation is None:
                _invalid("PERSONAL_PREPARATION_REQUIRED", "referenced B2 is missing")
            PersonalPreparationEnvelopeValidator().validate(envelope.personal_preparation)
            if (
                envelope.personal_preparation.preparation.preparation_id
                != contract.personal_preparation_reference.preparation_id
            ):
                _invalid(
                    "PERSONAL_PREPARATION_REFERENCE_MISMATCH",
                    "supplied B2 preparation ID does not match",
                )


def _unique_source_ids(
    references: Tuple[SourceChainReference, ...],
    *,
    required: bool,
    duplicate_code: str,
) -> Tuple[str, ...]:
    if required and not references:
        _invalid(
            "SOURCE_CHAIN_REFERENCE_REQUIRED",
            "at least one source-chain reference is required",
        )
    ids = tuple(reference.source_chain_id for reference in references)
    if len(ids) != len(set(ids)):
        _invalid(duplicate_code, "source-chain references must be unique")
    return ids


def _invalid(code: str, message: str) -> None:
    raise ProfessionalDecisionBoundaryValidationError(code, message)


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("{} must be non-empty trimmed text".format(name))
    if "\x00" in value:
        raise ValueError("{} must not contain null bytes".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _aware_datetime(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _typed_tuple(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid items".format(name))
