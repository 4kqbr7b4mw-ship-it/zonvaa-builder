"""Immutable B2 authority contracts and stateless authorization evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Union

from governance.b2_data_corridor import (
    ALLOWED_B2_DATA_CLASSES,
    B2ConsentUse,
    B2DataClass,
)


B2_AUTHORIZATION_CONTRACT_VERSION = "1.0"


class B2AuthorityClass(str, Enum):
    CONSTITUTIONAL_DATA_AUTHORITY = "CONSTITUTIONAL_DATA_AUTHORITY"
    INSTITUTIONAL_CONSENT_AUTHORITY = "INSTITUTIONAL_CONSENT_AUTHORITY"


class B2InstitutionalScope(str, Enum):
    B2_PERSONAL_PREPARATION = "B2_PERSONAL_PREPARATION"
    B2_CONSENT_BOUND_AUTHORIZATION = "B2_CONSENT_BOUND_AUTHORIZATION"


class B2ConstitutionalBasis(str, Enum):
    ADR_0058 = "ADR-0058"
    ADR_0059 = "ADR-0059"
    ADR_0060 = "ADR-0060"


REQUIRED_B2_AUTHORITY_BASIS = (
    B2ConstitutionalBasis.ADR_0058,
    B2ConstitutionalBasis.ADR_0059,
    B2ConstitutionalBasis.ADR_0060,
)


class B2UODLOperation(str, Enum):
    REFERENCE_ONLY = "REFERENCE_ONLY"


class B2AuthorizationDecision(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    DENIED = "DENIED"


class B2AuthorizationReason(str, Enum):
    ALL_BINDINGS_EFFECTIVE = "ALL_BINDINGS_EFFECTIVE"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    D3_INEFFECTIVE = "D3_INEFFECTIVE"
    D3_BINDING_MISMATCH = "D3_BINDING_MISMATCH"
    T4_BINDING_MISMATCH = "T4_BINDING_MISMATCH"
    AAV_INEFFECTIVE = "AAV_INEFFECTIVE"
    AAV_BINDING_MISMATCH = "AAV_BINDING_MISMATCH"
    UODL_INEFFECTIVE = "UODL_INEFFECTIVE"
    UODL_BINDING_MISMATCH = "UODL_BINDING_MISMATCH"
    PURPOSE_SCOPE_INCONSISTENT = "PURPOSE_SCOPE_INCONSISTENT"


@dataclass(frozen=True)
class B2AuthorizationProvenance:
    source: B2ConstitutionalBasis
    decision_reference: str

    def __post_init__(self) -> None:
        _enum(self.source, B2ConstitutionalBasis, "source")
        _reference(self.decision_reference, "decision_reference", "decision:")


@dataclass(frozen=True)
class B2AuthorityId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "authority_id", "b2-authority:")


@dataclass(frozen=True)
class B2PurposeScope:
    purposes: Tuple[B2ConsentUse, ...]
    data_classes: Tuple[B2DataClass, ...]

    def __post_init__(self) -> None:
        _typed_unique_nonempty(self.purposes, B2ConsentUse, "purposes")
        _typed_unique_nonempty(self.data_classes, B2DataClass, "data_classes")
        if not set(self.data_classes).issubset(ALLOWED_B2_DATA_CLASSES):
            raise B2AuthorizationStructureError(
                "PURPOSE_SCOPE_DATA_CLASS_PROHIBITED",
                "purpose scope contains a data class outside the B2 corridor",
            )

    def contains(self, other: "B2PurposeScope") -> bool:
        if not isinstance(other, B2PurposeScope):
            raise TypeError("other must be a B2PurposeScope")
        return set(other.purposes).issubset(self.purposes) and set(
            other.data_classes
        ).issubset(self.data_classes)


@dataclass(frozen=True)
class B2Authority:
    authority_id: B2AuthorityId
    authority_class: B2AuthorityClass
    institutional_scope: B2InstitutionalScope
    constitutional_basis: Tuple[B2ConstitutionalBasis, ...]
    provenance: B2AuthorizationProvenance

    def __post_init__(self) -> None:
        if not isinstance(self.authority_id, B2AuthorityId):
            raise TypeError("authority_id must be a B2AuthorityId")
        _enum(self.authority_class, B2AuthorityClass, "authority_class")
        _enum(self.institutional_scope, B2InstitutionalScope, "institutional_scope")
        _typed_unique_nonempty(
            self.constitutional_basis,
            B2ConstitutionalBasis,
            "constitutional_basis",
        )
        if self.constitutional_basis != REQUIRED_B2_AUTHORITY_BASIS:
            raise B2AuthorizationStructureError(
                "AUTHORITY_BASIS_INCOMPLETE",
                "B2 authority requires the complete constitutional basis",
            )
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2D3Consent:
    consent_reference: str
    purpose_scope: B2PurposeScope
    effective_from: datetime
    effective_until: Optional[datetime]
    revoked_at: Optional[datetime]

    def __post_init__(self) -> None:
        _reference(self.consent_reference, "consent_reference", "d3:")
        _scope(self.purpose_scope)
        _temporal(self.effective_from, self.effective_until, self.revoked_at)

    def is_effective_at(self, evaluated_at: datetime) -> bool:
        _aware(evaluated_at, "evaluated_at")
        return _effective_at(
            evaluated_at, self.effective_from, self.effective_until, self.revoked_at
        )


@dataclass(frozen=True)
class B2T4GrantReceipt:
    receipt_reference: str
    grant_reference: str
    authority_reference: B2AuthorityId
    d3_reference: str
    purpose_scope: B2PurposeScope

    def __post_init__(self) -> None:
        _reference(self.receipt_reference, "receipt_reference", "t4:")
        _reference(self.grant_reference, "grant_reference", "b2-grant:")
        if not isinstance(self.authority_reference, B2AuthorityId):
            raise TypeError("authority_reference must be a B2AuthorityId")
        _reference(self.d3_reference, "d3_reference", "d3:")
        _scope(self.purpose_scope)


@dataclass(frozen=True)
class B2AAVBinding:
    aav_reference: str
    grant_reference: str
    authority_reference: B2AuthorityId
    d3_reference: str
    purpose_scope: B2PurposeScope
    effective_from: datetime
    effective_until: Optional[datetime]
    revoked_at: Optional[datetime]

    def __post_init__(self) -> None:
        _reference(self.aav_reference, "aav_reference", "aav:")
        _reference(self.grant_reference, "grant_reference", "b2-grant:")
        if not isinstance(self.authority_reference, B2AuthorityId):
            raise TypeError("authority_reference must be a B2AuthorityId")
        _reference(self.d3_reference, "d3_reference", "d3:")
        _scope(self.purpose_scope)
        _temporal(self.effective_from, self.effective_until, self.revoked_at)

    def is_effective_at(self, evaluated_at: datetime) -> bool:
        _aware(evaluated_at, "evaluated_at")
        return _effective_at(
            evaluated_at, self.effective_from, self.effective_until, self.revoked_at
        )


@dataclass(frozen=True)
class B2UODLBinding:
    uodl_reference: str
    grant_reference: str
    aav_reference: str
    operation: B2UODLOperation
    effective_from: datetime
    effective_until: Optional[datetime]
    revoked_at: Optional[datetime]

    def __post_init__(self) -> None:
        _reference(self.uodl_reference, "uodl_reference", "uodl:")
        _reference(self.grant_reference, "grant_reference", "b2-grant:")
        _reference(self.aav_reference, "aav_reference", "aav:")
        _enum(self.operation, B2UODLOperation, "operation")
        _temporal(self.effective_from, self.effective_until, self.revoked_at)

    def is_effective_at(self, evaluated_at: datetime) -> bool:
        _aware(evaluated_at, "evaluated_at")
        return _effective_at(
            evaluated_at, self.effective_from, self.effective_until, self.revoked_at
        )


@dataclass(frozen=True, init=False)
class B2Grant:
    grant_id: str
    authority_reference: B2AuthorityId
    d3_reference: str
    t4_reference: str
    aav_reference: str
    uodl_reference: str
    purpose_scope: B2PurposeScope
    provenance: B2AuthorizationProvenance

    def __init__(
        self,
        grant_id: str,
        authority: B2Authority,
        d3_consent: B2D3Consent,
        t4_reference: str,
        aav_reference: str,
        uodl_reference: str,
        purpose_scope: B2PurposeScope,
        provenance: B2AuthorizationProvenance,
    ) -> None:
        _reference(grant_id, "grant_id", "b2-grant:")
        if not isinstance(authority, B2Authority):
            raise TypeError("authority must be a B2Authority")
        if not isinstance(d3_consent, B2D3Consent):
            raise TypeError("d3_consent must be a B2D3Consent")
        _reference(t4_reference, "t4_reference", "t4:")
        _reference(aav_reference, "aav_reference", "aav:")
        _reference(uodl_reference, "uodl_reference", "uodl:")
        _scope(purpose_scope)
        _provenance(provenance)
        if not d3_consent.purpose_scope.contains(purpose_scope):
            raise B2AuthorizationStructureError(
                "GRANT_SCOPE_EXPANSION",
                "grant scope must be equal to or narrower than D3 scope",
            )
        object.__setattr__(self, "grant_id", grant_id)
        object.__setattr__(self, "authority_reference", authority.authority_id)
        object.__setattr__(self, "d3_reference", d3_consent.consent_reference)
        object.__setattr__(self, "t4_reference", t4_reference)
        object.__setattr__(self, "aav_reference", aav_reference)
        object.__setattr__(self, "uodl_reference", uodl_reference)
        object.__setattr__(self, "purpose_scope", purpose_scope)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True)
class B2AuthorizationEvaluationEvidence:
    evidence_id: str
    grant_reference: str
    authority_reference: B2AuthorityId
    d3_reference: str
    t4_reference: str
    aav_reference: str
    uodl_reference: str
    purpose_scope: B2PurposeScope
    evaluated_at: datetime
    decision: B2AuthorizationDecision
    reasons: Tuple[B2AuthorizationReason, ...]
    contract_version: str

    def __post_init__(self) -> None:
        _evidence(self, B2AuthorizationDecision.EFFECTIVE)
        if self.reasons != (B2AuthorizationReason.ALL_BINDINGS_EFFECTIVE,):
            raise ValueError("positive evidence requires the positive reason")


@dataclass(frozen=True)
class B2NegativeGovernanceEvidence:
    evidence_id: str
    grant_reference: str
    authority_reference: B2AuthorityId
    d3_reference: str
    t4_reference: str
    aav_reference: str
    uodl_reference: str
    purpose_scope: B2PurposeScope
    evaluated_at: datetime
    decision: B2AuthorizationDecision
    reasons: Tuple[B2AuthorizationReason, ...]
    contract_version: str

    def __post_init__(self) -> None:
        _evidence(self, B2AuthorizationDecision.DENIED)
        if B2AuthorizationReason.ALL_BINDINGS_EFFECTIVE in self.reasons:
            raise ValueError("negative evidence cannot contain the positive reason")


B2EvaluationEvidence = Union[
    B2AuthorizationEvaluationEvidence, B2NegativeGovernanceEvidence
]


class B2AuthorizationStructureError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B2AuthorizationEvaluator:
    """Evaluate complete supplied B2 bindings without time or runtime access."""

    def evaluate(
        self,
        grant: B2Grant,
        authority: B2Authority,
        d3_consent: B2D3Consent,
        t4_receipt: B2T4GrantReceipt,
        aav_binding: B2AAVBinding,
        uodl_binding: B2UODLBinding,
        evaluated_at: datetime,
        evidence_id: str,
    ) -> B2EvaluationEvidence:
        for value, expected, name in (
            (grant, B2Grant, "grant"),
            (authority, B2Authority, "authority"),
            (d3_consent, B2D3Consent, "d3_consent"),
            (t4_receipt, B2T4GrantReceipt, "t4_receipt"),
            (aav_binding, B2AAVBinding, "aav_binding"),
            (uodl_binding, B2UODLBinding, "uodl_binding"),
        ):
            if not isinstance(value, expected):
                raise TypeError("{} has an invalid type".format(name))
        _aware(evaluated_at, "evaluated_at")
        _reference(evidence_id, "evidence_id", "b2-evidence:")

        reasons = []
        if grant.authority_reference != authority.authority_id:
            reasons.append(B2AuthorizationReason.AUTHORITY_MISMATCH)
        if grant.d3_reference != d3_consent.consent_reference:
            reasons.append(B2AuthorizationReason.D3_BINDING_MISMATCH)
        if not d3_consent.is_effective_at(evaluated_at):
            reasons.append(B2AuthorizationReason.D3_INEFFECTIVE)
        if not _t4_matches(grant, t4_receipt):
            reasons.append(B2AuthorizationReason.T4_BINDING_MISMATCH)
        if not aav_binding.is_effective_at(evaluated_at):
            reasons.append(B2AuthorizationReason.AAV_INEFFECTIVE)
        if not _aav_matches(grant, aav_binding):
            reasons.append(B2AuthorizationReason.AAV_BINDING_MISMATCH)
        if not uodl_binding.is_effective_at(evaluated_at):
            reasons.append(B2AuthorizationReason.UODL_INEFFECTIVE)
        if not _uodl_matches(grant, aav_binding, uodl_binding):
            reasons.append(B2AuthorizationReason.UODL_BINDING_MISMATCH)
        if not d3_consent.purpose_scope.contains(grant.purpose_scope):
            reasons.append(B2AuthorizationReason.PURPOSE_SCOPE_INCONSISTENT)

        common = dict(
            evidence_id=evidence_id,
            grant_reference=grant.grant_id,
            authority_reference=grant.authority_reference,
            d3_reference=grant.d3_reference,
            t4_reference=grant.t4_reference,
            aav_reference=grant.aav_reference,
            uodl_reference=grant.uodl_reference,
            purpose_scope=grant.purpose_scope,
            evaluated_at=evaluated_at,
            contract_version=B2_AUTHORIZATION_CONTRACT_VERSION,
        )
        if reasons:
            return B2NegativeGovernanceEvidence(
                decision=B2AuthorizationDecision.DENIED,
                reasons=tuple(dict.fromkeys(reasons)),
                **common,
            )
        return B2AuthorizationEvaluationEvidence(
            decision=B2AuthorizationDecision.EFFECTIVE,
            reasons=(B2AuthorizationReason.ALL_BINDINGS_EFFECTIVE,),
            **common,
        )


def _t4_matches(grant: B2Grant, receipt: B2T4GrantReceipt) -> bool:
    return (
        receipt.receipt_reference == grant.t4_reference
        and receipt.grant_reference == grant.grant_id
        and receipt.authority_reference == grant.authority_reference
        and receipt.d3_reference == grant.d3_reference
        and receipt.purpose_scope == grant.purpose_scope
    )


def _aav_matches(grant: B2Grant, binding: B2AAVBinding) -> bool:
    return (
        binding.aav_reference == grant.aav_reference
        and binding.grant_reference == grant.grant_id
        and binding.authority_reference == grant.authority_reference
        and binding.d3_reference == grant.d3_reference
        and binding.purpose_scope == grant.purpose_scope
    )


def _uodl_matches(
    grant: B2Grant, aav: B2AAVBinding, binding: B2UODLBinding
) -> bool:
    return (
        binding.uodl_reference == grant.uodl_reference
        and binding.grant_reference == grant.grant_id
        and binding.aav_reference == aav.aav_reference
        and binding.operation is B2UODLOperation.REFERENCE_ONLY
    )


def _evidence(value: object, decision: B2AuthorizationDecision) -> None:
    _reference(getattr(value, "evidence_id"), "evidence_id", "b2-evidence:")
    _reference(getattr(value, "grant_reference"), "grant_reference", "b2-grant:")
    if not isinstance(getattr(value, "authority_reference"), B2AuthorityId):
        raise TypeError("authority_reference must be a B2AuthorityId")
    _reference(getattr(value, "d3_reference"), "d3_reference", "d3:")
    _reference(getattr(value, "t4_reference"), "t4_reference", "t4:")
    _reference(getattr(value, "aav_reference"), "aav_reference", "aav:")
    _reference(getattr(value, "uodl_reference"), "uodl_reference", "uodl:")
    _scope(getattr(value, "purpose_scope"))
    _aware(getattr(value, "evaluated_at"), "evaluated_at")
    if getattr(value, "decision") is not decision:
        raise ValueError("evidence has an invalid decision")
    _typed_unique_nonempty(
        getattr(value, "reasons"), B2AuthorizationReason, "reasons"
    )
    if getattr(value, "contract_version") != B2_AUTHORIZATION_CONTRACT_VERSION:
        raise ValueError("contract_version is invalid")


def _effective_at(
    evaluated_at: datetime,
    effective_from: datetime,
    effective_until: Optional[datetime],
    revoked_at: Optional[datetime],
) -> bool:
    if evaluated_at < effective_from:
        return False
    if effective_until is not None and evaluated_at >= effective_until:
        return False
    if revoked_at is not None and evaluated_at >= revoked_at:
        return False
    return True


def _temporal(
    effective_from: datetime,
    effective_until: Optional[datetime],
    revoked_at: Optional[datetime],
) -> None:
    _aware(effective_from, "effective_from")
    if effective_until is not None:
        _aware(effective_until, "effective_until")
        if effective_until <= effective_from:
            raise ValueError("effective_until must be after effective_from")
    if revoked_at is not None:
        _aware(revoked_at, "revoked_at")


def _reference(value: object, name: str, *prefixes: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("{} must be a non-empty reference".format(name))
    if not any(value.startswith(prefix) for prefix in prefixes):
        raise ValueError("{} has an invalid reference family".format(name))
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-._:")
    if any(character not in allowed for character in value):
        raise ValueError("{} must be a non-personal machine reference".format(name))


def _scope(value: object) -> None:
    if not isinstance(value, B2PurposeScope):
        raise TypeError("purpose_scope must be a B2PurposeScope")


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _typed_unique_nonempty(
    values: object, expected: type, name: str
) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not values:
        raise ValueError("{} must not be empty".format(name))
    if any(not isinstance(value, expected) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _provenance(value: object) -> None:
    if not isinstance(value, B2AuthorizationProvenance):
        raise TypeError("provenance must be a B2AuthorizationProvenance")
