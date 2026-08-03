from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
import inspect

import pytest

from governance.b2_authorization import B2PurposeScope, B2UODLOperation
from governance.b2_provider_authorization import (
    B2AuthorizationFoundation,
    B2ProviderAuthorizationEvaluator,
)
from governance.b2_provider_identity import (
    B2GovernanceDecisionId,
    B2InstitutionalSourceId,
    B2NonPersonalReferenceId,
)
from governance.b2_purpose_uodl_binding import (
    B2BindingEvaluationOutcome,
    B2BindingObservationScope,
    B2BindingProvenance,
    B2CorridorPurposeReference,
    B2PurposeBinding,
    B2PurposeBindingId,
    B2PurposeBindingRule,
    B2PurposeBindingValidator,
    B2PurposeComparisonRelation,
    B2PurposeUODLBindingFoundation,
    B2PurposeUODLBindingFoundationValidator,
    B2PurposeUODLBindingValidationError,
    B2UODLLayerRelation,
    B2UODLMapping,
    B2UODLMappingId,
    B2UODLMappingValidator,
    B2UODLPairRule,
)
from user_owned_data import StorageOperation

from test_guardian_b2_provider_authorization import (
    NOW,
    SCOPE,
    corridor_package,
    evaluation_inputs,
)


def provenance(at=NOW):
    return B2BindingProvenance(
        institutional_source_id=B2InstitutionalSourceId(
            "institutional-source:adr-0063"
        ),
        governance_decision_id=B2GovernanceDecisionId(
            "governance-decision:adr-0063"
        ),
        reference_id=B2NonPersonalReferenceId(
            "non-personal-reference:binding-provenance-01"
        ),
        created_at=at,
    )


def purpose_binding(scope=SCOPE, relation=B2PurposeComparisonRelation.NARROWER):
    return B2PurposeBinding(
        binding_id=B2PurposeBindingId("b2-purpose-binding:foundation-01"),
        corridor_reference="b2-corridor-1",
        source_purpose_reference=B2CorridorPurposeReference(
            "b2-corridor-purpose:b2-corridor-1"
        ),
        canonical_scope=scope,
        binding_rule=B2PurposeBindingRule.IDENTICAL_OR_NARROWER,
        comparison_relation=relation,
        evidence_references=(
            B2NonPersonalReferenceId("non-personal-reference:purpose-evidence-01"),
        ),
        provenance=provenance(),
        created_at=NOW,
        observation_scope=B2BindingObservationScope.PURPOSE_BINDING_INPUTS,
    )


def uodl_mapping():
    return B2UODLMapping(
        mapping_id=B2UODLMappingId("b2-uodl-mapping:foundation-01"),
        corridor_operation=StorageOperation.REFERENCE,
        b2_uodl_operation=B2UODLOperation.REFERENCE_ONLY,
        layer_relation=B2UODLLayerRelation.CORRIDOR_TO_AUTHORIZATION_REFERENCE,
        pair_rule=B2UODLPairRule.REFERENCE_TO_REFERENCE_ONLY,
        evidence_references=(
            B2NonPersonalReferenceId("non-personal-reference:uodl-evidence-01"),
        ),
        provenance=provenance(),
        created_at=NOW,
        observation_scope=B2BindingObservationScope.UODL_MAPPING_INPUTS,
    )


def full_package():
    values = evaluation_inputs()
    provider_evidence = B2ProviderAuthorizationEvaluator().evaluate(**values)
    foundation = B2AuthorizationFoundation(
        foundation_id="b2-foundation:adr-0063-01",
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
        evidence=provider_evidence,
    )
    binding = purpose_binding()
    mapping = uodl_mapping()
    return B2PurposeUODLBindingFoundation(
        foundation=foundation,
        purpose_binding=binding,
        purpose_evidence=B2PurposeBindingValidator().validate(
            binding,
            values["data_corridor"],
            B2NonPersonalReferenceId("non-personal-reference:purpose-receipt-01"),
        ),
        uodl_mapping=mapping,
        uodl_evidence=B2UODLMappingValidator().validate(
            mapping,
            B2NonPersonalReferenceId("non-personal-reference:uodl-receipt-01"),
        ),
    )


def test_identical_and_narrower_scope_bindings_are_accepted():
    corridor = corridor_package()
    identical_scope = B2PurposeScope(
        purposes=corridor.consent_boundary.allowed_use,
        data_classes=corridor.consent_boundary.allowed_scope,
    )
    identical = purpose_binding(
        identical_scope, B2PurposeComparisonRelation.IDENTICAL
    )
    narrower = purpose_binding()
    assert B2PurposeBindingValidator().validate(
        identical, corridor, B2NonPersonalReferenceId("non-personal-reference:receipt-identical")
    ).comparison_relation is B2PurposeComparisonRelation.IDENTICAL
    assert B2PurposeBindingValidator().validate(
        narrower, corridor, B2NonPersonalReferenceId("non-personal-reference:receipt-narrower")
    ).comparison_relation is B2PurposeComparisonRelation.NARROWER


def test_purpose_validation_is_deterministic_and_preserves_inputs():
    corridor = corridor_package()
    binding = purpose_binding()
    evidence_id = B2NonPersonalReferenceId("non-personal-reference:purpose-receipt-01")
    first = B2PurposeBindingValidator().validate(binding, corridor, evidence_id)
    second = B2PurposeBindingValidator().validate(binding, corridor, evidence_id)
    assert first == second
    assert first.binding_reference is binding.binding_id
    assert first.canonical_scope is binding.canonical_scope
    assert first.outcome is B2BindingEvaluationOutcome.CONFORMING


def test_broader_and_non_comparable_scopes_fail_closed():
    corridor = corridor_package()
    broader = B2PurposeScope(
        purposes=tuple(type(SCOPE.purposes[0])),
        data_classes=SCOPE.data_classes,
    )
    with pytest.raises(B2PurposeUODLBindingValidationError) as error:
        B2PurposeBindingValidator().validate(
            purpose_binding(broader, B2PurposeComparisonRelation.NARROWER), corridor
            , B2NonPersonalReferenceId("non-personal-reference:purpose-receipt-01")
        )
    assert error.value.code == "PURPOSE_SCOPE_EXPANSION"


@pytest.mark.parametrize(
    "change,code",
    (
        ({"corridor_reference": "b2-corridor-other"}, "CORRIDOR_REFERENCE_MISMATCH"),
        (
            {
                "source_purpose_reference": B2CorridorPurposeReference(
                    "b2-corridor-purpose:b2-corridor-other"
                )
            },
            "PURPOSE_REFERENCE_MISMATCH",
        ),
        (
            {"comparison_relation": B2PurposeComparisonRelation.IDENTICAL},
            "PURPOSE_RELATION_MISMATCH",
        ),
    ),
)
def test_inconsistent_purpose_bindings_fail_closed(change, code):
    with pytest.raises(B2PurposeUODLBindingValidationError) as error:
        B2PurposeBindingValidator().validate(
            replace(purpose_binding(), **change), corridor_package(),
            B2NonPersonalReferenceId("non-personal-reference:purpose-receipt-01")
        )
    assert error.value.code == code


def test_purpose_contract_rejects_missing_evidence_naive_time_and_personal_reference():
    with pytest.raises(ValueError):
        replace(purpose_binding(), evidence_references=())
    with pytest.raises(ValueError):
        replace(
            purpose_binding(),
            created_at=datetime(2026, 8, 3, 12, 0),
            provenance=provenance(datetime(2026, 8, 3, 12, 0)),
        )
    with pytest.raises(ValueError):
        B2PurposeBindingId("b2-purpose-binding:person-account")


def test_purpose_contract_has_no_permissive_relations_or_forbidden_power_fields():
    assert tuple(B2PurposeComparisonRelation) == (
        B2PurposeComparisonRelation.IDENTICAL,
        B2PurposeComparisonRelation.NARROWER,
    )
    names = {field.name for field in fields(B2PurposeBinding)}
    assert not names.intersection(
        {"purpose", "valid", "active", "approved", "authorized", "runtime", "token", "session", "cache"}
    )
    source = inspect.getsource(B2PurposeBindingValidator)
    assert "datetime.now" not in source
    assert "repository" not in source.lower()


def test_unknown_or_permissive_purpose_relations_are_not_constructible():
    for value in ("BROADER", "COMPATIBLE", "SIMILAR", "INFERRED", "UNKNOWN"):
        with pytest.raises(ValueError):
            B2PurposeComparisonRelation(value)
    with pytest.raises(TypeError):
        replace(purpose_binding(), comparison_relation="NARROWER")


def test_uodl_mapping_accepts_only_the_typed_ratified_pair_and_is_deterministic():
    mapping = uodl_mapping()
    evidence_id = B2NonPersonalReferenceId("non-personal-reference:uodl-receipt-01")
    first = B2UODLMappingValidator().validate(mapping, evidence_id)
    second = B2UODLMappingValidator().validate(mapping, evidence_id)
    assert first == second
    assert first.corridor_operation is StorageOperation.REFERENCE
    assert first.b2_uodl_operation is B2UODLOperation.REFERENCE_ONLY


@pytest.mark.parametrize(
    "field,value",
    (
        ("corridor_operation", StorageOperation.READ),
        ("corridor_operation", "REFERENCE"),
        ("b2_uodl_operation", "REFERENCE_ONLY"),
    ),
)
def test_uodl_mapping_rejects_other_operations_and_strings(field, value):
    with pytest.raises((TypeError, B2PurposeUODLBindingValidationError)):
        replace(uodl_mapping(), **{field: value})


def test_uodl_mapping_has_no_execution_or_content_fields():
    names = {field.name for field in fields(B2UODLMapping)}
    assert not names.intersection(
        {
            "read", "write", "copy", "content", "provider", "invoke", "runtime",
            "tool", "callback", "session", "cache", "token", "permission", "key",
            "secret", "handle",
        }
    )
    for method in ("authorize", "invoke", "execute", "migrate", "convert"):
        assert not hasattr(B2UODLMapping, method)


def test_uodl_contract_has_exactly_one_pair_rule_and_no_extra_hook_model():
    assert tuple(B2UODLPairRule) == (
        B2UODLPairRule.REFERENCE_TO_REFERENCE_ONLY,
    )
    assert tuple(B2UODLLayerRelation) == (
        B2UODLLayerRelation.CORRIDOR_TO_AUTHORIZATION_REFERENCE,
    )
    assert "hooks" not in {field.name for field in fields(B2UODLMapping)}


@pytest.mark.parametrize("field", ("purpose_binding", "uodl_mapping"))
def test_complete_foundation_fails_closed_when_a_binding_is_missing(field):
    package = full_package()
    with pytest.raises(TypeError):
        replace(package, **{field: None})


def test_complete_adr_0059_through_0063_chain_is_valid_without_execution():
    package = full_package()
    assert B2PurposeUODLBindingFoundationValidator().validate(package) is package
    assert package.foundation.data_corridor is package.foundation.data_corridor
    assert package.purpose_binding.canonical_scope is package.foundation.grant.purpose_scope


def test_foundation_rejects_evidence_and_binding_mismatches():
    package = full_package()
    with pytest.raises(B2PurposeUODLBindingValidationError):
        B2PurposeUODLBindingFoundationValidator().validate(
            replace(
                package,
                purpose_evidence=replace(
                    package.purpose_evidence,
                    input_evidence_references=(
                        B2NonPersonalReferenceId(
                            "non-personal-reference:other-evidence"
                        ),
                    ),
                ),
            )
        )


def test_contracts_are_immutable_and_expose_no_clock_or_state_source():
    binding = purpose_binding()
    with pytest.raises(FrozenInstanceError):
        binding.corridor_reference = "b2-corridor-other"
    for validator in (B2PurposeBindingValidator, B2UODLMappingValidator):
        signature = inspect.signature(validator().validate)
        assert "now" not in signature.parameters
        source = inspect.getsource(validator)
        assert "datetime.now" not in source
        assert "time.time" not in source
