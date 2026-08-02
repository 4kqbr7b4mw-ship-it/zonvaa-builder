"""Technology-neutral contracts for physical operational persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol, Tuple

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.operational_memory import (
    OperationalMemoryArtifactBinding,
    OperationalMemoryPackage,
    OperationalMemoryRecord,
    OperationalMemoryValidator,
)


class PersistencePortOperation(str, Enum):
    STORE = "STORE"
    READ = "READ"
    EXISTS = "EXISTS"


class PersistencePortResultStatus(str, Enum):
    STORED = "STORED"
    FOUND = "FOUND"
    EXISTS = "EXISTS"
    NOT_FOUND = "NOT_FOUND"
    REJECTED = "REJECTED"


class PhysicalPersistenceStatus(str, Enum):
    PERSISTED = "PERSISTED"


class PhysicalBackupStatus(str, Enum):
    PLANNED = "PLANNED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PhysicalRecoveryStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PhysicalCompletenessStatus(str, Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class PersistencePortRequest:
    request_id: str
    operation: PersistencePortOperation
    artifact_reference: str
    artifact_version: int
    physical_storage_reference: str

    def __post_init__(self) -> None:
        _text(self.request_id, "request_id")
        _enum(self.operation, PersistencePortOperation, "operation")
        _text(self.artifact_reference, "artifact_reference")
        _positive(self.artifact_version, "artifact_version")
        _text(self.physical_storage_reference, "physical_storage_reference")


@dataclass(frozen=True)
class PersistencePortResult:
    result_id: str
    request_reference: str
    operation: PersistencePortOperation
    artifact_reference: str
    artifact_version: int
    physical_storage_reference: str
    status: PersistencePortResultStatus
    completed_at: datetime
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.result_id, "result_id")
        _text(self.request_reference, "request_reference")
        _enum(self.operation, PersistencePortOperation, "operation")
        _text(self.artifact_reference, "artifact_reference")
        _positive(self.artifact_version, "artifact_version")
        _text(self.physical_storage_reference, "physical_storage_reference")
        _enum(self.status, PersistencePortResultStatus, "status")
        _aware(self.completed_at, "completed_at")
        _provenance(self.provenance)


class PhysicalOperationalPersistencePort(Protocol):
    """Opaque medium adapter; this package provides no implementation."""

    def execute(self, request: PersistencePortRequest) -> PersistencePortResult:
        ...


@dataclass(frozen=True)
class PhysicalPersistenceRecord:
    record_id: str
    operational_memory_reference: str
    artifact_reference: str
    artifact_version: int
    persistence_status: PhysicalPersistenceStatus
    physical_storage_reference: str
    port_result_reference: str
    persisted_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.record_id, "record_id"),
            (self.operational_memory_reference, "operational_memory_reference"),
            (self.artifact_reference, "artifact_reference"),
            (self.physical_storage_reference, "physical_storage_reference"),
            (self.port_result_reference, "port_result_reference"),
        ):
            _text(value, name)
        _positive(self.artifact_version, "artifact_version")
        _enum(self.persistence_status, PhysicalPersistenceStatus, "persistence_status")
        _aware(self.persisted_at, "persisted_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class PhysicalBackupContract:
    backup_id: str
    persistence_record_reference: str
    backup_status: PhysicalBackupStatus
    backup_at: datetime
    completeness_status: PhysicalCompletenessStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.backup_id, "backup_id")
        _text(self.persistence_record_reference, "persistence_record_reference")
        _enum(self.backup_status, PhysicalBackupStatus, "backup_status")
        _aware(self.backup_at, "backup_at")
        _enum(
            self.completeness_status,
            PhysicalCompletenessStatus,
            "completeness_status",
        )
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class PhysicalRecoveryContract:
    recovery_id: str
    backup_reference: str
    recovery_status: PhysicalRecoveryStatus
    recovered_at: datetime
    completeness_evidence_reference: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.recovery_id, "recovery_id")
        _text(self.backup_reference, "backup_reference")
        _enum(self.recovery_status, PhysicalRecoveryStatus, "recovery_status")
        _aware(self.recovered_at, "recovered_at")
        if self.recovery_status is PhysicalRecoveryStatus.COMPLETED:
            if self.completeness_evidence_reference is None:
                raise ValueError("completed recovery needs completeness evidence")
            _text(
                self.completeness_evidence_reference,
                "completeness_evidence_reference",
            )
        elif self.completeness_evidence_reference is not None:
            raise ValueError("only completed recovery may have completeness evidence")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class PhysicalOperationalPersistencePackage:
    package_id: str
    operational_memory: OperationalMemoryPackage
    port_requests: Tuple[PersistencePortRequest, ...]
    port_results: Tuple[PersistencePortResult, ...]
    persistence_records: Tuple[PhysicalPersistenceRecord, ...]
    backup_contracts: Tuple[PhysicalBackupContract, ...]
    recovery_contracts: Tuple[PhysicalRecoveryContract, ...]

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(self.operational_memory, OperationalMemoryPackage):
            raise TypeError("operational_memory has an invalid type")
        _typed_tuple(self.port_requests, PersistencePortRequest, "port_requests", True)
        _typed_tuple(self.port_results, PersistencePortResult, "port_results", True)
        _typed_tuple(
            self.persistence_records,
            PhysicalPersistenceRecord,
            "persistence_records",
            True,
        )
        _typed_tuple(
            self.backup_contracts,
            PhysicalBackupContract,
            "backup_contracts",
            False,
        )
        _typed_tuple(
            self.recovery_contracts,
            PhysicalRecoveryContract,
            "recovery_contracts",
            False,
        )


@dataclass(frozen=True)
class PhysicalOperationalPersistenceSnapshot:
    snapshot_id: str
    package: PhysicalOperationalPersistencePackage
    operational_memory: OperationalMemoryPackage
    persistence_records: Tuple[PhysicalPersistenceRecord, ...]
    operational_memory_records: Tuple[OperationalMemoryRecord, ...]
    artifact_bindings: Tuple[OperationalMemoryArtifactBinding, ...]
    persistence_statuses: Tuple[PhysicalPersistenceStatus, ...]
    artifact_versions: Tuple[int, ...]
    backup_statuses: Tuple[PhysicalBackupStatus, ...]
    recovery_statuses: Tuple[PhysicalRecoveryStatus, ...]
    review_statuses: Tuple[AuthorityReviewStatus, ...]
    provenances: Tuple[AuthorityProvenance, ...]

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        if not isinstance(self.package, PhysicalOperationalPersistencePackage):
            raise TypeError("package has an invalid type")
        if not isinstance(self.operational_memory, OperationalMemoryPackage):
            raise TypeError("operational_memory has an invalid type")
        _typed_tuple(
            self.persistence_records,
            PhysicalPersistenceRecord,
            "persistence_records",
            True,
        )
        _typed_tuple(
            self.operational_memory_records,
            OperationalMemoryRecord,
            "operational_memory_records",
            True,
        )
        _typed_tuple(
            self.artifact_bindings,
            OperationalMemoryArtifactBinding,
            "artifact_bindings",
            True,
        )
        _typed_tuple(
            self.persistence_statuses,
            PhysicalPersistenceStatus,
            "persistence_statuses",
            True,
        )
        _positive_tuple(self.artifact_versions, "artifact_versions")
        _typed_tuple(
            self.backup_statuses,
            PhysicalBackupStatus,
            "backup_statuses",
            True,
        )
        _typed_tuple(
            self.recovery_statuses,
            PhysicalRecoveryStatus,
            "recovery_statuses",
            False,
        )
        _typed_tuple(
            self.review_statuses,
            AuthorityReviewStatus,
            "review_statuses",
            True,
        )
        _typed_tuple(self.provenances, AuthorityProvenance, "provenances", True)


class PhysicalOperationalPersistenceValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class PhysicalOperationalPersistenceValidator:
    """Validate supplied persistence evidence without accessing a medium."""

    def validate(
        self,
        package: PhysicalOperationalPersistencePackage,
    ) -> PhysicalOperationalPersistencePackage:
        if not isinstance(package, PhysicalOperationalPersistencePackage):
            raise TypeError("package must be a PhysicalOperationalPersistencePackage")
        OperationalMemoryValidator().validate(package.operational_memory)
        self._identities(package)
        self._port_evidence(package)
        self._persistence_records(package)
        self._backup_and_recovery(package)
        return package

    def create_snapshot(
        self,
        package: PhysicalOperationalPersistencePackage,
        *,
        snapshot_id: str,
    ) -> PhysicalOperationalPersistenceSnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        used_ids = {package.package_id}
        used_ids.update(record.record_id for record in package.persistence_records)
        used_ids.update(backup.backup_id for backup in package.backup_contracts)
        used_ids.update(recovery.recovery_id for recovery in package.recovery_contracts)
        if snapshot_id in used_ids:
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        memory_records = tuple(
            _memory_binding(package.operational_memory, record).record
            for record in package.persistence_records
        )
        bindings = tuple(
            _memory_binding(package.operational_memory, record)
            for record in package.persistence_records
        )
        return PhysicalOperationalPersistenceSnapshot(
            snapshot_id=snapshot_id,
            package=package,
            operational_memory=package.operational_memory,
            persistence_records=package.persistence_records,
            operational_memory_records=memory_records,
            artifact_bindings=bindings,
            persistence_statuses=tuple(
                record.persistence_status for record in package.persistence_records
            ),
            artifact_versions=tuple(
                record.artifact_version for record in package.persistence_records
            ),
            backup_statuses=tuple(
                backup.backup_status for backup in package.backup_contracts
            ),
            recovery_statuses=tuple(
                recovery.recovery_status for recovery in package.recovery_contracts
            ),
            review_statuses=tuple(
                record.review_status for record in package.persistence_records
            ),
            provenances=tuple(
                record.provenance for record in package.persistence_records
            ),
        )

    @staticmethod
    def _identities(package: PhysicalOperationalPersistencePackage) -> None:
        groups = (
            tuple(request.request_id for request in package.port_requests),
            tuple(result.result_id for result in package.port_results),
            tuple(record.record_id for record in package.persistence_records),
            tuple(backup.backup_id for backup in package.backup_contracts),
            tuple(recovery.recovery_id for recovery in package.recovery_contracts),
        )
        all_ids = (package.package_id,) + tuple(value for group in groups for value in group)
        if len(all_ids) != len(set(all_ids)):
            _invalid("DUPLICATE_IDENTITY", "persistence identities must be unique")
        artifact_keys = tuple(
            (record.artifact_reference, record.artifact_version)
            for record in package.persistence_records
        )
        if len(artifact_keys) != len(set(artifact_keys)):
            _invalid(
                "DUPLICATE_PERSISTENCE",
                "artifact reference and version may be persisted only once",
            )
        physical_references = tuple(
            record.physical_storage_reference for record in package.persistence_records
        )
        if len(physical_references) != len(set(physical_references)):
            _invalid(
                "DUPLICATE_PHYSICAL_REFERENCE",
                "physical storage references must be unique",
            )

    @staticmethod
    def _port_evidence(package: PhysicalOperationalPersistencePackage) -> None:
        requests = {request.request_id: request for request in package.port_requests}
        if len(requests) != len(package.port_requests):
            _invalid("DUPLICATE_PORT_REQUEST", "port request ids must be unique")
        results = {result.result_id: result for result in package.port_results}
        if len(results) != len(package.port_results):
            _invalid("DUPLICATE_PORT_RESULT", "port result ids must be unique")
        result_request_references = tuple(
            result.request_reference for result in package.port_results
        )
        if len(result_request_references) != len(set(result_request_references)):
            _invalid("DUPLICATE_PORT_RESULT", "port request has multiple results")
        if set(result_request_references) != set(requests):
            _invalid("PORT_RESULT_MISSING", "every port request needs exactly one result")
        allowed_statuses = {
            PersistencePortOperation.STORE: (
                PersistencePortResultStatus.STORED,
                PersistencePortResultStatus.REJECTED,
            ),
            PersistencePortOperation.READ: (
                PersistencePortResultStatus.FOUND,
                PersistencePortResultStatus.NOT_FOUND,
                PersistencePortResultStatus.REJECTED,
            ),
            PersistencePortOperation.EXISTS: (
                PersistencePortResultStatus.EXISTS,
                PersistencePortResultStatus.NOT_FOUND,
                PersistencePortResultStatus.REJECTED,
            ),
        }
        for result in package.port_results:
            request = requests.get(result.request_reference)
            if request is None:
                _invalid("PORT_REQUEST_UNKNOWN", "port result references an unknown request")
            if not (
                result.operation is request.operation
                and result.artifact_reference == request.artifact_reference
                and result.artifact_version == request.artifact_version
                and result.physical_storage_reference
                == request.physical_storage_reference
            ):
                _invalid("PORT_RESULT_INCONSISTENT", "port request and result differ")
            if result.status not in allowed_statuses[result.operation]:
                _invalid("PORT_RESULT_STATUS_INVALID", "port result status is invalid")

    @staticmethod
    def _persistence_records(package: PhysicalOperationalPersistencePackage) -> None:
        results = {result.result_id: result for result in package.port_results}
        for record in package.persistence_records:
            binding = _memory_binding(package.operational_memory, record)
            memory_record = binding.record
            if not (
                record.artifact_reference == memory_record.artifact_reference
                and record.artifact_version == memory_record.artifact_version
            ):
                _invalid(
                    "OPERATIONAL_MEMORY_MISMATCH",
                    "physical record differs from operational memory",
                )
            result = results.get(record.port_result_reference)
            if result is None:
                _invalid("PORT_RESULT_UNKNOWN", "physical record has no port result")
            if not (
                result.operation is PersistencePortOperation.STORE
                and result.status is PersistencePortResultStatus.STORED
                and record.persistence_status is PhysicalPersistenceStatus.PERSISTED
                and result.artifact_reference == record.artifact_reference
                and result.artifact_version == record.artifact_version
                and result.physical_storage_reference
                == record.physical_storage_reference
                and result.completed_at == record.persisted_at
            ):
                _invalid(
                    "PERSISTENCE_RESULT_INCONSISTENT",
                    "persisted record and store result differ",
                )
            if not (
                record.review_status is memory_record.review_status
                and record.review_reference == memory_record.review_reference
                and record.provenance == memory_record.provenance
                and result.provenance == memory_record.provenance
            ):
                _invalid(
                    "PERSISTENCE_GOVERNANCE_INCONSISTENT",
                    "persistence governance differs from operational memory",
                )

    @staticmethod
    def _backup_and_recovery(package: PhysicalOperationalPersistencePackage) -> None:
        records = {record.record_id: record for record in package.persistence_records}
        backups_by_record = {}
        backups_by_id = {}
        for backup in package.backup_contracts:
            record = records.get(backup.persistence_record_reference)
            if record is None:
                _invalid("PERSISTENCE_RECORD_UNKNOWN", "backup references an unknown record")
            if backup.persistence_record_reference in backups_by_record:
                _invalid("DUPLICATE_BACKUP_CONTRACT", "record has multiple backup contracts")
            backups_by_record[backup.persistence_record_reference] = backup
            backups_by_id[backup.backup_id] = backup
            if not (
                backup.review_status is record.review_status
                and backup.review_reference == record.review_reference
                and backup.provenance == record.provenance
            ):
                _invalid("BACKUP_GOVERNANCE_INCONSISTENT", "backup governance differs")
            if (
                backup.backup_status is PhysicalBackupStatus.COMPLETED
                and backup.completeness_status is not PhysicalCompletenessStatus.COMPLETE
            ):
                _invalid("BACKUP_INCOMPLETE", "completed backup must be complete")
            if (
                backup.backup_status is not PhysicalBackupStatus.COMPLETED
                and backup.completeness_status is PhysicalCompletenessStatus.COMPLETE
            ):
                _invalid("BACKUP_STATUS_INCONSISTENT", "only completed backup may be complete")
        if set(backups_by_record) != set(records):
            _invalid("BACKUP_CONTRACT_MISSING", "every persistence record needs a backup contract")
        recovered_backups = set()
        for recovery in package.recovery_contracts:
            backup = backups_by_id.get(recovery.backup_reference)
            if backup is None:
                _invalid("BACKUP_UNKNOWN", "recovery references an unknown backup")
            if recovery.backup_reference in recovered_backups:
                _invalid("DUPLICATE_RECOVERY_CONTRACT", "backup has multiple recovery contracts")
            recovered_backups.add(recovery.backup_reference)
            if not (
                recovery.review_status is backup.review_status
                and recovery.review_reference == backup.review_reference
                and recovery.provenance == backup.provenance
            ):
                _invalid("RECOVERY_GOVERNANCE_INCONSISTENT", "recovery governance differs")
            if (
                recovery.recovery_status is PhysicalRecoveryStatus.COMPLETED
                and not (
                    backup.backup_status is PhysicalBackupStatus.COMPLETED
                    and backup.completeness_status
                    is PhysicalCompletenessStatus.COMPLETE
                )
            ):
                _invalid("RECOVERY_BACKUP_INCOMPLETE", "recovery needs a complete backup")


def _memory_binding(
    memory: OperationalMemoryPackage,
    record: PhysicalPersistenceRecord,
) -> OperationalMemoryArtifactBinding:
    matches = tuple(
        binding
        for binding in memory.bindings
        if binding.record.memory_id == record.operational_memory_reference
    )
    if len(matches) != 1:
        _invalid(
            "OPERATIONAL_MEMORY_REFERENCE_UNKNOWN",
            "physical record needs exactly one operational memory binding",
        )
    return matches[0]


def _invalid(code: str, message: str) -> None:
    raise PhysicalOperationalPersistenceValidationError(code, message)


def _text(value, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _positive(value, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("{} must be a positive integer".format(name))


def _aware(value, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value, enum_type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _typed_tuple(values, item_type, name: str, required: bool) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    if any(not isinstance(value, item_type) for value in values):
        raise TypeError("{} contains an invalid value".format(name))


def _positive_tuple(values, name: str) -> None:
    if not isinstance(values, tuple) or not values:
        raise ValueError("{} must be a non-empty tuple".format(name))
    for value in values:
        _positive(value, name)


def _review_pair(status, reference) -> None:
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed contract needs a review reference")
        _text(reference, "review_reference")
    elif reference is not None:
        raise ValueError("only reviewed contract may reference a review")


def _provenance(value) -> None:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
