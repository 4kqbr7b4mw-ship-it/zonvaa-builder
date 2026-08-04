"""Immutable ADR-0065 capability-invocation resolution without execution power."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple

from governance.b2_authorization import B2AuthorityId, B2PurposeScope
from governance.b2_provider_authorization import (
    B2ProviderAuthorizationId,
)
from governance.b2_provider_identity import (
    B2CapabilityDescriptor,
    B2NonPersonalReferenceId,
    B2ProviderIdentityId,
)
from governance.b2_purpose_uodl_binding import (
    B2BindingProvenance,
    B2PurposeBindingId,
    B2PurposeUODLBindingFoundation,
    B2PurposeUODLBindingFoundationValidator,
    B2UODLMappingId,
)


B2_CAPABILITY_INVOCATION_CONTRACT_VERSION = "1.0"


class B2CapabilityInvocationDecisionResult(str, Enum):
    CONSISTENT_FOR_NON_EXECUTING_RESOLUTION = (
        "CONSISTENT_FOR_NON_EXECUTING_RESOLUTION"
    )
    REJECTED_WITH_CONTROLLED_STOP = "REJECTED_WITH_CONTROLLED_STOP"


class B2CapabilityInvocationAssertion(str, Enum):
    NO_EXECUTION_OCCURRED = "NO_EXECUTION_OCCURRED"
    CONTROLLED_STOP = "CONTROLLED_STOP"


class B2CapabilityInvocationObservationScope(str, Enum):
    REFERENCE_BINDING = "REFERENCE_BINDING"
    REQUEST_EVALUATION = "REQUEST_EVALUATION"
    MECHANICAL_DECISION = "MECHANICAL_DECISION"
    INVOCATION_EVIDENCE = "INVOCATION_EVIDENCE"
    EVALUATION_RECEIPT = "EVALUATION_RECEIPT"
    CONTROLLED_RESOLUTION = "CONTROLLED_RESOLUTION"


class B2CapabilityInvocationViolation(str, Enum):
    UPSTREAM_FOUNDATION_INEFFECTIVE = "UPSTREAM_FOUNDATION_INEFFECTIVE"
    CORRIDOR_REFERENCE_MISMATCH = "CORRIDOR_REFERENCE_MISMATCH"
    AUTHORITY_REFERENCE_MISMATCH = "AUTHORITY_REFERENCE_MISMATCH"
    GRANT_REFERENCE_MISMATCH = "GRANT_REFERENCE_MISMATCH"
    PROVIDER_IDENTITY_MISMATCH = "PROVIDER_IDENTITY_MISMATCH"
    PROVIDER_AUTHORIZATION_MISMATCH = "PROVIDER_AUTHORIZATION_MISMATCH"
    PURPOSE_BINDING_MISMATCH = "PURPOSE_BINDING_MISMATCH"
    UODL_MAPPING_MISMATCH = "UODL_MAPPING_MISMATCH"
    CAPABILITY_BINDING_MISMATCH = "CAPABILITY_BINDING_MISMATCH"
    CAPABILITY_NOT_DESCRIBED = "CAPABILITY_NOT_DESCRIBED"
    PURPOSE_SCOPE_EXPANSION = "PURPOSE_SCOPE_EXPANSION"
    EVALUATION_TIME_MISMATCH = "EVALUATION_TIME_MISMATCH"


@dataclass(frozen=True)
class B2CapabilityInvocationRequestId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "request_id", "b2-capability-invocation-request:")


@dataclass(frozen=True)
class B2CapabilityInvocationBindingId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "binding_id", "b2-capability-invocation-binding:")


@dataclass(frozen=True)
class B2CapabilityInvocationDecisionId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "decision_id", "b2-capability-invocation-decision:")


@dataclass(frozen=True)
class B2CapabilityInvocationEvidenceId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "evidence_id", "b2-capability-invocation-evidence:")


@dataclass(frozen=True)
class B2CapabilityInvocationReceiptId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "receipt_id", "b2-capability-invocation-receipt:")


@dataclass(frozen=True)
class B2CapabilityInvocationResolutionSnapshotId:
    value: str

    def __post_init__(self) -> None:
        _reference(
            self.value,
            "resolution_snapshot_id",
            "b2-capability-invocation-resolution-snapshot:",
        )


@dataclass(frozen=True)
class B2CapabilityInvocationIntent:
    capability_descriptor: B2CapabilityDescriptor
    purpose_scope: B2PurposeScope

    def __post_init__(self) -> None:
        _instance(
            self.capability_descriptor,
            B2CapabilityDescriptor,
            "capability_descriptor",
        )
        _instance(self.purpose_scope, B2PurposeScope, "purpose_scope")


@dataclass(frozen=True)
class B2CapabilityInvocationBinding:
    binding_id: B2CapabilityInvocationBindingId
    provider_identity_reference: B2ProviderIdentityId
    provider_authorization_reference: B2ProviderAuthorizationId
    capability_descriptor: B2CapabilityDescriptor
    purpose_binding_reference: B2PurposeBindingId
    uodl_mapping_reference: B2UODLMappingId
    evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    bound_at: datetime
    observation_scope: B2CapabilityInvocationObservationScope

    def __post_init__(self) -> None:
        _instance(self.binding_id, B2CapabilityInvocationBindingId, "binding_id")
        _instance(
            self.provider_identity_reference,
            B2ProviderIdentityId,
            "provider_identity_reference",
        )
        _instance(
            self.provider_authorization_reference,
            B2ProviderAuthorizationId,
            "provider_authorization_reference",
        )
        _instance(
            self.capability_descriptor,
            B2CapabilityDescriptor,
            "capability_descriptor",
        )
        _instance(
            self.purpose_binding_reference,
            B2PurposeBindingId,
            "purpose_binding_reference",
        )
        _instance(
            self.uodl_mapping_reference,
            B2UODLMappingId,
            "uodl_mapping_reference",
        )
        _evidence_references(self.evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        _aware(self.bound_at, "bound_at")
        if self.bound_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "binding provenance time differs")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.REFERENCE_BINDING,
        )


@dataclass(frozen=True)
class B2CapabilityInvocationRequest:
    request_id: B2CapabilityInvocationRequestId
    data_corridor_reference: str
    authority_reference: B2AuthorityId
    grant_reference: str
    provider_identity_reference: B2ProviderIdentityId
    provider_authorization_reference: B2ProviderAuthorizationId
    purpose_binding_reference: B2PurposeBindingId
    uodl_mapping_reference: B2UODLMappingId
    invocation_binding_reference: B2CapabilityInvocationBindingId
    intent: B2CapabilityInvocationIntent
    evaluated_at: datetime
    evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    observation_scope: B2CapabilityInvocationObservationScope

    def __post_init__(self) -> None:
        _instance(self.request_id, B2CapabilityInvocationRequestId, "request_id")
        _reference(self.data_corridor_reference, "data_corridor_reference", "b2-corridor-")
        _instance(self.authority_reference, B2AuthorityId, "authority_reference")
        _reference(self.grant_reference, "grant_reference", "b2-grant:")
        _instance(
            self.provider_identity_reference,
            B2ProviderIdentityId,
            "provider_identity_reference",
        )
        _instance(
            self.provider_authorization_reference,
            B2ProviderAuthorizationId,
            "provider_authorization_reference",
        )
        _instance(
            self.purpose_binding_reference,
            B2PurposeBindingId,
            "purpose_binding_reference",
        )
        _instance(self.uodl_mapping_reference, B2UODLMappingId, "uodl_mapping_reference")
        _instance(
            self.invocation_binding_reference,
            B2CapabilityInvocationBindingId,
            "invocation_binding_reference",
        )
        _instance(self.intent, B2CapabilityInvocationIntent, "intent")
        _aware(self.evaluated_at, "evaluated_at")
        _evidence_references(self.evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        if self.evaluated_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "request provenance time differs")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.REQUEST_EVALUATION,
        )


@dataclass(frozen=True)
class B2CapabilityInvocationDecision:
    decision_id: B2CapabilityInvocationDecisionId
    request_reference: B2CapabilityInvocationRequestId
    result: B2CapabilityInvocationDecisionResult
    evaluated_at: datetime
    canonical_rule_references: Tuple[B2NonPersonalReferenceId, ...]
    violations: Tuple[B2CapabilityInvocationViolation, ...]
    assertions: Tuple[B2CapabilityInvocationAssertion, ...]
    provenance: B2BindingProvenance
    observation_scope: B2CapabilityInvocationObservationScope

    def __post_init__(self) -> None:
        _instance(self.decision_id, B2CapabilityInvocationDecisionId, "decision_id")
        _instance(
            self.request_reference,
            B2CapabilityInvocationRequestId,
            "request_reference",
        )
        _enum(self.result, B2CapabilityInvocationDecisionResult, "result")
        _aware(self.evaluated_at, "evaluated_at")
        _evidence_references(self.canonical_rule_references)
        _typed_unique_tuple(self.violations, B2CapabilityInvocationViolation, "violations")
        _assertions(self.assertions, require_controlled_stop=True)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        if self.evaluated_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "decision provenance time differs")
        if self.result is B2CapabilityInvocationDecisionResult.CONSISTENT_FOR_NON_EXECUTING_RESOLUTION:
            if self.violations:
                _invalid("DECISION_VIOLATIONS_INVALID", "positive decision has violations")
        elif not self.violations:
            _invalid("DECISION_VIOLATIONS_MISSING", "rejection requires violations")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.MECHANICAL_DECISION,
        )


@dataclass(frozen=True)
class B2CapabilityInvocationEvidence:
    evidence_id: B2CapabilityInvocationEvidenceId
    request_reference: B2CapabilityInvocationRequestId
    binding_reference: B2CapabilityInvocationBindingId
    decision_reference: B2CapabilityInvocationDecisionId
    canonical_input_references: Tuple[B2NonPersonalReferenceId, ...]
    canonical_rule_references: Tuple[B2NonPersonalReferenceId, ...]
    consistency_references: Tuple[B2NonPersonalReferenceId, ...]
    violations: Tuple[B2CapabilityInvocationViolation, ...]
    assertions: Tuple[B2CapabilityInvocationAssertion, ...]
    evaluated_at: datetime
    provenance: B2BindingProvenance
    observation_scope: B2CapabilityInvocationObservationScope
    contract_version: str = B2_CAPABILITY_INVOCATION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _instance(self.evidence_id, B2CapabilityInvocationEvidenceId, "evidence_id")
        _instance(self.request_reference, B2CapabilityInvocationRequestId, "request_reference")
        _instance(self.binding_reference, B2CapabilityInvocationBindingId, "binding_reference")
        _instance(self.decision_reference, B2CapabilityInvocationDecisionId, "decision_reference")
        _evidence_references(self.canonical_input_references)
        _evidence_references(self.canonical_rule_references)
        _typed_unique_tuple(
            self.consistency_references,
            B2NonPersonalReferenceId,
            "consistency_references",
        )
        _typed_unique_tuple(self.violations, B2CapabilityInvocationViolation, "violations")
        if bool(self.consistency_references) == bool(self.violations):
            _invalid(
                "EVIDENCE_FINDINGS_INVALID",
                "evidence requires either consistencies or violations",
            )
        _assertions(self.assertions, require_controlled_stop=True)
        _aware(self.evaluated_at, "evaluated_at")
        _instance(self.provenance, B2BindingProvenance, "provenance")
        if self.evaluated_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "evidence provenance time differs")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.INVOCATION_EVIDENCE,
        )
        if self.contract_version != B2_CAPABILITY_INVOCATION_CONTRACT_VERSION:
            raise ValueError("contract_version is invalid")


@dataclass(frozen=True)
class B2CapabilityInvocationReceipt:
    receipt_id: B2CapabilityInvocationReceiptId
    request_reference: B2CapabilityInvocationRequestId
    decision_reference: B2CapabilityInvocationDecisionId
    evidence_reference: B2CapabilityInvocationEvidenceId
    assertions: Tuple[B2CapabilityInvocationAssertion, ...]
    recorded_at: datetime
    provenance: B2BindingProvenance
    observation_scope: B2CapabilityInvocationObservationScope

    def __post_init__(self) -> None:
        _instance(self.receipt_id, B2CapabilityInvocationReceiptId, "receipt_id")
        _instance(self.request_reference, B2CapabilityInvocationRequestId, "request_reference")
        _instance(self.decision_reference, B2CapabilityInvocationDecisionId, "decision_reference")
        _instance(self.evidence_reference, B2CapabilityInvocationEvidenceId, "evidence_reference")
        if self.assertions != (B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,):
            _invalid("RECEIPT_ASSERTION_INVALID", "receipt only confirms no execution")
        _aware(self.recorded_at, "recorded_at")
        _instance(self.provenance, B2BindingProvenance, "provenance")
        if self.recorded_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "receipt provenance time differs")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.EVALUATION_RECEIPT,
        )


@dataclass(frozen=True)
class B2CapabilityInvocationResolutionSnapshot:
    resolution_snapshot_id: B2CapabilityInvocationResolutionSnapshotId
    request_reference: B2CapabilityInvocationRequestId
    binding_reference: B2CapabilityInvocationBindingId
    decision_reference: B2CapabilityInvocationDecisionId
    evidence_reference: B2CapabilityInvocationEvidenceId
    receipt_reference: B2CapabilityInvocationReceiptId
    assertions: Tuple[B2CapabilityInvocationAssertion, ...]
    resolved_at: datetime
    provenance: B2BindingProvenance
    observation_scope: B2CapabilityInvocationObservationScope

    def __post_init__(self) -> None:
        _instance(
            self.resolution_snapshot_id,
            B2CapabilityInvocationResolutionSnapshotId,
            "resolution_snapshot_id",
        )
        _instance(self.request_reference, B2CapabilityInvocationRequestId, "request_reference")
        _instance(self.binding_reference, B2CapabilityInvocationBindingId, "binding_reference")
        _instance(self.decision_reference, B2CapabilityInvocationDecisionId, "decision_reference")
        _instance(self.evidence_reference, B2CapabilityInvocationEvidenceId, "evidence_reference")
        _instance(self.receipt_reference, B2CapabilityInvocationReceiptId, "receipt_reference")
        _assertions(self.assertions, require_controlled_stop=True)
        _aware(self.resolved_at, "resolved_at")
        _instance(self.provenance, B2BindingProvenance, "provenance")
        if self.resolved_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "snapshot provenance time differs")
        _exact_scope(
            self.observation_scope,
            B2CapabilityInvocationObservationScope.CONTROLLED_RESOLUTION,
        )


@dataclass(frozen=True)
class B2CapabilityInvocationFoundation:
    upstream_foundation: B2PurposeUODLBindingFoundation
    binding: B2CapabilityInvocationBinding
    request: B2CapabilityInvocationRequest
    decision: B2CapabilityInvocationDecision
    evidence: B2CapabilityInvocationEvidence
    receipt: B2CapabilityInvocationReceipt
    resolution_snapshot: B2CapabilityInvocationResolutionSnapshot

    def __post_init__(self) -> None:
        for value, expected, name in (
            (self.upstream_foundation, B2PurposeUODLBindingFoundation, "upstream_foundation"),
            (self.binding, B2CapabilityInvocationBinding, "binding"),
            (self.request, B2CapabilityInvocationRequest, "request"),
            (self.decision, B2CapabilityInvocationDecision, "decision"),
            (self.evidence, B2CapabilityInvocationEvidence, "evidence"),
            (self.receipt, B2CapabilityInvocationReceipt, "receipt"),
            (
                self.resolution_snapshot,
                B2CapabilityInvocationResolutionSnapshot,
                "resolution_snapshot",
            ),
        ):
            _instance(value, expected, name)


class B2CapabilityInvocationValidator:
    """Validate immutable supplied references without clocks, state, or execution."""

    def validate(
        self,
        binding: B2CapabilityInvocationBinding,
        request: B2CapabilityInvocationRequest,
        upstream_foundation: B2PurposeUODLBindingFoundation,
    ) -> B2CapabilityInvocationRequest:
        violations = _collect_violations(binding, request, upstream_foundation)
        if violations:
            _invalid(violations[0].value, "invocation reference chain is inconsistent")
        return request


class B2CapabilityInvocationEvaluator:
    """Resolve a supplied request into evidence and a mandatory controlled stop."""

    def evaluate(
        self,
        binding: B2CapabilityInvocationBinding,
        request: B2CapabilityInvocationRequest,
        upstream_foundation: B2PurposeUODLBindingFoundation,
        decision_id: B2CapabilityInvocationDecisionId,
        evidence_id: B2CapabilityInvocationEvidenceId,
        receipt_id: B2CapabilityInvocationReceiptId,
        resolution_snapshot_id: B2CapabilityInvocationResolutionSnapshotId,
        canonical_rule_references: Tuple[B2NonPersonalReferenceId, ...],
        canonical_input_references: Tuple[B2NonPersonalReferenceId, ...],
        consistency_references: Tuple[B2NonPersonalReferenceId, ...],
    ) -> B2CapabilityInvocationFoundation:
        _instance(decision_id, B2CapabilityInvocationDecisionId, "decision_id")
        _instance(evidence_id, B2CapabilityInvocationEvidenceId, "evidence_id")
        _instance(receipt_id, B2CapabilityInvocationReceiptId, "receipt_id")
        _instance(
            resolution_snapshot_id,
            B2CapabilityInvocationResolutionSnapshotId,
            "resolution_snapshot_id",
        )
        _evidence_references(canonical_rule_references)
        _evidence_references(canonical_input_references)
        _typed_unique_tuple(
            consistency_references,
            B2NonPersonalReferenceId,
            "consistency_references",
        )
        violations = _collect_violations(binding, request, upstream_foundation)
        if not violations and not consistency_references:
            raise ValueError("positive resolution requires consistency references")
        result = (
            B2CapabilityInvocationDecisionResult.REJECTED_WITH_CONTROLLED_STOP
            if violations
            else B2CapabilityInvocationDecisionResult.CONSISTENT_FOR_NON_EXECUTING_RESOLUTION
        )
        assertions = (
            B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,
            B2CapabilityInvocationAssertion.CONTROLLED_STOP,
        )
        decision = B2CapabilityInvocationDecision(
            decision_id=decision_id,
            request_reference=request.request_id,
            result=result,
            evaluated_at=request.evaluated_at,
            canonical_rule_references=canonical_rule_references,
            violations=violations,
            assertions=assertions,
            provenance=request.provenance,
            observation_scope=B2CapabilityInvocationObservationScope.MECHANICAL_DECISION,
        )
        evidence = B2CapabilityInvocationEvidence(
            evidence_id=evidence_id,
            request_reference=request.request_id,
            binding_reference=binding.binding_id,
            decision_reference=decision_id,
            canonical_input_references=canonical_input_references,
            canonical_rule_references=canonical_rule_references,
            consistency_references=consistency_references if not violations else (),
            violations=violations,
            assertions=assertions,
            evaluated_at=request.evaluated_at,
            provenance=request.provenance,
            observation_scope=B2CapabilityInvocationObservationScope.INVOCATION_EVIDENCE,
        )
        receipt = B2CapabilityInvocationReceipt(
            receipt_id=receipt_id,
            request_reference=request.request_id,
            decision_reference=decision_id,
            evidence_reference=evidence_id,
            assertions=(B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,),
            recorded_at=request.evaluated_at,
            provenance=request.provenance,
            observation_scope=B2CapabilityInvocationObservationScope.EVALUATION_RECEIPT,
        )
        snapshot = B2CapabilityInvocationResolutionSnapshot(
            resolution_snapshot_id=resolution_snapshot_id,
            request_reference=request.request_id,
            binding_reference=binding.binding_id,
            decision_reference=decision_id,
            evidence_reference=evidence_id,
            receipt_reference=receipt_id,
            assertions=assertions,
            resolved_at=request.evaluated_at,
            provenance=request.provenance,
            observation_scope=B2CapabilityInvocationObservationScope.CONTROLLED_RESOLUTION,
        )
        return B2CapabilityInvocationFoundation(
            upstream_foundation=upstream_foundation,
            binding=binding,
            request=request,
            decision=decision,
            evidence=evidence,
            receipt=receipt,
            resolution_snapshot=snapshot,
        )


class B2CapabilityInvocationFoundationValidator:
    """Reconstruct and compare the complete non-executing ADR-0065 resolution."""

    def validate(
        self, foundation: B2CapabilityInvocationFoundation
    ) -> B2CapabilityInvocationFoundation:
        _instance(foundation, B2CapabilityInvocationFoundation, "foundation")
        expected = B2CapabilityInvocationEvaluator().evaluate(
            binding=foundation.binding,
            request=foundation.request,
            upstream_foundation=foundation.upstream_foundation,
            decision_id=foundation.decision.decision_id,
            evidence_id=foundation.evidence.evidence_id,
            receipt_id=foundation.receipt.receipt_id,
            resolution_snapshot_id=foundation.resolution_snapshot.resolution_snapshot_id,
            canonical_rule_references=foundation.decision.canonical_rule_references,
            canonical_input_references=foundation.evidence.canonical_input_references,
            consistency_references=foundation.evidence.consistency_references,
        )
        if expected != foundation:
            _invalid("FOUNDATION_EVIDENCE_MISMATCH", "foundation resolution differs")
        return foundation


class B2CapabilityInvocationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _collect_violations(
    binding: B2CapabilityInvocationBinding,
    request: B2CapabilityInvocationRequest,
    upstream: B2PurposeUODLBindingFoundation,
) -> Tuple[B2CapabilityInvocationViolation, ...]:
    _instance(binding, B2CapabilityInvocationBinding, "binding")
    _instance(request, B2CapabilityInvocationRequest, "request")
    _instance(upstream, B2PurposeUODLBindingFoundation, "upstream_foundation")
    violations = []
    try:
        B2PurposeUODLBindingFoundationValidator().validate(upstream)
    except (TypeError, ValueError):
        violations.append(B2CapabilityInvocationViolation.UPSTREAM_FOUNDATION_INEFFECTIVE)
    base = upstream.foundation
    if request.data_corridor_reference != base.data_corridor.corridor.corridor_id:
        violations.append(B2CapabilityInvocationViolation.CORRIDOR_REFERENCE_MISMATCH)
    if request.authority_reference != base.authority.authority_id:
        violations.append(B2CapabilityInvocationViolation.AUTHORITY_REFERENCE_MISMATCH)
    if request.grant_reference != base.grant.grant_id:
        violations.append(B2CapabilityInvocationViolation.GRANT_REFERENCE_MISMATCH)
    if request.provider_identity_reference != base.provider_identity.identity_id:
        violations.append(B2CapabilityInvocationViolation.PROVIDER_IDENTITY_MISMATCH)
    if (
        request.provider_authorization_reference
        != base.provider_authorization.authorization_id
        or binding.provider_authorization_reference
        != base.provider_authorization.authorization_id
    ):
        violations.append(B2CapabilityInvocationViolation.PROVIDER_AUTHORIZATION_MISMATCH)
    if (
        binding.provider_identity_reference != base.provider_identity.identity_id
        or binding.provider_identity_reference != request.provider_identity_reference
    ):
        violations.append(B2CapabilityInvocationViolation.PROVIDER_IDENTITY_MISMATCH)
    if request.purpose_binding_reference != upstream.purpose_binding.binding_id or (
        binding.purpose_binding_reference != upstream.purpose_binding.binding_id
    ):
        violations.append(B2CapabilityInvocationViolation.PURPOSE_BINDING_MISMATCH)
    if request.uodl_mapping_reference != upstream.uodl_mapping.mapping_id or (
        binding.uodl_mapping_reference != upstream.uodl_mapping.mapping_id
    ):
        violations.append(B2CapabilityInvocationViolation.UODL_MAPPING_MISMATCH)
    if request.invocation_binding_reference != binding.binding_id:
        violations.append(B2CapabilityInvocationViolation.CAPABILITY_BINDING_MISMATCH)
    if (
        request.intent.capability_descriptor is not binding.capability_descriptor
        or binding.capability_descriptor not in base.provider_identity.capability_descriptors
    ):
        violations.append(B2CapabilityInvocationViolation.CAPABILITY_NOT_DESCRIBED)
    if not upstream.purpose_binding.canonical_scope.contains(request.intent.purpose_scope):
        violations.append(B2CapabilityInvocationViolation.PURPOSE_SCOPE_EXPANSION)
    if request.evaluated_at != base.evaluated_at:
        violations.append(B2CapabilityInvocationViolation.EVALUATION_TIME_MISMATCH)
    return tuple(dict.fromkeys(violations))


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
        {"person", "personal", "human", "name", "email", "contact", "account", "user", "device"}
    ):
        raise ValueError("{} must not identify a natural person".format(name))


def _evidence_references(values: object) -> None:
    if not isinstance(values, tuple):
        raise TypeError("references must be a tuple")
    if not values:
        raise ValueError("references must not be empty")
    _typed_unique_tuple(values, B2NonPersonalReferenceId, "references")


def _typed_unique_tuple(values: object, expected: type, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if any(not isinstance(value, expected) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _assertions(
    values: object, *, require_controlled_stop: bool
) -> None:
    _typed_unique_tuple(values, B2CapabilityInvocationAssertion, "assertions")
    required = {B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED}
    if require_controlled_stop:
        required.add(B2CapabilityInvocationAssertion.CONTROLLED_STOP)
    if set(values) != required:
        _invalid("ASSERTIONS_INVALID", "the ratified non-execution assertions are required")


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _instance(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _enum(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _exact_scope(
    value: object, expected: B2CapabilityInvocationObservationScope
) -> None:
    if value is not expected:
        _invalid("OBSERVATION_SCOPE_INVALID", "observation scope differs")


def _invalid(code: str, message: str) -> None:
    raise B2CapabilityInvocationValidationError(code, message)
