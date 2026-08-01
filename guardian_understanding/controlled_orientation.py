"""Immutable evidence for already provided, controlled B1 orientation."""

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
from guardian_understanding.source_chain import SourceChainReference


class OrientationProviderType(str, Enum):
    HUMAN_OPERATOR = "HUMAN_OPERATOR"
    TYPED_INPUT_ADAPTER = "TYPED_INPUT_ADAPTER"
    CONTENT_MODEL = "CONTENT_MODEL"


class ProfessionalReviewStatus(str, Enum):
    NOT_DECLARED = "NOT_DECLARED"
    COMPLETED_DECLARED = "COMPLETED_DECLARED"
    REQUIRED = "REQUIRED"


class ControlledOrientationCapability(str, Enum):
    RECORD_PROVIDED_ORIENTATION = "RECORD_PROVIDED_ORIENTATION"
    GENERATE_CONTENT = "GENERATE_CONTENT"
    INTERPRET_NATURAL_LANGUAGE = "INTERPRET_NATURAL_LANGUAGE"
    CLASSIFY_REQUEST = "CLASSIFY_REQUEST"
    ACTIVATE_ANSWER_MODE = "ACTIVATE_ANSWER_MODE"
    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    EVALUATE_SOURCE = "EVALUATE_SOURCE"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    PERSIST_ORIENTATION = "PERSIST_ORIENTATION"


NON_EXECUTING_ORIENTATION_CAPABILITIES = (
    ControlledOrientationCapability.RECORD_PROVIDED_ORIENTATION,
)


@dataclass(frozen=True)
class BoundaryReference:
    boundary_id: str

    def __post_init__(self) -> None:
        _text(self.boundary_id, "boundary_id")


@dataclass(frozen=True)
class B1OrientationContract:
    """Record already supplied B1 text without interpreting or changing it."""

    orientation_id: str
    classification_reference: ClassificationReference
    boundary_reference: BoundaryReference
    source_chain_references: Tuple[SourceChainReference, ...]
    orientation_summary: str
    general_information: str
    uncertainty_notice: str
    source_notice: str
    limitations: str
    created_at: datetime
    provider_type: OrientationProviderType
    provider_reference: str
    professional_review_status: ProfessionalReviewStatus
    professional_review_reference: Optional[str]
    capabilities: Tuple[ControlledOrientationCapability, ...] = (
        ControlledOrientationCapability.RECORD_PROVIDED_ORIENTATION,
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.orientation_id, "orientation_id"),
            (self.orientation_summary, "orientation_summary"),
            (self.general_information, "general_information"),
            (self.uncertainty_notice, "uncertainty_notice"),
            (self.source_notice, "source_notice"),
            (self.limitations, "limitations"),
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
        _aware_datetime(self.created_at, "created_at")
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
        _typed_tuple(
            self.capabilities,
            ControlledOrientationCapability,
            "capabilities",
        )


class ControlledOrientationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B1OrientationContractValidator:
    """Validate typed structure only; never inspect the supplied text."""

    def validate(self, contract: B1OrientationContract) -> B1OrientationContract:
        if not isinstance(contract, B1OrientationContract):
            raise TypeError("contract must be a B1OrientationContract")

        if not contract.source_chain_references:
            _invalid(
                "SOURCE_CHAIN_REFERENCE_REQUIRED",
                "at least one source-chain reference is required",
            )
        source_ids = tuple(
            reference.source_chain_id
            for reference in contract.source_chain_references
        )
        if len(source_ids) != len(set(source_ids)):
            _invalid(
                "DUPLICATE_SOURCE_CHAIN_REFERENCE",
                "source-chain references must be unique",
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
                "recording provided orientation must remain explicit",
            )
        if set(contract.capabilities) - set(NON_EXECUTING_ORIENTATION_CAPABILITIES):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "controlled orientation cannot possess executing capabilities",
            )

        return contract


class B1OrientationSafetyValidator:
    """Require an exact supplied B1 classification and boundary."""

    def validate(
        self,
        orientation: B1OrientationContract,
        classification: GuardianClassificationContract,
        boundary: AnswerBoundaryContract,
    ) -> B1OrientationContract:
        orientation = B1OrientationContractValidator().validate(orientation)
        classification = GuardianClassificationValidator().validate(classification)
        boundary = GuardianAnswerBoundaryValidator().validate(boundary)

        if (
            orientation.classification_reference.classification_id
            != classification.classification_id
        ):
            _invalid(
                "CLASSIFICATION_REFERENCE_MISMATCH",
                "orientation classification reference does not match",
            )
        if orientation.boundary_reference.boundary_id != boundary.boundary_id:
            _invalid(
                "BOUNDARY_REFERENCE_MISMATCH",
                "orientation boundary reference does not match",
            )
        b1_level = answer_mode_protection_level(
            AnswerOperatingMode.B1_GENERAL_ORIENTATION
        )
        if answer_mode_protection_level(classification.effective_level) != b1_level:
            _invalid(
                "CLASSIFICATION_NOT_B1",
                "controlled B1 orientation requires an effective B1 classification",
            )
        if answer_mode_protection_level(boundary.effective_mode) != b1_level:
            _invalid(
                "BOUNDARY_NOT_B1",
                "controlled B1 orientation requires an effective B1 boundary",
            )
        if classification.professional_decision_requested:
            _invalid(
                "PROFESSIONAL_DECISION_FORBIDDEN",
                "controlled B1 orientation cannot represent a professional decision",
            )

        return orientation


@dataclass(frozen=True)
class ControlledOrientationEnvelope:
    foundation: GuardianAnswerFoundationIntegration
    orientation: B1OrientationContract

    def __post_init__(self) -> None:
        if not isinstance(self.foundation, GuardianAnswerFoundationIntegration):
            raise TypeError(
                "foundation must be a GuardianAnswerFoundationIntegration"
            )
        if not isinstance(self.orientation, B1OrientationContract):
            raise TypeError("orientation must be a B1OrientationContract")


class ControlledOrientationEnvelopeValidator:
    """Validate the complete referenced B1 evidence flow without execution."""

    def validate(
        self,
        envelope: ControlledOrientationEnvelope,
    ) -> ControlledOrientationEnvelope:
        if not isinstance(envelope, ControlledOrientationEnvelope):
            raise TypeError("envelope must be a ControlledOrientationEnvelope")

        foundation = GuardianAnswerFoundationIntegrationValidator().validate(
            envelope.foundation
        )
        if not foundation.require_complete_source_chain_set:
            _invalid(
                "COMPLETE_SOURCE_CHAIN_SET_REQUIRED",
                "controlled orientation requires complete source-chain validation",
            )

        B1OrientationSafetyValidator().validate(
            envelope.orientation,
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
                "the B1 boundary must reference the integrated classification",
            )

        orientation_source_ids = tuple(
            reference.source_chain_id
            for reference in envelope.orientation.source_chain_references
        )
        classification_source_ids = tuple(
            reference.source_chain_id
            for reference in foundation.classification_contract.source_chain_references
        )
        supplied_source_ids = tuple(
            contract.source_chain_id
            for contract in foundation.source_chain_contracts
        )
        if orientation_source_ids != classification_source_ids:
            _invalid(
                "ORIENTATION_SOURCE_CHAIN_SET_MISMATCH",
                "orientation and classification source-chain references must match exactly",
            )
        if orientation_source_ids != supplied_source_ids:
            _invalid(
                "SUPPLIED_SOURCE_CHAIN_SET_MISMATCH",
                "orientation references and supplied source chains must match exactly",
            )

        return envelope


def _invalid(code: str, message: str) -> None:
    raise ControlledOrientationValidationError(code, message)


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
