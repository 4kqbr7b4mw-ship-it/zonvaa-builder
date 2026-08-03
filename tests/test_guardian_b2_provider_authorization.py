from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

from artifact_contract import ArtifactAuthorization, AuthorizationScope, AuthorizationStatus
from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.b2_authorization import (
    REQUIRED_B2_AUTHORITY_BASIS,
    B2AAVBinding,
    B2AuthorizationDecision,
    B2AuthorizationEvaluator,
    B2AuthorizationProvenance,
    B2AuthorizationReason,
    B2Authority,
    B2AuthorityClass,
    B2AuthorityId,
    B2D3Consent,
    B2Grant,
    B2InstitutionalScope,
    B2NegativeGovernanceEvidence,
    B2PurposeScope,
    B2T4GrantReceipt,
    B2UODLBinding,
    B2UODLOperation,
)
from governance.b2_data_corridor import (
    ALLOWED_B2_DATA_CLASSES,
    ALLOWED_B2_DATA_FLOWS,
    ALLOWED_B2_DATA_SOURCES,
    D1_D6_REFERENCES,
    D3_REFERENCE,
    PROHIBITED_B2_DATA_CLASSES,
    PROHIBITED_B2_DATA_FLOWS,
    PROHIBITED_B2_DATA_SOURCES,
    PROHIBITED_RESIDUAL_IDENTIFIERS,
    REQUIRED_D3_BINDINGS,
    REQUIRED_PROHIBITED_USES,
    B2ConsentBoundary,
    B2ConsentUse,
    B2DataClass,
    B2DataClassification,
    B2DataCorridor,
    B2DataCorridorPackage,
    B2DataCorridorSnapshot,
    B2DataSensitivity,
    B2DepersonalizationBoundary,
    B2NegativeCorridorRules,
    B2ProhibitedCombination,
    B2ProhibitedDestination,
    B2ProhibitedPurposeChange,
)
from governance.b2_provider_authorization import (
    B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION,
    B2AuthorizationFoundation,
    B2AuthorizationFoundationValidator,
    B2ProviderAuthorization,
    B2ProviderAuthorizationEvaluationEvidence,
    B2ProviderAuthorizationEvaluator,
    B2ProviderAuthorizationId,
    B2ProviderAuthorizationNegativeGovernanceEvidence,
    B2ProviderAuthorizationProvenance,
    B2ProviderAuthorizationReason,
    B2ProviderAuthorizationValidator,
)
from governance.b2_provider_identity import (
    B2CapabilityDescriptor,
    B2GovernanceDecisionId,
    B2InstitutionalSourceId,
    B2NonPersonalReferenceId,
    B2ProviderClass,
    B2ProviderIdentity,
    B2ProviderIdentityId,
    B2ProviderProvenance,
    B2RegistrationBasisReference,
    B2ResponsibilityArea,
)
from governance.models import NormLevel
from governance.provider_authorization import ProviderIdentity
from guardian_runtime import RetentionClass
from user_owned_data import (
    ReferenceAuthorization,
    ReferenceRetention,
    StorageAvailability,
    StorageOperation,
    StorageProvider,
    StorageReference,
    StorageScope,
)


NOW = datetime(2026, 8, 3, 13, 30, tzinfo=timezone.utc)
PURPOSE = "Synthetic B2 authorization foundation"
AUTH_PROVENANCE = B2AuthorizationProvenance(
    source=REQUIRED_B2_AUTHORITY_BASIS[-1],
    decision_reference="decision:adr-0060",
)
CORRIDOR_PROVENANCE = AuthorityProvenance(
    norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
    source_reference="knowledge/adr/ADR-0059-guardian-b2-data-corridor-consent-boundary-v1.md",
    decision_reference="ADR-0059",
)
SCOPE = B2PurposeScope(
    purposes=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
    data_classes=(B2DataClass.DEPERSONALIZED_CONTEXT,),
)


def authority():
    return B2Authority(
        authority_id=B2AuthorityId("b2-authority:foundation-01"),
        authority_class=B2AuthorityClass.CONSTITUTIONAL_DATA_AUTHORITY,
        institutional_scope=B2InstitutionalScope.B2_CONSENT_BOUND_AUTHORIZATION,
        constitutional_basis=REQUIRED_B2_AUTHORITY_BASIS,
        provenance=AUTH_PROVENANCE,
    )


def d3(*, revoked_at=None):
    return B2D3Consent(
        consent_reference="d3:foundation-01",
        purpose_scope=SCOPE,
        effective_from=NOW - timedelta(hours=1),
        effective_until=NOW + timedelta(days=1),
        revoked_at=revoked_at,
    )


def grant(consent=None):
    return B2Grant(
        grant_id="b2-grant:foundation-01",
        authority=authority(),
        d3_consent=consent or d3(),
        t4_reference="t4:foundation-01",
        aav_reference="aav:foundation-01",
        uodl_reference="uodl:foundation-01",
        purpose_scope=SCOPE,
        provenance=AUTH_PROVENANCE,
    )


def provider_identity(identifier="b2-provider-identity:unit-01"):
    return B2ProviderIdentity(
        identity_id=B2ProviderIdentityId(identifier),
        provider_class=B2ProviderClass.INSTITUTIONAL_SERVICE_UNIT,
        responsibility_areas=(B2ResponsibilityArea.PERSONAL_PREPARATION_SUPPORT,),
        capability_descriptors=(
            B2CapabilityDescriptor.PERSONAL_PREPARATION_SERVICE_DESCRIPTOR,
        ),
        provenance=B2ProviderProvenance(
            institutional_source_id=B2InstitutionalSourceId(
                "institutional-source:unit-01"
            ),
            governance_decision_id=B2GovernanceDecisionId(
                "governance-decision:adr-0061"
            ),
            registration_basis=B2RegistrationBasisReference(
                "registration-basis:unit-01"
            ),
            reference_id=B2NonPersonalReferenceId(
                "non-personal-reference:identity-01"
            ),
            created_at=NOW,
        ),
    )


def corridor_package():
    artifact_authorization = ArtifactAuthorization(
        authorization_id="aav:foundation-01",
        subject_id="synthetic-subject-01",
        granted_by="synthetic-subject-01",
        scopes=(AuthorizationScope.READ,),
        purpose=PURPOSE,
        status=AuthorizationStatus.ACTIVE,
        granted_at=NOW - timedelta(hours=1),
        binding_references=("b2-corridor-1", "uodl:foundation-01"),
    )
    storage = StorageReference(
        reference_id="uodl:foundation-01",
        owner="synthetic-subject-01",
        storage_provider=StorageProvider.LOCAL_FOLDER,
        storage_scope=StorageScope.OWNER_PRIVATE,
        locator="vault-ref:foundation/input",
        checksum=None,
        version=1,
        created_at=NOW - timedelta(hours=1),
        last_verified=None,
        authorization=ReferenceAuthorization(
            reference_id="uodl:foundation-01",
            authorization=artifact_authorization,
            operations=(StorageOperation.REFERENCE,),
        ),
        capability=None,
        retention=ReferenceRetention(RetentionClass.KEEP_UNTIL_REVOKED),
        availability=StorageAvailability.UNKNOWN,
    )
    corridor = B2DataCorridor(
        corridor_id="b2-corridor-1",
        version=1,
        purpose=PURPOSE,
        allowed_data_classes=ALLOWED_B2_DATA_CLASSES,
        excluded_data_classes=PROHIBITED_B2_DATA_CLASSES,
        allowed_data_sources=ALLOWED_B2_DATA_SOURCES,
        excluded_data_sources=PROHIBITED_B2_DATA_SOURCES,
        allowed_flow_directions=ALLOWED_B2_DATA_FLOWS,
        excluded_flow_directions=PROHIBITED_B2_DATA_FLOWS,
        d1_d6_references=D1_D6_REFERENCES,
        d3_reference=D3_REFERENCE,
        aav_reference=artifact_authorization,
        uodl_reference=storage,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review-adr-0059",
        provenance=CORRIDOR_PROVENANCE,
    )
    consent = B2ConsentBoundary(
        consent_id="b2-consent-1",
        corridor_reference=corridor.corridor_id,
        purpose_binding=PURPOSE,
        allowed_scope=ALLOWED_B2_DATA_CLASSES,
        d3_binding=REQUIRED_D3_BINDINGS,
        revocation_reference="aav-revocation:foundation-01",
        allowed_use=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
        prohibited_use=REQUIRED_PROHIBITED_USES,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=CORRIDOR_PROVENANCE,
    )
    classifications = tuple(
        B2DataClassification(
            data_class=data_class,
            sensitivity=(
                B2DataSensitivity.NON_PERSONAL
                if data_class is B2DataClass.GENERAL_NON_PERSONAL_INFORMATION
                else B2DataSensitivity.PERSONAL
            ),
            personal=data_class is not B2DataClass.GENERAL_NON_PERSONAL_INFORMATION,
            depersonalizable=data_class in ALLOWED_B2_DATA_CLASSES,
            never_allowed=data_class in PROHIBITED_B2_DATA_CLASSES,
            allowed_b2_uses=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,)
            if data_class in ALLOWED_B2_DATA_CLASSES
            else (),
            provenance=CORRIDOR_PROVENANCE,
        )
        for data_class in B2DataClass
    )
    depersonalization = B2DepersonalizationBoundary(
        boundary_id="b2-depersonalization-1",
        d1_d6_references=D1_D6_REFERENCES,
        removed_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        allowed_residual_data=(B2DataClass.DEPERSONALIZED_CONTEXT,),
        prohibited_residual_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=CORRIDOR_PROVENANCE,
    )
    negative_rules = B2NegativeCorridorRules(
        prohibited_data_classes=PROHIBITED_B2_DATA_CLASSES,
        prohibited_data_sources=PROHIBITED_B2_DATA_SOURCES,
        prohibited_flow_directions=PROHIBITED_B2_DATA_FLOWS,
        prohibited_combinations=tuple(B2ProhibitedCombination),
        prohibited_residual_identifiers=PROHIBITED_RESIDUAL_IDENTIFIERS,
        prohibited_purpose_changes=tuple(B2ProhibitedPurposeChange),
        prohibited_destinations=tuple(B2ProhibitedDestination),
        provenance=CORRIDOR_PROVENANCE,
    )
    snapshot = B2DataCorridorSnapshot(
        snapshot_id="b2-corridor-snapshot-1",
        corridor=corridor,
        consent_boundary=consent,
        data_classifications=classifications,
        depersonalization_boundary=depersonalization,
        negative_rules=negative_rules,
        review_status=corridor.review_status,
        review_reference=corridor.review_reference,
        provenance=CORRIDOR_PROVENANCE,
    )
    return B2DataCorridorPackage(
        package_id="b2-data-corridor-package-1",
        corridor=corridor,
        consent_boundary=consent,
        data_classifications=classifications,
        depersonalization_boundary=depersonalization,
        negative_rules=negative_rules,
        snapshot=snapshot,
    )


def current_bindings(item=None, consent=None):
    item = item or grant(consent)
    consent = consent or d3()
    return dict(
        grant=item,
        authority=authority(),
        d3_consent=consent,
        t4_receipt=B2T4GrantReceipt(
            receipt_reference=item.t4_reference,
            grant_reference=item.grant_id,
            authority_reference=item.authority_reference,
            d3_reference=item.d3_reference,
            purpose_scope=item.purpose_scope,
        ),
        aav_binding=B2AAVBinding(
            aav_reference=item.aav_reference,
            grant_reference=item.grant_id,
            authority_reference=item.authority_reference,
            d3_reference=item.d3_reference,
            purpose_scope=item.purpose_scope,
            effective_from=NOW - timedelta(hours=1),
            effective_until=NOW + timedelta(days=1),
            revoked_at=None,
        ),
        uodl_binding=B2UODLBinding(
            uodl_reference=item.uodl_reference,
            grant_reference=item.grant_id,
            aav_reference=item.aav_reference,
            operation=B2UODLOperation.REFERENCE_ONLY,
            effective_from=NOW - timedelta(hours=1),
            effective_until=NOW + timedelta(days=1),
            revoked_at=None,
        ),
    )


def provider_authorization(identity=None, item=None, corridor=None):
    identity = identity or provider_identity()
    item = item or grant()
    corridor = corridor or corridor_package()
    provenance = B2ProviderAuthorizationProvenance(
        institutional_source_id=B2InstitutionalSourceId(
            "institutional-source:authorization-01"
        ),
        governance_decision_id=B2GovernanceDecisionId(
            "governance-decision:adr-0062"
        ),
        authorization_basis_reference=B2NonPersonalReferenceId(
            "non-personal-reference:authorization-01"
        ),
        evaluation_evidence_reference="b2-evidence:foundation-base-01",
        provider_identity_reference=identity.identity_id,
        grant_reference=item.grant_id,
        evaluated_at=NOW,
    )
    return B2ProviderAuthorization(
        authorization_id=B2ProviderAuthorizationId(
            "b2-provider-authorization:foundation-01"
        ),
        provider_identity=identity,
        grant=item,
        data_corridor=corridor,
        evaluation_evidence_reference="b2-evidence:foundation-base-01",
        evaluated_at=NOW,
        provenance=provenance,
    )


def evaluation_inputs(**changes):
    item = changes.pop("grant", grant())
    identity = changes.pop("provider_identity", provider_identity())
    corridor = changes.pop("data_corridor", corridor_package())
    authorization = changes.pop(
        "authorization", provider_authorization(identity, item, corridor)
    )
    values = dict(
        authorization=authorization,
        provider_identity=identity,
        data_corridor=corridor,
        evaluated_at=NOW,
        base_evidence_id="b2-evidence:foundation-base-01",
        provider_evidence_id="b2-provider-authorization-evidence:foundation-01",
        observed_negative_evidence=(),
        **current_bindings(item),
    )
    values.update(changes)
    return values


def evaluate(**changes):
    return B2ProviderAuthorizationEvaluator().evaluate(**evaluation_inputs(**changes))


def test_valid_provider_authorization_is_immutable_and_reference_only():
    item = provider_authorization()
    assert item.contract_version == B2_PROVIDER_AUTHORIZATION_CONTRACT_VERSION
    assert "provider_identity" not in {field.name for field in fields(item)}
    with pytest.raises(FrozenInstanceError):
        item.grant_reference = "b2-grant:changed"


def test_complete_positive_reference_chain_is_effective_and_deterministic():
    first = evaluate()
    second = evaluate()
    assert first == second
    assert isinstance(first, B2ProviderAuthorizationEvaluationEvidence)
    assert first.decision is B2AuthorizationDecision.EFFECTIVE


def test_validator_returns_the_same_authorization_identity():
    values = evaluation_inputs()
    result = B2ProviderAuthorizationValidator().validate(
        values["authorization"],
        values["provider_identity"],
        values["grant"],
        values["data_corridor"],
    )
    assert result is values["authorization"]


def test_full_foundation_preserves_every_object_identity():
    values = evaluation_inputs()
    evidence = B2ProviderAuthorizationEvaluator().evaluate(**values)
    foundation = B2AuthorizationFoundation(
        foundation_id="b2-foundation:reference-01",
        data_corridor=values["data_corridor"],
        authority=values["authority"],
        grant=values["grant"],
        provider_identity=values["provider_identity"],
        provider_authorization=values["authorization"],
        d3_consent=values["d3_consent"],
        t4_receipt=values["t4_receipt"],
        aav_binding=values["aav_binding"],
        uodl_binding=values["uodl_binding"],
        evaluated_at=NOW,
        evidence=evidence,
    )
    assert B2AuthorizationFoundationValidator().validate(foundation) is foundation
    assert foundation.data_corridor is values["data_corridor"]
    assert foundation.provider_identity is values["provider_identity"]


@pytest.mark.parametrize(
    "binding,reason",
    (
        ("d3_consent", B2AuthorizationReason.D3_INEFFECTIVE),
        ("t4_receipt", B2AuthorizationReason.T4_BINDING_MISMATCH),
        ("aav_binding", B2AuthorizationReason.AAV_BINDING_MISMATCH),
        ("uodl_binding", B2AuthorizationReason.UODL_BINDING_MISMATCH),
    ),
)
def test_each_current_binding_is_independently_required(binding, reason):
    values = evaluation_inputs()
    if binding == "d3_consent":
        values[binding] = d3(revoked_at=NOW)
    else:
        values[binding] = replace(values[binding], grant_reference="b2-grant:other")
    result = B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert isinstance(result, B2ProviderAuthorizationNegativeGovernanceEvidence)
    assert B2ProviderAuthorizationReason.BASE_AUTHORIZATION_DENIED in result.reasons
    assert reason in result.base_reasons


def test_d3_and_t4_never_replace_each_other():
    values = evaluation_inputs()
    values["t4_receipt"] = replace(
        values["t4_receipt"], receipt_reference="t4:other"
    )
    result = B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert result.decision is B2AuthorizationDecision.DENIED
    assert B2AuthorizationReason.T4_BINDING_MISMATCH in result.base_reasons


def test_previous_negative_governance_evidence_is_observation_only():
    negative_values = current_bindings(grant(), d3(revoked_at=NOW))
    negative = B2AuthorizationEvaluator().evaluate(
        **negative_values,
        evaluated_at=NOW,
        evidence_id="b2-evidence:previous-denial-01",
    )
    assert isinstance(negative, B2NegativeGovernanceEvidence)
    result = evaluate(observed_negative_evidence=(negative,))
    assert result.decision is B2AuthorizationDecision.EFFECTIVE
    assert result.observed_negative_evidence_references == (negative.evidence_id,)


def test_provider_identity_mismatch_is_negative_without_mutation():
    values = evaluation_inputs()
    original = values["authorization"]
    values["provider_identity"] = provider_identity("b2-provider-identity:unit-02")
    result = B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert B2ProviderAuthorizationReason.PROVIDER_IDENTITY_MISMATCH in result.reasons
    assert values["authorization"] is original


def test_corridor_grant_aav_and_uodl_references_must_match():
    values = evaluation_inputs()
    other_grant = B2Grant(
        grant_id="b2-grant:other-01",
        authority=authority(),
        d3_consent=d3(),
        t4_reference="t4:other-01",
        aav_reference="aav:other-01",
        uodl_reference="uodl:other-01",
        purpose_scope=SCOPE,
        provenance=AUTH_PROVENANCE,
    )
    values["grant"] = other_grant
    values.update(current_bindings(other_grant))
    result = B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert B2ProviderAuthorizationReason.GRANT_BINDING_MISMATCH in result.reasons
    assert B2ProviderAuthorizationReason.CORRIDOR_BINDING_MISMATCH in result.reasons


def test_invalid_corridor_is_negative_and_not_repaired():
    values = evaluation_inputs()
    package = values["data_corridor"]
    invalid_corridor = replace(
        package.corridor,
        allowed_data_classes=package.corridor.allowed_data_classes[:-1],
    )
    values["data_corridor"] = replace(package, corridor=invalid_corridor)
    result = B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert B2ProviderAuthorizationReason.CORRIDOR_BINDING_MISMATCH in result.reasons


@pytest.mark.parametrize("data_class", PROHIBITED_B2_DATA_CLASSES)
def test_every_prohibited_corridor_data_class_is_rejected(data_class):
    with pytest.raises(Exception):
        B2PurposeScope(
            purposes=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
            data_classes=(data_class,),
        )


def test_only_the_ratified_uodl_hook_is_modelable():
    assert tuple(B2UODLOperation) == (B2UODLOperation.REFERENCE_ONLY,)
    values = current_bindings()["uodl_binding"].__dict__
    with pytest.raises(TypeError, match="B2UODLOperation"):
        B2UODLBinding(**dict(values, operation="READ"))


@pytest.mark.parametrize(
    "field",
    ("valid", "active", "revoked", "expired", "authorized", "denied", "blocked"),
)
def test_provider_authorization_cannot_model_status_fields(field):
    assert field not in {item.name for item in fields(B2ProviderAuthorization)}
    values = dict(
        authorization_id=B2ProviderAuthorizationId(
            "b2-provider-authorization:foundation-01"
        ),
        provider_identity=provider_identity(),
        grant=grant(),
        data_corridor=corridor_package(),
        evaluation_evidence_reference="b2-evidence:foundation-base-01",
        evaluated_at=NOW,
        provenance=provider_authorization().provenance,
        **{field: True},
    )
    with pytest.raises(TypeError):
        B2ProviderAuthorization(**values)


@pytest.mark.parametrize(
    "field",
    (
        "natural_person",
        "personal_identity",
        "personal_content",
        "invocation",
        "runtime",
        "tool",
        "session",
        "cache",
        "token",
        "key_material",
        "content_access",
    ),
)
def test_provider_authorization_cannot_model_personal_or_executable_fields(field):
    assert field not in {item.name for item in fields(B2ProviderAuthorization)}
    with pytest.raises(TypeError):
        B2ProviderAuthorization(**dict(provider_authorization().__dict__, **{field: "x"}))


def test_natural_person_provider_identity_is_structurally_rejected():
    with pytest.raises(ValueError, match="natural person"):
        provider_identity("b2-provider-identity:person-01")


def test_b1_provider_identity_is_not_a_b2_provider_identity():
    assert not issubclass(B2ProviderIdentity, ProviderIdentity)
    values = evaluation_inputs()
    values["provider_identity"] = ProviderIdentity  # type: ignore[assignment]
    with pytest.raises(TypeError, match="B2ProviderIdentity"):
        B2ProviderAuthorizationEvaluator().evaluate(**values)


def test_evaluation_requires_explicit_timezone_aware_time():
    values = evaluation_inputs()
    values.pop("evaluated_at")
    with pytest.raises(TypeError):
        B2ProviderAuthorizationEvaluator().evaluate(**values)
    values["evaluated_at"] = datetime(2026, 8, 3, 13, 30)
    with pytest.raises(ValueError, match="timezone-aware"):
        B2ProviderAuthorizationEvaluator().evaluate(**values)


def test_no_hidden_time_repository_service_or_state_source_exists():
    source = inspect.getsource(B2ProviderAuthorizationEvaluator)
    for forbidden in (
        "now(",
        "utcnow(",
        "repository",
        "service_lookup",
        "global_state",
        "session",
        "cache",
    ):
        assert forbidden not in source.lower()


def test_evidence_has_no_permission_token_or_execution_effect():
    result = evaluate()
    names = {item.name for item in fields(result)}
    assert not {
        "permission",
        "token",
        "grant",
        "active",
        "runtime",
        "invocation",
        "execute",
    } & names
    for method in ("authorize", "invoke", "execute", "run"):
        assert not hasattr(result, method)


def test_negative_evidence_has_no_block_sanction_or_profile_effect():
    result = evaluate(d3_consent=d3(revoked_at=NOW))
    assert isinstance(result, B2ProviderAuthorizationNegativeGovernanceEvidence)
    names = {item.name for item in fields(result)}
    assert not {"blocked", "sanction", "risk_score", "profile", "deny_future"} & names


def test_evaluation_does_not_mutate_any_input():
    values = evaluation_inputs()
    before = dict(values)
    B2ProviderAuthorizationEvaluator().evaluate(**values)
    assert values == before
    for item in before.values():
        if hasattr(item, "__dataclass_fields__"):
            with pytest.raises(FrozenInstanceError):
                setattr(item, next(iter(item.__dataclass_fields__)), "changed")


def test_foundation_has_no_runtime_invocation_or_execution_surface():
    names = {item.name for item in fields(B2AuthorizationFoundation)}
    assert not {"runtime", "invocation", "tool", "session", "cache", "token"} & names
    for method in ("authorize", "invoke", "execute", "run"):
        assert not hasattr(B2AuthorizationFoundation, method)
