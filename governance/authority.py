"""Immutable, non-executing Guardian Authority Model contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from governance.models import NormLevel


class AuthorityType(str, Enum):
    SOVEREIGN_DECISION = "SOVEREIGN_DECISION"
    GOVERNANCE_OVERSIGHT = "GOVERNANCE_OVERSIGHT"
    OPERATIONAL_IMPLEMENTATION = "OPERATIONAL_IMPLEMENTATION"
    DETERMINISTIC_VALIDATION = "DETERMINISTIC_VALIDATION"
    GUARDIAN_COMMUNICATION = "GUARDIAN_COMMUNICATION"
    PROFESSIONAL_JUDGMENT = "PROFESSIONAL_JUDGMENT"


class AuthorityActorClass(str, Enum):
    HUMAN_SOVEREIGN = "HUMAN_SOVEREIGN"
    OPERATIONAL_LEADERSHIP = "OPERATIONAL_LEADERSHIP"
    TRUST_COUNCIL = "TRUST_COUNCIL"
    USER_CONVENTION = "USER_CONVENTION"
    STEWARDSHIP_STRUCTURE = "STEWARDSHIP_STRUCTURE"
    GUARDIAN = "GUARDIAN"
    DETERMINISTIC_CORE = "DETERMINISTIC_CORE"
    MODEL_LAYER = "MODEL_LAYER"
    HUMAN_PROFESSIONAL = "HUMAN_PROFESSIONAL"


class AuthorityCapability(str, Enum):
    DEFINE_PERSONAL_INTENT = "DEFINE_PERSONAL_INTENT"
    RATIFY_ARCHITECTURE_DECISION = "RATIFY_ARCHITECTURE_DECISION"
    REVIEW_TRUST_DOMAIN = "REVIEW_TRUST_DOMAIN"
    ISSUE_SUSPENSIVE_VETO = "ISSUE_SUSPENSIVE_VETO"
    APPROVE_CONSTITUTION_CHANGE = "APPROVE_CONSTITUTION_CHANGE"
    IMPLEMENT_APPROVED_CHANGE = "IMPLEMENT_APPROVED_CHANGE"
    VALIDATE_TYPED_CONTRACT = "VALIDATE_TYPED_CONTRACT"
    PRESENT_GUARDIAN_RESPONSE = "PRESENT_GUARDIAN_RESPONSE"
    MAKE_PROFESSIONAL_JUDGMENT = "MAKE_PROFESSIONAL_JUDGMENT"


class AuthorityExercise(str, Enum):
    NON_DELEGABLE = "NON_DELEGABLE"
    DELEGABLE = "DELEGABLE"
    JOINT_EXERCISE = "JOINT_EXERCISE"


class AuthorityControlLevel(str, Enum):
    EXPLICIT_HUMAN_CONTROL = "EXPLICIT_HUMAN_CONTROL"
    INDEPENDENT_REVIEW = "INDEPENDENT_REVIEW"
    MULTI_PARTY_CONTROL = "MULTI_PARTY_CONTROL"
    STRUCTURAL_VALIDATION = "STRUCTURAL_VALIDATION"


class AuthorityReviewStatus(str, Enum):
    NOT_REVIEWED = "NOT_REVIEWED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REVIEWED = "REVIEWED"


class AuthorityModelCapability(str, Enum):
    DESCRIBE_AUTHORITY_MODEL = "DESCRIBE_AUTHORITY_MODEL"
    AUTHORIZE_PROVIDER = "AUTHORIZE_PROVIDER"
    ACTIVATE_RUNTIME = "ACTIVATE_RUNTIME"
    CLASSIFY_REQUEST = "CLASSIFY_REQUEST"
    GENERATE_ANSWER = "GENERATE_ANSWER"
    ACQUIRE_SOURCE = "ACQUIRE_SOURCE"
    ACTIVATE_WORKFLOW = "ACTIVATE_WORKFLOW"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    MODIFY_STATE = "MODIFY_STATE"
    PERSIST_AUTHORITY = "PERSIST_AUTHORITY"


NON_EXECUTING_AUTHORITY_MODEL_CAPABILITIES = (
    AuthorityModelCapability.DESCRIBE_AUTHORITY_MODEL,
)


@dataclass(frozen=True)
class AuthorityProvenance:
    norm_level: NormLevel
    source_reference: str
    decision_reference: str

    def __post_init__(self) -> None:
        _enum(self.norm_level, NormLevel, "norm_level")
        if self.norm_level is NormLevel.C1_CONSTITUTION:
            raise ValueError("authority provenance must not claim C1 authority")
        _text(self.source_reference, "source_reference")
        _text(self.decision_reference, "decision_reference")


@dataclass(frozen=True)
class AuthorityDefinition:
    authority_id: str
    authority_type: AuthorityType
    responsibility: str
    capabilities: Tuple[AuthorityCapability, ...]
    exercise: AuthorityExercise
    revocable: bool
    required_control_levels: Tuple[AuthorityControlLevel, ...]
    joint_actor_classes: Tuple[AuthorityActorClass, ...]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.authority_id, "authority_id")
        _enum(self.authority_type, AuthorityType, "authority_type")
        _text(self.responsibility, "responsibility")
        _typed_unique_nonempty(self.capabilities, AuthorityCapability, "capabilities")
        _enum(self.exercise, AuthorityExercise, "exercise")
        if not isinstance(self.revocable, bool):
            raise TypeError("revocable must be a bool")
        _typed_unique_nonempty(
            self.required_control_levels,
            AuthorityControlLevel,
            "required_control_levels",
        )
        _typed_unique(self.joint_actor_classes, AuthorityActorClass, "joint_actor_classes")
        if not isinstance(self.provenance, AuthorityProvenance):
            raise TypeError("provenance must be an AuthorityProvenance")


@dataclass(frozen=True)
class ActorResponsibilityBoundary:
    boundary_id: str
    actor_class: AuthorityActorClass
    responsibilities: Tuple[str, ...]
    allowed_authority_references: Tuple[str, ...]
    prohibited_authority_references: Tuple[str, ...]
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.boundary_id, "boundary_id")
        _enum(self.actor_class, AuthorityActorClass, "actor_class")
        _strings(self.responsibilities, "responsibilities", required=True)
        _strings(
            self.allowed_authority_references,
            "allowed_authority_references",
            required=False,
        )
        _strings(
            self.prohibited_authority_references,
            "prohibited_authority_references",
            required=False,
        )
        if not isinstance(self.provenance, AuthorityProvenance):
            raise TypeError("provenance must be an AuthorityProvenance")


@dataclass(frozen=True)
class AuthorityDelegationRule:
    delegation_rule_id: str
    authority_reference: str
    delegating_actor_class: AuthorityActorClass
    receiving_actor_classes: Tuple[AuthorityActorClass, ...]
    requires_explicit_human_confirmation: bool
    revocable: bool
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.delegation_rule_id, "delegation_rule_id")
        _text(self.authority_reference, "authority_reference")
        _enum(
            self.delegating_actor_class,
            AuthorityActorClass,
            "delegating_actor_class",
        )
        _typed_unique_nonempty(
            self.receiving_actor_classes,
            AuthorityActorClass,
            "receiving_actor_classes",
        )
        for value, name in (
            (
                self.requires_explicit_human_confirmation,
                "requires_explicit_human_confirmation",
            ),
            (self.revocable, "revocable"),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be a bool".format(name))
        if not isinstance(self.provenance, AuthorityProvenance):
            raise TypeError("provenance must be an AuthorityProvenance")


@dataclass(frozen=True)
class ProhibitedAuthorityCombination:
    combination_id: str
    first_authority_reference: str
    second_authority_reference: str
    reason: str
    provenance: AuthorityProvenance

    def __post_init__(self) -> None:
        _text(self.combination_id, "combination_id")
        _text(self.first_authority_reference, "first_authority_reference")
        _text(self.second_authority_reference, "second_authority_reference")
        _text(self.reason, "reason")
        if not isinstance(self.provenance, AuthorityProvenance):
            raise TypeError("provenance must be an AuthorityProvenance")


@dataclass(frozen=True)
class GuardianAuthorityModel:
    authority_model_id: str
    version: str
    authorities: Tuple[AuthorityDefinition, ...]
    actor_boundaries: Tuple[ActorResponsibilityBoundary, ...]
    delegation_rules: Tuple[AuthorityDelegationRule, ...]
    prohibited_combinations: Tuple[ProhibitedAuthorityCombination, ...]
    provenance: AuthorityProvenance
    review_status: AuthorityReviewStatus
    review_reference: Optional[str]
    capabilities: Tuple[AuthorityModelCapability, ...] = (
        AuthorityModelCapability.DESCRIBE_AUTHORITY_MODEL,
    )

    def __post_init__(self) -> None:
        _text(self.authority_model_id, "authority_model_id")
        _text(self.version, "version")
        _typed_tuple(self.authorities, AuthorityDefinition, "authorities")
        _typed_tuple(
            self.actor_boundaries,
            ActorResponsibilityBoundary,
            "actor_boundaries",
        )
        _typed_tuple(
            self.delegation_rules,
            AuthorityDelegationRule,
            "delegation_rules",
        )
        _typed_tuple(
            self.prohibited_combinations,
            ProhibitedAuthorityCombination,
            "prohibited_combinations",
        )
        if not isinstance(self.provenance, AuthorityProvenance):
            raise TypeError("provenance must be an AuthorityProvenance")
        _enum(self.review_status, AuthorityReviewStatus, "review_status")
        if self.review_reference is not None:
            _text(self.review_reference, "review_reference")
        _typed_unique_nonempty(
            self.capabilities,
            AuthorityModelCapability,
            "capabilities",
        )


class GuardianAuthorityValidationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianAuthorityModelValidator:
    """Validate a supplied authority constitution without granting authority."""

    def validate(self, model: GuardianAuthorityModel) -> GuardianAuthorityModel:
        if not isinstance(model, GuardianAuthorityModel):
            raise TypeError("model must be a GuardianAuthorityModel")
        if not model.authorities:
            _invalid("AUTHORITIES_REQUIRED", "at least one authority is required")
        if not model.actor_boundaries:
            _invalid("ACTOR_BOUNDARIES_REQUIRED", "actor boundaries are required")
        self._validate_unique_identities(model)
        self._validate_provenance(model)
        self._validate_review(model)
        self._validate_capabilities(model)

        authorities = {item.authority_id: item for item in model.authorities}
        boundaries = {item.actor_class: item for item in model.actor_boundaries}
        self._validate_boundaries(authorities, boundaries)
        self._validate_exercise(authorities, boundaries, model.delegation_rules)
        self._validate_delegations(authorities, boundaries, model.delegation_rules)
        self._validate_prohibited_combinations(
            authorities,
            boundaries,
            model.prohibited_combinations,
        )
        return model

    @staticmethod
    def _validate_unique_identities(model: GuardianAuthorityModel) -> None:
        identifiers = (
            [model.authority_model_id]
            + [item.authority_id for item in model.authorities]
            + [item.boundary_id for item in model.actor_boundaries]
            + [item.delegation_rule_id for item in model.delegation_rules]
            + [item.combination_id for item in model.prohibited_combinations]
        )
        if len(identifiers) != len(set(identifiers)):
            _invalid("DUPLICATE_IDENTITY", "all authority identities must be unique")
        actor_classes = tuple(item.actor_class for item in model.actor_boundaries)
        if len(actor_classes) != len(set(actor_classes)):
            _invalid("DUPLICATE_ACTOR_BOUNDARY", "actor classes must be unique")

    @staticmethod
    def _validate_provenance(model: GuardianAuthorityModel) -> None:
        values = (
            tuple(item.provenance for item in model.authorities)
            + tuple(item.provenance for item in model.actor_boundaries)
            + tuple(item.provenance for item in model.delegation_rules)
            + tuple(item.provenance for item in model.prohibited_combinations)
        )
        if any(value != model.provenance for value in values):
            _invalid(
                "PROVENANCE_MISMATCH",
                "all authority entries must share the model provenance",
            )

    @staticmethod
    def _validate_review(model: GuardianAuthorityModel) -> None:
        if model.review_status is AuthorityReviewStatus.REVIEWED:
            if model.review_reference is None:
                _invalid("REVIEW_REFERENCE_REQUIRED", "reviewed model needs a reference")
        elif model.review_reference is not None:
            _invalid(
                "UNEXPECTED_REVIEW_REFERENCE",
                "only a reviewed model may carry a review reference",
            )

    @staticmethod
    def _validate_capabilities(model: GuardianAuthorityModel) -> None:
        if model.capabilities != NON_EXECUTING_AUTHORITY_MODEL_CAPABILITIES:
            _invalid(
                "EXECUTING_CAPABILITY_FORBIDDEN",
                "authority model may only describe supplied authority",
            )

    @staticmethod
    def _validate_boundaries(authorities, boundaries) -> None:
        authority_ids = set(authorities)
        for boundary in boundaries.values():
            allowed = set(boundary.allowed_authority_references)
            prohibited = set(boundary.prohibited_authority_references)
            if (allowed | prohibited) - authority_ids:
                _invalid("UNKNOWN_AUTHORITY_REFERENCE", "boundary references unknown authority")
            if allowed & prohibited:
                _invalid("CONTRADICTORY_BOUNDARY", "authority cannot be allowed and prohibited")
            if allowed | prohibited != authority_ids:
                _invalid(
                    "INCOMPLETE_RESPONSIBILITY_BOUNDARY",
                    "every authority must be allowed or prohibited for each actor class",
                )

    @staticmethod
    def _validate_exercise(authorities, boundaries, rules) -> None:
        rules_by_authority = {}
        for rule in rules:
            rules_by_authority.setdefault(rule.authority_reference, []).append(rule)
        for authority in authorities.values():
            authority_rules = rules_by_authority.get(authority.authority_id, [])
            if authority.exercise is AuthorityExercise.DELEGABLE:
                if not authority_rules:
                    _invalid("DELEGATION_RULE_REQUIRED", "delegable authority needs a rule")
                if authority.joint_actor_classes:
                    _invalid("UNEXPECTED_JOINT_ACTORS", "delegable authority is not joint")
            elif authority_rules:
                _invalid(
                    "NON_DELEGABLE_AUTHORITY_DELEGATED",
                    "non-delegable or joint authority cannot have delegation rules",
                )
            if authority.exercise is AuthorityExercise.JOINT_EXERCISE:
                if len(authority.joint_actor_classes) < 2:
                    _invalid("JOINT_ACTORS_REQUIRED", "joint authority needs two actor classes")
                if (
                    AuthorityControlLevel.MULTI_PARTY_CONTROL
                    not in authority.required_control_levels
                ):
                    _invalid(
                        "MULTI_PARTY_CONTROL_REQUIRED",
                        "joint authority needs multi-party control",
                    )
                for actor_class in authority.joint_actor_classes:
                    boundary = boundaries.get(actor_class)
                    if boundary is None:
                        _invalid("ACTOR_BOUNDARY_REQUIRED", "joint actor needs a boundary")
                    if authority.authority_id not in boundary.allowed_authority_references:
                        _invalid(
                            "RESPONSIBILITY_BOUNDARY_EXCEEDED",
                            "joint actor lacks authority boundary",
                        )
            elif authority.joint_actor_classes:
                _invalid("UNEXPECTED_JOINT_ACTORS", "only joint authority may list joint actors")

    @staticmethod
    def _validate_delegations(authorities, boundaries, rules) -> None:
        for rule in rules:
            authority = authorities.get(rule.authority_reference)
            if authority is None:
                _invalid("UNKNOWN_AUTHORITY_REFERENCE", "delegation references unknown authority")
            if authority.exercise is not AuthorityExercise.DELEGABLE:
                _invalid("NON_DELEGABLE_AUTHORITY_DELEGATED", "authority cannot be delegated")
            source = boundaries.get(rule.delegating_actor_class)
            if source is None:
                _invalid("ACTOR_BOUNDARY_REQUIRED", "delegating actor needs a boundary")
            if rule.authority_reference not in source.allowed_authority_references:
                _invalid("RESPONSIBILITY_BOUNDARY_EXCEEDED", "delegating actor lacks authority")
            if rule.delegating_actor_class in rule.receiving_actor_classes:
                _invalid("SELF_DELEGATION", "actor class cannot delegate to itself")
            for actor_class in rule.receiving_actor_classes:
                receiver = boundaries.get(actor_class)
                if receiver is None:
                    _invalid("ACTOR_BOUNDARY_REQUIRED", "receiving actor needs a boundary")
                if rule.authority_reference not in receiver.allowed_authority_references:
                    _invalid("RESPONSIBILITY_BOUNDARY_EXCEEDED", "receiver exceeds its boundary")
            if rule.revocable is not authority.revocable:
                _invalid("REVOCABILITY_MISMATCH", "delegation revocability must match authority")

    @staticmethod
    def _validate_prohibited_combinations(authorities, boundaries, combinations) -> None:
        pairs = set()
        for combination in combinations:
            first = combination.first_authority_reference
            second = combination.second_authority_reference
            if first not in authorities or second not in authorities:
                _invalid("UNKNOWN_AUTHORITY_REFERENCE", "combination references unknown authority")
            if first == second:
                _invalid("SELF_PROHIBITED_COMBINATION", "combination needs two authorities")
            pair = frozenset((first, second))
            if pair in pairs:
                _invalid("DUPLICATE_PROHIBITED_COMBINATION", "combination is duplicated")
            pairs.add(pair)
            for boundary in boundaries.values():
                allowed = set(boundary.allowed_authority_references)
                if {first, second} <= allowed:
                    _invalid(
                        "PROHIBITED_AUTHORITY_COMBINATION",
                        "actor boundary permits a prohibited combination",
                    )


def _invalid(code: str, message: str) -> None:
    raise GuardianAuthorityValidationError(code, message)


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value: object, name: str, *, required: bool) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_tuple(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid values".format(name))


def _typed_unique(value: object, item_type: type, name: str) -> None:
    _typed_tuple(value, item_type, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _typed_unique_nonempty(value: object, item_type: type, name: str) -> None:
    _typed_unique(value, item_type, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))
