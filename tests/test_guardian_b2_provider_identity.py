from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
import inspect

import pytest

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
from governance.provider_authorization import ProviderIdentity


CREATED_AT = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)


def provenance():
    return B2ProviderProvenance(
        institutional_source_id=B2InstitutionalSourceId(
            "institutional-source:unit-01"
        ),
        governance_decision_id=B2GovernanceDecisionId(
            "governance-decision:adr-0061"
        ),
        registration_basis=B2RegistrationBasisReference(
            "registration-basis:contract-01"
        ),
        reference_id=B2NonPersonalReferenceId(
            "non-personal-reference:evidence-01"
        ),
        created_at=CREATED_AT,
    )


def arguments():
    return dict(
        identity_id=B2ProviderIdentityId("b2-provider-identity:unit-01"),
        provider_class=B2ProviderClass.INSTITUTIONAL_SERVICE_UNIT,
        responsibility_areas=(
            B2ResponsibilityArea.GENERAL_ORIENTATION_SUPPORT,
        ),
        capability_descriptors=(
            B2CapabilityDescriptor.GENERAL_ORIENTATION_SERVICE_DESCRIPTOR,
        ),
        provenance=provenance(),
    )


def test_valid_b2_provider_identity_is_immutable_and_non_executing():
    item = B2ProviderIdentity(**arguments())
    assert item.identity_id.value == "b2-provider-identity:unit-01"
    assert item.provenance.created_at is CREATED_AT
    with pytest.raises(FrozenInstanceError):
        item.provider_class = B2ProviderClass.RESEARCH_SERVICE_UNIT


def test_provider_classes_are_exactly_the_ratified_closed_set():
    assert tuple(B2ProviderClass) == (
        B2ProviderClass.INSTITUTIONAL_SERVICE_UNIT,
        B2ProviderClass.PROFESSIONAL_ROLE_UNIT,
        B2ProviderClass.MODEL_SERVICE_UNIT,
        B2ProviderClass.RESEARCH_SERVICE_UNIT,
        B2ProviderClass.TECHNICAL_TOOL_SERVICE_UNIT,
    )


def test_professional_role_unit_has_no_natural_person_binding():
    item = B2ProviderIdentity(
        **dict(arguments(), provider_class=B2ProviderClass.PROFESSIONAL_ROLE_UNIT)
    )
    assert item.provider_class is B2ProviderClass.PROFESSIONAL_ROLE_UNIT
    assert "natural_person" not in {field.name for field in fields(item)}


def test_model_service_unit_has_no_ml_model_or_runtime_semantics():
    item = B2ProviderClass.MODEL_SERVICE_UNIT
    for name in ("model", "predict", "train", "run", "execute", "runtime"):
        assert not hasattr(item, name)


def test_technical_tool_service_unit_has_no_invocation_or_runtime_semantics():
    item = B2ProviderClass.TECHNICAL_TOOL_SERVICE_UNIT
    for name in ("invoke", "call", "run", "execute", "activate", "runtime"):
        assert not hasattr(item, name)


def test_responsibility_areas_are_exactly_the_ratified_closed_set():
    assert tuple(B2ResponsibilityArea) == (
        B2ResponsibilityArea.GENERAL_ORIENTATION_SUPPORT,
        B2ResponsibilityArea.PERSONAL_PREPARATION_SUPPORT,
        B2ResponsibilityArea.PROFESSIONAL_REVIEW_PREPARATION_SUPPORT,
        B2ResponsibilityArea.SOURCE_REFERENCE_SUPPORT,
    )


def test_capabilities_are_exactly_the_ratified_closed_descriptors():
    assert tuple(B2CapabilityDescriptor) == (
        B2CapabilityDescriptor.GENERAL_ORIENTATION_SERVICE_DESCRIPTOR,
        B2CapabilityDescriptor.PERSONAL_PREPARATION_SERVICE_DESCRIPTOR,
        B2CapabilityDescriptor.PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR,
        B2CapabilityDescriptor.SOURCE_REFERENCE_SERVICE_DESCRIPTOR,
    )


def test_b1_to_b2_conversion_is_not_available():
    assert not issubclass(B2ProviderIdentity, ProviderIdentity)
    assert not hasattr(B2ProviderIdentity, "from_b1")
    assert not hasattr(B2ProviderIdentity, "upgrade")
    with pytest.raises(TypeError):
        B2ProviderIdentity(ProviderIdentity)  # type: ignore[call-arg]


def test_no_b1_b2_union_type_is_available():
    module_source = inspect.getsource(
        __import__("governance.b2_provider_identity", fromlist=["*"])
    )
    assert "Union" not in module_source
    assert "ProviderIdentity" not in module_source.replace("B2ProviderIdentity", "")


def test_natural_person_identity_is_rejected():
    with pytest.raises(ValueError, match="natural person"):
        B2ProviderIdentityId("b2-provider-identity:person-01")


def test_natural_person_field_is_not_modelable():
    with pytest.raises(TypeError):
        B2ProviderIdentity(**dict(arguments(), natural_person="forbidden"))


def test_free_provider_class_is_rejected():
    with pytest.raises(TypeError, match="B2ProviderClass"):
        B2ProviderIdentity(**dict(arguments(), provider_class="CUSTOM_UNIT"))


def test_missing_provider_class_is_rejected():
    values = arguments()
    values.pop("provider_class")
    with pytest.raises(TypeError):
        B2ProviderIdentity(**values)


def test_free_responsibility_area_is_rejected():
    with pytest.raises(TypeError, match="invalid value"):
        B2ProviderIdentity(
            **dict(arguments(), responsibility_areas=("free responsibility",))
        )


def test_missing_responsibility_area_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        B2ProviderIdentity(**dict(arguments(), responsibility_areas=()))


def test_free_capability_is_rejected():
    with pytest.raises(TypeError, match="invalid value"):
        B2ProviderIdentity(
            **dict(arguments(), capability_descriptors=("free capability",))
        )


def test_missing_capability_descriptor_is_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        B2ProviderIdentity(**dict(arguments(), capability_descriptors=()))


def test_missing_provenance_is_rejected():
    values = arguments()
    values.pop("provenance")
    with pytest.raises(TypeError):
        B2ProviderIdentity(**values)


def test_free_provenance_text_is_rejected():
    with pytest.raises(TypeError, match="B2ProviderProvenance"):
        B2ProviderIdentity(**dict(arguments(), provenance="self confirmed"))


def test_naive_provenance_time_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        B2ProviderProvenance(
            institutional_source_id=B2InstitutionalSourceId(
                "institutional-source:unit-01"
            ),
            governance_decision_id=B2GovernanceDecisionId(
                "governance-decision:adr-0061"
            ),
            registration_basis=B2RegistrationBasisReference(
                "registration-basis:contract-01"
            ),
            reference_id=B2NonPersonalReferenceId(
                "non-personal-reference:evidence-01"
            ),
            created_at=datetime(2026, 8, 3, 12, 0),
        )


def test_no_hidden_system_time_exists():
    source = inspect.getsource(
        __import__("governance.b2_provider_identity", fromlist=["*"])
    )
    assert "datetime.now" not in source
    assert ".now(" not in source


def _assert_forbidden_field(field_name, value="forbidden"):
    assert field_name not in {item.name for item in fields(B2ProviderIdentity)}
    with pytest.raises(TypeError):
        B2ProviderIdentity(**dict(arguments(), **{field_name: value}))


def test_authority_field_is_not_modelable():
    _assert_forbidden_field("authority")


def test_grant_field_is_not_modelable():
    _assert_forbidden_field("grant")


def test_authorization_field_is_not_modelable():
    _assert_forbidden_field("authorization")


def test_permission_field_is_not_modelable():
    _assert_forbidden_field("permission")


def test_invocation_field_is_not_modelable():
    _assert_forbidden_field("invocation")


def test_runtime_field_is_not_modelable():
    _assert_forbidden_field("runtime")


def test_key_reference_is_not_modelable():
    _assert_forbidden_field("key_reference")


def test_key_material_is_not_modelable():
    _assert_forbidden_field("key_material")


def test_credential_is_not_modelable():
    _assert_forbidden_field("credential")


def test_secret_is_not_modelable():
    _assert_forbidden_field("secret")


def test_content_access_is_not_modelable():
    _assert_forbidden_field("content_access")


def test_personal_content_is_not_modelable():
    _assert_forbidden_field("personal_content")


def test_status_field_is_not_modelable():
    _assert_forbidden_field("status")


def test_active_field_is_not_modelable():
    _assert_forbidden_field("active", True)


def test_valid_field_is_not_modelable():
    _assert_forbidden_field("valid", True)


def test_authorized_status_is_not_modelable():
    _assert_forbidden_field("authorized", True)


def test_revoked_status_is_not_modelable():
    _assert_forbidden_field("revoked", True)


def test_expired_status_is_not_modelable():
    _assert_forbidden_field("expired", True)


def test_session_field_is_not_modelable():
    _assert_forbidden_field("session")


def test_cache_field_is_not_modelable():
    _assert_forbidden_field("cache")


def test_token_field_is_not_modelable():
    _assert_forbidden_field("token")


def test_capability_descriptors_have_no_executable_methods_or_flags():
    item = B2CapabilityDescriptor.GENERAL_ORIENTATION_SERVICE_DESCRIPTOR
    for name in (
        "authorize",
        "invoke",
        "execute",
        "activate",
        "runtime",
        "token",
        "grant",
    ):
        assert not hasattr(item, name)


def test_capability_descriptor_is_neither_permission_nor_boolean_flag():
    item = B2CapabilityDescriptor.GENERAL_ORIENTATION_SERVICE_DESCRIPTOR
    assert not isinstance(item, bool)
    assert not hasattr(item, "permission")
    assert not hasattr(item, "allowed")
    assert not hasattr(item, "enabled")


def test_provider_identity_has_no_authorize_path():
    assert not hasattr(B2ProviderIdentity, "authorize")


def test_provider_identity_has_no_invoke_path():
    assert not hasattr(B2ProviderIdentity, "invoke")


def test_provider_identity_has_no_execute_or_runtime_path():
    assert not hasattr(B2ProviderIdentity, "execute")
    assert not hasattr(B2ProviderIdentity, "run")
    assert not hasattr(B2ProviderIdentity, "runtime")


def test_previous_reference_is_declarative_and_cannot_reference_self():
    previous = B2ProviderIdentityId("b2-provider-identity:unit-00")
    item = B2ProviderIdentity(
        **dict(arguments(), previous_identity_reference=previous)
    )
    assert item.previous_identity_reference is previous
    with pytest.raises(ValueError, match="must differ"):
        B2ProviderIdentity(
            **dict(
                arguments(),
                previous_identity_reference=B2ProviderIdentityId(
                    "b2-provider-identity:unit-01"
                ),
            )
        )
