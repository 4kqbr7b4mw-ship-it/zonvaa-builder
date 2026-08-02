from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.authority import AuthorityReviewStatus
from governance.capability_invocation import InvocationOperationMode
from governance.read_only_b1_runtime import (
    ProviderOutputKind,
    ProviderTechnicalStatus,
    RuntimeExecutionStatus,
)
from governance.runtime_incident import (
    EXPECTED_INCIDENT_SEVERITY,
    READ_ONLY_B1_RUNTIME_REFERENCE,
    RuntimeIncidentEvidence,
    RuntimeIncidentPackage,
    RuntimeIncidentSeverity,
    RuntimeIncidentSnapshotStatus,
    RuntimeIncidentType,
    RuntimeIncidentValidationError,
    RuntimeIncidentValidator,
    RuntimeNoIncidentEvidence,
)
from tests.test_guardian_capability_invocation import NOW, provenance
from tests.test_read_only_b1_provider_runtime import FakeAdapter, envelope, run


INCIDENT_AT = NOW + timedelta(hours=1, milliseconds=500)


def no_incident(outcome):
    return RuntimeNoIncidentEvidence(
        no_incident_id="no-incident-b1",
        execution_reference=outcome.request.execution_id,
        provider_reference=outcome.request.provider_reference,
        runtime_reference=READ_ONLY_B1_RUNTIME_REFERENCE,
        successful_execution_declared=True,
        no_detected_deviation_declared=True,
        checked_at=INCIDENT_AT,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:no-incident",
        provenance=provenance(),
    )


def incident(outcome, incident_type, **changes):
    values = dict(
        incident_id="incident-{}".format(incident_type.value.lower()),
        execution_reference=outcome.request.execution_id,
        provider_reference=outcome.request.provider_reference,
        runtime_reference=READ_ONLY_B1_RUNTIME_REFERENCE,
        incident_type=incident_type,
        severity=EXPECTED_INCIDENT_SEVERITY[incident_type],
        occurred_at=INCIDENT_AT,
        affected_capability=outcome.request.capability,
        affected_answer_mode=outcome.request.answer_mode,
        technical_cause="Already supplied technical cause.",
        professional_cause="Already supplied professional cause.",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:incident",
        provenance=provenance(),
    )
    values.update(changes)
    return RuntimeIncidentEvidence(**values)


def package(
    execution_envelope,
    outcome,
    *,
    incident_value=None,
    no_incident_value=None,
):
    return RuntimeIncidentPackage(
        package_id="runtime-incident-package-b1",
        runtime_reference=READ_ONLY_B1_RUNTIME_REFERENCE,
        execution_envelope=execution_envelope,
        runtime_outcome=outcome,
        incident=incident_value,
        no_incident=no_incident_value,
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:incident-package",
        provenance=provenance(),
    )


def outcome_for(incident_type):
    value = envelope()
    if incident_type is RuntimeIncidentType.PROVIDER_TECHNICAL_ERROR:
        return value, run(value, FakeAdapter(status=ProviderTechnicalStatus.ERROR))
    if incident_type is RuntimeIncidentType.PROVIDER_TIMEOUT:
        return value, run(value, FakeAdapter(status=ProviderTechnicalStatus.TIMED_OUT))
    if incident_type is RuntimeIncidentType.OUTPUT_BOUNDARY_REJECTION:
        adapter = FakeAdapter(kind=ProviderOutputKind.TOOL_INSTRUCTION)
        return value, run(value, adapter)
    if incident_type is RuntimeIncidentType.INVALID_PROVIDER_RESPONSE:
        adapter = FakeAdapter()

        def invalid_response(request_value):
            adapter.calls.append(request_value)
            return object()

        adapter.invoke = invalid_response
        return value, run(value, adapter)
    if incident_type is RuntimeIncidentType.CONTROLLED_DEGRADATION:
        return value, run(value, FakeAdapter(status=ProviderTechnicalStatus.DEGRADED))
    if incident_type is RuntimeIncidentType.PRE_EXECUTION_BLOCK:
        blocked = replace(
            value,
            request=replace(
                value.request,
                operation_mode=InvocationOperationMode.READ_WRITE,
            ),
        )
        return blocked, run(blocked, FakeAdapter())
    raise AssertionError("unsupported fixture incident type")


def test_successful_runtime_has_immutable_no_incident_evidence():
    value = envelope()
    outcome = run(value, FakeAdapter())
    evidence = no_incident(outcome)
    record = package(value, outcome, no_incident_value=evidence)
    validator = RuntimeIncidentValidator()
    assert validator.validate(record) is record
    assert validator.validate(record) is record
    with pytest.raises(FrozenInstanceError):
        evidence.no_incident_id = "changed"


@pytest.mark.parametrize("incident_type", tuple(RuntimeIncidentType))
def test_each_runtime_incident_scenario_matches_supplied_runtime_outcome(incident_type):
    value, outcome = outcome_for(incident_type)
    evidence = incident(outcome, incident_type)
    record = package(value, outcome, incident_value=evidence)
    assert RuntimeIncidentValidator().validate(record) is record
    if incident_type is RuntimeIncidentType.PRE_EXECUTION_BLOCK:
        assert outcome.evidence.provider_called is False
    else:
        assert outcome.evidence.provider_called is True


def test_incident_and_no_incident_are_mutually_exclusive():
    value = envelope()
    outcome = run(value, FakeAdapter())
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(package(value, outcome))
    assert error.value.code == "EXCLUSIVE_EVIDENCE_REQUIRED"
    incident_value = incident(
        outcome_for(RuntimeIncidentType.CONTROLLED_DEGRADATION)[1],
        RuntimeIncidentType.CONTROLLED_DEGRADATION,
    )
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(
                value,
                outcome,
                incident_value=incident_value,
                no_incident_value=no_incident(outcome),
            )
        )
    assert error.value.code == "EXCLUSIVE_EVIDENCE_REQUIRED"


def test_no_incident_requires_success_and_both_explicit_declarations():
    value, failed = outcome_for(RuntimeIncidentType.PROVIDER_TECHNICAL_ERROR)
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(value, failed, no_incident_value=no_incident(failed))
        )
    assert error.value.code == "NO_INCIDENT_REQUIRES_SUCCESS"
    successful = run(value, FakeAdapter())
    incomplete = replace(
        no_incident(successful), no_detected_deviation_declared=False
    )
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(value, successful, no_incident_value=incomplete)
        )
    assert error.value.code == "NO_INCIDENT_DECLARATION_INCOMPLETE"


def test_incident_type_and_severity_must_match_runtime_outcome():
    value, outcome = outcome_for(RuntimeIncidentType.PROVIDER_TIMEOUT)
    wrong_type = incident(outcome, RuntimeIncidentType.PROVIDER_TECHNICAL_ERROR)
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(value, outcome, incident_value=wrong_type)
        )
    assert error.value.code == "INCIDENT_RESULT_INCONSISTENT"
    wrong_severity = incident(
        outcome,
        RuntimeIncidentType.PROVIDER_TIMEOUT,
        severity=RuntimeIncidentSeverity.WARNING,
    )
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(value, outcome, incident_value=wrong_severity)
        )
    assert error.value.code == "INCIDENT_SEVERITY_INCONSISTENT"


def test_runtime_execution_provider_and_capability_references_are_consistent():
    value, outcome = outcome_for(RuntimeIncidentType.PROVIDER_TIMEOUT)
    for changed in (
        incident(
            outcome,
            RuntimeIncidentType.PROVIDER_TIMEOUT,
            execution_reference="other",
        ),
        incident(
            outcome,
            RuntimeIncidentType.PROVIDER_TIMEOUT,
            provider_reference="other",
        ),
    ):
        with pytest.raises(RuntimeIncidentValidationError) as error:
            RuntimeIncidentValidator().validate(
                package(value, outcome, incident_value=changed)
            )
        assert error.value.code == "INCIDENT_REFERENCE_INCONSISTENT"


def test_runtime_object_identity_and_internal_references_are_preserved():
    value = envelope()
    outcome = run(value, FakeAdapter())
    copied_request = replace(outcome.request)
    changed_outcome = replace(outcome, request=copied_request)
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(
                value,
                changed_outcome,
                no_incident_value=no_incident(changed_outcome),
            )
        )
    assert error.value.code == "RUNTIME_OBJECT_IDENTITY_MISMATCH"
    changed_receipt = replace(outcome.receipt, result_reference="other-result")
    changed_outcome = replace(outcome, receipt=changed_receipt)
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(
                value,
                changed_outcome,
                no_incident_value=no_incident(changed_outcome),
            )
        )
    assert error.value.code == "RUNTIME_REFERENCE_INCONSISTENT"


def test_identities_runtime_reference_and_provenance_are_validated():
    value = envelope()
    outcome = run(value, FakeAdapter())
    evidence = no_incident(outcome)
    duplicate = package(
        value,
        outcome,
        no_incident_value=replace(
            evidence,
            no_incident_id=outcome.result.result_id,
        ),
    )
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(duplicate)
    assert error.value.code == "DUPLICATE_IDENTITY"
    wrong_runtime = replace(
        package(value, outcome, no_incident_value=evidence),
        runtime_reference="runtime:other",
    )
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(wrong_runtime)
    assert error.value.code == "RUNTIME_REFERENCE_INVALID"
    wrong_provenance = replace(evidence, provenance=provenance("different"))
    with pytest.raises(RuntimeIncidentValidationError) as error:
        RuntimeIncidentValidator().validate(
            package(value, outcome, no_incident_value=wrong_provenance)
        )
    assert error.value.code == "PROVENANCE_INCONSISTENT"


def test_snapshot_is_read_only_and_retains_original_objects():
    value, outcome = outcome_for(RuntimeIncidentType.PROVIDER_TIMEOUT)
    incident_value = incident(outcome, RuntimeIncidentType.PROVIDER_TIMEOUT)
    record = package(value, outcome, incident_value=incident_value)
    snapshot = RuntimeIncidentValidator().create_snapshot(
        record,
        snapshot_id="runtime-incident-snapshot-b1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:incident-snapshot",
        provenance=provenance(),
    )
    assert snapshot.execution is value.request
    assert snapshot.runtime_outcome is outcome
    assert snapshot.incident is incident_value
    assert snapshot.no_incident is None
    assert snapshot.severity is RuntimeIncidentSeverity.ERROR
    assert snapshot.status is RuntimeIncidentSnapshotStatus.INCIDENT_RECORDED
    with pytest.raises(FrozenInstanceError):
        snapshot.status = RuntimeIncidentSnapshotStatus.NO_INCIDENT_RECORDED


def test_no_incident_snapshot_has_no_severity_and_is_not_a_guarantee():
    value = envelope()
    outcome = run(value, FakeAdapter())
    evidence = no_incident(outcome)
    snapshot = RuntimeIncidentValidator().create_snapshot(
        package(value, outcome, no_incident_value=evidence),
        snapshot_id="runtime-no-incident-snapshot-b1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:no-incident-snapshot",
        provenance=provenance(),
    )
    assert snapshot.no_incident is evidence
    assert snapshot.severity is None
    assert snapshot.status is RuntimeIncidentSnapshotStatus.NO_INCIDENT_RECORDED
    for name in ("guarantee_quality", "retry", "repair", "notify", "persist"):
        assert not hasattr(snapshot, name)


def test_deterministic_repetition_changes_nothing_and_produces_equal_snapshot():
    value = envelope()
    outcome = run(value, FakeAdapter())
    record = package(value, outcome, no_incident_value=no_incident(outcome))
    validator = RuntimeIncidentValidator()
    kwargs = dict(
        snapshot_id="runtime-no-incident-snapshot-b1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:no-incident-snapshot",
        provenance=provenance(),
    )
    first = validator.create_snapshot(record, **kwargs)
    second = validator.create_snapshot(record, **kwargs)
    assert first == second
    assert first.runtime_outcome is outcome


def test_incident_contract_has_no_detection_repair_notification_or_persistence_api():
    validator = RuntimeIncidentValidator()
    for name in (
        "detect",
        "classify",
        "repair",
        "retry",
        "notify",
        "persist",
        "write_audit_log",
        "activate_workflow",
    ):
        assert not hasattr(validator, name)
