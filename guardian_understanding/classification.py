"""Immutable evidence for an already provided answer-mode classification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    answer_mode_protection_level,
    most_protective_answer_mode,
)
from guardian_understanding.source_chain import SourceChainReference


class ClassificationReason(str, Enum):
    GENERAL_ORIENTATION = "GENERAL_ORIENTATION"
    PERSONAL_PREPARATION = "PERSONAL_PREPARATION"
    PROFESSIONAL_DECISION_REQUESTED = "PROFESSIONAL_DECISION_REQUESTED"
    UNCERTAIN_CLASSIFICATION = "UNCERTAIN_CLASSIFICATION"
    CONFLICTING_SIGNALS = "CONFLICTING_SIGNALS"
    PROTECTIVE_ESCALATION = "PROTECTIVE_ESCALATION"
    MANUAL_ASSIGNMENT = "MANUAL_ASSIGNMENT"


class ClassificationProviderType(str, Enum):
    HUMAN_OPERATOR = "HUMAN_OPERATOR"
    TYPED_INPUT_ADAPTER = "TYPED_INPUT_ADAPTER"
    CLASSIFIER_MODEL = "CLASSIFIER_MODEL"


class ClassificationUncertaintyStatus(str, Enum):
    CERTAIN = "CERTAIN"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING_INPUTS = "CONFLICTING_INPUTS"


class ClassificationCapability(str, Enum):
    RECORD_PROVIDED_CLASSIFICATION = "RECORD_PROVIDED_CLASSIFICATION"
    INTERPRET_NATURAL_LANGUAGE = "INTERPRET_NATURAL_LANGUAGE"
    CLASSIFY_REQUEST = "CLASSIFY_REQUEST"
    DETERMINE_CANDIDATES = "DETERMINE_CANDIDATES"
    CALL_MODEL = "CALL_MODEL"
    AUTHORIZE_PROVIDER = "AUTHORIZE_PROVIDER"
    ACTIVATE_ANSWER_MODE = "ACTIVATE_ANSWER_MODE"
    CREATE_BOUNDARY_CONTRACT = "CREATE_BOUNDARY_CONTRACT"
    GENERATE_ANSWER = "GENERATE_ANSWER"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    PERSIST_CLASSIFICATION = "PERSIST_CLASSIFICATION"


NON_EXECUTING_CLASSIFICATION_CAPABILITIES = (
    ClassificationCapability.RECORD_PROVIDED_CLASSIFICATION,
)


@dataclass(frozen=True)
class GuardianClassificationContract:
    """Typed evidence only; it never derives or activates a classification."""

    classification_id: str
    provided_minimum_level: AnswerOperatingMode
    candidate_levels: Tuple[AnswerOperatingMode, ...]
    effective_level: AnswerOperatingMode
    classification_reason: ClassificationReason
    professional_decision_requested: bool
    provider_type: ClassificationProviderType
    provider_reference: str
    classified_at: datetime
    uncertainty_status: ClassificationUncertaintyStatus
    conversation_context_reference: str
    previous_classification_id: Optional[str]
    source_chain_references: Tuple[SourceChainReference, ...] = ()
    capabilities: Tuple[ClassificationCapability, ...] = (
        ClassificationCapability.RECORD_PROVIDED_CLASSIFICATION,
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.classification_id, "classification_id"),
            (self.provider_reference, "provider_reference"),
            (
                self.conversation_context_reference,
                "conversation_context_reference",
            ),
        ):
            _text(value, name)
        _enum(
            self.provided_minimum_level,
            AnswerOperatingMode,
            "provided_minimum_level",
        )
        _typed_tuple(self.candidate_levels, AnswerOperatingMode, "candidate_levels")
        _enum(self.effective_level, AnswerOperatingMode, "effective_level")
        _enum(
            self.classification_reason,
            ClassificationReason,
            "classification_reason",
        )
        if not isinstance(self.professional_decision_requested, bool):
            raise TypeError("professional_decision_requested must be a bool")
        _enum(self.provider_type, ClassificationProviderType, "provider_type")
        _aware_datetime(self.classified_at, "classified_at")
        _enum(
            self.uncertainty_status,
            ClassificationUncertaintyStatus,
            "uncertainty_status",
        )
        if self.previous_classification_id is not None:
            _text(self.previous_classification_id, "previous_classification_id")
        _typed_tuple(
            self.source_chain_references,
            SourceChainReference,
            "source_chain_references",
        )
        _typed_tuple(
            self.capabilities,
            ClassificationCapability,
            "capabilities",
        )


class ClassificationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianClassificationValidator:
    """Validate provided classification evidence without producing a result."""

    def validate(
        self,
        contract: GuardianClassificationContract,
    ) -> GuardianClassificationContract:
        if not isinstance(contract, GuardianClassificationContract):
            raise TypeError("contract must be a GuardianClassificationContract")

        if not contract.candidate_levels:
            _invalid("EMPTY_CANDIDATES", "candidate_levels must not be empty")
        if len(contract.candidate_levels) != len(set(contract.candidate_levels)):
            _invalid("DUPLICATE_CANDIDATES", "candidate_levels must be unique")

        if contract.effective_level is not most_protective_answer_mode(
            contract.candidate_levels
        ):
            _invalid(
                "EFFECTIVE_LEVEL_NOT_PROTECTIVE_MAXIMUM",
                "effective_level must be the most protective candidate",
            )
        if answer_mode_protection_level(
            contract.effective_level
        ) < answer_mode_protection_level(contract.provided_minimum_level):
            _invalid(
                "MINIMUM_LEVEL_NOT_MET",
                "effective_level must meet the provided minimum level",
            )

        if contract.professional_decision_requested:
            required = AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
            if required not in contract.candidate_levels or contract.effective_level is not required:
                _invalid(
                    "PROFESSIONAL_DECISION_REQUIRES_B3",
                    "a provided professional decision request requires B3",
                )

        if (
            contract.classification_reason is ClassificationReason.MANUAL_ASSIGNMENT
            and contract.provider_type is not ClassificationProviderType.HUMAN_OPERATOR
        ):
            _invalid(
                "MANUAL_ASSIGNMENT_REQUIRES_HUMAN",
                "manual assignment requires a human operator provider",
            )

        if contract.previous_classification_id == contract.classification_id:
            _invalid(
                "SELF_PREDECESSOR",
                "previous_classification_id must not reference the contract itself",
            )

        source_chain_ids = tuple(
            reference.source_chain_id
            for reference in contract.source_chain_references
        )
        if len(source_chain_ids) != len(set(source_chain_ids)):
            _invalid(
                "DUPLICATE_SOURCE_CHAIN_REFERENCE",
                "source-chain references must be unique",
            )

        if not contract.capabilities:
            _invalid(
                "RECORD_CAPABILITY_MISSING",
                "recording provided classification evidence must remain explicit",
            )
        if set(contract.capabilities) - set(
            NON_EXECUTING_CLASSIFICATION_CAPABILITIES
        ):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "classification evidence cannot possess executing capabilities",
            )

        return contract


def _invalid(code: str, message: str) -> None:
    raise ClassificationValidationError(code, message)


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
