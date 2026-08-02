"""Immutable governance contracts for permitted runtime observation scope."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Optional, Tuple

from governance.authority import (
    AuthorityActorClass,
    AuthorityProvenance,
    AuthorityReviewStatus,
)


class RuntimeObservationEvent(str, Enum):
    EXECUTION_REQUEST_VALIDATED = "EXECUTION_REQUEST_VALIDATED"
    PROVIDER_INVOCATION_STARTED = "PROVIDER_INVOCATION_STARTED"
    PROVIDER_INVOCATION_COMPLETED = "PROVIDER_INVOCATION_COMPLETED"
    PROVIDER_TECHNICAL_ERROR = "PROVIDER_TECHNICAL_ERROR"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    OUTPUT_BOUNDARY_ACCEPTED = "OUTPUT_BOUNDARY_ACCEPTED"
    OUTPUT_BOUNDARY_REJECTED = "OUTPUT_BOUNDARY_REJECTED"
    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
    CONTROLLED_DEGRADATION = "CONTROLLED_DEGRADATION"
    RUNTIME_RESULT_RECORDED = "RUNTIME_RESULT_RECORDED"
    INCIDENT_EVIDENCE_BOUND = "INCIDENT_EVIDENCE_BOUND"


class RuntimeObservationCategory(str, Enum):
    SYSTEM_EXECUTION_LIFECYCLE = "SYSTEM_EXECUTION_LIFECYCLE"
    PROVIDER_TECHNICAL_STATUS = "PROVIDER_TECHNICAL_STATUS"
    OUTPUT_BOUNDARY_STATUS = "OUTPUT_BOUNDARY_STATUS"
    RUNTIME_CONTROL_STATUS = "RUNTIME_CONTROL_STATUS"
    INCIDENT_EVIDENCE_STATUS = "INCIDENT_EVIDENCE_STATUS"
    USER_BEHAVIOR = "USER_BEHAVIOR"
    USER_PROFILE = "USER_PROFILE"
    USER_CONTENT = "USER_CONTENT"
    USER_INTERACTION_PATTERN = "USER_INTERACTION_PATTERN"
    USAGE_STATISTICS = "USAGE_STATISTICS"


SYSTEM_OBSERVATION_CATEGORIES = (
    RuntimeObservationCategory.SYSTEM_EXECUTION_LIFECYCLE,
    RuntimeObservationCategory.PROVIDER_TECHNICAL_STATUS,
    RuntimeObservationCategory.OUTPUT_BOUNDARY_STATUS,
    RuntimeObservationCategory.RUNTIME_CONTROL_STATUS,
    RuntimeObservationCategory.INCIDENT_EVIDENCE_STATUS,
)

PROHIBITED_USER_OBSERVATION_CATEGORIES = (
    RuntimeObservationCategory.USER_BEHAVIOR,
    RuntimeObservationCategory.USER_PROFILE,
    RuntimeObservationCategory.USER_CONTENT,
    RuntimeObservationCategory.USER_INTERACTION_PATTERN,
    RuntimeObservationCategory.USAGE_STATISTICS,
)

RUNTIME_EVENT_CATEGORIES = MappingProxyType(
    {
        RuntimeObservationEvent.EXECUTION_REQUEST_VALIDATED:
            RuntimeObservationCategory.SYSTEM_EXECUTION_LIFECYCLE,
        RuntimeObservationEvent.PROVIDER_INVOCATION_STARTED:
            RuntimeObservationCategory.SYSTEM_EXECUTION_LIFECYCLE,
        RuntimeObservationEvent.PROVIDER_INVOCATION_COMPLETED:
            RuntimeObservationCategory.SYSTEM_EXECUTION_LIFECYCLE,
        RuntimeObservationEvent.PROVIDER_TECHNICAL_ERROR:
            RuntimeObservationCategory.PROVIDER_TECHNICAL_STATUS,
        RuntimeObservationEvent.PROVIDER_TIMEOUT:
            RuntimeObservationCategory.PROVIDER_TECHNICAL_STATUS,
        RuntimeObservationEvent.OUTPUT_BOUNDARY_ACCEPTED:
            RuntimeObservationCategory.OUTPUT_BOUNDARY_STATUS,
        RuntimeObservationEvent.OUTPUT_BOUNDARY_REJECTED:
            RuntimeObservationCategory.OUTPUT_BOUNDARY_STATUS,
        RuntimeObservationEvent.EXECUTION_BLOCKED:
            RuntimeObservationCategory.RUNTIME_CONTROL_STATUS,
        RuntimeObservationEvent.CONTROLLED_DEGRADATION:
            RuntimeObservationCategory.RUNTIME_CONTROL_STATUS,
        RuntimeObservationEvent.RUNTIME_RESULT_RECORDED:
            RuntimeObservationCategory.SYSTEM_EXECUTION_LIFECYCLE,
        RuntimeObservationEvent.INCIDENT_EVIDENCE_BOUND:
            RuntimeObservationCategory.INCIDENT_EVIDENCE_STATUS,
    }
)


class ObservationProfileApprovalStatus(str, Enum):
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ObservationSnapshotStatus(str, Enum):
    GOVERNANCE_PROFILE_VALIDATED = "GOVERNANCE_PROFILE_VALIDATED"


GOVERNANCE_PROFILE_ACTORS = (
    AuthorityActorClass.HUMAN_SOVEREIGN,
    AuthorityActorClass.OPERATIONAL_LEADERSHIP,
    AuthorityActorClass.TRUST_COUNCIL,
    AuthorityActorClass.USER_CONVENTION,
    AuthorityActorClass.STEWARDSHIP_STRUCTURE,
)


@dataclass(frozen=True)
class RuntimeObservationProfile:
    profile_id: str
    version: int
    name: str
    purpose: str
    observation_scope_reference: str
    explicitly_unobserved_areas: Tuple[RuntimeObservationCategory, ...]
    allowed_categories: Tuple[RuntimeObservationCategory, ...]
    prohibited_categories: Tuple[RuntimeObservationCategory, ...]
    responsibility_reference: str
    approval_status: ObservationProfileApprovalStatus
    approval_reference: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    change_actor_class: AuthorityActorClass
    change_authority_reference: str
    previous_profile_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.profile_id, "profile_id"),
            (self.name, "name"),
            (self.purpose, "purpose"),
            (self.observation_scope_reference, "observation_scope_reference"),
            (self.responsibility_reference, "responsibility_reference"),
            (self.change_authority_reference, "change_authority_reference"),
        ):
            _text(value, name)
        _positive_version(self.version, "version")
        _typed_unique_nonempty(
            self.explicitly_unobserved_areas,
            RuntimeObservationCategory,
            "explicitly_unobserved_areas",
        )
        _typed_unique_nonempty(
            self.allowed_categories,
            RuntimeObservationCategory,
            "allowed_categories",
        )
        _typed_unique_nonempty(
            self.prohibited_categories,
            RuntimeObservationCategory,
            "prohibited_categories",
        )
        _enum(
            self.approval_status,
            ObservationProfileApprovalStatus,
            "approval_status",
        )
        _approval_pair(self.approval_status, self.approval_reference)
        _review_pair(self.review_status, self.review_reference)
        _enum(self.change_actor_class, AuthorityActorClass, "change_actor_class")
        if self.previous_profile_reference is not None:
            _text(self.previous_profile_reference, "previous_profile_reference")
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeObservationScope:
    scope_id: str
    version: int
    observed_runtime_events: Tuple[RuntimeObservationEvent, ...]
    explicitly_unobserved_runtime_events: Tuple[RuntimeObservationEvent, ...]
    justification: str
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.scope_id, "scope_id")
        _positive_version(self.version, "version")
        _typed_unique(
            self.observed_runtime_events,
            RuntimeObservationEvent,
            "observed_runtime_events",
        )
        _typed_unique(
            self.explicitly_unobserved_runtime_events,
            RuntimeObservationEvent,
            "explicitly_unobserved_runtime_events",
        )
        _text(self.justification, "justification")
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeObservationGovernance:
    governance_id: str
    profile: RuntimeObservationProfile
    scope: RuntimeObservationScope
    previous_profile: Optional[RuntimeObservationProfile] = None

    def __post_init__(self) -> None:
        _text(self.governance_id, "governance_id")
        if not isinstance(self.profile, RuntimeObservationProfile):
            raise TypeError("profile has an invalid type")
        if not isinstance(self.scope, RuntimeObservationScope):
            raise TypeError("scope has an invalid type")
        if self.previous_profile is not None and not isinstance(
            self.previous_profile,
            RuntimeObservationProfile,
        ):
            raise TypeError("previous_profile has an invalid type")


@dataclass(frozen=True)
class RuntimeObservationSnapshot:
    snapshot_id: str
    profile: RuntimeObservationProfile
    scope: RuntimeObservationScope
    version: int
    status: ObservationSnapshotStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        if not isinstance(self.profile, RuntimeObservationProfile):
            raise TypeError("profile has an invalid type")
        if not isinstance(self.scope, RuntimeObservationScope):
            raise TypeError("scope has an invalid type")
        _positive_version(self.version, "version")
        _enum(self.status, ObservationSnapshotStatus, "status")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


class RuntimeObservationGovernanceValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class RuntimeObservationGovernanceValidator:
    """Validate governance metadata without observing any event."""

    def validate(
        self,
        governance: RuntimeObservationGovernance,
    ) -> RuntimeObservationGovernance:
        if not isinstance(governance, RuntimeObservationGovernance):
            raise TypeError("governance must be a RuntimeObservationGovernance")
        self._validate_identities(governance)
        self._validate_profile(governance.profile)
        self._validate_scope(governance.profile, governance.scope)
        self._validate_version(governance)
        return governance

    def create_snapshot(
        self,
        governance: RuntimeObservationGovernance,
        *,
        snapshot_id: str,
        review_status: AuthorityReviewStatus,
        review_reference: Optional[str],
        provenance: AuthorityProvenance,
    ) -> RuntimeObservationSnapshot:
        self.validate(governance)
        _text(snapshot_id, "snapshot_id")
        identities = self._identities(governance)
        if snapshot_id in identities:
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        if provenance != governance.profile.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "snapshot provenance differs")
        return RuntimeObservationSnapshot(
            snapshot_id=snapshot_id,
            profile=governance.profile,
            scope=governance.scope,
            version=governance.profile.version,
            status=ObservationSnapshotStatus.GOVERNANCE_PROFILE_VALIDATED,
            review_status=review_status,
            review_reference=review_reference,
            provenance=provenance,
        )

    @classmethod
    def _validate_identities(cls, governance) -> None:
        identities = cls._identities(governance)
        if len(identities) != len(set(identities)):
            _invalid("DUPLICATE_IDENTITY", "observation identities must be unique")

    @staticmethod
    def _identities(governance):
        identities = [
            governance.governance_id,
            governance.profile.profile_id,
            governance.scope.scope_id,
        ]
        if governance.previous_profile is not None:
            identities.append(governance.previous_profile.profile_id)
        return tuple(identities)

    @staticmethod
    def _validate_profile(profile) -> None:
        allowed = set(profile.allowed_categories)
        prohibited = set(profile.prohibited_categories)
        unobserved = set(profile.explicitly_unobserved_areas)
        system_categories = set(SYSTEM_OBSERVATION_CATEGORIES)
        user_categories = set(PROHIBITED_USER_OBSERVATION_CATEGORIES)
        if not allowed <= system_categories:
            _invalid(
                "USER_OBSERVATION_PROHIBITED",
                "only system observation categories may be allowed",
            )
        if allowed & prohibited:
            _invalid(
                "CONTRADICTORY_OBSERVATION_CATEGORIES",
                "allowed and prohibited observation categories overlap",
            )
        if prohibited != user_categories or unobserved != user_categories:
            _invalid(
                "USER_OBSERVATION_BOUNDARY_INCOMPLETE",
                "all user observation categories must remain prohibited",
            )
        if profile.change_actor_class not in GOVERNANCE_PROFILE_ACTORS:
            _invalid(
                "RUNTIME_PROFILE_CHANGE_PROHIBITED",
                "runtime and non-governance actors cannot change a profile",
            )

    @staticmethod
    def _validate_scope(profile, scope) -> None:
        if profile.observation_scope_reference != scope.scope_id:
            _invalid("SCOPE_REFERENCE_MISMATCH", "profile references another scope")
        if profile.version != scope.version:
            _invalid("SCOPE_VERSION_MISMATCH", "profile and scope versions differ")
        observed = set(scope.observed_runtime_events)
        unobserved = set(scope.explicitly_unobserved_runtime_events)
        if observed & unobserved:
            _invalid(
                "CONTRADICTORY_OBSERVATION_SCOPE",
                "observed and unobserved runtime events overlap",
            )
        if observed | unobserved != set(RuntimeObservationEvent):
            _invalid(
                "INCOMPLETE_OBSERVATION_SCOPE",
                "every runtime event must be explicitly classified",
            )
        allowed = set(profile.allowed_categories)
        if any(RUNTIME_EVENT_CATEGORIES[event] not in allowed for event in observed):
            _invalid(
                "OBSERVATION_CATEGORY_NOT_ALLOWED",
                "an observed runtime event has no allowed category",
            )
        if scope.provenance != profile.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "scope provenance differs")

    @staticmethod
    def _validate_version(governance) -> None:
        profile = governance.profile
        previous = governance.previous_profile
        if profile.version == 1:
            if profile.previous_profile_reference is not None or previous is not None:
                _invalid(
                    "UNEXPECTED_PREVIOUS_PROFILE",
                    "version one cannot reference a previous profile",
                )
            return
        if profile.previous_profile_reference is None or previous is None:
            _invalid(
                "PREVIOUS_PROFILE_REQUIRED",
                "later versions require the previous profile",
            )
        RuntimeObservationGovernanceValidator._validate_profile(previous)
        if profile.previous_profile_reference != previous.profile_id:
            _invalid(
                "PREVIOUS_PROFILE_REFERENCE_MISMATCH",
                "previous profile reference differs",
            )
        if previous.version + 1 != profile.version:
            _invalid(
                "PROFILE_VERSION_SEQUENCE_INVALID",
                "profile versions must be consecutive",
            )


def _invalid(code: str, message: str) -> None:
    raise RuntimeObservationGovernanceValidationError(code, message)


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _positive_version(value: object, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("{} must be a positive integer".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _typed_unique(values, item_type, name) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for value in values:
        if not isinstance(value, item_type):
            raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(values, item_type, name) -> None:
    _typed_unique(values, item_type, name)
    if not values:
        raise ValueError("{} must not be empty".format(name))


def _approval_pair(status, reference) -> None:
    if status is ObservationProfileApprovalStatus.APPROVED:
        if reference is None:
            raise ValueError("approved profile needs an approval reference")
    elif reference is not None:
        raise ValueError("only an approved profile may reference an approval")


def _review_pair(status, reference) -> None:
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed observation needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed observation may reference a review")


def _provenance(value) -> None:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
