import hashlib
import json
import re
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from artifact_contract import (
    ArtifactAuthorization,
    AuthorizationScope,
    AuthorizationStatus,
)


class KnowledgeType(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"
    USER_STATEMENT = "USER_STATEMENT"
    EXTERNAL_STATEMENT = "EXTERNAL_STATEMENT"
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    INTERPRETATION = "INTERPRETATION"
    PREFERENCE = "PREFERENCE"
    DECISION = "DECISION"
    COMMITMENT = "COMMITMENT"
    MEMORY = "MEMORY"
    PROCEDURAL_KNOWLEDGE = "PROCEDURAL_KNOWLEDGE"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    USER_CONFIRMED = "USER_CONFIRMED"
    SOURCE_CONFIRMED = "SOURCE_CONFIRMED"
    SYSTEM_VALIDATED = "SYSTEM_VALIDATED"
    DISPUTED = "DISPUTED"
    SUPERSEDED = "SUPERSEDED"
    INVALIDATED = "INVALIDATED"


class Confidence(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CONFIRMED = "CONFIRMED"


class Validity(str, Enum):
    CURRENT = "CURRENT"
    TEMPORARY = "TEMPORARY"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"
    DISPUTED = "DISPUTED"
    UNKNOWN = "UNKNOWN"


class Sensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    PERSONAL = "PERSONAL"
    SENSITIVE = "SENSITIVE"
    HIGHLY_SENSITIVE = "HIGHLY_SENSITIVE"


class Visibility(str, Enum):
    OWNER_ONLY = "OWNER_ONLY"
    AUTHORIZED_PARTICIPANTS = "AUTHORIZED_PARTICIPANTS"
    SHARED_SAFE = "SHARED_SAFE"


class RetentionClass(str, Enum):
    KEEP_UNTIL_REVOKED = "KEEP_UNTIL_REVOKED"
    KEEP_FOR_ACTIVE_CONTEXT = "KEEP_FOR_ACTIVE_CONTEXT"
    KEEP_UNTIL_DATE = "KEEP_UNTIL_DATE"
    ARCHIVE = "ARCHIVE"
    ANONYMIZE = "ANONYMIZE"
    DELETE = "DELETE"
    LEGAL_HOLD = "LEGAL_HOLD"
    UNKNOWN = "UNKNOWN"


class MemoryScope(str, Enum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    USER_PREFERENCE = "USER_PREFERENCE"
    CONFIRMED_DECISION = "CONFIRMED_DECISION"
    OPEN_COMMITMENT = "OPEN_COMMITMENT"
    RELATIONSHIP_AND_TRUST = "RELATIONSHIP_AND_TRUST"
    HISTORICAL = "HISTORICAL"


class SourceType(str, Enum):
    USER = "USER"
    EXTERNAL_PERSON = "EXTERNAL_PERSON"
    DOCUMENT_REFERENCE = "DOCUMENT_REFERENCE"
    SYSTEM_OBSERVATION = "SYSTEM_OBSERVATION"
    DERIVED = "DERIVED"
    UNKNOWN = "UNKNOWN"


class ExtractionMethod(str, Enum):
    DIRECT_STATEMENT = "DIRECT_STATEMENT"
    USER_ENTRY = "USER_ENTRY"
    SOURCE_IMPORT = "SOURCE_IMPORT"
    SYSTEM_OBSERVATION = "SYSTEM_OBSERVATION"
    DETERMINISTIC_TRANSFORMATION = "DETERMINISTIC_TRANSFORMATION"
    UNKNOWN = "UNKNOWN"


class VerificationMethod(str, Enum):
    NONE = "NONE"
    USER_CONFIRMATION = "USER_CONFIRMATION"
    SOURCE_COMPARISON = "SOURCE_COMPARISON"
    SYSTEM_VALIDATION = "SYSTEM_VALIDATION"
    PROFESSIONAL_CONFIRMATION = "PROFESSIONAL_CONFIRMATION"
    UNKNOWN = "UNKNOWN"


class TransitionType(str, Enum):
    STATEMENT_RECORDED = "statement_recorded"
    SOURCE_ATTACHED = "source_attached"
    VERIFICATION_ADDED = "verification_added"
    HYPOTHESIS_CREATED = "hypothesis_created"
    HYPOTHESIS_CONFIRMED = "hypothesis_confirmed"
    HYPOTHESIS_REJECTED = "hypothesis_rejected"
    INTERPRETATION_ADDED = "interpretation_added"
    CONTRADICTION_DETECTED = "contradiction_detected"
    KNOWLEDGE_SUPERSEDED = "knowledge_superseded"
    RETENTION_CHANGED = "retention_changed"
    KNOWLEDGE_ARCHIVED = "knowledge_archived"
    KNOWLEDGE_ANONYMIZED = "knowledge_anonymized"
    KNOWLEDGE_DELETED = "knowledge_deleted"


class TransitionResult(str, Enum):
    PLANNED = "PLANNED"


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if (
        not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError(
            "{} must be a trimmed single line".format(field_name)
        )
    return value


def _aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


def _identifiers(value: object, field_name: str) -> Tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    for item in value:
        _text(item, "{} item".format(field_name))
    if len(value) != len(set(value)):
        raise ValueError("{} must contain unique values".format(field_name))
    return value


def _enum(value: object, enum_type: type, field_name: str) -> object:
    if not isinstance(value, enum_type):
        raise TypeError(
            "{} must be {}".format(field_name, enum_type.__name__)
        )
    return value


def _reference(value: object, field_name: str) -> str:
    value = _text(value, field_name)
    lowered = value.lower()
    if (
        lowered.startswith("data:")
        or lowered.startswith("base64:")
        or len(value) > 1000
    ):
        raise ValueError(
            "{} must reference content, not embed it".format(field_name)
        )
    if any(ord(character) < 32 for character in value):
        raise ValueError("{} contains control characters".format(field_name))
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*:\S+", value) is None:
        raise ValueError(
            "{} must be a logical reference with a scheme".format(
                field_name
            )
        )
    return value


@dataclass(frozen=True)
class TransformationStep:
    transformation_type: str
    performed_by: str
    performed_at: datetime
    input_reference_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.transformation_type, "transformation_type")
        _text(self.performed_by, "performed_by")
        _aware(self.performed_at, "performed_at")
        _identifiers(self.input_reference_ids, "input_reference_ids")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transformation_type": self.transformation_type,
            "performed_by": self.performed_by,
            "performed_at": self.performed_at.isoformat(),
            "input_reference_ids": list(self.input_reference_ids),
        }


@dataclass(frozen=True)
class Provenance:
    source_type: SourceType
    source_id: str
    source_owner: str
    source_timestamp: datetime
    extraction_method: ExtractionMethod
    verification_method: VerificationMethod
    transformation_history: Tuple[TransformationStep, ...] = ()
    source_hash: Optional[str] = None

    def __post_init__(self) -> None:
        _enum(self.source_type, SourceType, "source_type")
        _text(self.source_id, "source_id")
        _text(self.source_owner, "source_owner")
        _aware(self.source_timestamp, "source_timestamp")
        _enum(
            self.extraction_method,
            ExtractionMethod,
            "extraction_method",
        )
        _enum(
            self.verification_method,
            VerificationMethod,
            "verification_method",
        )
        if not isinstance(self.transformation_history, tuple) or not all(
            isinstance(item, TransformationStep)
            for item in self.transformation_history
        ):
            raise TypeError(
                "transformation_history must contain TransformationStep"
            )
        if self.source_hash is not None:
            if (
                not isinstance(self.source_hash, str)
                or len(self.source_hash) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in self.source_hash
                )
            ):
                raise ValueError("source_hash must be a SHA-256 digest")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "source_owner": self.source_owner,
            "source_timestamp": self.source_timestamp.isoformat(),
            "extraction_method": self.extraction_method.value,
            "verification_method": self.verification_method.value,
            "transformation_history": [
                item.to_dict() for item in self.transformation_history
            ],
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True)
class KnowledgeItem:
    knowledge_id: str
    subject_id: str
    owner_id: str
    knowledge_type: KnowledgeType
    content_reference: str
    source_references: Tuple[str, ...]
    provenance: Optional[Provenance]
    confidence: Confidence
    validity: Validity
    sensitivity: Sensitivity
    visibility: Visibility
    created_at: datetime
    observed_at: datetime
    valid_from: datetime
    valid_until: Optional[datetime]
    supersedes: Tuple[str, ...]
    contradicted_by: Tuple[str, ...]
    retention_class: RetentionClass
    verification_status: VerificationStatus
    version: int
    retention_until: Optional[datetime] = None
    retention_basis_references: Tuple[str, ...] = ()
    authorization_references: Tuple[str, ...] = ()
    event_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        for name in ("knowledge_id", "subject_id", "owner_id"):
            _text(getattr(self, name), name)
        _reference(self.content_reference, "content_reference")
        _identifiers(self.source_references, "source_references")
        _enum(self.knowledge_type, KnowledgeType, "knowledge_type")
        if self.provenance is not None and not isinstance(
            self.provenance,
            Provenance,
        ):
            raise TypeError("provenance must be Provenance or None")
        if (
            self.provenance is None
            and self.knowledge_type is not KnowledgeType.UNKNOWN
        ):
            raise ValueError("Knowledge requires provenance")
        _enum(self.confidence, Confidence, "confidence")
        _enum(self.validity, Validity, "validity")
        _enum(self.sensitivity, Sensitivity, "sensitivity")
        _enum(self.visibility, Visibility, "visibility")
        for name in ("created_at", "observed_at", "valid_from"):
            _aware(getattr(self, name), name)
        if self.observed_at > self.created_at:
            raise ValueError("observed_at must not follow created_at")
        if self.valid_until is not None:
            _aware(self.valid_until, "valid_until")
            if self.valid_until < self.valid_from:
                raise ValueError("valid_until must not precede valid_from")
        if self.event_at is not None:
            _aware(self.event_at, "event_at")
        _identifiers(self.supersedes, "supersedes")
        _identifiers(self.contradicted_by, "contradicted_by")
        if self.knowledge_id in self.supersedes:
            raise ValueError("Knowledge cannot supersede itself")
        if self.knowledge_id in self.contradicted_by:
            raise ValueError("Knowledge cannot contradict itself")
        _enum(self.retention_class, RetentionClass, "retention_class")
        _enum(
            self.verification_status,
            VerificationStatus,
            "verification_status",
        )
        if not isinstance(self.version, int) or isinstance(self.version, bool):
            raise TypeError("version must be an int")
        if self.version < 1:
            raise ValueError("version must be positive")
        if self.retention_until is not None:
            _aware(self.retention_until, "retention_until")
        _identifiers(
            self.retention_basis_references,
            "retention_basis_references",
        )
        _identifiers(
            self.authorization_references,
            "authorization_references",
        )
        self._validate_semantics()

    def _validate_semantics(self) -> None:
        if self.knowledge_type is KnowledgeType.VERIFIED_FACT:
            if self.provenance is None or not self.source_references:
                raise ValueError(
                    "VERIFIED_FACT requires provenance and sources"
                )
            if self.verification_status not in {
                VerificationStatus.USER_CONFIRMED,
                VerificationStatus.SOURCE_CONFIRMED,
                VerificationStatus.SYSTEM_VALIDATED,
            }:
                raise ValueError(
                    "VERIFIED_FACT requires confirmed verification"
                )
            if (
                self.provenance.verification_method
                in {VerificationMethod.NONE, VerificationMethod.UNKNOWN}
            ):
                raise ValueError(
                    "VERIFIED_FACT requires a verification method"
                )
        if self.knowledge_type is KnowledgeType.USER_STATEMENT:
            if self.provenance is None:
                raise ValueError("USER_STATEMENT requires provenance")
            if self.provenance.source_type is not SourceType.USER:
                raise ValueError(
                    "USER_STATEMENT provenance must identify the user"
                )
        if self.knowledge_type in {
            KnowledgeType.HYPOTHESIS,
            KnowledgeType.INTERPRETATION,
        } and not self.source_references:
            raise ValueError(
                "{} requires source references".format(
                    self.knowledge_type.value
                )
            )
        if (
            self.knowledge_type is KnowledgeType.HYPOTHESIS
            and self.confidence is Confidence.CONFIRMED
        ):
            raise ValueError("HYPOTHESIS must remain explicitly uncertain")
        if (
            self.verification_status is VerificationStatus.DISPUTED
            and self.validity is not Validity.DISPUTED
        ):
            raise ValueError("Disputed verification requires disputed validity")
        if (
            self.verification_status is VerificationStatus.SUPERSEDED
            and self.validity is not Validity.SUPERSEDED
        ):
            raise ValueError(
                "Superseded verification requires superseded validity"
            )
        if (
            self.verification_status is VerificationStatus.INVALIDATED
            and self.validity not in {
                Validity.EXPIRED,
                Validity.DISPUTED,
                Validity.SUPERSEDED,
            }
        ):
            raise ValueError(
                "Invalidated knowledge cannot remain current"
            )
        if (
            self.retention_class is RetentionClass.KEEP_UNTIL_DATE
            and self.retention_until is None
        ):
            raise ValueError("KEEP_UNTIL_DATE requires retention_until")
        if (
            self.retention_class is not RetentionClass.KEEP_UNTIL_DATE
            and self.retention_until is not None
        ):
            raise ValueError(
                "retention_until is only valid for KEEP_UNTIL_DATE"
            )
        if (
            self.retention_class is RetentionClass.LEGAL_HOLD
            and not self.retention_basis_references
        ):
            raise ValueError(
                "LEGAL_HOLD requires documented binding references"
            )
        if (
            self.visibility is Visibility.OWNER_ONLY
            and self.authorization_references
        ):
            raise ValueError(
                "Owner-only knowledge cannot reference sharing authority"
            )
        if (
            self.visibility is not Visibility.OWNER_ONLY
            and not self.authorization_references
        ):
            raise ValueError(
                "Shared visibility requires authorization references"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "subject_id": self.subject_id,
            "owner_id": self.owner_id,
            "knowledge_type": self.knowledge_type.value,
            "content_reference": self.content_reference,
            "source_references": list(self.source_references),
            "provenance": (
                self.provenance.to_dict()
                if self.provenance is not None
                else None
            ),
            "confidence": self.confidence.value,
            "validity": self.validity.value,
            "sensitivity": self.sensitivity.value,
            "visibility": self.visibility.value,
            "created_at": self.created_at.isoformat(),
            "observed_at": self.observed_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": (
                self.valid_until.isoformat()
                if self.valid_until is not None
                else None
            ),
            "supersedes": list(self.supersedes),
            "contradicted_by": list(self.contradicted_by),
            "retention_class": self.retention_class.value,
            "verification_status": self.verification_status.value,
            "version": self.version,
            "retention_until": (
                self.retention_until.isoformat()
                if self.retention_until is not None
                else None
            ),
            "retention_basis_references": list(
                self.retention_basis_references
            ),
            "authorization_references": list(
                self.authorization_references
            ),
            "event_at": (
                self.event_at.isoformat()
                if self.event_at is not None
                else None
            ),
        }


@dataclass(frozen=True)
class GuardianMemory:
    episodic_ids: Tuple[str, ...] = ()
    semantic_ids: Tuple[str, ...] = ()
    preference_ids: Tuple[str, ...] = ()
    decision_ids: Tuple[str, ...] = ()
    commitment_ids: Tuple[str, ...] = ()
    relationship_trust_ids: Tuple[str, ...] = ()
    historical_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        all_ids = []
        for name in (
            "episodic_ids",
            "semantic_ids",
            "preference_ids",
            "decision_ids",
            "commitment_ids",
            "relationship_trust_ids",
            "historical_ids",
        ):
            values = _identifiers(getattr(self, name), name)
            all_ids.extend(values)
        if len(all_ids) != len(set(all_ids)):
            raise ValueError(
                "Knowledge IDs may belong to only one memory scope"
            )

    def all_ids(self) -> Tuple[str, ...]:
        return (
            self.episodic_ids
            + self.semantic_ids
            + self.preference_ids
            + self.decision_ids
            + self.commitment_ids
            + self.relationship_trust_ids
            + self.historical_ids
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episodic_ids": list(self.episodic_ids),
            "semantic_ids": list(self.semantic_ids),
            "preference_ids": list(self.preference_ids),
            "decision_ids": list(self.decision_ids),
            "commitment_ids": list(self.commitment_ids),
            "relationship_trust_ids": list(
                self.relationship_trust_ids
            ),
            "historical_ids": list(self.historical_ids),
        }


@dataclass(frozen=True)
class KnowledgeConflict:
    conflict_id: str
    knowledge_ids: Tuple[str, str]
    detected_at: datetime
    reason: str
    requires_clarification: bool = True

    def __post_init__(self) -> None:
        _text(self.conflict_id, "conflict_id")
        if (
            not isinstance(self.knowledge_ids, tuple)
            or len(self.knowledge_ids) != 2
        ):
            raise TypeError("knowledge_ids must contain exactly two IDs")
        _identifiers(self.knowledge_ids, "knowledge_ids")
        _aware(self.detected_at, "detected_at")
        _text(self.reason, "reason")
        if self.requires_clarification is not True:
            raise ValueError(
                "Knowledge conflicts must require clarification"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "knowledge_ids": list(self.knowledge_ids),
            "detected_at": self.detected_at.isoformat(),
            "reason": self.reason,
            "requires_clarification": self.requires_clarification,
        }


@dataclass(frozen=True)
class RetentionConstraint:
    knowledge_id: str
    retention_class: RetentionClass
    binding_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.knowledge_id, "knowledge_id")
        _enum(self.retention_class, RetentionClass, "retention_class")
        _identifiers(self.binding_references, "binding_references")
        if (
            self.retention_class is RetentionClass.LEGAL_HOLD
            and not self.binding_references
        ):
            raise ValueError("LEGAL_HOLD requires binding references")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "retention_class": self.retention_class.value,
            "binding_references": list(self.binding_references),
        }


@dataclass(frozen=True)
class ArtifactAuthorizationEvidence:
    artifact_id: str
    knowledge_ids: Tuple[str, ...]
    authorization: ArtifactAuthorization

    def __post_init__(self) -> None:
        _text(self.artifact_id, "artifact_id")
        _identifiers(self.knowledge_ids, "knowledge_ids")
        if not self.knowledge_ids:
            raise ValueError(
                "Authorization evidence requires knowledge scope"
            )
        if not isinstance(self.authorization, ArtifactAuthorization):
            raise TypeError(
                "authorization must be ArtifactAuthorization"
            )
        if self.authorization.status is not AuthorizationStatus.ACTIVE:
            raise ValueError("Authorization evidence must be active")
        if AuthorizationScope.AUTHORIZE_ACTION not in (
            self.authorization.scopes
        ):
            raise ValueError(
                "Guardian transition requires authorize_action scope"
            )

    @property
    def authorization_id(self) -> str:
        return self.authorization.authorization_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "knowledge_ids": list(self.knowledge_ids),
            "authorization": {
                "authorization_id": self.authorization.authorization_id,
                "subject_id": self.authorization.subject_id,
                "granted_by": self.authorization.granted_by,
                "scopes": [
                    item.value for item in self.authorization.scopes
                ],
                "purpose": self.authorization.purpose,
                "status": self.authorization.status.value,
                "granted_at": (
                    self.authorization.granted_at.isoformat()
                ),
                "revoked_at": (
                    self.authorization.revoked_at.isoformat()
                    if self.authorization.revoked_at is not None
                    else None
                ),
                "binding_references": list(
                    self.authorization.binding_references
                ),
            },
        }


@dataclass(frozen=True)
class KnowledgeTransition:
    transition_id: str
    transition_type: TransitionType
    previous_item: Optional[KnowledgeItem]
    new_item: Optional[KnowledgeItem]
    trigger: str
    authorization_reference: str
    occurred_at: datetime
    reason: str
    source_references: Tuple[str, ...]
    result: TransitionResult = TransitionResult.PLANNED

    def __post_init__(self) -> None:
        _text(self.transition_id, "transition_id")
        _enum(self.transition_type, TransitionType, "transition_type")
        if self.previous_item is not None and not isinstance(
            self.previous_item,
            KnowledgeItem,
        ):
            raise TypeError("previous_item must be KnowledgeItem or None")
        if self.new_item is not None and not isinstance(
            self.new_item,
            KnowledgeItem,
        ):
            raise TypeError("new_item must be KnowledgeItem or None")
        _text(self.trigger, "trigger")
        _text(self.authorization_reference, "authorization_reference")
        _aware(self.occurred_at, "occurred_at")
        _text(self.reason, "reason")
        _identifiers(self.source_references, "source_references")
        if not self.source_references:
            raise ValueError(
                "KnowledgeTransition requires source references"
            )
        _enum(self.result, TransitionResult, "result")
        _validate_transition(self)

    def validate(self) -> None:
        _validate_transition(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "transition_type": self.transition_type.value,
            "previous_item": (
                self.previous_item.to_dict()
                if self.previous_item is not None
                else None
            ),
            "new_item": (
                self.new_item.to_dict()
                if self.new_item is not None
                else None
            ),
            "trigger": self.trigger,
            "authorization_reference": self.authorization_reference,
            "occurred_at": self.occurred_at.isoformat(),
            "reason": self.reason,
            "source_references": list(self.source_references),
            "result": self.result.value,
        }


def _validate_transition(transition: KnowledgeTransition) -> None:
    before = transition.previous_item
    after = transition.new_item
    creation_types = {
        TransitionType.STATEMENT_RECORDED: {
            KnowledgeType.USER_STATEMENT,
            KnowledgeType.EXTERNAL_STATEMENT,
            KnowledgeType.OBSERVATION,
        },
        TransitionType.HYPOTHESIS_CREATED: {KnowledgeType.HYPOTHESIS},
        TransitionType.INTERPRETATION_ADDED: {
            KnowledgeType.INTERPRETATION
        },
    }
    if transition.transition_type in creation_types:
        if before is not None or after is None:
            raise ValueError("Creation transition has invalid states")
        if after.knowledge_type not in creation_types[
            transition.transition_type
        ]:
            raise ValueError("Creation transition has invalid KnowledgeType")
        if after.visibility is not Visibility.OWNER_ONLY:
            raise ValueError(
                "Conversation knowledge cannot create shared visibility"
            )
        return
    if transition.transition_type is TransitionType.KNOWLEDGE_DELETED:
        if before is None or after is not None:
            raise ValueError("Deletion requires previous state only")
        if before.retention_class is not RetentionClass.DELETE:
            raise ValueError("Only DELETE-class knowledge may be deleted")
        return
    if before is None or after is None:
        raise ValueError("Transition requires previous and new state")
    if before.knowledge_id != after.knowledge_id:
        raise ValueError("Transition cannot change knowledge_id")
    if before.subject_id != after.subject_id or before.owner_id != after.owner_id:
        raise ValueError("Transition cannot change person boundaries")
    if before.knowledge_type is not after.knowledge_type:
        raise ValueError("Knowledge Types cannot be converted by transition")
    if after.version != before.version + 1:
        raise ValueError("Transition must increment version exactly once")
    kind = transition.transition_type
    allowed_changes = {
        TransitionType.SOURCE_ATTACHED: {
            "source_references",
            "provenance",
            "version",
        },
        TransitionType.VERIFICATION_ADDED: {
            "verification_status",
            "confidence",
            "provenance",
            "version",
        },
        TransitionType.HYPOTHESIS_CONFIRMED: {
            "verification_status",
            "confidence",
            "provenance",
            "version",
        },
        TransitionType.HYPOTHESIS_REJECTED: {
            "verification_status",
            "validity",
            "version",
        },
        TransitionType.CONTRADICTION_DETECTED: {
            "contradicted_by",
            "verification_status",
            "validity",
            "version",
        },
        TransitionType.KNOWLEDGE_SUPERSEDED: {
            "verification_status",
            "validity",
            "version",
        },
        TransitionType.RETENTION_CHANGED: {
            "retention_class",
            "retention_until",
            "retention_basis_references",
            "version",
        },
        TransitionType.KNOWLEDGE_ARCHIVED: {
            "retention_class",
            "retention_until",
            "retention_basis_references",
            "version",
        },
        TransitionType.KNOWLEDGE_ANONYMIZED: {
            "content_reference",
            "provenance",
            "retention_class",
            "retention_until",
            "retention_basis_references",
            "version",
        },
    }
    changed = {
        field_name
        for field_name, old_value in before.to_dict().items()
        if after.to_dict()[field_name] != old_value
    }
    if not changed <= allowed_changes.get(kind, set()):
        raise ValueError(
            "Transition contains unrelated mutations: {}".format(
                ", ".join(sorted(changed - allowed_changes.get(kind, set())))
            )
        )
    if kind is TransitionType.SOURCE_ATTACHED:
        if not set(before.source_references) < set(after.source_references):
            raise ValueError("source_attached must add a source")
    elif kind is TransitionType.VERIFICATION_ADDED:
        if before.verification_status is after.verification_status:
            raise ValueError("verification_added must change verification")
        if after.verification_status is VerificationStatus.UNVERIFIED:
            raise ValueError(
                "verification_added cannot remove verification"
            )
    elif kind is TransitionType.HYPOTHESIS_CONFIRMED:
        if before.knowledge_type is not KnowledgeType.HYPOTHESIS:
            raise ValueError("Only a hypothesis can be confirmed")
        if after.verification_status not in {
            VerificationStatus.USER_CONFIRMED,
            VerificationStatus.SOURCE_CONFIRMED,
            VerificationStatus.SYSTEM_VALIDATED,
        }:
            raise ValueError("Confirmed hypothesis needs verification")
    elif kind is TransitionType.HYPOTHESIS_REJECTED:
        if (
            before.knowledge_type is not KnowledgeType.HYPOTHESIS
            or after.verification_status
            is not VerificationStatus.INVALIDATED
        ):
            raise ValueError("Rejected hypothesis must be invalidated")
    elif kind is TransitionType.CONTRADICTION_DETECTED:
        if not set(before.contradicted_by) < set(after.contradicted_by):
            raise ValueError("contradiction_detected must add a reference")
        if after.validity is not Validity.DISPUTED:
            raise ValueError("Contradicted knowledge must be disputed")
    elif kind is TransitionType.KNOWLEDGE_SUPERSEDED:
        if (
            after.validity is not Validity.SUPERSEDED
            or after.verification_status
            is not VerificationStatus.SUPERSEDED
        ):
            raise ValueError("Superseded knowledge must be marked")
    elif kind is TransitionType.RETENTION_CHANGED:
        if before.retention_class is after.retention_class:
            raise ValueError("retention_changed must change retention")
    elif kind is TransitionType.KNOWLEDGE_ARCHIVED:
        if after.retention_class is not RetentionClass.ARCHIVE:
            raise ValueError("Archived knowledge must use ARCHIVE")
    elif kind is TransitionType.KNOWLEDGE_ANONYMIZED:
        if after.retention_class is not RetentionClass.ANONYMIZE:
            raise ValueError("Anonymized knowledge must use ANONYMIZE")


@dataclass(frozen=True)
class GuardianRuntimeSnapshot:
    schema_version: str
    captured_at: datetime
    active_guardian_id: Optional[str]
    active_subject_id: Optional[str]
    knowledge_snapshot_version: int
    applicable_memory_scope: Tuple[MemoryScope, ...]
    knowledge_items: Tuple[KnowledgeItem, ...]
    memory: GuardianMemory
    unresolved_conflicts: Tuple[KnowledgeConflict, ...]
    open_hypotheses: Tuple[str, ...]
    active_authorizations: Tuple[ArtifactAuthorizationEvidence, ...]
    retention_constraints: Tuple[RetentionConstraint, ...]
    provenance_integrity: bool
    transitions: Tuple[KnowledgeTransition, ...]
    runtime_context_hash: str

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("GuardianRuntimeSnapshot schema must be 1.0")
        _aware(self.captured_at, "captured_at")
        if (self.active_guardian_id is None) != (
            self.active_subject_id is None
        ):
            raise ValueError(
                "Guardian and subject assignment must be present together"
            )
        if self.active_guardian_id is not None:
            _text(self.active_guardian_id, "active_guardian_id")
            _text(self.active_subject_id, "active_subject_id")
        if (
            not isinstance(self.knowledge_snapshot_version, int)
            or isinstance(self.knowledge_snapshot_version, bool)
        ):
            raise TypeError("knowledge_snapshot_version must be an int")
        if self.knowledge_snapshot_version < 0:
            raise ValueError(
                "knowledge_snapshot_version must not be negative"
            )
        if (
            not isinstance(self.applicable_memory_scope, tuple)
            or not all(
                isinstance(item, MemoryScope)
                for item in self.applicable_memory_scope
            )
        ):
            raise TypeError(
                "applicable_memory_scope must contain MemoryScope"
            )
        if len(self.applicable_memory_scope) != len(
            set(self.applicable_memory_scope)
        ):
            raise ValueError("applicable_memory_scope must be unique")
        if not isinstance(self.knowledge_items, tuple) or not all(
            isinstance(item, KnowledgeItem)
            for item in self.knowledge_items
        ):
            raise TypeError("knowledge_items must contain KnowledgeItem")
        if not isinstance(self.memory, GuardianMemory):
            raise TypeError("memory must be GuardianMemory")
        if not isinstance(self.unresolved_conflicts, tuple) or not all(
            isinstance(item, KnowledgeConflict)
            for item in self.unresolved_conflicts
        ):
            raise TypeError(
                "unresolved_conflicts must contain KnowledgeConflict"
            )
        _identifiers(self.open_hypotheses, "open_hypotheses")
        if not isinstance(self.active_authorizations, tuple) or not all(
            isinstance(item, ArtifactAuthorizationEvidence)
            for item in self.active_authorizations
        ):
            raise TypeError(
                "active_authorizations must contain "
                "ArtifactAuthorizationEvidence"
            )
        if not isinstance(self.retention_constraints, tuple) or not all(
            isinstance(item, RetentionConstraint)
            for item in self.retention_constraints
        ):
            raise TypeError(
                "retention_constraints must contain RetentionConstraint"
            )
        if not isinstance(self.provenance_integrity, bool):
            raise TypeError("provenance_integrity must be a bool")
        if not isinstance(self.transitions, tuple) or not all(
            isinstance(item, KnowledgeTransition)
            for item in self.transitions
        ):
            raise TypeError(
                "transitions must contain KnowledgeTransition"
            )
        for transition in self.transitions:
            transition.validate()
        self._validate_scope()
        self._validate_transition_history()
        expected_hash = self.calculate_hash()
        if self.runtime_context_hash != expected_hash:
            raise ValueError("Guardian Runtime context hash is invalid")

    def _validate_scope(self) -> None:
        item_ids = tuple(item.knowledge_id for item in self.knowledge_items)
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Knowledge IDs must be unique")
        items = {item.knowledge_id: item for item in self.knowledge_items}
        if self.active_subject_id is None:
            if (
                self.knowledge_items
                or self.memory.all_ids()
                or self.unresolved_conflicts
                or self.open_hypotheses
                or self.active_authorizations
                or self.retention_constraints
                or self.transitions
                or self.applicable_memory_scope
            ):
                raise ValueError(
                    "Unbound Guardian Runtime must be completely empty"
                )
            return
        for item in self.knowledge_items:
            if item.created_at > self.captured_at:
                raise ValueError(
                    "Knowledge cannot be stored after snapshot capture"
                )
            if (
                item.owner_id != self.active_subject_id
                or item.subject_id != self.active_subject_id
            ):
                raise ValueError(
                    "Knowledge item crosses the person-bound context"
                )
            for reference in item.supersedes + item.contradicted_by:
                if reference not in items:
                    raise ValueError(
                        "Knowledge relation references another context"
                    )
            for superseded_id in item.supersedes:
                superseded = items[superseded_id]
                if superseded.validity is not Validity.SUPERSEDED:
                    raise ValueError(
                        "Superseded reference must preserve old history"
                    )
            active = {
                evidence.authorization_id: evidence
                for evidence in self.active_authorizations
            }
            if not set(item.authorization_references) <= set(
                active
            ):
                raise ValueError(
                    "Knowledge visibility lacks active authorization"
                )
            for reference in item.authorization_references:
                evidence = active[reference]
                if (
                    item.knowledge_id not in evidence.knowledge_ids
                    or AuthorizationScope.READ
                    not in evidence.authorization.scopes
                ):
                    raise ValueError(
                        "Knowledge sharing exceeds authorization scope"
                    )
        authorization_ids = tuple(
            item.authorization_id for item in self.active_authorizations
        )
        if len(authorization_ids) != len(set(authorization_ids)):
            raise ValueError("Active authorization IDs must be unique")
        for evidence in self.active_authorizations:
            if (
                evidence.authorization.granted_by
                != self.active_subject_id
            ):
                raise ValueError(
                    "Authorization must be granted by the active owner"
                )
        if set(self.memory.all_ids()) - set(item_ids):
            raise ValueError("Memory references unknown knowledge")
        expected_hypotheses = {
            item.knowledge_id
            for item in self.knowledge_items
            if item.knowledge_type is KnowledgeType.HYPOTHESIS
            and item.verification_status
            not in {
                VerificationStatus.INVALIDATED,
                VerificationStatus.SUPERSEDED,
            }
        }
        if set(self.open_hypotheses) != expected_hypotheses:
            raise ValueError("open_hypotheses is inconsistent")
        for conflict in self.unresolved_conflicts:
            if set(conflict.knowledge_ids) - set(item_ids):
                raise ValueError("Conflict references unknown knowledge")
            left, right = (
                items[item_id] for item_id in conflict.knowledge_ids
            )
            if (
                right.knowledge_id not in left.contradicted_by
                and left.knowledge_id not in right.contradicted_by
            ):
                raise ValueError(
                    "Conflict must be referenced by contradictory knowledge"
                )
        conflict_pairs = {
            frozenset(conflict.knowledge_ids)
            for conflict in self.unresolved_conflicts
        }
        for item in self.knowledge_items:
            for contradiction in item.contradicted_by:
                if frozenset((item.knowledge_id, contradiction)) not in (
                    conflict_pairs
                ):
                    raise ValueError(
                        "Contradiction lacks a visible conflict record"
                    )
        conflict_ids = tuple(
            item.conflict_id for item in self.unresolved_conflicts
        )
        if len(conflict_ids) != len(set(conflict_ids)):
            raise ValueError("Conflict IDs must be unique")
        constrained = {
            constraint.knowledge_id
            for constraint in self.retention_constraints
        }
        expected_constraints = {
            item.knowledge_id
            for item in self.knowledge_items
            if item.retention_class
            in {
                RetentionClass.KEEP_UNTIL_DATE,
                RetentionClass.LEGAL_HOLD,
            }
        }
        if constrained != expected_constraints:
            raise ValueError("retention_constraints is inconsistent")
        if len(self.retention_constraints) != len(constrained):
            raise ValueError("Retention constraints must be unique")
        actual_integrity = all(
            item.provenance is not None
            or item.knowledge_type is KnowledgeType.UNKNOWN
            for item in self.knowledge_items
        )
        if self.provenance_integrity is not actual_integrity:
            raise ValueError("provenance_integrity is inconsistent")

    def _validate_transition_history(self) -> None:
        transition_ids = tuple(
            item.transition_id for item in self.transitions
        )
        if len(transition_ids) != len(set(transition_ids)):
            raise ValueError("Transition IDs must be unique")
        previous_time: Optional[datetime] = None
        latest: Dict[str, Optional[KnowledgeItem]] = {}
        for transition in self.transitions:
            if transition.occurred_at > self.captured_at:
                raise ValueError(
                    "Transition cannot occur after snapshot capture"
                )
            if (
                previous_time is not None
                and transition.occurred_at < previous_time
            ):
                raise ValueError(
                    "Transition history must be chronological"
                )
            before = transition.previous_item
            after = transition.new_item
            knowledge_id = (
                before.knowledge_id
                if before is not None
                else after.knowledge_id
            )
            if knowledge_id in latest and latest[knowledge_id] != before:
                raise ValueError(
                    "Transition history must form an explicit state chain"
                )
            latest[knowledge_id] = after
            previous_time = transition.occurred_at
        current = {
            item.knowledge_id: item for item in self.knowledge_items
        }
        for knowledge_id, latest_item in latest.items():
            if latest_item is None:
                if knowledge_id in current:
                    raise ValueError(
                        "Deleted knowledge remains in the snapshot"
                    )
            elif current.get(knowledge_id) != latest_item:
                raise ValueError(
                    "Snapshot does not match its last transition"
                )

    def payload(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "captured_at": self.captured_at.isoformat(),
            "active_guardian_id": self.active_guardian_id,
            "active_subject_id": self.active_subject_id,
            "knowledge_snapshot_version": self.knowledge_snapshot_version,
            "applicable_memory_scope": [
                item.value for item in self.applicable_memory_scope
            ],
            "knowledge_items": [
                item.to_dict() for item in self.knowledge_items
            ],
            "memory": self.memory.to_dict(),
            "unresolved_conflicts": [
                item.to_dict() for item in self.unresolved_conflicts
            ],
            "open_hypotheses": list(self.open_hypotheses),
            "active_authorizations": [
                item.to_dict() for item in self.active_authorizations
            ],
            "retention_constraints": [
                item.to_dict() for item in self.retention_constraints
            ],
            "provenance_integrity": self.provenance_integrity,
            "transitions": [
                item.to_dict() for item in self.transitions
            ],
        }

    def calculate_hash(self) -> str:
        canonical = json.dumps(
            self.payload(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        result = self.payload()
        result["runtime_context_hash"] = self.runtime_context_hash
        return result

    @classmethod
    def create(
        cls,
        *,
        captured_at: datetime,
        active_guardian_id: Optional[str],
        active_subject_id: Optional[str],
        knowledge_snapshot_version: int,
        applicable_memory_scope: Tuple[MemoryScope, ...],
        knowledge_items: Tuple[KnowledgeItem, ...],
        memory: GuardianMemory,
        unresolved_conflicts: Tuple[KnowledgeConflict, ...],
        active_authorizations: Tuple[
            ArtifactAuthorizationEvidence,
            ...,
        ],
        transitions: Tuple[KnowledgeTransition, ...] = (),
    ) -> "GuardianRuntimeSnapshot":
        hypotheses = tuple(
            sorted(
                item.knowledge_id
                for item in knowledge_items
                if item.knowledge_type is KnowledgeType.HYPOTHESIS
                and item.verification_status
                not in {
                    VerificationStatus.INVALIDATED,
                    VerificationStatus.SUPERSEDED,
                }
            )
        )
        constraints = tuple(
            RetentionConstraint(
                knowledge_id=item.knowledge_id,
                retention_class=item.retention_class,
                binding_references=item.retention_basis_references,
            )
            for item in sorted(
                knowledge_items,
                key=lambda candidate: candidate.knowledge_id,
            )
            if item.retention_class
            in {
                RetentionClass.KEEP_UNTIL_DATE,
                RetentionClass.LEGAL_HOLD,
            }
        )
        kwargs = {
            "schema_version": "1.0",
            "captured_at": captured_at,
            "active_guardian_id": active_guardian_id,
            "active_subject_id": active_subject_id,
            "knowledge_snapshot_version": knowledge_snapshot_version,
            "applicable_memory_scope": applicable_memory_scope,
            "knowledge_items": tuple(
                sorted(
                    knowledge_items,
                    key=lambda item: item.knowledge_id,
                )
            ),
            "memory": memory,
            "unresolved_conflicts": tuple(
                sorted(
                    unresolved_conflicts,
                    key=lambda item: item.conflict_id,
                )
            ),
            "open_hypotheses": hypotheses,
            "active_authorizations": tuple(
                sorted(
                    active_authorizations,
                    key=lambda item: item.authorization_id,
                )
            ),
            "retention_constraints": constraints,
            "provenance_integrity": all(
                item.provenance is not None
                or item.knowledge_type is KnowledgeType.UNKNOWN
                for item in knowledge_items
            ),
            "transitions": transitions,
        }
        temporary = object.__new__(cls)
        for name, value in kwargs.items():
            object.__setattr__(temporary, name, value)
        context_hash = temporary.calculate_hash()
        return cls(runtime_context_hash=context_hash, **kwargs)

    @classmethod
    def unbound(cls, captured_at: datetime) -> "GuardianRuntimeSnapshot":
        return cls.create(
            captured_at=captured_at,
            active_guardian_id=None,
            active_subject_id=None,
            knowledge_snapshot_version=0,
            applicable_memory_scope=(),
            knowledge_items=(),
            memory=GuardianMemory(),
            unresolved_conflicts=(),
            active_authorizations=(),
        )


def replace_item(item: KnowledgeItem, **changes: Any) -> KnowledgeItem:
    return replace(item, **changes)


@dataclass(frozen=True)
class GuardianRuntimeContractContext:
    content: str
    source: Path
    version: str
    content_hash: str
    knowledge_types: Tuple[KnowledgeType, ...]
    verification_statuses: Tuple[VerificationStatus, ...]
    confidence_levels: Tuple[Confidence, ...]
    validity_states: Tuple[Validity, ...]
    retention_classes: Tuple[RetentionClass, ...]
    memory_scopes: Tuple[MemoryScope, ...]
    transition_types: Tuple[TransitionType, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Guardian Runtime contract content is empty")
        if not isinstance(self.source, Path):
            raise TypeError("Guardian Runtime source must be a Path")
        _text(self.version, "Guardian Runtime version")
        if (
            not isinstance(self.content_hash, str)
            or len(self.content_hash) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.content_hash
            )
        ):
            raise ValueError(
                "Guardian Runtime content_hash must be SHA-256"
            )
        for name, enum_type in (
            ("knowledge_types", KnowledgeType),
            ("verification_statuses", VerificationStatus),
            ("confidence_levels", Confidence),
            ("validity_states", Validity),
            ("retention_classes", RetentionClass),
            ("memory_scopes", MemoryScope),
            ("transition_types", TransitionType),
        ):
            value = getattr(self, name)
            if value != tuple(enum_type):
                raise ValueError(
                    "{} must contain every enum value once".format(name)
                )
