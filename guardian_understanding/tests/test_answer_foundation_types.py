import inspect

from guardian_understanding import answer_foundation, classification
from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    answer_mode_protection_level,
    most_protective_answer_mode,
)


def test_all_foundation_modules_share_the_canonical_answer_mode_enum():
    assert classification.AnswerOperatingMode is AnswerOperatingMode
    assert answer_foundation.AnswerOperatingMode is AnswerOperatingMode


def test_protection_order_exists_only_in_answer_boundary_module():
    for module in (classification, answer_foundation):
        source = inspect.getsource(module)
        assert "_PROTECTION_LEVEL" not in source
        assert "class AnswerOperatingMode" not in source


def test_foundation_modules_use_the_canonical_protection_helpers():
    assert classification.answer_mode_protection_level is answer_mode_protection_level
    assert classification.most_protective_answer_mode is most_protective_answer_mode
    assert answer_foundation.answer_mode_protection_level is answer_mode_protection_level

