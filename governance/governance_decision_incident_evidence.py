"""Immutable ADR-0064/A1 governance decision and incident evidence contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, Union


GOVERNANCE_DECISION_INCIDENT_CONTRACT_VERSION = "1.0"
GOVERNANCE_DECISION_RECORD_DIRECTORY = "governance/decisions/"
GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY = "governance/incidents/"


class GovernanceDecisionClass(str, Enum):
    ARCHITECTURE_RATIFICATION = "ARCHITECTURE_RATIFICATION"
    INSTITUTIONAL_IMPLEMENTATION_APPROVAL = "INSTITUTIONAL_IMPLEMENTATION_APPROVAL"
    COMMIT_APPROVAL = "COMMIT_APPROVAL"
    PUSH_APPROVAL = "PUSH_APPROVAL"


class GovernanceInstitutionalRole(str, Enum):
    INSTITUTION_FOUNDER = "INSTITUTION_FOUNDER"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"
    REVIEWER = "REVIEWER"


class GovernanceStep(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    ADR_DOCUMENTATION = "ADR_DOCUMENTATION"
    ARCHITECTURE_VALIDATION = "ARCHITECTURE_VALIDATION"
    HUMAN_RATIFICATION = "HUMAN_RATIFICATION"
    RATIFICATION_DOCUMENTATION = "RATIFICATION_DOCUMENTATION"
    RATIFICATION_COMMIT = "RATIFICATION_COMMIT"
    RATIFICATION_PUSH = "RATIFICATION_PUSH"
    INSTITUTIONAL_IMPLEMENTATION_APPROVAL = "INSTITUTIONAL_IMPLEMENTATION_APPROVAL"
    IMPLEMENTATION_APPROVAL_DOCUMENTATION = "IMPLEMENTATION_APPROVAL_DOCUMENTATION"
    IMPLEMENTATION_APPROVAL_COMMIT = "IMPLEMENTATION_APPROVAL_COMMIT"
    IMPLEMENTATION_APPROVAL_PUSH = "IMPLEMENTATION_APPROVAL_PUSH"
    SEPARATE_IMPLEMENTATION_ORDER = "SEPARATE_IMPLEMENTATION_ORDER"
    IMPLEMENTATION = "IMPLEMENTATION"
    TESTS_AND_REVIEW = "TESTS_AND_REVIEW"
    COMMIT_APPROVAL = "COMMIT_APPROVAL"
    IMPLEMENTATION_COMMIT = "IMPLEMENTATION_COMMIT"
    PUSH_APPROVAL = "PUSH_APPROVAL"
    IMPLEMENTATION_PUSH = "IMPLEMENTATION_PUSH"


class GovernanceScopeType(str, Enum):
    GRANTED_SCOPE = "GRANTED_SCOPE"
    EXCLUDED_SCOPE = "EXCLUDED_SCOPE"


class GovernanceDeviationCode(str, Enum):
    STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR = "STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR"
    REQUIRED_APPROVAL_ABSENT = "REQUIRED_APPROVAL_ABSENT"
    REQUIRED_EVIDENCE_ABSENT = "REQUIRED_EVIDENCE_ABSENT"
    APPROVED_SCOPE_EXCEEDED = "APPROVED_SCOPE_EXCEEDED"
    DOCUMENTED_STATUS_CONTRADICTS_EVIDENCE = "DOCUMENTED_STATUS_CONTRADICTS_EVIDENCE"
    WORK_STATE_RETROACTIVELY_REINTERPRETED = "WORK_STATE_RETROACTIVELY_REINTERPRETED"
    DECISION_TIME_EVIDENCE_ABSENT = "DECISION_TIME_EVIDENCE_ABSENT"
    DECISION_AND_DOCUMENTATION_TIME_CONFLATED = "DECISION_AND_DOCUMENTATION_TIME_CONFLATED"


class GovernanceIncidentClass(str, Enum):
    IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE = "IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE"
    IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL = "IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL"
    IMPLEMENTATION_BEFORE_APPROVAL_PUSH = "IMPLEMENTATION_BEFORE_APPROVAL_PUSH"
    COMMIT_WITHOUT_COMMIT_APPROVAL = "COMMIT_WITHOUT_COMMIT_APPROVAL"
    PUSH_WITHOUT_PUSH_APPROVAL = "PUSH_WITHOUT_PUSH_APPROVAL"
    SCOPE_EXCEEDED = "SCOPE_EXCEEDED"
    GOVERNANCE_EVIDENCE_MISSING = "GOVERNANCE_EVIDENCE_MISSING"
    STATUS_MISREPRESENTED = "STATUS_MISREPRESENTED"
    WORK_STATE_RETROACTIVELY_REINTERPRETED = "WORK_STATE_RETROACTIVELY_REINTERPRETED"
    DECISION_TIME_NOT_DOCUMENTED = "DECISION_TIME_NOT_DOCUMENTED"
    DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED = "DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED"


class GovernanceEvidenceType(str, Enum):
    ADR_ARTIFACT = "ADR_ARTIFACT"
    ARCHITECTURE_VALIDATION_ARTIFACT = "ARCHITECTURE_VALIDATION_ARTIFACT"
    RATIFICATION_RECORD = "RATIFICATION_RECORD"
    IMPLEMENTATION_APPROVAL_RECORD = "IMPLEMENTATION_APPROVAL_RECORD"
    COMMIT_REFERENCE = "COMMIT_REFERENCE"
    PUSH_EVIDENCE = "PUSH_EVIDENCE"
    TEST_VALIDATION_ARTIFACT = "TEST_VALIDATION_ARTIFACT"
    HANDOVER_ARTIFACT = "HANDOVER_ARTIFACT"
    REPOSITORY_STATUS_EVIDENCE = "REPOSITORY_STATUS_EVIDENCE"
    GOVERNANCE_DECISION_RECORD = "GOVERNANCE_DECISION_RECORD"


class MissingGovernanceEvidenceType(str, Enum):
    RATIFICATION_EVIDENCE_MISSING = "RATIFICATION_EVIDENCE_MISSING"
    IMPLEMENTATION_APPROVAL_EVIDENCE_MISSING = "IMPLEMENTATION_APPROVAL_EVIDENCE_MISSING"
    COMMIT_APPROVAL_EVIDENCE_MISSING = "COMMIT_APPROVAL_EVIDENCE_MISSING"
    PUSH_APPROVAL_EVIDENCE_MISSING = "PUSH_APPROVAL_EVIDENCE_MISSING"
    DECISION_TIME_EVIDENCE_MISSING = "DECISION_TIME_EVIDENCE_MISSING"
    DECISION_ROLE_EVIDENCE_MISSING = "DECISION_ROLE_EVIDENCE_MISSING"
    SCOPE_DOCUMENTATION_MISSING = "SCOPE_DOCUMENTATION_MISSING"
    PUSH_TIME_NOT_RECONSTRUCTABLE = "PUSH_TIME_NOT_RECONSTRUCTABLE"
    DECISION_DOCUMENTATION_TIME_SEPARATION_MISSING = "DECISION_DOCUMENTATION_TIME_SEPARATION_MISSING"


class MissingGovernanceEvidenceStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED_BY_REFERENCED_EVIDENCE = "CLOSED_BY_REFERENCED_EVIDENCE"
    HISTORICALLY_NOT_RECONSTRUCTABLE = "HISTORICALLY_NOT_RECONSTRUCTABLE"


class GovernanceImpactCode(str, Enum):
    GOVERNANCE_TRACEABILITY_LIMITED = "GOVERNANCE_TRACEABILITY_LIMITED"
    GATE_SEQUENCE_BREACHED = "GATE_SEQUENCE_BREACHED"
    SCOPE_CONFORMITY_UNCONFIRMED = "SCOPE_CONFORMITY_UNCONFIRMED"
    FORMAL_STATUS_UNCONFIRMED = "FORMAL_STATUS_UNCONFIRMED"
    NO_TECHNICAL_ERROR_EVIDENCED = "NO_TECHNICAL_ERROR_EVIDENCED"
    NO_RUNTIME_IMPACT_EVIDENCED = "NO_RUNTIME_IMPACT_EVIDENCED"
    NO_PERSONAL_DATA_IMPACT_EVIDENCED = "NO_PERSONAL_DATA_IMPACT_EVIDENCED"


class GovernanceCorrectionStep(str, Enum):
    DOCUMENT_MISSING_EVIDENCE = "DOCUMENT_MISSING_EVIDENCE"
    PUSH_APPROVAL_COMMIT = "PUSH_APPROVAL_COMMIT"
    REISSUE_IMPLEMENTATION_ORDER = "REISSUE_IMPLEMENTATION_ORDER"
    REVALIDATE_WORK_STATE_AGAINST_SCOPE = "REVALIDATE_WORK_STATE_AGAINST_SCOPE"
    ADD_MISSING_NEGATIVE_TESTS = "ADD_MISSING_NEGATIVE_TESTS"
    CORRECT_STATUS_DOCUMENTATION = "CORRECT_STATUS_DOCUMENTATION"
    DOCUMENT_GOVERNANCE_INCIDENT = "DOCUMENT_GOVERNANCE_INCIDENT"
    REQUEST_INSTITUTIONAL_DECISION = "REQUEST_INSTITUTIONAL_DECISION"


class GovernanceCorrectionStepState(str, Enum):
    DOCUMENTED_AS_COMPLETED = "DOCUMENTED_AS_COMPLETED"
    DOCUMENTED_AS_OPEN = "DOCUMENTED_AS_OPEN"


class GovernanceDocumentationState(str, Enum):
    FULLY_DOCUMENTED = "FULLY_DOCUMENTED"
    INCOMPLETELY_DOCUMENTED = "INCOMPLETELY_DOCUMENTED"
    OPEN_EVIDENCE_GAP = "OPEN_EVIDENCE_GAP"
    HISTORICALLY_NOT_FULLY_RECONSTRUCTABLE = "HISTORICALLY_NOT_FULLY_RECONSTRUCTABLE"
    CORRECTION_SEQUENCE_DOCUMENTED = "CORRECTION_SEQUENCE_DOCUMENTED"
    INSTITUTIONAL_DECISION_OPEN = "INSTITUTIONAL_DECISION_OPEN"


class GovernanceStatementScope(str, Enum):
    DECISION_DOCUMENTED = "DECISION_DOCUMENTED"
    SCOPE_DOCUMENTED = "SCOPE_DOCUMENTED"
    REPOSITORY_STATE_DOCUMENTED = "REPOSITORY_STATE_DOCUMENTED"
    SEQUENCE_DEVIATION_DOCUMENTED = "SEQUENCE_DEVIATION_DOCUMENTED"
    EVIDENCE_GAP_DOCUMENTED = "EVIDENCE_GAP_DOCUMENTED"
    CORRECTION_SEQUENCE_DOCUMENTED = "CORRECTION_SEQUENCE_DOCUMENTED"
    HISTORICAL_TIME_UNKNOWN_DOCUMENTED = "HISTORICAL_TIME_UNKNOWN_DOCUMENTED"
    NO_TECHNICAL_IMPACT_EVIDENCED = "NO_TECHNICAL_IMPACT_EVIDENCED"


class GovernanceProvenanceArtifactClass(str, Enum):
    ADR = "ADR"
    RATIFICATION_RECORD = "RATIFICATION_RECORD"
    IMPLEMENTATION_APPROVAL_RECORD = "IMPLEMENTATION_APPROVAL_RECORD"
    COMMIT = "COMMIT"
    PUSH_EVIDENCE = "PUSH_EVIDENCE"
    TEST_ARTIFACT = "TEST_ARTIFACT"
    HANDOVER = "HANDOVER"
    GOVERNANCE_DECISION_RECORD = "GOVERNANCE_DECISION_RECORD"
    GOVERNANCE_INCIDENT_EVIDENCE = "GOVERNANCE_INCIDENT_EVIDENCE"


class GovernanceProvenanceContext(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    RATIFICATION = "RATIFICATION"
    IMPLEMENTATION_APPROVAL = "IMPLEMENTATION_APPROVAL"
    IMPLEMENTATION = "IMPLEMENTATION"
    VALIDATION = "VALIDATION"
    COMMIT = "COMMIT"
    PUSH = "PUSH"
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    INCIDENT_DOCUMENTATION = "INCIDENT_DOCUMENTATION"


class GovernanceOpenQuestionClass(str, Enum):
    ARCHITECTURE_DECISION_REQUIRED = "ARCHITECTURE_DECISION_REQUIRED"
    RATIFICATION_REQUIRED = "RATIFICATION_REQUIRED"
    IMPLEMENTATION_APPROVAL_REQUIRED = "IMPLEMENTATION_APPROVAL_REQUIRED"
    EVIDENCE_CONFIRMATION_REQUIRED = "EVIDENCE_CONFIRMATION_REQUIRED"
    CORRECTION_SEQUENCE_DECISION_REQUIRED = "CORRECTION_SEQUENCE_DECISION_REQUIRED"


class GovernanceHistoricalTimeState(str, Enum):
    UNKNOWN = "UNBEKANNT"


@dataclass(frozen=True)
class GovernanceDecisionId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "decision_id", "governance-decision-record:")


@dataclass(frozen=True)
class GovernanceIncidentId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "incident_id", "governance-incident:")


@dataclass(frozen=True)
class GovernanceProvenanceId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "provenance_id", "governance-provenance:")


@dataclass(frozen=True)
class GovernanceSubjectReference:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "subject_reference", "adr:", "package:")


@dataclass(frozen=True)
class GovernanceCanonicalArtifactReference:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "artifact_reference", "repository-artifact:")


@dataclass(frozen=True)
class GovernanceSectionReference:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "section_reference", "section:")


@dataclass(frozen=True)
class GovernanceKnownTime:
    value: datetime

    def __post_init__(self) -> None:
        _aware(self.value, "value")


@dataclass(frozen=True)
class GovernanceScopeEntry:
    scope_type: GovernanceScopeType
    artifact_reference: GovernanceCanonicalArtifactReference
    section_reference: GovernanceSectionReference

    def __post_init__(self) -> None:
        _enum(self.scope_type, GovernanceScopeType, "scope_type")
        _instance(self.artifact_reference, GovernanceCanonicalArtifactReference, "artifact_reference")
        _instance(self.section_reference, GovernanceSectionReference, "section_reference")


@dataclass(frozen=True)
class GovernanceEvidenceReference:
    evidence_type: GovernanceEvidenceType
    reference: GovernanceCanonicalArtifactReference
    statement_scopes: Tuple[GovernanceStatementScope, ...]

    def __post_init__(self) -> None:
        _enum(self.evidence_type, GovernanceEvidenceType, "evidence_type")
        _instance(self.reference, GovernanceCanonicalArtifactReference, "reference")
        _typed_nonempty_tuple(self.statement_scopes, GovernanceStatementScope, "statement_scopes")
        allowed = _EVIDENCE_SCOPE_MATRIX[self.evidence_type]
        if not set(self.statement_scopes).issubset(allowed):
            raise ValueError("evidence type cannot confirm the supplied statement scope")


@dataclass(frozen=True)
class MissingGovernanceEvidence:
    missing_type: MissingGovernanceEvidenceType
    governance_step: GovernanceStep
    unconfirmed_statement: GovernanceStatementScope
    status: MissingGovernanceEvidenceStatus
    observation_scope: GovernanceStatementScope
    closing_evidence_reference: Optional[GovernanceEvidenceReference] = None

    def __post_init__(self) -> None:
        _enum(self.missing_type, MissingGovernanceEvidenceType, "missing_type")
        _enum(self.governance_step, GovernanceStep, "governance_step")
        _enum(self.unconfirmed_statement, GovernanceStatementScope, "unconfirmed_statement")
        _enum(self.status, MissingGovernanceEvidenceStatus, "status")
        _enum(self.observation_scope, GovernanceStatementScope, "observation_scope")
        if self.status is MissingGovernanceEvidenceStatus.CLOSED_BY_REFERENCED_EVIDENCE:
            _instance(self.closing_evidence_reference, GovernanceEvidenceReference, "closing_evidence_reference")
        elif self.closing_evidence_reference is not None:
            raise ValueError("only closed missing evidence may reference closing evidence")


@dataclass(frozen=True)
class GovernanceProvenance:
    provenance_id: GovernanceProvenanceId
    artifact_class: GovernanceProvenanceArtifactClass
    context: GovernanceProvenanceContext
    repository_reference: GovernanceCanonicalArtifactReference
    source_references: Tuple[GovernanceEvidenceReference, ...]
    documented_at: GovernanceKnownTime
    statement_scopes: Tuple[GovernanceStatementScope, ...]

    def __post_init__(self) -> None:
        _instance(self.provenance_id, GovernanceProvenanceId, "provenance_id")
        _enum(self.artifact_class, GovernanceProvenanceArtifactClass, "artifact_class")
        _enum(self.context, GovernanceProvenanceContext, "context")
        _instance(self.repository_reference, GovernanceCanonicalArtifactReference, "repository_reference")
        _typed_nonempty_tuple(self.source_references, GovernanceEvidenceReference, "source_references")
        _instance(self.documented_at, GovernanceKnownTime, "documented_at")
        _typed_nonempty_tuple(self.statement_scopes, GovernanceStatementScope, "statement_scopes")
        supported = _supported_scopes(self.source_references)
        if not set(self.statement_scopes).issubset(supported):
            raise ValueError("provenance cannot extend source evidence")


@dataclass(frozen=True)
class GovernanceOpenDecisionQuestion:
    question_class: GovernanceOpenQuestionClass
    reference: GovernanceCanonicalArtifactReference
    display: Optional[str] = None

    def __post_init__(self) -> None:
        _enum(self.question_class, GovernanceOpenQuestionClass, "question_class")
        _instance(self.reference, GovernanceCanonicalArtifactReference, "reference")
        if self.display is not None:
            _non_personal_display(self.display, "display")


@dataclass(frozen=True)
class GovernanceCorrectionAction:
    step: GovernanceCorrectionStep
    state: GovernanceCorrectionStepState

    def __post_init__(self) -> None:
        _enum(self.step, GovernanceCorrectionStep, "step")
        _enum(self.state, GovernanceCorrectionStepState, "state")


@dataclass(frozen=True)
class GovernanceDecisionRecord:
    decision_id: GovernanceDecisionId
    decision_class: GovernanceDecisionClass
    subject_reference: GovernanceSubjectReference
    institutional_role: GovernanceInstitutionalRole
    decided_at: GovernanceKnownTime
    repository_documented_at: GovernanceKnownTime
    granted_scopes: Tuple[GovernanceScopeEntry, ...]
    excluded_scopes: Tuple[GovernanceScopeEntry, ...]
    evidence_references: Tuple[GovernanceEvidenceReference, ...]
    provenance: GovernanceProvenance
    documentation_state: GovernanceDocumentationState
    statement_scopes: Tuple[GovernanceStatementScope, ...]

    def __post_init__(self) -> None:
        GovernanceDecisionRecordValidator().validate(self)


GovernanceEventTime = Union[GovernanceKnownTime, GovernanceHistoricalTimeState]


@dataclass(frozen=True)
class GovernanceIncidentEvidence:
    incident_id: GovernanceIncidentId
    incident_class: GovernanceIncidentClass
    governance_step: GovernanceStep
    subject_reference: GovernanceSubjectReference
    deviation_code: GovernanceDeviationCode
    evidence_references: Tuple[GovernanceEvidenceReference, ...]
    missing_evidence: Tuple[MissingGovernanceEvidence, ...]
    event_time: GovernanceEventTime
    captured_at: GovernanceKnownTime
    repository_documented_at: GovernanceKnownTime
    impact_codes: Tuple[GovernanceImpactCode, ...]
    correction_actions: Tuple[GovernanceCorrectionAction, ...]
    documentation_state: GovernanceDocumentationState
    provenance: GovernanceProvenance
    open_decision_question: Optional[GovernanceOpenDecisionQuestion]
    statement_scopes: Tuple[GovernanceStatementScope, ...]

    def __post_init__(self) -> None:
        GovernanceIncidentEvidenceValidator().validate(self)


class GovernanceEvidencePrimitiveValidator:
    """Validate supplied evidence primitives without external reads."""

    def validate_reference(self, reference: GovernanceEvidenceReference) -> GovernanceEvidenceReference:
        _instance(reference, GovernanceEvidenceReference, "reference")
        return reference

    def validate_known_time(self, value: GovernanceKnownTime) -> GovernanceKnownTime:
        _instance(value, GovernanceKnownTime, "value")
        return value

    def validate_unknown_time(self, value: GovernanceHistoricalTimeState) -> GovernanceHistoricalTimeState:
        if value is not GovernanceHistoricalTimeState.UNKNOWN:
            raise TypeError("value must be GovernanceHistoricalTimeState.UNKNOWN")
        return value


class GovernanceRoleDecisionValidator:
    def validate(
        self,
        role: GovernanceInstitutionalRole,
        decision_class: GovernanceDecisionClass,
    ) -> None:
        _enum(role, GovernanceInstitutionalRole, "role")
        _enum(decision_class, GovernanceDecisionClass, "decision_class")
        if role not in _DECISION_ROLE_MATRIX[decision_class]:
            raise ValueError("institutional role is not allowed for decision class")


class GovernanceStepSequenceValidator:
    def validate(self, steps: Tuple[GovernanceStep, ...]) -> Tuple[GovernanceStep, ...]:
        if not isinstance(steps, tuple) or any(not isinstance(step, GovernanceStep) for step in steps):
            raise TypeError("steps must be a tuple of GovernanceStep")
        if steps != tuple(GovernanceStep):
            raise ValueError("governance steps must preserve the ratified 18-step sequence")
        return steps


class GovernanceIncidentClassificationValidator:
    def validate(
        self,
        incident_class: GovernanceIncidentClass,
        governance_step: GovernanceStep,
        deviation_code: GovernanceDeviationCode,
    ) -> None:
        _enum(incident_class, GovernanceIncidentClass, "incident_class")
        _enum(governance_step, GovernanceStep, "governance_step")
        _enum(deviation_code, GovernanceDeviationCode, "deviation_code")
        if deviation_code not in _INCIDENT_DEVIATION_MATRIX[incident_class]:
            raise ValueError("incident class and deviation code are inconsistent")
        if governance_step not in _INCIDENT_STEP_MATRIX[incident_class]:
            raise ValueError("incident class and governance step are inconsistent")


class GovernanceEvidenceValidator:
    def validate(self, reference: GovernanceEvidenceReference) -> GovernanceEvidenceReference:
        _instance(reference, GovernanceEvidenceReference, "reference")
        return reference


class MissingGovernanceEvidenceValidator:
    def validate(self, missing: MissingGovernanceEvidence) -> MissingGovernanceEvidence:
        _instance(missing, MissingGovernanceEvidence, "missing")
        return missing


class GovernanceTimeValidator:
    def validate_known(self, value: GovernanceKnownTime) -> GovernanceKnownTime:
        _instance(value, GovernanceKnownTime, "value")
        return value

    def validate_event(self, value: GovernanceEventTime) -> GovernanceEventTime:
        if not isinstance(value, GovernanceKnownTime) and value is not GovernanceHistoricalTimeState.UNKNOWN:
            raise TypeError("event time must be known timezone-aware time or UNBEKANNT")
        return value


class GovernanceProvenanceValidator:
    def validate(self, provenance: GovernanceProvenance) -> GovernanceProvenance:
        _instance(provenance, GovernanceProvenance, "provenance")
        return provenance


class GovernanceOpenDecisionQuestionValidator:
    def validate(self, question: GovernanceOpenDecisionQuestion) -> GovernanceOpenDecisionQuestion:
        _instance(question, GovernanceOpenDecisionQuestion, "question")
        return question


class GovernanceCustodyReferenceValidator:
    def validate(self, directory: str) -> str:
        if directory not in (
            GOVERNANCE_DECISION_RECORD_DIRECTORY,
            GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY,
        ):
            raise ValueError("directory is not a ratified governance custody reference")
        return directory


class GovernanceScopeValidator:
    def validate_sets(
        self,
        granted_scopes: Tuple[GovernanceScopeEntry, ...],
        excluded_scopes: Tuple[GovernanceScopeEntry, ...],
    ) -> None:
        _typed_nonempty_tuple(granted_scopes, GovernanceScopeEntry, "granted_scopes")
        _typed_nonempty_tuple(excluded_scopes, GovernanceScopeEntry, "excluded_scopes")
        if any(scope.scope_type is not GovernanceScopeType.GRANTED_SCOPE for scope in granted_scopes):
            raise ValueError("granted scopes require GRANTED_SCOPE")
        if any(scope.scope_type is not GovernanceScopeType.EXCLUDED_SCOPE for scope in excluded_scopes):
            raise ValueError("excluded scopes require EXCLUDED_SCOPE")
        granted_keys = {_scope_key(scope) for scope in granted_scopes}
        excluded_keys = {_scope_key(scope) for scope in excluded_scopes}
        if len(granted_keys) != len(granted_scopes) or len(excluded_keys) != len(excluded_scopes):
            raise ValueError("scope entries must be unique")
        if granted_keys.intersection(excluded_keys):
            raise ValueError("granted and excluded scopes must be disjoint")


class GovernanceDecisionRecordValidator:
    """Validate a supplied decision record without making a decision."""

    def validate(self, record: GovernanceDecisionRecord) -> GovernanceDecisionRecord:
        _instance(record, GovernanceDecisionRecord, "record")
        _instance(record.decision_id, GovernanceDecisionId, "decision_id")
        _enum(record.decision_class, GovernanceDecisionClass, "decision_class")
        _instance(record.subject_reference, GovernanceSubjectReference, "subject_reference")
        _enum(record.institutional_role, GovernanceInstitutionalRole, "institutional_role")
        GovernanceRoleDecisionValidator().validate(record.institutional_role, record.decision_class)
        _instance(record.decided_at, GovernanceKnownTime, "decided_at")
        _instance(record.repository_documented_at, GovernanceKnownTime, "repository_documented_at")
        if record.decided_at.value == record.repository_documented_at.value:
            raise ValueError("decision and repository documentation times must remain distinct")
        GovernanceScopeValidator().validate_sets(record.granted_scopes, record.excluded_scopes)
        _typed_nonempty_tuple(record.evidence_references, GovernanceEvidenceReference, "evidence_references")
        required_type = _DECISION_EVIDENCE_MATRIX[record.decision_class]
        if required_type not in {item.evidence_type for item in record.evidence_references}:
            raise ValueError("decision class lacks its required evidence type")
        _instance(record.provenance, GovernanceProvenance, "provenance")
        _enum(record.documentation_state, GovernanceDocumentationState, "documentation_state")
        _typed_nonempty_tuple(record.statement_scopes, GovernanceStatementScope, "statement_scopes")
        if GovernanceStatementScope.DECISION_DOCUMENTED not in record.statement_scopes:
            raise ValueError("decision record must be limited to documented decision scope")
        if GovernanceStatementScope.SCOPE_DOCUMENTED not in record.statement_scopes:
            raise ValueError("decision record must document its scope")
        return record


class GovernanceIncidentEvidenceValidator:
    """Validate supplied incident evidence without judging or correcting it."""

    def validate(self, incident: GovernanceIncidentEvidence) -> GovernanceIncidentEvidence:
        _instance(incident, GovernanceIncidentEvidence, "incident")
        _instance(incident.incident_id, GovernanceIncidentId, "incident_id")
        _enum(incident.incident_class, GovernanceIncidentClass, "incident_class")
        _enum(incident.governance_step, GovernanceStep, "governance_step")
        _instance(incident.subject_reference, GovernanceSubjectReference, "subject_reference")
        _enum(incident.deviation_code, GovernanceDeviationCode, "deviation_code")
        GovernanceIncidentClassificationValidator().validate(
            incident.incident_class,
            incident.governance_step,
            incident.deviation_code,
        )
        _typed_nonempty_tuple(incident.evidence_references, GovernanceEvidenceReference, "evidence_references")
        if not isinstance(incident.missing_evidence, tuple):
            raise TypeError("missing_evidence must be a tuple")
        for item in incident.missing_evidence:
            _instance(item, MissingGovernanceEvidence, "missing_evidence item")
        if isinstance(incident.event_time, GovernanceKnownTime):
            pass
        elif incident.event_time is not GovernanceHistoricalTimeState.UNKNOWN:
            raise TypeError("event_time must be known timezone-aware time or UNBEKANNT")
        _instance(incident.captured_at, GovernanceKnownTime, "captured_at")
        _instance(incident.repository_documented_at, GovernanceKnownTime, "repository_documented_at")
        if incident.captured_at.value == incident.repository_documented_at.value:
            raise ValueError("capture and repository documentation times must remain distinct")
        _typed_nonempty_tuple(incident.impact_codes, GovernanceImpactCode, "impact_codes")
        if not isinstance(incident.correction_actions, tuple):
            raise TypeError("correction_actions must be a tuple")
        for action in incident.correction_actions:
            _instance(action, GovernanceCorrectionAction, "correction action")
        _enum(incident.documentation_state, GovernanceDocumentationState, "documentation_state")
        _instance(incident.provenance, GovernanceProvenance, "provenance")
        if incident.open_decision_question is not None:
            _instance(incident.open_decision_question, GovernanceOpenDecisionQuestion, "open_decision_question")
        _typed_nonempty_tuple(incident.statement_scopes, GovernanceStatementScope, "statement_scopes")
        supported = _supported_scopes(incident.evidence_references)
        if not set(incident.statement_scopes).issubset(supported):
            raise ValueError("incident statement scope exceeds evidence")
        if GovernanceStatementScope.SEQUENCE_DEVIATION_DOCUMENTED not in incident.statement_scopes and GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED not in incident.statement_scopes:
            raise ValueError("incident must document a deviation or evidence gap")
        if incident.event_time is GovernanceHistoricalTimeState.UNKNOWN and GovernanceStatementScope.HISTORICAL_TIME_UNKNOWN_DOCUMENTED not in incident.statement_scopes:
            raise ValueError("unknown event time must remain explicitly documented")
        return incident


_DECISION_ROLE_MATRIX = {
    GovernanceDecisionClass.ARCHITECTURE_RATIFICATION: {GovernanceInstitutionalRole.INSTITUTION_FOUNDER},
    GovernanceDecisionClass.INSTITUTIONAL_IMPLEMENTATION_APPROVAL: {GovernanceInstitutionalRole.INSTITUTION_FOUNDER},
    GovernanceDecisionClass.COMMIT_APPROVAL: {GovernanceInstitutionalRole.CHIEF_ARCHITECT},
    GovernanceDecisionClass.PUSH_APPROVAL: {GovernanceInstitutionalRole.CHIEF_ARCHITECT},
}

_DECISION_EVIDENCE_MATRIX = {
    GovernanceDecisionClass.ARCHITECTURE_RATIFICATION: GovernanceEvidenceType.RATIFICATION_RECORD,
    GovernanceDecisionClass.INSTITUTIONAL_IMPLEMENTATION_APPROVAL: GovernanceEvidenceType.IMPLEMENTATION_APPROVAL_RECORD,
    GovernanceDecisionClass.COMMIT_APPROVAL: GovernanceEvidenceType.TEST_VALIDATION_ARTIFACT,
    GovernanceDecisionClass.PUSH_APPROVAL: GovernanceEvidenceType.COMMIT_REFERENCE,
}

_EVIDENCE_SCOPE_MATRIX = {
    GovernanceEvidenceType.ADR_ARTIFACT: {GovernanceStatementScope.SCOPE_DOCUMENTED, GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED, GovernanceStatementScope.HISTORICAL_TIME_UNKNOWN_DOCUMENTED},
    GovernanceEvidenceType.ARCHITECTURE_VALIDATION_ARTIFACT: {GovernanceStatementScope.NO_TECHNICAL_IMPACT_EVIDENCED, GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED},
    GovernanceEvidenceType.RATIFICATION_RECORD: {GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED},
    GovernanceEvidenceType.IMPLEMENTATION_APPROVAL_RECORD: {GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED},
    GovernanceEvidenceType.COMMIT_REFERENCE: {GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED, GovernanceStatementScope.SEQUENCE_DEVIATION_DOCUMENTED},
    GovernanceEvidenceType.PUSH_EVIDENCE: {GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED, GovernanceStatementScope.SEQUENCE_DEVIATION_DOCUMENTED},
    GovernanceEvidenceType.TEST_VALIDATION_ARTIFACT: {GovernanceStatementScope.NO_TECHNICAL_IMPACT_EVIDENCED},
    GovernanceEvidenceType.HANDOVER_ARTIFACT: {GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED, GovernanceStatementScope.CORRECTION_SEQUENCE_DOCUMENTED},
    GovernanceEvidenceType.REPOSITORY_STATUS_EVIDENCE: {GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED, GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED, GovernanceStatementScope.HISTORICAL_TIME_UNKNOWN_DOCUMENTED},
    GovernanceEvidenceType.GOVERNANCE_DECISION_RECORD: {GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED},
}

_INCIDENT_DEVIATION_MATRIX = {
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE: {GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR, GovernanceDeviationCode.REQUIRED_APPROVAL_ABSENT},
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL: {GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR, GovernanceDeviationCode.REQUIRED_APPROVAL_ABSENT},
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_APPROVAL_PUSH: {GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR},
    GovernanceIncidentClass.COMMIT_WITHOUT_COMMIT_APPROVAL: {GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR, GovernanceDeviationCode.REQUIRED_APPROVAL_ABSENT},
    GovernanceIncidentClass.PUSH_WITHOUT_PUSH_APPROVAL: {GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR, GovernanceDeviationCode.REQUIRED_APPROVAL_ABSENT},
    GovernanceIncidentClass.SCOPE_EXCEEDED: {GovernanceDeviationCode.APPROVED_SCOPE_EXCEEDED},
    GovernanceIncidentClass.GOVERNANCE_EVIDENCE_MISSING: {GovernanceDeviationCode.REQUIRED_EVIDENCE_ABSENT},
    GovernanceIncidentClass.STATUS_MISREPRESENTED: {GovernanceDeviationCode.DOCUMENTED_STATUS_CONTRADICTS_EVIDENCE},
    GovernanceIncidentClass.WORK_STATE_RETROACTIVELY_REINTERPRETED: {GovernanceDeviationCode.WORK_STATE_RETROACTIVELY_REINTERPRETED},
    GovernanceIncidentClass.DECISION_TIME_NOT_DOCUMENTED: {GovernanceDeviationCode.DECISION_TIME_EVIDENCE_ABSENT},
    GovernanceIncidentClass.DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED: {GovernanceDeviationCode.DECISION_AND_DOCUMENTATION_TIME_CONFLATED},
}

_INCIDENT_STEP_MATRIX = {
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE: {GovernanceStep.IMPLEMENTATION},
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL: {GovernanceStep.IMPLEMENTATION},
    GovernanceIncidentClass.IMPLEMENTATION_BEFORE_APPROVAL_PUSH: {GovernanceStep.IMPLEMENTATION},
    GovernanceIncidentClass.COMMIT_WITHOUT_COMMIT_APPROVAL: {GovernanceStep.IMPLEMENTATION_COMMIT},
    GovernanceIncidentClass.PUSH_WITHOUT_PUSH_APPROVAL: {GovernanceStep.IMPLEMENTATION_PUSH},
    GovernanceIncidentClass.SCOPE_EXCEEDED: set(GovernanceStep),
    GovernanceIncidentClass.GOVERNANCE_EVIDENCE_MISSING: set(GovernanceStep),
    GovernanceIncidentClass.STATUS_MISREPRESENTED: set(GovernanceStep),
    GovernanceIncidentClass.WORK_STATE_RETROACTIVELY_REINTERPRETED: set(GovernanceStep),
    GovernanceIncidentClass.DECISION_TIME_NOT_DOCUMENTED: {GovernanceStep.HUMAN_RATIFICATION, GovernanceStep.INSTITUTIONAL_IMPLEMENTATION_APPROVAL},
    GovernanceIncidentClass.DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED: {GovernanceStep.RATIFICATION_DOCUMENTATION, GovernanceStep.IMPLEMENTATION_APPROVAL_DOCUMENTATION},
}


def _scope_key(scope: GovernanceScopeEntry) -> Tuple[str, str]:
    return (scope.artifact_reference.value, scope.section_reference.value)


def _supported_scopes(references: Tuple[GovernanceEvidenceReference, ...]) -> set:
    scopes = set()
    for reference in references:
        scopes.update(reference.statement_scopes)
    return scopes


def _reference(value: object, name: str, *prefixes: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("{} must be a non-empty machine reference".format(name))
    if not any(value.startswith(prefix) and len(value) > len(prefix) for prefix in prefixes):
        raise ValueError("{} has an invalid reference family".format(name))
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-._:/#")
    if any(character not in allowed for character in value):
        raise ValueError("{} must be a non-personal machine reference".format(name))
    normalized = value.replace("_", "-").replace(":", "-").replace("/", "-").replace("#", "-")
    segments = set(normalized.split("-"))
    if segments.intersection({"person", "personal", "human", "name", "email", "contact", "employee", "user", "device", "account", "profile"}):
        raise ValueError("{} must not identify a natural person".format(name))


def _non_personal_display(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise ValueError("{} must be a non-empty bounded display".format(name))
    if len(value) > 240 or "@" in value:
        raise ValueError("{} must not contain personal identity data".format(name))
    lowered = value.lower()
    if any(token in lowered for token in ("email", "employee", "person name", "name:", "user id", "phone")):
        raise ValueError("{} must not contain personal identity data".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _instance(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _enum(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _typed_nonempty_tuple(value: object, expected: type, name: str) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("{} must be a non-empty tuple".format(name))
    if any(not isinstance(item, expected) for item in value):
        raise TypeError("{} contains an invalid item".format(name))
    if len(set(value)) != len(value):
        raise ValueError("{} must not contain duplicates".format(name))
