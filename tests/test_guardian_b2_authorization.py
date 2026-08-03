from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

from governance.authority import AuthorityDefinition
from governance.b2_authorization import (
    B2_AUTHORIZATION_CONTRACT_VERSION,
    REQUIRED_B2_AUTHORITY_BASIS,
    B2AAVBinding,
    B2AuthorizationDecision,
    B2AuthorizationEvaluationEvidence,
    B2AuthorizationEvaluator,
    B2AuthorizationProvenance,
    B2AuthorizationReason,
    B2AuthorizationStructureError,
    B2Authority,
    B2AuthorityClass,
    B2AuthorityId,
    B2ConstitutionalBasis,
    B2D3Consent,
    B2Grant,
    B2InstitutionalScope,
    B2NegativeGovernanceEvidence,
    B2PurposeScope,
    B2T4GrantReceipt,
    B2UODLBinding,
    B2UODLOperation,
)
from governance.b2_data_corridor import B2ConsentUse, B2DataClass


NOW = datetime(2026, 8, 2, 20, 0, tzinfo=timezone.utc)
LATER = NOW + timedelta(hours=1)
FULL_SCOPE = B2PurposeScope(
    purposes=(
        B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,
        B2ConsentUse.BIND_PROVIDED_CONTEXT,
    ),
    data_classes=(
        B2DataClass.CONFIRMED_PERSONAL_FACT,
        B2DataClass.DEPERSONALIZED_CONTEXT,
    ),
)
NARROW_SCOPE = B2PurposeScope(
    purposes=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
    data_classes=(B2DataClass.DEPERSONALIZED_CONTEXT,),
)
INCOMPARABLE_SCOPE = B2PurposeScope(
    purposes=(B2ConsentUse.BIND_PROVIDED_CONTEXT,),
    data_classes=(B2DataClass.DEPERSONALIZED_CONTEXT,),
)
PROVENANCE = B2AuthorizationProvenance(
    source=B2ConstitutionalBasis.ADR_0060,
    decision_reference="decision:adr-0060",
)


def authority():
    return B2Authority(
        authority_id=B2AuthorityId("b2-authority:constitutional-1"),
        authority_class=B2AuthorityClass.CONSTITUTIONAL_DATA_AUTHORITY,
        institutional_scope=B2InstitutionalScope.B2_CONSENT_BOUND_AUTHORIZATION,
        constitutional_basis=REQUIRED_B2_AUTHORITY_BASIS,
        provenance=PROVENANCE,
    )


def d3(scope=FULL_SCOPE, revoked_at=None):
    return B2D3Consent(
        consent_reference="d3:consent-1",
        purpose_scope=scope,
        effective_from=NOW - timedelta(hours=1),
        effective_until=NOW + timedelta(days=1),
        revoked_at=revoked_at,
    )


def grant(scope=NARROW_SCOPE, consent=None):
    return B2Grant(
        grant_id="b2-grant:grant-1",
        authority=authority(),
        d3_consent=consent or d3(),
        t4_reference="t4:receipt-1",
        aav_reference="aav:binding-1",
        uodl_reference="uodl:binding-1",
        purpose_scope=scope,
        provenance=PROVENANCE,
    )


def inputs(consent=None, **changes):
    item = grant(consent=consent)
    consent = consent or d3()
    values = dict(
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
        evaluated_at=NOW,
        evidence_id="b2-evidence:evaluation-1",
    )
    values.update(changes)
    return values


def evaluate(values=None):
    return B2AuthorizationEvaluator().evaluate(**(values or inputs()))


def test_b2_authority_is_immutable_and_structurally_separate_from_b1():
    item = authority()
    assert not isinstance(item, AuthorityDefinition)
    with pytest.raises(FrozenInstanceError):
        item.authority_class = B2AuthorityClass.INSTITUTIONAL_CONSENT_AUTHORITY


@pytest.mark.parametrize(
    "field",
    ("natural_person", "provider_reference", "runtime_reference", "personal_content"),
)
def test_b2_authority_cannot_model_operational_or_personal_fields(field):
    assert field not in {item.name for item in fields(B2Authority)}
    values = dict(
        authority_id=B2AuthorityId("b2-authority:constitutional-1"),
        authority_class=B2AuthorityClass.CONSTITUTIONAL_DATA_AUTHORITY,
        institutional_scope=B2InstitutionalScope.B2_CONSENT_BOUND_AUTHORIZATION,
        constitutional_basis=REQUIRED_B2_AUTHORITY_BASIS,
        provenance=PROVENANCE,
    )
    values[field] = "forbidden"
    with pytest.raises(TypeError):
        B2Authority(**values)


def test_grant_requires_d3():
    values = _grant_arguments()
    values["d3_consent"] = None
    with pytest.raises(TypeError):
        B2Grant(**values)


def test_grant_requires_t4():
    values = _grant_arguments()
    values.pop("t4_reference")
    with pytest.raises(TypeError):
        B2Grant(**values)


def test_grant_requires_aav():
    values = _grant_arguments()
    values.pop("aav_reference")
    with pytest.raises(TypeError):
        B2Grant(**values)


def test_grant_requires_uodl():
    values = _grant_arguments()
    values.pop("uodl_reference")
    with pytest.raises(TypeError):
        B2Grant(**values)


def test_grant_requires_b2_authority():
    values = _grant_arguments()
    values["authority"] = object()
    with pytest.raises(TypeError, match="B2Authority"):
        B2Grant(**values)


def test_grant_scope_expansion_is_structurally_rejected():
    with pytest.raises(B2AuthorizationStructureError) as error:
        grant(scope=FULL_SCOPE, consent=d3(NARROW_SCOPE))
    assert error.value.code == "GRANT_SCOPE_EXPANSION"


def test_equal_and_narrower_grant_scopes_are_allowed():
    assert grant(scope=FULL_SCOPE).purpose_scope is FULL_SCOPE
    assert grant(scope=NARROW_SCOPE).purpose_scope is NARROW_SCOPE


def test_inconsistent_current_scope_causes_negative_evaluation():
    values = inputs()
    values["d3_consent"] = d3(INCOMPARABLE_SCOPE)
    result = evaluate(values)
    assert result.decision is B2AuthorizationDecision.DENIED
    assert B2AuthorizationReason.PURPOSE_SCOPE_INCONSISTENT in result.reasons


@pytest.mark.parametrize(
    "field",
    ("valid", "active", "revoked", "expired", "authorized", "evaluation_result"),
)
def test_grant_cannot_model_stored_effectiveness_fields(field):
    assert field not in {item.name for item in fields(B2Grant)}
    values = _grant_arguments()
    values[field] = True
    with pytest.raises(TypeError):
        B2Grant(**values)


def test_grant_cannot_model_provider_reference():
    assert "provider_reference" not in {item.name for item in fields(B2Grant)}
    with pytest.raises(TypeError):
        B2Grant(**dict(_grant_arguments(), provider_reference="provider:1"))


def test_grant_cannot_model_runtime_reference():
    assert "runtime_reference" not in {item.name for item in fields(B2Grant)}
    with pytest.raises(TypeError):
        B2Grant(**dict(_grant_arguments(), runtime_reference="runtime:1"))


def test_grant_cannot_model_personal_content():
    assert "personal_content" not in {item.name for item in fields(B2Grant)}
    with pytest.raises(TypeError):
        B2Grant(**dict(_grant_arguments(), personal_content="forbidden"))
    with pytest.raises(ValueError, match="non-personal machine reference"):
        B2AuthorityId("b2-authority:person@example.invalid")


def test_purpose_scope_cannot_model_a_prohibited_personal_data_class():
    with pytest.raises(B2AuthorizationStructureError) as error:
        B2PurposeScope(
            purposes=(B2ConsentUse.STRUCTURE_PERSONAL_PREPARATION,),
            data_classes=(B2DataClass.RAW_CONVERSATION,),
        )
    assert error.value.code == "PURPOSE_SCOPE_DATA_CLASS_PROHIBITED"


def test_no_b1_to_b2_upgrade_or_conversion_exists():
    module_source = inspect.getsource(__import__("governance.b2_authorization", fromlist=["*"]))
    assert "upgrade" not in module_source.lower()
    assert "convert" not in module_source.lower()
    with pytest.raises(TypeError, match="B2Authority"):
        B2Grant(**dict(_grant_arguments(), authority=object()))


def test_positive_evaluation_requires_every_current_binding():
    result = evaluate()
    assert isinstance(result, B2AuthorizationEvaluationEvidence)
    assert result.decision is B2AuthorizationDecision.EFFECTIVE
    assert result.contract_version == B2_AUTHORIZATION_CONTRACT_VERSION


def test_d3_alone_is_never_sufficient():
    values = inputs()
    values["t4_receipt"] = replace(values["t4_receipt"], grant_reference="b2-grant:other")
    assert evaluate(values).decision is B2AuthorizationDecision.DENIED


def test_revoked_d3_denies_without_mutating_grant():
    original = grant()
    values = inputs(consent=d3(revoked_at=NOW))
    result = evaluate(values)
    assert B2AuthorizationReason.D3_INEFFECTIVE in result.reasons
    assert original == grant()


@pytest.mark.parametrize(
    "binding,reason",
    (
        ("t4_receipt", B2AuthorizationReason.T4_BINDING_MISMATCH),
        ("aav_binding", B2AuthorizationReason.AAV_BINDING_MISMATCH),
        ("uodl_binding", B2AuthorizationReason.UODL_BINDING_MISMATCH),
    ),
)
def test_inconsistent_t4_aav_or_uodl_binding_is_denied(binding, reason):
    values = inputs()
    item = values[binding]
    values[binding] = replace(item, grant_reference="b2-grant:other")
    assert reason in evaluate(values).reasons


def test_evaluation_requires_explicit_timezone_aware_time():
    values = inputs()
    values.pop("evaluated_at")
    with pytest.raises(TypeError):
        B2AuthorizationEvaluator().evaluate(**values)
    values["evaluated_at"] = datetime(2026, 8, 2, 20, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        evaluate(values)


def test_evaluation_has_no_hidden_time_source_and_is_deterministic():
    source = inspect.getsource(B2AuthorizationEvaluator)
    assert "now(" not in source
    assert "utcnow(" not in source
    values = inputs()
    assert evaluate(values) == evaluate(values)


def test_evaluation_evidence_cannot_be_a_token_or_authorize_later():
    result = evaluate()
    field_names = {item.name for item in fields(result)}
    assert not {"token", "capability", "active", "valid_until"} & field_names
    with pytest.raises(TypeError):
        B2AuthorizationEvaluationEvidence(**dict(result.__dict__, token="forbidden"))


def test_evaluation_evidence_cannot_be_an_evaluation_input():
    values = inputs()
    values["grant"] = evaluate(values)
    with pytest.raises(TypeError, match="grant"):
        evaluate(values)


def test_negative_governance_evidence_has_no_blocking_effect():
    values = inputs()
    values["d3_consent"] = d3(revoked_at=NOW)
    result = evaluate(values)
    assert isinstance(result, B2NegativeGovernanceEvidence)
    field_names = {item.name for item in fields(result)}
    assert not {"blocked", "sanction", "deny_future", "risk_score"} & field_names
    with pytest.raises(TypeError):
        B2NegativeGovernanceEvidence(**dict(result.__dict__, blocked=True))


def test_negative_governance_evidence_cannot_contain_personal_content():
    values = inputs()
    values["d3_consent"] = d3(revoked_at=NOW)
    result = evaluate(values)
    assert "personal_content" not in {item.name for item in fields(result)}
    with pytest.raises(TypeError):
        B2NegativeGovernanceEvidence(**dict(result.__dict__, personal_content="forbidden"))


def test_evaluation_and_all_inputs_remain_immutable_and_unmodified():
    values = inputs()
    before = dict(values)
    result = evaluate(values)
    assert values == before
    for item in tuple(values.values()) + (result,):
        if hasattr(item, "__dataclass_fields__"):
            with pytest.raises(FrozenInstanceError):
                setattr(item, next(iter(item.__dataclass_fields__)), "changed")


def _grant_arguments():
    return dict(
        grant_id="b2-grant:grant-1",
        authority=authority(),
        d3_consent=d3(),
        t4_reference="t4:receipt-1",
        aav_reference="aav:binding-1",
        uodl_reference="uodl:binding-1",
        purpose_scope=NARROW_SCOPE,
        provenance=PROVENANCE,
    )
