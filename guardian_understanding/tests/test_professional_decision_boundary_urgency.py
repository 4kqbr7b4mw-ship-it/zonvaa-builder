import inspect

import pytest

from guardian_understanding import (
    ProfessionalDecisionBoundaryValidationError,
    UrgencyStatus,
)
from guardian_understanding import professional_decision_boundary as module
from guardian_understanding.tests.test_professional_decision_boundary_contract import (
    VALIDATOR,
    professional_boundary,
)


def test_not_declared_urgent_allows_no_notice_or_a_supplied_notice():
    assert VALIDATOR.validate(professional_boundary()).urgent_help_notice is None
    assert VALIDATOR.validate(
        professional_boundary(urgent_help_notice="Bereitgestellter Hinweis.")
    )


def test_urgent_professional_review_accepts_supplied_notice():
    value = professional_boundary(
        urgency_status=UrgencyStatus.URGENT_PROFESSIONAL_REVIEW,
        urgent_help_notice="Eine zeitnahe professionelle Prüfung wurde benannt.",
    )
    assert VALIDATOR.validate(value) is value


def test_immediate_help_requires_a_supplied_non_empty_notice():
    with pytest.raises(ProfessionalDecisionBoundaryValidationError) as error:
        VALIDATOR.validate(
            professional_boundary(urgency_status=UrgencyStatus.IMMEDIATE_HELP_REQUIRED)
        )
    assert error.value.code == "URGENT_HELP_NOTICE_REQUIRED"
    value = professional_boundary(
        urgency_status=UrgencyStatus.IMMEDIATE_HELP_REQUIRED,
        urgent_help_notice="Bereitgestellter Soforthilfehinweis.",
    )
    assert VALIDATOR.validate(value) is value


def test_urgency_is_only_supplied_without_detection_triage_or_contact():
    source = inspect.getsource(module)
    for forbidden in ("detect(", "triage(", "locate(", "contact(", "call(", "requests", "urllib"):
        assert forbidden not in source
