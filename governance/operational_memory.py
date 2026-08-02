"""Immutable operational-memory contracts without a physical storage runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Union

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.read_only_b1_runtime import (
    B1RuntimeExecutionRequest,
    B1RuntimeResult,
    RuntimeExecutionEvidence,
    RuntimeExecutionReceipt,
)
from governance.runtime_audit import (
    RuntimeAuditEvidence,
    RuntimeAuditPackage,
    RuntimeAuditProfile,
    RuntimeAuditResolutionSnapshot,
    RuntimeAuditScope,
    RuntimeAuditValidator,
)
from governance.runtime_incident import (
    RuntimeIncidentEvidence,
    RuntimeIncidentPackage,
    RuntimeIncidentValidator,
    RuntimeNoIncidentEvidence,
)
from governance.runtime_observation import (
    RuntimeObservationGovernance,
    RuntimeObservationGovernanceValidator,
)


class OperationalMemoryArtifactType(str, Enum):
    OBSERVATION_GOVERNANCE = "OBSERVATION_GOVERNANCE"
    RUNTIME_EXECUTION = "RUNTIME_EXECUTION"
    RUNTIME_RESULT = "RUNTIME_RESULT"
    RUNTIME_EVIDENCE = "RUNTIME_EVIDENCE"
    RUNTIME_RECEIPT = "RUNTIME_RECEIPT"
    INCIDENT_EVIDENCE = "INCIDENT_EVIDENCE"
    NO_INCIDENT_EVIDENCE = "NO_INCIDENT_EVIDENCE"
    AUDIT_PROFILE = "AUDIT_PROFILE"
    AUDIT_SCOPE = "AUDIT_SCOPE"
    AUDIT_EVIDENCE = "AUDIT_EVIDENCE"
    AUDIT_RESOLUTION_SNAPSHOT = "AUDIT_RESOLUTION_SNAPSHOT"


class OperationalMemoryOrigin(str, Enum):
    OBSERVATION_GOVERNANCE = "OBSERVATION_GOVERNANCE"
    READ_ONLY_B1_RUNTIME = "READ_ONLY_B1_RUNTIME"
    RUNTIME_INCIDENT_EVIDENCE = "RUNTIME_INCIDENT_EVIDENCE"
    RUNTIME_AUDIT = "RUNTIME_AUDIT"


OperationalMemoryArtifact = Union[
    RuntimeObservationGovernance,
    B1RuntimeExecutionRequest,
    B1RuntimeResult,
    RuntimeExecutionEvidence,
    RuntimeExecutionReceipt,
    RuntimeIncidentEvidence,
    RuntimeNoIncidentEvidence,
    RuntimeAuditProfile,
    RuntimeAuditScope,
    RuntimeAuditEvidence,
    RuntimeAuditResolutionSnapshot,
]


@dataclass(frozen=True)
class OperationalMemoryRecord:
    memory_id: str
    artifact_type: OperationalMemoryArtifactType
    artifact_reference: str
    artifact_version: int
    persisted_at: datetime
    origin: OperationalMemoryOrigin
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.memory_id, "memory_id")
        _enum(self.artifact_type, OperationalMemoryArtifactType, "artifact_type")
        _text(self.artifact_reference, "artifact_reference")
        _positive(self.artifact_version, "artifact_version")
        _aware(self.persisted_at, "persisted_at")
        _enum(self.origin, OperationalMemoryOrigin, "origin")
        _review_pair(self.review_status, self.review_reference)
        if self.review_status is not AuthorityReviewStatus.REVIEWED:
            raise ValueError("operational memory requires reviewed artifacts")
        _provenance(self.provenance)


@dataclass(frozen=True)
class OperationalMemoryArtifactBinding:
    record: OperationalMemoryRecord
    artifact: OperationalMemoryArtifact

    def __post_init__(self) -> None:
        if not isinstance(self.record, OperationalMemoryRecord):
            raise TypeError("record has an invalid type")
        if type(self.artifact) not in _ARTIFACT_TYPES.values():
            raise TypeError("artifact is not an operational evidence type")


@dataclass(frozen=True)
class OperationalMemoryPackage:
    package_id: str
    bindings: Tuple[OperationalMemoryArtifactBinding, ...]
    observation_governances: Tuple[RuntimeObservationGovernance, ...]
    incident_packages: Tuple[RuntimeIncidentPackage, ...]
    audit_packages: Tuple[RuntimeAuditPackage, ...]
    audit_snapshots: Tuple[RuntimeAuditResolutionSnapshot, ...]
    declared_validation_gaps: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        _typed_tuple(self.bindings, OperationalMemoryArtifactBinding, "bindings", True)
        _typed_tuple(
            self.observation_governances,
            RuntimeObservationGovernance,
            "observation_governances",
            False,
        )
        _typed_tuple(
            self.incident_packages,
            RuntimeIncidentPackage,
            "incident_packages",
            False,
        )
        _typed_tuple(self.audit_packages, RuntimeAuditPackage, "audit_packages", False)
        _typed_tuple(
            self.audit_snapshots,
            RuntimeAuditResolutionSnapshot,
            "audit_snapshots",
            False,
        )
        _strings(self.declared_validation_gaps, "declared_validation_gaps", False)


@dataclass(frozen=True)
class OperationalMemorySnapshot:
    snapshot_id: str
    package: OperationalMemoryPackage
    records: Tuple[OperationalMemoryRecord, ...]
    artifact_bindings: Tuple[OperationalMemoryArtifactBinding, ...]
    artifact_types: Tuple[OperationalMemoryArtifactType, ...]
    artifact_versions: Tuple[int, ...]
    review_statuses: Tuple[AuthorityReviewStatus, ...]
    provenances: Tuple[AuthorityProvenance, ...]
    declared_validation_gaps: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        if not isinstance(self.package, OperationalMemoryPackage):
            raise TypeError("package has an invalid type")
        _typed_tuple(self.records, OperationalMemoryRecord, "records", True)
        _typed_tuple(
            self.artifact_bindings,
            OperationalMemoryArtifactBinding,
            "artifact_bindings",
            True,
        )
        _typed_tuple(
            self.artifact_types,
            OperationalMemoryArtifactType,
            "artifact_types",
            True,
        )
        if not isinstance(self.artifact_versions, tuple) or any(
            not isinstance(value, int) or isinstance(value, bool) or value < 1
            for value in self.artifact_versions
        ):
            raise TypeError("artifact_versions contains an invalid value")
        _typed_tuple(
            self.review_statuses,
            AuthorityReviewStatus,
            "review_statuses",
            True,
        )
        _typed_tuple(
            self.provenances,
            AuthorityProvenance,
            "provenances",
            True,
        )
        _strings(self.declared_validation_gaps, "declared_validation_gaps", False)


class OperationalMemoryValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class OperationalMemoryValidator:
    """Validate supplied machine evidence without storing or transforming it."""

    def validate(self, package: OperationalMemoryPackage) -> OperationalMemoryPackage:
        if not isinstance(package, OperationalMemoryPackage):
            raise TypeError("package must be an OperationalMemoryPackage")
        self._validate_contexts(package)
        candidates = self._validated_candidates(package)
        self._validate_bindings(package, candidates)
        self._validate_identities_and_duplicates(package)
        return package

    def create_snapshot(
        self,
        package: OperationalMemoryPackage,
        *,
        snapshot_id: str,
    ) -> OperationalMemorySnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        if snapshot_id == package.package_id or snapshot_id in {
            binding.record.memory_id for binding in package.bindings
        }:
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        records = tuple(binding.record for binding in package.bindings)
        return OperationalMemorySnapshot(
            snapshot_id=snapshot_id,
            package=package,
            records=records,
            artifact_bindings=package.bindings,
            artifact_types=tuple(record.artifact_type for record in records),
            artifact_versions=tuple(record.artifact_version for record in records),
            review_statuses=tuple(record.review_status for record in records),
            provenances=tuple(record.provenance for record in records),
            declared_validation_gaps=package.declared_validation_gaps,
        )

    @staticmethod
    def _validate_contexts(package: OperationalMemoryPackage) -> None:
        observation_validator = RuntimeObservationGovernanceValidator()
        incident_validator = RuntimeIncidentValidator()
        audit_validator = RuntimeAuditValidator()
        for governance in package.observation_governances:
            observation_validator.validate(governance)
        for incident_package in package.incident_packages:
            incident_validator.validate(incident_package)
        for audit_package in package.audit_packages:
            audit_validator.validate(audit_package)
        for snapshot in package.audit_snapshots:
            matching = tuple(
                audit_package
                for audit_package in package.audit_packages
                if snapshot.audit_evidence is audit_package.audit_evidence
            )
            if len(matching) != 1:
                _invalid(
                    "AUDIT_SNAPSHOT_VALIDATION_CONTEXT_MISSING",
                    "audit snapshot needs exactly one validated audit package",
                )
            audit_package = matching[0]
            if not (
                snapshot.audit_profile is audit_package.audit_profile
                and snapshot.audit_scope is audit_package.audit_scope
                and snapshot.observation_governance
                is audit_package.observation_governance
                and snapshot.execution_envelope is audit_package.execution_envelope
                and snapshot.runtime_outcome is audit_package.runtime_outcome
                and snapshot.incident_package is audit_package.incident_package
            ):
                _invalid(
                    "AUDIT_SNAPSHOT_OBJECT_IDENTITY_MISMATCH",
                    "audit snapshot does not preserve the validated objects",
                )

    @classmethod
    def _validated_candidates(cls, package: OperationalMemoryPackage):
        candidates = []
        for governance in package.observation_governances:
            candidates.append((OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE, governance, governance.profile.version))
        incident_contexts = list(package.incident_packages)
        for audit_package in package.audit_packages:
            if audit_package.incident_package is not None and all(
                audit_package.incident_package is not value
                for value in incident_contexts
            ):
                incident_contexts.append(audit_package.incident_package)
            cls._append_runtime_candidates(candidates, audit_package)
            version = audit_package.audit_profile.version
            candidates.extend(
                (
                    (OperationalMemoryArtifactType.AUDIT_PROFILE, audit_package.audit_profile, version),
                    (OperationalMemoryArtifactType.AUDIT_SCOPE, audit_package.audit_scope, version),
                    (OperationalMemoryArtifactType.AUDIT_EVIDENCE, audit_package.audit_evidence, version),
                )
            )
        for incident_package in incident_contexts:
            cls._append_runtime_candidates(candidates, incident_package)
            if incident_package.incident is not None:
                candidates.append((OperationalMemoryArtifactType.INCIDENT_EVIDENCE, incident_package.incident, 1))
            if incident_package.no_incident is not None:
                candidates.append((OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE, incident_package.no_incident, 1))
        for snapshot in package.audit_snapshots:
            version = next(
                audit_package.audit_profile.version
                for audit_package in package.audit_packages
                if snapshot.audit_evidence is audit_package.audit_evidence
            )
            candidates.append((OperationalMemoryArtifactType.AUDIT_RESOLUTION_SNAPSHOT, snapshot, version))
        unique = []
        for candidate in candidates:
            if all(candidate[1] is not existing[1] for existing in unique):
                unique.append(candidate)
        return tuple(unique)

    @staticmethod
    def _append_runtime_candidates(candidates, context) -> None:
        envelope = context.execution_envelope
        outcome = context.runtime_outcome
        candidates.append((OperationalMemoryArtifactType.RUNTIME_EXECUTION, envelope.request, 1))
        if outcome is not None:
            candidates.extend(
                (
                    (OperationalMemoryArtifactType.RUNTIME_RESULT, outcome.result, 1),
                    (OperationalMemoryArtifactType.RUNTIME_EVIDENCE, outcome.evidence, 1),
                    (OperationalMemoryArtifactType.RUNTIME_RECEIPT, outcome.receipt, 1),
                )
            )

    @staticmethod
    def _validate_bindings(package, candidates) -> None:
        for binding in package.bindings:
            record = binding.record
            expected_type = _ARTIFACT_TYPES[record.artifact_type]
            if type(binding.artifact) is not expected_type:
                _invalid("ARTIFACT_TYPE_MISMATCH", "record type differs from artifact")
            matches = tuple(
                candidate
                for candidate in candidates
                if candidate[0] is record.artifact_type
                and candidate[1] is binding.artifact
            )
            if len(matches) != 1:
                _invalid(
                    "ARTIFACT_NOT_VALIDATED",
                    "artifact is absent from the supplied validated contexts",
                )
            _, artifact, expected_version = matches[0]
            reference = _artifact_reference(record.artifact_type, artifact)
            review_status, review_reference, provenance = _artifact_governance(
                record.artifact_type,
                artifact,
            )
            expected_origin = _ARTIFACT_ORIGINS[record.artifact_type]
            if record.artifact_reference != reference:
                _invalid("ARTIFACT_REFERENCE_MISMATCH", "artifact reference differs")
            if record.artifact_version != expected_version:
                _invalid("ARTIFACT_VERSION_MISMATCH", "artifact version differs")
            if record.origin is not expected_origin:
                _invalid("ARTIFACT_ORIGIN_MISMATCH", "artifact origin differs")
            if (
                record.review_status is not review_status
                or record.review_reference != review_reference
            ):
                _invalid("REVIEW_INCONSISTENT", "record review differs from artifact")
            if record.provenance != provenance:
                _invalid("PROVENANCE_INCONSISTENT", "record provenance differs")

    @staticmethod
    def _validate_identities_and_duplicates(package) -> None:
        memory_ids = tuple(binding.record.memory_id for binding in package.bindings)
        if package.package_id in memory_ids or len(memory_ids) != len(set(memory_ids)):
            _invalid("DUPLICATE_IDENTITY", "operational memory identities must be unique")
        artifact_keys = tuple(
            (binding.record.artifact_reference, binding.record.artifact_version)
            for binding in package.bindings
        )
        if len(artifact_keys) != len(set(artifact_keys)):
            _invalid(
                "DUPLICATE_ARTIFACT_VERSION",
                "artifact reference and version identify a duplicate record",
            )


_ARTIFACT_TYPES = {
    OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE: RuntimeObservationGovernance,
    OperationalMemoryArtifactType.RUNTIME_EXECUTION: B1RuntimeExecutionRequest,
    OperationalMemoryArtifactType.RUNTIME_RESULT: B1RuntimeResult,
    OperationalMemoryArtifactType.RUNTIME_EVIDENCE: RuntimeExecutionEvidence,
    OperationalMemoryArtifactType.RUNTIME_RECEIPT: RuntimeExecutionReceipt,
    OperationalMemoryArtifactType.INCIDENT_EVIDENCE: RuntimeIncidentEvidence,
    OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE: RuntimeNoIncidentEvidence,
    OperationalMemoryArtifactType.AUDIT_PROFILE: RuntimeAuditProfile,
    OperationalMemoryArtifactType.AUDIT_SCOPE: RuntimeAuditScope,
    OperationalMemoryArtifactType.AUDIT_EVIDENCE: RuntimeAuditEvidence,
    OperationalMemoryArtifactType.AUDIT_RESOLUTION_SNAPSHOT: RuntimeAuditResolutionSnapshot,
}


_ARTIFACT_ORIGINS = {
    OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE: OperationalMemoryOrigin.OBSERVATION_GOVERNANCE,
    OperationalMemoryArtifactType.RUNTIME_EXECUTION: OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
    OperationalMemoryArtifactType.RUNTIME_RESULT: OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
    OperationalMemoryArtifactType.RUNTIME_EVIDENCE: OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
    OperationalMemoryArtifactType.RUNTIME_RECEIPT: OperationalMemoryOrigin.READ_ONLY_B1_RUNTIME,
    OperationalMemoryArtifactType.INCIDENT_EVIDENCE: OperationalMemoryOrigin.RUNTIME_INCIDENT_EVIDENCE,
    OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE: OperationalMemoryOrigin.RUNTIME_INCIDENT_EVIDENCE,
    OperationalMemoryArtifactType.AUDIT_PROFILE: OperationalMemoryOrigin.RUNTIME_AUDIT,
    OperationalMemoryArtifactType.AUDIT_SCOPE: OperationalMemoryOrigin.RUNTIME_AUDIT,
    OperationalMemoryArtifactType.AUDIT_EVIDENCE: OperationalMemoryOrigin.RUNTIME_AUDIT,
    OperationalMemoryArtifactType.AUDIT_RESOLUTION_SNAPSHOT: OperationalMemoryOrigin.RUNTIME_AUDIT,
}


def _artifact_reference(artifact_type, artifact):
    names = {
        OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE: "governance_id",
        OperationalMemoryArtifactType.RUNTIME_EXECUTION: "execution_id",
        OperationalMemoryArtifactType.RUNTIME_RESULT: "result_id",
        OperationalMemoryArtifactType.RUNTIME_EVIDENCE: "evidence_id",
        OperationalMemoryArtifactType.RUNTIME_RECEIPT: "receipt_id",
        OperationalMemoryArtifactType.INCIDENT_EVIDENCE: "incident_id",
        OperationalMemoryArtifactType.NO_INCIDENT_EVIDENCE: "no_incident_id",
        OperationalMemoryArtifactType.AUDIT_PROFILE: "audit_profile_id",
        OperationalMemoryArtifactType.AUDIT_SCOPE: "audit_scope_id",
        OperationalMemoryArtifactType.AUDIT_EVIDENCE: "audit_evidence_id",
        OperationalMemoryArtifactType.AUDIT_RESOLUTION_SNAPSHOT: "snapshot_id",
    }
    return getattr(artifact, names[artifact_type])


def _artifact_governance(artifact_type, artifact):
    if artifact_type is OperationalMemoryArtifactType.OBSERVATION_GOVERNANCE:
        artifact = artifact.profile
    return artifact.review_status, artifact.review_reference, artifact.provenance


def _invalid(code, message):
    raise OperationalMemoryValidationError(code, message)


def _text(value, name):
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _positive(value, name):
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("{} must be a positive integer".format(name))


def _aware(value, name):
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value, enum_type, name):
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _typed_tuple(values, item_type, name, required):
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    if any(not isinstance(value, item_type) for value in values):
        raise TypeError("{} contains an invalid value".format(name))


def _strings(values, name, required):
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    for value in values:
        _text(value, name)
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _review_pair(status, reference):
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed memory record needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed memory record may reference a review")


def _provenance(value):
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
