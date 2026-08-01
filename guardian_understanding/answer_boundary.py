"""Typed, non-executing answer-boundary contracts from ADR-0047."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class AnswerOperatingMode(str, Enum):
    B1_GENERAL_ORIENTATION = "B1_GENERAL_ORIENTATION"
    B2_PERSONAL_PREPARATION = "B2_PERSONAL_PREPARATION"
    B3_PROFESSIONAL_DECISION_REQUIRED = "B3_PROFESSIONAL_DECISION_REQUIRED"


class AnswerCapability(str, Enum):
    READ_TYPED_INPUT = "READ_TYPED_INPUT"
    PRESENT_GENERAL_INFORMATION = "PRESENT_GENERAL_INFORMATION"
    STRUCTURE_PERSONAL_PREPARATION = "STRUCTURE_PERSONAL_PREPARATION"
    STATE_CLEAR_NON_CONFIRMATION = "STATE_CLEAR_NON_CONFIRMATION"
    MAKE_PROFESSIONAL_CASE_DECISION = "MAKE_PROFESSIONAL_CASE_DECISION"
    MODIFY_UNDERSTANDING_STATE = "MODIFY_UNDERSTANDING_STATE"
    MODIFY_ARTIFACT = "MODIFY_ARTIFACT"
    CREATE_RESOLUTION = "CREATE_RESOLUTION"
    MODIFY_RIGHTS = "MODIFY_RIGHTS"
    MODIFY_APPROVALS = "MODIFY_APPROVALS"
    MODIFY_JOURNEY_STATUS = "MODIFY_JOURNEY_STATUS"
    MODIFY_SOURCE_CHAIN = "MODIFY_SOURCE_CHAIN"
    ACTIVATE_DOMAIN = "ACTIVATE_DOMAIN"
    ACTIVATE_TOOL = "ACTIVATE_TOOL"
    START_WORKFLOW = "START_WORKFLOW"
    ROUTE_REQUEST = "ROUTE_REQUEST"


NON_EXECUTING_CAPABILITIES = (
    AnswerCapability.READ_TYPED_INPUT,
    AnswerCapability.PRESENT_GENERAL_INFORMATION,
    AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,
    AnswerCapability.STATE_CLEAR_NON_CONFIRMATION,
)

ALWAYS_FORBIDDEN_CAPABILITIES = tuple(
    capability
    for capability in AnswerCapability
    if capability not in NON_EXECUTING_CAPABILITIES
)

_PROTECTION_LEVEL = {
    AnswerOperatingMode.B1_GENERAL_ORIENTATION: 1,
    AnswerOperatingMode.B2_PERSONAL_PREPARATION: 2,
    AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: 3,
}


def answer_mode_protection_level(mode: AnswerOperatingMode) -> int:
    """Return the canonical ADR-0047 protection level for a typed mode."""

    _enum(mode, AnswerOperatingMode, "mode")
    return _PROTECTION_LEVEL[mode]


def most_protective_answer_mode(
    modes: Tuple[AnswerOperatingMode, ...],
) -> AnswerOperatingMode:
    """Select the highest typed mode using only the canonical protection order."""

    if not isinstance(modes, tuple) or not modes:
        raise ValueError("modes must be a non-empty tuple")
    for mode in modes:
        _enum(mode, AnswerOperatingMode, "mode")
    return max(modes, key=answer_mode_protection_level)


@dataclass(frozen=True)
class AnswerBoundaryContract:
    requested_mode: AnswerOperatingMode
    effective_mode: AnswerOperatingMode
    classification_reason: str
    affected_domains: Tuple[str, ...]
    has_personal_context: bool
    requests_professional_case_decision: bool
    requires_clear_non_confirmation: bool
    boundary_statement: Optional[str]
    allowed_capabilities: Tuple[AnswerCapability, ...]
    forbidden_capabilities: Tuple[AnswerCapability, ...]

    def __post_init__(self) -> None:
        _enum(self.requested_mode, AnswerOperatingMode, "requested_mode")
        _enum(self.effective_mode, AnswerOperatingMode, "effective_mode")
        _text(self.classification_reason, "classification_reason")
        _strings(self.affected_domains, "affected_domains")
        for value, name in (
            (self.has_personal_context, "has_personal_context"),
            (
                self.requests_professional_case_decision,
                "requests_professional_case_decision",
            ),
            (
                self.requires_clear_non_confirmation,
                "requires_clear_non_confirmation",
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError("{} must be a bool".format(name))
        if self.boundary_statement is not None:
            _text(self.boundary_statement, "boundary_statement")
        _capabilities(self.allowed_capabilities, "allowed_capabilities")
        _capabilities(self.forbidden_capabilities, "forbidden_capabilities")


class AnswerBoundaryValidationError(ValueError):
    """A stable validation failure without any repair or side effect."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class GuardianAnswerBoundaryValidator:
    """Validate already typed metadata; never classify or execute a request."""

    def validate(self, contract: AnswerBoundaryContract) -> AnswerBoundaryContract:
        if not isinstance(contract, AnswerBoundaryContract):
            raise TypeError("contract must be an AnswerBoundaryContract")

        if answer_mode_protection_level(
            contract.effective_mode
        ) < answer_mode_protection_level(contract.requested_mode):
            _invalid("MODE_DOWNGRADE", "effective_mode must not reduce protection")

        allowed = set(contract.allowed_capabilities)
        forbidden = set(contract.forbidden_capabilities)
        if allowed - set(NON_EXECUTING_CAPABILITIES):
            _invalid("EXECUTING_CAPABILITY_ALLOWED", "allowed capabilities must be non-executing")
        if allowed & forbidden:
            _invalid("CAPABILITY_CONFLICT", "a capability cannot be both allowed and forbidden")
        if not set(ALWAYS_FORBIDDEN_CAPABILITIES) <= forbidden:
            _invalid("REQUIRED_PROHIBITION_MISSING", "all executing capabilities must be forbidden")

        required_capability = {
            AnswerOperatingMode.B1_GENERAL_ORIENTATION: AnswerCapability.PRESENT_GENERAL_INFORMATION,
            AnswerOperatingMode.B2_PERSONAL_PREPARATION: AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,
            AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: AnswerCapability.STATE_CLEAR_NON_CONFIRMATION,
        }[contract.effective_mode]
        if required_capability not in allowed:
            _invalid("MODE_CAPABILITY_MISSING", "effective mode capability is missing")

        if (
            contract.requests_professional_case_decision
            and contract.effective_mode is not AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
        ):
            _invalid(
                "CASE_DECISION_MODE_MISMATCH",
                "a requested professional case decision requires B3",
            )

        if contract.effective_mode is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED:
            if not contract.requires_clear_non_confirmation:
                _invalid("NON_CONFIRMATION_NOT_REQUIRED", "B3 must require clear non-confirmation")
            if not _is_controlled_non_confirmation(contract.boundary_statement):
                _invalid("NON_CONFIRMATION_MISSING", "B3 requires a controlled non-confirmation statement")
        elif contract.requires_clear_non_confirmation:
            _invalid("NON_CONFIRMATION_MODE_MISMATCH", "clear non-confirmation requires B3")

        return contract


def _is_controlled_non_confirmation(value: Optional[str]) -> bool:
    if value == "Ich kann das nicht bestätigen.":
        return True
    prefix = "Ich kann nicht bestätigen, ob "
    return bool(value and value.startswith(prefix) and value.endswith(".") and len(value) > len(prefix) + 1)


def _invalid(code: str, message: str) -> None:
    raise AnswerBoundaryValidationError(code, message)


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _strings(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))


def _capabilities(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, AnswerCapability) for item in value):
        raise TypeError("{} contains invalid capabilities".format(name))
    if len(value) != len(set(value)):
        raise ValueError("{} must not contain duplicates".format(name))
