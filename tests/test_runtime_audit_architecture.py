from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.models import NormLevel
from governance.runtime_audit import (
    PROHIBITED_USER_AUDIT_SUBJECTS,
    SYSTEM_AUDIT_SUBJECTS,
    RuntimeAuditCheck,
    RuntimeAuditCompletenessLevel,
    RuntimeAuditCompletenessStatus,
    RuntimeAuditEvidence,
    RuntimeAuditEvidenceType,
    RuntimeAuditPackage,
    RuntimeAuditProfile,
    RuntimeAuditProfileChangeActor,
    RuntimeAuditResult,
    RuntimeAuditScope,
    RuntimeAuditTimeBoundary,
    RuntimeAuditValidationError,
    RuntimeAuditValidator,
)
from governance.runtime_incident import RuntimeIncidentType
from governance.runtime_observation import ObservationProfileApprovalStatus
from tests.test_read_only_b1_provider_runtime import FakeAdapter, envelope, run
from tests.test_runtime_incident_evidence import incident, no_incident, outcome_for, package as incident_package
from tests.test_runtime_observation_governance import governance


ALL_EVIDENCE = tuple(RuntimeAuditEvidenceType)
ALL_CHECKS = tuple(RuntimeAuditCheck)


def audit_provenance():
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference="knowledge/adr/ADR-0054-runtime-audit-architecture-v1.md",
        decision_reference="ADR-0054",
    )


def audit_profile(observation, **changes):
    values = dict(
        audit_profile_id="runtime-audit-profile-v1",
        version=1,
        name="Read-only B1 Runtime Audit",
        purpose="Review only supplied system evidence.",
        observation_profile_reference=observation.profile.profile_id,
        observation_profile_version=observation.profile.version,
        observation_scope_reference=observation.scope.scope_id,
        allowed_audit_subjects=SYSTEM_AUDIT_SUBJECTS,
        excluded_audit_subjects=PROHIBITED_USER_AUDIT_SUBJECTS,
        required_evidence_types=ALL_EVIDENCE,
        required_completeness_level=RuntimeAuditCompletenessLevel.COMPLETE_CHAIN_REQUIRED,
        responsibility_reference="authority:runtime-audit-governance",
        change_actor_class=RuntimeAuditProfileChangeActor.INSTITUTIONAL_GOVERNANCE,
        approval_status=ObservationProfileApprovalStatus.APPROVED,
        approval_reference="approval:runtime-audit-v1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-audit-profile-v1",
        justification="A bounded audit of supplied B1 runtime evidence.",
        previous_profile_reference=None,
        provenance=audit_provenance(),
    )
    values.update(changes)
    return RuntimeAuditProfile(**values)


def audit_scope(profile, observation, execution, *, available=ALL_EVIDENCE, **changes):
    missing = tuple(item for item in RuntimeAuditEvidenceType if item not in available)
    values = dict(
        audit_scope_id="runtime-audit-scope-v1",
        audit_profile_reference=profile.audit_profile_id,
        execution_reference=execution.request.execution_id,
        observation_scope_reference=observation.scope.scope_id,
        observed_runtime_events=observation.scope.observed_runtime_events,
        explicitly_unobserved_runtime_events=observation.scope.explicitly_unobserved_runtime_events,
        available_evidence_types=available,
        missing_evidence_types=missing,
        auditable_statements=observation.scope.observed_runtime_events,
        explicitly_not_auditable_statements=observation.scope.explicitly_unobserved_runtime_events,
        time_boundary=RuntimeAuditTimeBoundary(
            starts_at=execution.request.started_at,
            ends_at=execution.request.started_at + timedelta(hours=2),
        ),
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-audit-scope-v1",
        provenance=audit_provenance(),
    )
    values.update(changes)
    return RuntimeAuditScope(**values)


def audit_evidence(profile, scope, observation, execution, outcome, incident_record, **changes):
    missing = scope.missing_evidence_types
    result = RuntimeAuditResult.INCOMPLETE_EVIDENCE if missing else (
        RuntimeAuditResult.COMPLETE_WITH_INCIDENT
        if incident_record is not None and incident_record.incident is not None
        else RuntimeAuditResult.COMPLETE_AND_CONSISTENT
    )
    completeness = RuntimeAuditCompletenessStatus.INCOMPLETE if missing else RuntimeAuditCompletenessStatus.COMPLETE
    chain = [profile.audit_profile_id, scope.audit_scope_id, observation.governance_id, execution.request.execution_id]
    if outcome is not None:
        chain.append(outcome.evidence.evidence_id)
    if incident_record is not None:
        chain.append(incident_record.package_id)
    incident_reference = None
    if incident_record is not None:
        incident_reference = incident_record.incident.incident_id if incident_record.incident is not None else incident_record.no_incident.no_incident_id
    non_executable = set()
    if RuntimeAuditEvidenceType.RUNTIME_EXECUTION_EVIDENCE in missing:
        non_executable.add(RuntimeAuditCheck.RUNTIME_EVIDENCE_VALID)
    if RuntimeAuditEvidenceType.INCIDENT_OR_NO_INCIDENT_EVIDENCE in missing:
        non_executable.add(RuntimeAuditCheck.INCIDENT_EVIDENCE_EXCLUSIVE)
        non_executable.add(RuntimeAuditCheck.NO_INCIDENT_SCOPE_BOUND)
    passed = tuple(item for item in RuntimeAuditCheck if item not in non_executable)
    values = dict(
        audit_evidence_id="runtime-audit-evidence-v1",
        audit_profile_reference=profile.audit_profile_id,
        audit_scope_reference=scope.audit_scope_id,
        runtime_execution_reference=execution.request.execution_id,
        observation_governance_reference=observation.governance_id,
        runtime_evidence_reference=outcome.evidence.evidence_id if outcome is not None else None,
        incident_or_no_incident_evidence_reference=incident_reference,
        checked_evidence_chain=tuple(chain),
        passed_audit_checks=passed,
        failed_audit_checks=(),
        non_executable_audit_checks=tuple(
            item for item in RuntimeAuditCheck if item in non_executable
        ),
        detected_evidence_gaps=missing,
        completeness_status=completeness,
        audit_result=result,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:runtime-audit-evidence-v1",
        provenance=audit_provenance(),
    )
    values.update(changes)
    return RuntimeAuditEvidence(**values)


def complete_package(*, incident_type=None):
    observation = governance()
    if incident_type is None:
        execution = envelope()
        outcome = run(execution, FakeAdapter())
        evidence = no_incident(outcome)
        record = incident_package(execution, outcome, no_incident_value=evidence)
    else:
        execution, outcome = outcome_for(incident_type)
        record = incident_package(execution, outcome, incident_value=incident(outcome, incident_type))
    profile = audit_profile(observation)
    scope = audit_scope(profile, observation, execution)
    evidence = audit_evidence(profile, scope, observation, execution, outcome, record)
    return RuntimeAuditPackage(
        package_id="runtime-audit-package-v1",
        audit_profile=profile,
        audit_scope=scope,
        observation_governance=observation,
        execution_envelope=execution,
        runtime_outcome=outcome,
        incident_package=record,
        audit_evidence=evidence,
    )


def test_complete_no_incident_audit_is_immutable_deterministic_and_scope_bound():
    value = complete_package()
    validator = RuntimeAuditValidator()
    assert validator.validate(value) is value
    assert validator.validate(value) is value
    assert value.audit_evidence.audit_result is RuntimeAuditResult.COMPLETE_AND_CONSISTENT
    assert value.incident_package.no_incident.observation_scope_reference == value.observation_governance.scope.scope_id
    with pytest.raises(FrozenInstanceError):
        value.audit_profile.version = 2


@pytest.mark.parametrize("incident_type", tuple(RuntimeIncidentType))
def test_complete_incident_audits_retain_each_supplied_runtime_incident(incident_type):
    value = complete_package(incident_type=incident_type)
    assert RuntimeAuditValidator().validate(value) is value
    assert value.audit_evidence.audit_result is RuntimeAuditResult.COMPLETE_WITH_INCIDENT


def test_no_incident_without_or_outside_observation_binding_is_rejected():
    value = complete_package()
    no_scope = replace(value.incident_package.no_incident, observation_scope_reference="other")
    changed_record = replace(value.incident_package, no_incident=no_scope)
    with pytest.raises(RuntimeAuditValidationError) as error:
        RuntimeAuditValidator().validate(replace(value, incident_package=changed_record))
    assert error.value.code == "NO_INCIDENT_OBSERVATION_BINDING_MISMATCH"


def test_unobserved_event_cannot_be_claimed_auditable_or_incident_free():
    value = complete_package()
    unobserved = value.audit_scope.explicitly_unobserved_runtime_events[0]
    changed_scope = replace(
        value.audit_scope,
        auditable_statements=value.audit_scope.auditable_statements + (unobserved,),
        explicitly_not_auditable_statements=(),
    )
    changed_evidence = replace(value.audit_evidence, audit_scope_reference=changed_scope.audit_scope_id)
    with pytest.raises(RuntimeAuditValidationError) as error:
        RuntimeAuditValidator().validate(replace(value, audit_scope=changed_scope, audit_evidence=changed_evidence))
    assert error.value.code == "AUDIT_OUTSIDE_OBSERVATION_SCOPE"


def test_missing_runtime_or_incident_evidence_remains_visible():
    value = complete_package()
    for missing, runtime_reference in (
        ((RuntimeAuditEvidenceType.RUNTIME_EXECUTION_EVIDENCE, RuntimeAuditEvidenceType.INCIDENT_OR_NO_INCIDENT_EVIDENCE), None),
        ((RuntimeAuditEvidenceType.INCIDENT_OR_NO_INCIDENT_EVIDENCE,), value.runtime_outcome.evidence.evidence_id),
    ):
        available = tuple(item for item in RuntimeAuditEvidenceType if item not in missing)
        scope = audit_scope(value.audit_profile, value.observation_governance, value.execution_envelope, available=available)
        chain = [value.audit_profile.audit_profile_id, scope.audit_scope_id, value.observation_governance.governance_id, value.execution_envelope.request.execution_id]
        if runtime_reference is not None:
            chain.append(runtime_reference)
        evidence = audit_evidence(
            value.audit_profile,
            scope,
            value.observation_governance,
            value.execution_envelope,
            value.runtime_outcome,
            None,
            runtime_evidence_reference=runtime_reference,
            checked_evidence_chain=tuple(chain),
        )
        changed = replace(value, audit_scope=scope, incident_package=None, audit_evidence=evidence)
        assert RuntimeAuditValidator().validate(changed) is changed
        assert changed.audit_evidence.audit_result is RuntimeAuditResult.INCOMPLETE_EVIDENCE
        assert set(changed.audit_evidence.detected_evidence_gaps) == set(missing)


def test_wrong_observation_version_and_foundation_identity_are_rejected():
    value = complete_package()
    wrong_profile = replace(value.audit_profile, observation_profile_version=2)
    with pytest.raises(RuntimeAuditValidationError) as error:
        RuntimeAuditValidator().validate(replace(value, audit_profile=wrong_profile))
    assert error.value.code == "OBSERVATION_PROFILE_REFERENCE_MISMATCH"
    copied_outcome = replace(value.runtime_outcome, request=replace(value.runtime_outcome.request))
    with pytest.raises(RuntimeAuditValidationError) as error:
        RuntimeAuditValidator().validate(replace(value, runtime_outcome=copied_outcome, incident_package=None))
    assert error.value.code == "RUNTIME_OBJECT_IDENTITY_MISMATCH"


@pytest.mark.parametrize(
    "actor",
    (
        RuntimeAuditProfileChangeActor.RUNTIME,
        RuntimeAuditProfileChangeActor.MODEL,
        RuntimeAuditProfileChangeActor.PROVIDER,
        RuntimeAuditProfileChangeActor.TOOL,
    ),
)
def test_runtime_model_provider_and_tool_cannot_change_audit_profile(actor):
    value = complete_package()
    with pytest.raises(RuntimeAuditValidationError) as error:
        RuntimeAuditValidator().validate(replace(value, audit_profile=replace(value.audit_profile, change_actor_class=actor)))
    assert error.value.code == "AUDIT_PROFILE_CHANGE_PROHIBITED"


def test_user_observation_content_topics_profiles_and_statistics_are_structurally_excluded():
    value = complete_package()
    assert set(value.audit_profile.excluded_audit_subjects) == set(PROHIBITED_USER_AUDIT_SUBJECTS)
    for subject in PROHIBITED_USER_AUDIT_SUBJECTS:
        changed = replace(value.audit_profile, allowed_audit_subjects=value.audit_profile.allowed_audit_subjects + (subject,))
        with pytest.raises(RuntimeAuditValidationError) as error:
            RuntimeAuditValidator().validate(replace(value, audit_profile=changed))
        assert error.value.code == "USER_AUDIT_PROHIBITED"


def test_read_only_snapshot_preserves_all_object_identities_and_gaps():
    value = complete_package()
    snapshot = RuntimeAuditValidator().create_snapshot(value, snapshot_id="runtime-audit-snapshot-v1")
    assert snapshot.audit_profile is value.audit_profile
    assert snapshot.audit_scope is value.audit_scope
    assert snapshot.observation_governance is value.observation_governance
    assert snapshot.execution_envelope is value.execution_envelope
    assert snapshot.runtime_outcome is value.runtime_outcome
    assert snapshot.incident_package is value.incident_package
    assert snapshot.audit_evidence is value.audit_evidence


def test_audit_validator_has_no_observation_generation_persistence_metrics_or_notifications():
    validator = RuntimeAuditValidator()
    for name in (
        "observe", "detect_incident", "derive_no_incident", "generate_audit",
        "persist", "record_metric", "notify", "activate_runtime", "profile_user",
    ):
        assert not hasattr(validator, name)
