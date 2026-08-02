"""Immutable B2 data-corridor governance contracts without data movement."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Type

from artifact_contract import ArtifactAuthorization, AuthorizationStatus
from governance.authority import AuthorityProvenance, AuthorityReviewStatus
from user_owned_data import StorageOperation, StorageReference


class B2DataRuleReference(str, Enum):
    D1_STANDARD_DEPERSONALIZATION = "ADR-0047-D1"
    D2_STRICT_WORLD_SEPARATION = "ADR-0047-D2"
    D3_CONSENT_ONLY_EXCEPTION = "ADR-0047-D3"
    D4_MINIMALITY = "ADR-0047-D4"
    D5_UNSAFE_EXTERNAL_PARTIES = "ADR-0047-D5"
    D6_NO_SILENT_ENRICHMENT = "ADR-0047-D6"


D1_D6_REFERENCES = tuple(B2DataRuleReference)
D3_REFERENCE = B2DataRuleReference.D3_CONSENT_ONLY_EXCEPTION


class B2DataClass(str, Enum):
    CONFIRMED_PERSONAL_FACT = "CONFIRMED_PERSONAL_FACT"
    AUTHORIZED_DOCUMENT_FRAGMENT = "AUTHORIZED_DOCUMENT_FRAGMENT"
    PURPOSE_BOUND_CONTEXT_ATTRIBUTE = "PURPOSE_BOUND_CONTEXT_ATTRIBUTE"
    DEPERSONALIZED_CONTEXT = "DEPERSONALIZED_CONTEXT"
    GENERAL_NON_PERSONAL_INFORMATION = "GENERAL_NON_PERSONAL_INFORMATION"
    RAW_CONVERSATION = "RAW_CONVERSATION"
    COMPLETE_DOCUMENT = "COMPLETE_DOCUMENT"
    COMPLETE_UNDERSTANDING_STATE = "COMPLETE_UNDERSTANDING_STATE"
    HYPOTHESIS = "HYPOTHESIS"
    T2_RELATIONSHIP_ARTIFACT = "T2_RELATIONSHIP_ARTIFACT"
    CREDENTIAL_OR_SECRET = "CREDENTIAL_OR_SECRET"
    UNAUTHORIZED_THIRD_PARTY_DATA = "UNAUTHORIZED_THIRD_PARTY_DATA"
    DIRECT_IDENTIFIER = "DIRECT_IDENTIFIER"
    NON_REQUIRED_INDIRECT_IDENTIFIER = "NON_REQUIRED_INDIRECT_IDENTIFIER"


ALLOWED_B2_DATA_CLASSES = (
    B2DataClass.CONFIRMED_PERSONAL_FACT,
    B2DataClass.AUTHORIZED_DOCUMENT_FRAGMENT,
    B2DataClass.PURPOSE_BOUND_CONTEXT_ATTRIBUTE,
    B2DataClass.DEPERSONALIZED_CONTEXT,
    B2DataClass.GENERAL_NON_PERSONAL_INFORMATION,
)

PROHIBITED_B2_DATA_CLASSES = tuple(
    item for item in B2DataClass if item not in ALLOWED_B2_DATA_CLASSES
)


class B2DataSensitivity(str, Enum):
    NON_PERSONAL = "NON_PERSONAL"
    PERSONAL = "PERSONAL"
    SPECIAL_CATEGORY = "SPECIAL_CATEGORY"
    SECRET = "SECRET"


class B2DataSource(str, Enum):
    USER_CONFIRMED_INPUT = "USER_CONFIRMED_INPUT"
    USER_OWNED_REFERENCE = "USER_OWNED_REFERENCE"
    EXPLICITLY_AUTHORIZED_DOCUMENT_FRAGMENT = (
        "EXPLICITLY_AUTHORIZED_DOCUMENT_FRAGMENT"
    )
    DEPERSONALIZATION_BOUNDARY_OUTPUT = "DEPERSONALIZATION_BOUNDARY_OUTPUT"
    GENERAL_NON_PERSONAL_SOURCE = "GENERAL_NON_PERSONAL_SOURCE"
    RAW_CONVERSATION_STORE = "RAW_CONVERSATION_STORE"
    COMPLETE_DOCUMENT_STORE = "COMPLETE_DOCUMENT_STORE"
    UNDERSTANDING_STATE_STORE = "UNDERSTANDING_STATE_STORE"
    RELATIONSHIP_ARTIFACT_STORE = "RELATIONSHIP_ARTIFACT_STORE"
    CREDENTIAL_STORE = "CREDENTIAL_STORE"
    UNAUTHORIZED_THIRD_PARTY_SOURCE = "UNAUTHORIZED_THIRD_PARTY_SOURCE"


ALLOWED_B2_DATA_SOURCES = (
    B2DataSource.USER_CONFIRMED_INPUT,
    B2DataSource.USER_OWNED_REFERENCE,
    B2DataSource.EXPLICITLY_AUTHORIZED_DOCUMENT_FRAGMENT,
    B2DataSource.DEPERSONALIZATION_BOUNDARY_OUTPUT,
    B2DataSource.GENERAL_NON_PERSONAL_SOURCE,
)

PROHIBITED_B2_DATA_SOURCES = tuple(
    item for item in B2DataSource if item not in ALLOWED_B2_DATA_SOURCES
)


class B2DataFlowDirection(str, Enum):
    USER_OWNED_REFERENCE_TO_DEPERSONALIZATION = (
        "USER_OWNED_REFERENCE_TO_DEPERSONALIZATION"
    )
    USER_CONFIRMED_INPUT_TO_DEPERSONALIZATION = (
        "USER_CONFIRMED_INPUT_TO_DEPERSONALIZATION"
    )
    DEPERSONALIZATION_TO_B2_CORRIDOR = "DEPERSONALIZATION_TO_B2_CORRIDOR"
    GENERAL_NON_PERSONAL_SOURCE_TO_B2_CORRIDOR = (
        "GENERAL_NON_PERSONAL_SOURCE_TO_B2_CORRIDOR"
    )
    B2_CORRIDOR_TO_RUNTIME = "B2_CORRIDOR_TO_RUNTIME"
    B2_CORRIDOR_TO_OBSERVATION = "B2_CORRIDOR_TO_OBSERVATION"
    B2_CORRIDOR_TO_AUDIT = "B2_CORRIDOR_TO_AUDIT"
    B2_CORRIDOR_TO_OPERATIONAL_MEMORY = "B2_CORRIDOR_TO_OPERATIONAL_MEMORY"
    B2_CORRIDOR_TO_PHYSICAL_PERSISTENCE = (
        "B2_CORRIDOR_TO_PHYSICAL_PERSISTENCE"
    )
    B2_CORRIDOR_TO_METRICS = "B2_CORRIDOR_TO_METRICS"
    B2_CORRIDOR_TO_NOTIFICATIONS = "B2_CORRIDOR_TO_NOTIFICATIONS"
    B2_CORRIDOR_TO_PROVIDER = "B2_CORRIDOR_TO_PROVIDER"


ALLOWED_B2_DATA_FLOWS = (
    B2DataFlowDirection.USER_OWNED_REFERENCE_TO_DEPERSONALIZATION,
    B2DataFlowDirection.USER_CONFIRMED_INPUT_TO_DEPERSONALIZATION,
    B2DataFlowDirection.DEPERSONALIZATION_TO_B2_CORRIDOR,
    B2DataFlowDirection.GENERAL_NON_PERSONAL_SOURCE_TO_B2_CORRIDOR,
)

PROHIBITED_B2_DATA_FLOWS = tuple(
    item for item in B2DataFlowDirection if item not in ALLOWED_B2_DATA_FLOWS
)


class B2ConsentRequirement(str, Enum):
    EXPLICIT_SOVEREIGN_CONSENT = "EXPLICIT_SOVEREIGN_CONSENT"
    AAV_AUTHORIZATION_RECORDED = "AAV_AUTHORIZATION_RECORDED"
    REVOCABLE = "REVOCABLE"
    DATA_CLASSES_BOUND = "DATA_CLASSES_BOUND"
    SINGLE_PROCESS_BOUND = "SINGLE_PROCESS_BOUND"
    MINIMALITY_REVIEW_DOCUMENTED = "MINIMALITY_REVIEW_DOCUMENTED"


REQUIRED_D3_BINDINGS = tuple(B2ConsentRequirement)


class B2ConsentUse(str, Enum):
    STRUCTURE_PERSONAL_PREPARATION = "STRUCTURE_PERSONAL_PREPARATION"
    BIND_PROVIDED_CONTEXT = "BIND_PROVIDED_CONTEXT"
    PREPARE_PROFESSIONAL_REVIEW = "PREPARE_PROFESSIONAL_REVIEW"


class B2ProhibitedUse(str, Enum):
    PROFESSIONAL_DECISION = "PROFESSIONAL_DECISION"
    AUTHORITY_GRANT = "AUTHORITY_GRANT"
    PROVIDER_INVOCATION = "PROVIDER_INVOCATION"
    RUNTIME_EXECUTION = "RUNTIME_EXECUTION"
    PERSIST_PERSONAL_CONTENT = "PERSIST_PERSONAL_CONTENT"
    USER_PROFILING = "USER_PROFILING"
    TRAINING_DATA_CREATION = "TRAINING_DATA_CREATION"
    UNBOUND_SECONDARY_USE = "UNBOUND_SECONDARY_USE"


REQUIRED_PROHIBITED_USES = tuple(B2ProhibitedUse)


class B2ResidualIdentifier(str, Enum):
    NAME = "NAME"
    ADDRESS = "ADDRESS"
    CONTACT_IDENTIFIER = "CONTACT_IDENTIFIER"
    ACCOUNT_IDENTIFIER = "ACCOUNT_IDENTIFIER"
    INSURANCE_IDENTIFIER = "INSURANCE_IDENTIFIER"
    OFFICIAL_IDENTIFIER = "OFFICIAL_IDENTIFIER"
    STABLE_CROSS_CASE_KEY = "STABLE_CROSS_CASE_KEY"
    IDENTIFYING_COMBINATION = "IDENTIFYING_COMBINATION"


PROHIBITED_RESIDUAL_IDENTIFIERS = tuple(B2ResidualIdentifier)


class B2ProhibitedCombination(str, Enum):
    RAW_CONVERSATION_IN_CORRIDOR = "RAW_CONVERSATION_IN_CORRIDOR"
    COMPLETE_DOCUMENT_IN_CORRIDOR = "COMPLETE_DOCUMENT_IN_CORRIDOR"
    THIRD_PARTY_DATA_WITHOUT_OWN_AUTHORIZATION = (
        "THIRD_PARTY_DATA_WITHOUT_OWN_AUTHORIZATION"
    )
    IDENTIFIER_AFTER_DEPERSONALIZATION = "IDENTIFIER_AFTER_DEPERSONALIZATION"
    D3_WITHOUT_AAV_AND_UODL = "D3_WITHOUT_AAV_AND_UODL"


class B2ProhibitedPurposeChange(str, Enum):
    UNBOUND_SECONDARY_PURPOSE = "UNBOUND_SECONDARY_PURPOSE"
    USER_PROFILING = "USER_PROFILING"
    TRAINING = "TRAINING"
    CROSS_USER_AGGREGATION = "CROSS_USER_AGGREGATION"
    TOPIC_OR_LIFE_AREA_ANALYSIS = "TOPIC_OR_LIFE_AREA_ANALYSIS"


class B2ProhibitedDestination(str, Enum):
    RUNTIME = "RUNTIME"
    OBSERVATION = "OBSERVATION"
    AUDIT = "AUDIT"
    OPERATIONAL_MEMORY = "OPERATIONAL_MEMORY"
    PHYSICAL_PERSISTENCE = "PHYSICAL_PERSISTENCE"
    METRICS = "METRICS"
    NOTIFICATIONS = "NOTIFICATIONS"


@dataclass(frozen=True)
class B2DataClassification:
    data_class: B2DataClass
    sensitivity: B2DataSensitivity
    personal: bool
    depersonalizable: bool
    never_allowed: bool
    allowed_b2_uses: Tuple[B2ConsentUse, ...]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _enum(self.data_class, B2DataClass, "data_class")
        _enum(self.sensitivity, B2DataSensitivity, "sensitivity")
        for value, name in (
            (self.personal, "personal"),
            (self.depersonalizable, "depersonalizable"),
            (self.never_allowed, "never_allowed"),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be a bool".format(name))
        _typed_unique(self.allowed_b2_uses, B2ConsentUse, "allowed_b2_uses")
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2NegativeCorridorRules:
    prohibited_data_classes: Tuple[B2DataClass, ...]
    prohibited_data_sources: Tuple[B2DataSource, ...]
    prohibited_flow_directions: Tuple[B2DataFlowDirection, ...]
    prohibited_combinations: Tuple[B2ProhibitedCombination, ...]
    prohibited_residual_identifiers: Tuple[B2ResidualIdentifier, ...]
    prohibited_purpose_changes: Tuple[B2ProhibitedPurposeChange, ...]
    prohibited_destinations: Tuple[B2ProhibitedDestination, ...]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _typed_unique_nonempty(
            self.prohibited_data_classes,
            B2DataClass,
            "prohibited_data_classes",
        )
        _typed_unique_nonempty(
            self.prohibited_data_sources,
            B2DataSource,
            "prohibited_data_sources",
        )
        _typed_unique_nonempty(
            self.prohibited_flow_directions,
            B2DataFlowDirection,
            "prohibited_flow_directions",
        )
        _typed_unique_nonempty(
            self.prohibited_combinations,
            B2ProhibitedCombination,
            "prohibited_combinations",
        )
        _typed_unique_nonempty(
            self.prohibited_residual_identifiers,
            B2ResidualIdentifier,
            "prohibited_residual_identifiers",
        )
        _typed_unique_nonempty(
            self.prohibited_purpose_changes,
            B2ProhibitedPurposeChange,
            "prohibited_purpose_changes",
        )
        _typed_unique_nonempty(
            self.prohibited_destinations,
            B2ProhibitedDestination,
            "prohibited_destinations",
        )
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2DataCorridor:
    corridor_id: str
    version: int
    purpose: str
    allowed_data_classes: Tuple[B2DataClass, ...]
    excluded_data_classes: Tuple[B2DataClass, ...]
    allowed_data_sources: Tuple[B2DataSource, ...]
    excluded_data_sources: Tuple[B2DataSource, ...]
    allowed_flow_directions: Tuple[B2DataFlowDirection, ...]
    excluded_flow_directions: Tuple[B2DataFlowDirection, ...]
    d1_d6_references: Tuple[B2DataRuleReference, ...]
    d3_reference: B2DataRuleReference
    aav_reference: ArtifactAuthorization
    uodl_reference: StorageReference
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.corridor_id, "corridor_id")
        _positive_int(self.version, "version")
        _text(self.purpose, "purpose")
        _typed_unique_nonempty(
            self.allowed_data_classes, B2DataClass, "allowed_data_classes"
        )
        _typed_unique_nonempty(
            self.excluded_data_classes, B2DataClass, "excluded_data_classes"
        )
        _typed_unique_nonempty(
            self.allowed_data_sources, B2DataSource, "allowed_data_sources"
        )
        _typed_unique_nonempty(
            self.excluded_data_sources, B2DataSource, "excluded_data_sources"
        )
        _typed_unique_nonempty(
            self.allowed_flow_directions,
            B2DataFlowDirection,
            "allowed_flow_directions",
        )
        _typed_unique_nonempty(
            self.excluded_flow_directions,
            B2DataFlowDirection,
            "excluded_flow_directions",
        )
        _typed_unique_nonempty(
            self.d1_d6_references,
            B2DataRuleReference,
            "d1_d6_references",
        )
        _enum(self.d3_reference, B2DataRuleReference, "d3_reference")
        if not isinstance(self.aav_reference, ArtifactAuthorization):
            raise TypeError("aav_reference must be an ArtifactAuthorization")
        if not isinstance(self.uodl_reference, StorageReference):
            raise TypeError("uodl_reference must be a StorageReference")
        _review(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2ConsentBoundary:
    consent_id: str
    corridor_reference: str
    purpose_binding: str
    allowed_scope: Tuple[B2DataClass, ...]
    d3_binding: Tuple[B2ConsentRequirement, ...]
    revocation_reference: str
    allowed_use: Tuple[B2ConsentUse, ...]
    prohibited_use: Tuple[B2ProhibitedUse, ...]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.consent_id, "consent_id")
        _text(self.corridor_reference, "corridor_reference")
        _text(self.purpose_binding, "purpose_binding")
        _typed_unique_nonempty(self.allowed_scope, B2DataClass, "allowed_scope")
        _typed_unique_nonempty(
            self.d3_binding, B2ConsentRequirement, "d3_binding"
        )
        _text(self.revocation_reference, "revocation_reference")
        _typed_unique_nonempty(self.allowed_use, B2ConsentUse, "allowed_use")
        _typed_unique_nonempty(
            self.prohibited_use, B2ProhibitedUse, "prohibited_use"
        )
        _review(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2DepersonalizationBoundary:
    boundary_id: str
    d1_d6_references: Tuple[B2DataRuleReference, ...]
    removed_identifiers: Tuple[B2ResidualIdentifier, ...]
    allowed_residual_data: Tuple[B2DataClass, ...]
    prohibited_residual_identifiers: Tuple[B2ResidualIdentifier, ...]
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.boundary_id, "boundary_id")
        _typed_unique_nonempty(
            self.d1_d6_references,
            B2DataRuleReference,
            "d1_d6_references",
        )
        _typed_unique_nonempty(
            self.removed_identifiers,
            B2ResidualIdentifier,
            "removed_identifiers",
        )
        _typed_unique_nonempty(
            self.allowed_residual_data,
            B2DataClass,
            "allowed_residual_data",
        )
        _typed_unique_nonempty(
            self.prohibited_residual_identifiers,
            B2ResidualIdentifier,
            "prohibited_residual_identifiers",
        )
        _review(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2DataCorridorSnapshot:
    snapshot_id: str
    corridor: B2DataCorridor
    consent_boundary: B2ConsentBoundary
    data_classifications: Tuple[B2DataClassification, ...]
    depersonalization_boundary: B2DepersonalizationBoundary
    negative_rules: B2NegativeCorridorRules
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.snapshot_id, "snapshot_id")
        if not isinstance(self.corridor, B2DataCorridor):
            raise TypeError("corridor has an invalid type")
        if not isinstance(self.consent_boundary, B2ConsentBoundary):
            raise TypeError("consent_boundary has an invalid type")
        _typed_tuple(
            self.data_classifications,
            B2DataClassification,
            "data_classifications",
        )
        if not isinstance(
            self.depersonalization_boundary, B2DepersonalizationBoundary
        ):
            raise TypeError("depersonalization_boundary has an invalid type")
        if not isinstance(self.negative_rules, B2NegativeCorridorRules):
            raise TypeError("negative_rules has an invalid type")
        _review(self.review_status, self.review_reference)
        _provenance(self.provenance)


@dataclass(frozen=True)
class B2DataCorridorPackage:
    package_id: str
    corridor: B2DataCorridor
    consent_boundary: B2ConsentBoundary
    data_classifications: Tuple[B2DataClassification, ...]
    depersonalization_boundary: B2DepersonalizationBoundary
    negative_rules: B2NegativeCorridorRules
    snapshot: B2DataCorridorSnapshot

    def __post_init__(self) -> None:
        _text(self.package_id, "package_id")
        if not isinstance(self.corridor, B2DataCorridor):
            raise TypeError("corridor has an invalid type")
        if not isinstance(self.consent_boundary, B2ConsentBoundary):
            raise TypeError("consent_boundary has an invalid type")
        _typed_tuple(
            self.data_classifications,
            B2DataClassification,
            "data_classifications",
        )
        if not isinstance(
            self.depersonalization_boundary, B2DepersonalizationBoundary
        ):
            raise TypeError("depersonalization_boundary has an invalid type")
        if not isinstance(self.negative_rules, B2NegativeCorridorRules):
            raise TypeError("negative_rules has an invalid type")
        if not isinstance(self.snapshot, B2DataCorridorSnapshot):
            raise TypeError("snapshot has an invalid type")


class B2DataCorridorValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class B2DataCorridorValidator:
    """Validate supplied B2 boundaries without moving or processing data."""

    def validate(self, package: B2DataCorridorPackage) -> B2DataCorridorPackage:
        if not isinstance(package, B2DataCorridorPackage):
            raise TypeError("package must be a B2DataCorridorPackage")
        self._validate_rules(package)
        self._validate_aav_uodl(package)
        self._validate_consent(package)
        self._validate_classifications(package)
        self._validate_depersonalization(package)
        self._validate_negative_rules(package)
        self._validate_review_and_provenance(package)
        self._validate_snapshot(package)
        return package

    @staticmethod
    def _validate_rules(package: B2DataCorridorPackage) -> None:
        corridor = package.corridor
        if corridor.d1_d6_references != D1_D6_REFERENCES:
            _invalid("D1_D6_BINDING_INCOMPLETE", "all D1-D6 rules are required")
        if corridor.d3_reference is not D3_REFERENCE:
            _invalid("D3_BINDING_REQUIRED", "D3 must be explicitly bound")
        if corridor.allowed_data_classes != ALLOWED_B2_DATA_CLASSES:
            _invalid("ALLOWED_DATA_CLASSES_INVALID", "allowed classes differ")
        if corridor.excluded_data_classes != PROHIBITED_B2_DATA_CLASSES:
            _invalid("EXCLUDED_DATA_CLASSES_INCOMPLETE", "excluded classes differ")
        if corridor.allowed_data_sources != ALLOWED_B2_DATA_SOURCES:
            _invalid("ALLOWED_DATA_SOURCES_INVALID", "allowed sources differ")
        if corridor.excluded_data_sources != PROHIBITED_B2_DATA_SOURCES:
            _invalid("EXCLUDED_DATA_SOURCES_INCOMPLETE", "excluded sources differ")
        if corridor.allowed_flow_directions != ALLOWED_B2_DATA_FLOWS:
            _invalid("ALLOWED_FLOWS_INVALID", "allowed flows differ")
        if corridor.excluded_flow_directions != PROHIBITED_B2_DATA_FLOWS:
            _invalid("EXCLUDED_FLOWS_INCOMPLETE", "excluded flows differ")

    @staticmethod
    def _validate_aav_uodl(package: B2DataCorridorPackage) -> None:
        corridor = package.corridor
        authorization = corridor.aav_reference
        if authorization.status is not AuthorizationStatus.ACTIVE:
            _invalid("AAV_AUTHORIZATION_INACTIVE", "AAV authorization must be active")
        if corridor.corridor_id not in authorization.binding_references:
            _invalid("AAV_REFERENCE_INVALID", "AAV must bind the corridor")
        if authorization.purpose != corridor.purpose:
            _invalid("AAV_PURPOSE_MISMATCH", "AAV purpose must match corridor")
        storage_reference = corridor.uodl_reference
        if storage_reference.authorization.authorization is not authorization:
            _invalid(
                "UODL_AAV_IDENTITY_MISMATCH",
                "UODL must use the identical AAV authorization",
            )
        if StorageOperation.REFERENCE not in (
            storage_reference.authorization.operations
        ):
            _invalid("UODL_REFERENCE_INVALID", "UODL REFERENCE is required")

    @staticmethod
    def _validate_consent(package: B2DataCorridorPackage) -> None:
        corridor = package.corridor
        consent = package.consent_boundary
        if consent.corridor_reference != corridor.corridor_id:
            _invalid("CONSENT_CORRIDOR_MISMATCH", "consent belongs to another corridor")
        if consent.purpose_binding != corridor.purpose:
            _invalid("CONSENT_PURPOSE_MISMATCH", "consent purpose must match corridor")
        if consent.allowed_scope != corridor.allowed_data_classes:
            _invalid("CONSENT_SCOPE_MISMATCH", "consent scope must match allowed classes")
        if consent.d3_binding != REQUIRED_D3_BINDINGS:
            _invalid("D3_BINDING_INCOMPLETE", "all D3 requirements are required")
        if consent.prohibited_use != REQUIRED_PROHIBITED_USES:
            _invalid("PROHIBITED_USE_INCOMPLETE", "all prohibited uses are required")

    @staticmethod
    def _validate_classifications(package: B2DataCorridorPackage) -> None:
        items = package.data_classifications
        classes = tuple(item.data_class for item in items)
        if len(classes) != len(set(classes)):
            _invalid("DUPLICATE_DATA_CLASSIFICATION", "classifications must be unique")
        if set(classes) != set(B2DataClass):
            _invalid("DATA_CLASSIFICATION_INCOMPLETE", "every data class is required")
        for item in items:
            prohibited = item.data_class in PROHIBITED_B2_DATA_CLASSES
            if item.never_allowed is not prohibited:
                _invalid("DATA_CLASSIFICATION_INVALID", "never_allowed is inconsistent")
            if prohibited and item.allowed_b2_uses:
                _invalid("PROHIBITED_DATA_CLASS_HAS_USE", "prohibited class has B2 use")
            if not prohibited and not item.allowed_b2_uses:
                _invalid("ALLOWED_DATA_CLASS_HAS_NO_USE", "allowed class needs a use")

    @staticmethod
    def _validate_depersonalization(package: B2DataCorridorPackage) -> None:
        boundary = package.depersonalization_boundary
        if boundary.d1_d6_references != D1_D6_REFERENCES:
            _invalid("DEPERSONALIZATION_BINDING_INCOMPLETE", "D1-D6 are required")
        if boundary.removed_identifiers != PROHIBITED_RESIDUAL_IDENTIFIERS:
            _invalid("REMOVED_IDENTIFIERS_INCOMPLETE", "all identifiers must be removed")
        if boundary.prohibited_residual_identifiers != (
            PROHIBITED_RESIDUAL_IDENTIFIERS
        ):
            _invalid("RESIDUAL_IDENTIFIERS_INCOMPLETE", "residual identifiers differ")
        if not set(boundary.allowed_residual_data).issubset(
            set(package.corridor.allowed_data_classes)
        ):
            _invalid("RESIDUAL_DATA_NOT_ALLOWED", "residual data is outside corridor")

    @staticmethod
    def _validate_negative_rules(package: B2DataCorridorPackage) -> None:
        rules = package.negative_rules
        expected = (
            (rules.prohibited_data_classes, PROHIBITED_B2_DATA_CLASSES),
            (rules.prohibited_data_sources, PROHIBITED_B2_DATA_SOURCES),
            (rules.prohibited_flow_directions, PROHIBITED_B2_DATA_FLOWS),
            (rules.prohibited_combinations, tuple(B2ProhibitedCombination)),
            (
                rules.prohibited_residual_identifiers,
                PROHIBITED_RESIDUAL_IDENTIFIERS,
            ),
            (rules.prohibited_purpose_changes, tuple(B2ProhibitedPurposeChange)),
            (rules.prohibited_destinations, tuple(B2ProhibitedDestination)),
        )
        if any(actual != required for actual, required in expected):
            _invalid("NEGATIVE_RULES_INCOMPLETE", "negative rules must be complete")

    @staticmethod
    def _validate_review_and_provenance(package: B2DataCorridorPackage) -> None:
        objects = (
            package.corridor,
            package.consent_boundary,
            package.depersonalization_boundary,
            package.snapshot,
        )
        provenance = package.corridor.provenance
        review_status = package.corridor.review_status
        review_reference = package.corridor.review_reference
        for item in objects:
            if item.provenance != provenance:
                _invalid("PROVENANCE_INCONSISTENT", "provenance must match")
            if item.review_status is not review_status:
                _invalid("REVIEW_STATUS_INCONSISTENT", "review status must match")
            if item.review_reference != review_reference:
                _invalid("REVIEW_REFERENCE_INCONSISTENT", "review reference must match")
        for item in package.data_classifications + (package.negative_rules,):
            if item.provenance != provenance:
                _invalid("PROVENANCE_INCONSISTENT", "provenance must match")

    @staticmethod
    def _validate_snapshot(package: B2DataCorridorPackage) -> None:
        snapshot = package.snapshot
        if snapshot.corridor is not package.corridor:
            _invalid("SNAPSHOT_IDENTITY_MISMATCH", "corridor identity changed")
        if snapshot.consent_boundary is not package.consent_boundary:
            _invalid("SNAPSHOT_IDENTITY_MISMATCH", "consent identity changed")
        if snapshot.data_classifications is not package.data_classifications:
            _invalid("SNAPSHOT_IDENTITY_MISMATCH", "classification tuple changed")
        if snapshot.depersonalization_boundary is not (
            package.depersonalization_boundary
        ):
            _invalid("SNAPSHOT_IDENTITY_MISMATCH", "boundary identity changed")
        if snapshot.negative_rules is not package.negative_rules:
            _invalid("SNAPSHOT_IDENTITY_MISMATCH", "negative rules identity changed")


def _invalid(code: str, message: str) -> None:
    raise B2DataCorridorValidationError(code, message)


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value or value != value.strip() or "\n" in value or "\r" in value:
        raise ValueError("{} must be a trimmed single line".format(field_name))
    return value


def _positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("{} must be an integer".format(field_name))
    if value < 1:
        raise ValueError("{} must be positive".format(field_name))
    return value


def _enum(value: object, expected: Type[Enum], field_name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be {}".format(field_name, expected.__name__))


def _typed_tuple(value: object, expected: type, field_name: str) -> tuple:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    if not all(isinstance(item, expected) for item in value):
        raise TypeError("{} contains invalid values".format(field_name))
    return value


def _typed_unique(value: object, expected: type, field_name: str) -> tuple:
    values = _typed_tuple(value, expected, field_name)
    if len(values) != len(set(values)):
        raise ValueError("{} must be unique".format(field_name))
    return values


def _typed_unique_nonempty(
    value: object, expected: type, field_name: str
) -> tuple:
    values = _typed_unique(value, expected, field_name)
    if not values:
        raise ValueError("{} must not be empty".format(field_name))
    return values


def _review(
    status: AuthorityReviewStatus, reference: Optional[str]
) -> None:
    _enum(status, AuthorityReviewStatus, "review_status")
    if status is AuthorityReviewStatus.REVIEWED and reference is None:
        raise ValueError("reviewed status requires review_reference")
    if status is not AuthorityReviewStatus.REVIEWED and reference is not None:
        raise ValueError("only reviewed status may have review_reference")
    if reference is not None:
        _text(reference, "review_reference")


def _provenance(value: object) -> AuthorityProvenance:
    if not isinstance(value, AuthorityProvenance):
        raise TypeError("provenance must be an AuthorityProvenance")
    return value
