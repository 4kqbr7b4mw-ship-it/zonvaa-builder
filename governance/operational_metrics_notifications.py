"""Immutable operational metrics and notification evidence contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from governance.operational_memory import OperationalMemoryArtifactType
from governance.physical_operational_persistence import (
    PhysicalOperationalPersistencePackage,
    PhysicalOperationalPersistenceValidator,
    PhysicalPersistenceRecord,
)
from governance.runtime_audit import (
    RuntimeAuditCompletenessStatus,
    RuntimeAuditProfileChangeActor,
    RuntimeAuditTimeBoundary,
)
from governance.runtime_observation import (
    ObservationProfileApprovalStatus,
    RuntimeObservationEvent,
)


class OperationalMetricAggregationRule(str, Enum):
    PROVIDED_COUNT = "PROVIDED_COUNT"
    PROVIDED_DURATION = "PROVIDED_DURATION"
    PROVIDED_RATIO = "PROVIDED_RATIO"
    PROVIDED_BOOLEAN = "PROVIDED_BOOLEAN"
    PROVIDED_STATUS = "PROVIDED_STATUS"


class OperationalMetricUnit(str, Enum):
    COUNT = "COUNT"
    MILLISECONDS = "MILLISECONDS"
    PERCENT = "PERCENT"
    BOOLEAN = "BOOLEAN"
    STATUS = "STATUS"


class OperationalMetricUncertaintyStatus(str, Enum):
    CERTAIN = "CERTAIN"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    PROVIDED_UNCERTAINTY = "PROVIDED_UNCERTAINTY"


class OperationalNotificationSourceType(str, Enum):
    METRIC_OBSERVATION = "METRIC_OBSERVATION"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class OperationalNotificationTriggerCondition(str, Enum):
    METRIC_VALUE_PROVIDED = "METRIC_VALUE_PROVIDED"
    METRIC_INCOMPLETE = "METRIC_INCOMPLETE"
    SYSTEM_EVENT_DECLARED = "SYSTEM_EVENT_DECLARED"
    GOVERNANCE_BLOCK_DECLARED = "GOVERNANCE_BLOCK_DECLARED"


class OperationalNotificationTriggerReason(str, Enum):
    METRIC_VALUE_DECLARED = "METRIC_VALUE_DECLARED"
    METRIC_EVIDENCE_INCOMPLETE = "METRIC_EVIDENCE_INCOMPLETE"
    SYSTEM_EVENT_DECLARED = "SYSTEM_EVENT_DECLARED"
    GOVERNANCE_BLOCK_DECLARED = "GOVERNANCE_BLOCK_DECLARED"
    EXTERNAL_DECISION_DECLARED = "EXTERNAL_DECISION_DECLARED"


class OperationalNotificationSeverity(str, Enum):
    INFORMATION = "INFORMATION"
    WARNING = "WARNING"
    ERROR = "ERROR"


class OperationalNotificationRecipientCategory(str, Enum):
    OPERATIONAL_LEADERSHIP = "OPERATIONAL_LEADERSHIP"
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    TRUST_COUNCIL = "TRUST_COUNCIL"


class OperationalNotificationMessageType(str, Enum):
    OPERATIONAL_STATUS = "OPERATIONAL_STATUS"
    OPERATIONAL_WARNING = "OPERATIONAL_WARNING"
    GOVERNANCE_REVIEW_REQUIRED = "GOVERNANCE_REVIEW_REQUIRED"


class OperationalNotificationExcludedContent(str, Enum):
    USER_IDENTITY = "USER_IDENTITY"
    PERSONAL_DATA = "PERSONAL_DATA"
    CONVERSATION_CONTENT = "CONVERSATION_CONTENT"
    USER_PROFILE = "USER_PROFILE"
    USER_TOPIC = "USER_TOPIC"
    LIFE_DOMAIN = "LIFE_DOMAIN"
    GENERATED_FREE_TEXT = "GENERATED_FREE_TEXT"


class OperationalNotificationDecisionStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PREPARED = "PREPARED"
    BLOCKED = "BLOCKED"
    SUPPRESSED = "SUPPRESSED"
    DELIVERED_EXTERNALLY_DECLARED = "DELIVERED_EXTERNALLY_DECLARED"


class OperationalNotificationDeliveryStatus(str, Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    EXTERNAL_DELIVERY_DECLARED = "EXTERNAL_DELIVERY_DECLARED"


@dataclass(frozen=True)
class OperationalMetricDefinition:
    metric_definition_id: str
    version: int
    name: str
    purpose: str
    allowed_system_events: Tuple[RuntimeObservationEvent, ...]
    explicitly_excluded_events: Tuple[RuntimeObservationEvent, ...]
    input_artifact_types: Tuple[OperationalMemoryArtifactType, ...]
    aggregation_rule: OperationalMetricAggregationRule
    unit: OperationalMetricUnit
    time_boundary: RuntimeAuditTimeBoundary
    observation_profile_reference: str
    audit_profile_reference: str
    responsibility_reference: str
    approval_status: ObservationProfileApprovalStatus
    approval_reference: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    justification: str
    change_actor_class: RuntimeAuditProfileChangeActor
    previous_definition_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.metric_definition_id, "metric_definition_id"),
            (self.name, "name"),
            (self.purpose, "purpose"),
            (self.observation_profile_reference, "observation_profile_reference"),
            (self.audit_profile_reference, "audit_profile_reference"),
            (self.responsibility_reference, "responsibility_reference"),
            (self.justification, "justification"),
        ):
            _text(value, name)
        _positive(self.version, "version")
        _typed_unique_nonempty(
            self.allowed_system_events,
            RuntimeObservationEvent,
            "allowed_system_events",
        )
        _typed_unique(
            self.explicitly_excluded_events,
            RuntimeObservationEvent,
            "explicitly_excluded_events",
        )
        _typed_unique_nonempty(
            self.input_artifact_types,
            OperationalMemoryArtifactType,
            "input_artifact_types",
        )
        _enum(self.aggregation_rule, OperationalMetricAggregationRule, "aggregation_rule")
        _enum(self.unit, OperationalMetricUnit, "unit")
        if not isinstance(self.time_boundary, RuntimeAuditTimeBoundary):
            raise TypeError("time_boundary has an invalid type")
        _approval_pair(self.approval_status, self.approval_reference)
        _review_pair(self.review_status, self.review_reference)
        _enum(self.change_actor_class, RuntimeAuditProfileChangeActor, "change_actor_class")
        if self.previous_definition_reference is not None:
            _text(self.previous_definition_reference, "previous_definition_reference")
        _version_reference(self.version, self.previous_definition_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class OperationalMetricObservation:
    metric_observation_id: str
    metric_definition_reference: str
    metric_definition_version: int
    persistence_record_references: Tuple[str, ...]
    operational_memory_artifact_references: Tuple[str, ...]
    time_boundary: RuntimeAuditTimeBoundary
    provided_value: str
    unit: OperationalMetricUnit
    completeness_status: RuntimeAuditCompletenessStatus
    missing_input_artifact_types: Tuple[OperationalMemoryArtifactType, ...]
    uncertainty_status: OperationalMetricUncertaintyStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.metric_observation_id, "metric_observation_id")
        _text(self.metric_definition_reference, "metric_definition_reference")
        _positive(self.metric_definition_version, "metric_definition_version")
        _strings(self.persistence_record_references, "persistence_record_references", True)
        _strings(
            self.operational_memory_artifact_references,
            "operational_memory_artifact_references",
            True,
        )
        if not isinstance(self.time_boundary, RuntimeAuditTimeBoundary):
            raise TypeError("time_boundary has an invalid type")
        _text(self.provided_value, "provided_value")
        _enum(self.unit, OperationalMetricUnit, "unit")
        _metric_value(self.provided_value, self.unit)
        _enum(
            self.completeness_status,
            RuntimeAuditCompletenessStatus,
            "completeness_status",
        )
        _typed_unique(
            self.missing_input_artifact_types,
            OperationalMemoryArtifactType,
            "missing_input_artifact_types",
        )
        _enum(
            self.uncertainty_status,
            OperationalMetricUncertaintyStatus,
            "uncertainty_status",
        )
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class OperationalMetricPackage:
    package_id: str
    persistence_package: PhysicalOperationalPersistencePackage
    definition: OperationalMetricDefinition
    observation: OperationalMetricObservation

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(
            self.persistence_package,
            PhysicalOperationalPersistencePackage,
        ):
            raise TypeError("persistence_package has an invalid type")
        if not isinstance(self.definition, OperationalMetricDefinition):
            raise TypeError("definition has an invalid type")
        if not isinstance(self.observation, OperationalMetricObservation):
            raise TypeError("observation has an invalid type")


@dataclass(frozen=True)
class OperationalMetricSnapshot:
    snapshot_id: str
    package: OperationalMetricPackage
    definition: OperationalMetricDefinition
    observation: OperationalMetricObservation
    persistence_records: Tuple[PhysicalPersistenceRecord, ...]
    provided_value: str
    unit: OperationalMetricUnit
    time_boundary: RuntimeAuditTimeBoundary
    completeness_status: RuntimeAuditCompletenessStatus
    missing_input_artifact_types: Tuple[OperationalMemoryArtifactType, ...]
    uncertainty_status: OperationalMetricUncertaintyStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance


class OperationalMetricValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class OperationalMetricValidator:
    """Validate a supplied metric value without calculating it."""

    def validate(self, package: OperationalMetricPackage) -> OperationalMetricPackage:
        if not isinstance(package, OperationalMetricPackage):
            raise TypeError("package must be an OperationalMetricPackage")
        PhysicalOperationalPersistenceValidator().validate(package.persistence_package)
        self._definition(package)
        self._bindings(package)
        self._completeness(package)
        self._governance(package)
        return package

    def create_snapshot(
        self,
        package: OperationalMetricPackage,
        *,
        snapshot_id: str,
    ) -> OperationalMetricSnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        if snapshot_id in {
            package.package_id,
            package.definition.metric_definition_id,
            package.observation.metric_observation_id,
        }:
            _metric_invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        observation = package.observation
        return OperationalMetricSnapshot(
            snapshot_id=snapshot_id,
            package=package,
            definition=package.definition,
            observation=observation,
            persistence_records=package.persistence_package.persistence_records,
            provided_value=observation.provided_value,
            unit=observation.unit,
            time_boundary=observation.time_boundary,
            completeness_status=observation.completeness_status,
            missing_input_artifact_types=observation.missing_input_artifact_types,
            uncertainty_status=observation.uncertainty_status,
            review_status=observation.review_status,
            review_reference=observation.review_reference,
            provenance=observation.provenance,
        )

    @staticmethod
    def _definition(package: OperationalMetricPackage) -> None:
        definition = package.definition
        expected_units = {
            OperationalMetricAggregationRule.PROVIDED_COUNT:
                OperationalMetricUnit.COUNT,
            OperationalMetricAggregationRule.PROVIDED_DURATION:
                OperationalMetricUnit.MILLISECONDS,
            OperationalMetricAggregationRule.PROVIDED_RATIO:
                OperationalMetricUnit.PERCENT,
            OperationalMetricAggregationRule.PROVIDED_BOOLEAN:
                OperationalMetricUnit.BOOLEAN,
            OperationalMetricAggregationRule.PROVIDED_STATUS:
                OperationalMetricUnit.STATUS,
        }
        if definition.unit is not expected_units[definition.aggregation_rule]:
            _metric_invalid(
                "METRIC_UNIT_INVALID",
                "metric aggregation declaration and unit differ",
            )
        allowed = set(definition.allowed_system_events)
        excluded = set(definition.explicitly_excluded_events)
        if allowed & excluded or allowed | excluded != set(RuntimeObservationEvent):
            _metric_invalid(
                "METRIC_EVENT_SCOPE_INVALID",
                "metric events need a complete non-overlapping partition",
            )
        if definition.change_actor_class in {
            RuntimeAuditProfileChangeActor.RUNTIME,
            RuntimeAuditProfileChangeActor.MODEL,
            RuntimeAuditProfileChangeActor.PROVIDER,
            RuntimeAuditProfileChangeActor.TOOL,
        }:
            _metric_invalid(
                "METRIC_CHANGE_ACTOR_PROHIBITED",
                "runtime, model, provider and tool actors cannot define metrics",
            )
        audit_packages = package.persistence_package.operational_memory.audit_packages
        matches = tuple(
            audit_package
            for audit_package in audit_packages
            if audit_package.audit_profile.audit_profile_id
            == definition.audit_profile_reference
            and audit_package.observation_governance.profile.profile_id
            == definition.observation_profile_reference
        )
        if len(matches) != 1:
            _metric_invalid(
                "METRIC_GOVERNANCE_REFERENCE_INVALID",
                "metric needs exactly one bound audit and observation profile",
            )
        audit_package = matches[0]
        if not allowed.issubset(
            set(audit_package.observation_governance.scope.observed_runtime_events)
        ):
            _metric_invalid(
                "METRIC_EVENT_NOT_OBSERVED",
                "metric may use only observed system events",
            )
        if not _within(definition.time_boundary, audit_package.audit_scope.time_boundary):
            _metric_invalid(
                "METRIC_TIME_BOUNDARY_INVALID",
                "metric definition exceeds the audited time boundary",
            )

    @staticmethod
    def _bindings(package: OperationalMetricPackage) -> None:
        observation = package.observation
        definition = package.definition
        if not (
            observation.metric_definition_reference == definition.metric_definition_id
            and observation.metric_definition_version == definition.version
            and observation.unit is definition.unit
        ):
            _metric_invalid("METRIC_DEFINITION_MISMATCH", "metric references differ")
        records = package.persistence_package.persistence_records
        if set(observation.persistence_record_references) != {
            record.record_id for record in records
        }:
            _metric_invalid(
                "PERSISTENCE_BINDING_INCOMPLETE",
                "metric must bind the complete supplied persistence record set",
            )
        if set(observation.operational_memory_artifact_references) != {
            record.artifact_reference for record in records
        }:
            _metric_invalid(
                "MEMORY_BINDING_INCOMPLETE",
                "metric must bind the complete supplied memory artifact set",
            )
        if not _within(observation.time_boundary, definition.time_boundary):
            _metric_invalid(
                "METRIC_OBSERVATION_TIME_INVALID",
                "metric observation exceeds its definition boundary",
            )

    @staticmethod
    def _completeness(package: OperationalMetricPackage) -> None:
        definition = package.definition
        observation = package.observation
        memory_records = {
            binding.record.memory_id: binding.record
            for binding in package.persistence_package.operational_memory.bindings
        }
        actual_types = {
            memory_records[record.operational_memory_reference].artifact_type
            for record in package.persistence_package.persistence_records
        }
        expected_types = set(definition.input_artifact_types)
        if not actual_types.issubset(expected_types):
            _metric_invalid(
                "METRIC_INPUT_TYPE_NOT_ALLOWED",
                "persisted artifact type is not allowed by the metric",
            )
        missing = expected_types - actual_types
        if set(observation.missing_input_artifact_types) != missing:
            _metric_invalid(
                "MISSING_INPUTS_INCONSISTENT",
                "missing metric inputs must remain visible",
            )
        if observation.completeness_status is RuntimeAuditCompletenessStatus.COMPLETE:
            if missing:
                _metric_invalid(
                    "FALSE_COMPLETE_METRIC",
                    "metric cannot be complete while inputs are missing",
                )
            if observation.uncertainty_status is not OperationalMetricUncertaintyStatus.CERTAIN:
                _metric_invalid(
                    "METRIC_UNCERTAINTY_INCONSISTENT",
                    "complete metric must declare certain structural evidence",
                )
        elif not missing:
            _metric_invalid(
                "METRIC_COMPLETENESS_INCONSISTENT",
                "incomplete metric needs an explicit missing input",
            )

    @staticmethod
    def _governance(package: OperationalMetricPackage) -> None:
        definition = package.definition
        observation = package.observation
        if not (
            definition.approval_status is ObservationProfileApprovalStatus.APPROVED
            and definition.review_status is AuthorityReviewStatus.REVIEWED
            and observation.review_status is definition.review_status
            and observation.review_reference == definition.review_reference
            and observation.provenance == definition.provenance
        ):
            _metric_invalid(
                "METRIC_GOVERNANCE_INCONSISTENT",
                "metric approval, review or provenance is inconsistent",
            )


@dataclass(frozen=True)
class OperationalNotificationPolicy:
    notification_policy_id: str
    version: int
    name: str
    purpose: str
    source_type: OperationalNotificationSourceType
    metric_definition_reference: Optional[str]
    metric_definition_version: Optional[int]
    system_event: Optional[RuntimeObservationEvent]
    trigger_condition: OperationalNotificationTriggerCondition
    severity: OperationalNotificationSeverity
    recipient_category: OperationalNotificationRecipientCategory
    allowed_message_types: Tuple[OperationalNotificationMessageType, ...]
    excluded_contents: Tuple[OperationalNotificationExcludedContent, ...]
    responsibility_reference: str
    approval_status: ObservationProfileApprovalStatus
    approval_reference: Optional[str]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    justification: str
    change_actor_class: RuntimeAuditProfileChangeActor
    previous_policy_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        for value, name in (
            (self.notification_policy_id, "notification_policy_id"),
            (self.name, "name"),
            (self.purpose, "purpose"),
            (self.responsibility_reference, "responsibility_reference"),
            (self.justification, "justification"),
        ):
            _text(value, name)
        _positive(self.version, "version")
        _enum(self.source_type, OperationalNotificationSourceType, "source_type")
        if self.metric_definition_reference is not None:
            _text(self.metric_definition_reference, "metric_definition_reference")
        if self.metric_definition_version is not None:
            _positive(self.metric_definition_version, "metric_definition_version")
        if self.system_event is not None:
            _enum(self.system_event, RuntimeObservationEvent, "system_event")
        _enum(
            self.trigger_condition,
            OperationalNotificationTriggerCondition,
            "trigger_condition",
        )
        _enum(self.severity, OperationalNotificationSeverity, "severity")
        _enum(
            self.recipient_category,
            OperationalNotificationRecipientCategory,
            "recipient_category",
        )
        _typed_unique_nonempty(
            self.allowed_message_types,
            OperationalNotificationMessageType,
            "allowed_message_types",
        )
        _typed_unique_nonempty(
            self.excluded_contents,
            OperationalNotificationExcludedContent,
            "excluded_contents",
        )
        _approval_pair(self.approval_status, self.approval_reference)
        _review_pair(self.review_status, self.review_reference)
        _enum(self.change_actor_class, RuntimeAuditProfileChangeActor, "change_actor_class")
        if self.previous_policy_reference is not None:
            _text(self.previous_policy_reference, "previous_policy_reference")
        _version_reference(self.version, self.previous_policy_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class OperationalNotificationEvidence:
    notification_evidence_id: str
    policy_reference: str
    policy_version: int
    source_reference: str
    decision_status: OperationalNotificationDecisionStatus
    severity: OperationalNotificationSeverity
    trigger_reason: OperationalNotificationTriggerReason
    intended_recipient_category: OperationalNotificationRecipientCategory
    message_type: Optional[OperationalNotificationMessageType]
    provided_message_reference: Optional[str]
    delivery_status: OperationalNotificationDeliveryStatus
    decided_at: datetime
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.notification_evidence_id, "notification_evidence_id")
        _text(self.policy_reference, "policy_reference")
        _positive(self.policy_version, "policy_version")
        _text(self.source_reference, "source_reference")
        _enum(
            self.decision_status,
            OperationalNotificationDecisionStatus,
            "decision_status",
        )
        _enum(self.severity, OperationalNotificationSeverity, "severity")
        _enum(
            self.trigger_reason,
            OperationalNotificationTriggerReason,
            "trigger_reason",
        )
        _enum(
            self.intended_recipient_category,
            OperationalNotificationRecipientCategory,
            "intended_recipient_category",
        )
        if self.message_type is not None:
            _enum(self.message_type, OperationalNotificationMessageType, "message_type")
        if self.provided_message_reference is not None:
            _text(self.provided_message_reference, "provided_message_reference")
        _enum(self.delivery_status, OperationalNotificationDeliveryStatus, "delivery_status")
        _aware(self.decided_at, "decided_at")
        _review_pair(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class OperationalNotificationPackage:
    package_id: str
    persistence_package: PhysicalOperationalPersistencePackage
    policy: OperationalNotificationPolicy
    evidence: OperationalNotificationEvidence
    metric_package: Optional[OperationalMetricPackage]

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(
            self.persistence_package,
            PhysicalOperationalPersistencePackage,
        ):
            raise TypeError("persistence_package has an invalid type")
        if not isinstance(self.policy, OperationalNotificationPolicy):
            raise TypeError("policy has an invalid type")
        if not isinstance(self.evidence, OperationalNotificationEvidence):
            raise TypeError("evidence has an invalid type")
        if self.metric_package is not None and not isinstance(
            self.metric_package,
            OperationalMetricPackage,
        ):
            raise TypeError("metric_package has an invalid type")


@dataclass(frozen=True)
class OperationalNotificationSnapshot:
    snapshot_id: str
    package: OperationalNotificationPackage
    policy: OperationalNotificationPolicy
    source_reference: str
    evidence: OperationalNotificationEvidence
    decision_status: OperationalNotificationDecisionStatus
    severity: OperationalNotificationSeverity
    recipient_category: OperationalNotificationRecipientCategory
    provided_message_reference: Optional[str]
    delivery_status: OperationalNotificationDeliveryStatus
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance


class OperationalNotificationValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class OperationalNotificationValidator:
    """Validate supplied notification evidence without delivering it."""

    def validate(
        self,
        package: OperationalNotificationPackage,
    ) -> OperationalNotificationPackage:
        if not isinstance(package, OperationalNotificationPackage):
            raise TypeError("package must be an OperationalNotificationPackage")
        PhysicalOperationalPersistenceValidator().validate(package.persistence_package)
        self._policy(package)
        self._source(package)
        self._evidence(package)
        return package

    def create_snapshot(
        self,
        package: OperationalNotificationPackage,
        *,
        snapshot_id: str,
    ) -> OperationalNotificationSnapshot:
        self.validate(package)
        _text(snapshot_id, "snapshot_id")
        if snapshot_id in {
            package.package_id,
            package.policy.notification_policy_id,
            package.evidence.notification_evidence_id,
        }:
            _notification_invalid("DUPLICATE_IDENTITY", "snapshot identity must be unique")
        evidence = package.evidence
        return OperationalNotificationSnapshot(
            snapshot_id=snapshot_id,
            package=package,
            policy=package.policy,
            source_reference=evidence.source_reference,
            evidence=evidence,
            decision_status=evidence.decision_status,
            severity=evidence.severity,
            recipient_category=evidence.intended_recipient_category,
            provided_message_reference=evidence.provided_message_reference,
            delivery_status=evidence.delivery_status,
            review_status=evidence.review_status,
            review_reference=evidence.review_reference,
            provenance=evidence.provenance,
        )

    @staticmethod
    def _policy(package: OperationalNotificationPackage) -> None:
        policy = package.policy
        if policy.change_actor_class in {
            RuntimeAuditProfileChangeActor.RUNTIME,
            RuntimeAuditProfileChangeActor.MODEL,
            RuntimeAuditProfileChangeActor.PROVIDER,
            RuntimeAuditProfileChangeActor.TOOL,
        }:
            _notification_invalid(
                "NOTIFICATION_CHANGE_ACTOR_PROHIBITED",
                "runtime, model, provider and tool actors cannot define policies",
            )
        if set(policy.excluded_contents) != set(OperationalNotificationExcludedContent):
            _notification_invalid(
                "NOTIFICATION_CONTENT_BOUNDARY_INCOMPLETE",
                "all user and generated content categories must be excluded",
            )
        if not (
            policy.approval_status is ObservationProfileApprovalStatus.APPROVED
            and policy.review_status is AuthorityReviewStatus.REVIEWED
        ):
            _notification_invalid(
                "NOTIFICATION_GOVERNANCE_INCONSISTENT",
                "notification policy must be approved and reviewed",
            )
        if policy.source_type is OperationalNotificationSourceType.METRIC_OBSERVATION:
            if (
                policy.metric_definition_reference is None
                or policy.metric_definition_version is None
                or policy.system_event is not None
                or policy.trigger_condition
                not in {
                    OperationalNotificationTriggerCondition.METRIC_VALUE_PROVIDED,
                    OperationalNotificationTriggerCondition.METRIC_INCOMPLETE,
                }
            ):
                _notification_invalid(
                    "NOTIFICATION_METRIC_SOURCE_INVALID",
                    "metric policy has inconsistent source fields",
                )
        elif (
            policy.metric_definition_reference is not None
            or policy.metric_definition_version is not None
            or policy.system_event is None
            or policy.trigger_condition
            not in {
                OperationalNotificationTriggerCondition.SYSTEM_EVENT_DECLARED,
                OperationalNotificationTriggerCondition.GOVERNANCE_BLOCK_DECLARED,
            }
        ):
            _notification_invalid(
                "NOTIFICATION_EVENT_SOURCE_INVALID",
                "event policy has inconsistent source fields",
            )

    @staticmethod
    def _source(package: OperationalNotificationPackage) -> None:
        policy = package.policy
        evidence = package.evidence
        if policy.source_type is OperationalNotificationSourceType.METRIC_OBSERVATION:
            if package.metric_package is None:
                _notification_invalid(
                    "METRIC_PACKAGE_MISSING",
                    "metric notification needs a metric package",
                )
            OperationalMetricValidator().validate(package.metric_package)
            if package.metric_package.persistence_package is not package.persistence_package:
                _notification_invalid(
                    "PERSISTENCE_IDENTITY_MISMATCH",
                    "metric and notification need the same persistence package",
                )
            definition = package.metric_package.definition
            observation = package.metric_package.observation
            if not (
                policy.metric_definition_reference == definition.metric_definition_id
                and policy.metric_definition_version == definition.version
                and evidence.source_reference == observation.metric_observation_id
            ):
                _notification_invalid(
                    "NOTIFICATION_METRIC_REFERENCE_INVALID",
                    "notification metric references differ",
                )
            if (
                policy.trigger_condition
                is OperationalNotificationTriggerCondition.METRIC_INCOMPLETE
                and observation.completeness_status
                is RuntimeAuditCompletenessStatus.COMPLETE
            ):
                _notification_invalid(
                    "NOTIFICATION_TRIGGER_INCONSISTENT",
                    "incomplete trigger requires incomplete metric evidence",
                )
        else:
            if package.metric_package is not None:
                _notification_invalid(
                    "UNEXPECTED_METRIC_PACKAGE",
                    "event notification must not include a metric package",
                )
            persisted_references = {
                record.artifact_reference
                for record in package.persistence_package.persistence_records
            }
            if evidence.source_reference not in persisted_references:
                _notification_invalid(
                    "NOTIFICATION_EVENT_REFERENCE_INVALID",
                    "event notification needs a persisted artifact reference",
                )
            observed_events = set()
            for audit_package in (
                package.persistence_package.operational_memory.audit_packages
            ):
                observed_events.update(
                    audit_package.observation_governance.scope.observed_runtime_events
                )
            if policy.system_event not in observed_events:
                _notification_invalid(
                    "NOTIFICATION_EVENT_NOT_OBSERVED",
                    "notification event must be within observation governance",
                )

    @staticmethod
    def _evidence(package: OperationalNotificationPackage) -> None:
        policy = package.policy
        evidence = package.evidence
        if not (
            evidence.policy_reference == policy.notification_policy_id
            and evidence.policy_version == policy.version
            and evidence.severity is policy.severity
            and evidence.intended_recipient_category is policy.recipient_category
            and evidence.review_status is policy.review_status
            and evidence.review_reference == policy.review_reference
            and evidence.provenance == policy.provenance
        ):
            _notification_invalid(
                "NOTIFICATION_EVIDENCE_INCONSISTENT",
                "notification evidence differs from policy",
            )
        allowed_reasons = {
            OperationalNotificationTriggerCondition.METRIC_VALUE_PROVIDED: (
                OperationalNotificationTriggerReason.METRIC_VALUE_DECLARED,
                OperationalNotificationTriggerReason.EXTERNAL_DECISION_DECLARED,
            ),
            OperationalNotificationTriggerCondition.METRIC_INCOMPLETE: (
                OperationalNotificationTriggerReason.METRIC_EVIDENCE_INCOMPLETE,
            ),
            OperationalNotificationTriggerCondition.SYSTEM_EVENT_DECLARED: (
                OperationalNotificationTriggerReason.SYSTEM_EVENT_DECLARED,
            ),
            OperationalNotificationTriggerCondition.GOVERNANCE_BLOCK_DECLARED: (
                OperationalNotificationTriggerReason.GOVERNANCE_BLOCK_DECLARED,
            ),
        }
        if evidence.trigger_reason not in allowed_reasons[policy.trigger_condition]:
            _notification_invalid(
                "NOTIFICATION_TRIGGER_INCONSISTENT",
                "notification trigger condition and supplied reason differ",
            )
        needs_message = evidence.decision_status in {
            OperationalNotificationDecisionStatus.PREPARED,
            OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED,
        }
        if needs_message:
            if (
                evidence.message_type not in policy.allowed_message_types
                or evidence.provided_message_reference is None
            ):
                _notification_invalid(
                    "NOTIFICATION_MESSAGE_REFERENCE_MISSING",
                    "prepared notification needs an allowed provided message reference",
                )
        elif evidence.message_type is not None or evidence.provided_message_reference is not None:
            _notification_invalid(
                "UNEXPECTED_NOTIFICATION_MESSAGE",
                "non-prepared notification must not carry a message",
            )
        externally_declared = (
            evidence.decision_status
            is OperationalNotificationDecisionStatus.DELIVERED_EXTERNALLY_DECLARED
        )
        if externally_declared != (
            evidence.delivery_status
            is OperationalNotificationDeliveryStatus.EXTERNAL_DELIVERY_DECLARED
        ):
            _notification_invalid(
                "NOTIFICATION_DELIVERY_INCONSISTENT",
                "external delivery is only a matching supplied declaration",
            )


def _within(inner: RuntimeAuditTimeBoundary, outer: RuntimeAuditTimeBoundary) -> bool:
    return inner.starts_at >= outer.starts_at and inner.ends_at <= outer.ends_at


def _version_reference(version: int, previous_reference: Optional[str]) -> None:
    if version == 1 and previous_reference is not None:
        raise ValueError("version one must not reference a predecessor")
    if version > 1 and previous_reference is None:
        raise ValueError("later version needs a predecessor reference")


def _metric_value(value: str, unit: OperationalMetricUnit) -> None:
    if unit in {OperationalMetricUnit.COUNT, OperationalMetricUnit.MILLISECONDS}:
        if not value.isdigit():
            raise ValueError("count and duration values must be non-negative integers")
    elif unit is OperationalMetricUnit.PERCENT:
        if not value.isdigit() or not 0 <= int(value) <= 100:
            raise ValueError("percent value must be an integer from zero to one hundred")
    elif unit is OperationalMetricUnit.BOOLEAN:
        if value not in {"TRUE", "FALSE"}:
            raise ValueError("boolean value must be TRUE or FALSE")
    elif unit is OperationalMetricUnit.STATUS and value not in {
        "PRESENT",
        "ABSENT",
        "DEGRADED",
        "BLOCKED",
    }:
        raise ValueError("status value is not allowed")


def _metric_invalid(code: str, message: str) -> None:
    raise OperationalMetricValidationError(code, message)


def _notification_invalid(code: str, message: str) -> None:
    raise OperationalNotificationValidationError(code, message)


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


def _typed_unique(values, item_type, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if any(not isinstance(value, item_type) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(values, item_type, name: str) -> None:
    _typed_unique(values, item_type, name)
    if not values:
        raise ValueError("{} must not be empty".format(name))


def _strings(values, name: str, required: bool) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not values:
        raise ValueError("{} must not be empty".format(name))
    for value in values:
        _text(value, name)
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))


def _approval_pair(status, reference) -> None:
    _enum(status, ObservationProfileApprovalStatus, "approval_status")
    if status is ObservationProfileApprovalStatus.APPROVED:
        if reference is None:
            raise ValueError("approved contract needs an approval reference")
        _text(reference, "approval_reference")
    elif reference is not None:
        raise ValueError("only approved contract may reference an approval")


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
