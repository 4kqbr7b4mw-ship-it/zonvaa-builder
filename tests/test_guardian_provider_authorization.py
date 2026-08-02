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
    GuardianAuthorityValidationError,
    ProhibitedAuthorityCombination,
)
from governance.models import NormLevel
from governance.provider_authorization import (
    AuthorizationDecisionEvidence,
    AuthorizationDecisionType,
    AuthorizationExpirationEvidence,
    AuthorizationRestorationEvidence,
    AuthorizationRevocationEvidence,
    AuthorizationSuspensionEvidence,
    AuthorizationUncertaintyStatus,
    DecidingActorReference,
    GuardianProviderAuthorizationPackage,
    GuardianProviderAuthorizationValidator,
    ProviderAuthorizationGrant,
    ProviderAuthorizationPackageCapability,
    ProviderAuthorizationResolutionSnapshot,
    ProviderAuthorizationStatus,
    ProviderAuthorizationValidationError,
    ProviderIdentity,
    ProviderIdentityVerificationStatus,
    ProviderType,
)


NOW = datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc)


def provenance():
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference="knowledge/adr/ADR-0049-guardian-provider-authorization-v1.md",
        decision_reference="ADR-0049",
    )


def authority_model():
    internal = AuthorityDefinition(
        authority_id="authority-internal-validation",
        authority_type=AuthorityType.DETERMINISTIC_VALIDATION,
        responsibility="Validate supplied typed contracts.",
        capabilities=(AuthorityCapability.VALIDATE_TYPED_CONTRACT,),
        exercise=AuthorityExercise.DELEGABLE,
        revocable=True,
        required_control_levels=(AuthorityControlLevel.STRUCTURAL_VALIDATION,),
        joint_actor_classes=(),
        provenance=provenance(),
    )
    human = AuthorityDefinition(
        authority_id="authority-human-review",
        authority_type=AuthorityType.PROFESSIONAL_JUDGMENT,
        responsibility="Document supplied professional review.",
        capabilities=(AuthorityCapability.MAKE_PROFESSIONAL_JUDGMENT,),
        exercise=AuthorityExercise.NON_DELEGABLE,
        revocable=True,
        required_control_levels=(AuthorityControlLevel.INDEPENDENT_REVIEW,),
        joint_actor_classes=(),
        provenance=provenance(),
    )
    model = AuthorityDefinition(
        authority_id="authority-model-description",
        authority_type=AuthorityType.GUARDIAN_COMMUNICATION,
        responsibility="Present supplied non-authoritative content.",
        capabilities=(AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,),
        exercise=AuthorityExercise.DELEGABLE,
        revocable=True,
        required_control_levels=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
        joint_actor_classes=(),
        provenance=provenance(),
    )
    joint = AuthorityDefinition(
        authority_id="authority-joint-governance",
        authority_type=AuthorityType.GOVERNANCE_OVERSIGHT,
        responsibility="Exercise supplied joint governance approval.",
        capabilities=(AuthorityCapability.APPROVE_CONSTITUTION_CHANGE,),
        exercise=AuthorityExercise.JOINT_EXERCISE,
        revocable=False,
        required_control_levels=(AuthorityControlLevel.MULTI_PARTY_CONTROL,),
        joint_actor_classes=(
            AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            AuthorityActorClass.TRUST_COUNCIL,
            AuthorityActorClass.USER_CONVENTION,
        ),
        provenance=provenance(),
    )
    authorities = (internal, human, model, joint)
    authority_ids = tuple(item.authority_id for item in authorities)

    def boundary(identifier, actor_class, allowed):
        return ActorResponsibilityBoundary(
            boundary_id=identifier,
            actor_class=actor_class,
            responsibilities=("Declared responsibility",),
            allowed_authority_references=allowed,
            prohibited_authority_references=tuple(
                item for item in authority_ids if item not in allowed
            ),
            provenance=provenance(),
        )

    boundaries = (
        boundary(
            "boundary-operational",
            AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            (internal.authority_id, model.authority_id, joint.authority_id),
        ),
        boundary(
            "boundary-core",
            AuthorityActorClass.DETERMINISTIC_CORE,
            (internal.authority_id,),
        ),
        boundary(
            "boundary-human-professional",
            AuthorityActorClass.HUMAN_PROFESSIONAL,
            (human.authority_id,),
        ),
        boundary(
            "boundary-model",
            AuthorityActorClass.MODEL_LAYER,
            (model.authority_id,),
        ),
        boundary(
            "boundary-trust",
            AuthorityActorClass.TRUST_COUNCIL,
            (joint.authority_id,),
        ),
        boundary(
            "boundary-users",
            AuthorityActorClass.USER_CONVENTION,
            (joint.authority_id,),
        ),
    )
    return GuardianAuthorityModel(
        authority_model_id="authority-model-provider-tests",
        version="1.0",
        authorities=authorities,
        actor_boundaries=boundaries,
        delegation_rules=(
            AuthorityDelegationRule(
                delegation_rule_id="rule-internal-to-core",
                authority_reference=internal.authority_id,
                delegating_actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
                receiving_actor_classes=(AuthorityActorClass.DETERMINISTIC_CORE,),
                requires_explicit_human_confirmation=True,
                revocable=True,
                provenance=provenance(),
            ),
            AuthorityDelegationRule(
                delegation_rule_id="rule-model-to-model-layer",
                authority_reference=model.authority_id,
                delegating_actor_class=AuthorityActorClass.OPERATIONAL_LEADERSHIP,
                receiving_actor_classes=(AuthorityActorClass.MODEL_LAYER,),
                requires_explicit_human_confirmation=True,
                revocable=True,
                provenance=provenance(),
            ),
        ),
        prohibited_combinations=(
            ProhibitedAuthorityCombination(
                combination_id="combination-human-model",
                first_authority_reference=human.authority_id,
                second_authority_reference=model.authority_id,
                reason="Professional judgment and model presentation stay separate.",
                provenance=provenance(),
            ),
        ),
        provenance=provenance(),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-authority-model",
    )


def provider(
    identifier="provider-internal",
    provider_type=ProviderType.INTERNAL_SYSTEM_COMPONENT,
    actor_class=AuthorityActorClass.DETERMINISTIC_CORE,
    supported=(AuthorityType.DETERMINISTIC_VALIDATION,),
):
    return ProviderIdentity(
        provider_id=identifier,
        provider_type=provider_type,
        identity_reference="identity:{}".format(identifier),
        actor_class=actor_class,
        responsibility_scope="Provided scope for {}".format(identifier),
        supported_authority_types=supported,
        origin_evidence_reference="origin:{}".format(identifier),
        identity_verification_status=(
            ProviderIdentityVerificationStatus.VERIFIED_DECLARED
        ),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:{}".format(identifier),
        valid_from=NOW,
        valid_until=NOW + timedelta(days=365),
        uncertainty_status=AuthorizationUncertaintyStatus.CERTAIN,
        provenance=provenance(),
    )


def grant(
    identity=None,
    identifier="authorization-internal",
    authority_id="authority-internal-validation",
    capability=AuthorityCapability.VALIDATE_TYPED_CONTRACT,
    boundary_id="boundary-core",
    status=ProviderAuthorizationStatus.AUTHORIZED,
    controls=(AuthorityControlLevel.STRUCTURAL_VALIDATION,),
    joint=(),
    delegable=True,
    revocable=True,
    granting_reference="rule-internal-to-core",
    valid_from=NOW,
    valid_until=None,
):
    identity = identity or provider()
    return ProviderAuthorizationGrant(
        authorization_id=identifier,
        provider_reference=identity.provider_id,
        authority_reference=authority_id,
        allowed_capabilities=(capability,),
        forbidden_capabilities=(),
        responsibility_boundary_reference=boundary_id,
        status=status,
        valid_from=valid_from,
        valid_until=valid_until or NOW + timedelta(days=30),
        control_levels=controls,
        required_joint_actor_classes=joint,
        delegable=delegable,
        revocable=revocable,
        granting_authority_reference=granting_reference,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:{}".format(identifier),
        uncertainty_status=AuthorizationUncertaintyStatus.CERTAIN,
        provenance=provenance(),
    )


def decision(value, decision_type=None, deciding_classes=None):
    expected = {
        ProviderAuthorizationStatus.PROPOSED: AuthorizationDecisionType.PROPOSE,
        ProviderAuthorizationStatus.AUTHORIZED: AuthorizationDecisionType.AUTHORIZE,
        ProviderAuthorizationStatus.REJECTED: AuthorizationDecisionType.REJECT,
        ProviderAuthorizationStatus.SUSPENDED: AuthorizationDecisionType.SUSPEND,
        ProviderAuthorizationStatus.REVOKED: AuthorizationDecisionType.REVOKE,
        ProviderAuthorizationStatus.EXPIRED: AuthorizationDecisionType.EXPIRE,
    }[value.status]
    deciding_classes = deciding_classes or (AuthorityActorClass.OPERATIONAL_LEADERSHIP,)
    return AuthorizationDecisionEvidence(
        decision_evidence_id="decision:{}".format(value.authorization_id),
        authorization_reference=value.authorization_id,
        decision_type=decision_type or expected,
        decision_reason="Provided decision reason",
        checked_authority_rule_references=(value.authority_reference,),
        checked_responsibility_boundary_references=(
            value.responsibility_boundary_reference,
        ),
        detected_conflicts=(),
        required_control_levels=value.control_levels,
        deciding_actors=tuple(
            DecidingActorReference(
                actor_reference="actor:{}".format(item.value),
                actor_class=item,
            )
            for item in deciding_classes
        ),
        decided_at=value.valid_from,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-decision:{}".format(value.authorization_id),
        provenance=provenance(),
    )


def package(identity=None, value=None, **changes):
    identity = identity or provider()
    value = value or grant(identity)
    data = {
        "package_id": "provider-authorization-package",
        "authority_model": authority_model(),
        "providers": (identity,),
        "authorizations": (value,),
        "decisions": (decision(value),),
        "provenance": provenance(),
    }
    data.update(changes)
    return GuardianProviderAuthorizationPackage(**data)


def lifecycle(evidence_type, value, previous, resulting, suffix):
    return evidence_type(
        evidence_id="{}:{}".format(suffix, value.authorization_id),
        authorization_reference=value.authorization_id,
        reason="Provided {} reason".format(suffix),
        effective_at=value.valid_from + timedelta(days=1),
        deciding_authority_reference=value.granting_authority_reference,
        control_levels=value.control_levels,
        previous_status=previous,
        resulting_status=resulting,
        provenance=provenance(),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:{}:{}".format(suffix, value.authorization_id),
    )


def test_valid_internal_system_provider_authorization_is_immutable_and_stable():
    value = package()
    validator = GuardianProviderAuthorizationValidator()

    assert validator.validate(value) is value
    assert validator.validate(value) is value
    with pytest.raises(FrozenInstanceError):
        value.package_id = "changed"


def test_valid_human_review_provider_uses_non_delegable_authority_directly():
    identity = provider(
        "provider-human-review",
        ProviderType.HUMAN_REVIEW_PROVIDER,
        AuthorityActorClass.HUMAN_PROFESSIONAL,
        (AuthorityType.PROFESSIONAL_JUDGMENT,),
    )
    value = grant(
        identity,
        "authorization-human-review",
        "authority-human-review",
        AuthorityCapability.MAKE_PROFESSIONAL_JUDGMENT,
        "boundary-human-professional",
        controls=(AuthorityControlLevel.INDEPENDENT_REVIEW,),
        delegable=False,
        granting_reference="authority-human-review",
    )

    assert GuardianProviderAuthorizationValidator().validate(
        package(identity, value)
    ).authorizations[0] is value


def test_valid_model_provider_is_only_assigned_supplied_descriptive_capability():
    identity = provider(
        "provider-model",
        ProviderType.MODEL_PROVIDER,
        AuthorityActorClass.MODEL_LAYER,
        (AuthorityType.GUARDIAN_COMMUNICATION,),
    )
    value = grant(
        identity,
        "authorization-model-description",
        "authority-model-description",
        AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,
        "boundary-model",
        controls=(AuthorityControlLevel.EXPLICIT_HUMAN_CONTROL,),
        granting_reference="rule-model-to-model-layer",
    )

    result = GuardianProviderAuthorizationValidator().validate(package(identity, value))
    assert result is not None
    assert value.allowed_capabilities == (
        AuthorityCapability.PRESENT_GUARDIAN_RESPONSE,
    )


def test_actor_class_and_responsibility_boundary_must_match_authority_model():
    identity = replace(provider(), actor_class=AuthorityActorClass.MODEL_LAYER)
    with pytest.raises(ProviderAuthorizationValidationError) as actor_error:
        GuardianProviderAuthorizationValidator().validate(package(identity))
    assert actor_error.value.code == "BOUNDARY_REFERENCE_MISMATCH"

    value = replace(grant(), responsibility_boundary_reference="boundary-model")
    with pytest.raises(ProviderAuthorizationValidationError) as boundary_error:
        GuardianProviderAuthorizationValidator().validate(package(value=value))
    assert boundary_error.value.code == "BOUNDARY_REFERENCE_MISMATCH"


def test_provider_supported_authority_type_and_capability_boundary_are_complete():
    identity = replace(
        provider(),
        supported_authority_types=(AuthorityType.GUARDIAN_COMMUNICATION,),
    )
    with pytest.raises(ProviderAuthorizationValidationError) as type_error:
        GuardianProviderAuthorizationValidator().validate(package(identity))
    assert type_error.value.code == "PROVIDER_AUTHORITY_TYPE_MISMATCH"

    value = replace(
        grant(),
        allowed_capabilities=(),
        forbidden_capabilities=(),
    )
    with pytest.raises(ProviderAuthorizationValidationError) as capability_error:
        GuardianProviderAuthorizationValidator().validate(package(value=value))
    assert capability_error.value.code == "INCOMPLETE_CAPABILITY_BOUNDARY"


def test_prohibited_authority_combination_is_rejected_by_existing_model_validator():
    base = authority_model()
    human_model = next(
        item
        for item in base.actor_boundaries
        if item.actor_class is AuthorityActorClass.HUMAN_PROFESSIONAL
    )
    invalid = replace(
        human_model,
        allowed_authority_references=(
            "authority-human-review",
            "authority-model-description",
        ),
        prohibited_authority_references=(
            "authority-internal-validation",
            "authority-joint-governance",
        ),
    )
    model = replace(
        base,
        actor_boundaries=tuple(
            invalid if item is human_model else item for item in base.actor_boundaries
        ),
    )
    with pytest.raises(GuardianAuthorityValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(
            replace(package(), authority_model=model)
        )
    assert error.value.code == "PROHIBITED_AUTHORITY_COMBINATION"


def test_joint_authority_requires_all_declared_actor_classes():
    identity = provider(
        "provider-operational",
        ProviderType.HUMAN_REVIEW_PROVIDER,
        AuthorityActorClass.OPERATIONAL_LEADERSHIP,
        (AuthorityType.GOVERNANCE_OVERSIGHT,),
    )
    value = grant(
        identity,
        "authorization-joint",
        "authority-joint-governance",
        AuthorityCapability.APPROVE_CONSTITUTION_CHANGE,
        "boundary-operational",
        controls=(AuthorityControlLevel.MULTI_PARTY_CONTROL,),
        joint=(
            AuthorityActorClass.OPERATIONAL_LEADERSHIP,
            AuthorityActorClass.TRUST_COUNCIL,
            AuthorityActorClass.USER_CONVENTION,
        ),
        delegable=False,
        revocable=False,
        granting_reference="authority-joint-governance",
    )
    incomplete = decision(
        value,
        deciding_classes=(AuthorityActorClass.OPERATIONAL_LEADERSHIP,),
    )
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(
            package(identity, value, decisions=(incomplete,))
        )
    assert error.value.code == "JOINT_CONTROL_INCOMPLETE"


def test_validity_period_is_bounded_by_provider_and_never_uses_current_time():
    value = grant(valid_until=NOW + timedelta(days=10))
    assert GuardianProviderAuthorizationValidator().validate(package(value=value))

    outside = replace(value, valid_until=NOW + timedelta(days=500))
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(package(value=outside))
    assert error.value.code == "VALIDITY_OUTSIDE_PROVIDER_IDENTITY"


def test_expired_status_requires_explicit_expiration_evidence():
    value = grant(status=ProviderAuthorizationStatus.EXPIRED)
    with pytest.raises(ProviderAuthorizationValidationError) as missing:
        GuardianProviderAuthorizationValidator().validate(package(value=value))
    assert missing.value.code == "LIFECYCLE_EVIDENCE_REQUIRED"

    expiration = lifecycle(
        AuthorizationExpirationEvidence,
        value,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.EXPIRED,
        "expiration",
    )
    result = GuardianProviderAuthorizationValidator().validate(
        package(value=value, expirations=(expiration,))
    )
    assert result.expirations[0] is expiration


def test_revocation_and_suspension_are_explicit_and_consistent():
    revoked = grant(status=ProviderAuthorizationStatus.REVOKED)
    revocation = lifecycle(
        AuthorizationRevocationEvidence,
        revoked,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.REVOKED,
        "revocation",
    )
    assert GuardianProviderAuthorizationValidator().validate(
        package(value=revoked, revocations=(revocation,))
    )

    suspended = grant(status=ProviderAuthorizationStatus.SUSPENDED)
    suspension = lifecycle(
        AuthorizationSuspensionEvidence,
        suspended,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.SUSPENDED,
        "suspension",
    )
    assert GuardianProviderAuthorizationValidator().validate(
        package(value=suspended, suspensions=(suspension,))
    )


def test_restoration_follows_suspension_without_extending_validity():
    value = grant(status=ProviderAuthorizationStatus.AUTHORIZED)
    suspension = lifecycle(
        AuthorizationSuspensionEvidence,
        value,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.SUSPENDED,
        "suspension",
    )
    restoration = replace(
        lifecycle(
            AuthorizationRestorationEvidence,
            value,
            ProviderAuthorizationStatus.SUSPENDED,
            ProviderAuthorizationStatus.AUTHORIZED,
            "restoration",
        ),
        effective_at=NOW + timedelta(days=2),
    )
    restored_decision = decision(value, AuthorizationDecisionType.RESTORE)
    assert GuardianProviderAuthorizationValidator().validate(
        package(
            value=value,
            decisions=(restored_decision,),
            suspensions=(suspension,),
            restorations=(restoration,),
        )
    )

    retroactive = replace(restoration, effective_at=suspension.effective_at)
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(
            package(
                value=value,
                decisions=(restored_decision,),
                suspensions=(suspension,),
                restorations=(retroactive,),
            )
        )
    assert error.value.code == "RETROACTIVE_RESTORATION"


def test_parallel_duplicate_authorizations_are_rejected():
    first = grant(identifier="authorization-first")
    second = grant(identifier="authorization-second")
    value = package(
        value=first,
        authorizations=(first, second),
        decisions=(decision(first), decision(second)),
    )
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(value)
    assert error.value.code == "PARALLEL_AUTHORIZATION_CONFLICT"


def test_unpermitted_delegation_rule_reference_is_rejected():
    value = replace(grant(), granting_authority_reference="unknown-rule")
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(package(value=value))
    assert error.value.code == "DELEGATION_RULE_MISMATCH"


def test_snapshot_preserves_mixed_explicit_statuses_and_original_objects():
    identity = provider()
    active = grant(identity, "authorization-active")
    suspended = grant(
        identity,
        "authorization-suspended",
        status=ProviderAuthorizationStatus.SUSPENDED,
        valid_from=NOW + timedelta(days=31),
        valid_until=NOW + timedelta(days=60),
    )
    revoked = grant(
        identity,
        "authorization-revoked",
        status=ProviderAuthorizationStatus.REVOKED,
        valid_from=NOW + timedelta(days=61),
        valid_until=NOW + timedelta(days=90),
    )
    expired = grant(
        identity,
        "authorization-expired",
        status=ProviderAuthorizationStatus.EXPIRED,
        valid_from=NOW + timedelta(days=91),
        valid_until=NOW + timedelta(days=120),
    )
    suspension = lifecycle(
        AuthorizationSuspensionEvidence,
        suspended,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.SUSPENDED,
        "suspension",
    )
    revocation = lifecycle(
        AuthorizationRevocationEvidence,
        revoked,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.REVOKED,
        "revocation",
    )
    expiration = lifecycle(
        AuthorizationExpirationEvidence,
        expired,
        ProviderAuthorizationStatus.AUTHORIZED,
        ProviderAuthorizationStatus.EXPIRED,
        "expiration",
    )
    boundary = next(
        item
        for item in authority_model().actor_boundaries
        if item.actor_class is AuthorityActorClass.DETERMINISTIC_CORE
    )
    snapshot = ProviderAuthorizationResolutionSnapshot(
        snapshot_id="snapshot-mixed",
        provider=identity,
        authorized=(active,),
        suspended=(suspended,),
        revoked=(revoked,),
        expired=(expired,),
        allowed_capabilities=active.allowed_capabilities,
        forbidden_capabilities=active.forbidden_capabilities,
        control_levels=active.control_levels,
        responsibility_boundaries=(boundary,),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-snapshot",
        uncertainties=(AuthorizationUncertaintyStatus.CERTAIN,),
        provenance=provenance(),
    )
    package_value = package(
        identity,
        active,
        authorizations=(active, suspended, revoked, expired),
        decisions=tuple(decision(item) for item in (active, suspended, revoked, expired)),
        suspensions=(suspension,),
        revocations=(revocation,),
        expirations=(expiration,),
        snapshots=(snapshot,),
    )
    result = GuardianProviderAuthorizationValidator().validate(package_value)
    assert result is package_value
    assert result.snapshots[0].provider is identity
    assert result.snapshots[0].authorized[0] is active


@pytest.mark.parametrize(
    "capability",
    tuple(
        item
        for item in ProviderAuthorizationPackageCapability
        if item is not ProviderAuthorizationPackageCapability.DESCRIBE_AUTHORIZATION
    ),
)
def test_package_rejects_every_executing_capability(capability):
    with pytest.raises(ProviderAuthorizationValidationError) as error:
        GuardianProviderAuthorizationValidator().validate(
            replace(package(), capabilities=(capability,))
        )
    assert error.value.code == "EXECUTING_CAPABILITY_FORBIDDEN"


def test_package_has_no_runtime_selection_activation_or_trust_methods():
    value = package()
    for name in (
        "execute",
        "activate",
        "select_provider",
        "evaluate_trust",
        "classify",
        "generate",
        "research",
        "persist",
    ):
        assert not hasattr(value, name)
