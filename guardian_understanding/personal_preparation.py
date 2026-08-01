"""Immutable evidence for already provided personal preparation at B2."""

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
from guardian_understanding.source_chain import SourceChainReference


class PersonalPreparationCapability(str, Enum):
    RECORD_PROVIDED_PREPARATION = "RECORD_PROVIDED_PREPARATION"
    INTERPRET_NATURAL_LANGUAGE = "INTERPRET_NATURAL_LANGUAGE"
    EXTRACT_PERSONAL_FACTS = "EXTRACT_PERSONAL_FACTS"
    GENERATE_OPEN_QUESTIONS = "GENERATE_OPEN_QUESTIONS"
    DETERMINE_OPTIONS = "DETERMINE_OPTIONS"
    PRIORITIZE_OPTION = "PRIORITIZE_OPTION"
    ASSESS_RISK = "ASSESS_RISK"
    RESOLVE_UNCERTAINTY = "RESOLVE_UNCERTAINTY"
    MAKE_PROFESSIONAL_DECISION = "MAKE_PROFESSIONAL_DECISION"
    ACTIVATE_ANSWER_MODE = "ACTIVATE_ANSWER_MODE"
    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    PERSIST_PREPARATION = "PERSIST_PREPARATION"


NON_EXECUTING_PREPARATION_CAPABILITIES = (
    PersonalPreparationCapability.RECORD_PROVIDED_PREPARATION,
)


@dataclass(frozen=True)
class PersonalContextReference:
    personal_context_id: str

    def __post_init__(self) -> None:
        _text(self.personal_context_id, "personal_context_id")


@dataclass(frozen=True)
class GeneralOrientationReference:
    orientation_id: str

    def __post_init__(self) -> None:
        _text(self.orientation_id, "orientation_id")


@dataclass(frozen=True)
class KnownFactEntry:
    entry_id: str
    content: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _entry(self.entry_id, self.content, self.source_chain_references)


@dataclass(frozen=True)
class OpenQuestionEntry:
    entry_id: str
    content: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _entry(self.entry_id, self.content, self.source_chain_references)


@dataclass(frozen=True)
class OptionForConsiderationEntry:
    entry_id: str
    content: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _entry(self.entry_id, self.content, self.source_chain_references)


@dataclass(frozen=True)
class UncertaintyEntry:
    entry_id: str
    content: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _entry(self.entry_id, self.content, self.source_chain_references)


@dataclass(frozen=True)
class ProfessionalReviewTopicEntry:
    entry_id: str
    content: str
    source_chain_references: Tuple[SourceChainReference, ...] = ()

    def __post_init__(self) -> None:
        _entry(self.entry_id, self.content, self.source_chain_references)


@dataclass(frozen=True)
class B2PersonalPreparationContract:
    preparation_id: str
    classification_reference: ClassificationReference
    boundary_reference: BoundaryReference
    source_chain_references: Tuple[SourceChainReference, ...]
    personal_context_reference: PersonalContextReference
    preparation_goal: str
    known_facts: Tuple[KnownFactEntry, ...]
    open_questions: Tuple[OpenQuestionEntry, ...]
    options_for_consideration: Tuple[OptionForConsiderationEntry, ...]
    uncertainties: Tuple[UncertaintyEntry, ...]
    professional_review_topics: Tuple[ProfessionalReviewTopicEntry, ...]
    general_orientation_reference: Optional[GeneralOrientationReference]
    created_at: datetime
    provider_type: OrientationProviderType
    provider_reference: str
    professional_review_status: ProfessionalReviewStatus
    professional_review_reference: Optional[str]
    capabilities: Tuple[PersonalPreparationCapability, ...] = (
        PersonalPreparationCapability.RECORD_PROVIDED_PREPARATION,
    )

    def __post_init__(self) -> None:
        _text(self.preparation_id, "preparation_id")
        _text(self.preparation_goal, "preparation_goal")
        _text(self.provider_reference, "provider_reference")
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
        if not isinstance(self.personal_context_reference, PersonalContextReference):
            raise TypeError(
                "personal_context_reference must be a PersonalContextReference"
            )
        _typed_tuple(self.known_facts, KnownFactEntry, "known_facts")
        _typed_tuple(self.open_questions, OpenQuestionEntry, "open_questions")
        _typed_tuple(
            self.options_for_consideration,
            OptionForConsiderationEntry,
            "options_for_consideration",
        )
        _typed_tuple(self.uncertainties, UncertaintyEntry, "uncertainties")
        _typed_tuple(
            self.professional_review_topics,
            ProfessionalReviewTopicEntry,
            "professional_review_topics",
        )
        if self.general_orientation_reference is not None and not isinstance(
            self.general_orientation_reference,
            GeneralOrientationReference,
        ):
            raise TypeError(
                "general_orientation_reference must be a GeneralOrientationReference"
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
            PersonalPreparationCapability,
            "capabilities",
        )


class PersonalPreparationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B2PersonalPreparationContractValidator:
    """Validate provided structure without interpreting preparation content."""

    def validate(
        self,
        contract: B2PersonalPreparationContract,
    ) -> B2PersonalPreparationContract:
        if not isinstance(contract, B2PersonalPreparationContract):
            raise TypeError("contract must be a B2PersonalPreparationContract")

        total_source_ids = _unique_source_ids(
            contract.source_chain_references,
            required=True,
            duplicate_code="DUPLICATE_SOURCE_CHAIN_REFERENCE",
        )
        if not contract.known_facts and not contract.open_questions:
            _invalid(
                "PREPARATION_CONTENT_REQUIRED",
                "at least one known fact or open question is required",
            )
        if not contract.professional_review_topics:
            _invalid(
                "PROFESSIONAL_REVIEW_TOPIC_REQUIRED",
                "at least one professional review topic is required",
            )

        for entries, label in (
            (contract.known_facts, "known_facts"),
            (contract.open_questions, "open_questions"),
            (contract.options_for_consideration, "options_for_consideration"),
            (contract.uncertainties, "uncertainties"),
            (contract.professional_review_topics, "professional_review_topics"),
        ):
            entry_ids = tuple(entry.entry_id for entry in entries)
            if len(entry_ids) != len(set(entry_ids)):
                _invalid(
                    "DUPLICATE_ENTRY_ID",
                    "{} entry IDs must be unique".format(label),
                )
            for entry in entries:
                entry_source_ids = _unique_source_ids(
                    entry.source_chain_references,
                    required=False,
                    duplicate_code="DUPLICATE_ENTRY_SOURCE_CHAIN_REFERENCE",
                )
                if not set(entry_source_ids) <= set(total_source_ids):
                    _invalid(
                        "ENTRY_SOURCE_CHAIN_NOT_DECLARED",
                        "entry source-chain references must belong to the preparation",
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
                "recording provided preparation must remain explicit",
            )
        if set(contract.capabilities) - set(
            NON_EXECUTING_PREPARATION_CAPABILITIES
        ):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "personal preparation cannot possess executing capabilities",
            )

        return contract


class B2PersonalPreparationSafetyValidator:
    """Require an exact supplied B2 classification and boundary."""

    def validate(
        self,
        preparation: B2PersonalPreparationContract,
        classification: GuardianClassificationContract,
        boundary: AnswerBoundaryContract,
    ) -> B2PersonalPreparationContract:
        preparation = B2PersonalPreparationContractValidator().validate(preparation)
        classification = GuardianClassificationValidator().validate(classification)
        boundary = GuardianAnswerBoundaryValidator().validate(boundary)

        if (
            preparation.classification_reference.classification_id
            != classification.classification_id
        ):
            _invalid(
                "CLASSIFICATION_REFERENCE_MISMATCH",
                "preparation classification reference does not match",
            )
        if preparation.boundary_reference.boundary_id != boundary.boundary_id:
            _invalid(
                "BOUNDARY_REFERENCE_MISMATCH",
                "preparation boundary reference does not match",
            )

        b2_level = answer_mode_protection_level(
            AnswerOperatingMode.B2_PERSONAL_PREPARATION
        )
        if answer_mode_protection_level(classification.effective_level) != b2_level:
            _invalid(
                "CLASSIFICATION_NOT_B2",
                "personal preparation requires an effective B2 classification",
            )
        if answer_mode_protection_level(boundary.effective_mode) != b2_level:
            _invalid(
                "BOUNDARY_NOT_B2",
                "personal preparation requires an effective B2 boundary",
            )
        if classification.professional_decision_requested:
            _invalid(
                "PROFESSIONAL_DECISION_FORBIDDEN",
                "personal preparation cannot represent a professional decision",
            )

        return preparation


@dataclass(frozen=True)
class PersonalPreparationEnvelope:
    foundation: GuardianAnswerFoundationIntegration
    preparation: B2PersonalPreparationContract
    general_orientation: Optional[ControlledOrientationEnvelope] = None

    def __post_init__(self) -> None:
        if not isinstance(self.foundation, GuardianAnswerFoundationIntegration):
            raise TypeError(
                "foundation must be a GuardianAnswerFoundationIntegration"
            )
        if not isinstance(self.preparation, B2PersonalPreparationContract):
            raise TypeError(
                "preparation must be a B2PersonalPreparationContract"
            )
        if self.general_orientation is not None and not isinstance(
            self.general_orientation,
            ControlledOrientationEnvelope,
        ):
            raise TypeError(
                "general_orientation must be a ControlledOrientationEnvelope"
            )


class PersonalPreparationEnvelopeValidator:
    """Validate the complete B2 evidence flow without producing any content."""

    def validate(
        self,
        envelope: PersonalPreparationEnvelope,
    ) -> PersonalPreparationEnvelope:
        if not isinstance(envelope, PersonalPreparationEnvelope):
            raise TypeError("envelope must be a PersonalPreparationEnvelope")

        foundation = GuardianAnswerFoundationIntegrationValidator().validate(
            envelope.foundation
        )
        if not foundation.require_complete_source_chain_set:
            _invalid(
                "COMPLETE_SOURCE_CHAIN_SET_REQUIRED",
                "personal preparation requires complete source-chain validation",
            )

        B2PersonalPreparationSafetyValidator().validate(
            envelope.preparation,
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
                "the B2 boundary must reference the integrated classification",
            )

        preparation_source_ids = tuple(
            reference.source_chain_id
            for reference in envelope.preparation.source_chain_references
        )
        supplied_source_ids = tuple(
            contract.source_chain_id
            for contract in foundation.source_chain_contracts
        )
        if preparation_source_ids != supplied_source_ids:
            _invalid(
                "SOURCE_CHAIN_SET_MISMATCH",
                "preparation references and supplied source chains must match exactly",
            )

        orientation_reference = envelope.preparation.general_orientation_reference
        if orientation_reference is None:
            if envelope.general_orientation is not None:
                _invalid(
                    "UNREFERENCED_GENERAL_ORIENTATION",
                    "an unreferenced B1 orientation cannot be supplied",
                )
        else:
            if envelope.general_orientation is None:
                _invalid(
                    "GENERAL_ORIENTATION_REQUIRED",
                    "the referenced B1 orientation must be supplied",
                )
            ControlledOrientationEnvelopeValidator().validate(
                envelope.general_orientation
            )
            if (
                envelope.general_orientation.orientation.orientation_id
                != orientation_reference.orientation_id
            ):
                _invalid(
                    "GENERAL_ORIENTATION_REFERENCE_MISMATCH",
                    "the supplied B1 orientation ID does not match",
                )

        return envelope


def _entry(
    entry_id: object,
    content: object,
    source_chain_references: object,
) -> None:
    _text(entry_id, "entry_id")
    _text(content, "content")
    _typed_tuple(
        source_chain_references,
        SourceChainReference,
        "source_chain_references",
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
    source_ids = tuple(reference.source_chain_id for reference in references)
    if len(source_ids) != len(set(source_ids)):
        _invalid(duplicate_code, "source-chain references must be unique")
    return source_ids


def _invalid(code: str, message: str) -> None:
    raise PersonalPreparationValidationError(code, message)


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
