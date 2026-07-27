import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Type


class SuccessionEventType(str, Enum):
    DEATH = "DEATH"
    INCAPACITY = "INCAPACITY"
    POWER_OF_ATTORNEY_EFFECTIVE = "POWER_OF_ATTORNEY_EFFECTIVE"
    BUSINESS_SUCCESSION = "BUSINESS_SUCCESSION"
    FOUNDATION_TRANSFER = "FOUNDATION_TRANSFER"
    CUSTOM = "CUSTOM"


class EventStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class VerificationStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class DirectiveStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"
    EXECUTED = "EXECUTED"


class BeneficiaryReferenceType(str, Enum):
    IDENTITY = "IDENTITY"
    ROLE = "ROLE"


class ResourceType(str, Enum):
    DOCUMENT = "DOCUMENT"
    DOCUMENT_GROUP = "DOCUMENT_GROUP"
    MEMORY = "MEMORY"
    PHOTO_COLLECTION = "PHOTO_COLLECTION"
    KEY = "KEY"
    INFORMATION = "INFORMATION"
    CUSTOM = "CUSTOM"


class AccessType(str, Enum):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    RECEIVE_COPY = "RECEIVE_COPY"
    DECRYPT = "DECRYPT"
    TRANSFER_CONTROL = "TRANSFER_CONTROL"


class ReleaseScope(str, Enum):
    EXPLICIT_RESOURCE_GRANTS = "EXPLICIT_RESOURCE_GRANTS"


class ReleaseDecision(str, Enum):
    NO_RELEASE = "NO_RELEASE"
    ELIGIBLE = "ELIGIBLE"


class EligibilityBlocker(str, Enum):
    DIRECTIVE_MISSING = "DIRECTIVE_MISSING"
    DIRECTIVE_NOT_ACTIVE = "DIRECTIVE_NOT_ACTIVE"
    DIRECTIVE_REVOKED = "DIRECTIVE_REVOKED"
    EVENT_NOT_OPEN = "EVENT_NOT_OPEN"
    EVENT_TYPE_MISMATCH = "EVENT_TYPE_MISMATCH"
    SUBJECT_MISMATCH = "SUBJECT_MISMATCH"
    VERIFICATION_NOT_MET = "VERIFICATION_NOT_MET"
    BENEFICIARY_MISSING = "BENEFICIARY_MISSING"
    RESOURCE_GRANT_MISSING = "RESOURCE_GRANT_MISSING"
    GRANT_BENEFICIARY_MISMATCH = "GRANT_BENEFICIARY_MISMATCH"
    RELEASE_CONDITION_OPEN = "RELEASE_CONDITION_OPEN"


class SuccessionAuditEventType(str, Enum):
    DIRECTIVE_CREATED = "DIRECTIVE_CREATED"
    DIRECTIVE_UPDATED = "DIRECTIVE_UPDATED"
    DIRECTIVE_REVOKED = "DIRECTIVE_REVOKED"
    VERIFICATION_STARTED = "VERIFICATION_STARTED"
    VERIFICATION_STATUS_CHANGED = "VERIFICATION_STATUS_CHANGED"
    RELEASE_ELIGIBILITY_EVALUATED = "RELEASE_ELIGIBILITY_EVALUATED"
    RELEASE_BLOCKED = "RELEASE_BLOCKED"
    RELEASE_AUTHORIZED = "RELEASE_AUTHORIZED"
    RELEASE_STARTED = "RELEASE_STARTED"
    RELEASE_COMPLETED = "RELEASE_COMPLETED"
    RELEASE_FAILED = "RELEASE_FAILED"


class AuditActorType(str, Enum):
    USER = "USER"
    EXTERNAL_VERIFIER = "EXTERNAL_VERIFIER"
    SYSTEM = "SYSTEM"


def _text(
    value: object,
    field_name: str,
    maximum: int = 1000,
) -> str:
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
    if len(value) > maximum or any(ord(char) < 32 for char in value):
        raise ValueError("{} contains invalid content".format(field_name))
    return value


def _optional_text(
    value: object,
    field_name: str,
    maximum: int = 1000,
) -> Optional[str]:
    if value is None:
        return None
    return _text(value, field_name, maximum)


def _aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


def _optional_aware(
    value: object,
    field_name: str,
) -> Optional[datetime]:
    if value is None:
        return None
    return _aware(value, field_name)


def _enum(value: object, expected: Type[Enum], field_name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(
            "{} must be {}".format(field_name, expected.__name__)
        )


def _identifiers(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    for item in value:
        _text(item, "{} item".format(field_name), maximum=255)
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(field_name))
    return value


def _reference(value: object, field_name: str) -> str:
    reference = _text(value, field_name, maximum=1000)
    lowered = reference.lower()
    if lowered.startswith("data:") or lowered.startswith("base64:"):
        raise ValueError(
            "{} must reference content, not embed it".format(field_name)
        )
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*:\S+", reference) is None:
        raise ValueError(
            "{} must be a logical reference with a scheme".format(
                field_name
            )
        )
    return reference


def _references(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    for item in value:
        _reference(item, "{} item".format(field_name))
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(field_name))
    return value


@dataclass(frozen=True)
class BeneficiaryReference:
    beneficiary_id: str
    reference_type: BeneficiaryReferenceType
    reference_value: str

    def __post_init__(self) -> None:
        _text(self.beneficiary_id, "beneficiary_id", maximum=255)
        _enum(
            self.reference_type,
            BeneficiaryReferenceType,
            "reference_type",
        )
        _reference(self.reference_value, "reference_value")

    def to_dict(self) -> Dict[str, str]:
        return {
            "beneficiary_id": self.beneficiary_id,
            "reference_type": self.reference_type.value,
            "reference_value": self.reference_value,
        }


@dataclass(frozen=True)
class ResourceGrant:
    grant_id: str
    resource_reference: str
    resource_type: ResourceType
    access_type: AccessType
    beneficiary_reference_id: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    def __post_init__(self) -> None:
        _text(self.grant_id, "grant_id", maximum=255)
        _reference(
            self.resource_reference,
            "resource_reference",
        )
        _enum(self.resource_type, ResourceType, "resource_type")
        _enum(self.access_type, AccessType, "access_type")
        _text(
            self.beneficiary_reference_id,
            "beneficiary_reference_id",
            maximum=255,
        )
        _optional_aware(self.valid_from, "valid_from")
        _optional_aware(self.valid_until, "valid_until")
        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until < self.valid_from
        ):
            raise ValueError("valid_until must not precede valid_from")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "resource_reference": self.resource_reference,
            "resource_type": self.resource_type.value,
            "access_type": self.access_type.value,
            "beneficiary_reference_id": self.beneficiary_reference_id,
            "valid_from": (
                self.valid_from.isoformat()
                if self.valid_from is not None
                else None
            ),
            "valid_until": (
                self.valid_until.isoformat()
                if self.valid_until is not None
                else None
            ),
        }


@dataclass(frozen=True)
class ReleaseCondition:
    condition_id: str
    required_verification_status: VerificationStatus
    verification_reference_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.condition_id, "condition_id", maximum=255)
        _enum(
            self.required_verification_status,
            VerificationStatus,
            "required_verification_status",
        )
        if self.required_verification_status is not VerificationStatus.VERIFIED:
            raise ValueError(
                "release conditions must require VERIFIED status"
            )
        _references(
            self.verification_reference_ids,
            "verification_reference_ids",
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "required_verification_status": (
                self.required_verification_status.value
            ),
            "verification_reference_ids": list(
                self.verification_reference_ids
            ),
        }


@dataclass(frozen=True)
class SuccessionEvent:
    event_id: str
    event_type: SuccessionEventType
    subject_id: str
    status: EventStatus
    reported_at: datetime
    verification_status: VerificationStatus
    evidence_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.event_id, "event_id", maximum=255)
        _enum(self.event_type, SuccessionEventType, "event_type")
        _text(self.subject_id, "subject_id", maximum=255)
        _enum(self.status, EventStatus, "status")
        _aware(self.reported_at, "reported_at")
        _enum(
            self.verification_status,
            VerificationStatus,
            "verification_status",
        )
        _references(self.evidence_references, "evidence_references")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "subject_id": self.subject_id,
            "status": self.status.value,
            "reported_at": self.reported_at.isoformat(),
            "verification_status": self.verification_status.value,
            "evidence_references": list(self.evidence_references),
        }


@dataclass(frozen=True)
class SuccessionDirective:
    directive_id: str
    owner_id: str
    event_type: SuccessionEventType
    beneficiary: Optional[BeneficiaryReference]
    resource_grants: Tuple[ResourceGrant, ...]
    release_scope: ReleaseScope
    release_conditions: Tuple[ReleaseCondition, ...]
    required_verification_status: VerificationStatus
    status: DirectiveStatus
    revision: int
    created_at: datetime
    updated_at: datetime
    revoked_at: Optional[datetime] = None
    previous_revision: Optional[int] = None
    audit_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.directive_id, "directive_id", maximum=255)
        _text(self.owner_id, "owner_id", maximum=255)
        _enum(self.event_type, SuccessionEventType, "event_type")
        if self.beneficiary is not None and not isinstance(
            self.beneficiary,
            BeneficiaryReference,
        ):
            raise TypeError(
                "beneficiary must be BeneficiaryReference or None"
            )
        if not isinstance(self.resource_grants, tuple) or not all(
            isinstance(item, ResourceGrant)
            for item in self.resource_grants
        ):
            raise TypeError(
                "resource_grants must contain ResourceGrant values"
            )
        grant_ids = tuple(item.grant_id for item in self.resource_grants)
        resource_references = tuple(
            item.resource_reference for item in self.resource_grants
        )
        if len(grant_ids) != len(set(grant_ids)):
            raise ValueError("resource_grants must have unique grant IDs")
        if len(resource_references) != len(set(resource_references)):
            raise ValueError(
                "resource_grants must have unique resource references"
            )
        _enum(self.release_scope, ReleaseScope, "release_scope")
        if not isinstance(self.release_conditions, tuple) or not all(
            isinstance(item, ReleaseCondition)
            for item in self.release_conditions
        ):
            raise TypeError(
                "release_conditions must contain ReleaseCondition values"
            )
        condition_ids = tuple(
            item.condition_id for item in self.release_conditions
        )
        if len(condition_ids) != len(set(condition_ids)):
            raise ValueError(
                "release_conditions must have unique condition IDs"
            )
        _enum(
            self.required_verification_status,
            VerificationStatus,
            "required_verification_status",
        )
        if self.required_verification_status is not VerificationStatus.VERIFIED:
            raise ValueError(
                "succession release must require VERIFIED status"
            )
        _enum(self.status, DirectiveStatus, "status")
        if not isinstance(self.revision, int) or isinstance(
            self.revision,
            bool,
        ):
            raise TypeError("revision must be an integer")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        _aware(self.created_at, "created_at")
        _aware(self.updated_at, "updated_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not precede created_at")
        _optional_aware(self.revoked_at, "revoked_at")
        if (
            self.status is DirectiveStatus.REVOKED
            and self.revoked_at is None
        ):
            raise ValueError("REVOKED directive requires revoked_at")
        if (
            self.status is not DirectiveStatus.REVOKED
            and self.revoked_at is not None
        ):
            raise ValueError("revoked_at is only valid for REVOKED")
        if self.previous_revision is not None:
            if not isinstance(self.previous_revision, int) or isinstance(
                self.previous_revision,
                bool,
            ):
                raise TypeError("previous_revision must be an integer")
            if self.previous_revision != self.revision - 1:
                raise ValueError(
                    "previous_revision must immediately precede revision"
                )
        elif self.revision != 1:
            raise ValueError(
                "revision after 1 requires previous_revision"
            )
        _references(self.audit_references, "audit_references")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directive_id": self.directive_id,
            "owner_id": self.owner_id,
            "event_type": self.event_type.value,
            "beneficiary": (
                self.beneficiary.to_dict()
                if self.beneficiary is not None
                else None
            ),
            "resource_grants": [
                item.to_dict() for item in self.resource_grants
            ],
            "release_scope": self.release_scope.value,
            "release_conditions": [
                item.to_dict() for item in self.release_conditions
            ],
            "required_verification_status": (
                self.required_verification_status.value
            ),
            "status": self.status.value,
            "revision": self.revision,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "revoked_at": (
                self.revoked_at.isoformat()
                if self.revoked_at is not None
                else None
            ),
            "previous_revision": self.previous_revision,
            "audit_references": list(self.audit_references),
        }


@dataclass(frozen=True)
class SuccessionDirectiveHistory:
    revisions: Tuple[SuccessionDirective, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.revisions, tuple) or not self.revisions:
            raise ValueError("revisions must be a non-empty tuple")
        if not all(
            isinstance(item, SuccessionDirective)
            for item in self.revisions
        ):
            raise TypeError(
                "revisions must contain SuccessionDirective values"
            )
        first = self.revisions[0]
        if first.revision != 1:
            raise ValueError("directive history must begin at revision 1")
        for index, current in enumerate(self.revisions):
            if current.directive_id != first.directive_id:
                raise ValueError(
                    "directive history cannot mix directive IDs"
                )
            if current.owner_id != first.owner_id:
                raise ValueError(
                    "directive history cannot change owner"
                )
            if index == 0:
                continue
            previous = self.revisions[index - 1]
            if previous.status in {
                DirectiveStatus.REVOKED,
                DirectiveStatus.EXECUTED,
            }:
                raise ValueError(
                    "terminal or revoked directive cannot be revised"
                )
            if (
                current.revision != previous.revision + 1
                or current.previous_revision != previous.revision
            ):
                raise ValueError(
                    "directive revisions must be contiguous"
                )
            if current.updated_at < previous.updated_at:
                raise ValueError(
                    "directive revisions must be chronological"
                )
            if current.created_at != first.created_at:
                raise ValueError(
                    "directive revisions must preserve created_at"
                )

    @property
    def current(self) -> SuccessionDirective:
        return self.revisions[-1]

    def append(
        self,
        revision: SuccessionDirective,
    ) -> "SuccessionDirectiveHistory":
        return SuccessionDirectiveHistory(self.revisions + (revision,))


@dataclass(frozen=True)
class ReleaseEligibility:
    decision: ReleaseDecision
    eligible: bool
    blocking_reasons: Tuple[EligibilityBlocker, ...]
    open_conditions: Tuple[str, ...]
    directive_id: Optional[str]
    event_id: str
    evaluated_at: datetime
    authorized_actions: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _enum(self.decision, ReleaseDecision, "decision")
        if not isinstance(self.eligible, bool):
            raise TypeError("eligible must be a bool")
        if not isinstance(self.blocking_reasons, tuple) or not all(
            isinstance(item, EligibilityBlocker)
            for item in self.blocking_reasons
        ):
            raise TypeError(
                "blocking_reasons must contain EligibilityBlocker values"
            )
        if len(self.blocking_reasons) != len(set(self.blocking_reasons)):
            raise ValueError("blocking_reasons must be unique")
        _identifiers(self.open_conditions, "open_conditions")
        _optional_text(self.directive_id, "directive_id", maximum=255)
        _text(self.event_id, "event_id", maximum=255)
        _aware(self.evaluated_at, "evaluated_at")
        _identifiers(self.authorized_actions, "authorized_actions")
        if self.authorized_actions:
            raise ValueError(
                "eligibility cannot authorize technical actions"
            )
        if self.eligible != (self.decision is ReleaseDecision.ELIGIBLE):
            raise ValueError("eligible and decision are inconsistent")
        if self.eligible and (
            self.blocking_reasons or self.open_conditions
        ):
            raise ValueError(
                "eligible result cannot contain blockers"
            )
        if not self.eligible and not self.blocking_reasons:
            raise ValueError(
                "NO_RELEASE result requires a blocking reason"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "eligible": self.eligible,
            "blocking_reasons": [
                item.value for item in self.blocking_reasons
            ],
            "open_conditions": list(self.open_conditions),
            "directive_id": self.directive_id,
            "event_id": self.event_id,
            "evaluated_at": self.evaluated_at.isoformat(),
            "authorized_actions": [],
        }


def evaluate_release_eligibility(
    directive: Optional[SuccessionDirective],
    event: SuccessionEvent,
    evaluated_at: datetime,
) -> ReleaseEligibility:
    if directive is not None and not isinstance(
        directive,
        SuccessionDirective,
    ):
        raise TypeError(
            "directive must be SuccessionDirective or None"
        )
    if not isinstance(event, SuccessionEvent):
        raise TypeError("event must be SuccessionEvent")
    _aware(evaluated_at, "evaluated_at")

    if directive is None:
        return ReleaseEligibility(
            decision=ReleaseDecision.NO_RELEASE,
            eligible=False,
            blocking_reasons=(EligibilityBlocker.DIRECTIVE_MISSING,),
            open_conditions=(),
            directive_id=None,
            event_id=event.event_id,
            evaluated_at=evaluated_at,
        )

    blockers = []
    open_conditions = []
    if directive.status is DirectiveStatus.REVOKED:
        blockers.append(EligibilityBlocker.DIRECTIVE_REVOKED)
    elif directive.status is not DirectiveStatus.ACTIVE:
        blockers.append(EligibilityBlocker.DIRECTIVE_NOT_ACTIVE)
    if event.status is not EventStatus.OPEN:
        blockers.append(EligibilityBlocker.EVENT_NOT_OPEN)
    if event.event_type is not directive.event_type:
        blockers.append(EligibilityBlocker.EVENT_TYPE_MISMATCH)
    if event.subject_id != directive.owner_id:
        blockers.append(EligibilityBlocker.SUBJECT_MISMATCH)
    if (
        event.verification_status
        is not directive.required_verification_status
    ):
        blockers.append(EligibilityBlocker.VERIFICATION_NOT_MET)
    if directive.beneficiary is None:
        blockers.append(EligibilityBlocker.BENEFICIARY_MISSING)
    if not directive.resource_grants:
        blockers.append(EligibilityBlocker.RESOURCE_GRANT_MISSING)
    if directive.beneficiary is not None and any(
        grant.beneficiary_reference_id
        != directive.beneficiary.beneficiary_id
        for grant in directive.resource_grants
    ):
        blockers.append(
            EligibilityBlocker.GRANT_BENEFICIARY_MISMATCH
        )
    for condition in directive.release_conditions:
        if (
            event.verification_status
            is not condition.required_verification_status
        ):
            open_conditions.append(condition.condition_id)
    if open_conditions:
        blockers.append(EligibilityBlocker.RELEASE_CONDITION_OPEN)

    ordered_blockers = tuple(
        blocker for blocker in EligibilityBlocker if blocker in blockers
    )
    ordered_conditions = tuple(sorted(open_conditions))
    eligible = not ordered_blockers
    return ReleaseEligibility(
        decision=(
            ReleaseDecision.ELIGIBLE
            if eligible
            else ReleaseDecision.NO_RELEASE
        ),
        eligible=eligible,
        blocking_reasons=ordered_blockers,
        open_conditions=ordered_conditions,
        directive_id=directive.directive_id,
        event_id=event.event_id,
        evaluated_at=evaluated_at,
    )


@dataclass(frozen=True)
class SuccessionAuditEvent:
    audit_event_id: str
    sequence: int
    event_type: SuccessionAuditEventType
    directive_id: str
    occurred_at: datetime
    actor_type: AuditActorType
    actor_reference: str
    reason_code: str
    reference_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.audit_event_id, "audit_event_id", maximum=255)
        if not isinstance(self.sequence, int) or isinstance(
            self.sequence,
            bool,
        ):
            raise TypeError("sequence must be an integer")
        if self.sequence < 1:
            raise ValueError("sequence must be positive")
        _enum(self.event_type, SuccessionAuditEventType, "event_type")
        _text(self.directive_id, "directive_id", maximum=255)
        _aware(self.occurred_at, "occurred_at")
        _enum(self.actor_type, AuditActorType, "actor_type")
        _reference(self.actor_reference, "actor_reference")
        _text(self.reason_code, "reason_code", maximum=128)
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", self.reason_code) is None:
            raise ValueError(
                "reason_code must be a stable uppercase identifier"
            )
        _references(self.reference_ids, "reference_ids")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_event_id": self.audit_event_id,
            "sequence": self.sequence,
            "event_type": self.event_type.value,
            "directive_id": self.directive_id,
            "occurred_at": self.occurred_at.isoformat(),
            "actor_type": self.actor_type.value,
            "actor_reference": self.actor_reference,
            "reason_code": self.reason_code,
            "reference_ids": list(self.reference_ids),
        }


@dataclass(frozen=True)
class SuccessionAuditTrail:
    events: Tuple[SuccessionAuditEvent, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.events, tuple) or not all(
            isinstance(item, SuccessionAuditEvent)
            for item in self.events
        ):
            raise TypeError(
                "events must contain SuccessionAuditEvent values"
            )
        ids = tuple(item.audit_event_id for item in self.events)
        if len(ids) != len(set(ids)):
            raise ValueError("audit event IDs must be unique")
        for index, event in enumerate(self.events, start=1):
            if event.sequence != index:
                raise ValueError(
                    "audit event sequence must be contiguous"
                )
            if (
                index > 1
                and event.occurred_at < self.events[index - 2].occurred_at
            ):
                raise ValueError(
                    "audit events must be chronological"
                )

    def append(
        self,
        event: SuccessionAuditEvent,
    ) -> "SuccessionAuditTrail":
        if not isinstance(event, SuccessionAuditEvent):
            raise TypeError("event must be SuccessionAuditEvent")
        return SuccessionAuditTrail(self.events + (event,))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "events": [event.to_dict() for event in self.events],
        }
