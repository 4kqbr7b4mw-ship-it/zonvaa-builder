"""Immutable, read-only audit contracts for supplied runtime evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.read_only_b1_runtime import (
    B1RuntimeExecutionEnvelope,
    B1RuntimeExecutionOutcome,
    B1RuntimeExecutionRequestValidator,
)
from governance.runtime_incident import (
    READ_ONLY_B1_RUNTIME_REFERENCE,
    RuntimeIncidentPackage,
    RuntimeIncidentType,
    RuntimeIncidentValidator,
)
from governance.runtime_observation import (
    ObservationProfileApprovalStatus,
    RuntimeObservationEvent,
    RuntimeObservationGovernance,
    RuntimeObservationGovernanceValidator,
)


class RuntimeAuditSubject(str, Enum):
    RUNTIME_EXECUTION = "RUNTIME_EXECUTION"
    RUNTIME_EVIDENCE = "RUNTIME_EVIDENCE"
    OBSERVATION_GOVERNANCE = "OBSERVATION_GOVERNANCE"
    INCIDENT_OR_NO_INCIDENT_EVIDENCE = "INCIDENT_OR_NO_INCIDENT_EVIDENCE"
    USER_BEHAVIOR = "USER_BEHAVIOR"
    USER_PROFILE = "USER_PROFILE"
    USER_CONTENT = "USER_CONTENT"
    USER_TOPIC = "USER_TOPIC"
    USAGE_STATISTICS = "USAGE_STATISTICS"


SYSTEM_AUDIT_SUBJECTS = (
    RuntimeAuditSubject.RUNTIME_EXECUTION,
    RuntimeAuditSubject.RUNTIME_EVIDENCE,
    RuntimeAuditSubject.OBSERVATION_GOVERNANCE,
    RuntimeAuditSubject.INCIDENT_OR_NO_INCIDENT_EVIDENCE,
)
PROHIBITED_USER_AUDIT_SUBJECTS = (
    RuntimeAuditSubject.USER_BEHAVIOR,
    RuntimeAuditSubject.USER_PROFILE,
    RuntimeAuditSubject.USER_CONTENT,
    RuntimeAuditSubject.USER_TOPIC,
    RuntimeAuditSubject.USAGE_STATISTICS,
)


class RuntimeAuditEvidenceType(str, Enum):
    EXECUTION_REQUEST = "EXECUTION_REQUEST"
    RUNTIME_RESULT = "RUNTIME_RESULT"
    RUNTIME_EXECUTION_EVIDENCE = "RUNTIME_EXECUTION_EVIDENCE"
    RUNTIME_EXECUTION_RECEIPT = "RUNTIME_EXECUTION_RECEIPT"
    OBSERVATION_PROFILE = "OBSERVATION_PROFILE"
    OBSERVATION_SCOPE = "OBSERVATION_SCOPE"
    INCIDENT_OR_NO_INCIDENT_EVIDENCE = "INCIDENT_OR_NO_INCIDENT_EVIDENCE"


class RuntimeAuditCompletenessLevel(str, Enum):
    COMPLETE_CHAIN_REQUIRED = "COMPLETE_CHAIN_REQUIRED"
    EXPLICIT_GAPS_ALLOWED = "EXPLICIT_GAPS_ALLOWED"


class RuntimeAuditCompletenessStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    NOT_ASSESSABLE = "NOT_ASSESSABLE"


class RuntimeAuditResult(str, Enum):
    COMPLETE_AND_CONSISTENT = "COMPLETE_AND_CONSISTENT"
    COMPLETE_WITH_INCIDENT = "COMPLETE_WITH_INCIDENT"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    OBSERVATION_SCOPE_INSUFFICIENT = "OBSERVATION_SCOPE_INSUFFICIENT"
    INCONSISTENT_EVIDENCE = "INCONSISTENT_EVIDENCE"
    NOT_AUDITABLE = "NOT_AUDITABLE"
    BLOCKED_BY_GOVERNANCE_GAP = "BLOCKED_BY_GOVERNANCE_GAP"


class RuntimeAuditProfileChangeActor(str, Enum):
    HUMAN_GOVERNANCE = "HUMAN_GOVERNANCE"
    INSTITUTIONAL_GOVERNANCE = "INSTITUTIONAL_GOVERNANCE"
    RUNTIME = "RUNTIME"
    MODEL = "MODEL"
    PROVIDER = "PROVIDER"
    TOOL = "TOOL"


class RuntimeAuditCheck(str, Enum):
    OBSERVATION_GOVERNANCE_VALID = "OBSERVATION_GOVERNANCE_VALID"
    AUDIT_PROFILE_VALID = "AUDIT_PROFILE_VALID"
    AUDIT_SCOPE_VALID = "AUDIT_SCOPE_VALID"
    RUNTIME_REFERENCES_VALID = "RUNTIME_REFERENCES_VALID"
    RUNTIME_EVIDENCE_VALID = "RUNTIME_EVIDENCE_VALID"
    INCIDENT_EVIDENCE_EXCLUSIVE = "INCIDENT_EVIDENCE_EXCLUSIVE"
    NO_INCIDENT_SCOPE_BOUND = "NO_INCIDENT_SCOPE_BOUND"
    CLAIMS_WITHIN_OBSERVATION_SCOPE = "CLAIMS_WITHIN_OBSERVATION_SCOPE"
    EVIDENCE_COMPLETENESS_VISIBLE = "EVIDENCE_COMPLETENESS_VISIBLE"
    REVIEW_AND_PROVENANCE_VALID = "REVIEW_AND_PROVENANCE_VALID"


@dataclass(frozen=True)
class RuntimeAuditTimeBoundary:
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        _aware(self.starts_at, "starts_at")
        _aware(self.ends_at, "ends_at")
        if self.ends_at < self.starts_at:
            raise ValueError("ends_at must not precede starts_at")


@dataclass(frozen=True)
class RuntimeAuditProfile:
    audit_profile_id: str
    version: int
    name: str
    purpose: str
    observation_profile_reference: str
    observation_profile_version: int
    observation_scope_reference: str
    allowed_audit_subjects: Tuple[RuntimeAuditSubject, ...]
    excluded_audit_subjects: Tuple[RuntimeAuditSubject, ...]
    required_evidence_types: Tuple[RuntimeAuditEvidenceType, ...]
    required_completeness_level: RuntimeAuditCompletenessLevel
    responsibility_reference: str
    change_actor_class: RuntimeAuditProfileChangeActor
    approval_status: ObservationProfileApprovalStatus
    approval_reference: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    justification: str
    previous_profile_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.audit_profile_id, "audit_profile_id"),
            (self.name, "name"),
            (self.purpose, "purpose"),
            (self.observation_profile_reference, "observation_profile_reference"),
            (self.observation_scope_reference, "observation_scope_reference"),
            (self.responsibility_reference, "responsibility_reference"),
            (self.justification, "justification"),
        ):
            _text(value, name)
        _positive(self.version, "version")
        _positive(self.observation_profile_version, "observation_profile_version")
        _typed_unique_nonempty(self.allowed_audit_subjects, RuntimeAuditSubject, "allowed_audit_subjects")
        _typed_unique_nonempty(self.excluded_audit_subjects, RuntimeAuditSubject, "excluded_audit_subjects")
        _typed_unique_nonempty(self.required_evidence_types, RuntimeAuditEvidenceType, "required_evidence_types")
        _enum(self.required_completeness_level, RuntimeAuditCompletenessLevel, "required_completeness_level")
        _enum(self.change_actor_class, RuntimeAuditProfileChangeActor, "change_actor_class")
        _approval_pair(self.approval_status, self.approval_reference)
        _review_pair(self.review_status, self.review_reference)
        if self.previous_profile_reference is not None:
            _text(self.previous_profile_reference, "previous_profile_reference")
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeAuditScope:
    audit_scope_id: str
    audit_profile_reference: str
    execution_reference: str
    observation_scope_reference: str
    observed_runtime_events: Tuple[RuntimeObservationEvent, ...]
    explicitly_unobserved_runtime_events: Tuple[RuntimeObservationEvent, ...]
    available_evidence_types: Tuple[RuntimeAuditEvidenceType, ...]
    missing_evidence_types: Tuple[RuntimeAuditEvidenceType, ...]
    auditable_statements: Tuple[RuntimeObservationEvent, ...]
    explicitly_not_auditable_statements: Tuple[RuntimeObservationEvent, ...]
    time_boundary: RuntimeAuditTimeBoundary
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.audit_scope_id, "audit_scope_id"),
            (self.audit_profile_reference, "audit_profile_reference"),
            (self.execution_reference, "execution_reference"),
            (self.observation_scope_reference, "observation_scope_reference"),
        ):
            _text(value, name)
        for values, item_type, name in (
            (self.observed_runtime_events, RuntimeObservationEvent, "observed_runtime_events"),
            (self.explicitly_unobserved_runtime_events, RuntimeObservationEvent, "explicitly_unobserved_runtime_events"),
            (self.available_evidence_types, RuntimeAuditEvidenceType, "available_evidence_types"),
            (self.missing_evidence_types, RuntimeAuditEvidenceType, "missing_evidence_types"),
            (self.auditable_statements, RuntimeObservationEvent, "auditable_statements"),
            (self.explicitly_not_auditable_statements, RuntimeObservationEvent, "explicitly_not_auditable_statements"),
        ):
            _typed_unique(values, item_type, name)
        if not isinstance(self.time_boundary, RuntimeAuditTimeBoundary):
            raise TypeError("time_boundary has an invalid type")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeAuditEvidence:
    audit_evidence_id: str
    audit_profile_reference: str
    audit_scope_reference: str
    runtime_execution_reference: str
    observation_governance_reference: str
    runtime_evidence_reference: Optional[str]
    incident_or_no_incident_evidence_reference: Optional[str]
    checked_evidence_chain: Tuple[str, ...]
    passed_audit_checks: Tuple[RuntimeAuditCheck, ...]
    failed_audit_checks: Tuple[RuntimeAuditCheck, ...]
    non_executable_audit_checks: Tuple[RuntimeAuditCheck, ...]
    detected_evidence_gaps: Tuple[RuntimeAuditEvidenceType, ...]
    completeness_status: RuntimeAuditCompletenessStatus
    audit_result: RuntimeAuditResult
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.audit_evidence_id, "audit_evidence_id"),
            (self.audit_profile_reference, "audit_profile_reference"),
            (self.audit_scope_reference, "audit_scope_reference"),
            (self.runtime_execution_reference, "runtime_execution_reference"),
            (self.observation_governance_reference, "observation_governance_reference"),
        ):
            _text(value, name)
        for value, name in (
            (self.runtime_evidence_reference, "runtime_evidence_reference"),
            (self.incident_or_no_incident_evidence_reference, "incident_or_no_incident_evidence_reference"),
        ):
            if value is not None:
                _text(value, name)
        _strings(self.checked_evidence_chain, "checked_evidence_chain", False)
        for values, item_type, name in (
            (self.passed_audit_checks, RuntimeAuditCheck, "passed_audit_checks"),
            (self.failed_audit_checks, RuntimeAuditCheck, "failed_audit_checks"),
            (self.non_executable_audit_checks, RuntimeAuditCheck, "non_executable_audit_checks"),
            (self.detected_evidence_gaps, RuntimeAuditEvidenceType, "detected_evidence_gaps"),
        ):
            _typed_unique(values, item_type, name)
        check_sets = (set(self.passed_audit_checks), set(self.failed_audit_checks), set(self.non_executable_audit_checks))
        if any(check_sets[index] & check_sets[other] for index in range(3) for other in range(index + 1, 3)):
            raise ValueError("an audit check must have exactly one status")
        if set().union(*check_sets) != set(RuntimeAuditCheck):
            raise ValueError("every audit check needs an explicit status")
        _enum(self.completeness_status, RuntimeAuditCompletenessStatus, "completeness_status")
        _enum(self.audit_result, RuntimeAuditResult, "audit_result")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class RuntimeAuditPackage:
    package_id: str
    audit_profile: RuntimeAuditProfile
    audit_scope: RuntimeAuditScope
    observation_governance: RuntimeObservationGovernance
    execution_envelope: B1RuntimeExecutionEnvelope
    runtime_outcome: Optional[B1RuntimeExecutionOutcome]
    incident_package: Optional[RuntimeIncidentPackage]
    audit_evidence: RuntimeAuditEvidence
    previous_audit_profile: Optional[RuntimeAuditProfile] = None

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(self.audit_profile, RuntimeAuditProfile):
            raise TypeError("audit_profile has an invalid type")
        if not isinstance(self.audit_scope, RuntimeAuditScope):
            raise TypeError("audit_scope has an invalid type")
        if not isinstance(self.observation_governance, RuntimeObservationGovernance):
            raise TypeError("observation_governance has an invalid type")
        if not isinstance(self.execution_envelope, B1RuntimeExecutionEnvelope):
            raise TypeError("execution_envelope has an invalid type")
        if self.runtime_outcome is not None and not isinstance(self.runtime_outcome, B1RuntimeExecutionOutcome):
            raise TypeError("runtime_outcome has an invalid type")
        if self.incident_package is not None and not isinstance(self.incident_package, RuntimeIncidentPackage):
            raise TypeError("incident_package has an invalid type")
        if not isinstance(self.audit_evidence, RuntimeAuditEvidence):
            raise TypeError("audit_evidence has an invalid type")
        if self.previous_audit_profile is not None and not isinstance(self.previous_audit_profile, RuntimeAuditProfile):
            raise TypeError("previous_audit_profile has an invalid type")


@dataclass(frozen=True)
class RuntimeAuditResolutionSnapshot:
    snapshot_id: str
    audit_profile: RuntimeAuditProfile
    audit_scope: RuntimeAuditScope
    observation_governance: RuntimeObservationGovernance
    execution_envelope: B1RuntimeExecutionEnvelope
    runtime_outcome: Optional[B1RuntimeExecutionOutcome]
    incident_package: Optional[RuntimeIncidentPackage]
    audit_evidence: RuntimeAuditEvidence
    audit_result: RuntimeAuditResult
    detected_evidence_gaps: Tuple[RuntimeAuditEvidenceType, ...]
    explicitly_not_auditable_statements: Tuple[RuntimeObservationEvent, ...]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance


class RuntimeAuditValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class RuntimeAuditValidator:
    """Validate supplied audit evidence without observing or producing it."""

    def validate(self, package: RuntimeAuditPackage) -> RuntimeAuditPackage:
        if not isinstance(package, RuntimeAuditPackage):
            raise TypeError("package must be a RuntimeAuditPackage")
        RuntimeObservationGovernanceValidator().validate(package.observation_governance)
        pre_execution_block = (
            package.incident_package is not None
            and package.incident_package.incident is not None
            and package.incident_package.incident.incident_type
            is RuntimeIncidentType.PRE_EXECUTION_BLOCK
        )
        if not pre_execution_block:
            B1RuntimeExecutionRequestValidator().validate(package.execution_envelope)
        if package.incident_package is not None:
            RuntimeIncidentValidator().validate(package.incident_package)
        self._profile(package)
        self._scope(package)
        self._runtime(package)
        self._no_incident_binding(package)
        self._evidence(package)
        self._identities(package)
        return package

    def create_snapshot(self, package: RuntimeAuditPackage, *, snapshot_id: str) -> RuntimeAuditResolutionSnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        if snapshot_id in self._all_ids(package):
            _invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        evidence = package.audit_evidence
        return RuntimeAuditResolutionSnapshot(
            snapshot_id=snapshot_id,
            audit_profile=package.audit_profile,
            audit_scope=package.audit_scope,
            observation_governance=package.observation_governance,
            execution_envelope=package.execution_envelope,
            runtime_outcome=package.runtime_outcome,
            incident_package=package.incident_package,
            audit_evidence=evidence,
            audit_result=evidence.audit_result,
            detected_evidence_gaps=evidence.detected_evidence_gaps,
            explicitly_not_auditable_statements=package.audit_scope.explicitly_not_auditable_statements,
            review_status=evidence.review_status,
            review_reference=evidence.review_reference,
            provenance=evidence.provenance,
        )

    @staticmethod
    def _profile(package) -> None:
        profile = package.audit_profile
        observation = package.observation_governance
        if set(profile.allowed_audit_subjects) != set(SYSTEM_AUDIT_SUBJECTS) or set(profile.excluded_audit_subjects) != set(PROHIBITED_USER_AUDIT_SUBJECTS):
            _invalid("USER_AUDIT_PROHIBITED", "audit subjects must exclude all user observation")
        if profile.change_actor_class not in (RuntimeAuditProfileChangeActor.HUMAN_GOVERNANCE, RuntimeAuditProfileChangeActor.INSTITUTIONAL_GOVERNANCE):
            _invalid("AUDIT_PROFILE_CHANGE_PROHIBITED", "runtime, model, provider and tool actors cannot change audit profiles")
        if profile.approval_status is not ObservationProfileApprovalStatus.APPROVED:
            _invalid("AUDIT_PROFILE_NOT_APPROVED", "audit profile must be approved")
        if (profile.observation_profile_reference != observation.profile.profile_id or profile.observation_profile_version != observation.profile.version or profile.observation_scope_reference != observation.scope.scope_id):
            _invalid("OBSERVATION_PROFILE_REFERENCE_MISMATCH", "audit profile references another observation governance")
        previous = package.previous_audit_profile
        if profile.version == 1:
            if profile.previous_profile_reference is not None or previous is not None:
                _invalid("UNEXPECTED_PREVIOUS_PROFILE", "version one cannot have a predecessor")
        elif previous is None or profile.previous_profile_reference != previous.audit_profile_id or previous.version + 1 != profile.version:
            _invalid("AUDIT_PROFILE_VERSION_INVALID", "audit profile predecessor is inconsistent")

    @staticmethod
    def _scope(package) -> None:
        scope = package.audit_scope
        profile = package.audit_profile
        observation = package.observation_governance.scope
        if scope.audit_profile_reference != profile.audit_profile_id or scope.observation_scope_reference != observation.scope_id:
            _invalid("AUDIT_SCOPE_REFERENCE_MISMATCH", "audit scope references differ")
        if scope.execution_reference != package.execution_envelope.request.execution_id:
            _invalid("EXECUTION_REFERENCE_MISMATCH", "audit scope references another execution")
        partitions = (
            (scope.observed_runtime_events, scope.explicitly_unobserved_runtime_events, set(RuntimeObservationEvent), "OBSERVATION_SCOPE_INCOMPLETE"),
            (scope.available_evidence_types, scope.missing_evidence_types, set(RuntimeAuditEvidenceType), "EVIDENCE_SCOPE_INCOMPLETE"),
            (scope.auditable_statements, scope.explicitly_not_auditable_statements, set(RuntimeObservationEvent), "AUDIT_STATEMENT_SCOPE_INCOMPLETE"),
        )
        for included, excluded, universe, code in partitions:
            if set(included) & set(excluded) or set(included) | set(excluded) != universe:
                _invalid(code, "audit scope partition is contradictory or incomplete")
        if tuple(scope.observed_runtime_events) != tuple(observation.observed_runtime_events) or tuple(scope.explicitly_unobserved_runtime_events) != tuple(observation.explicitly_unobserved_runtime_events):
            _invalid("OBSERVATION_SCOPE_BINDING_MISMATCH", "audit scope differs from observation scope")
        if set(scope.auditable_statements) - set(scope.observed_runtime_events):
            _invalid("AUDIT_OUTSIDE_OBSERVATION_SCOPE", "audit claims an unobserved event")
        if set(profile.required_evidence_types) - set(scope.available_evidence_types) != set(scope.missing_evidence_types) & set(profile.required_evidence_types):
            _invalid("REQUIRED_EVIDENCE_VISIBILITY_INVALID", "required evidence gaps are not explicit")

    @staticmethod
    def _runtime(package) -> None:
        execution = package.execution_envelope.request
        outcome = package.runtime_outcome
        incident = package.incident_package
        if outcome is not None:
            if outcome.request is not execution:
                _invalid("RUNTIME_OBJECT_IDENTITY_MISMATCH", "runtime outcome changed the execution object")
            if outcome.evidence.execution_reference != execution.execution_id or outcome.result.provider_reference != execution.provider_reference:
                _invalid("RUNTIME_REFERENCE_INCONSISTENT", "runtime references differ")
        if incident is not None:
            if outcome is None or incident.execution_envelope is not package.execution_envelope or incident.runtime_outcome is not outcome:
                _invalid("INCIDENT_OBJECT_IDENTITY_MISMATCH", "incident evidence uses another runtime object")
            if incident.runtime_reference != READ_ONLY_B1_RUNTIME_REFERENCE:
                _invalid("RUNTIME_REFERENCE_INVALID", "incident runtime differs")

    @staticmethod
    def _no_incident_binding(package) -> None:
        incident_package = package.incident_package
        if incident_package is None or incident_package.no_incident is None:
            return
        evidence = incident_package.no_incident
        observation = package.observation_governance
        if (evidence.observation_profile_reference != observation.profile.profile_id or evidence.observation_profile_version != observation.profile.version or evidence.observation_scope_reference != observation.scope.scope_id):
            _invalid("NO_INCIDENT_OBSERVATION_BINDING_MISMATCH", "no-incident evidence references another observation scope")
        if (tuple(evidence.observed_runtime_events) != tuple(observation.scope.observed_runtime_events) or tuple(evidence.explicitly_unobserved_runtime_events) != tuple(observation.scope.explicitly_unobserved_runtime_events)):
            _invalid("NO_INCIDENT_OBSERVATION_SCOPE_MISMATCH", "no-incident event scope differs")
        if not set(evidence.performed_observation_checks) or set(evidence.performed_observation_checks) & set(evidence.unperformed_observation_checks):
            _invalid("NO_INCIDENT_CHECK_BINDING_INVALID", "no-incident checks are incomplete or contradictory")

    @staticmethod
    def _evidence(package) -> None:
        evidence = package.audit_evidence
        profile = package.audit_profile
        scope = package.audit_scope
        observation = package.observation_governance
        outcome = package.runtime_outcome
        incident = package.incident_package
        if (evidence.audit_profile_reference != profile.audit_profile_id or evidence.audit_scope_reference != scope.audit_scope_id or evidence.runtime_execution_reference != scope.execution_reference or evidence.observation_governance_reference != observation.governance_id):
            _invalid("AUDIT_EVIDENCE_REFERENCE_MISMATCH", "audit evidence references differ")
        expected_runtime_ref = outcome.evidence.evidence_id if outcome is not None else None
        expected_incident_ref = None
        if incident is not None:
            expected_incident_ref = incident.incident.incident_id if incident.incident is not None else incident.no_incident.no_incident_id
        if evidence.runtime_evidence_reference is not None and evidence.runtime_evidence_reference != expected_runtime_ref:
            _invalid("AUDIT_EVIDENCE_OBJECT_MISMATCH", "runtime evidence reference differs")
        if evidence.incident_or_no_incident_evidence_reference != expected_incident_ref:
            _invalid("AUDIT_EVIDENCE_OBJECT_MISMATCH", "audit evidence object references differ")
        actual_available = {
            RuntimeAuditEvidenceType.EXECUTION_REQUEST,
            RuntimeAuditEvidenceType.OBSERVATION_PROFILE,
            RuntimeAuditEvidenceType.OBSERVATION_SCOPE,
        }
        if outcome is not None:
            actual_available.update(
                (
                    RuntimeAuditEvidenceType.RUNTIME_RESULT,
                    RuntimeAuditEvidenceType.RUNTIME_EXECUTION_RECEIPT,
                )
            )
        if evidence.runtime_evidence_reference is not None:
            actual_available.add(RuntimeAuditEvidenceType.RUNTIME_EXECUTION_EVIDENCE)
        if evidence.incident_or_no_incident_evidence_reference is not None:
            actual_available.add(RuntimeAuditEvidenceType.INCIDENT_OR_NO_INCIDENT_EVIDENCE)
        if set(scope.available_evidence_types) != actual_available:
            _invalid("EVIDENCE_AVAILABILITY_INCONSISTENT", "available evidence differs from supplied references")
        if set(evidence.detected_evidence_gaps) != set(scope.missing_evidence_types):
            _invalid("EVIDENCE_GAPS_NOT_VISIBLE", "audit evidence must retain every declared gap")
        if (
            RuntimeAuditEvidenceType.RUNTIME_EXECUTION_EVIDENCE
            in scope.missing_evidence_types
            and RuntimeAuditCheck.RUNTIME_EVIDENCE_VALID
            in evidence.passed_audit_checks
        ):
            _invalid("MISSING_EVIDENCE_MARKED_VALID", "missing runtime evidence cannot pass validation")
        if (
            RuntimeAuditEvidenceType.INCIDENT_OR_NO_INCIDENT_EVIDENCE
            in scope.missing_evidence_types
            and RuntimeAuditCheck.INCIDENT_EVIDENCE_EXCLUSIVE
            in evidence.passed_audit_checks
        ):
            _invalid("MISSING_EVIDENCE_MARKED_VALID", "missing incident evidence cannot pass validation")
        if set(evidence.checked_evidence_chain) != set(RuntimeAuditValidator._expected_chain(package)):
            _invalid("AUDIT_CHAIN_INCOMPLETE", "checked evidence chain differs")
        expected_result, expected_completeness = RuntimeAuditValidator._expected_result(package)
        if evidence.audit_result is not expected_result or evidence.completeness_status is not expected_completeness:
            _invalid("AUDIT_RESULT_INCONSISTENT", "audit result exceeds supplied evidence")
        if evidence.provenance != profile.provenance or scope.provenance != profile.provenance:
            _invalid("PROVENANCE_INCONSISTENT", "audit provenance differs")

    @staticmethod
    def _expected_chain(package):
        values = [package.audit_profile.audit_profile_id, package.audit_scope.audit_scope_id, package.observation_governance.governance_id, package.execution_envelope.request.execution_id]
        if package.audit_evidence.runtime_evidence_reference is not None:
            values.append(package.audit_evidence.runtime_evidence_reference)
        if package.incident_package is not None:
            values.append(package.incident_package.package_id)
        return tuple(values)

    @staticmethod
    def _expected_result(package):
        evidence = package.audit_evidence
        scope = package.audit_scope
        if evidence.failed_audit_checks:
            return RuntimeAuditResult.INCONSISTENT_EVIDENCE, RuntimeAuditCompletenessStatus.NOT_ASSESSABLE
        if set(scope.auditable_statements) != set(scope.observed_runtime_events):
            return RuntimeAuditResult.OBSERVATION_SCOPE_INSUFFICIENT, RuntimeAuditCompletenessStatus.INCOMPLETE
        if scope.missing_evidence_types:
            return RuntimeAuditResult.INCOMPLETE_EVIDENCE, RuntimeAuditCompletenessStatus.INCOMPLETE
        if evidence.non_executable_audit_checks:
            return RuntimeAuditResult.BLOCKED_BY_GOVERNANCE_GAP, RuntimeAuditCompletenessStatus.NOT_ASSESSABLE
        if not scope.auditable_statements:
            return RuntimeAuditResult.NOT_AUDITABLE, RuntimeAuditCompletenessStatus.NOT_ASSESSABLE
        if package.incident_package is not None and package.incident_package.incident is not None:
            return RuntimeAuditResult.COMPLETE_WITH_INCIDENT, RuntimeAuditCompletenessStatus.COMPLETE
        return RuntimeAuditResult.COMPLETE_AND_CONSISTENT, RuntimeAuditCompletenessStatus.COMPLETE

    @classmethod
    def _identities(cls, package) -> None:
        ids = cls._all_ids(package)
        if len(ids) != len(set(ids)):
            _invalid("DUPLICATE_IDENTITY", "audit identities must be unique")

    @staticmethod
    def _all_ids(package):
        observation = package.observation_governance
        execution = package.execution_envelope.request
        values = [
            package.package_id,
            package.audit_profile.audit_profile_id,
            package.audit_scope.audit_scope_id,
            package.audit_evidence.audit_evidence_id,
            observation.governance_id,
            observation.profile.profile_id,
            observation.scope.scope_id,
            execution.execution_id,
        ]
        if package.runtime_outcome is not None:
            values.extend(
                (
                    package.runtime_outcome.result.result_id,
                    package.runtime_outcome.evidence.evidence_id,
                    package.runtime_outcome.receipt.receipt_id,
                )
            )
        if package.incident_package is not None:
            values.append(package.incident_package.package_id)
            values.append(
                package.incident_package.incident.incident_id
                if package.incident_package.incident is not None
                else package.incident_package.no_incident.no_incident_id
            )
        if package.previous_audit_profile is not None:
            values.append(package.previous_audit_profile.audit_profile_id)
        return tuple(values)


def _invalid(code, message):
    raise RuntimeAuditValidationError(code, message)


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


def _typed_unique(values, item_type, name):
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if any(not isinstance(value, item_type) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(values, item_type, name):
    _typed_unique(values, item_type, name)
    if not values:
        raise ValueError("{} must not be empty".format(name))


def _strings(values, name, required):
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    for value in values:
        _text(value, name)
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _approval_pair(status, reference):
    _enum(status, ObservationProfileApprovalStatus, "approval_status")
    if status is ObservationProfileApprovalStatus.APPROVED:
        if reference is None:
            raise ValueError("approved audit profile needs an approval reference")
    elif reference is not None:
        raise ValueError("only an approved audit profile may reference an approval")


def _review_pair(status, reference):
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED:
        if reference is None:
            raise ValueError("reviewed audit evidence needs a review reference")
    elif reference is not None:
        raise ValueError("only reviewed audit evidence may reference a review")


def _provenance(value):
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
