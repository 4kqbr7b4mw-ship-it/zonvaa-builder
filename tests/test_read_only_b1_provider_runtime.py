from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.authority import (
    AuthorityCapability,
    AuthorityControlLevel,
    AuthorityReviewStatus,
)
from governance.capability_invocation import (
    InvocationDataScope,
    InvocationDecisionReason,
    InvocationOperationMode,
)
from governance.provider_authorization import ProviderAuthorizationStatus
from governance.read_only_b1_runtime import (
    B1ReadOnlyRuntimeExecutor,
    B1RuntimeExecutionEnvelope,
    B1RuntimeExecutionRequest,
    B1RuntimeExecutionRequestValidator,
    B1RuntimeOutputValidator,
    B1RuntimeValidationError,
    ProviderAdapterResult,
    ProviderOutputKind,
    ProviderTechnicalStatus,
    RuntimeBlockReason,
    RuntimeDataField,
    RuntimeExecutionStatus,
    RuntimeOutputContract,
    RuntimeProvisionStatus,
    RuntimeRecordMetadata,
)
from guardian_understanding.answer_boundary import AnswerOperatingMode
from guardian_understanding.source_chain import (
    GuardianAnswerContextReference,
    GuardianSourceChainContract,
    SourceKind,
    SourceProvenanceCategory,
    SourceRecheckKind,
    SourceRecheckRequirement,
    SourceUncertaintyStatus,
)
from tests.test_guardian_capability_invocation import (
    NOW,
    answer_boundary,
    invocation_boundary,
    provenance,
    provider_package,
    request,
)


def source_chain(source_chain_id="source-chain-b1"):
    return GuardianSourceChainContract(
        source_chain_id=source_chain_id,
        source_name="Provided official source",
        publisher="Provided publisher",
        source_kind=SourceKind.PRIMARY,
        source_authority="Provided authority",
        source_reference="source:official",
        retrieved_at=NOW,
        publication_or_version="1.0",
        supported_statement="Already supplied general statement.",
        jurisdiction_or_scope="DE",
        declared_contradictions=(),
        uncertainty_status=SourceUncertaintyStatus.CONFIRMED,
        recheck_requirement=SourceRecheckRequirement(
            kind=SourceRecheckKind.EVENT_BASED,
            event_reference="event:source-change",
        ),
        answer_context_reference=GuardianAnswerContextReference(
            guardian_answer_id="answer:b1",
            conversation_context_id="conversation:b1",
        ),
        provenance_category=SourceProvenanceCategory.PROVIDED_SOURCE_RECORD,
        provenance_reference="provenance:source-b1",
    )


def accepted_invocation():
    boundary = invocation_boundary()
    validator = __import__(
        "governance.capability_invocation", fromlist=["GuardianCapabilityInvocationValidator"]
    ).GuardianCapabilityInvocationValidator()
    receipt = validator.create_receipt(
        boundary,
        receipt_id="invocation-receipt-b1",
        validated_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:invocation-receipt",
        provenance=provenance(),
    )
    snapshot = validator.create_resolution_snapshot(
        boundary,
        receipt,
        snapshot_id="invocation-resolution-b1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:invocation-resolution",
        provenance=provenance(),
    )
    return boundary, receipt, snapshot


def runtime_request(boundary, receipt, snapshot, **changes):
    values = dict(
        execution_id="execution-b1",
        invocation_request_reference=boundary.request.invocation_id,
        accepted_decision_reference=boundary.decision.decision_id,
        invocation_evidence_reference=boundary.evidence.evidence_id,
        invocation_receipt_reference=receipt.receipt_id,
        invocation_resolution_snapshot_reference=snapshot.snapshot_id,
        provider_reference=boundary.request.provider_reference,
        authorization_reference=boundary.request.authorization_reference,
        capability=boundary.request.capability,
        operation_mode=InvocationOperationMode.READ_ONLY,
        answer_mode=AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        input_contract_reference=boundary.request.input_contract_reference,
        input_schema_version=boundary.request.input_schema_version,
        input_payload=(RuntimeDataField("query", "What is a general term?"),),
        context_bindings=boundary.request.context_bindings,
        source_chain_references=boundary.request.source_chain_references,
        started_at=NOW + timedelta(hours=1),
        timeout_seconds=5,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-request",
        uncertainty_status=boundary.request.uncertainty_status,
        provenance=boundary.provenance,
        output_contract=RuntimeOutputContract(
            output_contract_id="output-contract:b1",
            schema_version="1.0",
            allowed_fields=("orientation", "source_notice"),
            required_fields=("orientation",),
            maximum_fields=2,
            maximum_value_length=500,
        ),
        provided_degradation_notice="The supplied provider result is unavailable.",
    )
    values.update(changes)
    return B1RuntimeExecutionRequest(**values)


def envelope(**request_changes):
    boundary, receipt, snapshot = accepted_invocation()
    execution = runtime_request(boundary, receipt, snapshot, **request_changes)
    return B1RuntimeExecutionEnvelope(
        request=execution,
        invocation_boundary=boundary,
        invocation_receipt=receipt,
        invocation_resolution_snapshot=snapshot,
        source_chains=(source_chain(),),
    )


def metadata():
    return RuntimeRecordMetadata(
        result_id="runtime-result-b1",
        evidence_id="runtime-evidence-b1",
        receipt_id="runtime-receipt-b1",
        finished_at=NOW + timedelta(hours=1, seconds=1),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-result",
        provenance=provenance(),
    )


class FakeAdapter:
    provider_reference = "provider-b1"
    capability = AuthorityCapability.PRESENT_GUARDIAN_RESPONSE

    def __init__(self, status=ProviderTechnicalStatus.SUCCEEDED, kind=ProviderOutputKind.B1_GENERAL_ORIENTATION, fields=None, raises=False):
        self.status = status
        self.kind = kind
        self.fields = fields or (RuntimeDataField("orientation", "Provided B1 output."),)
        self.raises = raises
        self.calls = []

    def invoke(self, request_value):
        self.calls.append(request_value)
        if self.raises:
            raise RuntimeError("controlled provider failure")
        return ProviderAdapterResult(
            provider_reference=self.provider_reference,
            capability=self.capability,
            output_kind=self.kind,
            technical_status=self.status,
            output_fields=self.fields,
            started_at=NOW + timedelta(hours=1),
            finished_at=NOW + timedelta(hours=1, milliseconds=100),
            error_code=("provider-error" if self.status is ProviderTechnicalStatus.ERROR else None),
        )


def run(value=None, adapter=None):
    return B1ReadOnlyRuntimeExecutor().execute(
        value or envelope(), adapter or FakeAdapter(), metadata()
    )


def test_valid_complete_b1_read_only_execution_calls_named_provider_once():
    adapter = FakeAdapter()
    value = envelope()
    outcome = run(value, adapter)
    assert len(adapter.calls) == 1
    assert adapter.calls[0].input_payload is value.request.input_payload
    assert adapter.calls[0].context_bindings is value.request.context_bindings
    assert outcome.request is value.request
    assert outcome.result.status is RuntimeExecutionStatus.SUCCEEDED
    assert outcome.result.provision_status is RuntimeProvisionStatus.PROVIDED_NOT_ACTIVATED
    assert outcome.result.output_fields == adapter.fields
    assert outcome.evidence.provider_called is True
    assert outcome.receipt.provider_called is True
    with pytest.raises(FrozenInstanceError):
        outcome.result.status = RuntimeExecutionStatus.BLOCKED


def test_execution_request_validation_returns_same_immutable_envelope():
    value = envelope()
    validator = B1RuntimeExecutionRequestValidator()
    assert validator.validate(value) is value
    assert validator.validate(value) is value


@pytest.mark.parametrize(
    "mode,reason",
    (
        (AnswerOperatingMode.B2_PERSONAL_PREPARATION, InvocationDecisionReason.CLASSIFICATION_TOO_HIGH),
        (AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, InvocationDecisionReason.CLASSIFICATION_TOO_HIGH),
    ),
)
def test_b2_and_b3_are_blocked_before_provider_call(mode, reason):
    accepted = envelope()
    blocked_boundary = invocation_boundary(
        reason,
        request_value=request(maximum_answer_mode=mode),
        answer_boundary_value=answer_boundary(mode),
    )
    value = replace(accepted, invocation_boundary=blocked_boundary)
    adapter = FakeAdapter()
    outcome = run(value, adapter)
    assert adapter.calls == []
    assert outcome.result.status is RuntimeExecutionStatus.BLOCKED


@pytest.mark.parametrize(
    "mode",
    (InvocationOperationMode.READ_WRITE, InvocationOperationMode.PRIVILEGED),
)
def test_write_and_privileged_modes_are_blocked_before_call(mode):
    value = replace(envelope(), request=replace(envelope().request, operation_mode=mode))
    adapter = FakeAdapter()
    outcome = run(value, adapter)
    assert adapter.calls == []
    assert outcome.result.block_reason is RuntimeBlockReason.OPERATION_MODE_NOT_ALLOWED


@pytest.mark.parametrize(
    "mode",
    (InvocationOperationMode.SIMULATION, InvocationOperationMode.DEGRADED),
)
def test_declarative_invocation_modes_are_not_real_runtime_permissions(mode):
    value = replace(envelope(), request=replace(envelope().request, operation_mode=mode))
    adapter = FakeAdapter()
    outcome = run(value, adapter)
    assert adapter.calls == []
    assert outcome.result.block_reason is RuntimeBlockReason.OPERATION_MODE_NOT_ALLOWED


@pytest.mark.parametrize(
    "reason,status",
    (
        (InvocationDecisionReason.PROVIDER_UNKNOWN, RuntimeExecutionStatus.REJECTED),
        (InvocationDecisionReason.AUTHORIZATION_MISSING, RuntimeExecutionStatus.REJECTED),
        (InvocationDecisionReason.AUTHORIZATION_SUSPENDED, RuntimeExecutionStatus.BLOCKED),
        (InvocationDecisionReason.AUTHORIZATION_REVOKED, RuntimeExecutionStatus.BLOCKED),
        (InvocationDecisionReason.AUTHORIZATION_EXPIRED, RuntimeExecutionStatus.BLOCKED),
        (InvocationDecisionReason.CAPABILITY_DENIED, RuntimeExecutionStatus.BLOCKED),
        (InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED, RuntimeExecutionStatus.BLOCKED),
        (InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT, RuntimeExecutionStatus.BLOCKED),
    ),
)
def test_invalid_invocation_paths_never_call_provider(reason, status):
    base = envelope()
    request_value = request()
    package_value = provider_package()
    if reason is InvocationDecisionReason.PROVIDER_UNKNOWN:
        request_value = request(provider_reference="provider-unknown")
    elif reason is InvocationDecisionReason.AUTHORIZATION_MISSING:
        request_value = request(authorization_reference="authorization-unknown")
    elif reason is InvocationDecisionReason.AUTHORIZATION_SUSPENDED:
        package_value = provider_package(ProviderAuthorizationStatus.SUSPENDED)
    elif reason is InvocationDecisionReason.AUTHORIZATION_REVOKED:
        package_value = provider_package(ProviderAuthorizationStatus.REVOKED)
    elif reason is InvocationDecisionReason.AUTHORIZATION_EXPIRED:
        package_value = provider_package(ProviderAuthorizationStatus.EXPIRED)
    elif reason is InvocationDecisionReason.CAPABILITY_DENIED:
        request_value = request(capability=AuthorityCapability.VALIDATE_TYPED_CONTRACT)
    elif reason is InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED:
        package_value = provider_package(grant_changes={"responsibility_boundary_reference": "wrong-boundary"})
    elif reason is InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT:
        request_value = request(
            required_control_levels=(AuthorityControlLevel.STRUCTURAL_VALIDATION,)
        )
    blocked = invocation_boundary(reason, request_value=request_value, package_value=package_value)
    adapter = FakeAdapter()
    outcome = run(replace(base, invocation_boundary=blocked), adapter)
    assert adapter.calls == []
    assert outcome.result.status is status


def test_inconsistent_receipt_and_resolution_are_blocked_before_call():
    original = envelope()
    adapter = FakeAdapter()
    wrong_receipt = replace(original.invocation_receipt, invocation_reference="other")
    outcome = run(replace(original, invocation_receipt=wrong_receipt), adapter)
    assert outcome.result.block_reason is RuntimeBlockReason.RECEIPT_INCONSISTENT
    assert adapter.calls == []
    adapter = FakeAdapter()
    wrong_snapshot = replace(
        original.invocation_resolution_snapshot,
        request=replace(original.invocation_boundary.request),
    )
    outcome = run(
        replace(original, invocation_resolution_snapshot=wrong_snapshot), adapter
    )
    assert outcome.result.block_reason is RuntimeBlockReason.RESOLUTION_SNAPSHOT_INCONSISTENT
    assert adapter.calls == []


def test_missing_accepted_decision_is_fail_closed_before_provider_call():
    value = envelope()
    blocked_boundary = invocation_boundary(
        InvocationDecisionReason.AUTHORIZATION_NOT_AUTHORIZED,
        package_value=provider_package(ProviderAuthorizationStatus.PROPOSED),
    )
    adapter = FakeAdapter()
    outcome = run(replace(value, invocation_boundary=blocked_boundary), adapter)
    assert adapter.calls == []
    assert outcome.result.block_reason is RuntimeBlockReason.INVOCATION_NOT_ACCEPTED
    assert outcome.result.technical_status is ProviderTechnicalStatus.NOT_CALLED


def test_unknown_adapter_and_missing_or_wrong_bindings_block_before_call():
    value = envelope()
    adapter = FakeAdapter()
    adapter.provider_reference = "other-provider"
    outcome = run(value, adapter)
    assert outcome.result.block_reason is RuntimeBlockReason.PROVIDER_MISMATCH
    assert adapter.calls == []
    for changed, reason in (
        (replace(value.request, source_chain_references=("missing",)), RuntimeBlockReason.SOURCE_BINDING_MISSING),
        (replace(value.request, input_contract_reference="other-contract"), RuntimeBlockReason.INPUT_CONTRACT_MISSING),
        (replace(value.request, context_bindings=value.request.context_bindings[:-1]), RuntimeBlockReason.CONTEXT_BINDING_MISSING),
    ):
        adapter = FakeAdapter()
        outcome = run(replace(value, request=changed), adapter)
        assert outcome.result.block_reason is reason
        assert adapter.calls == []


def test_personal_data_and_missing_depersonalization_binding_are_blocked():
    value = envelope()
    personal_boundary = replace(
        value.invocation_boundary,
        request=replace(value.invocation_boundary.request, data_scope=InvocationDataScope.PERSONAL),
    )
    adapter = FakeAdapter()
    outcome = run(replace(value, invocation_boundary=personal_boundary), adapter)
    assert adapter.calls == []
    assert outcome.result.status is RuntimeExecutionStatus.BLOCKED
    missing_binding = replace(value.request, context_bindings=value.request.context_bindings[:-1])
    adapter = FakeAdapter()
    assert run(replace(value, request=missing_binding), adapter).result.block_reason is RuntimeBlockReason.CONTEXT_BINDING_MISSING
    assert adapter.calls == []


@pytest.mark.parametrize(
    "status,expected,reason",
    (
        (ProviderTechnicalStatus.TIMED_OUT, RuntimeExecutionStatus.TIMED_OUT, RuntimeBlockReason.PROVIDER_TIMEOUT),
        (ProviderTechnicalStatus.ERROR, RuntimeExecutionStatus.PROVIDER_ERROR, RuntimeBlockReason.PROVIDER_TECHNICAL_ERROR),
    ),
)
def test_timeout_and_provider_error_are_typed_without_fallback(status, expected, reason):
    adapter = FakeAdapter(status=status)
    outcome = run(adapter=adapter)
    assert len(adapter.calls) == 1
    assert outcome.result.status is expected
    assert outcome.result.block_reason is reason
    assert outcome.result.degradation_notice == "The supplied provider result is unavailable."


def test_provider_exception_is_controlled_and_not_retried():
    adapter = FakeAdapter(raises=True)
    outcome = run(adapter=adapter)
    assert len(adapter.calls) == 1
    assert outcome.result.status is RuntimeExecutionStatus.PROVIDER_ERROR
    assert outcome.evidence.provider_called is True


def test_non_contract_provider_response_is_rejected_without_second_call():
    adapter = FakeAdapter()

    def invalid_result(request_value):
        adapter.calls.append(request_value)
        return {"orientation": "not a typed provider result"}

    adapter.invoke = invalid_result
    outcome = run(adapter=adapter)
    assert len(adapter.calls) == 1
    assert outcome.result.status is RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE
    assert outcome.result.block_reason is RuntimeBlockReason.PROVIDER_RESPONSE_INVALID


def test_elapsed_timeout_boundary_blocks_late_success_without_retry():
    adapter = FakeAdapter()

    def late_result(request_value):
        adapter.calls.append(request_value)
        return ProviderAdapterResult(
            provider_reference=adapter.provider_reference,
            capability=adapter.capability,
            output_kind=ProviderOutputKind.B1_GENERAL_ORIENTATION,
            technical_status=ProviderTechnicalStatus.SUCCEEDED,
            output_fields=adapter.fields,
            started_at=NOW,
            finished_at=NOW + timedelta(seconds=6),
        )

    adapter.invoke = late_result
    outcome = run(adapter=adapter)
    assert len(adapter.calls) == 1
    assert outcome.result.status is RuntimeExecutionStatus.TIMED_OUT


def test_runtime_record_provenance_mismatch_blocks_before_provider_call():
    adapter = FakeAdapter()
    wrong_metadata = replace(metadata(), provenance=provenance("different"))
    outcome = B1ReadOnlyRuntimeExecutor().execute(envelope(), adapter, wrong_metadata)
    assert adapter.calls == []
    assert outcome.result.block_reason is RuntimeBlockReason.PROVENANCE_INCONSISTENT


@pytest.mark.parametrize(
    "kind",
    (
        ProviderOutputKind.B2_PERSONAL_PREPARATION,
        ProviderOutputKind.B3_PROFESSIONAL_BOUNDARY,
        ProviderOutputKind.STATE_CHANGE_INSTRUCTION,
        ProviderOutputKind.TOOL_INSTRUCTION,
    ),
)
def test_output_boundary_rejects_non_b1_and_executing_output_kinds(kind):
    adapter = FakeAdapter(kind=kind)
    outcome = run(adapter=adapter)
    assert outcome.result.status is RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE
    assert outcome.result.block_reason is RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED
    assert outcome.result.output_fields == ()


def test_output_boundary_rejects_unexpected_missing_oversized_and_wrong_identity():
    cases = (
        FakeAdapter(fields=(RuntimeDataField("unexpected", "value"),)),
        FakeAdapter(fields=(RuntimeDataField("source_notice", "value"),)),
        FakeAdapter(fields=(RuntimeDataField("orientation", "x" * 501),)),
    )
    for adapter in cases:
        outcome = run(adapter=adapter)
        assert outcome.result.status is RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE
    result = FakeAdapter().invoke(None)
    with pytest.raises(B1RuntimeValidationError):
        B1RuntimeOutputValidator().validate(
            envelope().request, replace(result, provider_reference="other")
        )


def test_degraded_result_is_not_fallback_or_guardian_answer_activation():
    adapter = FakeAdapter(status=ProviderTechnicalStatus.DEGRADED)
    outcome = run(adapter=adapter)
    assert len(adapter.calls) == 1
    assert outcome.result.status is RuntimeExecutionStatus.DEGRADED
    assert outcome.result.provision_status is RuntimeProvisionStatus.DEGRADED_NOT_ACTIVATED
    assert not hasattr(outcome, "activate_answer")
    assert not hasattr(outcome, "retry")
    assert not hasattr(outcome, "fallback_provider")


def test_deterministic_repetition_has_no_persistence_audit_or_mutation():
    value = envelope()
    first = run(value, FakeAdapter())
    second = run(value, FakeAdapter())
    assert first == second
    assert first.request is value.request
    for name in ("persist", "audit_log", "save", "write", "select_provider", "retry"):
        assert not hasattr(B1ReadOnlyRuntimeExecutor(), name)
