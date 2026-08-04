from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

from governance.governance_decision_incident_evidence import (
    GOVERNANCE_DECISION_RECORD_DIRECTORY,
    GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY,
    GovernanceCanonicalArtifactReference,
    GovernanceCorrectionAction,
    GovernanceCorrectionStep,
    GovernanceCorrectionStepState,
    GovernanceCustodyReferenceValidator,
    GovernanceDecisionClass,
    GovernanceDecisionId,
    GovernanceDecisionRecord,
    GovernanceDecisionRecordValidator,
    GovernanceDeviationCode,
    GovernanceDocumentationState,
    GovernanceEvidenceReference,
    GovernanceEvidenceType,
    GovernanceEvidenceValidator,
    GovernanceHistoricalTimeState,
    GovernanceImpactCode,
    GovernanceIncidentClass,
    GovernanceIncidentEvidence,
    GovernanceIncidentEvidenceValidator,
    GovernanceIncidentClassificationValidator,
    GovernanceIncidentId,
    GovernanceInstitutionalRole,
    GovernanceKnownTime,
    GovernanceOpenDecisionQuestion,
    GovernanceOpenDecisionQuestionValidator,
    GovernanceOpenQuestionClass,
    GovernanceProvenance,
    GovernanceProvenanceArtifactClass,
    GovernanceProvenanceContext,
    GovernanceProvenanceId,
    GovernanceProvenanceValidator,
    GovernanceRoleDecisionValidator,
    GovernanceScopeEntry,
    GovernanceScopeType,
    GovernanceSectionReference,
    GovernanceStatementScope,
    GovernanceStep,
    GovernanceStepSequenceValidator,
    GovernanceSubjectReference,
    GovernanceTimeValidator,
    MissingGovernanceEvidence,
    MissingGovernanceEvidenceStatus,
    MissingGovernanceEvidenceType,
    MissingGovernanceEvidenceValidator,
)
from governance.runtime_incident import RuntimeIncidentEvidence, RuntimeIncidentType


T0 = GovernanceKnownTime(datetime(2026, 8, 3, 19, 0, tzinfo=timezone.utc))
T1 = GovernanceKnownTime(datetime(2026, 8, 3, 19, 1, tzinfo=timezone.utc))
T2 = GovernanceKnownTime(datetime(2026, 8, 3, 19, 2, tzinfo=timezone.utc))


def artifact(name="governance/ratification-adr-0064.md"):
    return GovernanceCanonicalArtifactReference("repository-artifact:" + name)


def evidence(evidence_type, scopes, name="governance/evidence.md"):
    return GovernanceEvidenceReference(evidence_type, artifact(name), scopes)


def ratification_evidence():
    return evidence(
        GovernanceEvidenceType.RATIFICATION_RECORD,
        (GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED),
        "governance/ratification-adr-0064.md",
    )


def implementation_approval_evidence():
    return evidence(
        GovernanceEvidenceType.IMPLEMENTATION_APPROVAL_RECORD,
        (GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED),
        "governance/institutional-implementation-approval-adr-0064.md",
    )


def repository_evidence(*scopes):
    return evidence(GovernanceEvidenceType.REPOSITORY_STATUS_EVIDENCE, scopes, "governance/repository-status.md")


def provenance(source, artifact_class=GovernanceProvenanceArtifactClass.GOVERNANCE_DECISION_RECORD, context=GovernanceProvenanceContext.RATIFICATION):
    return GovernanceProvenance(
        GovernanceProvenanceId("governance-provenance:adr-0064-test"),
        artifact_class,
        context,
        artifact("governance/decisions/test.md"),
        (source,),
        T1,
        source.statement_scopes,
    )


def scope(scope_type, section):
    return GovernanceScopeEntry(scope_type, artifact("knowledge/adr/adr-0064.md"), GovernanceSectionReference("section:" + section))


def decision_record(decision_class=GovernanceDecisionClass.ARCHITECTURE_RATIFICATION, role=GovernanceInstitutionalRole.INSTITUTION_FOUNDER, source=None):
    source = source or ratification_evidence()
    return GovernanceDecisionRecord(
        GovernanceDecisionId("governance-decision-record:adr-0064-test"),
        decision_class,
        GovernanceSubjectReference("adr:0064"),
        role,
        T0,
        T1,
        (scope(GovernanceScopeType.GRANTED_SCOPE, "architecture"),),
        (scope(GovernanceScopeType.EXCLUDED_SCOPE, "runtime"),),
        (source,),
        provenance(source),
        GovernanceDocumentationState.FULLY_DOCUMENTED,
        (GovernanceStatementScope.DECISION_DOCUMENTED, GovernanceStatementScope.SCOPE_DOCUMENTED),
    )


def incident_evidence(incident_class=GovernanceIncidentClass.GOVERNANCE_EVIDENCE_MISSING, deviation=GovernanceDeviationCode.REQUIRED_EVIDENCE_ABSENT, step=GovernanceStep.HUMAN_RATIFICATION, unknown=True):
    scopes = (GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED, GovernanceStatementScope.HISTORICAL_TIME_UNKNOWN_DOCUMENTED)
    source = repository_evidence(*scopes)
    missing = MissingGovernanceEvidence(
        MissingGovernanceEvidenceType.RATIFICATION_EVIDENCE_MISSING,
        GovernanceStep.HUMAN_RATIFICATION,
        GovernanceStatementScope.DECISION_DOCUMENTED,
        MissingGovernanceEvidenceStatus.HISTORICALLY_NOT_RECONSTRUCTABLE,
        GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED,
    )
    return GovernanceIncidentEvidence(
        GovernanceIncidentId("governance-incident:adr-0059-gap"),
        incident_class,
        step,
        GovernanceSubjectReference("adr:0059"),
        deviation,
        (source,),
        (missing,),
        GovernanceHistoricalTimeState.UNKNOWN if unknown else T0,
        T1,
        T2,
        (GovernanceImpactCode.GOVERNANCE_TRACEABILITY_LIMITED,),
        (GovernanceCorrectionAction(GovernanceCorrectionStep.DOCUMENT_MISSING_EVIDENCE, GovernanceCorrectionStepState.DOCUMENTED_AS_COMPLETED),),
        GovernanceDocumentationState.HISTORICALLY_NOT_FULLY_RECONSTRUCTABLE,
        provenance(source, GovernanceProvenanceArtifactClass.GOVERNANCE_INCIDENT_EVIDENCE, GovernanceProvenanceContext.INCIDENT_DOCUMENTATION),
        GovernanceOpenDecisionQuestion(GovernanceOpenQuestionClass.EVIDENCE_CONFIRMATION_REQUIRED, artifact("governance/open-questions/adr-0059.md"), "Ratification evidence remains unconfirmed"),
        scopes,
    )


def test_all_ratified_taxonomies_are_exact_and_closed():
    assert tuple(item.value for item in GovernanceDecisionClass) == ("ARCHITECTURE_RATIFICATION", "INSTITUTIONAL_IMPLEMENTATION_APPROVAL", "COMMIT_APPROVAL", "PUSH_APPROVAL")
    assert tuple(item.value for item in GovernanceInstitutionalRole) == ("INSTITUTION_FOUNDER", "CHIEF_ARCHITECT", "REVIEWER")
    assert len(GovernanceStep) == 18
    assert len(GovernanceIncidentClass) == 11
    assert len(GovernanceDeviationCode) == 8
    assert len(GovernanceEvidenceType) == 10
    assert len(MissingGovernanceEvidenceType) == 9
    assert len(MissingGovernanceEvidenceStatus) == 3
    assert len(GovernanceImpactCode) == 7
    assert len(GovernanceCorrectionStep) == 8
    assert len(GovernanceDocumentationState) == 6
    assert len(GovernanceStatementScope) == 8
    assert len(GovernanceProvenanceArtifactClass) == 9
    assert len(GovernanceProvenanceContext) == 9
    assert len(GovernanceOpenQuestionClass) == 5
    with pytest.raises(ValueError):
        GovernanceDecisionClass("OTHER")


def test_governance_steps_preserve_the_ratified_order():
    assert tuple(item.value for item in GovernanceStep) == (
        "ARCHITECTURE", "ADR_DOCUMENTATION", "ARCHITECTURE_VALIDATION", "HUMAN_RATIFICATION",
        "RATIFICATION_DOCUMENTATION", "RATIFICATION_COMMIT", "RATIFICATION_PUSH",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL", "IMPLEMENTATION_APPROVAL_DOCUMENTATION",
        "IMPLEMENTATION_APPROVAL_COMMIT", "IMPLEMENTATION_APPROVAL_PUSH", "SEPARATE_IMPLEMENTATION_ORDER",
        "IMPLEMENTATION", "TESTS_AND_REVIEW", "COMMIT_APPROVAL", "IMPLEMENTATION_COMMIT",
        "PUSH_APPROVAL", "IMPLEMENTATION_PUSH",
    )
    assert GovernanceStepSequenceValidator().validate(tuple(GovernanceStep)) == tuple(GovernanceStep)
    with pytest.raises(ValueError):
        GovernanceStepSequenceValidator().validate(tuple(GovernanceStep)[:-1])


@pytest.mark.parametrize(
    "decision_class,role,source",
    (
        (GovernanceDecisionClass.ARCHITECTURE_RATIFICATION, GovernanceInstitutionalRole.INSTITUTION_FOUNDER, ratification_evidence()),
        (GovernanceDecisionClass.INSTITUTIONAL_IMPLEMENTATION_APPROVAL, GovernanceInstitutionalRole.INSTITUTION_FOUNDER, implementation_approval_evidence()),
        (GovernanceDecisionClass.COMMIT_APPROVAL, GovernanceInstitutionalRole.CHIEF_ARCHITECT, evidence(GovernanceEvidenceType.TEST_VALIDATION_ARTIFACT, (GovernanceStatementScope.NO_TECHNICAL_IMPACT_EVIDENCED,))),
        (GovernanceDecisionClass.PUSH_APPROVAL, GovernanceInstitutionalRole.CHIEF_ARCHITECT, evidence(GovernanceEvidenceType.COMMIT_REFERENCE, (GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED,))),
    ),
)
def test_each_ratified_decision_class_has_a_valid_role_and_evidence(decision_class, role, source):
    record = decision_record(decision_class, role, source)
    assert GovernanceDecisionRecordValidator().validate(record) is record
    assert GovernanceDecisionRecordValidator().validate(record) is record


@pytest.mark.parametrize("role", tuple(GovernanceInstitutionalRole))
def test_reviewer_and_wrong_roles_cannot_make_decisions(role):
    if role is GovernanceInstitutionalRole.INSTITUTION_FOUNDER:
        return
    with pytest.raises(ValueError):
        decision_record(role=role)


def test_decision_scope_is_nonempty_disjoint_and_missing_scope_is_not_granted():
    record = decision_record()
    assert record.granted_scopes[0].section_reference.value == "section:architecture"
    assert all(item.section_reference.value != "section:missing" for item in record.granted_scopes)
    with pytest.raises(ValueError):
        replace(record, excluded_scopes=(scope(GovernanceScopeType.EXCLUDED_SCOPE, "architecture"),))
    with pytest.raises(ValueError):
        replace(record, granted_scopes=())
    with pytest.raises(ValueError):
        replace(record, excluded_scopes=())


def test_decision_times_are_aware_and_separate():
    record = decision_record()
    with pytest.raises(ValueError):
        replace(record, repository_documented_at=record.decided_at)
    with pytest.raises(ValueError):
        GovernanceKnownTime(datetime(2026, 8, 3, 19, 0))


def test_decision_evidence_and_provenance_cannot_substitute_each_other():
    record = decision_record()
    wrong = repository_evidence(GovernanceStatementScope.REPOSITORY_STATE_DOCUMENTED)
    with pytest.raises(ValueError):
        replace(record, evidence_references=(wrong,))
    with pytest.raises(ValueError):
        GovernanceProvenance(record.provenance.provenance_id, record.provenance.artifact_class, record.provenance.context, record.provenance.repository_reference, (wrong,), T1, (GovernanceStatementScope.DECISION_DOCUMENTED,))


def test_valid_incident_with_unknown_historical_time_is_deterministic_and_immutable():
    incident = incident_evidence()
    assert GovernanceIncidentEvidenceValidator().validate(incident) is incident
    assert GovernanceIncidentEvidenceValidator().validate(incident) is incident
    assert incident.event_time is GovernanceHistoricalTimeState.UNKNOWN
    with pytest.raises(FrozenInstanceError):
        incident.event_time = T0


def test_implementation_before_approval_push_is_valid_with_consistent_relation():
    source = evidence(GovernanceEvidenceType.COMMIT_REFERENCE, (GovernanceStatementScope.SEQUENCE_DEVIATION_DOCUMENTED,))
    incident = incident_evidence()
    incident = replace(
        incident,
        incident_class=GovernanceIncidentClass.IMPLEMENTATION_BEFORE_APPROVAL_PUSH,
        governance_step=GovernanceStep.IMPLEMENTATION,
        deviation_code=GovernanceDeviationCode.STEP_OCCURRED_BEFORE_REQUIRED_PREDECESSOR,
        evidence_references=(source,),
        missing_evidence=(),
        event_time=T0,
        provenance=provenance(source, GovernanceProvenanceArtifactClass.GOVERNANCE_INCIDENT_EVIDENCE, GovernanceProvenanceContext.INCIDENT_DOCUMENTATION),
        statement_scopes=(GovernanceStatementScope.SEQUENCE_DEVIATION_DOCUMENTED,),
    )
    assert GovernanceIncidentEvidenceValidator().validate(incident) is incident


def test_incident_rejects_inconsistent_class_deviation_and_step():
    incident = incident_evidence()
    with pytest.raises(ValueError):
        replace(incident, deviation_code=GovernanceDeviationCode.APPROVED_SCOPE_EXCEEDED)
    with pytest.raises(ValueError):
        replace(incident, incident_class=GovernanceIncidentClass.COMMIT_WITHOUT_COMMIT_APPROVAL)


def test_unknown_event_time_cannot_be_silently_replaced_or_undocumented():
    incident = incident_evidence()
    with pytest.raises(ValueError):
        replace(incident, statement_scopes=(GovernanceStatementScope.EVIDENCE_GAP_DOCUMENTED,))
    assert incident.event_time is not incident.repository_documented_at


def test_missing_evidence_closure_requires_reference_but_never_removes_incident():
    missing = incident_evidence().missing_evidence[0]
    with pytest.raises(TypeError):
        replace(missing, status=MissingGovernanceEvidenceStatus.CLOSED_BY_REFERENCED_EVIDENCE)
    closing = ratification_evidence()
    closed = replace(missing, status=MissingGovernanceEvidenceStatus.CLOSED_BY_REFERENCED_EVIDENCE, closing_evidence_reference=closing)
    incident = replace(incident_evidence(), missing_evidence=(closed,))
    assert incident.incident_class is GovernanceIncidentClass.GOVERNANCE_EVIDENCE_MISSING


def test_evidence_type_cannot_claim_more_than_its_ratified_observation_scope():
    with pytest.raises(ValueError):
        evidence(GovernanceEvidenceType.COMMIT_REFERENCE, (GovernanceStatementScope.DECISION_DOCUMENTED,))
    with pytest.raises(ValueError):
        evidence(GovernanceEvidenceType.HANDOVER_ARTIFACT, (GovernanceStatementScope.DECISION_DOCUMENTED,))
    with pytest.raises(ValueError):
        evidence(GovernanceEvidenceType.REPOSITORY_STATUS_EVIDENCE, (GovernanceStatementScope.DECISION_DOCUMENTED,))


@pytest.mark.parametrize(
    "value",
    (
        "repository-artifact:employee-profile",
        "repository-artifact:person-name",
        "repository-artifact:user-account",
        "repository-artifact:Email",
    ),
)
def test_personal_or_free_identity_references_are_rejected(value):
    with pytest.raises(ValueError):
        GovernanceCanonicalArtifactReference(value)


@pytest.mark.parametrize("display", ("name: Jane", "employee profile", "mail@example.org", "user id 123"))
def test_open_question_display_cannot_carry_personal_identity(display):
    with pytest.raises(ValueError):
        GovernanceOpenDecisionQuestion(GovernanceOpenQuestionClass.EVIDENCE_CONFIRMATION_REQUIRED, artifact(), display)


def test_contracts_have_no_power_person_runtime_or_status_effect_fields():
    forbidden = {"person", "name", "email", "employee_id", "profile", "sanction", "blocked", "authorized", "permission", "token", "session", "cache", "runtime", "observation", "revoked", "severity", "risk_score"}
    for contract in (GovernanceDecisionRecord, GovernanceIncidentEvidence, GovernanceProvenance, GovernanceScopeEntry, MissingGovernanceEvidence):
        assert not {field.name for field in fields(contract)}.intersection(forbidden)


def test_governance_incident_is_not_runtime_incident_observation_or_memory():
    assert not issubclass(GovernanceIncidentClass, RuntimeIncidentType)
    assert GovernanceIncidentEvidence is not RuntimeIncidentEvidence
    source = inspect.getsource(GovernanceIncidentEvidenceValidator).lower()
    for forbidden in ("runtime", "observation", "audit", "memory", "metrics", "notification", "monitor", "persist"):
        assert forbidden not in source


def test_validators_have_no_clock_repository_git_or_external_state_source():
    source = (inspect.getsource(GovernanceDecisionRecordValidator) + inspect.getsource(GovernanceIncidentEvidenceValidator)).lower()
    for forbidden in ("datetime.now", "time.time", "subprocess", "git ", "open(", "requests", "cache", "pathlib", "os."):
        assert forbidden not in source


def test_canonical_directories_are_documentation_locations_only():
    assert GOVERNANCE_DECISION_RECORD_DIRECTORY == "governance/decisions/"
    assert GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY == "governance/incidents/"
    validator = GovernanceCustodyReferenceValidator()
    assert validator.validate(GOVERNANCE_DECISION_RECORD_DIRECTORY) == GOVERNANCE_DECISION_RECORD_DIRECTORY
    assert validator.validate(GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY) == GOVERNANCE_INCIDENT_EVIDENCE_DIRECTORY
    with pytest.raises(ValueError):
        validator.validate("runtime/incidents/")


def test_specialized_validators_only_confirm_supplied_typed_objects():
    record = decision_record()
    incident = incident_evidence()
    GovernanceRoleDecisionValidator().validate(record.institutional_role, record.decision_class)
    GovernanceIncidentClassificationValidator().validate(incident.incident_class, incident.governance_step, incident.deviation_code)
    assert GovernanceEvidenceValidator().validate(record.evidence_references[0]) is record.evidence_references[0]
    assert MissingGovernanceEvidenceValidator().validate(incident.missing_evidence[0]) is incident.missing_evidence[0]
    assert GovernanceTimeValidator().validate_known(record.decided_at) is record.decided_at
    assert GovernanceTimeValidator().validate_event(incident.event_time) is GovernanceHistoricalTimeState.UNKNOWN
    assert GovernanceProvenanceValidator().validate(record.provenance) is record.provenance
    assert GovernanceOpenDecisionQuestionValidator().validate(incident.open_decision_question) is incident.open_decision_question
