from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from governance.authority import (
    ActorResponsibilityBoundary,
    AuthorityActorClass,
    AuthorityCapability,
    AuthorityControlLevel,
    AuthorityDefinition,
    AuthorityDelegationRule,
    AuthorityExercise,
    AuthorityProvenance,
    AuthorityReviewStatus,
    AuthorityType,
    GuardianAuthorityModel,
)
from governance.capability_invocation import (
    CapabilityInvocationPackageCapability,
    CapabilityInvocationRequest,
    CapabilityInvocationResolutionSnapshot,
    CapabilityInvocationValidationError,
    GuardianCapabilityInvocationBoundary,
    GuardianCapabilityInvocationValidator,
    InvocationCheck,
    InvocationContextBinding,
    InvocationContextBindingType,
    InvocationDataScope,
    InvocationDecisionReason,
    InvocationDecisionStatus,
    InvocationOperationMode,
    InvocationReceiptValidationStatus,
    CapabilityInvocationDecision,
    CapabilityInvocationEvidence,
)
from governance.models import NormLevel
from governance.provider_authorization import (
    AuthorizationDecisionEvidence,
    AuthorizationDecisionType,
    AuthorizationExpirationEvidence,
    AuthorizationRevocationEvidence,
    AuthorizationSuspensionEvidence,
    AuthorizationUncertaintyStatus,
    DecidingActorReference,
    GuardianProviderAuthorizationPackage,
    ProviderAuthorizationGrant,
    ProviderAuthorizationResolutionSnapshot,
    ProviderAuthorizationStatus,
    ProviderIdentity,
    ProviderIdentityVerificationStatus,
    ProviderType,
)
from guardian_understanding.answer_boundary import (
    ALWAYS_FORBIDDEN_CAPABILITIES,
    AnswerBoundaryContract,
    AnswerCapability,
    AnswerOperatingMode,
)


NOW = datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc)


def provenance(reference="ADR-0050"):
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference=(
            "knowledge/adr/"
            "ADR-0050-guardian-capability-invocation-boundary-v1.md"
        ),
        decision_reference=reference,
    )


def authority_model():
    authority = AuthorityDefinition(
        authority_id="authority-b1-presentation",
        authority_type=AuthorityType.GUARDIAN_COMMUNICATION,
        responsibility="Present already supplied B1 orientation.",
        capabilities=(AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,),
        exercise=AuthorityExercise.DELEGABLE,
        revocable=True,
        required_control_levels=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
        joint_actor_classes=(),
        provenance=provenance(),
    )
    boundary = ActorResponsibilityBoundary(
        boundary_id="boundary-model-layer",
        actor_class=AuthorityActorClass.MODEL_LAYER,
        responsibilities=("Present supplied B1 content",),
        allowed_authority_references=(authority.authority_id,),
        prohibited_authority_references=(),
        provenance=provenance(),
    )
    return GuardianAuthorityModel(
        authority_model_id="authority-model-invocation-tests",
        version="1.0",
        authorities=(authority,),
        actor_boundaries=(
            boundary,
            ActorResponsibilityBoundary(
                boundary_id="boundary-operational",
                actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
                responsibilities=("Supply an approved delegation rule",),
                allowed_authority_references=(authority.authority_id,),
                prohibited_authority_references=(),
                provenance=provenance(),
            ),
        ),
        delegation_rules=(
            AuthorityDelegationRule(
                delegation_rule_id="rule-b1-model-provider",
                authority_reference=authority.authority_id,
                delegating_actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
                receiving_actor_classes=(AuthorityActorClass.MODEL_LAYER,),
                requires_explicit_human_confirmation=True,
                revocable=True,
                provenance=provenance(),
            ),
        ),
        prohibited_combinations=(),
        provenance=provenance(),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-authority-model",
    )


def provider():
    return ProviderIdentity(
        provider_id="provider-b1",
        provider_type=ProviderType.MODEL_PROVIDER,
        identity_reference="provider:b1",
        actor_class=AuthorityActorClass.MODEL_LAYER,
        responsibility_scope="Present supplied B1 content only.",
        supported_authority_types=(AuthorityType.GUARDIAN_COMMUNICATION,),
        origin_evidence_reference="origin:provider-b1",
        identity_verification_status=(
            ProviderIdentityVerificationStatus.VERIFIED_DECLARED
        ),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-provider-b1",
        valid_from=NOW,
        valid_until=NOW + timedelta(days=365),
        uncertainty_status=AuthorizationUncertaintyStatus.CERTAIN,
        provenance=provenance(),
    )


def authorization(status=ProviderAuthorizationStatus.AUTHORIZED, **changes):
    values = dict(
        authorization_id="authorization-b1",
        provider_reference="provider-b1",
        authority_reference="authority-b1-presentation",
        allowed_capabilities=(AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,),
        forbidden_capabilities=(),
        responsibility_boundary_reference="boundary-model-layer",
        status=status,
        valid_from=NOW,
        valid_until=NOW + timedelta(days=30),
        control_levels=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
        required_joint_actor_classes=(),
        delegable=True,
        revocable=True,
        granting_authority_reference="rule-b1-model-provider",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-authorization-b1",
        uncertainty_status=AuthorizationUncertaintyStatus.CERTAIN,
        provenance=provenance(),
    )
    values.update(changes)
    return ProviderAuthorizationGrant(**values)


def authorization_decision(grant):
    decision_type = {
        ProviderAuthorizationStatus.PROPOSED: AuthorizationDecisionType.PROPOSE,
        ProviderAuthorizationStatus.AUTHORIZED: AuthorizationDecisionType.AUTHORIZE,
        ProviderAuthorizationStatus.REJECTED: AuthorizationDecisionType.REJECT,
        ProviderAuthorizationStatus.SUSPENDED: AuthorizationDecisionType.SUSPEND,
        ProviderAuthorizationStatus.REVOKED: AuthorizationDecisionType.REVOKE,
        ProviderAuthorizationStatus.EXPIRED: AuthorizationDecisionType.EXPIRE,
    }[grant.status]
    return AuthorizationDecisionEvidence(
        decision_evidence_id="grant-decision-{}".format(grant.status.value.lower()),
        authorization_reference=grant.authorization_id,
        decision_type=decision_type,
        decision_reason="Supplied provider authorization decision.",
        checked_authority_rule_references=(grant.authority_reference,),
        checked_responsibility_boundary_references=(
            grant.responsibility_boundary_reference,
        ),
        detected_conflicts=(),
        required_control_levels=grant.control_levels,
        deciding_actors=(
            DecidingActorReference(
                actor_reference="actor-operational",
                actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            ),
        ),
        decided_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-grant-decision",
        provenance=provenance(),
    )


def lifecycle_evidence(grant):
    common = dict(
        authorization_reference=grant.authorization_id,
        reason="Supplied lifecycle evidence.",
        effective_at=NOW + timedelta(days=1),
        deciding_authority_reference=grant.granting_authority_reference,
        control_levels=grant.control_levels,
        previous_status=ProviderAuthorizationStatus.AUTHORIZED,
        provenance=provenance(),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-lifecycle",
    )
    if grant.status is ProviderAuthorizationStatus.SUSPENDED:
        return AuthorizationSuspensionEvidence(
            evidence_id="suspension-b1",
            resulting_status=ProviderAuthorizationStatus.SUSPENDED,
            **common
        )
    if grant.status is ProviderAuthorizationStatus.REVOKED:
        return AuthorizationRevocationEvidence(
            evidence_id="revocation-b1",
            resulting_status=ProviderAuthorizationStatus.REVOKED,
            **common
        )
    if grant.status is ProviderAuthorizationStatus.EXPIRED:
        return AuthorizationExpirationEvidence(
            evidence_id="expiration-b1",
            resulting_status=ProviderAuthorizationStatus.EXPIRED,
            **common
        )
    return None


def provider_snapshot(identity, grant, *, inconsistent=False):
    statuses = {
        ProviderAuthorizationStatus.AUTHORIZED: "authorized",
        ProviderAuthorizationStatus.SUSPENDED: "suspended",
        ProviderAuthorizationStatus.REVOKED: "revoked",
        ProviderAuthorizationStatus.EXPIRED: "expired",
    }
    groups = {name: () for name in statuses.values()}
    if grant.status in statuses:
        groups[statuses[grant.status]] = (grant,)
    allowed = (
        grant.allowed_capabilities
        if grant.status is ProviderAuthorizationStatus.AUTHORIZED
        else ()
    )
    if inconsistent:
        allowed = () if allowed else (AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,)
    return ProviderAuthorizationResolutionSnapshot(
        snapshot_id="provider-snapshot-b1",
        provider=identity,
        authorized=groups["authorized"],
        suspended=groups["suspended"],
        revoked=groups["revoked"],
        expired=groups["expired"],
        allowed_capabilities=allowed,
        forbidden_capabilities=(),
        control_levels=(
            grant.control_levels
            if grant.status is ProviderAuthorizationStatus.AUTHORIZED
            else ()
        ),
        responsibility_boundaries=(authority_model().actor_boundaries[0],),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-provider-snapshot",
        uncertainties=(
            (AuthorizationUncertaintyStatus.CERTAIN,)
            if grant.status
            in (
                ProviderAuthorizationStatus.AUTHORIZED,
                ProviderAuthorizationStatus.SUSPENDED,
                ProviderAuthorizationStatus.REVOKED,
                ProviderAuthorizationStatus.EXPIRED,
            )
            else ()
        ),
        provenance=provenance(),
    )


def provider_package(
    status=ProviderAuthorizationStatus.AUTHORIZED,
    *,
    include_snapshot=True,
    inconsistent_snapshot=False,
    grant_changes=None,
):
    identity = provider()
    grant = authorization(status, **(grant_changes or {}))
    lifecycle = lifecycle_evidence(grant)
    lifecycle_values = {
        "revocations": (),
        "suspensions": (),
        "expirations": (),
    }
    if isinstance(lifecycle, AuthorizationRevocationEvidence):
        lifecycle_values["revocations"] = (lifecycle,)
    elif isinstance(lifecycle, AuthorizationSuspensionEvidence):
        lifecycle_values["suspensions"] = (lifecycle,)
    elif isinstance(lifecycle, AuthorizationExpirationEvidence):
        lifecycle_values["expirations"] = (lifecycle,)
    snapshots = ()
    if include_snapshot:
        snapshots = (provider_snapshot(identity, grant, inconsistent=inconsistent_snapshot),)
    return GuardianProviderAuthorizationPackage(
        package_id="provider-authorization-package-b1",
        authority_model=authority_model(),
        providers=(identity,),
        authorizations=(grant,),
        decisions=(authorization_decision(grant),),
        snapshots=snapshots,
        provenance=provenance(),
        **lifecycle_values
    )


def answer_boundary(mode=AnswerOperatingMode.B1_GENERAL_ORIENTATION):
    allowed = (AnswerCapability.READ_TYPED_INPUT,)
    if mode is AnswerOperatingMode.B1_GENERAL_ORIENTATION:
        allowed += (AnswerCapability.PRESENT_GENERAL_INFORMATION,)
    elif mode is AnswerOperatingMode.B2_PERSONAL_PREPARATION:
        allowed += (AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,)
    else:
        allowed += (AnswerCapability.STATE_CLEAR_NON_CONFIRMATION,)
    return AnswerBoundaryContract(
        boundary_id="answer-boundary-b1",
        requested_mode=mode,
        effective_mode=mode,
        classification_reason="Supplied mode for invocation.",
        affected_domains=("general-orientation",),
        has_personal_context=False,
        requests_professional_case_decision=(
            mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        ),
        requires_clear_non_confirmation=(
            mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        ),
        boundary_statement=(
            "Ich kann das nicht bestätigen."
            if mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
            else None
        ),
        allowed_capabilities=allowed,
        forbidden_capabilities=ALWAYS_FORBIDDEN_CAPABILITIES,
    )


def request(**changes):
    values = dict(
        invocation_id="invocation-b1",
        requestor_reference="requestor:guardian",
        provider_reference="provider-b1",
        authorization_reference="authorization-b1",
        authority_reference="authority-b1-presentation",
        capability=AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,
        requested_operation="Present supplied general orientation.",
        operation_mode=InvocationOperationMode.READ_ONLY,
        maximum_answer_mode=AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        answer_boundary_reference="answer-boundary-b1",
        context_bindings=(
            InvocationContextBinding(
                "context-jurisdiction",
                InvocationContextBindingType.JURISDICTION,
                "jurisdiction:de",
            ),
            InvocationContextBinding(
                "context-purpose",
                InvocationContextBindingType.PURPOSE,
                "purpose:general-orientation",
            ),
            InvocationContextBinding(
                "context-data-scope",
                InvocationContextBindingType.DATA_SCOPE,
                "data-scope:depersonalized",
            ),
        ),
        data_scope=InvocationDataScope.DEPERSONALIZED,
        source_chain_references=("source-chain-b1",),
        source_chains_required=True,
        input_contract_reference="input-contract:b1",
        input_schema_version="1.0",
        input_reference="input:b1",
        input_constraints=("typed-input-only",),
        required_control_levels=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
        provided_joint_actor_classes=(),
        requested_at=NOW,
        uncertainty_status=AuthorizationUncertaintyStatus.CERTAIN,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-request",
        provenance=provenance(),
    )
    values.update(changes)
    return CapabilityInvocationRequest(**values)


REASON_CHECK = {
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
    InvocationDecisionReason.RESOLUTION_SNAPSHOT_MISSING: InvocationCheck.RESOLUTION_SNAPSHOT,
    InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT: InvocationCheck.RESOLUTION_SNAPSHOT,
    InvocationDecisionReason.INPUT_CONTRACT_MISSING: InvocationCheck.INPUT_CONTRACT,
    InvocationDecisionReason.PROVENANCE_INCONSISTENT: InvocationCheck.PROVENANCE,
    InvocationDecisionReason.GOVERNANCE_GAP: InvocationCheck.AUTHORITY_MODEL,
}


def invocation_boundary(
    reason=None,
    *,
    request_value=None,
    package_value=None,
    answer_boundary_value=None,
):
    request_value = request_value or request()
    package_value = package_value or provider_package()
    answer_boundary_value = answer_boundary_value or answer_boundary(
        request_value.maximum_answer_mode
    )
    status = InvocationDecisionStatus.ACCEPTED
    reasons = ()
    if reason is not None:
        status = (
            InvocationDecisionStatus.REJECTED
            if reason
            in (
                InvocationDecisionReason.PROVIDER_UNKNOWN,
                InvocationDecisionReason.AUTHORIZATION_MISSING,
            )
            else InvocationDecisionStatus.BLOCKED
        )
        reasons = (reason,)
    decision_value = CapabilityInvocationDecision(
        decision_id="invocation-decision-b1",
        invocation_reference=request_value.invocation_id,
        status=status,
        reasons=reasons,
        decision_reason="Supplied invocation boundary decision.",
        decided_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-invocation-decision",
        provenance=provenance(),
    )
    failed = () if reason is None else (REASON_CHECK[reason],)
    passed = tuple(item for item in InvocationCheck if item not in failed)
    lifecycle_refs = tuple(
        item.evidence_id
        for values in (
            package_value.revocations,
            package_value.suspensions,
            package_value.expirations,
            package_value.restorations,
        )
        for item in values
        if item.authorization_reference == request_value.authorization_reference
    )
    matching_snapshots = tuple(
        item
        for item in package_value.snapshots
        if item.provider.provider_id == request_value.provider_reference
    )
    snapshot_reference = (
        matching_snapshots[0].snapshot_id if len(matching_snapshots) == 1 else None
    )
    evidence_value = CapabilityInvocationEvidence(
        evidence_id="invocation-evidence-b1",
        invocation_reference=request_value.invocation_id,
        request_reference=request_value.invocation_id,
        decision_reference=decision_value.decision_id,
        checked_provider_reference=(
            None
            if reason is InvocationDecisionReason.PROVIDER_UNKNOWN
            else request_value.provider_reference
        ),
        checked_authorization_reference=(
            None
            if reason is InvocationDecisionReason.AUTHORIZATION_MISSING
            else request_value.authorization_reference
        ),
        checked_authority_reference=(
            None
            if reason
            in (
                InvocationDecisionReason.PROVIDER_UNKNOWN,
                InvocationDecisionReason.AUTHORIZATION_MISSING,
            )
            else request_value.authority_reference
        ),
        checked_resolution_snapshot_reference=snapshot_reference,
        checked_lifecycle_evidence_references=lifecycle_refs,
        checked_answer_mode=request_value.maximum_answer_mode,
        checked_operation_mode=request_value.operation_mode,
        checked_control_levels=request_value.required_control_levels,
        detected_conflicts=(),
        validator_references=(
            "GuardianAuthorityModelValidator",
            "GuardianProviderAuthorizationValidator",
            "GuardianAnswerBoundaryValidator",
            "GuardianCapabilityInvocationValidator",
        ),
        passed_checks=passed,
        failed_checks=failed,
        result=status,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-invocation-evidence",
        provenance=provenance(),
    )
    return GuardianCapabilityInvocationBoundary(
        boundary_id="capability-invocation-boundary-b1",
        provider_authorization_package=package_value,
        answer_boundary=answer_boundary_value,
        request=request_value,
        decision=decision_value,
        evidence=evidence_value,
        provenance=provenance(),
    )


def validate_reason(reason, request_value=None, package_value=None, boundary_value=None):
    value = invocation_boundary(
        reason,
        request_value=request_value,
        package_value=package_value,
        answer_boundary_value=boundary_value,
    )
    assert GuardianCapabilityInvocationValidator().validate(value) is value
    assert value.decision.reasons == (reason,)
    return value


def test_valid_b1_request_is_accepted_immutable_and_deterministic():
    value = invocation_boundary()
    validator = GuardianCapabilityInvocationValidator()
    assert validator.validate(value) is value
    assert validator.validate(value) is value
    assert value.decision.status is InvocationDecisionStatus.ACCEPTED
    with pytest.raises(FrozenInstanceError):
        value.request.invocation_id = "changed"


@pytest.mark.parametrize(
    "operation_mode",
    (
        InvocationOperationMode.READ_ONLY,
        InvocationOperationMode.SIMULATION,
        InvocationOperationMode.DEGRADED,
    ),
)
def test_each_allowed_v1_operation_mode_remains_declarative(operation_mode):
    value = invocation_boundary(request_value=request(operation_mode=operation_mode))
    assert GuardianCapabilityInvocationValidator().validate(value) is value


def test_missing_provider_or_authorization_is_rejected():
    validate_reason(
        InvocationDecisionReason.PROVIDER_UNKNOWN,
        request(provider_reference="provider-unknown"),
    )
    validate_reason(
        InvocationDecisionReason.AUTHORIZATION_MISSING,
        request(authorization_reference="authorization-unknown"),
    )


@pytest.mark.parametrize(
    "status,reason",
    (
        (
            ProviderAuthorizationStatus.PROPOSED,
            InvocationDecisionReason.AUTHORIZATION_NOT_AUTHORIZED,
        ),
        (
            ProviderAuthorizationStatus.SUSPENDED,
            InvocationDecisionReason.AUTHORIZATION_SUSPENDED,
        ),
        (
            ProviderAuthorizationStatus.REVOKED,
            InvocationDecisionReason.AUTHORIZATION_REVOKED,
        ),
        (
            ProviderAuthorizationStatus.EXPIRED,
            InvocationDecisionReason.AUTHORIZATION_EXPIRED,
        ),
    ),
)
def test_non_authorized_and_lifecycle_statuses_are_blocked(status, reason):
    validate_reason(reason, package_value=provider_package(status))


def test_wrong_authority_and_denied_capability_are_blocked():
    validate_reason(
        InvocationDecisionReason.AUTHORITY_MISMATCH,
        request(authority_reference="authority-unknown"),
    )
    validate_reason(
        InvocationDecisionReason.CAPABILITY_DENIED,
        request(capability=AuthorityCapability.VALIDATE_TYPED_CONTRACT),
    )


def test_responsibility_control_and_joint_boundaries_block():
    validate_reason(
        InvocationDecisionReason.RESPONSIBILITY_BOUNDARY_EXCEEDED,
        package_value=provider_package(
            grant_changes={"responsibility_boundary_reference": "wrong-boundary"}
        ),
    )
    validate_reason(
        InvocationDecisionReason.CONTROL_LEVEL_INSUFFICIENT,
        request(
            required_control_levels=(AuthorityControlLevel.STRUCTURAL_VALIDATION,)
        ),
    )
    validate_reason(
        InvocationDecisionReason.JOINT_CONTROL_INCOMPLETE,
        package_value=provider_package(
            grant_changes={
                "required_joint_actor_classes": (
                    AuthorityActorClass.TRUST_COUNCIL,
                )
            }
        ),
    )


@pytest.mark.parametrize(
    "mode",
    (
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
    ),
)
def test_b2_and_b3_requests_are_blocked(mode):
    validate_reason(
        InvocationDecisionReason.CLASSIFICATION_TOO_HIGH,
        request(maximum_answer_mode=mode),
        boundary_value=answer_boundary(mode),
    )


@pytest.mark.parametrize(
    "mode",
    (InvocationOperationMode.READ_WRITE, InvocationOperationMode.PRIVILEGED),
)
def test_write_and_privileged_operation_modes_are_blocked(mode):
    validate_reason(
        InvocationDecisionReason.OPERATION_MODE_NOT_ALLOWED,
        request(operation_mode=mode),
    )


def test_missing_context_source_input_and_snapshot_are_blocked():
    incomplete_context = request(context_bindings=request().context_bindings[:1])
    validate_reason(
        InvocationDecisionReason.CONTEXT_BINDING_MISSING,
        incomplete_context,
    )
    validate_reason(
        InvocationDecisionReason.SOURCE_BINDING_MISSING,
        request(source_chain_references=()),
    )
    validate_reason(
        InvocationDecisionReason.INPUT_CONTRACT_MISSING,
        request(input_contract_reference=None),
    )
    validate_reason(
        InvocationDecisionReason.RESOLUTION_SNAPSHOT_MISSING,
        package_value=provider_package(include_snapshot=False),
    )


def test_inconsistent_provider_snapshot_is_blocked():
    validate_reason(
        InvocationDecisionReason.RESOLUTION_SNAPSHOT_INCONSISTENT,
        package_value=provider_package(inconsistent_snapshot=True),
    )


def test_inconsistent_provenance_is_blocked_fail_closed():
    validate_reason(
        InvocationDecisionReason.PROVENANCE_INCONSISTENT,
        request(provenance=provenance("different-decision")),
    )


def test_accepted_decision_cannot_hide_a_failed_check():
    value = invocation_boundary()
    wrong = replace(
        value,
        request=replace(value.request, operation_mode=InvocationOperationMode.READ_WRITE),
        evidence=replace(
            value.evidence,
            checked_operation_mode=InvocationOperationMode.READ_WRITE,
        ),
    )
    with pytest.raises(CapabilityInvocationValidationError) as error:
        GuardianCapabilityInvocationValidator().validate(wrong)
    assert error.value.code == "FAIL_CLOSED_DECISION_MISMATCH"


def test_receipt_is_created_without_persistence_or_execution():
    value = invocation_boundary()
    validator = GuardianCapabilityInvocationValidator()
    receipt = validator.create_receipt(
        value,
        receipt_id="invocation-receipt-b1",
        validated_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-receipt",
        provenance=provenance(),
    )
    assert receipt.validation_status is InvocationReceiptValidationStatus.VALIDATED
    assert receipt.decision_status is InvocationDecisionStatus.ACCEPTED
    assert receipt.failed_checks == ()
    assert receipt.passed_checks == tuple(InvocationCheck)
    repeated = validator.create_receipt(
        value,
        receipt_id="invocation-receipt-b1",
        validated_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-receipt",
        provenance=provenance(),
    )
    assert repeated == receipt
    with pytest.raises(FrozenInstanceError):
        receipt.receipt_id = "changed"


def test_complete_read_only_resolution_snapshot_keeps_original_objects():
    value = invocation_boundary()
    validator = GuardianCapabilityInvocationValidator()
    receipt = validator.create_receipt(
        value,
        receipt_id="invocation-receipt-b1",
        validated_at=NOW,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-receipt",
        provenance=provenance(),
    )
    snapshot = validator.create_resolution_snapshot(
        value,
        receipt,
        snapshot_id="invocation-resolution-b1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-invocation-resolution",
        provenance=provenance(),
    )
    assert isinstance(snapshot, CapabilityInvocationResolutionSnapshot)
    assert snapshot.request is value.request
    assert snapshot.decision is value.decision
    assert snapshot.evidence is value.evidence
    assert snapshot.receipt is receipt
    assert snapshot.provider is value.provider_authorization_package.providers[0]
    assert snapshot.authorization is value.provider_authorization_package.authorizations[0]
    assert (
        snapshot.provider_authorization_snapshot
        is value.provider_authorization_package.snapshots[0]
    )


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in CapabilityInvocationPackageCapability
        if item is not CapabilityInvocationPackageCapability.DESCRIBE_INVOCATION
    ),
)
def test_every_executing_boundary_capability_is_rejected(capability):
    with pytest.raises(CapabilityInvocationValidationError) as error:
        GuardianCapabilityInvocationValidator().validate(
            replace(invocation_boundary(), capabilities=(capability,))
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_boundary_has_no_runtime_persistence_audit_or_activation_methods():
    value = invocation_boundary()
    for name in (
        "execute",
        "run",
        "activate",
        "select_provider",
        "authorize",
        "persist",
        "write_audit_log",
        "retry",
        "rate_limit",
        "circuit_breaker",
        "sign",
        "hash",
    ):
        assert not hasattr(value, name)
