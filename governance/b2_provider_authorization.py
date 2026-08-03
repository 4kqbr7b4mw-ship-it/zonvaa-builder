"""Immutable B2 provider authorization evidence without execution power."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple, Union

from governance.b2_authorization import (
    B2_AUTHORIZATION_CONTRACT_VERSION,
    B2AAVBinding,
    B2AuthorizationDecision,
    B2AuthorizationEvaluationEvidence,
    B2AuthorizationEvaluator,
    B2AuthorizationReason,
    B2Authority,
    B2AuthorityId,
    B2D3Consent,
    B2EvaluationEvidence,
    B2Grant,
    B2NegativeGovernanceEvidence,
    B2PurposeScope,
    B2T4GrantReceipt,
    B2UODLBinding,
    B2UODLOperation,
)
from governance.b2_data_corridor import (
    B2DataCorridorPackage,
    B2DataCorridorValidationError,
    B2DataCorridorValidator,
)
from governance.b2_provider_identity import (
    B2GovernanceDecisionId,
    B2InstitutionalSourceId,
    B2NonPersonalReferenceId,
    B2ProviderIdentity,
    B2ProviderIdentityId,
)


B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION = "1.0"


class B2ProviderAuthorizationReason(str, Enum):
    ALL_PROVIDER_BINDINGS_EFFECTIVE = "ALL_PROVIDER_BINDINGS_EFFECTIVE"
    PROVIDER_IDENTITY_MISMATCH = "PROVIDER_IDENTITY_MISMATCH"
    GRANT_BINDING_MISMATCH = "GRANT_BINDING_MISMATCH"
    CORRIDOR_BINDING_MISMATCH = "CORRIDOR_BINDING_MISMATCH"
    BASE_AUTHORIZATION_DENIED = "BASE_AUTHORIZATION_DENIED"
    PROVENANCE_BINDING_MISMATCH = "PROVENANCE_BINDING_MISMATCH"


@dataclass(frozen=True)
class B2ProviderAuthorizationId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "authorization_id", "b2-provider-authorization:")


@dataclass(frozen=True)
class B2ProviderAuthorizationProvenance:
    institutional_source_id: B2InstitutionalSourceId
    governance_decision_id: B2GovernanceDecisionId
    authorization_basis_reference: B2NonPersonalReferenceId
    evaluation_evidence_reference: str
    provider_identity_reference: B2ProviderIdentityId
    grant_reference: str
    evaluated_at: datetime

    def __post_init__(self) -> None:
        _instance(
            self.institutional_source_id,
            B2InstitutionalSourceId,
            "institutional_source_id",
        )
        _instance(
            self.governance_decision_id,
            B2GovernanceDecisionId,
            "governance_decision_id",
        )
        _instance(
            self.authorization_basis_reference,
            B2NonPersonalReferenceId,
            "authorization_basis_reference",
        )
        _reference(
            self.evaluation_evidence_reference,
            "evaluation_evidence_reference",
            "b2-evidence:",
        )
        _instance(
            self.provider_identity_reference,
            B2ProviderIdentityId,
            "provider_identity_reference",
        )
        _reference(self.grant_reference, "grant_reference", "b2-grant:")
        _aware(self.evaluated_at, "evaluated_at")


@dataclass(frozen=True, init=False)
class B2ProviderAuthorization:
    authorization_id: B2ProviderAuthorizationId
    provider_identity_reference: B2ProviderIdentityId
    grant_reference: str
    authority_reference: B2AuthorityId
    d3_reference: str
    t4_reference: str
    aav_reference: str
    uodl_reference: str
    purpose_scope: B2PurposeScope
    data_corridor_reference: str
    evaluation_evidence_reference: str
    evaluated_at: datetime
    provenance: B2ProviderAuthorizationProvenance
    contract_version: str

    def __init__(
        self,
        authorization_id: B2ProviderAuthorizationId,
        provider_identity: B2ProviderIdentity,
        grant: B2Grant,
        data_corridor: B2DataCorridorPackage,
        evaluation_evidence_reference: str,
        evaluated_at: datetime,
        provenance: B2ProviderAuthorizationProvenance,
    ) -> None:
        _instance(authorization_id, B2ProviderAuthorizationId, "authorization_id")
        _instance(provider_identity, B2ProviderIdentity, "provider_identity")
        _instance(grant, B2Grant, "grant")
        _instance(data_corridor, B2DataCorridorPackage, "data_corridor")
        _reference(
            evaluation_evidence_reference,
            "evaluation_evidence_reference",
            "b2-evidence:",
        )
        _aware(evaluated_at, "evaluated_at")
        _instance(provenance, B2ProviderAuthorizationProvenance, "provenance")
        object.__setattr__(self, "authorization_id", authorization_id)
        object.__setattr__(
            self, "provider_identity_reference", provider_identity.identity_id
        )
        object.__setattr__(self, "grant_reference", grant.grant_id)
        object.__setattr__(self, "authority_reference", grant.authority_reference)
        object.__setattr__(self, "d3_reference", grant.d3_reference)
        object.__setattr__(self, "t4_reference", grant.t4_reference)
        object.__setattr__(self, "aav_reference", grant.aav_reference)
        object.__setattr__(self, "uodl_reference", grant.uodl_reference)
        object.__setattr__(self, "purpose_scope", grant.purpose_scope)
        object.__setattr__(
            self, "data_corridor_reference", data_corridor.corridor.corridor_id
        )
        object.__setattr__(
            self, "evaluation_evidence_reference", evaluation_evidence_reference
        )
        object.__setattr__(self, "evaluated_at", evaluated_at)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(
            self, "contract_version", B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION
        )


@dataclass(frozen=True)
class B2ProviderAuthorizationEvaluationEvidence:
    evidence_id: str
    provider_authorization_reference: B2ProviderAuthorizationId
    provider_identity_reference: B2ProviderIdentityId
    grant_reference: str
    data_corridor_reference: str
    base_evaluation_evidence_reference: str
    evaluated_at: datetime
    decision: B2AuthorizationDecision
    reasons: Tuple[B2ProviderAuthorizationReason, ...]
    base_reasons: Tuple[B2AuthorizationReason, ...]
    observed_negative_evidence_references: Tuple[str, ...]
    provenance: B2ProviderAuthorizationProvenance
    contract_version: str

    def __post_init__(self) -> None:
        _provider_evidence(self, B2AuthorizationDecision.EFFECTIVE)
        if self.reasons != (
            B2ProviderAuthorizationReason.ALL_PROVIDER_BINDINGS_EFFECTIVE,
        ):
            raise ValueError("positive evidence requires the positive reason")
        if self.base_reasons != (B2AuthorizationReason.ALL_BINDINGS_EFFECTIVE,):
            raise ValueError("positive evidence requires positive base evidence")


@dataclass(frozen=True)
class B2ProviderAuthorizationNegativeGovernanceEvidence:
    evidence_id: str
    provider_authorization_reference: B2ProviderAuthorizationId
    provider_identity_reference: B2ProviderIdentityId
    grant_reference: str
    data_corridor_reference: str
    base_evaluation_evidence_reference: str
    evaluated_at: datetime
    decision: B2AuthorizationDecision
    reasons: Tuple[B2ProviderAuthorizationReason, ...]
    base_reasons: Tuple[B2AuthorizationReason, ...]
    observed_negative_evidence_references: Tuple[str, ...]
    provenance: B2ProviderAuthorizationProvenance
    contract_version: str

    def __post_init__(self) -> None:
        _provider_evidence(self, B2AuthorizationDecision.DENIED)
        if B2ProviderAuthorizationReason.ALL_PROVIDER_BINDINGS_EFFECTIVE in self.reasons:
            raise ValueError("negative evidence cannot contain the positive reason")


B2ProviderAuthorizationEvidence = Union[
    B2ProviderAuthorizationEvaluationEvidence,
    B2ProviderAuthorizationNegativeGovernanceEvidence,
]


class B2ProviderAuthorizationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B2ProviderAuthorizationValidator:
    """Validate supplied references without reading state or authorizing work."""

    def validate(
        self,
        authorization: B2ProviderAuthorization,
        provider_identity: B2ProviderIdentity,
        grant: B2Grant,
        data_corridor: B2DataCorridorPackage,
    ) -> B2ProviderAuthorization:
        _instance(authorization, B2ProviderAuthorization, "authorization")
        _instance(provider_identity, B2ProviderIdentity, "provider_identity")
        _instance(grant, B2Grant, "grant")
        _instance(data_corridor, B2DataCorridorPackage, "data_corridor")
        if authorization.provider_identity_reference != provider_identity.identity_id:
            _invalid("PROVIDER_IDENTITY_MISMATCH", "provider identity differs")
        if authorization.grant_reference != grant.grant_id:
            _invalid("GRANT_BINDING_MISMATCH", "grant differs")
        if authorization.data_corridor_reference != data_corridor.corridor.corridor_id:
            _invalid("CORRIDOR_BINDING_MISMATCH", "corridor differs")
        if not _authorization_matches_grant(authorization, grant):
            _invalid("GRANT_BINDING_MISMATCH", "grant bindings differ")
        if not _provenance_matches(authorization):
            _invalid("PROVENANCE_BINDING_MISMATCH", "provenance differs")
        return authorization


class B2ProviderAuthorizationEvaluator:
    """Apply ADR-0060 to supplied immutable provider and corridor objects."""

    def evaluate(
        self,
        authorization: B2ProviderAuthorization,
        provider_identity: B2ProviderIdentity,
        data_corridor: B2DataCorridorPackage,
        grant: B2Grant,
        authority: B2Authority,
        d3_consent: B2D3Consent,
        t4_receipt: B2T4GrantReceipt,
        aav_binding: B2AAVBinding,
        uodl_binding: B2UODLBinding,
        evaluated_at: datetime,
        base_evidence_id: str,
        provider_evidence_id: str,
        observed_negative_evidence: Tuple[B2NegativeGovernanceEvidence, ...] = (),
    ) -> B2ProviderAuthorizationEvidence:
        _aware(evaluated_at, "evaluated_at")
        _reference(base_evidence_id, "base_evidence_id", "b2-evidence:")
        _reference(
            provider_evidence_id,
            "provider_evidence_id",
            "b2-provider-authorization-evidence:",
        )
        _typed_tuple(
            observed_negative_evidence,
            B2NegativeGovernanceEvidence,
            "observed_negative_evidence",
        )

        reasons = []
        try:
            B2DataCorridorValidator().validate(data_corridor)
        except B2DataCorridorValidationError:
            reasons.append(B2ProviderAuthorizationReason.CORRIDOR_BINDING_MISMATCH)

        try:
            B2ProviderAuthorizationValidator().validate(
                authorization, provider_identity, grant, data_corridor
            )
        except B2ProviderAuthorizationValidationError as error:
            reason = {
                "PROVIDER_IDENTITY_MISMATCH": B2ProviderAuthorizationReason.PROVIDER_IDENTITY_MISMATCH,
                "GRANT_BINDING_MISMATCH": B2ProviderAuthorizationReason.GRANT_BINDING_MISMATCH,
                "CORRIDOR_BINDING_MISMATCH": B2ProviderAuthorizationReason.CORRIDOR_BINDING_MISMATCH,
                "PROVENANCE_BINDING_MISMATCH": B2ProviderAuthorizationReason.PROVENANCE_BINDING_MISMATCH,
            }[error.code]
            reasons.append(reason)

        if not _corridor_matches_grant(data_corridor, grant):
            reasons.append(B2ProviderAuthorizationReason.CORRIDOR_BINDING_MISMATCH)

        base_evidence = B2AuthorizationEvaluator().evaluate(
            grant=grant,
            authority=authority,
            d3_consent=d3_consent,
            t4_receipt=t4_receipt,
            aav_binding=aav_binding,
            uodl_binding=uodl_binding,
            evaluated_at=evaluated_at,
            evidence_id=base_evidence_id,
        )
        if base_evidence.decision is not B2AuthorizationDecision.EFFECTIVE:
            reasons.append(B2ProviderAuthorizationReason.BASE_AUTHORIZATION_DENIED)
        if (
            authorization.evaluated_at != evaluated_at
            or authorization.evaluation_evidence_reference != base_evidence_id
        ):
            reasons.append(B2ProviderAuthorizationReason.PROVENANCE_BINDING_MISMATCH)

        common = dict(
            evidence_id=provider_evidence_id,
            provider_authorization_reference=authorization.authorization_id,
            provider_identity_reference=provider_identity.identity_id,
            grant_reference=grant.grant_id,
            data_corridor_reference=data_corridor.corridor.corridor_id,
            base_evaluation_evidence_reference=base_evidence.evidence_id,
            evaluated_at=evaluated_at,
            base_reasons=base_evidence.reasons,
            observed_negative_evidence_references=tuple(
                item.evidence_id for item in observed_negative_evidence
            ),
            provenance=authorization.provenance,
            contract_version=B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION,
        )
        if reasons:
            return B2ProviderAuthorizationNegativeGovernanceEvidence(
                decision=B2AuthorizationDecision.DENIED,
                reasons=tuple(dict.fromkeys(reasons)),
                **common,
            )
        return B2ProviderAuthorizationEvaluationEvidence(
            decision=B2AuthorizationDecision.EFFECTIVE,
            reasons=(
                B2ProviderAuthorizationReason.ALL_PROVIDER_BINDINGS_EFFECTIVE,
            ),
            **common,
        )


@dataclass(frozen=True)
class B2AuthorizationFoundation:
    foundation_id: str
    data_corridor: B2DataCorridorPackage
    authority: B2Authority
    grant: B2Grant
    provider_identity: B2ProviderIdentity
    provider_authorization: B2ProviderAuthorization
    d3_consent: B2D3Consent
    t4_receipt: B2T4GrantReceipt
    aav_binding: B2AAVBinding
    uodl_binding: B2UODLBinding
    evaluated_at: datetime
    evidence: B2ProviderAuthorizationEvidence
    observed_negative_evidence: Tuple[B2NegativeGovernanceEvidence, ...] = ()

    def __post_init__(self) -> None:
        _reference(self.foundation_id, "foundation_id", "b2-foundation:")
        for value, expected, name in (
            (self.data_corridor, B2DataCorridorPackage, "data_corridor"),
            (self.authority, B2Authority, "authority"),
            (self.grant, B2Grant, "grant"),
            (self.provider_identity, B2ProviderIdentity, "provider_identity"),
            (
                self.provider_authorization,
                B2ProviderAuthorization,
                "provider_authorization",
            ),
            (self.d3_consent, B2D3Consent, "d3_consent"),
            (self.t4_receipt, B2T4GrantReceipt, "t4_receipt"),
            (self.aav_binding, B2AAVBinding, "aav_binding"),
            (self.uodl_binding, B2UODLBinding, "uodl_binding"),
        ):
            _instance(value, expected, name)
        _aware(self.evaluated_at, "evaluated_at")
        if not isinstance(
            self.evidence,
            (
                B2ProviderAuthorizationEvaluationEvidence,
                B2ProviderAuthorizationNegativeGovernanceEvidence,
            ),
        ):
            raise TypeError("evidence has an invalid type")
        _typed_tuple(
            self.observed_negative_evidence,
            B2NegativeGovernanceEvidence,
            "observed_negative_evidence",
        )


class B2AuthorizationFoundationValidator:
    """Validate the complete supplied corridor-to-provider reference chain."""

    def validate(self, foundation: B2AuthorizationFoundation) -> B2AuthorizationFoundation:
        _instance(foundation, B2AuthorizationFoundation, "foundation")
        B2DataCorridorValidator().validate(foundation.data_corridor)
        B2ProviderAuthorizationValidator().validate(
            foundation.provider_authorization,
            foundation.provider_identity,
            foundation.grant,
            foundation.data_corridor,
        )
        if foundation.evidence.decision is not B2AuthorizationDecision.EFFECTIVE:
            _invalid("FOUNDATION_NOT_EFFECTIVE", "foundation requires positive evidence")
        expected = B2ProviderAuthorizationEvaluator().evaluate(
            authorization=foundation.provider_authorization,
            provider_identity=foundation.provider_identity,
            data_corridor=foundation.data_corridor,
            grant=foundation.grant,
            authority=foundation.authority,
            d3_consent=foundation.d3_consent,
            t4_receipt=foundation.t4_receipt,
            aav_binding=foundation.aav_binding,
            uodl_binding=foundation.uodl_binding,
            evaluated_at=foundation.evaluated_at,
            base_evidence_id=foundation.evidence.base_evaluation_evidence_reference,
            provider_evidence_id=foundation.evidence.evidence_id,
            observed_negative_evidence=foundation.observed_negative_evidence,
        )
        if expected != foundation.evidence:
            _invalid("FOUNDATION_EVIDENCE_MISMATCH", "evidence differs")
        return foundation


def _authorization_matches_grant(
    authorization: B2ProviderAuthorization, grant: B2Grant
) -> bool:
    return (
        authorization.grant_reference == grant.grant_id
        and authorization.authority_reference == grant.authority_reference
        and authorization.d3_reference == grant.d3_reference
        and authorization.t4_reference == grant.t4_reference
        and authorization.aav_reference == grant.aav_reference
        and authorization.uodl_reference == grant.uodl_reference
        and authorization.purpose_scope == grant.purpose_scope
        and authorization.contract_version
        == B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION
    )


def _provenance_matches(authorization: B2ProviderAuthorization) -> bool:
    provenance = authorization.provenance
    return (
        provenance.evaluation_evidence_reference
        == authorization.evaluation_evidence_reference
        and provenance.provider_identity_reference
        == authorization.provider_identity_reference
        and provenance.grant_reference == authorization.grant_reference
        and provenance.evaluated_at == authorization.evaluated_at
    )


def _corridor_matches_grant(
    data_corridor: B2DataCorridorPackage, grant: B2Grant
) -> bool:
    corridor = data_corridor.corridor
    consent = data_corridor.consent_boundary
    return (
        corridor.aav_reference.authorization_id == grant.aav_reference
        and corridor.uodl_reference.reference_id == grant.uodl_reference
        and set(grant.purpose_scope.data_classes).issubset(consent.allowed_scope)
        and set(grant.purpose_scope.purposes).issubset(consent.allowed_use)
    )


def _provider_evidence(value: object, decision: B2AuthorizationDecision) -> None:
    _reference(
        getattr(value, "evidence_id"),
        "evidence_id",
        "b2-provider-authorization-evidence:",
    )
    _instance(
        getattr(value, "provider_authorization_reference"),
        B2ProviderAuthorizationId,
        "provider_authorization_reference",
    )
    _instance(
        getattr(value, "provider_identity_reference"),
        B2ProviderIdentityId,
        "provider_identity_reference",
    )
    _reference(getattr(value, "grant_reference"), "grant_reference", "b2-grant:")
    _reference(
        getattr(value, "data_corridor_reference"),
        "data_corridor_reference",
        "b2-corridor-",
    )
    _reference(
        getattr(value, "base_evaluation_evidence_reference"),
        "base_evaluation_evidence_reference",
        "b2-evidence:",
    )
    _aware(getattr(value, "evaluated_at"), "evaluated_at")
    if getattr(value, "decision") is not decision:
        raise ValueError("evidence has an invalid decision")
    _typed_unique_nonempty(
        getattr(value, "reasons"), B2ProviderAuthorizationReason, "reasons"
    )
    _typed_unique_nonempty(
        getattr(value, "base_reasons"), B2AuthorizationReason, "base_reasons"
    )
    _reference_tuple(
        getattr(value, "observed_negative_evidence_references"),
        "observed_negative_evidence_references",
        "b2-evidence:",
    )
    _instance(
        getattr(value, "provenance"),
        B2ProviderAuthorizationProvenance,
        "provenance",
    )
    if getattr(value, "contract_version") != B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION:
        raise ValueError("contract_version is invalid")


def _reference(value: object, name: str, prefix: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("{} must be a non-empty machine reference".format(name))
    if not value.startswith(prefix) or len(value) == len(prefix):
        raise ValueError("{} has an invalid reference family".format(name))
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-._:")
    if any(character not in allowed for character in value):
        raise ValueError("{} must be a non-personal machine reference".format(name))
    segments = set(value.replace("_", "-").replace(":", "-").split("-"))
    if segments.intersection(
        {"person", "personal", "human", "name", "email", "contact", "account"}
    ):
        raise ValueError("{} must not identify a natural person".format(name))


def _reference_tuple(values: object, name: str, prefix: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))
    for value in values:
        _reference(value, name, prefix)


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _instance(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _typed_tuple(values: object, expected: type, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if any(not isinstance(value, expected) for value in values):
        raise TypeError("{} contains an invalid value".format(name))


def _typed_unique_nonempty(values: object, expected: type, name: str) -> None:
    _typed_tuple(values, expected, name)
    if not values:
        raise ValueError("{} must not be empty".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _invalid(code: str, message: str) -> None:
    raise B2ProviderAuthorizationValidationError(code, message)
