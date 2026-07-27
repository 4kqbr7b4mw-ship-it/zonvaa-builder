from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from artifact_contract import (
    ArtifactAuthorization,
    AuthorizationScope,
    AuthorizationStatus,
)
from guardian_runtime import RetentionClass
from knowledge.manager import KnowledgeManager
from user_owned_data import (
    ChecksumAlgorithm,
    ChecksumMetadata,
    ReferenceAuthorization,
    ReferenceRetention,
    StorageAvailability,
    StorageCapability,
    StorageOperation,
    StorageProvider,
    StorageReference,
    StorageScope,
    UserOwnedDataContractLoader,
)


NOW = datetime(2026, 7, 27, 9, 0, tzinfo=timezone.utc)


def authorization(
    *,
    authorization_id="authorization-1",
    reference_id="reference-1",
    owner="person-1",
    scopes=(
        AuthorizationScope.READ,
        AuthorizationScope.AUTHORIZE_ACTION,
    ),
    operations=(
        StorageOperation.REFERENCE,
        StorageOperation.READ,
    ),
    status=AuthorizationStatus.ACTIVE,
    revoked_at=None,
):
    return ReferenceAuthorization(
        reference_id=reference_id,
        authorization=ArtifactAuthorization(
            authorization_id=authorization_id,
            subject_id=owner,
            granted_by=owner,
            scopes=scopes,
            purpose="Access the explicitly referenced user-owned item.",
            status=status,
            granted_at=NOW - timedelta(days=1),
            revoked_at=revoked_at,
            binding_references=(reference_id,),
        ),
        operations=operations,
    )


def reference(**overrides):
    values = {
        "reference_id": "reference-1",
        "owner": "person-1",
        "storage_provider": StorageProvider.LOCAL_FOLDER,
        "storage_scope": StorageScope.OWNER_PRIVATE,
        "locator": "vault-ref:documents/reference-1",
        "checksum": ChecksumMetadata(
            algorithm=ChecksumAlgorithm.SHA256,
            value="a" * 64,
        ),
        "version": 1,
        "created_at": NOW - timedelta(days=2),
        "last_verified": NOW - timedelta(days=1),
        "authorization": authorization(),
        "capability": None,
        "retention": ReferenceRetention(
            RetentionClass.KEEP_UNTIL_REVOKED
        ),
        "availability": StorageAvailability.AVAILABLE,
    }
    values.update(overrides)
    return StorageReference(**values)


def test_provider_scope_availability_and_operation_values_are_stable():
    assert tuple(item.value for item in StorageProvider) == (
        "LOCAL_FOLDER",
        "NAS",
        "PRIVATE_CLOUD",
        "SELF_HOSTED_SERVER",
        "EXTERNAL_CONNECTOR",
        "UNKNOWN",
    )
    assert tuple(item.value for item in StorageScope) == (
        "OWNER_PRIVATE",
        "AUTHORIZED_SHARED",
        "SHARED_SAFE",
        "EXTERNAL_CONTROLLED",
        "UNKNOWN",
    )
    assert tuple(item.value for item in StorageAvailability) == (
        "UNKNOWN",
        "AVAILABLE",
        "TEMPORARILY_UNAVAILABLE",
        "UNAVAILABLE",
        "VERIFICATION_REQUIRED",
    )
    assert tuple(item.value for item in StorageOperation) == (
        "REFERENCE",
        "READ",
        "COPY",
        "SYNCHRONIZE",
        "EXPORT",
        "DELETE_METADATA",
        "DELETE_ORIGINAL",
    )


def test_storage_reference_has_only_the_approved_metadata_fields():
    assert tuple(item.name for item in fields(StorageReference)) == (
        "reference_id",
        "owner",
        "storage_provider",
        "storage_scope",
        "locator",
        "checksum",
        "version",
        "created_at",
        "last_verified",
        "authorization",
        "capability",
        "retention",
        "availability",
    )
    assert "content" not in reference().to_dict()


def test_reference_is_immutable_and_preserves_input_values():
    stored = reference()

    with pytest.raises(FrozenInstanceError):
        stored.version = 2
    assert stored.owner == "person-1"
    assert stored.locator == "vault-ref:documents/reference-1"


@pytest.mark.parametrize(
    "locator",
    (
        "first line\nsecond line",
        "data:application/pdf;base64,AAAA",
        "base64:AAAA",
        "%PDF-1.7 embedded document",
        "A" * 256,
        "plain-path-without-reference-scheme",
    ),
)
def test_locator_rejects_embedded_content_and_untyped_paths(locator):
    with pytest.raises(ValueError, match="locator|content|reference"):
        reference(locator=locator)


@pytest.mark.parametrize(
    "provider,locator",
    (
        (StorageProvider.LOCAL_FOLDER, "local-ref:folder/document"),
        (StorageProvider.NAS, "nas-ref:vault/document"),
        (StorageProvider.PRIVATE_CLOUD, "private-ref:item/123"),
        (
            StorageProvider.SELF_HOSTED_SERVER,
            "self-hosted-ref:item/123",
        ),
        (
            StorageProvider.EXTERNAL_CONNECTOR,
            "connector-ref:item/123",
        ),
        (StorageProvider.UNKNOWN, "unknown-ref:item/123"),
    ),
)
def test_all_provider_kinds_use_the_same_reference_contract(
    provider,
    locator,
):
    stored = reference(
        storage_provider=provider,
        locator=locator,
        availability=StorageAvailability.UNKNOWN,
        last_verified=None,
    )

    assert stored.storage_provider is provider


def test_available_reference_requires_a_verification_time():
    with pytest.raises(ValueError, match="last_verified"):
        reference(last_verified=None)
    with pytest.raises(ValueError, match="precedes"):
        reference(last_verified=NOW - timedelta(days=3))


def test_shared_scope_requires_explicit_owner_authorization():
    with pytest.raises(TypeError, match="ReferenceAuthorization"):
        reference(
            storage_scope=StorageScope.SHARED_SAFE,
            authorization=None,
        )
    with pytest.raises(ValueError, match="belong to the owner"):
        reference(
            storage_scope=StorageScope.AUTHORIZED_SHARED,
            authorization=authorization(owner="person-2"),
        )


def test_authorization_is_granular_and_bound_to_exact_reference():
    with pytest.raises(ValueError, match="bound to its reference"):
        ReferenceAuthorization(
            reference_id="reference-1",
            authorization=ArtifactAuthorization(
                authorization_id="authorization-unbound",
                subject_id="person-1",
                granted_by="person-1",
                scopes=(AuthorizationScope.READ,),
                purpose="An intentionally unbound authorization.",
                status=AuthorizationStatus.ACTIVE,
                granted_at=NOW - timedelta(days=1),
            ),
            operations=(StorageOperation.REFERENCE,),
        )

    with pytest.raises(ValueError, match="another reference"):
        reference(
            authorization=authorization(reference_id="reference-2"),
        )


def test_reference_requires_explicit_reference_operation():
    with pytest.raises(ValueError, match="REFERENCE authorization"):
        reference(
            authorization=authorization(
                operations=(StorageOperation.READ,),
            )
        )


def test_copy_and_synchronization_are_not_implicitly_authorized():
    stored = reference()

    with pytest.raises(ValueError, match="not explicitly authorized"):
        stored.require_authorization(StorageOperation.COPY, NOW)
    with pytest.raises(ValueError, match="not explicitly authorized"):
        stored.require_authorization(StorageOperation.SYNCHRONIZE, NOW)


def test_copy_requires_existing_action_scope_and_explicit_operation():
    with pytest.raises(ValueError, match="authorize_action"):
        authorization(
            scopes=(AuthorizationScope.READ,),
            operations=(StorageOperation.COPY,),
        )

    permitted = reference(
        authorization=authorization(
            operations=(
                StorageOperation.REFERENCE,
                StorageOperation.COPY,
            ),
        )
    )
    assert (
        permitted.require_authorization(StorageOperation.COPY, NOW)
        == "authorization-1"
    )


def test_revoked_authorization_cannot_be_used():
    with pytest.raises(ValueError, match="active"):
        authorization(
            status=AuthorizationStatus.REVOKED,
            revoked_at=NOW,
        )


def test_original_deletion_has_a_stricter_boundary_than_metadata_deletion():
    deletion = authorization(
        operations=(
            StorageOperation.REFERENCE,
            StorageOperation.DELETE_METADATA,
            StorageOperation.DELETE_ORIGINAL,
        )
    )
    unknown = reference(
        storage_provider=StorageProvider.UNKNOWN,
        availability=StorageAvailability.UNKNOWN,
        last_verified=None,
        authorization=deletion,
    )

    assert (
        unknown.require_authorization(
            StorageOperation.DELETE_METADATA,
            NOW,
        )
        == "authorization-1"
    )
    with pytest.raises(ValueError, match="provider capability"):
        unknown.require_authorization(
            StorageOperation.DELETE_ORIGINAL,
            NOW,
        )

    deletable = reference(
        authorization=deletion,
        capability=StorageCapability(
            operations=(StorageOperation.DELETE_ORIGINAL,),
            verified_at=NOW,
            evidence_reference="capability-evidence-1",
        ),
    )
    assert (
        deletable.require_authorization(
            StorageOperation.DELETE_ORIGINAL,
            NOW,
        )
        == "authorization-1"
    )


def test_retention_reuses_guardian_runtime_classes_and_explicit_bases():
    with pytest.raises(ValueError, match="retain_until"):
        ReferenceRetention(RetentionClass.KEEP_UNTIL_DATE)
    with pytest.raises(ValueError, match="binding references"):
        ReferenceRetention(RetentionClass.LEGAL_HOLD)

    held = ReferenceRetention(
        RetentionClass.LEGAL_HOLD,
        binding_references=("binding-1",),
    )
    assert held.retention_class is RetentionClass.LEGAL_HOLD


def test_checksum_is_metadata_and_requires_a_canonical_digest():
    checksum = ChecksumMetadata(
        ChecksumAlgorithm.SHA512,
        "b" * 128,
    )
    assert checksum.to_dict()["value"] == "b" * 128
    with pytest.raises(ValueError, match="lowercase hexadecimal"):
        ChecksumMetadata(ChecksumAlgorithm.SHA256, "A" * 64)


def test_knowledge_manager_validates_without_resolving_locator():
    stored = reference()
    manager = KnowledgeManager()

    assert manager.validate_storage_reference(stored) is stored
    with pytest.raises(TypeError, match="StorageReference"):
        manager.validate_storage_reference("local-ref:document")


def test_contract_loader_is_complete_versioned_and_deterministic():
    first = UserOwnedDataContractLoader().load()
    second = UserOwnedDataContractLoader().load()

    assert first == second
    assert first.version == "1.0"
    assert len(first.content_hash) == 64
    assert first.storage_providers == tuple(StorageProvider)
    assert first.storage_scopes == tuple(StorageScope)
    assert first.availability_states == tuple(StorageAvailability)
    assert first.storage_operations == tuple(StorageOperation)


def test_contract_loader_rejects_an_incomplete_contract(tmp_path):
    source = tmp_path / "contract.md"
    source.write_text(
        "# User-Owned Data\n\nVersion: 1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="incomplete"):
        UserOwnedDataContractLoader(source).load()
