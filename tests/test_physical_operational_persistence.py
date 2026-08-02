from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.operational_memory import OperationalMemoryArtifactType
from governance.physical_operational_persistence import (
    PersistencePortOperation,
    PersistencePortRequest,
    PersistencePortResult,
    PersistencePortResultStatus,
    PhysicalBackupContract,
    PhysicalBackupStatus,
    PhysicalCompletenessStatus,
    PhysicalOperationalPersistencePackage,
    PhysicalOperationalPersistenceValidationError,
    PhysicalOperationalPersistenceValidator,
    PhysicalPersistenceRecord,
    PhysicalPersistenceStatus,
    PhysicalRecoveryContract,
    PhysicalRecoveryStatus,
)
from governance.runtime_audit import RuntimeAuditValidator
from tests.test_guardian_capability_invocation import NOW
from tests.test_operational_memory import memory_package
from tests.test_runtime_audit_architecture import complete_package


PERSISTED_AT = NOW + timedelta(hours=4)
BACKUP_AT = NOW + timedelta(hours=5)
RECOVERED_AT = NOW + timedelta(hours=6)


def persistence_package(*, include_backup=True, include_recovery=False):
    audit_package = complete_package()
    memory = memory_package(
        audit_package,
        (OperationalMemoryArtifactType.RUNTIME_EVIDENCE,),
    )
    memory_record = memory.bindings[0].record
    request = PersistencePortRequest(
        request_id="persistence-port-request-v1",
        operation=PersistencePortOperation.STORE,
        artifact_reference=memory_record.artifact_reference,
        artifact_version=memory_record.artifact_version,
        physical_storage_reference="opaque-medium://runtime-evidence-v1",
    )
    result = PersistencePortResult(
        result_id="persistence-port-result-v1",
        request_reference=request.request_id,
        operation=request.operation,
        artifact_reference=request.artifact_reference,
        artifact_version=request.artifact_version,
        physical_storage_reference=request.physical_storage_reference,
        status=PersistencePortResultStatus.STORED,
        completed_at=PERSISTED_AT,
        provenance=memory_record.provenance,
    )
    physical_record = PhysicalPersistenceRecord(
        record_id="physical-persistence-record-v1",
        operational_memory_reference=memory_record.memory_id,
        artifact_reference=memory_record.artifact_reference,
        artifact_version=memory_record.artifact_version,
        persistence_status=PhysicalPersistenceStatus.PERSISTED,
        physical_storage_reference=request.physical_storage_reference,
        port_result_reference=result.result_id,
        persisted_at=PERSISTED_AT,
        review_status=memory_record.review_status,
        review_reference=memory_record.review_reference,
        provenance=memory_record.provenance,
    )
    backup = PhysicalBackupContract(
        backup_id="physical-backup-contract-v1",
        persistence_record_reference=physical_record.record_id,
        backup_status=PhysicalBackupStatus.COMPLETED,
        backup_at=BACKUP_AT,
        completeness_status=PhysicalCompletenessStatus.COMPLETE,
        review_status=physical_record.review_status,
        review_reference=physical_record.review_reference,
        provenance=physical_record.provenance,
    )
    recovery = PhysicalRecoveryContract(
        recovery_id="physical-recovery-contract-v1",
        backup_reference=backup.backup_id,
        recovery_status=PhysicalRecoveryStatus.COMPLETED,
        recovered_at=RECOVERED_AT,
        completeness_evidence_reference="recovery-completeness-evidence-v1",
        review_status=backup.review_status,
        review_reference=backup.review_reference,
        provenance=backup.provenance,
    )
    return PhysicalOperationalPersistencePackage(
        package_id="physical-operational-persistence-package-v1",
        operational_memory=memory,
        port_requests=(request,),
        port_results=(result,),
        persistence_records=(physical_record,),
        backup_contracts=(backup,) if include_backup else (),
        recovery_contracts=(recovery,) if include_recovery else (),
    )


def test_valid_persistence_preserves_operational_memory_identity_deterministically():
    package = persistence_package()
    validator = PhysicalOperationalPersistenceValidator()
    assert validator.validate(package) is package
    assert validator.validate(package) is package
    assert package.operational_memory.bindings[0].artifact is (
        package.operational_memory.audit_packages[0].runtime_outcome.evidence
    )
    with pytest.raises(FrozenInstanceError):
        package.persistence_records = ()


def test_persistence_port_contracts_cover_store_read_and_exists_without_adapter():
    package = persistence_package()
    base = package.port_requests[0]
    requests = tuple(
        replace(base, request_id="request-{}".format(operation.value), operation=operation)
        for operation in PersistencePortOperation
    )
    assert tuple(request.operation for request in requests) == tuple(PersistencePortOperation)
    assert not hasattr(PhysicalOperationalPersistenceValidator(), "execute")


def test_duplicate_persistence_is_rejected_by_artifact_reference_and_version():
    package = persistence_package()
    record = package.persistence_records[0]
    duplicate = replace(
        record,
        record_id="different-physical-record",
        physical_storage_reference="opaque-medium://duplicate-location",
    )
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(package, persistence_records=(record, duplicate))
        )
    assert error.value.code == "DUPLICATE_PERSISTENCE"


def test_unknown_operational_memory_artifact_and_invalid_version_are_rejected():
    package = persistence_package()
    record = package.persistence_records[0]
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(
                package,
                persistence_records=(
                    replace(record, operational_memory_reference="unknown-memory"),
                ),
            )
        )
    assert error.value.code == "OPERATIONAL_MEMORY_REFERENCE_UNKNOWN"
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(package, persistence_records=(replace(record, artifact_version=2),))
        )
    assert error.value.code == "OPERATIONAL_MEMORY_MISMATCH"


def test_store_result_and_physical_reference_must_be_consistent():
    package = persistence_package()
    result = package.port_results[0]
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(
                package,
                port_results=(replace(result, status=PersistencePortResultStatus.FOUND),),
            )
        )
    assert error.value.code == "PORT_RESULT_STATUS_INVALID"


def test_backup_contract_is_required_and_must_be_complete_when_completed():
    without_backup = persistence_package(include_backup=False)
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(without_backup)
    assert error.value.code == "BACKUP_CONTRACT_MISSING"
    package = persistence_package()
    backup = package.backup_contracts[0]
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(
                package,
                backup_contracts=(
                    replace(
                        backup,
                        completeness_status=PhysicalCompletenessStatus.INCOMPLETE,
                    ),
                ),
            )
        )
    assert error.value.code == "BACKUP_INCOMPLETE"


def test_recovery_contract_requires_known_complete_backup():
    package = persistence_package(include_recovery=True)
    assert PhysicalOperationalPersistenceValidator().validate(package) is package
    recovery = package.recovery_contracts[0]
    with pytest.raises(PhysicalOperationalPersistenceValidationError) as error:
        PhysicalOperationalPersistenceValidator().validate(
            replace(
                package,
                recovery_contracts=(replace(recovery, backup_reference="unknown-backup"),),
            )
        )
    assert error.value.code == "BACKUP_UNKNOWN"
    with pytest.raises(ValueError, match="completeness evidence"):
        replace(recovery, completeness_evidence_reference=None)


def test_snapshot_is_read_only_and_projects_original_objects():
    package = persistence_package(include_recovery=True)
    snapshot = PhysicalOperationalPersistenceValidator().create_snapshot(
        package,
        snapshot_id="physical-operational-persistence-snapshot-v1",
    )
    assert snapshot.package is package
    assert snapshot.operational_memory is package.operational_memory
    assert snapshot.persistence_records is package.persistence_records
    assert snapshot.operational_memory_records[0] is (
        package.operational_memory.bindings[0].record
    )
    assert snapshot.artifact_bindings[0] is package.operational_memory.bindings[0]
    with pytest.raises(FrozenInstanceError):
        snapshot.persistence_records = ()


def test_no_database_file_cloud_backup_recovery_metrics_or_notification_runtime():
    validator = PhysicalOperationalPersistenceValidator()
    for name in (
        "connect_database",
        "write_file",
        "connect_cloud",
        "execute_backup",
        "execute_recovery",
        "record_metric",
        "notify",
        "activate_runtime",
        "activate_workflow",
    ):
        assert not hasattr(validator, name)
