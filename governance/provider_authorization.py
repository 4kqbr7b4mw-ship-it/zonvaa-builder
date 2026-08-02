"""Immutable provider-authorization evidence without execution authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from governance.authority import (
    ActorResponsibilityBoundary,
    AuthorityActorClass,
    AuthorityCapability,
    AuthorityControlLevel,
    AuthorityDefinition,
    AuthorityExercise,
    AuthorityProvenance,
    AuthorityReviewStatus,
    AuthorityType,
    GuardianAuthorityModel,
    GuardianAuthorityModelValidator,
)


class ProviderType(str, Enum):
    INTERNAL_SYSTEM_COMPONENT = "INTERNAL_SYSTEM_COMPONENT"
    EXTERNAL_SERVICE_PROVIDER = "EXTERNAL_SERVICE_PROVIDER"
    PROFESSIONAL_SERVICE_PROVIDER = "PROFESSIONAL_SERVICE_PROVIDER"
    HUMAN_REVIEW_PROVIDER = "HUMAN_REVIEW_PROVIDER"
    MODEL_PROVIDER = "MODEL_PROVIDER"
    RESEARCH_PROVIDER = "RESEARCH_PROVIDER"
    TOOL_PROVIDER = "TOOL_PROVIDER"
    OTHER_DECLARED_PROVIDER = "OTHER_DECLARED_PROVIDER"


class ProviderIdentityVerificationStatus(str, Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    EVIDENCE_PROVIDED = "EVIDENCE_PROVIDED"
    VERIFIED_DECLARED = "VERIFIED_DECLARED"


class ProviderAuthorizationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class AuthorizationDecisionType(str, Enum):
    PROPOSE = "PROPOSE"
    AUTHORIZE = "AUTHORIZE"
    REJECT = "REJECT"
    SUSPEND = "SUSPEND"
    REVOKE = "REVOKE"
    EXPIRE = "EXPIRE"
    RESTORE = "RESTORE"


class AuthorizationUncertaintyStatus(str, Enum):
    CERTAIN = "CERTAIN"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"


class ProviderAuthorizationPackageCapability(str, Enum):
    DESCRIBE_AUTHORIZATION = "DESCRIBE_AUTHORIZATION"
    AUTHORIZE_PROVIDER = "AUTHORIZE_PROVIDER"
    ACTIVATE_CAPABILITY = "ACTIVATE_CAPABILITY"
    SELECT_PROVIDER = "SELECT_PROVIDER"
    EVALUATE_TRUST = "EVALUATE_TRUST"
    ACTIVATE_RUNTIME = "ACTIVATE_RUNTIME"
    CLASSIFY_REQUEST = "CLASSIFY_REQUEST"
    GENERATE_ANSWER = "GENERATE_ANSWER"
    ACQUIRE_SOURCE = "ACQUIRE_SOURCE"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    START_WORKFLOW = "START_WORKFLOW"
    MODIFY_STATE = "MODIFY_STATE"
    PERSIST_AUTHORIZATION = "PERSIST_AUTHORIZATION"


NON_EXECUTING_PROVIDER_AUTHORIZATION_CAPABILITIES = (
    ProviderAuthorizationPackageCapability.DESCRIBE_AUTHORIZATION,
)


@dataclass(frozen=True)
class ProviderIdentity:
    provider_id: str
    provider_type: ProviderType
    identity_reference: str
    actor_class: AuthorityActorClass
    responsibility_scope: str
    supported_authority_types: Tuple[AuthorityType, ...]
    origin_evidence_reference: str
    identity_verification_status: ProviderIdentityVerificationStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    uncertainty_status: AuthorizationUncertaintyStatus
    provenance: AuthorityProvenance
    previous_provider_id: Optional[str] = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.provider_id, "provider_id"),
            (self.identity_reference, "identity_reference"),
            (self.responsibility_scope, "responsibility_scope"),
            (self.origin_evidence_reference, "origin_evidence_reference"),
        ):
            _text(value, name)
        _enum(self.provider_type, ProviderType, "provider_type")
        _enum(self.actor_class, AuthorityActorClass, "actor_class")
        _typed_unique_nonempty(
            self.supported_authority_types,
            AuthorityType,
            "supported_authority_types",
        )
        _enum(
            self.identity_verification_status,
            ProviderIdentityVerificationStatus,
            "identity_verification_status",
        )
        _enum(self.review_status, AuthorityReviewStatus, "review_status")
        if self.review_reference is not None:
            _text(self.review_reference, "review_reference")
        _aware(self.valid_from, "valid_from")
        if self.valid_until is not None:
            _aware(self.valid_until, "valid_until")
            if self.valid_until <= self.valid_from:
                raise ValueError("valid_until must be after valid_from")
        _enum(
            self.uncertainty_status,
            AuthorizationUncertaintyStatus,
            "uncertainty_status",
        )
        _provenance(self.provenance)
        if self.previous_provider_id is not None:
            _text(self.previous_provider_id, "previous_provider_id")


@dataclass(frozen=True)
class ProviderAuthorizationGrant:
    authorization_id: str
    provider_reference: str
    authority_reference: str
    allowed_capabilities: Tuple[AuthorityCapability, ...]
    forbidden_capabilities: Tuple[AuthorityCapability, ...]
    responsibility_boundary_reference: str
    status: ProviderAuthorizationStatus
    valid_from: datetime
    valid_until: Optional[datetime]
    control_levels: Tuple[AuthorityControlLevel, ...]
    required_joint_actor_classes: Tuple[AuthorityActorClass, ...]
    delegable: bool
    revocable: bool
    granting_authority_reference: str
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    uncertainty_status: AuthorizationUncertaintyStatus
    provenance: AuthorityProvenance
    previous_authorization_id: Optional[str] = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.authorization_id, "authorization_id"),
            (self.provider_reference, "provider_reference"),
            (self.authority_reference, "authority_reference"),
            (
                self.responsibility_boundary_reference,
                "responsibility_boundary_reference",
            ),
            (self.granting_authority_reference, "granting_authority_reference"),
        ):
            _text(value, name)
        _typed_unique(
            self.allowed_capabilities,
            AuthorityCapability,
            "allowed_capabilities",
        )
        _typed_unique(
            self.forbidden_capabilities,
            AuthorityCapability,
            "forbidden_capabilities",
        )
        _enum(self.status, ProviderAuthorizationStatus, "status")
        _aware(self.valid_from, "valid_from")
        if self.valid_until is not None:
            _aware(self.valid_until, "valid_until")
            if self.valid_until <= self.valid_from:
                raise ValueError("valid_until must be after valid_from")
        _typed_unique_nonempty(
            self.control_levels,
            AuthorityControlLevel,
            "control_levels",
        )
        _typed_unique(
            self.required_joint_actor_classes,
            AuthorityActorClass,
            "required_joint_actor_classes",
        )
        for value, name in (
            (self.delegable, "delegable"),
            (self.revocable, "revocable"),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be a bool".format(name))
        _enum(self.review_status, AuthorityReviewStatus, "review_status")
        if self.review_reference is not None:
            _text(self.review_reference, "review_reference")
        _enum(
            self.uncertainty_status,
            AuthorizationUncertaintyStatus,
            "uncertainty_status",
        )
        _provenance(self.provenance)
        if self.previous_authorization_id is not None:
            _text(self.previous_authorization_id, "previous_authorization_id")


@dataclass(frozen=True)
class DecidingActorReference:
    actor_reference: str
    actor_class: AuthorityActorClass

    def __post_init__(self) -> None:
        _text(self.actor_reference, "actor_reference")
        _enum(self.actor_class, AuthorityActorClass, "actor_class")


@dataclass(frozen=True)
class AuthorizationDecisionEvidence:
    decision_evidence_id: str
    authorization_reference: str
    decision_type: AuthorizationDecisionType
    decision_reason: str
    checked_authority_rule_references: Tuple[str, ...]
    checked_responsibility_boundary_references: Tuple[str, ...]
    detected_conflicts: Tuple[str, ...]
    required_control_levels: Tuple[AuthorityControlLevel, ...]
    deciding_actors: Tuple[DecidingActorReference, ...]
    decided_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.decision_evidence_id, "decision_evidence_id")
        _text(self.authorization_reference, "authorization_reference")
        _enum(self.decision_type, AuthorizationDecisionType, "decision_type")
        _text(self.decision_reason, "decision_reason")
        _strings(
            self.checked_authority_rule_references,
            "checked_authority_rule_references",
            required=True,
        )
        _strings(
            self.checked_responsibility_boundary_references,
            "checked_responsibility_boundary_references",
            required=True,
        )
        _strings(self.detected_conflicts, "detected_conflicts", required=False)
        _typed_unique_nonempty(
            self.required_control_levels,
            AuthorityControlLevel,
            "required_control_levels",
        )
        _typed_tuple(self.deciding_actors, DecidingActorReference, "deciding_actors")
        if not self.deciding_actors:
            raise ValueError("deciding_actors must not be empty")
        references = tuple(item.actor_reference for item in self.deciding_actors)
        if len(references) != len(set(references)):
            raise ValueError("deciding actor references must be unique")
        _aware(self.decided_at, "decided_at")
        _enum(self.review_status, AuthorityReviewStatus, "review_status")
        if self.review_reference is not None:
            _text(self.review_reference, "review_reference")
        _provenance(self.provenance)


@dataclass(frozen=True)
class AuthorizationRevocationEvidence:
    evidence_id: str
    authorization_reference: str
    reason: str
    effective_at: datetime
    deciding_authority_reference: str
    control_levels: Tuple[AuthorityControlLevel, ...]
    previous_status: ProviderAuthorizationStatus
    resulting_status: ProviderAuthorizationStatus
    provenance: AuthorityProvenance
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]

    def __post_init__(self) -> None:
        _lifecycle_fields(self)


@dataclass(frozen=True)
class AuthorizationSuspensionEvidence:
    evidence_id: str
    authorization_reference: str
    reason: str
    effective_at: datetime
    deciding_authority_reference: str
    control_levels: Tuple[AuthorityControlLevel, ...]
    previous_status: ProviderAuthorizationStatus
    resulting_status: ProviderAuthorizationStatus
    provenance: AuthorityProvenance
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]

    def __post_init__(self) -> None:
        _lifecycle_fields(self)


@dataclass(frozen=True)
class AuthorizationExpirationEvidence:
    evidence_id: str
    authorization_reference: str
    reason: str
    effective_at: datetime
    deciding_authority_reference: str
    control_levels: Tuple[AuthorityControlLevel, ...]
    previous_status: ProviderAuthorizationStatus
    resulting_status: ProviderAuthorizationStatus
    provenance: AuthorityProvenance
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]

    def __post_init__(self) -> None:
        _lifecycle_fields(self)


@dataclass(frozen=True)
class AuthorizationRestorationEvidence:
    evidence_id: str
    authorization_reference: str
    reason: str
    effective_at: datetime
    deciding_authority_reference: str
    control_levels: Tuple[AuthorityControlLevel, ...]
    previous_status: ProviderAuthorizationStatus
    resulting_status: ProviderAuthorizationStatus
    provenance: AuthorityProvenance
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]

    def __post_init__(self) -> None:
        _lifecycle_fields(self)


@dataclass(frozen=True)
class ProviderAuthorizationResolutionSnapshot:
    snapshot_id: str
    provider: ProviderIdentity
    authorized: Tuple[ProviderAuthorizationGrant, ...]
    suspended: Tuple[ProviderAuthorizationGrant, ...]
    revoked: Tuple[ProviderAuthorizationGrant, ...]
    expired: Tuple[ProviderAuthorizationGrant, ...]
    allowed_capabilities: Tuple[AuthorityCapability, ...]
    forbidden_capabilities: Tuple[AuthorityCapability, ...]
    control_levels: Tuple[AuthorityControlLevel, ...]
    responsibility_boundaries: Tuple[ActorResponsibilityBoundary, ...]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    uncertainties: Tuple[AuthorizationUncertaintyStatus, ...]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        if not isinstance(self.provider, ProviderIdentity):
            raise TypeError("provider must be a ProviderIdentity")
        for values, name in (
            (self.authorized, "authorized"),
            (self.suspended, "suspended"),
            (self.revoked, "revoked"),
            (self.expired, "expired"),
        ):
            _typed_tuple(values, ProviderAuthorizationGrant, name)
        _typed_unique(
            self.allowed_capabilities,
            AuthorityCapability,
            "allowed_capabilities",
        )
        _typed_unique(
            self.forbidden_capabilities,
            AuthorityCapability,
            "forbidden_capabilities",
        )
        _typed_unique(
            self.control_levels,
            AuthorityControlLevel,
            "control_levels",
        )
        _typed_tuple(
            self.responsibility_boundaries,
            ActorResponsibilityBoundary,
            "responsibility_boundaries",
        )
        _enum(self.review_status, AuthorityReviewStatus, "review_status")
        if self.review_reference is not None:
            _text(self.review_reference, "review_reference")
        _typed_unique(
            self.uncertainties,
            AuthorizationUncertaintyStatus,
            "uncertainties",
        )
        _provenance(self.provenance)


@dataclass(frozen=True)
class GuardianProviderAuthorizationPackage:
    package_id: str
    authority_model: GuardianAuthorityModel
    providers: Tuple[ProviderIdentity, ...]
    authorizations: Tuple[ProviderAuthorizationGrant, ...]
    decisions: Tuple[AuthorizationDecisionEvidence, ...]
    revocations: Tuple[AuthorizationRevocationEvidence, ...] = ()
    suspensions: Tuple[AuthorizationSuspensionEvidence, ...] = ()
    expirations: Tuple[AuthorizationExpirationEvidence, ...] = ()
    restorations: Tuple[AuthorizationRestorationEvidence, ...] = ()
    snapshots: Tuple[ProviderAuthorizationResolutionSnapshot, ...] = ()
    provenance: Optional[AuthorityProvenance] = None
    capabilities: Tuple[ProviderAuthorizationPackageCapability, ...] = (
        ProviderAuthorizationPackageCapability.DESCRIBE_AUTHORIZATION,
    )

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(self.authority_model, GuardianAuthorityModel):
            raise TypeError("authority_model must be a GuardianAuthorityModel")
        for values, item_type, name in (
            (self.providers, ProviderIdentity, "providers"),
            (self.authorizations, ProviderAuthorizationGrant, "authorizations"),
            (self.decisions, AuthorizationDecisionEvidence, "decisions"),
            (self.revocations, AuthorizationRevocationEvidence, "revocations"),
            (self.suspensions, AuthorizationSuspensionEvidence, "suspensions"),
            (self.expirations, AuthorizationExpirationEvidence, "expirations"),
            (self.restorations, AuthorizationRestorationEvidence, "restorations"),
            (
                self.snapshots,
                ProviderAuthorizationResolutionSnapshot,
                "snapshots",
            ),
        ):
            _typed_tuple(values, item_type, name)
        if not self.providers:
            raise ValueError("providers must not be empty")
        if self.provenance is None:
            raise ValueError("provenance is required")
        _provenance(self.provenance)
        _typed_unique_nonempty(
            self.capabilities,
            ProviderAuthorizationPackageCapability,
            "capabilities",
        )


class ProviderAuthorizationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianProviderAuthorizationValidator:
    """Validate supplied authorization evidence without executing authority."""

    def validate(
        self,
        package: GuardianProviderAuthorizationPackage,
    ) -> GuardianProviderAuthorizationPackage:
        if not isinstance(package, GuardianProviderAuthorizationPackage):
            raise TypeError("package must be a GuardianProviderAuthorizationPackage")
        GuardianAuthorityModelValidator().validate(package.authority_model)
        self._validate_capabilities(package)
        self._validate_global_identities(package)
        self._validate_provenance(package)
        providers = {item.provider_id: item for item in package.providers}
        authorities = {
            item.authority_id: item for item in package.authority_model.authorities
        }
        boundaries = {
            item.actor_class: item for item in package.authority_model.actor_boundaries
        }
        authorizations = {
            item.authorization_id: item for item in package.authorizations
        }
        decisions = self._decisions_by_authorization(package.decisions)
        self._validate_providers(package.providers)
        self._validate_authorizations(
            package,
            providers,
            authorities,
            boundaries,
            decisions,
        )
        self._validate_lifecycle(package, authorizations)
        self._validate_parallel_conflicts(package, providers, authorities)
        self._validate_snapshots(package, providers, boundaries)
        return package

    @staticmethod
    def _validate_capabilities(package) -> None:
        if package.capabilities != NON_EXECUTING_PROVIDER_AUTHORIZATION_CAPABILITIES:
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "provider authorization package is evidence only",
            )

    @staticmethod
    def _validate_global_identities(package) -> None:
        identifiers = [package.package_id]
        identifiers.extend(item.provider_id for item in package.providers)
        identifiers.extend(item.authorization_id for item in package.authorizations)
        identifiers.extend(item.decision_evidence_id for item in package.decisions)
        for values in (
            package.revocations,
            package.suspensions,
            package.expirations,
            package.restorations,
        ):
            identifiers.extend(item.evidence_id for item in values)
        identifiers.extend(item.snapshot_id for item in package.snapshots)
        if len(identifiers) != len(set(identifiers)):
            _invalid("DUPLICATE_IDENTITY", "all package identities must be unique")

    @staticmethod
    def _validate_provenance(package) -> None:
        values = (
            tuple(item.provenance for item in package.providers)
            + tuple(item.provenance for item in package.authorizations)
            + tuple(item.provenance for item in package.decisions)
            + tuple(item.provenance for item in package.revocations)
            + tuple(item.provenance for item in package.suspensions)
            + tuple(item.provenance for item in package.expirations)
            + tuple(item.provenance for item in package.restorations)
            + tuple(item.provenance for item in package.snapshots)
        )
        if any(value != package.provenance for value in values):
            _invalid("PROVENANCE_MISMATCH", "all package evidence must share provenance")

    @staticmethod
    def _decisions_by_authorization(decisions):
        result = {}
        for decision in decisions:
            if decision.authorization_reference in result:
                _invalid(
                    "DUPLICATE_DECISION_EVIDENCE",
                    "each authorization needs exactly one decision evidence",
                )
            result[decision.authorization_reference] = decision
        return result

    @staticmethod
    def _validate_providers(providers) -> None:
        for provider in providers:
            _review_pair(provider.review_status, provider.review_reference)
            if provider.previous_provider_id == provider.provider_id:
                _invalid("SELF_PREDECESSOR", "provider predecessor cannot reference itself")

    @classmethod
    def _validate_authorizations(
        cls,
        package,
        providers,
        authorities,
        boundaries,
        decisions,
    ) -> None:
        for grant in package.authorizations:
            provider = providers.get(grant.provider_reference)
            if provider is None:
                _invalid("UNKNOWN_PROVIDER_REFERENCE", "authorization provider is unknown")
            authority = authorities.get(grant.authority_reference)
            if authority is None:
                _invalid("UNKNOWN_AUTHORITY_REFERENCE", "authorization authority is unknown")
            boundary = boundaries.get(provider.actor_class)
            if boundary is None:
                _invalid("ACTOR_BOUNDARY_REQUIRED", "provider actor class needs a boundary")
            if grant.responsibility_boundary_reference != boundary.boundary_id:
                _invalid("BOUNDARY_REFERENCE_MISMATCH", "responsibility boundary differs")
            if authority.authority_id not in boundary.allowed_authority_references:
                _invalid("RESPONSIBILITY_BOUNDARY_EXCEEDED", "provider exceeds actor boundary")
            if authority.authority_type not in provider.supported_authority_types:
                _invalid(
                    "PROVIDER_AUTHORITY_TYPE_MISMATCH",
                    "provider does not support authority type",
                )
            cls._validate_grant_capabilities(grant, authority)
            cls._validate_grant_controls(package, grant, provider, authority)
            cls._validate_grant_validity(grant, provider)
            _review_pair(grant.review_status, grant.review_reference)
            if grant.previous_authorization_id == grant.authorization_id:
                _invalid("SELF_PREDECESSOR", "authorization predecessor cannot reference itself")
            decision = decisions.get(grant.authorization_id)
            if decision is None:
                _invalid("DECISION_EVIDENCE_REQUIRED", "authorization needs decision evidence")
            cls._validate_decision(grant, authority, boundary, decision)
        unknown = set(decisions) - set(
            item.authorization_id for item in package.authorizations
        )
        if unknown:
            _invalid("UNKNOWN_AUTHORIZATION_REFERENCE", "decision references unknown authorization")

    @staticmethod
    def _validate_grant_capabilities(grant, authority) -> None:
        allowed = set(grant.allowed_capabilities)
        forbidden = set(grant.forbidden_capabilities)
        defined = set(authority.capabilities)
        if allowed & forbidden:
            _invalid("CAPABILITY_CONFLICT", "capability cannot be allowed and forbidden")
        if allowed | forbidden != defined:
            _invalid("INCOMPLETE_CAPABILITY_BOUNDARY", "capability boundary must be complete")

    @staticmethod
    def _validate_grant_controls(package, grant, provider, authority) -> None:
        if grant.control_levels != authority.required_control_levels:
            _invalid("CONTROL_LEVEL_MISMATCH", "grant controls must match authority")
        if grant.required_joint_actor_classes != authority.joint_actor_classes:
            _invalid("JOINT_CONTROL_MISMATCH", "joint actor classes must match authority")
        expected_delegable = authority.exercise is AuthorityExercise.DELEGABLE
        if grant.delegable is not expected_delegable:
            _invalid("DELEGATION_MODE_MISMATCH", "grant delegation mode must match authority")
        if grant.revocable is not authority.revocable:
            _invalid("REVOCABILITY_MISMATCH", "grant revocability must match authority")
        if expected_delegable:
            matching_rules = tuple(
                rule
                for rule in package.authority_model.delegation_rules
                if rule.delegation_rule_id == grant.granting_authority_reference
                and rule.authority_reference == authority.authority_id
                and provider.actor_class in rule.receiving_actor_classes
            )
            if len(matching_rules) != 1:
                _invalid("DELEGATION_RULE_MISMATCH", "delegable grant needs matching rule")
        elif grant.granting_authority_reference != authority.authority_id:
            _invalid(
                "UNAUTHORIZED_GRANTING_REFERENCE",
                "non-delegable or joint grant must retain authority reference",
            )

    @staticmethod
    def _validate_grant_validity(grant, provider) -> None:
        if grant.valid_from < provider.valid_from:
            _invalid("VALIDITY_OUTSIDE_PROVIDER_IDENTITY", "grant starts before provider")
        if provider.valid_until is not None:
            if grant.valid_until is None or grant.valid_until > provider.valid_until:
                _invalid("VALIDITY_OUTSIDE_PROVIDER_IDENTITY", "grant exceeds provider validity")

    @staticmethod
    def _validate_decision(grant, authority, boundary, decision) -> None:
        expected = {
            ProviderAuthorizationStatus.PROPOSED: AuthorizationDecisionType.PROPOSE,
            ProviderAuthorizationStatus.AUTHORIZED: (
                AuthorizationDecisionType.AUTHORIZE,
                AuthorizationDecisionType.RESTORE,
            ),
            ProviderAuthorizationStatus.REJECTED: AuthorizationDecisionType.REJECT,
            ProviderAuthorizationStatus.SUSPENDED: AuthorizationDecisionType.SUSPEND,
            ProviderAuthorizationStatus.REVOKED: AuthorizationDecisionType.REVOKE,
            ProviderAuthorizationStatus.EXPIRED: AuthorizationDecisionType.EXPIRE,
        }[grant.status]
        allowed_types = expected if isinstance(expected, tuple) else (expected,)
        if decision.decision_type not in allowed_types:
            _invalid("DECISION_STATUS_MISMATCH", "decision type does not match status")
        if grant.authority_reference not in decision.checked_authority_rule_references:
            _invalid("AUTHORITY_RULE_EVIDENCE_MISSING", "decision did not check authority")
        if boundary.boundary_id not in decision.checked_responsibility_boundary_references:
            _invalid("BOUNDARY_EVIDENCE_MISSING", "decision did not check boundary")
        if decision.required_control_levels != authority.required_control_levels:
            _invalid("CONTROL_EVIDENCE_MISMATCH", "decision controls must match authority")
        deciding_classes = {item.actor_class for item in decision.deciding_actors}
        if not set(authority.joint_actor_classes) <= deciding_classes:
            _invalid("JOINT_CONTROL_INCOMPLETE", "joint deciding actors are incomplete")
        _review_pair(decision.review_status, decision.review_reference)

    @classmethod
    def _validate_lifecycle(cls, package, authorizations) -> None:
        revocations = cls._lifecycle_map(package.revocations, "revocation")
        suspensions = cls._lifecycle_map(package.suspensions, "suspension")
        expirations = cls._lifecycle_map(package.expirations, "expiration")
        restorations = cls._lifecycle_map(package.restorations, "restoration")
        for mapping in (revocations, suspensions, expirations, restorations):
            if set(mapping) - set(authorizations):
                _invalid("UNKNOWN_AUTHORIZATION_REFERENCE", "lifecycle evidence is foreign")
        for grant in authorizations.values():
            cls._validate_lifecycle_status(
                grant,
                revocations.get(grant.authorization_id),
                suspensions.get(grant.authorization_id),
                expirations.get(grant.authorization_id),
                restorations.get(grant.authorization_id),
            )

    @staticmethod
    def _lifecycle_map(values, label):
        result = {}
        for value in values:
            if value.authorization_reference in result:
                _invalid(
                    "DUPLICATE_LIFECYCLE_EVIDENCE",
                    "duplicate {} evidence".format(label),
                )
            result[value.authorization_reference] = value
        return result

    @staticmethod
    def _validate_lifecycle_status(
        grant,
        revocation,
        suspension,
        expiration,
        restoration,
    ):
        for evidence in tuple(
            item
            for item in (revocation, suspension, expiration, restoration)
            if item is not None
        ):
            if evidence.control_levels != grant.control_levels:
                _invalid("LIFECYCLE_CONTROL_MISMATCH", "lifecycle controls differ")
            if evidence.deciding_authority_reference != grant.granting_authority_reference:
                _invalid("LIFECYCLE_AUTHORITY_MISMATCH", "lifecycle authority differs")
            if evidence.effective_at < grant.valid_from:
                _invalid("LIFECYCLE_BEFORE_VALIDITY", "lifecycle evidence predates grant")
            if grant.valid_until is not None and evidence.effective_at > grant.valid_until:
                _invalid("LIFECYCLE_AFTER_VALIDITY", "lifecycle evidence exceeds validity")
            _review_pair(evidence.review_status, evidence.review_reference)
        expected_transitions = (
            (
                revocation,
                (
                    ProviderAuthorizationStatus.AUTHORIZED,
                    ProviderAuthorizationStatus.SUSPENDED,
                ),
                ProviderAuthorizationStatus.REVOKED,
            ),
            (
                suspension,
                (ProviderAuthorizationStatus.AUTHORIZED,),
                ProviderAuthorizationStatus.SUSPENDED,
            ),
            (
                expiration,
                (
                    ProviderAuthorizationStatus.AUTHORIZED,
                    ProviderAuthorizationStatus.SUSPENDED,
                ),
                ProviderAuthorizationStatus.EXPIRED,
            ),
            (
                restoration,
                (ProviderAuthorizationStatus.SUSPENDED,),
                ProviderAuthorizationStatus.AUTHORIZED,
            ),
        )
        for evidence, previous_values, resulting_value in expected_transitions:
            if evidence is None:
                continue
            if (
                evidence.previous_status not in previous_values
                or evidence.resulting_status is not resulting_value
            ):
                _invalid(
                    "INVALID_LIFECYCLE_TRANSITION",
                    "lifecycle status transition is not permitted",
                )
        expected = {
            ProviderAuthorizationStatus.REVOKED: revocation,
            ProviderAuthorizationStatus.SUSPENDED: suspension,
            ProviderAuthorizationStatus.EXPIRED: expiration,
        }
        if grant.status in expected and expected[grant.status] is None:
            _invalid("LIFECYCLE_EVIDENCE_REQUIRED", "terminal or suspended status needs evidence")
        if grant.status is not ProviderAuthorizationStatus.REVOKED and revocation is not None:
            _invalid("LIFECYCLE_STATUS_MISMATCH", "revocation conflicts with status")
        if grant.status is not ProviderAuthorizationStatus.EXPIRED and expiration is not None:
            _invalid("LIFECYCLE_STATUS_MISMATCH", "expiration conflicts with status")
        if grant.status is ProviderAuthorizationStatus.SUSPENDED and restoration is not None:
            _invalid("RESTORATION_STATUS_MISMATCH", "restored authorization must be authorized")
        if grant.status is ProviderAuthorizationStatus.AUTHORIZED and restoration is not None:
            if suspension is None:
                _invalid("SUSPENSION_EVIDENCE_REQUIRED", "restoration needs suspension")
            if restoration.effective_at <= suspension.effective_at:
                _invalid("RETROACTIVE_RESTORATION", "restoration must follow suspension")
            if grant.valid_until is not None and restoration.effective_at >= grant.valid_until:
                _invalid("RESTORATION_OUTSIDE_VALIDITY", "restoration cannot extend validity")
        elif restoration is not None:
            _invalid("RESTORATION_STATUS_MISMATCH", "restoration requires authorized status")
        if grant.status is not ProviderAuthorizationStatus.SUSPENDED:
            if suspension is not None and restoration is None:
                _invalid("LIFECYCLE_STATUS_MISMATCH", "unrestored suspension conflicts with status")

    @staticmethod
    def _validate_parallel_conflicts(package, providers, authorities) -> None:
        prohibited_pairs = {
            frozenset(
                (
                    item.first_authority_reference,
                    item.second_authority_reference,
                )
            )
            for item in package.authority_model.prohibited_combinations
        }
        active = tuple(
            item
            for item in package.authorizations
            if item.status is ProviderAuthorizationStatus.AUTHORIZED
        )
        for index, first in enumerate(active):
            for second in active[index + 1 :]:
                if first.provider_reference != second.provider_reference:
                    continue
                if not _periods_overlap(first, second):
                    continue
                pair = frozenset((first.authority_reference, second.authority_reference))
                if first.authority_reference == second.authority_reference:
                    _invalid("PARALLEL_AUTHORIZATION_CONFLICT", "duplicate active authority")
                if pair in prohibited_pairs:
                    _invalid("PROHIBITED_AUTHORITY_COMBINATION", "active grants conflict")

    @staticmethod
    def _validate_snapshots(package, providers, boundaries) -> None:
        authorizations = tuple(package.authorizations)
        for snapshot in package.snapshots:
            provider = providers.get(snapshot.provider.provider_id)
            if provider is not snapshot.provider:
                _invalid(
                    "SNAPSHOT_PROVIDER_IDENTITY_MISMATCH",
                    "snapshot provider is not original object",
                )
            expected = {
                ProviderAuthorizationStatus.AUTHORIZED: snapshot.authorized,
                ProviderAuthorizationStatus.SUSPENDED: snapshot.suspended,
                ProviderAuthorizationStatus.REVOKED: snapshot.revoked,
                ProviderAuthorizationStatus.EXPIRED: snapshot.expired,
            }
            included = tuple(item for values in expected.values() for item in values)
            if len(included) != len(set(item.authorization_id for item in included)):
                _invalid("DUPLICATE_SNAPSHOT_AUTHORIZATION", "snapshot duplicates authorization")
            applicable = tuple(
                item
                for item in authorizations
                if item.provider_reference == provider.provider_id
                and item.status in expected
            )
            if set(item.authorization_id for item in included) != set(
                item.authorization_id for item in applicable
            ):
                _invalid("SNAPSHOT_AUTHORIZATION_SET_MISMATCH", "snapshot set is incomplete")
            originals = {item.authorization_id: item for item in applicable}
            for status, values in expected.items():
                for item in values:
                    original_differs = (
                        originals.get(item.authorization_id) is not item
                    )
                    if original_differs or item.status is not status:
                        _invalid(
                            "SNAPSHOT_OBJECT_IDENTITY_MISMATCH",
                            "snapshot must retain grant objects",
                        )
            allowed = _ordered_unique(
                capability
                for item in snapshot.authorized
                for capability in item.allowed_capabilities
            )
            forbidden = _ordered_unique(
                capability
                for item in snapshot.authorized
                for capability in item.forbidden_capabilities
            )
            controls = _ordered_unique(
                control for item in snapshot.authorized for control in item.control_levels
            )
            uncertainties = _ordered_unique(
                item.uncertainty_status for item in applicable
            )
            boundary = boundaries[provider.actor_class]
            if snapshot.allowed_capabilities != allowed:
                _invalid("SNAPSHOT_CAPABILITY_MISMATCH", "allowed capabilities differ")
            if snapshot.forbidden_capabilities != forbidden:
                _invalid("SNAPSHOT_CAPABILITY_MISMATCH", "forbidden capabilities differ")
            if snapshot.control_levels != controls:
                _invalid("SNAPSHOT_CONTROL_MISMATCH", "snapshot controls differ")
            if snapshot.responsibility_boundaries != (boundary,):
                _invalid("SNAPSHOT_BOUNDARY_MISMATCH", "snapshot boundary differs")
            if snapshot.uncertainties != uncertainties:
                _invalid("SNAPSHOT_UNCERTAINTY_MISMATCH", "snapshot uncertainties differ")
            _review_pair(snapshot.review_status, snapshot.review_reference)


def _lifecycle_fields(value) -> None:
    for item, name in (
        (value.evidence_id, "evidence_id"),
        (value.authorization_reference, "authorization_reference"),
        (value.reason, "reason"),
        (value.deciding_authority_reference, "deciding_authority_reference"),
    ):
        _text(item, name)
    _aware(value.effective_at, "effective_at")
    _typed_unique_nonempty(
        value.control_levels,
        AuthorityControlLevel,
        "control_levels",
    )
    _enum(value.previous_status, ProviderAuthorizationStatus, "previous_status")
    _enum(value.resulting_status, ProviderAuthorizationStatus, "resulting_status")
    _provenance(value.provenance)
    _enum(value.review_status, AuthorityReviewStatus, "review_status")
    if value.review_reference is not None:
        _text(value.review_reference, "review_reference")


def _periods_overlap(first, second) -> bool:
    first_end = first.valid_until
    second_end = second.valid_until
    return (first_end is None or second.valid_from < first_end) and (
        second_end is None or first.valid_from < second_end
    )


def _ordered_unique(values) -> tuple:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return tuple(result)


def _review_pair(status, reference) -> None:
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            _invalid("REVIEW_REFERENCE_REQUIRED", "reviewed evidence needs reference")
    elif reference is not None:
        _invalid("UNEXPECTED_REVIEW_REFERENCE", "only reviewed evidence may reference review")


def _provenance(value) -> None:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")


def _invalid(code: str, message: str) -> None:
    raise ProviderAuthorizationValidationError(code, message)


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value: object, name: str, *, required: bool) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_tuple(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid values".format(name))


def _typed_unique(value: object, item_type: type, name: str) -> None:
    _typed_tuple(value, item_type, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(value: object, item_type: type, name: str) -> None:
    _typed_unique(value, item_type, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))
