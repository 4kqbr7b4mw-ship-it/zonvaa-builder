from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta
import inspect

import pytest

from governance.b2_capability_invocation import (
    B2CapabilityInvocationAssertion,
    B2CapabilityInvocationBinding,
    B2CapabilityInvocationBindingId,
    B2CapabilityInvocationDecisionId,
    B2CapabilityInvocationDecisionResult,
    B2CapabilityInvocationEvaluator,
    B2CapabilityInvocationEvidenceId,
    B2CapabilityInvocationFoundationValidator,
    B2CapabilityInvocationIntent,
    B2CapabilityInvocationObservationScope,
    B2CapabilityInvocationReceiptId,
    B2CapabilityInvocationRequest,
    B2CapabilityInvocationRequestId,
    B2CapabilityInvocationResolutionSnapshotId,
    B2CapabilityInvocationValidationError,
    B2CapabilityInvocationValidator,
    B2CapabilityInvocationViolation,
)
from governance.b2_provider_identity import (
    B2CapabilityDescriptor,
    B2NonPersonalReferenceId,
    B2ProviderIdentityId,
)
from governance.b2_authorization import B2D3Consent, B2Grant, B2PurposeScope
from governance.b2_provider_authorization import (
    B2AuthorizationFoundation,
    B2ProviderAuthorizationEvaluator,
)
from governance.b2_purpose_uodl_binding import (
    B2PurposeBindingValidator,
    B2PurposeComparisonRelation,
    B2PurposeUODLBindingFoundation,
    B2UODLMappingValidator,
)

from test_b2_purpose_uodl_binding import (
    NOW,
    full_package,
    provenance,
    purpose_binding,
    uodl_mapping,
)
from test_guardian_b2_provider_authorization import (
    AUTH_PROVENANCE,
    authority,
    corridor_package,
    current_bindings,
    provider_authorization,
    provider_identity,
)


def reference(value):
    return B2NonPersonalReferenceId("non-personal-reference:{}".format(value))


def binding(package=None):
    package = package or full_package()
    return B2CapabilityInvocationBinding(
        binding_id=B2CapabilityInvocationBindingId(
            "b2-capability-invocation-binding:foundation-01"
        ),
        provider_identity_reference=package.foundation.provider_identity.identity_id,
        provider_authorization_reference=(
            package.foundation.provider_authorization.authorization_id
        ),
        capability_descriptor=(
            B2CapabilityDescriptor.PERSONAL_PREPARATION_SERVICE_DESCRIPTOR
        ),
        purpose_binding_reference=package.purpose_binding.binding_id,
        uodl_mapping_reference=package.uodl_mapping.mapping_id,
        evidence_references=(reference("invocation-binding-01"),),
        provenance=provenance(),
        bound_at=NOW,
        observation_scope=(
            B2CapabilityInvocationObservationScope.REFERENCE_BINDING
        ),
    )


def request(package=None, invocation_binding=None, purpose=None):
    package = package or full_package()
    invocation_binding = invocation_binding or binding(package)
    purpose = purpose or package.purpose_binding.canonical_scope
    return B2CapabilityInvocationRequest(
        request_id=B2CapabilityInvocationRequestId(
            "b2-capability-invocation-request:foundation-01"
        ),
        data_corridor_reference=(
            package.foundation.data_corridor.corridor.corridor_id
        ),
        authority_reference=package.foundation.authority.authority_id,
        grant_reference=package.foundation.grant.grant_id,
        provider_identity_reference=package.foundation.provider_identity.identity_id,
        provider_authorization_reference=(
            package.foundation.provider_authorization.authorization_id
        ),
        purpose_binding_reference=package.purpose_binding.binding_id,
        uodl_mapping_reference=package.uodl_mapping.mapping_id,
        invocation_binding_reference=invocation_binding.binding_id,
        intent=B2CapabilityInvocationIntent(
            capability_descriptor=invocation_binding.capability_descriptor,
            purpose_scope=purpose,
        ),
        evaluated_at=NOW,
        evidence_references=(reference("invocation-request-01"),),
        provenance=provenance(),
        observation_scope=(
            B2CapabilityInvocationObservationScope.REQUEST_EVALUATION
        ),
    )


def evaluation(package=None, invocation_binding=None, invocation_request=None):
    package = package or full_package()
    invocation_binding = invocation_binding or binding(package)
    invocation_request = invocation_request or request(package, invocation_binding)
    return B2CapabilityInvocationEvaluator().evaluate(
        binding=invocation_binding,
        request=invocation_request,
        upstream_foundation=package,
        decision_id=B2CapabilityInvocationDecisionId(
            "b2-capability-invocation-decision:foundation-01"
        ),
        evidence_id=B2CapabilityInvocationEvidenceId(
            "b2-capability-invocation-evidence:foundation-01"
        ),
        receipt_id=B2CapabilityInvocationReceiptId(
            "b2-capability-invocation-receipt:foundation-01"
        ),
        resolution_snapshot_id=B2CapabilityInvocationResolutionSnapshotId(
            "b2-capability-invocation-resolution-snapshot:foundation-01"
        ),
        canonical_rule_references=(reference("adr-0065-rule-chain"),),
        canonical_input_references=(reference("adr-0065-input-chain"),),
        consistency_references=(reference("adr-0065-consistency-chain"),),
    )


def broad_full_package():
    corridor = corridor_package()
    broad_scope = B2PurposeScope(
        purposes=corridor.consent_boundary.allowed_use,
        data_classes=corridor.consent_boundary.allowed_scope,
    )
    consent = B2D3Consent(
        consent_reference="d3:foundation-01",
        purpose_scope=broad_scope,
        effective_from=NOW - timedelta(hours=1),
        effective_until=NOW + timedelta(days=1),
        revoked_at=None,
    )
    authority_value = authority()
    grant = B2Grant(
        grant_id="b2-grant:foundation-01",
        authority=authority_value,
        d3_consent=consent,
        t4_reference="t4:foundation-01",
        aav_reference="aav:foundation-01",
        uodl_reference="uodl:foundation-01",
        purpose_scope=broad_scope,
        provenance=AUTH_PROVENANCE,
    )
    identity = provider_identity()
    authorization = provider_authorization(identity, grant, corridor)
    bindings = current_bindings(grant, consent)
    provider_evidence = B2ProviderAuthorizationEvaluator().evaluate(
        authorization=authorization,
        provider_identity=identity,
        data_corridor=corridor,
        grant=grant,
        authority=bindings["authority"],
        d3_consent=bindings["d3_consent"],
        t4_receipt=bindings["t4_receipt"],
        aav_binding=bindings["aav_binding"],
        uodl_binding=bindings["uodl_binding"],
        evaluated_at=NOW,
        base_evidence_id="b2-evidence:foundation-base-01",
        provider_evidence_id="b2-provider-authorization-evidence:foundation-01",
    )
    base = B2AuthorizationFoundation(
        foundation_id="b2-foundation:adr-0065-broad-01",
        data_corridor=corridor,
        authority=bindings["authority"],
        grant=grant,
        provider_identity=identity,
        provider_authorization=authorization,
        d3_consent=bindings["d3_consent"],
        t4_receipt=bindings["t4_receipt"],
        aav_binding=bindings["aav_binding"],
        uodl_binding=bindings["uodl_binding"],
        evaluated_at=NOW,
        evidence=provider_evidence,
    )
    purpose = replace(
        purpose_binding(),
        canonical_scope=broad_scope,
        comparison_relation=B2PurposeComparisonRelation.IDENTICAL,
    )
    mapping = uodl_mapping()
    return B2PurposeUODLBindingFoundation(
        foundation=base,
        purpose_binding=purpose,
        purpose_evidence=B2PurposeBindingValidator().validate(
            purpose,
            corridor,
            reference("broad-purpose-receipt"),
        ),
        uodl_mapping=mapping,
        uodl_evidence=B2UODLMappingValidator().validate(
            mapping,
            reference("broad-uodl-receipt"),
        ),
    )


def test_valid_invocation_resolves_without_execution_and_is_deterministic():
    first = evaluation()
    second = evaluation()
    assert first == second
    assert first.decision.result is (
        B2CapabilityInvocationDecisionResult.CONSISTENT_FOR_NON_EXECUTING_RESOLUTION
    )
    assert first.decision.violations == ()
    assert first.receipt.assertions == (
        B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,
    )
    assert first.resolution_snapshot.assertions == (
        B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,
        B2CapabilityInvocationAssertion.CONTROLLED_STOP,
    )
    assert B2CapabilityInvocationFoundationValidator().validate(first) is first


def test_valid_narrower_invocation_purpose_resolves_without_execution():
    package = broad_full_package()
    narrower = B2PurposeScope(
        purposes=package.purpose_binding.canonical_scope.purposes,
        data_classes=(package.purpose_binding.canonical_scope.data_classes[0],),
    )
    invocation_binding = binding(package)
    result = evaluation(
        package,
        invocation_binding,
        request(package, invocation_binding, narrower),
    )
    assert result.decision.result is (
        B2CapabilityInvocationDecisionResult.CONSISTENT_FOR_NON_EXECUTING_RESOLUTION
    )
    assert result.request.intent.purpose_scope == narrower


def test_validator_preserves_complete_inputs():
    package = full_package()
    invocation_binding = binding(package)
    invocation_request = request(package, invocation_binding)
    assert (
        B2CapabilityInvocationValidator().validate(
            invocation_binding, invocation_request, package
        )
        is invocation_request
    )
    assert invocation_request.intent.purpose_scope is package.purpose_binding.canonical_scope
    assert package.foundation.provider_identity is package.foundation.provider_identity


@pytest.mark.parametrize(
    "field,value,violation",
    (
        ("data_corridor_reference", "b2-corridor-other", B2CapabilityInvocationViolation.CORRIDOR_REFERENCE_MISMATCH),
        ("grant_reference", "b2-grant:other", B2CapabilityInvocationViolation.GRANT_REFERENCE_MISMATCH),
        ("provider_identity_reference", B2ProviderIdentityId("b2-provider-identity:other"), B2CapabilityInvocationViolation.PROVIDER_IDENTITY_MISMATCH),
    ),
)
def test_inconsistent_request_rejects_with_controlled_stop(field, value, violation):
    package = full_package()
    invocation_binding = binding(package)
    invocation_request = replace(request(package, invocation_binding), **{field: value})
    result = evaluation(package, invocation_binding, invocation_request)
    assert result.decision.result is B2CapabilityInvocationDecisionResult.REJECTED_WITH_CONTROLLED_STOP
    assert violation in result.decision.violations
    assert B2CapabilityInvocationAssertion.CONTROLLED_STOP in result.resolution_snapshot.assertions
    with pytest.raises(B2CapabilityInvocationValidationError):
        B2CapabilityInvocationValidator().validate(
            invocation_binding, invocation_request, package
        )


def test_capability_mismatch_and_unlisted_capability_fail_closed():
    package = full_package()
    invocation_binding = binding(package)
    mismatched = replace(
        request(package, invocation_binding),
        intent=B2CapabilityInvocationIntent(
            B2CapabilityDescriptor.SOURCE_REFERENCE_SERVICE_DESCRIPTOR,
            package.purpose_binding.canonical_scope,
        ),
    )
    result = evaluation(package, invocation_binding, mismatched)
    assert result.decision.violations == (
        B2CapabilityInvocationViolation.CAPABILITY_NOT_DESCRIBED,
    )


def test_broader_or_non_comparable_purpose_fails_closed():
    package = full_package()
    broader = replace(
        request(package),
        intent=B2CapabilityInvocationIntent(
            B2CapabilityDescriptor.PERSONAL_PREPARATION_SERVICE_DESCRIPTOR,
            type(package.purpose_binding.canonical_scope)(
                purposes=tuple(type(package.purpose_binding.canonical_scope.purposes[0])),
                data_classes=package.purpose_binding.canonical_scope.data_classes,
            ),
        ),
    )
    result = evaluation(package, binding(package), broader)
    assert B2CapabilityInvocationViolation.PURPOSE_SCOPE_EXPANSION in result.decision.violations


def test_missing_evidence_naive_time_and_personal_ids_are_structurally_rejected():
    with pytest.raises(ValueError):
        replace(binding(), evidence_references=())
    with pytest.raises(ValueError):
        replace(
            request(),
            evaluated_at=datetime(2026, 8, 4, 12, 0),
            provenance=provenance(datetime(2026, 8, 4, 12, 0)),
        )
    with pytest.raises(ValueError):
        B2CapabilityInvocationRequestId(
            "b2-capability-invocation-request:person-account"
        )


@pytest.mark.parametrize(
    "field",
    (
        "request_id",
        "data_corridor_reference",
        "authority_reference",
        "grant_reference",
        "provider_identity_reference",
        "provider_authorization_reference",
        "purpose_binding_reference",
        "uodl_mapping_reference",
        "invocation_binding_reference",
        "intent",
        "evaluated_at",
        "provenance",
    ),
)
def test_missing_required_request_references_are_not_representable(field):
    with pytest.raises((TypeError, ValueError)):
        replace(request(), **{field: None})


def test_provider_authorization_purpose_uodl_binding_and_time_mismatches_reject():
    package = full_package()
    invocation_binding = binding(package)
    changes = (
        {
            "provider_authorization_reference": type(
                package.foundation.provider_authorization.authorization_id
            )("b2-provider-authorization:other")
        },
        {
            "purpose_binding_reference": type(package.purpose_binding.binding_id)(
                "b2-purpose-binding:other"
            )
        },
        {
            "uodl_mapping_reference": type(package.uodl_mapping.mapping_id)(
                "b2-uodl-mapping:other"
            )
        },
        {
            "evaluated_at": NOW.replace(hour=NOW.hour + 1),
            "provenance": provenance(NOW.replace(hour=NOW.hour + 1)),
        },
    )
    expected = (
        B2CapabilityInvocationViolation.PROVIDER_AUTHORIZATION_MISMATCH,
        B2CapabilityInvocationViolation.PURPOSE_BINDING_MISMATCH,
        B2CapabilityInvocationViolation.UODL_MAPPING_MISMATCH,
        B2CapabilityInvocationViolation.EVALUATION_TIME_MISMATCH,
    )
    for change, violation in zip(changes, expected):
        result = evaluation(
            package,
            invocation_binding,
            replace(request(package, invocation_binding), **change),
        )
        assert violation in result.decision.violations


def test_receipt_and_snapshot_cannot_claim_execution_or_continuation():
    result = evaluation()
    with pytest.raises(B2CapabilityInvocationValidationError):
        replace(
            result.receipt,
            assertions=(B2CapabilityInvocationAssertion.CONTROLLED_STOP,),
        )
    with pytest.raises(B2CapabilityInvocationValidationError):
        replace(
            result.resolution_snapshot,
            assertions=(B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,),
        )


def test_all_contracts_are_immutable():
    package = evaluation()
    for value in (
        package.binding,
        package.request,
        package.decision,
        package.evidence,
        package.receipt,
        package.resolution_snapshot,
        package,
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(value, fields(value)[0].name, None)


def test_decision_and_assertion_taxonomies_are_exactly_ratified():
    assert tuple(B2CapabilityInvocationDecisionResult) == (
        B2CapabilityInvocationDecisionResult.CONSISTENT_FOR_NON_EXECUTING_RESOLUTION,
        B2CapabilityInvocationDecisionResult.REJECTED_WITH_CONTROLLED_STOP,
    )
    assert tuple(B2CapabilityInvocationAssertion) == (
        B2CapabilityInvocationAssertion.NO_EXECUTION_OCCURRED,
        B2CapabilityInvocationAssertion.CONTROLLED_STOP,
    )
    for value in ("ACCEPTED", "EXECUTE", "READY_FOR_RUNTIME", "RUNTIME_APPROVED"):
        with pytest.raises(ValueError):
            B2CapabilityInvocationDecisionResult(value)


def test_no_separate_negative_evidence_or_runtime_surface_exists():
    import governance.b2_capability_invocation as module

    assert not hasattr(module, "B2NegativeCapabilityInvocationEvidence")
    forbidden_methods = (
        "execute", "invoke", "run", "dispatch", "send", "start",
        "enqueue", "schedule", "call", "trigger", "launch",
    )
    contracts = (
        B2CapabilityInvocationBinding,
        B2CapabilityInvocationRequest,
        type(evaluation().decision),
        type(evaluation().evidence),
        type(evaluation().receipt),
        type(evaluation().resolution_snapshot),
    )
    for contract in contracts:
        assert not any(hasattr(contract, method) for method in forbidden_methods)


def test_contract_fields_exclude_runtime_personal_and_status_semantics():
    forbidden = {
        "person", "name", "email", "user", "account", "payload", "endpoint",
        "url", "http_method", "function", "callback", "tool", "agent", "mcp",
        "queue", "event", "retry", "timeout", "scheduler", "session", "token",
        "cache", "permission", "secret", "key", "runtime_handle", "status",
        "pending", "approved", "active", "queued", "running", "executed",
        "completed", "failed", "revoked", "ready_for_runtime",
    }
    contracts = (
        B2CapabilityInvocationBinding,
        B2CapabilityInvocationRequest,
        type(evaluation().decision),
        type(evaluation().evidence),
        type(evaluation().receipt),
        type(evaluation().resolution_snapshot),
    )
    for contract in contracts:
        assert not forbidden.intersection(field.name for field in fields(contract))


def test_validator_and_evaluator_are_stateless_and_have_no_clock_or_io_source():
    for component in (
        B2CapabilityInvocationValidator,
        B2CapabilityInvocationEvaluator,
        B2CapabilityInvocationFoundationValidator,
    ):
        source = inspect.getsource(component).lower()
        for forbidden in (
            "datetime.now", "repository", "subprocess", "open(", "requests.",
            "cache", "session", "provider_client", "tool_client",
        ):
            assert forbidden not in source


def test_b1_and_governance_decisions_are_not_accepted_as_b2_types():
    from governance.capability_invocation import CapabilityInvocationRequest
    from governance.governance_decision_incident_evidence import GovernanceDecisionRecord

    with pytest.raises(TypeError):
        B2CapabilityInvocationValidator().validate(CapabilityInvocationRequest, request(), full_package())
    assert GovernanceDecisionRecord is not type(evaluation().decision)


def test_upstream_purpose_and_uodl_evidence_remain_required():
    package = full_package()
    invalid = replace(
        package,
        purpose_evidence=replace(
            package.purpose_evidence,
            input_evidence_references=(reference("different-purpose-input"),),
        ),
    )
    result = evaluation(invalid, binding(invalid), request(invalid, binding(invalid)))
    assert B2CapabilityInvocationViolation.UPSTREAM_FOUNDATION_INEFFECTIVE in result.decision.violations
