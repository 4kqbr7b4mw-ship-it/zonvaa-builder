from dataclasses import FrozenInstanceError

import pytest

from guardian_understanding import (
    ALWAYS_FORBIDDEN_CAPABILITIES,
    AnswerBoundaryContract,
    AnswerBoundaryValidationError,
    AnswerCapability,
    AnswerOperatingMode,
    GuardianAnswerBoundaryValidator,
)


VALIDATOR = GuardianAnswerBoundaryValidator()


def contract(requested, effective=None, **changes):
    effective = effective or requested
    allowed = {
        AnswerOperatingMode.B1_GENERAL_ORIENTATION: (
            AnswerCapability.READ_TYPED_INPUT,
            AnswerCapability.PRESENT_GENERAL_INFORMATION,
        ),
        AnswerOperatingMode.B2_PERSONAL_PREPARATION: (
            AnswerCapability.READ_TYPED_INPUT,
            AnswerCapability.PRESENT_GENERAL_INFORMATION,
            AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,
        ),
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED: (
            AnswerCapability.READ_TYPED_INPUT,
            AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,
            AnswerCapability.STATE_CLEAR_NON_CONFIRMATION,
        ),
    }[effective]
    values = {
        "boundary_id": "boundary-1",
        "requested_mode": requested,
        "effective_mode": effective,
        "classification_reason": "Bereits typisierter Prüfgrund.",
        "affected_domains": ("life_decisions",),
        "has_personal_context": effective is not AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        "requests_professional_case_decision": effective is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        "requires_clear_non_confirmation": effective is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        "boundary_statement": (
            "Ich kann das nicht bestätigen."
            if effective is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
            else None
        ),
        "allowed_capabilities": allowed,
        "forbidden_capabilities": ALWAYS_FORBIDDEN_CAPABILITIES,
    }
    values.update(changes)
    return AnswerBoundaryContract(**values)


@pytest.mark.parametrize("mode", tuple(AnswerOperatingMode))
def test_each_answer_mode_has_a_valid_non_executing_contract(mode):
    value = contract(mode)
    assert VALIDATOR.validate(value) is value


@pytest.mark.parametrize(
    ("requested", "effective"),
    (
        (AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B2_PERSONAL_PREPARATION),
        (AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED),
        (AnswerOperatingMode.B2_PERSONAL_PREPARATION, AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED),
    ),
)
def test_each_protective_escalation_is_valid(requested, effective):
    assert VALIDATOR.validate(contract(requested, effective)).effective_mode is effective


@pytest.mark.parametrize(
    ("requested", "effective"),
    (
        (AnswerOperatingMode.B2_PERSONAL_PREPARATION, AnswerOperatingMode.B1_GENERAL_ORIENTATION),
        (AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, AnswerOperatingMode.B2_PERSONAL_PREPARATION),
        (AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, AnswerOperatingMode.B1_GENERAL_ORIENTATION),
    ),
)
def test_each_protection_downgrade_is_rejected(requested, effective):
    with pytest.raises(AnswerBoundaryValidationError, match="must not reduce protection") as error:
        VALIDATOR.validate(contract(requested, effective))
    assert error.value.code == "MODE_DOWNGRADE"


@pytest.mark.parametrize(
    "statement",
    (None, "", "Eine Fachperson sollte das prüfen.", "Ich kann das vielleicht nicht bestätigen."),
)
def test_b3_without_controlled_clear_non_confirmation_is_rejected(statement):
    changes = {"boundary_statement": statement}
    if statement == "":
        with pytest.raises(ValueError, match="boundary_statement"):
            contract(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, **changes)
        return
    with pytest.raises(AnswerBoundaryValidationError) as error:
        VALIDATOR.validate(contract(AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED, **changes))
    assert error.value.code == "NON_CONFIRMATION_MISSING"


def test_b3_accepts_grammatically_concrete_controlled_non_confirmation():
    value = contract(
        AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED,
        boundary_statement="Ich kann nicht bestätigen, ob die konkrete Vollmacht wirksam ist.",
    )
    assert VALIDATOR.validate(value) is value


def test_b2_cannot_allow_a_professional_case_decision():
    value = contract(
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        allowed_capabilities=(
            AnswerCapability.STRUCTURE_PERSONAL_PREPARATION,
            AnswerCapability.MAKE_PROFESSIONAL_CASE_DECISION,
        ),
    )
    with pytest.raises(AnswerBoundaryValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "EXECUTING_CAPABILITY_ALLOWED"


def test_b2_cannot_claim_that_a_requested_case_decision_is_safely_handled():
    value = contract(
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        requests_professional_case_decision=True,
    )
    with pytest.raises(AnswerBoundaryValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "CASE_DECISION_MODE_MISMATCH"


@pytest.mark.parametrize(
    "capability",
    ALWAYS_FORBIDDEN_CAPABILITIES,
)
def test_every_executing_or_activating_capability_is_rejected(capability):
    value = contract(
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        allowed_capabilities=(AnswerCapability.PRESENT_GENERAL_INFORMATION, capability),
    )
    with pytest.raises(AnswerBoundaryValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "EXECUTING_CAPABILITY_ALLOWED"


def test_every_executing_capability_must_remain_explicitly_forbidden():
    value = contract(
        AnswerOperatingMode.B1_GENERAL_ORIENTATION,
        forbidden_capabilities=ALWAYS_FORBIDDEN_CAPABILITIES[:-1],
    )
    with pytest.raises(AnswerBoundaryValidationError) as error:
        VALIDATOR.validate(value)
    assert error.value.code == "REQUIRED_PROHIBITION_MISSING"


def test_contract_is_immutable():
    value = contract(AnswerOperatingMode.B1_GENERAL_ORIENTATION)
    with pytest.raises(FrozenInstanceError):
        value.effective_mode = AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED


def test_validation_is_deterministic_for_identical_typed_input():
    first = contract(AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B2_PERSONAL_PREPARATION)
    second = contract(AnswerOperatingMode.B1_GENERAL_ORIENTATION, AnswerOperatingMode.B2_PERSONAL_PREPARATION)
    assert first == second
    assert VALIDATOR.validate(first) == VALIDATOR.validate(second)


def test_validation_does_not_mutate_the_family_care_reference_journey():
    from tests.test_family_care_end_to_end_reference import build_reference_journey

    before = build_reference_journey()
    before_journey = before["journey"]
    VALIDATOR.validate(contract(AnswerOperatingMode.B2_PERSONAL_PREPARATION))
    after = build_reference_journey()
    assert after["journey"] == before_journey
    assert after["state"] == before["state"]
