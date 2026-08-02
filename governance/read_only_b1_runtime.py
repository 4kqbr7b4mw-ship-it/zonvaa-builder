"""Strict read-only B1 provider runtime from ADR-0051.

The module is intentionally a narrow execution boundary.  It can call one
explicitly supplied adapter only after the complete ADR-0050 evidence chain
has validated.  It does not select providers, retry, persist, or activate a
Guardian answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, Tuple

from governance.authority import (
    AuthorityCapability,
    AuthorityProvenance,
    AuthorityReviewStatus,
)
from governance.capability_invocation import (
    CapabilityInvocationReceipt,
    CapabilityInvocationResolutionSnapshot,
    GuardianCapabilityInvocationBoundary,
    GuardianCapabilityInvocationValidator,
    InvocationContextBinding,
    InvocationDataScope,
    InvocationDecisionStatus,
    InvocationOperationMode,
    InvocationReceiptValidationStatus,
)
from governance.provider_authorization import (
    AuthorizationExpirationEvidence,
    AuthorizationRevocationEvidence,
    AuthorizationSuspensionEvidence,
    AuthorizationUncertaintyStatus,
    ProviderAuthorizationStatus,
)
from guardian_understanding.answer_boundary import AnswerOperatingMode
from guardian_understanding.source_chain import (
    GuardianSourceChainContract,
    GuardianSourceChainValidator,
)


class RuntimeExecutionStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    TIMED_OUT = "TIMED_OUT"
    INVALID_PROVIDER_RESPONSE = "INVALID_PROVIDER_RESPONSE"
    DEGRADED = "DEGRADED"


class ProviderTechnicalStatus(str, Enum):
    NOT_CALLED = "NOT_CALLED"
    SUCCEEDED = "SUCCEEDED"
    ERROR = "ERROR"
    TIMED_OUT = "TIMED_OUT"
    DEGRADED = "DEGRADED"


class RuntimeProvisionStatus(str, Enum):
    PROVIDED_NOT_ACTIVATED = "PROVIDED_NOT_ACTIVATED"
    NOT_PROVIDED = "NOT_PROVIDED"
    DEGRADED_NOT_ACTIVATED = "DEGRADED_NOT_ACTIVATED"


class ProviderOutputKind(str, Enum):
    B1_GENERAL_ORIENTATION = "B1_GENERAL_ORIENTATION"
    B2_PERSONAL_PREPARATION = "B2_PERSONAL_PREPARATION"
    B3_PROFESSIONAL_BOUNDARY = "B3_PROFESSIONAL_BOUNDARY"
    STATE_CHANGE_INSTRUCTION = "STATE_CHANGE_INSTRUCTION"
    TOOL_INSTRUCTION = "TOOL_INSTRUCTION"


class RuntimeBlockReason(str, Enum):
    INVOCATION_NOT_ACCEPTED = "INVOCATION_NOT_ACCEPTED"
    INVOCATION_PATH_INCONSISTENT = "INVOCATION_PATH_INCONSISTENT"
    RECEIPT_INCONSISTENT = "RECEIPT_INCONSISTENT"
    RESOLUTION_SNAPSHOT_INCONSISTENT = "RESOLUTION_SNAPSHOT_INCONSISTENT"
    PROVIDER_MISMATCH = "PROVIDER_MISMATCH"
    AUTHORIZATION_NOT_AUTHORIZED = "AUTHORIZATION_NOT_AUTHORIZED"
    AUTHORIZATION_LIFECYCLE_BLOCKED = "AUTHORIZATION_LIFECYCLE_BLOCKED"
    CAPABILITY_NOT_AUTHORIZED = "CAPABILITY_NOT_AUTHORIZED"
    RESPONSIBILITY_BOUNDARY_EXCEEDED = "RESPONSIBILITY_BOUNDARY_EXCEEDED"
    CONTROL_LEVEL_INSUFFICIENT = "CONTROL_LEVEL_INSUFFICIENT"
    ANSWER_MODE_NOT_ALLOWED = "ANSWER_MODE_NOT_ALLOWED"
    OPERATION_MODE_NOT_ALLOWED = "OPERATION_MODE_NOT_ALLOWED"
    PERSONAL_DATA_FORBIDDEN = "PERSONAL_DATA_FORBIDDEN"
    CONTEXT_BINDING_MISSING = "CONTEXT_BINDING_MISSING"
    SOURCE_BINDING_MISSING = "SOURCE_BINDING_MISSING"
    INPUT_CONTRACT_MISSING = "INPUT_CONTRACT_MISSING"
    PROVENANCE_INCONSISTENT = "PROVENANCE_INCONSISTENT"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_TECHNICAL_ERROR = "PROVIDER_TECHNICAL_ERROR"
    PROVIDER_RESPONSE_INVALID = "PROVIDER_RESPONSE_INVALID"
    OUTPUT_BOUNDARY_FAILED = "OUTPUT_BOUNDARY_FAILED"


class RuntimeCheck(str, Enum):
    INVOCATION_BOUNDARY = "INVOCATION_BOUNDARY"
    ACCEPTED_DECISION = "ACCEPTED_DECISION"
    INVOCATION_RECEIPT = "INVOCATION_RECEIPT"
    INVOCATION_RESOLUTION = "INVOCATION_RESOLUTION"
    PROVIDER_IDENTITY = "PROVIDER_IDENTITY"
    AUTHORIZATION = "AUTHORIZATION"
    LIFECYCLE = "LIFECYCLE"
    CAPABILITY = "CAPABILITY"
    RESPONSIBILITY_BOUNDARY = "RESPONSIBILITY_BOUNDARY"
    CONTROL_LEVELS = "CONTROL_LEVELS"
    ANSWER_MODE = "ANSWER_MODE"
    OPERATION_MODE = "OPERATION_MODE"
    DATA_SCOPE = "DATA_SCOPE"
    CONTEXT_BINDINGS = "CONTEXT_BINDINGS"
    SOURCE_CHAINS = "SOURCE_CHAINS"
    INPUT_CONTRACT = "INPUT_CONTRACT"
    PROVENANCE = "PROVENANCE"
    OUTPUT_BOUNDARY = "OUTPUT_BOUNDARY"


RUNTIME_PRECHECKS = tuple(item for item in RuntimeCheck if item is not RuntimeCheck.OUTPUT_BOUNDARY)


@dataclass(frozen=True)
class RuntimeDataField:
    name: str
    value: str

    def __post_init__(self) -> None:
        _text(self.name, "name")
        _text(self.value, "value")


@dataclass(frozen=True)
class RuntimeOutputContract:
    output_contract_id: str
    schema_version: str
    allowed_fields: Tuple[str, ...]
    required_fields: Tuple[str, ...]
    maximum_fields: int
    maximum_value_length: int

    def __post_init__(self) -> None:
        _text(self.output_contract_id, "output_contract_id")
        _text(self.schema_version, "schema_version")
        _strings(self.allowed_fields, "allowed_fields", required=True)
        _strings(self.required_fields, "required_fields", required=True)
        if not set(self.required_fields) <= set(self.allowed_fields):
            raise ValueError("required_fields must be allowed")
        _positive_int(self.maximum_fields, "maximum_fields")
        _positive_int(self.maximum_value_length, "maximum_value_length")
        if len(self.allowed_fields) > self.maximum_fields:
            raise ValueError("allowed_fields exceed maximum_fields")


@dataclass(frozen=True)
class B1RuntimeExecutionRequest:
    execution_id: str
    invocation_request_reference: str
    accepted_decision_reference: str
    invocation_evidence_reference: str
    invocation_receipt_reference: str
    invocation_resolution_snapshot_reference: str
    provider_reference: str
    authorization_reference: str
    capability: AuthorityCapability
    operation_mode: InvocationOperationMode
    answer_mode: AnswerOperatingMode
    input_contract_reference: str
    input_schema_version: str
    input_payload: Tuple[RuntimeDataField, ...]
    context_bindings: Tuple[InvocationContextBinding, ...]
    source_chain_references: Tuple[str, ...]
    started_at: datetime
    timeout_seconds: int
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    uncertainty_status: AuthorizationUncertaintyStatus
    provenance: AuthorityProvenance
    output_contract: RuntimeOutputContract
    provided_degradation_notice: Optional[str] = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.execution_id, "execution_id"),
            (self.invocation_request_reference, "invocation_request_reference"),
            (self.accepted_decision_reference, "accepted_decision_reference"),
            (self.invocation_evidence_reference, "invocation_evidence_reference"),
            (self.invocation_receipt_reference, "invocation_receipt_reference"),
            (
                self.invocation_resolution_snapshot_reference,
                "invocation_resolution_snapshot_reference",
            ),
            (self.provider_reference, "provider_reference"),
            (self.authorization_reference, "authorization_reference"),
            (self.input_contract_reference, "input_contract_reference"),
            (self.input_schema_version, "input_schema_version"),
        ):
            _text(value, name)
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.operation_mode, InvocationOperationMode, "operation_mode")
        _enum(self.answer_mode, AnswerOperatingMode, "answer_mode")
        _typed_unique_nonempty(self.input_payload, RuntimeDataField, "input_payload")
        _unique_names(self.input_payload, "input payload")
        _typed_unique_nonempty(
            self.context_bindings, InvocationContextBinding, "context_bindings"
        )
        _strings(self.source_chain_references, "source_chain_references", required=True)
        _aware(self.started_at, "started_at")
        _positive_int(self.timeout_seconds, "timeout_seconds")
        _review_pair(self.review_status, self.review_reference)
        _enum(
            self.uncertainty_status,
            AuthorizationUncertaintyStatus,
            "uncertainty_status",
        )
        _provenance(self.provenance)
        if not isinstance(self.output_contract, RuntimeOutputContract):
            raise TypeError("output_contract must be a RuntimeOutputContract")
        if self.provided_degradation_notice is not None:
            _text(self.provided_degradation_notice, "provided_degradation_notice")


@dataclass(frozen=True)
class B1RuntimeExecutionEnvelope:
    request: B1RuntimeExecutionRequest
    invocation_boundary: GuardianCapabilityInvocationBoundary
    invocation_receipt: CapabilityInvocationReceipt
    invocation_resolution_snapshot: CapabilityInvocationResolutionSnapshot
    source_chains: Tuple[GuardianSourceChainContract, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.request, B1RuntimeExecutionRequest):
            raise TypeError("request must be a B1RuntimeExecutionRequest")
        if not isinstance(
            self.invocation_boundary, GuardianCapabilityInvocationBoundary
        ):
            raise TypeError("invocation_boundary has an invalid type")
        if not isinstance(self.invocation_receipt, CapabilityInvocationReceipt):
            raise TypeError("invocation_receipt has an invalid type")
        if not isinstance(
            self.invocation_resolution_snapshot,
            CapabilityInvocationResolutionSnapshot,
        ):
            raise TypeError("invocation_resolution_snapshot has an invalid type")
        _typed_tuple(self.source_chains, GuardianSourceChainContract, "source_chains")


@dataclass(frozen=True)
class ProviderAdapterRequest:
    execution_reference: str
    provider_reference: str
    capability: AuthorityCapability
    operation_mode: InvocationOperationMode
    answer_mode: AnswerOperatingMode
    input_contract_reference: str
    input_schema_version: str
    input_payload: Tuple[RuntimeDataField, ...]
    context_bindings: Tuple[InvocationContextBinding, ...]
    source_chain_references: Tuple[str, ...]
    timeout_seconds: int

    def __post_init__(self) -> None:
        for value, name in (
            (self.execution_reference, "execution_reference"),
            (self.provider_reference, "provider_reference"),
            (self.input_contract_reference, "input_contract_reference"),
            (self.input_schema_version, "input_schema_version"),
        ):
            _text(value, name)
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.operation_mode, InvocationOperationMode, "operation_mode")
        _enum(self.answer_mode, AnswerOperatingMode, "answer_mode")
        _typed_unique_nonempty(self.input_payload, RuntimeDataField, "input_payload")
        _unique_names(self.input_payload, "input payload")
        _typed_unique_nonempty(
            self.context_bindings, InvocationContextBinding, "context_bindings"
        )
        _strings(self.source_chain_references, "source_chain_references", True)
        _positive_int(self.timeout_seconds, "timeout_seconds")


@dataclass(frozen=True)
class ProviderAdapterResult:
    provider_reference: str
    capability: AuthorityCapability
    output_kind: ProviderOutputKind
    technical_status: ProviderTechnicalStatus
    output_fields: Tuple[RuntimeDataField, ...]
    started_at: datetime
    finished_at: datetime
    error_code: Optional[str] = None
    technical_detail: Optional[str] = None

    def __post_init__(self) -> None:
        _text(self.provider_reference, "provider_reference")
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.output_kind, ProviderOutputKind, "output_kind")
        _enum(self.technical_status, ProviderTechnicalStatus, "technical_status")
        _typed_tuple(self.output_fields, RuntimeDataField, "output_fields")
        _unique_names(self.output_fields, "output fields")
        _aware(self.started_at, "started_at")
        _aware(self.finished_at, "finished_at")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        for value, name in (
            (self.error_code, "error_code"),
            (self.technical_detail, "technical_detail"),
        ):
            if value is not None:
                _text(value, name)


class B1ReadOnlyProviderAdapter(Protocol):
    """One named provider and one B1 read-only capability; no discovery."""

    provider_reference: str
    capability: AuthorityCapability

    def invoke(self, request: ProviderAdapterRequest) -> ProviderAdapterResult:
        ...


@dataclass(frozen=True)
class RuntimeRecordMetadata:
    result_id: str
    evidence_id: str
    receipt_id: str
    finished_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.result_id, "result_id")
        _text(self.evidence_id, "evidence_id")
        _text(self.receipt_id, "receipt_id")
        if len({self.result_id, self.evidence_id, self.receipt_id}) != 3:
            raise ValueError("runtime record ids must be unique")
        _aware(self.finished_at, "finished_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B1RuntimeResult:
    result_id: str
    execution_reference: str
    provider_reference: str
    capability: AuthorityCapability
    answer_mode: AnswerOperatingMode
    output_fields: Tuple[RuntimeDataField, ...]
    source_chain_references: Tuple[str, ...]
    started_at: datetime
    finished_at: datetime
    status: RuntimeExecutionStatus
    technical_status: ProviderTechnicalStatus
    provision_status: RuntimeProvisionStatus
    block_reason: Optional[RuntimeBlockReason]
    degradation_notice: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    uncertainty_status: AuthorizationUncertaintyStatus
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.result_id, "result_id"),
            (self.execution_reference, "execution_reference"),
            (self.provider_reference, "provider_reference"),
        ):
            _text(value, name)
        _enum(self.capability, AuthorityCapability, "capability")
        _enum(self.answer_mode, AnswerOperatingMode, "answer_mode")
        _typed_tuple(self.output_fields, RuntimeDataField, "output_fields")
        _strings(self.source_chain_references, "source_chain_references", True)
        _aware(self.started_at, "started_at")
        _aware(self.finished_at, "finished_at")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        _enum(self.status, RuntimeExecutionStatus, "status")
        _enum(self.technical_status, ProviderTechnicalStatus, "technical_status")
        _enum(self.provision_status, RuntimeProvisionStatus, "provision_status")
        if self.block_reason is not None:
            _enum(self.block_reason, RuntimeBlockReason, "block_reason")
        if self.degradation_notice is not None:
            _text(self.degradation_notice, "degradation_notice")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeExecutionEvidence:
    evidence_id: str
    execution_reference: str
    invocation_boundary_reference: str
    provider_reference: str
    authorization_reference: str
    passed_checks: Tuple[RuntimeCheck, ...]
    failed_checks: Tuple[RuntimeCheck, ...]
    provider_called: bool
    technical_status: ProviderTechnicalStatus
    block_reason: Optional[RuntimeBlockReason]
    adapter_reference: str
    started_at: datetime
    finished_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.evidence_id, "evidence_id"),
            (self.execution_reference, "execution_reference"),
            (self.invocation_boundary_reference, "invocation_boundary_reference"),
            (self.provider_reference, "provider_reference"),
            (self.authorization_reference, "authorization_reference"),
            (self.adapter_reference, "adapter_reference"),
        ):
            _text(value, name)
        _typed_unique(self.passed_checks, RuntimeCheck, "passed_checks")
        _typed_unique(self.failed_checks, RuntimeCheck, "failed_checks")
        if set(self.passed_checks) & set(self.failed_checks):
            raise ValueError("runtime check cannot pass and fail")
        if not isinstance(self.provider_called, bool):
            raise TypeError("provider_called must be a bool")
        _enum(self.technical_status, ProviderTechnicalStatus, "technical_status")
        if self.block_reason is not None:
            _enum(self.block_reason, RuntimeBlockReason, "block_reason")
        _aware(self.started_at, "started_at")
        _aware(self.finished_at, "finished_at")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeExecutionReceipt:
    receipt_id: str
    execution_reference: str
    result_reference: str
    provider_called: bool
    completion_status: RuntimeExecutionStatus
    checked_boundary_reference: str
    source_chain_references: Tuple[str, ...]
    started_at: datetime
    finished_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.receipt_id, "receipt_id"),
            (self.execution_reference, "execution_reference"),
            (self.result_reference, "result_reference"),
            (self.checked_boundary_reference, "checked_boundary_reference"),
        ):
            _text(value, name)
        if not isinstance(self.provider_called, bool):
            raise TypeError("provider_called must be a bool")
        _enum(self.completion_status, RuntimeExecutionStatus, "completion_status")
        _strings(self.source_chain_references, "source_chain_references", True)
        _aware(self.started_at, "started_at")
        _aware(self.finished_at, "finished_at")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B1RuntimeExecutionOutcome:
    request: B1RuntimeExecutionRequest
    result: B1RuntimeResult
    evidence: RuntimeExecutionEvidence
    receipt: RuntimeExecutionReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.request, B1RuntimeExecutionRequest):
            raise TypeError("request has an invalid type")
        if not isinstance(self.result, B1RuntimeResult):
            raise TypeError("result has an invalid type")
        if not isinstance(self.evidence, RuntimeExecutionEvidence):
            raise TypeError("evidence has an invalid type")
        if not isinstance(self.receipt, RuntimeExecutionReceipt):
            raise TypeError("receipt has an invalid type")


class B1RuntimeValidationError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        reason: RuntimeBlockReason,
        check: RuntimeCheck,
    ) -> None:
        self.code = code
        self.reason = reason
        self.check = check
        super().__init__(message)


class B1RuntimeExecutionRequestValidator:
    """Validate the complete accepted path without calling a provider."""

    def validate(self, envelope: B1RuntimeExecutionEnvelope) -> B1RuntimeExecutionEnvelope:
        if not isinstance(envelope, B1RuntimeExecutionEnvelope):
            raise TypeError("envelope must be a B1RuntimeExecutionEnvelope")
        request = envelope.request
        boundary = envelope.invocation_boundary
        try:
            GuardianCapabilityInvocationValidator().validate(boundary)
        except (TypeError, ValueError) as error:
            _blocked(
                "INVOCATION_PATH_INCONSISTENT",
                str(error),
                RuntimeBlockReason.INVOCATION_PATH_INCONSISTENT,
                RuntimeCheck.INVOCATION_BOUNDARY,
            )
        if boundary.decision.status is not InvocationDecisionStatus.ACCEPTED:
            _blocked(
                "INVOCATION_NOT_ACCEPTED",
                "runtime requires an ACCEPTED invocation decision",
                RuntimeBlockReason.INVOCATION_NOT_ACCEPTED,
                RuntimeCheck.ACCEPTED_DECISION,
            )
        self._receipt_and_snapshot(envelope)
        snapshot = envelope.invocation_resolution_snapshot
        if request.provider_reference != snapshot.provider.provider_id:
            _blocked("PROVIDER_MISMATCH", "provider differs", RuntimeBlockReason.PROVIDER_MISMATCH, RuntimeCheck.PROVIDER_IDENTITY)
        if request.authorization_reference != snapshot.authorization.authorization_id:
            _blocked("AUTHORIZATION_MISMATCH", "authorization differs", RuntimeBlockReason.AUTHORIZATION_NOT_AUTHORIZED, RuntimeCheck.AUTHORIZATION)
        if snapshot.authorization.status is not ProviderAuthorizationStatus.AUTHORIZED:
            _blocked("AUTHORIZATION_NOT_AUTHORIZED", "authorization is not AUTHORIZED", RuntimeBlockReason.AUTHORIZATION_NOT_AUTHORIZED, RuntimeCheck.AUTHORIZATION)
        blocking_lifecycle = tuple(
            item
            for item in snapshot.lifecycle_evidence
            if isinstance(
                item,
                (
                    AuthorizationSuspensionEvidence,
                    AuthorizationRevocationEvidence,
                    AuthorizationExpirationEvidence,
                ),
            )
        )
        if blocking_lifecycle:
            _blocked("AUTHORIZATION_LIFECYCLE_BLOCKED", "lifecycle evidence prevents execution", RuntimeBlockReason.AUTHORIZATION_LIFECYCLE_BLOCKED, RuntimeCheck.LIFECYCLE)
        if (
            request.capability is not snapshot.capability
            or request.capability not in snapshot.authorization.allowed_capabilities
            or request.capability in snapshot.authorization.forbidden_capabilities
        ):
            _blocked("CAPABILITY_NOT_AUTHORIZED", "capability differs or is denied", RuntimeBlockReason.CAPABILITY_NOT_AUTHORIZED, RuntimeCheck.CAPABILITY)
        if snapshot.authorization.responsibility_boundary_reference not in tuple(
            item.boundary_id for item in snapshot.provider_authorization_snapshot.responsibility_boundaries
        ):
            _blocked("RESPONSIBILITY_BOUNDARY_EXCEEDED", "responsibility boundary differs", RuntimeBlockReason.RESPONSIBILITY_BOUNDARY_EXCEEDED, RuntimeCheck.RESPONSIBILITY_BOUNDARY)
        if request.context_bindings != snapshot.context_bindings:
            _blocked("CONTEXT_BINDING_MISSING", "context bindings differ", RuntimeBlockReason.CONTEXT_BINDING_MISSING, RuntimeCheck.CONTEXT_BINDINGS)
        if request.answer_mode is not AnswerOperatingMode.B1_GENERAL_ORIENTATION:
            _blocked("ANSWER_MODE_NOT_ALLOWED", "only B1 is executable", RuntimeBlockReason.ANSWER_MODE_NOT_ALLOWED, RuntimeCheck.ANSWER_MODE)
        if request.operation_mode is not InvocationOperationMode.READ_ONLY:
            _blocked("OPERATION_MODE_NOT_ALLOWED", "only READ_ONLY is executable", RuntimeBlockReason.OPERATION_MODE_NOT_ALLOWED, RuntimeCheck.OPERATION_MODE)
        if boundary.request.data_scope not in (InvocationDataScope.NON_PERSONAL, InvocationDataScope.DEPERSONALIZED):
            _blocked("PERSONAL_DATA_FORBIDDEN", "personal data is not executable", RuntimeBlockReason.PERSONAL_DATA_FORBIDDEN, RuntimeCheck.DATA_SCOPE)
        if request.input_contract_reference != boundary.request.input_contract_reference or request.input_schema_version != boundary.request.input_schema_version:
            _blocked("INPUT_CONTRACT_MISSING", "input contract differs", RuntimeBlockReason.INPUT_CONTRACT_MISSING, RuntimeCheck.INPUT_CONTRACT)
        self._source_chains(envelope)
        if request.provenance != boundary.provenance:
            _blocked("PROVENANCE_INCONSISTENT", "execution provenance differs", RuntimeBlockReason.PROVENANCE_INCONSISTENT, RuntimeCheck.PROVENANCE)
        return envelope

    @staticmethod
    def _receipt_and_snapshot(envelope) -> None:
        request = envelope.request
        boundary = envelope.invocation_boundary
        receipt = envelope.invocation_receipt
        snapshot = envelope.invocation_resolution_snapshot
        if (
            request.invocation_request_reference != boundary.request.invocation_id
            or request.accepted_decision_reference != boundary.decision.decision_id
            or request.invocation_evidence_reference != boundary.evidence.evidence_id
        ):
            _blocked("INVOCATION_REFERENCE_MISMATCH", "invocation references differ", RuntimeBlockReason.INVOCATION_PATH_INCONSISTENT, RuntimeCheck.INVOCATION_BOUNDARY)
        if (
            request.invocation_receipt_reference != receipt.receipt_id
            or receipt.decision_status is not InvocationDecisionStatus.ACCEPTED
            or receipt.validation_status is not InvocationReceiptValidationStatus.VALIDATED
            or receipt.invocation_reference != boundary.request.invocation_id
            or receipt.decision_reference != boundary.decision.decision_id
            or receipt.evidence_reference != boundary.evidence.evidence_id
        ):
            _blocked("RECEIPT_INCONSISTENT", "invocation receipt differs", RuntimeBlockReason.RECEIPT_INCONSISTENT, RuntimeCheck.INVOCATION_RECEIPT)
        if (
            request.invocation_resolution_snapshot_reference != snapshot.snapshot_id
            or snapshot.request is not boundary.request
            or snapshot.decision is not boundary.decision
            or snapshot.evidence is not boundary.evidence
            or snapshot.receipt is not receipt
        ):
            _blocked("RESOLUTION_SNAPSHOT_INCONSISTENT", "invocation resolution differs", RuntimeBlockReason.RESOLUTION_SNAPSHOT_INCONSISTENT, RuntimeCheck.INVOCATION_RESOLUTION)

    @staticmethod
    def _source_chains(envelope) -> None:
        references = envelope.request.source_chain_references
        provided = tuple(item.source_chain_id for item in envelope.source_chains)
        if len(provided) != len(set(provided)) or provided != references:
            _blocked("SOURCE_BINDING_MISSING", "source-chain set differs", RuntimeBlockReason.SOURCE_BINDING_MISSING, RuntimeCheck.SOURCE_CHAINS)
        if references != envelope.invocation_boundary.request.source_chain_references:
            _blocked("SOURCE_BINDING_MISSING", "invocation source-chain set differs", RuntimeBlockReason.SOURCE_BINDING_MISSING, RuntimeCheck.SOURCE_CHAINS)
        try:
            for source_chain in envelope.source_chains:
                GuardianSourceChainValidator().validate(source_chain)
        except (TypeError, ValueError) as error:
            _blocked("SOURCE_BINDING_MISSING", str(error), RuntimeBlockReason.SOURCE_BINDING_MISSING, RuntimeCheck.SOURCE_CHAINS)


class B1RuntimeOutputValidator:
    """Validate typed output structure without interpreting its text."""

    def validate(self, execution: B1RuntimeExecutionRequest, result: ProviderAdapterResult) -> ProviderAdapterResult:
        if result.provider_reference != execution.provider_reference or result.capability is not execution.capability:
            _blocked("PROVIDER_RESPONSE_INVALID", "provider response identity differs", RuntimeBlockReason.PROVIDER_RESPONSE_INVALID, RuntimeCheck.OUTPUT_BOUNDARY)
        if result.output_kind is not ProviderOutputKind.B1_GENERAL_ORIENTATION:
            _blocked("OUTPUT_BOUNDARY_FAILED", "output kind is not B1", RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED, RuntimeCheck.OUTPUT_BOUNDARY)
        contract = execution.output_contract
        names = tuple(item.name for item in result.output_fields)
        if len(names) > contract.maximum_fields or not set(names) <= set(contract.allowed_fields) or not set(contract.required_fields) <= set(names):
            _blocked("OUTPUT_BOUNDARY_FAILED", "output fields violate contract", RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED, RuntimeCheck.OUTPUT_BOUNDARY)
        if any(len(item.value) > contract.maximum_value_length for item in result.output_fields):
            _blocked("OUTPUT_BOUNDARY_FAILED", "output value exceeds contract", RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED, RuntimeCheck.OUTPUT_BOUNDARY)
        return result


class B1ReadOnlyRuntimeExecutor:
    """Call exactly one supplied adapter after complete fail-closed checks."""

    def execute(
        self,
        envelope: B1RuntimeExecutionEnvelope,
        adapter: B1ReadOnlyProviderAdapter,
        metadata: RuntimeRecordMetadata,
    ) -> B1RuntimeExecutionOutcome:
        request = envelope.request
        try:
            B1RuntimeExecutionRequestValidator().validate(envelope)
            if metadata.provenance != request.provenance:
                _blocked("PROVENANCE_INCONSISTENT", "runtime record provenance differs", RuntimeBlockReason.PROVENANCE_INCONSISTENT, RuntimeCheck.PROVENANCE)
            if adapter.provider_reference != request.provider_reference or adapter.capability is not request.capability:
                _blocked("PROVIDER_MISMATCH", "adapter is not the named provider/capability", RuntimeBlockReason.PROVIDER_MISMATCH, RuntimeCheck.PROVIDER_IDENTITY)
        except B1RuntimeValidationError as error:
            return self._outcome(envelope, metadata, adapter, False, self._status_for_precheck(envelope), ProviderTechnicalStatus.NOT_CALLED, error.reason, (), (error.check,))

        adapter_request = ProviderAdapterRequest(
            execution_reference=request.execution_id,
            provider_reference=request.provider_reference,
            capability=request.capability,
            operation_mode=request.operation_mode,
            answer_mode=request.answer_mode,
            input_contract_reference=request.input_contract_reference,
            input_schema_version=request.input_schema_version,
            input_payload=request.input_payload,
            context_bindings=request.context_bindings,
            source_chain_references=request.source_chain_references,
            timeout_seconds=request.timeout_seconds,
        )
        try:
            provider_result = adapter.invoke(adapter_request)
        except Exception:
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.PROVIDER_ERROR, ProviderTechnicalStatus.ERROR, RuntimeBlockReason.PROVIDER_TECHNICAL_ERROR, (), (RuntimeCheck.OUTPUT_BOUNDARY,))

        if not isinstance(provider_result, ProviderAdapterResult):
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE, ProviderTechnicalStatus.ERROR, RuntimeBlockReason.PROVIDER_RESPONSE_INVALID, (), (RuntimeCheck.OUTPUT_BOUNDARY,))
        if provider_result.technical_status is ProviderTechnicalStatus.TIMED_OUT:
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.TIMED_OUT, ProviderTechnicalStatus.TIMED_OUT, RuntimeBlockReason.PROVIDER_TIMEOUT, (), (RuntimeCheck.OUTPUT_BOUNDARY,))
        if provider_result.technical_status is ProviderTechnicalStatus.ERROR:
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.PROVIDER_ERROR, ProviderTechnicalStatus.ERROR, RuntimeBlockReason.PROVIDER_TECHNICAL_ERROR, (), (RuntimeCheck.OUTPUT_BOUNDARY,))
        elapsed = (provider_result.finished_at - provider_result.started_at).total_seconds()
        if elapsed > request.timeout_seconds:
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.TIMED_OUT, ProviderTechnicalStatus.TIMED_OUT, RuntimeBlockReason.PROVIDER_TIMEOUT, (), (RuntimeCheck.OUTPUT_BOUNDARY,))
        try:
            B1RuntimeOutputValidator().validate(request, provider_result)
        except B1RuntimeValidationError as error:
            return self._outcome(envelope, metadata, adapter, True, RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE, provider_result.technical_status, error.reason, (), (error.check,))
        status = RuntimeExecutionStatus.SUCCEEDED
        if provider_result.technical_status is ProviderTechnicalStatus.DEGRADED:
            status = RuntimeExecutionStatus.DEGRADED
        return self._outcome(envelope, metadata, adapter, True, status, provider_result.technical_status, None, provider_result.output_fields, ())

    @staticmethod
    def _status_for_precheck(envelope):
        if envelope.invocation_boundary.decision.status is InvocationDecisionStatus.REJECTED:
            return RuntimeExecutionStatus.REJECTED
        return RuntimeExecutionStatus.BLOCKED

    @staticmethod
    def _outcome(envelope, metadata, adapter, provider_called, status, technical_status, reason, output_fields, failed_checks):
        request = envelope.request
        if provider_called:
            passed_checks = RUNTIME_PRECHECKS
        elif failed_checks:
            failed_index = RUNTIME_PRECHECKS.index(failed_checks[0])
            passed_checks = RUNTIME_PRECHECKS[:failed_index]
        else:
            passed_checks = RUNTIME_PRECHECKS
        if provider_called and not failed_checks:
            passed_checks += (RuntimeCheck.OUTPUT_BOUNDARY,)
        provision = RuntimeProvisionStatus.NOT_PROVIDED
        if status is RuntimeExecutionStatus.SUCCEEDED:
            provision = RuntimeProvisionStatus.PROVIDED_NOT_ACTIVATED
        elif status is RuntimeExecutionStatus.DEGRADED:
            provision = RuntimeProvisionStatus.DEGRADED_NOT_ACTIVATED
        result = B1RuntimeResult(
            result_id=metadata.result_id,
            execution_reference=request.execution_id,
            provider_reference=request.provider_reference,
            capability=request.capability,
            answer_mode=request.answer_mode,
            output_fields=output_fields,
            source_chain_references=request.source_chain_references,
            started_at=request.started_at,
            finished_at=metadata.finished_at,
            status=status,
            technical_status=technical_status,
            provision_status=provision,
            block_reason=reason,
            degradation_notice=(request.provided_degradation_notice if status is not RuntimeExecutionStatus.SUCCEEDED else None),
            review_status=metadata.review_status,
            review_reference=metadata.review_reference,
            uncertainty_status=request.uncertainty_status,
            provenance=metadata.provenance,
        )
        evidence = RuntimeExecutionEvidence(
            evidence_id=metadata.evidence_id,
            execution_reference=request.execution_id,
            invocation_boundary_reference=envelope.invocation_boundary.boundary_id,
            provider_reference=request.provider_reference,
            authorization_reference=request.authorization_reference,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            provider_called=provider_called,
            technical_status=technical_status,
            block_reason=reason,
            adapter_reference=adapter.__class__.__name__,
            started_at=request.started_at,
            finished_at=metadata.finished_at,
            review_status=metadata.review_status,
            review_reference=metadata.review_reference,
            provenance=metadata.provenance,
        )
        receipt = RuntimeExecutionReceipt(
            receipt_id=metadata.receipt_id,
            execution_reference=request.execution_id,
            result_reference=result.result_id,
            provider_called=provider_called,
            completion_status=status,
            checked_boundary_reference=envelope.invocation_boundary.boundary_id,
            source_chain_references=request.source_chain_references,
            started_at=request.started_at,
            finished_at=metadata.finished_at,
            review_status=metadata.review_status,
            review_reference=metadata.review_reference,
            provenance=metadata.provenance,
        )
        return B1RuntimeExecutionOutcome(request=request, result=result, evidence=evidence, receipt=receipt)


def _blocked(code, message, reason, check):
    raise B1RuntimeValidationError(code, message, reason=reason, check=check)


def _text(value, name):
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _aware(value, name):
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _positive_int(value, name):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("{} must be a positive integer".format(name))


def _enum(value, enum_type, name):
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value, name, required):
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_tuple(value, item_type, name):
    if not isinstance(value, tuple) or not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid values".format(name))


def _typed_unique(value, item_type, name):
    _typed_tuple(value, item_type, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(value, item_type, name):
    _typed_unique(value, item_type, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))


def _unique_names(values, name):
    names = tuple(item.name for item in values)
    if len(names) != len(set(names)):
        raise ValueError("{} names must be unique".format(name))


def _review_pair(status, reference):
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed evidence needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed evidence may reference a review")


def _provenance(value):
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
