"""Immutable, non-reactive runtime incident evidence from ADR-0052."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Optional, Tuple

from governance.authority import (
    AuthorityCapability,
    AuthorityProvenance,
    AuthorityReviewStatus,
)
from governance.read_only_b1_runtime import (
    B1RuntimeExecutionEnvelope,
    B1RuntimeExecutionOutcome,
    B1RuntimeExecutionRequest,
    ProviderTechnicalStatus,
    RuntimeBlockReason,
    RuntimeExecutionStatus,
    RuntimeProvisionStatus,
)
from guardian_understanding.answer_boundary import AnswerOperatingMode
from governance.runtime_observation import RuntimeObservationEvent


READ_ONLY_B1_RUNTIME_REFERENCE = (
    "governance.read_only_b1_runtime:B1ReadOnlyRuntimeExecutor:v1"
)


class RuntimeIncidentType(str, Enum):
    PROVIDER_TECHNICAL_ERROR = "PROVIDER_TECHNICAL_ERROR"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    OUTPUT_BOUNDARY_REJECTION = "OUTPUT_BOUNDARY_REJECTION"
    INVALID_PROVIDER_RESPONSE = "INVALID_PROVIDER_RESPONSE"
    CONTROLLED_DEGRADATION = "CONTROLLED_DEGRADATION"
    PRE_EXECUTION_BLOCK = "PRE_EXECUTION_BLOCK"


class RuntimeIncidentSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"


class RuntimeIncidentSnapshotStatus(str, Enum):
    INCIDENT_RECORDED = "INCIDENT_RECORDED"
    NO_INCIDENT_RECORDED = "NO_INCIDENT_RECORDED"


EXPECTED_INCIDENT_SEVERITY = MappingProxyType(
    {
        RuntimeIncidentType.PROVIDER_TECHNICAL_ERROR: RuntimeIncidentSeverity.ERROR,
        RuntimeIncidentType.PROVIDER_TIMEOUT: RuntimeIncidentSeverity.ERROR,
        RuntimeIncidentType.OUTPUT_BOUNDARY_REJECTION: RuntimeIncidentSeverity.ERROR,
        RuntimeIncidentType.INVALID_PROVIDER_RESPONSE: RuntimeIncidentSeverity.ERROR,
        RuntimeIncidentType.CONTROLLED_DEGRADATION: RuntimeIncidentSeverity.WARNING,
        RuntimeIncidentType.PRE_EXECUTION_BLOCK: RuntimeIncidentSeverity.WARNING,
    }
)


@dataclass(frozen=True)
class RuntimeIncidentEvidence:
    incident_id: str
    execution_reference: str
    provider_reference: str
    runtime_reference: str
    incident_type: RuntimeIncidentType
    severity: RuntimeIncidentSeverity
    occurred_at: datetime
    affected_capability: AuthorityCapability
    affected_answer_mode: AnswerOperatingMode
    technical_cause: str
    professional_cause: str
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.incident_id, "incident_id"),
            (self.execution_reference, "execution_reference"),
            (self.provider_reference, "provider_reference"),
            (self.runtime_reference, "runtime_reference"),
            (self.technical_cause, "technical_cause"),
            (self.professional_cause, "professional_cause"),
        ):
            _text(value, name)
        _enum(self.incident_type, RuntimeIncidentType, "incident_type")
        _enum(self.severity, RuntimeIncidentSeverity, "severity")
        _aware(self.occurred_at, "occurred_at")
        _enum(self.affected_capability, AuthorityCapability, "affected_capability")
        _enum(self.affected_answer_mode, AnswerOperatingMode, "affected_answer_mode")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeNoIncidentEvidence:
    no_incident_id: str
    execution_reference: str
    provider_reference: str
    runtime_reference: str
    successful_execution_declared: bool
    no_detected_deviation_declared: bool
    observation_profile_reference: str
    observation_profile_version: int
    observation_scope_reference: str
    observed_runtime_events: Tuple[RuntimeObservationEvent, ...]
    explicitly_unobserved_runtime_events: Tuple[RuntimeObservationEvent, ...]
    performed_observation_checks: Tuple[str, ...]
    unperformed_observation_checks: Tuple[str, ...]
    checked_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.no_incident_id, "no_incident_id"),
            (self.execution_reference, "execution_reference"),
            (self.provider_reference, "provider_reference"),
            (self.runtime_reference, "runtime_reference"),
            (self.observation_profile_reference, "observation_profile_reference"),
            (self.observation_scope_reference, "observation_scope_reference"),
        ):
            _text(value, name)
        for value, name in (
            (self.successful_execution_declared, "successful_execution_declared"),
            (
                self.no_detected_deviation_declared,
                "no_detected_deviation_declared",
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be a bool".format(name))
        if (
            not isinstance(self.observation_profile_version, int)
            or isinstance(self.observation_profile_version, bool)
            or self.observation_profile_version < 1
        ):
            raise ValueError("observation_profile_version must be positive")
        _typed_unique(
            self.observed_runtime_events,
            RuntimeObservationEvent,
            "observed_runtime_events",
        )
        _typed_unique(
            self.explicitly_unobserved_runtime_events,
            RuntimeObservationEvent,
            "explicitly_unobserved_runtime_events",
        )
        _strings(
            self.performed_observation_checks,
            "performed_observation_checks",
            required=True,
        )
        _strings(
            self.unperformed_observation_checks,
            "unperformed_observation_checks",
            required=False,
        )
        _aware(self.checked_at, "checked_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeIncidentPackage:
    package_id: str
    runtime_reference: str
    execution_envelope: B1RuntimeExecutionEnvelope
    runtime_outcome: B1RuntimeExecutionOutcome
    incident: Optional[RuntimeIncidentEvidence]
    no_incident: Optional[RuntimeNoIncidentEvidence]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        _text(self.runtime_reference, "runtime_reference")
        if not isinstance(self.execution_envelope, B1RuntimeExecutionEnvelope):
            raise TypeError("execution_envelope has an invalid type")
        if not isinstance(self.runtime_outcome, B1RuntimeExecutionOutcome):
            raise TypeError("runtime_outcome has an invalid type")
        if self.incident is not None and not isinstance(
            self.incident, RuntimeIncidentEvidence
        ):
            raise TypeError("incident has an invalid type")
        if self.no_incident is not None and not isinstance(
            self.no_incident, RuntimeNoIncidentEvidence
        ):
            raise TypeError("no_incident has an invalid type")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeIncidentSnapshot:
    snapshot_id: str
    runtime_reference: str
    execution: B1RuntimeExecutionRequest
    runtime_outcome: B1RuntimeExecutionOutcome
    incident: Optional[RuntimeIncidentEvidence]
    no_incident: Optional[RuntimeNoIncidentEvidence]
    severity: Optional[RuntimeIncidentSeverity]
    status: RuntimeIncidentSnapshotStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        _text(self.runtime_reference, "runtime_reference")
        if not isinstance(self.execution, B1RuntimeExecutionRequest):
            raise TypeError("execution has an invalid type")
        if not isinstance(self.runtime_outcome, B1RuntimeExecutionOutcome):
            raise TypeError("runtime_outcome has an invalid type")
        if self.incident is not None and not isinstance(
            self.incident, RuntimeIncidentEvidence
        ):
            raise TypeError("incident has an invalid type")
        if self.no_incident is not None and not isinstance(
            self.no_incident, RuntimeNoIncidentEvidence
        ):
            raise TypeError("no_incident has an invalid type")
        if self.severity is not None:
            _enum(self.severity, RuntimeIncidentSeverity, "severity")
        _enum(self.status, RuntimeIncidentSnapshotStatus, "status")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


class RuntimeIncidentValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class RuntimeIncidentValidator:
    """Validate supplied evidence without detecting or reacting to incidents."""

    def validate(self, package: RuntimeIncidentPackage) -> RuntimeIncidentPackage:
        if not isinstance(package, RuntimeIncidentPackage):
            raise TypeError("package must be a RuntimeIncidentPackage")
        if package.runtime_reference != READ_ONLY_B1_RUNTIME_REFERENCE:
            _invalid("RUNTIME_REFERENCE_INVALID", "runtime reference is not canonical")
        self._validate_runtime_objects(package)
        self._validate_evidence_choice(package)
        self._validate_identities(package)
        self._validate_provenance(package)
        return package

    def create_snapshot(
        self,
        package: RuntimeIncidentPackage,
        *,
        snapshot_id: str,
        review_status: AuthorityReviewStatus,
        review_reference: Optional[str],
        provenance: AuthorityProvenance,
    ) -> RuntimeIncidentSnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        identities = self._identities(package)
        if snapshot_id in identities:
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        if provenance != package.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "snapshot provenance differs")
        incident = package.incident
        status = RuntimeIncidentSnapshotStatus.INCIDENT_RECORDED
        severity = incident.severity if incident is not None else None
        if package.no_incident is not None:
            status = RuntimeIncidentSnapshotStatus.NO_INCIDENT_RECORDED
        return RuntimeIncidentSnapshot(
            snapshot_id=snapshot_id,
            runtime_reference=package.runtime_reference,
            execution=package.execution_envelope.request,
            runtime_outcome=package.runtime_outcome,
            incident=package.incident,
            no_incident=package.no_incident,
            severity=severity,
            status=status,
            review_status=review_status,
            review_reference=review_reference,
            provenance=provenance,
        )

    @staticmethod
    def _validate_runtime_objects(package) -> None:
        envelope = package.execution_envelope
        outcome = package.runtime_outcome
        request = envelope.request
        result = outcome.result
        evidence = outcome.evidence
        receipt = outcome.receipt
        if outcome.request is not request:
            _invalid(
                "RUNTIME_OBJECT_IDENTITY_MISMATCH",
                "runtime outcome must retain the execution request object",
            )
        if (
            result.execution_reference != request.execution_id
            or evidence.execution_reference != request.execution_id
            or receipt.execution_reference != request.execution_id
            or receipt.result_reference != result.result_id
            or receipt.completion_status is not result.status
            or evidence.provider_called is not receipt.provider_called
            or result.provider_reference != request.provider_reference
            or evidence.provider_reference != request.provider_reference
            or evidence.authorization_reference != request.authorization_reference
            or result.capability is not request.capability
            or result.answer_mode is not request.answer_mode
            or receipt.checked_boundary_reference
            != envelope.invocation_boundary.boundary_id
        ):
            _invalid(
                "RUNTIME_REFERENCE_INCONSISTENT",
                "runtime result, evidence or receipt references differ",
            )
        if (
            result.finished_at != evidence.finished_at
            or result.finished_at != receipt.finished_at
            or result.started_at != evidence.started_at
            or result.started_at != receipt.started_at
        ):
            _invalid("RUNTIME_TIME_INCONSISTENT", "runtime timestamps differ")

    @classmethod
    def _validate_evidence_choice(cls, package) -> None:
        if (package.incident is None) == (package.no_incident is None):
            _invalid(
                "EXCLUSIVE_EVIDENCE_REQUIRED",
                "exactly one incident or no-incident evidence is required",
            )
        if package.incident is not None:
            cls._validate_incident(package)
        else:
            cls._validate_no_incident(package)

    @staticmethod
    def _validate_incident(package) -> None:
        incident = package.incident
        outcome = package.runtime_outcome
        request = outcome.request
        result = outcome.result
        if (
            incident.runtime_reference != package.runtime_reference
            or incident.execution_reference != request.execution_id
            or incident.provider_reference != request.provider_reference
            or incident.affected_capability is not request.capability
            or incident.affected_answer_mode is not request.answer_mode
        ):
            _invalid("INCIDENT_REFERENCE_INCONSISTENT", "incident references differ")
        if not request.started_at <= incident.occurred_at <= result.finished_at:
            _invalid("INCIDENT_TIME_INCONSISTENT", "incident time is outside execution")
        if incident.severity is not EXPECTED_INCIDENT_SEVERITY[incident.incident_type]:
            _invalid("INCIDENT_SEVERITY_INCONSISTENT", "incident severity differs")
        expected = {
            RuntimeIncidentType.PROVIDER_TECHNICAL_ERROR: (
                (RuntimeExecutionStatus.PROVIDER_ERROR,),
                (RuntimeBlockReason.PROVIDER_TECHNICAL_ERROR,),
                True,
            ),
            RuntimeIncidentType.PROVIDER_TIMEOUT: (
                (RuntimeExecutionStatus.TIMED_OUT,),
                (RuntimeBlockReason.PROVIDER_TIMEOUT,),
                True,
            ),
            RuntimeIncidentType.OUTPUT_BOUNDARY_REJECTION: (
                (RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE,),
                (RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED,),
                True,
            ),
            RuntimeIncidentType.INVALID_PROVIDER_RESPONSE: (
                (RuntimeExecutionStatus.INVALID_PROVIDER_RESPONSE,),
                (RuntimeBlockReason.PROVIDER_RESPONSE_INVALID,),
                True,
            ),
            RuntimeIncidentType.CONTROLLED_DEGRADATION: (
                (RuntimeExecutionStatus.DEGRADED,),
                (None,),
                True,
            ),
            RuntimeIncidentType.PRE_EXECUTION_BLOCK: (
                (RuntimeExecutionStatus.BLOCKED, RuntimeExecutionStatus.REJECTED),
                tuple(
                    item
                    for item in RuntimeBlockReason
                    if item
                    not in (
                        RuntimeBlockReason.PROVIDER_TIMEOUT,
                        RuntimeBlockReason.PROVIDER_TECHNICAL_ERROR,
                        RuntimeBlockReason.PROVIDER_RESPONSE_INVALID,
                        RuntimeBlockReason.OUTPUT_BOUNDARY_FAILED,
                    )
                ),
                False,
            ),
        }[incident.incident_type]
        statuses, reasons, provider_called = expected
        if (
            result.status not in statuses
            or result.block_reason not in reasons
            or outcome.evidence.provider_called is not provider_called
        ):
            _invalid(
                "INCIDENT_RESULT_INCONSISTENT",
                "incident type does not match the supplied runtime outcome",
            )

    @staticmethod
    def _validate_no_incident(package) -> None:
        evidence = package.no_incident
        outcome = package.runtime_outcome
        request = outcome.request
        result = outcome.result
        if (
            evidence.runtime_reference != package.runtime_reference
            or evidence.execution_reference != request.execution_id
            or evidence.provider_reference != request.provider_reference
        ):
            _invalid(
                "NO_INCIDENT_REFERENCE_INCONSISTENT",
                "no-incident references differ",
            )
        if not (
            evidence.successful_execution_declared
            and evidence.no_detected_deviation_declared
        ):
            _invalid(
                "NO_INCIDENT_DECLARATION_INCOMPLETE",
                "both no-incident declarations are required",
            )
        observed = set(evidence.observed_runtime_events)
        unobserved = set(evidence.explicitly_unobserved_runtime_events)
        if observed & unobserved or observed | unobserved != set(RuntimeObservationEvent):
            _invalid(
                "NO_INCIDENT_OBSERVATION_SCOPE_INVALID",
                "no-incident evidence needs a complete observation partition",
            )
        if set(evidence.performed_observation_checks) & set(
            evidence.unperformed_observation_checks
        ):
            _invalid(
                "NO_INCIDENT_CHECKS_CONTRADICTORY",
                "an observation check cannot be performed and unperformed",
            )
        if not request.started_at <= evidence.checked_at <= result.finished_at:
            _invalid(
                "NO_INCIDENT_TIME_INCONSISTENT",
                "no-incident check time is outside execution",
            )
        if not (
            result.status is RuntimeExecutionStatus.SUCCEEDED
            and result.technical_status is ProviderTechnicalStatus.SUCCEEDED
            and result.provision_status
            is RuntimeProvisionStatus.PROVIDED_NOT_ACTIVATED
            and result.block_reason is None
            and outcome.evidence.provider_called
            and outcome.receipt.provider_called
        ):
            _invalid(
                "NO_INCIDENT_REQUIRES_SUCCESS",
                "no-incident evidence requires a successful runtime outcome",
            )

    @classmethod
    def _validate_identities(cls, package) -> None:
        identities = cls._identities(package)
        if len(identities) != len(set(identities)):
            _invalid("DUPLICATE_IDENTITY", "incident identities must be unique")

    @staticmethod
    def _identities(package):
        outcome = package.runtime_outcome
        evidence_id = (
            package.incident.incident_id
            if package.incident is not None
            else package.no_incident.no_incident_id
        )
        return (
            package.package_id,
            evidence_id,
            outcome.request.execution_id,
            outcome.result.result_id,
            outcome.evidence.evidence_id,
            outcome.receipt.receipt_id,
        )

    @staticmethod
    def _validate_provenance(package) -> None:
        supplied = (
            package.incident.provenance
            if package.incident is not None
            else package.no_incident.provenance
        )
        outcome = package.runtime_outcome
        if (
            supplied != package.provenance
            or package.execution_envelope.request.provenance != package.provenance
            or outcome.result.provenance != package.provenance
            or outcome.evidence.provenance != package.provenance
            or outcome.receipt.provenance != package.provenance
        ):
            _invalid("PROVENANCE_INCONSISTENT", "incident provenance differs")


def _invalid(code: str, message: str) -> None:
    raise RuntimeIncidentValidationError(code, message)


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _review_pair(status, reference) -> None:
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed evidence needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed evidence may reference a review")


def _provenance(value) -> None:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")


def _typed_unique(values, item_type, name) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if any(not isinstance(value, item_type) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _strings(values, name, required) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    for value in values:
        _text(value, name)
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))
