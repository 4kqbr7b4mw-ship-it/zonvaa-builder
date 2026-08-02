"""Immutable ADR-0050 invocation evidence without execution authority."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from governance.authority import (
    AuthorityActorClass,
    AuthorityCapability,
    AuthorityControlLevel,
    AuthorityDefinition,
    AuthorityProvenance,
    AuthorityReviewStatus,
)
from governance.provider_authorization import (
    AuthorizationExpirationEvidence,
    AuthorizationRestorationEvidence,
    AuthorizationRevocationEvidence,
    AuthorizationSuspensionEvidence,
    AuthorizationUncertaintyStatus,
    GuardianProviderAuthorizationPackage,
    GuardianProviderAuthorizationValidator,
    ProviderAuthorizationGrant,
    ProviderAuthorizationResolutionSnapshot,
    ProviderAuthorizationStatus,
    ProviderAuthorizationValidationError,
    ProviderIdentity,
)
from guardian_understanding.answer_boundary import (
    AnswerBoundaryContract,
    AnswerOperatingMode,
    GuardianAnswerBoundaryValidator,
)


class InvocationOperationMode(str, Enum):
    READ_ONLY = "READ_ONLY"
    SIMULATION = "SIMULATION"
    DEGRADED = "DEGRADED"
    READ_WRITE = "READ_WRITE"
    PRIVILEGED = "PRIVILEGED"


class InvocationDataScope(str, Enum):
    NON_PERSONAL = "NON_PERSONAL"
    DEPERSONALIZED = "DEPERSONALIZED"
    PERSONAL = "PERSONAL"


class InvocationContextBindingType(str, Enum):
    JURISDICTION = "JURISDICTION"
    PURPOSE = "PURPOSE"
    CONVERSATION_OR_JOURNEY = "CONVERSATION_OR_JOURNEY"
    DATA_SCOPE = "DATA_SCOPE"


class InvocationDecisionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class InvocationDecisionReason(str, Enum):
    PROVIDER_UNKNOWN = "PROVIDER_UNKNOWN"
    AUTHORIZATION_MISSING = "AUTHORIZATION_MISSING"
    AUTHORIZATION_NOT_AUTHORIZED = "AUTHORIZATION_NOT_AUTHORIZED"
    AUTHORIZATION_SUSPENDED = "AUTHORIZATION_SUSPENDED"
    AUTHORIZATION_REVOKED = "AUTHORIZATION_REVOKED"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    CAPABILITY_DENIED = "CAPABILITY_DENIED"
    RESPONSIBILITY_BOUNDARY_EXCEEDED = "RESPONSIBILITY_BOUNDARY_EXCEEDED"
    CONTROL_LEVEL_INSUFFICIENT = "CONTROL_LEVEL_INSUFFICIENT"
    JOINT_CONTROL_INCOMPLETE = "JOINT_CONTROL_INCOMPLETE"
    OPERATION_MODE_NOT_ALLOWED = "OPERATION_MODE_NOT_ALLOWED"
    CLASSIFICATION_TOO_HIGH = "CLASSIFICATION_TOO_HIGH"
    CONTEXT_BINDING_MISSING = "CONTEXT_BINDING_MISSING"
    SOURCE_BINDING_MISSING = "SOURCE_BINDING_MISSING"
    RESOLUTION_SNAPSHOT_MISSING = "RESOLUTION_SNAPSHOT_MISSING"
    RESOLUTION_SNAPSHOT_INCONSISTENT = "RESOLUTION_SNAPSHOT_INCONSISTENT"
    INPUT_CONTRACT_MISSING = "INPUT_CONTRACT_MISSING"
    PROVENANCE_INCONSISTENT = "PROVENANCE_INCONSISTENT"
    GOVERNANCE_GAP = "GOVERNANCE_GAP"


class InvocationCheck(str, Enum):
    AUTHORITY_MODEL = "AUTHORITY_MODEL"
    PROVIDER_AUTHORIZATION_PACKAGE = "PROVIDER_AUTHORIZATION_PACKAGE"
    PROVIDER_IDENTITY = "PROVIDER_IDENTITY"
    AUTHORIZATION_GRANT = "AUTHORIZATION_GRANT"
    AUTHORITY_AND_CAPABILITY = "AUTHORITY_AND_CAPABILITY"
    RESPONSIBILITY_BOUNDARY = "RESPONSIBILITY_BOUNDARY"
    CONTROL_LEVELS = "CONTROL_LEVELS"
    JOINT_CONTROL = "JOINT_CONTROL"
    LIFECYCLE = "LIFECYCLE"
    ANSWER_BOUNDARY = "ANSWER_BOUNDARY"
    OPERATION_MODE = "OPERATION_MODE"
    CONTEXT_BINDINGS = "CONTEXT_BINDINGS"
    SOURCE_BINDINGS = "SOURCE_BINDINGS"
    INPUT_CONTRACT = "INPUT_CONTRACT"
    RESOLUTION_SNAPSHOT = "RESOLUTION_SNAPSHOT"
    PROVENANCE = "PROVENANCE"


class InvocationReceiptValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"


class CapabilityInvocationPackageCapability(str, Enum):
    DESCRIBE_INVOCATION = "DESCRIBE_INVOCATION"
    EXECUTE_CAPABILITY = "EXECUTE_CAPABILITY"
    ACTIVATE_PROVIDER = "ACTIVATE_PROVIDER"
    ACTIVATE_RUNTIME = "ACTIVATE_RUNTIME"
    SELECT_PROVIDER = "SELECT_PROVIDER"
    AUTHORIZE_PROVIDER = "AUTHORIZE_PROVIDER"
    MODIFY_STATE = "MODIFY_STATE"
    PERSIST_RECEIPT = "PERSIST_RECEIPT"
    WRITE_AUDIT_LOG = "WRITE_AUDIT_LOG"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    START_WORKFLOW = "START_WORKFLOW"


NON_EXECUTING_INVOCATION_CAPABILITIES = (
    CapabilityInvocationPackageCapability.DESCRIBE_INVOCATION,
)

ALLOWED_INVOCATION_OPERATION_MODES = (
    InvocationOperationMode.READ_ONLY,
    InvocationOperationMode.SIMULATION,
    InvocationOperationMode.DEGRADED,
)

REQUIRED_INVOCATION_CHECKS = tuple(InvocationCheck)


@dataclass(frozen=True)
class InvocationContextBinding:
    binding_id: str
    binding_type: InvocationContextBindingType
    reference: str

    def __post_init__(self) -> None:
        _text(self.binding_id, "binding_id")
        _enum(self.binding_type, InvocationContextBindingType, "binding_type")
        _text(self.reference, "reference")


@dataclass(frozen=True)
class CapabilityInvocationRequest:
    invocation_id: str
    requestor_reference: str
    provider_reference: str
    authorization_reference: str
    authority_reference: str
    capability: AuthorityCapability
    requested_operation: str
    operation_mode: InvocationOperationMode
    maximum_answer_mode: AnswerOperatingMode
    answer_boundary_reference: str
    context_bindings: Tuple[InvocationContextBinding, ...]
    data_scope: InvocationDataScope
    source_chain_references: Tuple[str, ...]
    source_chains_required: bool
    input_contract_reference: Optional[str]
    input_schema_version: Optional[str]
    input_reference: str
    input_constraints: Tuple[str, ...]
    required_control_levels: Tuple[AuthorityControlLevel, ...]
    provided_joint_actor_classes: Tuple[AuthorityActorClass, ...]
    requested_at: datetime
    uncertainty_status: AuthorizationUncertaintyStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.invocation_id, "invocation_id"),
            (self.requestor_reference, "requestor_reference"),
            (self.provider_reference, "provider_reference"),
            (self.authorization_reference, "authorization_reference"),
            (self.authority_reference, "authority_reference"),
            (self.requested_operation, "requested_operation"),
            (self.answer_boundary_reference, "answer_boundary_reference"),
            (self.input_reference, "input_reference"),
        ):
            _text(value, name)
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.operation_mode, InvocationOperationMode, "operation_mode")
        _enum(self.maximum_answer_mode, AnswerOperatingMode, "maximum_answer_mode")
        _typed_unique_nonempty(
            self.context_bindings,
            InvocationContextBinding,
            "context_bindings",
        )
        binding_ids = tuple(item.binding_id for item in self.context_bindings)
        if len(binding_ids) != len(set(binding_ids)):
            raise ValueError("context binding ids must be unique")
        binding_types = tuple(item.binding_type for item in self.context_bindings)
        if len(binding_types) != len(set(binding_types)):
            raise ValueError("context binding types must be unique")
        _enum(self.data_scope, InvocationDataScope, "data_scope")
        for value, name in (
            (self.input_contract_reference, "input_contract_reference"),
            (self.input_schema_version, "input_schema_version"),
        ):
            if value is not None:
                _text(value, name)
        _strings(self.source_chain_references, "source_chain_references", False)
        if not isinstance(self.source_chains_required, bool):
            raise TypeError("source_chains_required must be a bool")
        _strings(self.input_constraints, "input_constraints", False)
        _typed_unique_nonempty(
            self.required_control_levels,
            AuthorityControlLevel,
            "required_control_levels",
        )
        _typed_unique(
            self.provided_joint_actor_classes,
            AuthorityActorClass,
            "provided_joint_actor_classes",
        )
        _aware(self.requested_at, "requested_at")
        _enum(
            self.uncertainty_status,
            AuthorizationUncertaintyStatus,
            "uncertainty_status",
        )
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class CapabilityInvocationDecision:
    decision_id: str
    invocation_reference: str
    status: InvocationDecisionStatus
    reasons: Tuple[InvocationDecisionReason, ...]
    decision_reason: str
    decided_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.decision_id, "decision_id")
        _text(self.invocation_reference, "invocation_reference")
        _enum(self.status, InvocationDecisionStatus, "status")
        _typed_unique(
            self.reasons,
            InvocationDecisionReason,
            "reasons",
        )
        _text(self.decision_reason, "decision_reason")
        _aware(self.decided_at, "decided_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class CapabilityInvocationEvidence:
    evidence_id: str
    invocation_reference: str
    request_reference: str
    decision_reference: str
    checked_provider_reference: Optional[str]
    checked_authorization_reference: Optional[str]
    checked_authority_reference: Optional[str]
    checked_resolution_snapshot_reference: Optional[str]
    checked_lifecycle_evidence_references: Tuple[str, ...]
    checked_answer_mode: AnswerOperatingMode
    checked_operation_mode: InvocationOperationMode
    checked_control_levels: Tuple[AuthorityControlLevel, ...]
    detected_conflicts: Tuple[str, ...]
    validator_references: Tuple[str, ...]
    passed_checks: Tuple[InvocationCheck, ...]
    failed_checks: Tuple[InvocationCheck, ...]
    result: InvocationDecisionStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.evidence_id, "evidence_id"),
            (self.invocation_reference, "invocation_reference"),
            (self.request_reference, "request_reference"),
            (self.decision_reference, "decision_reference"),
        ):
            _text(value, name)
        for value, name in (
            (self.checked_provider_reference, "checked_provider_reference"),
            (
                self.checked_authorization_reference,
                "checked_authorization_reference",
            ),
            (self.checked_authority_reference, "checked_authority_reference"),
            (
                self.checked_resolution_snapshot_reference,
                "checked_resolution_snapshot_reference",
            ),
        ):
            if value is not None:
                _text(value, name)
        _strings(
            self.checked_lifecycle_evidence_references,
            "checked_lifecycle_evidence_references",
            False,
        )
        _enum(self.checked_answer_mode, AnswerOperatingMode, "checked_answer_mode")
        _enum(
            self.checked_operation_mode,
            InvocationOperationMode,
            "checked_operation_mode",
        )
        _typed_unique_nonempty(
            self.checked_control_levels,
            AuthorityControlLevel,
            "checked_control_levels",
        )
        _strings(self.detected_conflicts, "detected_conflicts", False)
        _strings(self.validator_references, "validator_references", True)
        _typed_unique(self.passed_checks, InvocationCheck, "passed_checks")
        _typed_unique(self.failed_checks, InvocationCheck, "failed_checks")
        if set(self.passed_checks) & set(self.failed_checks):
            raise ValueError("a check cannot pass and fail")
        if set(self.passed_checks) | set(self.failed_checks) != set(
            REQUIRED_INVOCATION_CHECKS
        ):
            raise ValueError("evidence must contain the complete check set")
        _enum(self.result, InvocationDecisionStatus, "result")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class GuardianCapabilityInvocationBoundary:
    boundary_id: str
    provider_authorization_package: GuardianProviderAuthorizationPackage
    answer_boundary: AnswerBoundaryContract
    request: CapabilityInvocationRequest
    decision: CapabilityInvocationDecision
    evidence: CapabilityInvocationEvidence
    provenance: AuthorityProvenance
    capabilities: Tuple[CapabilityInvocationPackageCapability, ...] = (
        CapabilityInvocationPackageCapability.DESCRIBE_INVOCATION,
    )

    def __post_init__(self) -> None:
        _text(self.boundary_id, "boundary_id")
        if not isinstance(
            self.provider_authorization_package,
            GuardianProviderAuthorizationPackage,
        ):
            raise TypeError(
                "provider_authorization_package must be a "
                "GuardianProviderAuthorizationPackage"
            )
        if not isinstance(self.answer_boundary, AnswerBoundaryContract):
            raise TypeError("answer_boundary must be an AnswerBoundaryContract")
        if not isinstance(self.request, CapabilityInvocationRequest):
            raise TypeError("request must be a CapabilityInvocationRequest")
        if not isinstance(self.decision, CapabilityInvocationDecision):
            raise TypeError("decision must be a CapabilityInvocationDecision")
        if not isinstance(self.evidence, CapabilityInvocationEvidence):
            raise TypeError("evidence must be a CapabilityInvocationEvidence")
        _provenance(self.provenance)
        _typed_unique_nonempty(
            self.capabilities,
            CapabilityInvocationPackageCapability,
            "capabilities",
        )


@dataclass(frozen=True)
class CapabilityInvocationReceipt:
    receipt_id: str
    invocation_reference: str
    decision_reference: str
    evidence_reference: str
    decision_status: InvocationDecisionStatus
    authority_chain_references: Tuple[str, ...]
    validation_status: InvocationReceiptValidationStatus
    passed_checks: Tuple[InvocationCheck, ...]
    failed_checks: Tuple[InvocationCheck, ...]
    validated_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.receipt_id, "receipt_id"),
            (self.invocation_reference, "invocation_reference"),
            (self.decision_reference, "decision_reference"),
            (self.evidence_reference, "evidence_reference"),
        ):
            _text(value, name)
        _enum(self.decision_status, InvocationDecisionStatus, "decision_status")
        _strings(
            self.authority_chain_references,
            "authority_chain_references",
            True,
        )
        _enum(
            self.validation_status,
            InvocationReceiptValidationStatus,
            "validation_status",
        )
        _typed_unique(self.passed_checks, InvocationCheck, "passed_checks")
        _typed_unique(self.failed_checks, InvocationCheck, "failed_checks")
        _aware(self.validated_at, "validated_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


LifecycleEvidence = (
    AuthorizationRevocationEvidence,
    AuthorizationSuspensionEvidence,
    AuthorizationExpirationEvidence,
    AuthorizationRestorationEvidence,
)


@dataclass(frozen=True)
class CapabilityInvocationResolutionSnapshot:
    snapshot_id: str
    request: CapabilityInvocationRequest
    decision: CapabilityInvocationDecision
    evidence: CapabilityInvocationEvidence
    receipt: CapabilityInvocationReceipt
    provider: ProviderIdentity
    authority: AuthorityDefinition
    authorization: ProviderAuthorizationGrant
    lifecycle_evidence: Tuple[object, ...]
    provider_authorization_snapshot: ProviderAuthorizationResolutionSnapshot
    capability: AuthorityCapability
    operation_mode: InvocationOperationMode
    answer_mode: AnswerOperatingMode
    control_levels: Tuple[AuthorityControlLevel, ...]
    context_bindings: Tuple[InvocationContextBinding, ...]
    source_chain_references: Tuple[str, ...]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    uncertainty_status: AuthorizationUncertaintyStatus
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        for value, item_type, name in (
            (self.request, CapabilityInvocationRequest, "request"),
            (self.decision, CapabilityInvocationDecision, "decision"),
            (self.evidence, CapabilityInvocationEvidence, "evidence"),
            (self.receipt, CapabilityInvocationReceipt, "receipt"),
            (self.provider, ProviderIdentity, "provider"),
            (self.authority, AuthorityDefinition, "authority"),
            (self.authorization, ProviderAuthorizationGrant, "authorization"),
            (
                self.provider_authorization_snapshot,
                ProviderAuthorizationResolutionSnapshot,
                "provider_authorization_snapshot",
            ),
        ):
            if not isinstance(value, item_type):
                raise TypeError("{} has an invalid type".format(name))
        if not isinstance(self.lifecycle_evidence, tuple) or not all(
            isinstance(item, LifecycleEvidence) for item in self.lifecycle_evidence
        ):
            raise TypeError("lifecycle_evidence contains invalid values")
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.operation_mode, InvocationOperationMode, "operation_mode")
        _enum(self.answer_mode, AnswerOperatingMode, "answer_mode")
        _typed_unique_nonempty(
            self.control_levels,
            AuthorityControlLevel,
            "control_levels",
        )
        _typed_unique_nonempty(
            self.context_bindings,
            InvocationContextBinding,
            "context_bindings",
        )
        _strings(self.source_chain_references, "source_chain_references", False)
        _review_pair(self.review_status, self.review_reference)
        _enum(
            self.uncertainty_status,
            AuthorizationUncertaintyStatus,
            "uncertainty_status",
        )
        _provenance(self.provenance)


class CapabilityInvocationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianCapabilityInvocationValidator:
    """Validate and receipt supplied invocation evidence without execution."""

    REQUIRED_VALIDATORS = (
        "GuardianAuthorityModelValidator",
        "GuardianProviderAuthorizationValidator",
        "GuardianAnswerBoundaryValidator",
        "GuardianCapabilityInvocationValidator",
    )

    _PROVIDER_ERROR_REASONS = {
        "RESPONSIBILITY_BOUNDARY_EXCEEDED": (
            InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED
        ),
        "BOUNDARY_REFERENCE_MISMATCH": (
            InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED
        ),
        "CONTROL_LEVEL_MISMATCH": InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT,
        "CONTROL_EVIDENCE_MISMATCH": (
            InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT
        ),
        "JOINT_CONTROL_MISMATCH": InvocationDecisionReason.JOINT_CONTROL_INCOMPLETE,
        "JOINT_CONTROL_INCOMPLETE": InvocationDecisionReason.JOINT_CONTROL_INCOMPLETE,
        "SNAPSHOT_AUTHORIZATION_SET_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_OBJECT_IDENTITY_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_PROVIDER_IDENTITY_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_CAPABILITY_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_CONTROL_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_BOUNDARY_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
        "SNAPSHOT_UNCERTAINTY_MISMATCH": (
            InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        ),
    }

    _REASON_CHECK = {
        InvocationDecisionReason.PROVIDER_UNKNOWN: InvocationCheck.PROVIDER_IDENTITY,
        InvocationDecisionReason.AUTHORIZATION_MISSING: InvocationCheck.AUTHORIZATION_GRANT,
        InvocationDecisionReason.AUTHORIZATION_NOT_AUTHORIZED: InvocationCheck.LIFECYCLE,
        InvocationDecisionReason.AUTHORIZATION_SUSPENDED: InvocationCheck.LIFECYCLE,
        InvocationDecisionReason.AUTHORIZATION_REVOKED: InvocationCheck.LIFECYCLE,
        InvocationDecisionReason.AUTHORIZATION_EXPIRED: InvocationCheck.LIFECYCLE,
        InvocationDecisionReason.AUTHORITY_MISMATCH: InvocationCheck.AUTHORITY_AND_CAPABILITY,
        InvocationDecisionReason.CAPABILITY_DENIED: InvocationCheck.AUTHORITY_AND_CAPABILITY,
        InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED: (
            InvocationCheck.RESPONSIBILITY_BOUNDARY
        ),
        InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT: InvocationCheck.CONTROL_LEVELS,
        InvocationDecisionReason.JOINT_CONTROL_INCOMPLETE: InvocationCheck.JOINT_CONTROL,
        InvocationDecisionReason.OPERATION_MODE_NOT_ALLOWED: InvocationCheck.OPERATION_MODE,
        InvocationDecisionReason.CLASSIFICATION_TOO_HIGH: InvocationCheck.ANSWER_BOUNDARY,
        InvocationDecisionReason.CONTEXT_BINDING_MISSING: InvocationCheck.CONTEXT_BINDINGS,
        InvocationDecisionReason.SOURCE_BINDING_MISSING: InvocationCheck.SOURCE_BINDINGS,
        InvocationDecisionReason.RESOLUTION_SNAPSHOT_MISSING: (
            InvocationCheck.RESOLUTION_SNAPSHOT
        ),
        InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT: (
            InvocationCheck.RESOLUTION_SNAPSHOT
        ),
        InvocationDecisionReason.INPUT_CONTRACT_MISSING: InvocationCheck.INPUT_CONTRACT,
        InvocationDecisionReason.PROVENANCE_INCONSISTENT: InvocationCheck.PROVENANCE,
        InvocationDecisionReason.GOVERNANCE_GAP: InvocationCheck.AUTHORITY_MODEL,
    }

    def validate(
        self,
        boundary: GuardianCapabilityInvocationBoundary,
    ) -> GuardianCapabilityInvocationBoundary:
        if not isinstance(boundary, GuardianCapabilityInvocationBoundary):
            raise TypeError("boundary must be a GuardianCapabilityInvocationBoundary")
        if boundary.capabilities != NON_EXECUTING_INVOCATION_CAPABILITIES:
            _invalid("EXECUTING_CAPABILITY_FORBIDDEN", "boundary is evidence only")
        issue = self._provider_package_issue(boundary.provider_authorization_package)
        if issue is None:
            issue = self._request_issue(boundary)
        self._validate_decision(boundary, issue)
        self._validate_evidence(boundary, issue)
        self._validate_global_ids(boundary)
        self._validate_provenance(boundary)
        return boundary

    def create_receipt(
        self,
        boundary: GuardianCapabilityInvocationBoundary,
        *,
        receipt_id: str,
        validated_at: datetime,
        review_status: AuthorityReviewStatus,
        review_reference: Optional[str],
        provenance: AuthorityProvenance,
    ) -> CapabilityInvocationReceipt:
        self.validate(boundary)
        _text(receipt_id, "receipt_id")
        if receipt_id in (
            boundary.boundary_id,
            boundary.request.invocation_id,
            boundary.decision.decision_id,
            boundary.evidence.evidence_id,
        ):
            _invalid("DUPLICATE_IDENTITY", "receipt identity must be unique")
        if provenance != boundary.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "receipt provenance differs")
        package = boundary.provider_authorization_package
        chain = (
            package.authority_model.authority_model_id,
            boundary.request.provider_reference,
            boundary.request.authorization_reference,
            boundary.request.authority_reference,
        )
        snapshots = tuple(
            item
            for item in package.snapshots
            if item.provider.provider_id == boundary.request.provider_reference
        )
        if snapshots:
            chain += (snapshots[0].snapshot_id,)
        return CapabilityInvocationReceipt(
            receipt_id=receipt_id,
            invocation_reference=boundary.request.invocation_id,
            decision_reference=boundary.decision.decision_id,
            evidence_reference=boundary.evidence.evidence_id,
            decision_status=boundary.decision.status,
            authority_chain_references=chain,
            validation_status=InvocationReceiptValidationStatus.VALIDATED,
            passed_checks=boundary.evidence.passed_checks,
            failed_checks=boundary.evidence.failed_checks,
            validated_at=validated_at,
            review_status=review_status,
            review_reference=review_reference,
            provenance=provenance,
        )

    def create_resolution_snapshot(
        self,
        boundary: GuardianCapabilityInvocationBoundary,
        receipt: CapabilityInvocationReceipt,
        *,
        snapshot_id: str,
        review_status: AuthorityReviewStatus,
        review_reference: Optional[str],
        provenance: AuthorityProvenance,
    ) -> CapabilityInvocationResolutionSnapshot:
        self.validate(boundary)
        self._validate_receipt(boundary, receipt)
        _text(snapshot_id, "snapshot_id")
        if snapshot_id in (
            boundary.boundary_id,
            boundary.request.invocation_id,
            boundary.decision.decision_id,
            boundary.evidence.evidence_id,
            receipt.receipt_id,
        ):
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        if boundary.decision.status is not InvocationDecisionStatus.ACCEPTED:
            _invalid("SNAPSHOT_REQUIRES_ACCEPTED", "full snapshot requires accepted request")
        if provenance != boundary.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "snapshot provenance differs")
        request = boundary.request
        package = boundary.provider_authorization_package
        provider = self._provider(package, request.provider_reference)
        grant = self._grant(package, request.authorization_reference)
        authority = self._authority(package, request.authority_reference)
        provider_snapshot = self._provider_snapshot(package, provider.provider_id)
        lifecycle = self._lifecycle(package, grant.authorization_id)
        return CapabilityInvocationResolutionSnapshot(
            snapshot_id=snapshot_id,
            request=request,
            decision=boundary.decision,
            evidence=boundary.evidence,
            receipt=receipt,
            provider=provider,
            authority=authority,
            authorization=grant,
            lifecycle_evidence=lifecycle,
            provider_authorization_snapshot=provider_snapshot,
            capability=request.capability,
            operation_mode=request.operation_mode,
            answer_mode=request.maximum_answer_mode,
            control_levels=request.required_control_levels,
            context_bindings=request.context_bindings,
            source_chain_references=request.source_chain_references,
            review_status=review_status,
            review_reference=review_reference,
            uncertainty_status=request.uncertainty_status,
            provenance=provenance,
        )

    @classmethod
    def _provider_package_issue(cls, package):
        try:
            GuardianProviderAuthorizationValidator().validate(package)
        except ProviderAuthorizationValidationError as error:
            return cls._PROVIDER_ERROR_REASONS.get(
                error.code,
                InvocationDecisionReason.GOVERNANCE_GAP,
            )
        except ValueError:
            return InvocationDecisionReason.GOVERNANCE_GAP
        return None

    @classmethod
    def _request_issue(cls, boundary):
        request = boundary.request
        package = boundary.provider_authorization_package
        if request.answer_boundary_reference != boundary.answer_boundary.boundary_id:
            return InvocationDecisionReason.CLASSIFICATION_TOO_HIGH
        if (
            request.maximum_answer_mode
            is not AnswerOperatingMode.B1_GENERAL_ORIENTATION
            or boundary.answer_boundary.effective_mode
            is not AnswerOperatingMode.B1_GENERAL_ORIENTATION
            or boundary.answer_boundary.requested_mode
            is not AnswerOperatingMode.B1_GENERAL_ORIENTATION
        ):
            return InvocationDecisionReason.CLASSIFICATION_TOO_HIGH
        try:
            GuardianAnswerBoundaryValidator().validate(boundary.answer_boundary)
        except ValueError:
            return InvocationDecisionReason.GOVERNANCE_GAP
        if request.operation_mode not in ALLOWED_INVOCATION_OPERATION_MODES:
            return InvocationDecisionReason.OPERATION_MODE_NOT_ALLOWED
        if request.data_scope not in (
            InvocationDataScope.NON_PERSONAL,
            InvocationDataScope.DEPERSONALIZED,
        ):
            return InvocationDecisionReason.CONTEXT_BINDING_MISSING
        required_bindings = {
            InvocationContextBindingType.JURISDICTION,
            InvocationContextBindingType.PURPOSE,
            InvocationContextBindingType.DATA_SCOPE,
        }
        provided_bindings = {item.binding_type for item in request.context_bindings}
        if not required_bindings <= provided_bindings:
            return InvocationDecisionReason.CONTEXT_BINDING_MISSING
        if request.source_chains_required and not request.source_chain_references:
            return InvocationDecisionReason.SOURCE_BINDING_MISSING
        if not (
            request.input_contract_reference
            and request.input_schema_version
            and request.input_reference
        ):
            return InvocationDecisionReason.INPUT_CONTRACT_MISSING
        providers = {item.provider_id: item for item in package.providers}
        provider = providers.get(request.provider_reference)
        if provider is None:
            return InvocationDecisionReason.PROVIDER_UNKNOWN
        grants = {item.authorization_id: item for item in package.authorizations}
        grant = grants.get(request.authorization_reference)
        if grant is None:
            return InvocationDecisionReason.AUTHORIZATION_MISSING
        if grant.provider_reference != provider.provider_id:
            return InvocationDecisionReason.AUTHORIZATION_MISSING
        status_reason = {
            ProviderAuthorizationStatus.PROPOSED: (
                InvocationDecisionReason.AUTHORIZATION_NOT_AUTHORIZED
            ),
            ProviderAuthorizationStatus.REJECTED: (
                InvocationDecisionReason.AUTHORIZATION_NOT_AUTHORIZED
            ),
            ProviderAuthorizationStatus.SUSPENDED: (
                InvocationDecisionReason.AUTHORIZATION_SUSPENDED
            ),
            ProviderAuthorizationStatus.REVOKED: (
                InvocationDecisionReason.AUTHORIZATION_REVOKED
            ),
            ProviderAuthorizationStatus.EXPIRED: (
                InvocationDecisionReason.AUTHORIZATION_EXPIRED
            ),
        }.get(grant.status)
        if status_reason is not None:
            return status_reason
        authorities = {
            item.authority_id: item for item in package.authority_model.authorities
        }
        authority = authorities.get(request.authority_reference)
        if authority is None or grant.authority_reference != request.authority_reference:
            return InvocationDecisionReason.AUTHORITY_MISMATCH
        if (
            request.capability not in grant.allowed_capabilities
            or request.capability in grant.forbidden_capabilities
            or request.capability not in authority.capabilities
        ):
            return InvocationDecisionReason.CAPABILITY_DENIED
        boundaries = {
            item.boundary_id: item
            for item in package.authority_model.actor_boundaries
        }
        responsibility = boundaries.get(grant.responsibility_boundary_reference)
        if (
            responsibility is None
            or responsibility.actor_class is not provider.actor_class
            or authority.authority_id
            not in responsibility.allowed_authority_references
        ):
            return InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED
        if request.required_control_levels != grant.control_levels:
            return InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT
        if not set(grant.required_joint_actor_classes) <= set(
            request.provided_joint_actor_classes
        ):
            return InvocationDecisionReason.JOINT_CONTROL_INCOMPLETE
        snapshots = tuple(
            item
            for item in package.snapshots
            if item.provider.provider_id == provider.provider_id
        )
        if not snapshots:
            return InvocationDecisionReason.RESOLUTION_SNAPSHOT_MISSING
        if len(snapshots) != 1 or grant not in snapshots[0].authorized:
            return InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT
        if request.provenance != boundary.provenance:
            return InvocationDecisionReason.PROVENANCE_INCONSISTENT
        return None

    @classmethod
    def _validate_decision(cls, boundary, issue) -> None:
        decision = boundary.decision
        if decision.invocation_reference != boundary.request.invocation_id:
            _invalid("DECISION_REFERENCE_MISMATCH", "decision references another request")
        expected_status = InvocationDecisionStatus.ACCEPTED
        expected_reasons = ()
        if issue is not None:
            expected_status = (
                InvocationDecisionStatus.REJECTED
                if issue
                in (
                    InvocationDecisionReason.PROVIDER_UNKNOWN,
                    InvocationDecisionReason.AUTHORIZATION_MISSING,
                )
                else InvocationDecisionStatus.BLOCKED
            )
            expected_reasons = (issue,)
        if decision.status is not expected_status or decision.reasons != expected_reasons:
            _invalid(
                "FAIL_CLOSED_DECISION_MISMATCH",
                "decision does not match the supplied validation evidence",
            )

    @classmethod
    def _validate_evidence(cls, boundary, issue) -> None:
        request = boundary.request
        decision = boundary.decision
        evidence = boundary.evidence
        if (
            evidence.invocation_reference != request.invocation_id
            or evidence.request_reference != request.invocation_id
            or evidence.decision_reference != decision.decision_id
        ):
            _invalid("EVIDENCE_REFERENCE_MISMATCH", "evidence references differ")
        if evidence.checked_answer_mode is not request.maximum_answer_mode:
            _invalid("EVIDENCE_MODE_MISMATCH", "checked answer mode differs")
        if evidence.checked_operation_mode is not request.operation_mode:
            _invalid("EVIDENCE_MODE_MISMATCH", "checked operation mode differs")
        if evidence.checked_control_levels != request.required_control_levels:
            _invalid("EVIDENCE_CONTROL_MISMATCH", "checked controls differ")
        if not set(cls.REQUIRED_VALIDATORS) <= set(evidence.validator_references):
            _invalid("VALIDATOR_EVIDENCE_MISSING", "validator references incomplete")
        expected_failed = () if issue is None else (cls._REASON_CHECK[issue],)
        expected_passed = tuple(
            check for check in REQUIRED_INVOCATION_CHECKS if check not in expected_failed
        )
        if (
            evidence.passed_checks != expected_passed
            or evidence.failed_checks != expected_failed
            or evidence.result is not decision.status
        ):
            _invalid("EVIDENCE_RESULT_MISMATCH", "evidence result differs")
        expected_lifecycle = tuple(
            item.evidence_id
            for item in cls._lifecycle(
                boundary.provider_authorization_package,
                request.authorization_reference,
            )
        )
        if evidence.checked_lifecycle_evidence_references != expected_lifecycle:
            _invalid("LIFECYCLE_EVIDENCE_MISMATCH", "lifecycle references differ")
        snapshots = tuple(
            item
            for item in boundary.provider_authorization_package.snapshots
            if item.provider.provider_id == request.provider_reference
        )
        expected_snapshot_reference = snapshots[0].snapshot_id if len(snapshots) == 1 else None
        if issue is InvocationDecisionReason.RESOLUTION_SNAPSHOT_MISSING:
            expected_snapshot_reference = None
        if evidence.checked_resolution_snapshot_reference != expected_snapshot_reference:
            _invalid("EVIDENCE_SNAPSHOT_MISMATCH", "snapshot evidence differs")
        cls._optional_reference(
            evidence.checked_provider_reference,
            request.provider_reference,
            issue is InvocationDecisionReason.PROVIDER_UNKNOWN,
        )
        cls._optional_reference(
            evidence.checked_authorization_reference,
            request.authorization_reference,
            issue is InvocationDecisionReason.AUTHORIZATION_MISSING,
        )
        cls._optional_reference(
            evidence.checked_authority_reference,
            request.authority_reference,
            issue in (
                InvocationDecisionReason.PROVIDER_UNKNOWN,
                InvocationDecisionReason.AUTHORIZATION_MISSING,
            ),
        )

    @staticmethod
    def _optional_reference(actual, expected, may_be_missing):
        if actual is None:
            if not may_be_missing:
                _invalid("EVIDENCE_REFERENCE_MISSING", "checked reference is missing")
        elif actual != expected:
            _invalid("EVIDENCE_REFERENCE_MISMATCH", "checked reference differs")

    @staticmethod
    def _validate_global_ids(boundary) -> None:
        identifiers = (
            boundary.boundary_id,
            boundary.request.invocation_id,
            boundary.decision.decision_id,
            boundary.evidence.evidence_id,
        )
        if len(identifiers) != len(set(identifiers)):
            _invalid("DUPLICATE_IDENTITY", "invocation identities must be unique")

    @staticmethod
    def _validate_provenance(boundary) -> None:
        if (
            boundary.decision.provenance != boundary.provenance
            or boundary.evidence.provenance != boundary.provenance
        ):
            _invalid("PROVENANCE_INCONSISTENT", "invocation provenance differs")
        if (
            boundary.request.provenance != boundary.provenance
            and boundary.decision.reasons
            != (InvocationDecisionReason.PROVENANCE_INCONSISTENT,)
        ):
            _invalid("PROVENANCE_INCONSISTENT", "request provenance differs")

    @staticmethod
    def _validate_receipt(boundary, receipt) -> None:
        if not isinstance(receipt, CapabilityInvocationReceipt):
            raise TypeError("receipt must be a CapabilityInvocationReceipt")
        package = boundary.provider_authorization_package
        expected_chain = (
            package.authority_model.authority_model_id,
            boundary.request.provider_reference,
            boundary.request.authorization_reference,
            boundary.request.authority_reference,
        )
        snapshots = tuple(
            item
            for item in package.snapshots
            if item.provider.provider_id == boundary.request.provider_reference
        )
        if snapshots:
            expected_chain += (snapshots[0].snapshot_id,)
        if (
            receipt.invocation_reference != boundary.request.invocation_id
            or receipt.decision_reference != boundary.decision.decision_id
            or receipt.evidence_reference != boundary.evidence.evidence_id
            or receipt.decision_status is not boundary.decision.status
            or receipt.passed_checks != boundary.evidence.passed_checks
            or receipt.failed_checks != boundary.evidence.failed_checks
            or receipt.provenance != boundary.provenance
            or receipt.authority_chain_references != expected_chain
            or receipt.validation_status
            is not InvocationReceiptValidationStatus.VALIDATED
        ):
            _invalid("RECEIPT_MISMATCH", "receipt differs from validated boundary")

    @staticmethod
    def _provider(package, reference):
        return next(item for item in package.providers if item.provider_id == reference)

    @staticmethod
    def _grant(package, reference):
        return next(
            item for item in package.authorizations if item.authorization_id == reference
        )

    @staticmethod
    def _authority(package, reference):
        return next(
            item
            for item in package.authority_model.authorities
            if item.authority_id == reference
        )

    @staticmethod
    def _provider_snapshot(package, provider_reference):
        return next(
            item
            for item in package.snapshots
            if item.provider.provider_id == provider_reference
        )

    @staticmethod
    def _lifecycle(package, authorization_reference):
        result = []
        for values in (
            package.revocations,
            package.suspensions,
            package.expirations,
            package.restorations,
        ):
            result.extend(
                item
                for item in values
                if item.authorization_reference == authorization_reference
            )
        return tuple(result)


def _invalid(code: str, message: str) -> None:
    raise CapabilityInvocationValidationError(code, message)


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value: object, name: str, required: bool) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid values".format(name))
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(value: object, item_type: type, name: str) -> None:
    _typed_unique(value, item_type, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))


def _review_pair(status, reference) -> None:
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed evidence needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed evidence may reference a review")


def _provenance(value) -> None:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
