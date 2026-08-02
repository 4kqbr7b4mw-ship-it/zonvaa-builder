from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.authority import AuthorityReviewStatus
from governance.operational_memory import (
    OperationalMemoryArtifactBinding,
    OperationalMemoryArtifactType,
    OperationalMemoryOrigin,
    OperationalMemoryPackage,
    OperationalMemoryRecord,
    OperationalMemoryValidationError,
    OperationalMemoryValidator,
)
from governance.runtime_audit import RuntimeAuditValidator
from governance.runtime_incident import RuntimeIncidentType
from tests.test_guardian_capability_invocation import NOW
from tests.test_runtime_audit_architecture import complete_package


PERSISTED_AT = NOW + timedelta(hours=3)


def artifact_metadata(artifact_type, audit_package, snapshot):
    outcome = audit_package.runtime_outcome
    incident_package = audit_package.incident_package
    values = {
        OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE: (
            audit_package.observation_governance,
            audit_package.observation_governance.governance_id,
            audit_package.observation_governance.profile.version,
            OperationalMemoryOrigin.OBSERVATION_GOVERNANCE,
            audit_package.observation_governance.profile,
        ),
        OperationalMemoryArtifactType.RUNTIME_EXECUTION: (
            audit_package.execution_envelope.request,
            audit_package.execution_envelope.request.execution_id,
            1,
            OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
            audit_package.execution_envelope.request,
        ),
        OperationalMemoryArtifactType.RUNTIME_RESULT: (
            outcome.result,
            outcome.result.result_id,
            1,
            OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
            outcome.result,
        ),
        OperationalMemoryArtifactType.RUNTIME_EVIDENCE: (
            outcome.evidence,
            outcome.evidence.evidence_id,
            1,
            OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
            outcome.evidence,
        ),
        OperationalMemoryArtifactType.RUNTIME_RECEIPT: (
            outcome.receipt,
            outcome.receipt.receipt_id,
            1,
            OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
            outcome.receipt,
        ),
        OperationalMemoryArtifactType.AUDIT_PROFILE: (
            audit_package.audit_profile,
            audit_package.audit_profile.audit_profile_id,
            audit_package.audit_profile.version,
            OperationalMemoryOrigin.RUNTIME_AUDIT,
            audit_package.audit_profile,
        ),
        OperationalMemoryArtifactType.AUDIT_SCOPE: (
            audit_package.audit_scope,
            audit_package.audit_scope.audit_scope_id,
            audit_package.audit_profile.version,
            OperationalMemoryOrigin.RUNTIME_AUDIT,
            audit_package.audit_scope,
        ),
        OperationalMemoryArtifactType.AUDIT_EVIDENCE: (
            audit_package.audit_evidence,
            audit_package.audit_evidence.audit_evidence_id,
            audit_package.audit_profile.version,
            OperationalMemoryOrigin.RUNTIME_AUDIT,
            audit_package.audit_evidence,
        ),
        OperationalMemoryArtifactType.AUDIT_RESOLUTION_SNAPSHOT: (
            snapshot,
            snapshot.snapshot_id,
            audit_package.audit_profile.version,
            OperationalMemoryOrigin.RUNTIME_AUDIT,
            snapshot,
        ),
    }
    if incident_package.incident is not None:
        values[OperationalMemoryArtifactType.INCIDENT_EVIDENCE] = (
            incident_package.incident,
            incident_package.incident.incident_id,
            1,
            OperationalMemoryOrigin.RUNTIME_INCIDENT_EVIDENCE,
            incident_package.incident,
        )
    if incident_package.no_incident is not None:
        values[OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE] = (
            incident_package.no_incident,
            incident_package.no_incident.no_incident_id,
            1,
            OperationalMemoryOrigin.RUNTIME_INCIDENT_EVIDENCE,
            incident_package.no_incident,
        )
    return values[artifact_type]


def binding(artifact_type, audit_package, snapshot, *, memory_id=None, **changes):
    artifact, reference, version, origin, governed = artifact_metadata(
        artifact_type,
        audit_package,
        snapshot,
    )
    values = dict(
        memory_id=memory_id or "memory-{}".format(artifact_type.value.lower()),
        artifact_type=artifact_type,
        artifact_reference=reference,
        artifact_version=version,
        persisted_at=PERSISTED_AT,
        origin=origin,
        review_status=governed.review_status,
        review_reference=governed.review_reference,
        provenance=governed.provenance,
    )
    values.update(changes)
    return OperationalMemoryArtifactBinding(
        record=OperationalMemoryRecord(**values),
        artifact=artifact,
    )


def memory_package(audit_package, artifact_types, **changes):
    snapshot = RuntimeAuditValidator().create_snapshot(
        audit_package,
        snapshot_id="runtime-audit-memory-snapshot-v1",
    )
    values = dict(
        package_id="operational-memory-package-v1",
        bindings=tuple(
            binding(artifact_type, audit_package, snapshot)
            for artifact_type in artifact_types
        ),
        observation_governances=(audit_package.observation_governance,),
        incident_packages=(audit_package.incident_package,),
        audit_packages=(audit_package,),
        audit_snapshots=(snapshot,),
        declared_validation_gaps=(),
    )
    values.update(changes)
    return OperationalMemoryPackage(**values)


def test_valid_runtime_incident_no_incident_and_audit_records():
    successful = complete_package()
    incident = complete_package(incident_type=RuntimeIncidentType.PROVIDER_TIMEOUT)
    for audit_package, artifact_type in (
        (successful, OperationalMemoryArtifactType.RUNTIME_EVIDENCE),
        (successful, OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE),
        (successful, OperationalMemoryArtifactType.AUDIT_EVIDENCE),
        (incident, OperationalMemoryArtifactType.INCIDENT_EVIDENCE),
    ):
        package = memory_package(audit_package, (artifact_type,))
        assert OperationalMemoryValidator().validate(package) is package


def test_complete_operational_memory_package_supports_only_canonical_artifacts():
    audit_package = complete_package()
    artifact_types = tuple(
        artifact_type
        for artifact_type in OperationalMemoryArtifactType
        if artifact_type is not OperationalMemoryArtifactType.INCIDENT_EVIDENCE
    )
    package = memory_package(audit_package, artifact_types)
    validator = OperationalMemoryValidator()
    assert validator.validate(package) is package
    assert validator.validate(package) is package
    assert tuple(binding.record.artifact_type for binding in package.bindings) == artifact_types
    with pytest.raises(FrozenInstanceError):
        package.bindings = ()


def test_duplicate_artifact_reference_and_version_is_rejected_even_with_new_memory_id():
    audit_package = complete_package()
    package = memory_package(
        audit_package,
        (OperationalMemoryArtifactType.RUNTIME_EVIDENCE,),
    )
    first = package.bindings[0]
    duplicate = replace(first, record=replace(first.record, memory_id="different-memory-id"))
    with pytest.raises(OperationalMemoryValidationError) as error:
        OperationalMemoryValidator().validate(
            replace(package, bindings=(first, duplicate))
        )
    assert error.value.code == "DUPLICATE_ARTIFACT_VERSION"


def test_unknown_user_conversation_personal_profile_and_usage_artifacts_are_unrepresentable():
    audit_package = complete_package()
    snapshot = RuntimeAuditValidator().create_snapshot(
        audit_package,
        snapshot_id="runtime-audit-memory-snapshot-v1",
    )
    valid = binding(
        OperationalMemoryArtifactType.RUNTIME_EVIDENCE,
        audit_package,
        snapshot,
    )
    for artifact in (
        "conversation content",
        {"user_id": "person-1"},
        {"profile": "usage-pattern"},
        object(),
    ):
        with pytest.raises(TypeError, match="operational evidence type"):
            OperationalMemoryArtifactBinding(record=valid.record, artifact=artifact)
    with pytest.raises(TypeError):
        OperationalMemoryRecord(
            **{
                **valid.record.__dict__,
                "artifact_type": "USER_DATA",
            }
        )


def test_unvalidated_copy_or_inconsistent_version_is_rejected():
    audit_package = complete_package()
    package = memory_package(
        audit_package,
        (OperationalMemoryArtifactType.RUNTIME_EVIDENCE,),
    )
    original = package.bindings[0]
    copied = replace(original.artifact)
    with pytest.raises(OperationalMemoryValidationError) as error:
        OperationalMemoryValidator().validate(
            replace(package, bindings=(replace(original, artifact=copied),))
        )
    assert error.value.code == "ARTIFACT_NOT_VALIDATED"
    with pytest.raises(OperationalMemoryValidationError) as error:
        OperationalMemoryValidator().validate(
            replace(
                package,
                bindings=(
                    replace(
                        original,
                        record=replace(original.record, artifact_version=2),
                    ),
                ),
            )
        )
    assert error.value.code == "ARTIFACT_VERSION_MISMATCH"


def test_review_and_provenance_must_match_original_artifact():
    audit_package = complete_package()
    package = memory_package(
        audit_package,
        (OperationalMemoryArtifactType.RUNTIME_EVIDENCE,),
    )
    original = package.bindings[0]
    with pytest.raises(ValueError, match="requires reviewed artifacts"):
        replace(
            original.record,
            review_status=AuthorityReviewStatus.NOT_REVIEWED,
            review_reference=None,
        )
    wrong_provenance = replace(
        original.record,
        provenance=audit_package.audit_profile.provenance,
    )
    with pytest.raises(OperationalMemoryValidationError) as error:
        OperationalMemoryValidator().validate(
            replace(
                package,
                bindings=(replace(original, record=wrong_provenance),),
            )
        )
    assert error.value.code == "PROVENANCE_INCONSISTENT"


def test_record_requires_timezone_and_machine_origin():
    audit_package = complete_package()
    package = memory_package(
        audit_package,
        (OperationalMemoryArtifactType.RUNTIME_EVIDENCE,),
    )
    record = package.bindings[0].record
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(record, persisted_at=PERSISTED_AT.replace(tzinfo=None))
    with pytest.raises(TypeError):
        replace(record, origin="USER_CONVERSATION")


def test_snapshot_is_read_only_and_preserves_package_records_and_artifacts():
    audit_package = complete_package()
    package = memory_package(
        audit_package,
        (
            OperationalMemoryArtifactType.RUNTIME_EVIDENCE,
            OperationalMemoryArtifactType.AUDIT_EVIDENCE,
        ),
        declared_validation_gaps=("provided validation gap",),
    )
    snapshot = OperationalMemoryValidator().create_snapshot(
        package,
        snapshot_id="operational-memory-snapshot-v1",
    )
    assert snapshot.package is package
    assert snapshot.artifact_bindings is package.bindings
    assert snapshot.records[0] is package.bindings[0].record
    assert snapshot.declared_validation_gaps == package.declared_validation_gaps
    with pytest.raises(FrozenInstanceError):
        snapshot.records = ()


def test_validator_has_no_store_generation_metrics_notification_or_lifecycle_api():
    validator = OperationalMemoryValidator()
    for name in (
        "persist",
        "save",
        "write",
        "delete",
        "expire",
        "archive",
        "replicate",
        "backup",
        "restore",
        "record_metric",
        "notify",
        "derive_incident",
        "derive_no_incident",
        "generate_evidence",
        "activate_runtime",
    ):
        assert not hasattr(validator, name)
