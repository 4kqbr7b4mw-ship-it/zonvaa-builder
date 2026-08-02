from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.models import NormLevel
from governance.operational_memory import OperationalMemoryArtifactType
from governance.operational_metrics_notifications import (
    OperationalMetricAggregationRule,
    OperationalMetricDefinition,
    OperationalMetricObservation,
    OperationalMetricPackage,
    OperationalMetricUnit,
    OperationalMetricUncertaintyStatus,
    OperationalMetricValidationError,
    OperationalMetricValidator,
    OperationalNotificationDecisionStatus,
    OperationalNotificationDeliveryStatus,
    OperationalNotificationEvidence,
    OperationalNotificationExcludedContent,
    OperationalNotificationMessageType,
    OperationalNotificationPackage,
    OperationalNotificationPolicy,
    OperationalNotificationRecipientCategory,
    OperationalNotificationSeverity,
    OperationalNotificationSourceType,
    OperationalNotificationTriggerCondition,
    OperationalNotificationTriggerReason,
    OperationalNotificationValidationError,
    OperationalNotificationValidator,
)
from governance.runtime_audit import (
    RuntimeAuditCompletenessStatus,
    RuntimeAuditProfileChangeActor,
)
from governance.runtime_observation import (
    ObservationProfileApprovalStatus,
    RuntimeObservationEvent,
)
from tests.test_guardian_capability_invocation import NOW
from tests.test_physical_operational_persistence import persistence_package


DECIDED_AT = NOW + timedelta(hours=7)


def provenance():
    return AuthorityProvenance(
        norm_level=NormLevel.C2_GOVERNANCE_CHARTER,
        source_reference=(
            "knowledge/adr/ADR-0057-operational-metrics-notifications-v1.md"
        ),
        decision_reference="ADR-0057",
    )


def metric_definition(*, incomplete=False, **changes):
    persistence = persistence_package()
    audit_package = persistence.operational_memory.audit_packages[0]
    allowed = (RuntimeObservationEvent.EXECUTION_REQUEST_VALIDATED,)
    values = dict(
        metric_definition_id="operational-metric-definition-v1",
        version=1,
        name="Validated execution evidence presence",
        purpose="Document a supplied technical evidence count.",
        allowed_system_events=allowed,
        explicitly_excluded_events=tuple(
            event for event in RuntimeObservationEvent if event not in allowed
        ),
        input_artifact_types=(OperationalMemoryArtifactType.RUNTIME_EVIDENCE,)
        + ((OperationalMemoryArtifactType.AUDIT_EVIDENCE,) if incomplete else ()),
        aggregation_rule=OperationalMetricAggregationRule.PROVIDED_COUNT,
        unit=OperationalMetricUnit.COUNT,
        time_boundary=audit_package.audit_scope.time_boundary,
        observation_profile_reference=(
            audit_package.observation_governance.profile.profile_id
        ),
        audit_profile_reference=audit_package.audit_profile.audit_profile_id,
        responsibility_reference="authority:operational-metrics-governance",
        approval_status=ObservationProfileApprovalStatus.APPROVED,
        approval_reference="approval:operational-metric-v1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:operational-metric-v1",
        justification="Only persisted technical runtime evidence is in scope.",
        change_actor_class=RuntimeAuditProfileChangeActor.HUMAN_GOVERNANCE,
        previous_definition_reference=None,
        provenance=provenance(),
    )
    values.update(changes)
    return persistence, OperationalMetricDefinition(**values)


def metric_package(*, incomplete=False, **observation_changes):
    persistence, definition = metric_definition(incomplete=incomplete)
    record = persistence.persistence_records[0]
    values = dict(
        metric_observation_id="operational-metric-observation-v1",
        metric_definition_reference=definition.metric_definition_id,
        metric_definition_version=definition.version,
        persistence_record_references=(record.record_id,),
        operational_memory_artifact_references=(record.artifact_reference,),
        time_boundary=definition.time_boundary,
        provided_value="1",
        unit=definition.unit,
        completeness_status=(
            RuntimeAuditCompletenessStatus.INCOMPLETE
            if incomplete
            else RuntimeAuditCompletenessStatus.COMPLETE
        ),
        missing_input_artifact_types=(
            (OperationalMemoryArtifactType.AUDIT_EVIDENCE,) if incomplete else ()
        ),
        uncertainty_status=(
            OperationalMetricUncertaintyStatus.INCOMPLETE_EVIDENCE
            if incomplete
            else OperationalMetricUncertaintyStatus.CERTAIN
        ),
        review_status=definition.review_status,
        review_reference=definition.review_reference,
        provenance=definition.provenance,
    )
    values.update(observation_changes)
    return OperationalMetricPackage(
        package_id="operational-metric-package-v1",
        persistence_package=persistence,
        definition=definition,
        observation=OperationalMetricObservation(**values),
    )


def notification_policy(metric, *, source_type=None, **changes):
    source_type = source_type or OperationalNotificationSourceType.METRIC_OBSERVATION
    values = dict(
        notification_policy_id="operational-notification-policy-v1",
        version=1,
        name="Operational evidence status notice",
        purpose="Document a supplied operational notification decision.",
        source_type=source_type,
        metric_definition_reference=(
            metric.definition.metric_definition_id
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else None
        ),
        metric_definition_version=(
            metric.definition.version
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else None
        ),
        system_event=(
            None
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else RuntimeObservationEvent.EXECUTION_REQUEST_VALIDATED
        ),
        trigger_condition=(
            OperationalNotificationTriggerCondition.METRIC_VALUE_PROVIDED
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else OperationalNotificationTriggerCondition.SYSTEM_EVENT_DECLARED
        ),
        severity=OperationalNotificationSeverity.INFORMATION,
        recipient_category=(
            OperationalNotificationRecipientCategory.OPERATIONAL_LEADERSHIP
        ),
        allowed_message_types=(
            OperationalNotificationMessageType.OPERATIONAL_STATUS,
        ),
        excluded_contents=tuple(OperationalNotificationExcludedContent),
        responsibility_reference="authority:operational-notification-governance",
        approval_status=ObservationProfileApprovalStatus.APPROVED,
        approval_reference="approval:operational-notification-v1",
        review_status=AuthorityReviewStatus.REVIEWED,
        review_reference="review:operational-notification-v1",
        justification="Only a supplied technical operations reference is permitted.",
        change_actor_class=RuntimeAuditProfileChangeActor.HUMAN_GOVERNANCE,
        previous_policy_reference=None,
        provenance=provenance(),
    )
    values.update(changes)
    return OperationalNotificationPolicy(**values)


def notification_package(
    status=OperationalNotificationDecisionStatus.PREPARED,
    *,
    source_type=OperationalNotificationSourceType.METRIC_OBSERVATION,
):
    metric = metric_package()
    policy = notification_policy(metric, source_type=source_type)
    has_message = status in {
        OperationalNotificationDecisionStatus.PREPARED,
        OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED,
    }
    evidence = OperationalNotificationEvidence(
        notification_evidence_id="operational-notification-evidence-v1",
        policy_reference=policy.notification_policy_id,
        policy_version=policy.version,
        source_reference=(
            metric.observation.metric_observation_id
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else metric.persistence_package.persistence_records[0].artifact_reference
        ),
        decision_status=status,
        severity=policy.severity,
        trigger_reason=(
            OperationalNotificationTriggerReason.METRIC_VALUE_DECLARED
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else OperationalNotificationTriggerReason.SYSTEM_EVENT_DECLARED
        ),
        intended_recipient_category=policy.recipient_category,
        message_type=(
            OperationalNotificationMessageType.OPERATIONAL_STATUS
            if has_message
            else None
        ),
        provided_message_reference=(
            "provided-message:operational-status-v1" if has_message else None
        ),
        delivery_status=(
            OperationalNotificationDeliveryStatus.EXTERNAL_DELIVERY_DECLARED
            if status
            is OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED
            else OperationalNotificationDeliveryStatus.NOT_ATTEMPTED
        ),
        decided_at=DECIDED_AT,
        review_status=policy.review_status,
        review_reference=policy.review_reference,
        provenance=policy.provenance,
    )
    return OperationalNotificationPackage(
        package_id="operational-notification-package-v1",
        persistence_package=metric.persistence_package,
        policy=policy,
        evidence=evidence,
        metric_package=(
            metric
            if source_type is OperationalNotificationSourceType.METRIC_OBSERVATION
            else None
        ),
    )


def test_valid_metric_is_immutable_deterministic_and_not_calculated():
    package = metric_package()
    validator = OperationalMetricValidator()
    assert validator.validate(package) is package
    assert validator.validate(package) is package
    assert package.observation.provided_value == "1"
    assert not hasattr(validator, "calculate")
    with pytest.raises(FrozenInstanceError):
        package.observation.provided_value = "2"


def test_missing_inputs_remain_visible_and_false_complete_is_rejected():
    package = metric_package(incomplete=True)
    assert OperationalMetricValidator().validate(package) is package
    false_complete = replace(
        package,
        observation=replace(
            package.observation,
            completeness_status=RuntimeAuditCompletenessStatus.COMPLETE,
            uncertainty_status=OperationalMetricUncertaintyStatus.CERTAIN,
        ),
    )
    with pytest.raises(OperationalMetricValidationError) as error:
        OperationalMetricValidator().validate(false_complete)
    assert error.value.code == "FALSE_COMPLETE_METRIC"


def test_metric_unit_must_match_the_closed_aggregation_declaration():
    package = metric_package()
    with pytest.raises(OperationalMetricValidationError) as error:
        OperationalMetricValidator().validate(
            replace(
                package,
                definition=replace(package.definition, unit=OperationalMetricUnit.PERCENT),
                observation=replace(package.observation, unit=OperationalMetricUnit.PERCENT),
            )
        )
    assert error.value.code == "METRIC_UNIT_INVALID"


def test_metric_rejects_user_content_frequency_topic_domain_and_profile_inputs():
    persistence, definition = metric_definition()
    assert persistence is not None
    for value in (
        "USER_IDENTITY",
        "PER_USER_FREQUENCY",
        "CONVERSATION_TOPIC",
        "LIFE_DOMAIN",
        "USER_PROFILE",
    ):
        with pytest.raises(TypeError):
            replace(definition, allowed_system_events=(value,))
    package = metric_package()
    with pytest.raises(ValueError, match="non-negative integers"):
        replace(package.observation, provided_value="user-topic:family-care")


@pytest.mark.parametrize(
    "actor",
    (
        RuntimeAuditProfileChangeActor.RUNTIME,
        RuntimeAuditProfileChangeActor.MODEL,
        RuntimeAuditProfileChangeActor.PROVIDER,
        RuntimeAuditProfileChangeActor.TOOL,
    ),
)
def test_runtime_model_provider_or_tool_cannot_define_metric(actor):
    package = metric_package()
    with pytest.raises(OperationalMetricValidationError) as error:
        OperationalMetricValidator().validate(
            replace(package, definition=replace(package.definition, change_actor_class=actor))
        )
    assert error.value.code == "METRIC_CHANGE_ACTOR_PROHIBITED"


def test_metric_snapshot_preserves_all_original_objects():
    package = metric_package()
    snapshot = OperationalMetricValidator().create_snapshot(
        package,
        snapshot_id="operational-metric-snapshot-v1",
    )
    assert snapshot.package is package
    assert snapshot.definition is package.definition
    assert snapshot.observation is package.observation
    assert snapshot.persistence_records is package.persistence_package.persistence_records


@pytest.mark.parametrize(
    "status",
    (
        OperationalNotificationDecisionStatus.PREPARED,
        OperationalNotificationDecisionStatus.NOT_REQUIRED,
        OperationalNotificationDecisionStatus.BLOCKED,
        OperationalNotificationDecisionStatus.SUPPRESSED,
        OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED,
    ),
)
def test_each_notification_status_is_declarative_and_valid(status):
    package = notification_package(status)
    validator = OperationalNotificationValidator()
    assert validator.validate(package) is package
    assert validator.validate(package) is package


def test_valid_notification_can_reference_an_observed_persisted_event():
    package = notification_package(
        OperationalNotificationDecisionStatus.NOT_REQUIRED,
        source_type=OperationalNotificationSourceType.SYSTEM_EVENT,
    )
    assert OperationalNotificationValidator().validate(package) is package


def test_external_delivery_is_only_a_supplied_matching_declaration():
    package = notification_package(
        OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED
    )
    assert OperationalNotificationValidator().validate(package) is package
    with pytest.raises(OperationalNotificationValidationError) as error:
        OperationalNotificationValidator().validate(
            replace(
                package,
                evidence=replace(
                    package.evidence,
                    delivery_status=OperationalNotificationDeliveryStatus.NOT_ATTEMPTED,
                ),
            )
        )
    assert error.value.code == "NOTIFICATION_DELIVERY_INCONSISTENT"


def test_end_user_generated_text_and_personal_content_are_unrepresentable():
    package = notification_package()
    for field, value in (
        ("recipient_category", "END_USER"),
        ("allowed_message_types", ("GENERATED_TEXT",)),
        ("excluded_contents", ("PERSONAL_MESSAGE",)),
    ):
        with pytest.raises(TypeError):
            replace(package.policy, **{field: value})


@pytest.mark.parametrize(
    "actor",
    (
        RuntimeAuditProfileChangeActor.RUNTIME,
        RuntimeAuditProfileChangeActor.MODEL,
        RuntimeAuditProfileChangeActor.PROVIDER,
        RuntimeAuditProfileChangeActor.TOOL,
    ),
)
def test_runtime_model_provider_or_tool_cannot_define_notification_policy(actor):
    package = notification_package()
    with pytest.raises(OperationalNotificationValidationError) as error:
        OperationalNotificationValidator().validate(
            replace(package, policy=replace(package.policy, change_actor_class=actor))
        )
    assert error.value.code == "NOTIFICATION_CHANGE_ACTOR_PROHIBITED"


def test_notification_snapshot_is_read_only_and_preserves_identity():
    package = notification_package()
    snapshot = OperationalNotificationValidator().create_snapshot(
        package,
        snapshot_id="operational-notification-snapshot-v1",
    )
    assert snapshot.package is package
    assert snapshot.policy is package.policy
    assert snapshot.evidence is package.evidence
    with pytest.raises(FrozenInstanceError):
        snapshot.decision_status = OperationalNotificationDecisionStatus.BLOCKED


def test_no_delivery_escalation_incident_persistence_runtime_or_ui_api_exists():
    validators = (OperationalMetricValidator(), OperationalNotificationValidator())
    for validator in validators:
        for name in (
            "calculate",
            "persist",
            "detect_incident",
            "escalate",
            "deliver",
            "send_email",
            "send_sms",
            "send_push",
            "send_webhook",
            "activate_runtime",
            "activate_b2",
            "activate_b3",
            "render_ui",
        ):
            assert not hasattr(validator, name)
