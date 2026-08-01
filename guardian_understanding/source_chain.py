"""Immutable, non-executing T4 source-chain contracts from ADR-0047."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional, Tuple


class SourceKind(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"


class SourceUncertaintyStatus(str, Enum):
    CONFIRMED = "bestätigt"
    DISPUTED = "strittig"
    CURRENTNESS_NOT_CONFIRMED = "Aktualität nicht bestätigt"
    POSSIBLY_OUTDATED = "möglicherweise überholt"
    CONTRADICTORY_SOURCE_SITUATION = "widersprüchliche Quellenlage"
    UNCONFIRMED = "unbestätigt"


class SourceRecheckKind(str, Enum):
    DATE_BASED = "DATE_BASED"
    EVENT_BASED = "EVENT_BASED"


class SourceProvenanceCategory(str, Enum):
    PROVIDED_SOURCE_RECORD = "PROVIDED_SOURCE_RECORD"
    PROVIDED_DOCUMENT_REFERENCE = "PROVIDED_DOCUMENT_REFERENCE"
    PROVIDED_RESEARCH_RESULT = "PROVIDED_RESEARCH_RESULT"


class SourceChainCapability(str, Enum):
    ACCEPT_TYPED_SOURCE_INFORMATION = "ACCEPT_TYPED_SOURCE_INFORMATION"
    RESEARCH_SOURCE = "RESEARCH_SOURCE"
    INTERPRET_SOURCE = "INTERPRET_SOURCE"
    EVALUATE_SOURCE = "EVALUATE_SOURCE"
    COMPARE_SOURCES = "COMPARE_SOURCES"
    PRIORITIZE_SOURCE = "PRIORITIZE_SOURCE"
    REPLACE_SOURCE = "REPLACE_SOURCE"
    MODIFY_STATE = "MODIFY_STATE"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    GRANT_APPROVAL = "GRANT_APPROVAL"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"
    PERSIST_SOURCE = "PERSIST_SOURCE"


NON_EXECUTING_SOURCE_CHAIN_CAPABILITIES = (
    SourceChainCapability.ACCEPT_TYPED_SOURCE_INFORMATION,
)


@dataclass(frozen=True)
class DeclaredSourceContradiction:
    conflicting_source_chain_id: str
    declaration_reference: str

    def __post_init__(self) -> None:
        _text(self.conflicting_source_chain_id, "conflicting_source_chain_id")
        _text(self.declaration_reference, "declaration_reference")


@dataclass(frozen=True)
class SourceRecheckRequirement:
    kind: SourceRecheckKind
    recheck_on: Optional[date] = None
    event_reference: Optional[str] = None

    def __post_init__(self) -> None:
        _enum(self.kind, SourceRecheckKind, "kind")
        if self.recheck_on is not None and type(self.recheck_on) is not date:
            raise TypeError("recheck_on must be a date")
        if self.event_reference is not None:
            _text(self.event_reference, "event_reference")


@dataclass(frozen=True)
class GuardianAnswerContextReference:
    guardian_answer_id: str
    conversation_context_id: str

    def __post_init__(self) -> None:
        _text(self.guardian_answer_id, "guardian_answer_id")
        _text(self.conversation_context_id, "conversation_context_id")


@dataclass(frozen=True)
class GuardianSourceChainContract:
    """One-to-one representation of the twelve ADR-0047 section 7 fields.

    Mapping: (1) source_name + publisher; (2) source_kind + source_authority;
    (3) source_reference; (4) retrieved_at; (5) publication_or_version;
    (6) supported_statement; (7) jurisdiction_or_scope;
    (8) declared_contradictions; (9) uncertainty_status;
    (10) recheck_requirement; (11) answer_context_reference;
    (12) provenance_category + provenance_reference.

    ``source_chain_id`` supplies identity for declarative contradiction
    references. ``capabilities`` is an explicit non-execution boundary. Neither
    field adds source content or a version/successor relationship.
    """

    source_chain_id: str
    source_name: str
    publisher: str
    source_kind: SourceKind
    source_authority: str
    source_reference: str
    retrieved_at: datetime
    publication_or_version: Optional[str]
    supported_statement: str
    jurisdiction_or_scope: str
    declared_contradictions: Tuple[DeclaredSourceContradiction, ...]
    uncertainty_status: SourceUncertaintyStatus
    recheck_requirement: SourceRecheckRequirement
    answer_context_reference: GuardianAnswerContextReference
    provenance_category: SourceProvenanceCategory
    provenance_reference: str
    capabilities: Tuple[SourceChainCapability, ...] = (
        SourceChainCapability.ACCEPT_TYPED_SOURCE_INFORMATION,
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.source_chain_id, "source_chain_id"),
            (self.source_name, "source_name"),
            (self.publisher, "publisher"),
            (self.source_authority, "source_authority"),
            (self.source_reference, "source_reference"),
            (self.supported_statement, "supported_statement"),
            (self.jurisdiction_or_scope, "jurisdiction_or_scope"),
            (self.provenance_reference, "provenance_reference"),
        ):
            _text(value, name)
        _enum(self.source_kind, SourceKind, "source_kind")
        _aware_datetime(self.retrieved_at, "retrieved_at")
        if self.publication_or_version is not None:
            _text(self.publication_or_version, "publication_or_version")
        _typed_tuple(
            self.declared_contradictions,
            DeclaredSourceContradiction,
            "declared_contradictions",
        )
        _enum(
            self.uncertainty_status,
            SourceUncertaintyStatus,
            "uncertainty_status",
        )
        if not isinstance(self.recheck_requirement, SourceRecheckRequirement):
            raise TypeError("recheck_requirement must be a SourceRecheckRequirement")
        if not isinstance(
            self.answer_context_reference,
            GuardianAnswerContextReference,
        ):
            raise TypeError(
                "answer_context_reference must be a GuardianAnswerContextReference"
            )
        _enum(
            self.provenance_category,
            SourceProvenanceCategory,
            "provenance_category",
        )
        _typed_tuple(self.capabilities, SourceChainCapability, "capabilities")


class SourceChainValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianSourceChainValidator:
    """Validate typed structure without assessing or changing source content."""

    def validate(
        self,
        contract: GuardianSourceChainContract,
    ) -> GuardianSourceChainContract:
        if not isinstance(contract, GuardianSourceChainContract):
            raise TypeError("contract must be a GuardianSourceChainContract")

        contradiction_ids = tuple(
            item.conflicting_source_chain_id
            for item in contract.declared_contradictions
        )
        if contract.source_chain_id in contradiction_ids:
            _invalid("SELF_CONTRADICTION", "a source chain cannot contradict itself")
        if len(contradiction_ids) != len(set(contradiction_ids)):
            _invalid(
                "DUPLICATE_CONTRADICTION",
                "declared contradiction references must be unique",
            )

        requirement = contract.recheck_requirement
        if requirement.kind is SourceRecheckKind.DATE_BASED:
            if requirement.recheck_on is None or requirement.event_reference is not None:
                _invalid(
                    "INVALID_DATE_RECHECK",
                    "date-based recheck requires only recheck_on",
                )
        elif requirement.kind is SourceRecheckKind.EVENT_BASED:
            if requirement.event_reference is None or requirement.recheck_on is not None:
                _invalid(
                    "INVALID_EVENT_RECHECK",
                    "event-based recheck requires only event_reference",
                )

        if not contract.capabilities:
            _invalid(
                "SOURCE_INPUT_CAPABILITY_MISSING",
                "typed source input capability is required",
            )
        if set(contract.capabilities) - set(NON_EXECUTING_SOURCE_CHAIN_CAPABILITIES):
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "source-chain contracts cannot possess executing capabilities",
            )

        return contract


def _invalid(code: str, message: str) -> None:
    raise SourceChainValidationError(code, message)


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

