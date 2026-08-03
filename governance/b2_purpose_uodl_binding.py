"""Immutable ADR-0063 purpose and UODL bindings without execution power."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple

from governance.b2_authorization import B2PurposeScope, B2UODLOperation
from governance.b2_data_corridor import B2DataCorridorPackage, B2DataCorridorValidator
from governance.b2_provider_authorization import (
    B2AuthorizationFoundation,
    B2AuthorizationFoundationValidator,
)
from governance.b2_provider_identity import (
    B2GovernanceDecisionId,
    B2InstitutionalSourceId,
    B2NonPersonalReferenceId,
)
from user_owned_data import StorageOperation


B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION = "1.0"


class B2PurposeComparisonRelation(str, Enum):
    IDENTICAL = "IDENTICAL"
    NARROWER = "NARROWER"


class B2PurposeBindingRule(str, Enum):
    IDENTICAL_OR_NARROWER = "IDENTICAL_OR_NARROWER"


class B2BindingObservationScope(str, Enum):
    PURPOSE_BINDING_INPUTS = "PURPOSE_BINDING_INPUTS"
    UODL_MAPPING_INPUTS = "UODL_MAPPING_INPUTS"


class B2UODLLayerRelation(str, Enum):
    CORRIDOR_TO_AUTHORIZATION_REFERENCE = "CORRIDOR_TO_AUTHORIZATION_REFERENCE"


class B2UODLPairRule(str, Enum):
    REFERENCE_TO_REFERENCE_ONLY = "REFERENCE_TO_REFERENCE_ONLY"


class B2BindingEvaluationOutcome(str, Enum):
    CONFORMING = "CONFORMING"


@dataclass(frozen=True)
class B2PurposeBindingId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "binding_id", "b2-purpose-binding:")


@dataclass(frozen=True)
class B2UODLMappingId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "mapping_id", "b2-uodl-mapping:")


@dataclass(frozen=True)
class B2CorridorPurposeReference:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "purpose_reference", "b2-corridor-purpose:")


@dataclass(frozen=True)
class B2BindingProvenance:
    institutional_source_id: B2InstitutionalSourceId
    governance_decision_id: B2GovernanceDecisionId
    reference_id: B2NonPersonalReferenceId
    created_at: datetime

    def __post_init__(self) -> None:
        _instance(self.institutional_source_id, B2InstitutionalSourceId, "institutional_source_id")
        _instance(self.governance_decision_id, B2GovernanceDecisionId, "governance_decision_id")
        _instance(self.reference_id, B2NonPersonalReferenceId, "reference_id")
        _aware(self.created_at, "created_at")


@dataclass(frozen=True)
class B2PurposeBinding:
    binding_id: B2PurposeBindingId
    corridor_reference: str
    source_purpose_reference: B2CorridorPurposeReference
    canonical_scope: B2PurposeScope
    binding_rule: B2PurposeBindingRule
    comparison_relation: B2PurposeComparisonRelation
    evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    created_at: datetime
    observation_scope: B2BindingObservationScope

    def __post_init__(self) -> None:
        _instance(self.binding_id, B2PurposeBindingId, "binding_id")
        _reference(self.corridor_reference, "corridor_reference", "b2-corridor-")
        _instance(self.source_purpose_reference, B2CorridorPurposeReference, "source_purpose_reference")
        _instance(self.canonical_scope, B2PurposeScope, "canonical_scope")
        _enum(self.binding_rule, B2PurposeBindingRule, "binding_rule")
        _enum(self.comparison_relation, B2PurposeComparisonRelation, "comparison_relation")
        _evidence_references(self.evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        _aware(self.created_at, "created_at")
        if self.created_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "binding and provenance times differ")
        if self.observation_scope is not B2BindingObservationScope.PURPOSE_BINDING_INPUTS:
            _invalid("OBSERVATION_SCOPE_INVALID", "purpose observation scope is required")


@dataclass(frozen=True)
class B2PurposeBindingEvidence:
    evidence_id: B2NonPersonalReferenceId
    binding_reference: B2PurposeBindingId
    corridor_reference: str
    canonical_scope: B2PurposeScope
    binding_rule: B2PurposeBindingRule
    comparison_relation: B2PurposeComparisonRelation
    input_evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    observed_at: datetime
    observation_scope: B2BindingObservationScope
    outcome: B2BindingEvaluationOutcome
    contract_version: str = B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _instance(self.evidence_id, B2NonPersonalReferenceId, "evidence_id")
        _instance(self.binding_reference, B2PurposeBindingId, "binding_reference")
        _reference(self.corridor_reference, "corridor_reference", "b2-corridor-")
        _instance(self.canonical_scope, B2PurposeScope, "canonical_scope")
        _enum(self.binding_rule, B2PurposeBindingRule, "binding_rule")
        _enum(self.comparison_relation, B2PurposeComparisonRelation, "comparison_relation")
        _evidence_references(self.input_evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        _aware(self.observed_at, "observed_at")
        if self.observation_scope is not B2BindingObservationScope.PURPOSE_BINDING_INPUTS:
            _invalid("OBSERVATION_SCOPE_INVALID", "purpose observation scope is required")
        if self.outcome is not B2BindingEvaluationOutcome.CONFORMING:
            _invalid("OUTCOME_INVALID", "only a conforming reconstruction is representable")
        _contract_version(self.contract_version)


class B2PurposeBindingValidator:
    """Validate a supplied binding without clocks, state, or text interpretation."""

    def validate(
        self,
        binding: B2PurposeBinding,
        corridor: B2DataCorridorPackage,
        evidence_id: B2NonPersonalReferenceId,
    ) -> B2PurposeBindingEvidence:
        _instance(binding, B2PurposeBinding, "binding")
        _instance(corridor, B2DataCorridorPackage, "corridor")
        _instance(evidence_id, B2NonPersonalReferenceId, "evidence_id")
        B2DataCorridorValidator().validate(corridor)
        if binding.corridor_reference != corridor.corridor.corridor_id:
            _invalid("CORRIDOR_REFERENCE_MISMATCH", "corridor reference differs")
        expected_purpose_reference = "b2-corridor-purpose:{}".format(
            corridor.corridor.corridor_id
        )
        if binding.source_purpose_reference.value != expected_purpose_reference:
            _invalid("PURPOSE_REFERENCE_MISMATCH", "purpose reference differs")

        corridor_scope = B2PurposeScope(
            purposes=corridor.consent_boundary.allowed_use,
            data_classes=corridor.consent_boundary.allowed_scope,
        )
        if not corridor_scope.contains(binding.canonical_scope):
            _invalid("PURPOSE_SCOPE_EXPANSION", "canonical scope is not equal or narrower")
        expected_relation = (
            B2PurposeComparisonRelation.IDENTICAL
            if corridor_scope == binding.canonical_scope
            else B2PurposeComparisonRelation.NARROWER
        )
        if binding.comparison_relation is not expected_relation:
            _invalid("PURPOSE_RELATION_MISMATCH", "declared relation differs from the half-order")

        return B2PurposeBindingEvidence(
            evidence_id=evidence_id,
            binding_reference=binding.binding_id,
            corridor_reference=binding.corridor_reference,
            canonical_scope=binding.canonical_scope,
            binding_rule=binding.binding_rule,
            comparison_relation=binding.comparison_relation,
            input_evidence_references=binding.evidence_references,
            provenance=binding.provenance,
            observed_at=binding.created_at,
            observation_scope=binding.observation_scope,
            outcome=B2BindingEvaluationOutcome.CONFORMING,
        )


@dataclass(frozen=True)
class B2UODLMapping:
    mapping_id: B2UODLMappingId
    corridor_operation: StorageOperation
    b2_uodl_operation: B2UODLOperation
    layer_relation: B2UODLLayerRelation
    pair_rule: B2UODLPairRule
    evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    created_at: datetime
    observation_scope: B2BindingObservationScope

    def __post_init__(self) -> None:
        _instance(self.mapping_id, B2UODLMappingId, "mapping_id")
        if self.corridor_operation is not StorageOperation.REFERENCE:
            _invalid("UODL_PAIR_INVALID", "corridor operation must be REFERENCE")
        if self.b2_uodl_operation is not B2UODLOperation.REFERENCE_ONLY:
            _invalid("UODL_PAIR_INVALID", "B2 UODL operation must be REFERENCE_ONLY")
        if self.layer_relation is not B2UODLLayerRelation.CORRIDOR_TO_AUTHORIZATION_REFERENCE:
            _invalid("UODL_LAYER_INVALID", "the ratified layer relation is required")
        if self.pair_rule is not B2UODLPairRule.REFERENCE_TO_REFERENCE_ONLY:
            _invalid("UODL_RULE_INVALID", "the ratified pair rule is required")
        _evidence_references(self.evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        _aware(self.created_at, "created_at")
        if self.created_at != self.provenance.created_at:
            _invalid("PROVENANCE_TIME_MISMATCH", "mapping and provenance times differ")
        if self.observation_scope is not B2BindingObservationScope.UODL_MAPPING_INPUTS:
            _invalid("OBSERVATION_SCOPE_INVALID", "UODL observation scope is required")


@dataclass(frozen=True)
class B2UODLMappingEvidence:
    evidence_id: B2NonPersonalReferenceId
    mapping_reference: B2UODLMappingId
    corridor_operation: StorageOperation
    b2_uodl_operation: B2UODLOperation
    layer_relation: B2UODLLayerRelation
    pair_rule: B2UODLPairRule
    input_evidence_references: Tuple[B2NonPersonalReferenceId, ...]
    provenance: B2BindingProvenance
    observed_at: datetime
    observation_scope: B2BindingObservationScope
    outcome: B2BindingEvaluationOutcome
    contract_version: str = B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _instance(self.evidence_id, B2NonPersonalReferenceId, "evidence_id")
        _instance(self.mapping_reference, B2UODLMappingId, "mapping_reference")
        if self.corridor_operation is not StorageOperation.REFERENCE:
            _invalid("UODL_PAIR_INVALID", "corridor operation must be REFERENCE")
        if self.b2_uodl_operation is not B2UODLOperation.REFERENCE_ONLY:
            _invalid("UODL_PAIR_INVALID", "B2 UODL operation must be REFERENCE_ONLY")
        if self.layer_relation is not B2UODLLayerRelation.CORRIDOR_TO_AUTHORIZATION_REFERENCE:
            _invalid("UODL_LAYER_INVALID", "the ratified layer relation is required")
        if self.pair_rule is not B2UODLPairRule.REFERENCE_TO_REFERENCE_ONLY:
            _invalid("UODL_RULE_INVALID", "the ratified pair rule is required")
        _evidence_references(self.input_evidence_references)
        _instance(self.provenance, B2BindingProvenance, "provenance")
        _aware(self.observed_at, "observed_at")
        if self.observation_scope is not B2BindingObservationScope.UODL_MAPPING_INPUTS:
            _invalid("OBSERVATION_SCOPE_INVALID", "UODL observation scope is required")
        if self.outcome is not B2BindingEvaluationOutcome.CONFORMING:
            _invalid("OUTCOME_INVALID", "only a conforming reconstruction is representable")
        _contract_version(self.contract_version)


class B2UODLMappingValidator:
    """Validate the single ratified typed pair without converting either type."""

    def validate(
        self, mapping: B2UODLMapping, evidence_id: B2NonPersonalReferenceId
    ) -> B2UODLMappingEvidence:
        _instance(mapping, B2UODLMapping, "mapping")
        _instance(evidence_id, B2NonPersonalReferenceId, "evidence_id")
        return B2UODLMappingEvidence(
            evidence_id=evidence_id,
            mapping_reference=mapping.mapping_id,
            corridor_operation=mapping.corridor_operation,
            b2_uodl_operation=mapping.b2_uodl_operation,
            layer_relation=mapping.layer_relation,
            pair_rule=mapping.pair_rule,
            input_evidence_references=mapping.evidence_references,
            provenance=mapping.provenance,
            observed_at=mapping.created_at,
            observation_scope=mapping.observation_scope,
            outcome=B2BindingEvaluationOutcome.CONFORMING,
        )


@dataclass(frozen=True)
class B2PurposeUODLBindingFoundation:
    foundation: B2AuthorizationFoundation
    purpose_binding: B2PurposeBinding
    purpose_evidence: B2PurposeBindingEvidence
    uodl_mapping: B2UODLMapping
    uodl_evidence: B2UODLMappingEvidence

    def __post_init__(self) -> None:
        _instance(self.foundation, B2AuthorizationFoundation, "foundation")
        _instance(self.purpose_binding, B2PurposeBinding, "purpose_binding")
        _instance(self.purpose_evidence, B2PurposeBindingEvidence, "purpose_evidence")
        _instance(self.uodl_mapping, B2UODLMapping, "uodl_mapping")
        _instance(self.uodl_evidence, B2UODLMappingEvidence, "uodl_evidence")


class B2PurposeUODLBindingFoundationValidator:
    """Validate the supplied ADR-0059 through ADR-0063 reference chain."""

    def validate(
        self, package: B2PurposeUODLBindingFoundation
    ) -> B2PurposeUODLBindingFoundation:
        _instance(package, B2PurposeUODLBindingFoundation, "package")
        B2AuthorizationFoundationValidator().validate(package.foundation)
        expected_purpose = B2PurposeBindingValidator().validate(
            package.purpose_binding,
            package.foundation.data_corridor,
            package.purpose_evidence.evidence_id,
        )
        expected_uodl = B2UODLMappingValidator().validate(
            package.uodl_mapping, package.uodl_evidence.evidence_id
        )
        if expected_purpose != package.purpose_evidence:
            _invalid("PURPOSE_EVIDENCE_MISMATCH", "purpose evidence differs")
        if expected_uodl != package.uodl_evidence:
            _invalid("UODL_EVIDENCE_MISMATCH", "UODL evidence differs")
        if package.purpose_binding.canonical_scope != package.foundation.grant.purpose_scope:
            _invalid("GRANT_PURPOSE_MISMATCH", "grant scope differs from purpose binding")
        if package.uodl_mapping.b2_uodl_operation is not package.foundation.uodl_binding.operation:
            _invalid("UODL_BINDING_MISMATCH", "authorization UODL operation differs")
        storage_operations = package.foundation.data_corridor.corridor.uodl_reference.authorization.operations
        if package.uodl_mapping.corridor_operation not in storage_operations:
            _invalid("CORRIDOR_UODL_MISMATCH", "corridor UODL operation differs")
        return package


class B2PurposeUODLBindingValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _reference(value: object, name: str, prefix: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("{} must be a non-empty machine reference".format(name))
    if not value.startswith(prefix) or len(value) == len(prefix):
        raise ValueError("{} has an invalid reference family".format(name))
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-._:")
    if any(character not in allowed for character in value):
        raise ValueError("{} must be a non-personal machine reference".format(name))
    segments = set(value.replace("_", "-").replace(":", "-").split("-"))
    if segments.intersection({"person", "personal", "human", "name", "email", "contact", "account"}):
        raise ValueError("{} must not identify a natural person".format(name))


def _evidence_references(values: object) -> None:
    if not isinstance(values, tuple):
        raise TypeError("evidence_references must be a tuple")
    if not values:
        raise ValueError("evidence_references must not be empty")
    if any(not isinstance(value, B2NonPersonalReferenceId) for value in values):
        raise TypeError("evidence_references contains an invalid value")
    if len(values) != len(set(values)):
        raise ValueError("evidence_references must not contain duplicates")


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


def _contract_version(value: object) -> None:
    if value != B2_PURPOSE_UODL_BINDING_CONTRACT_VERSION:
        raise ValueError("contract_version is invalid")


def _invalid(code: str, message: str) -> None:
    raise B2PurposeUODLBindingValidationError(code, message)
