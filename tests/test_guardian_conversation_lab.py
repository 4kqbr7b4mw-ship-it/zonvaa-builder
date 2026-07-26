import json
from pathlib import Path
import re

from life_decisions import PowerOfAttorneyWorkflow
from tests.guardian_conversation_lab_data import (
    AGE_GROUPS,
    DECISION_SPACES,
    EDUCATION_CONTEXTS,
    EMOTIONAL_STATES,
    NEED_TYPES,
    STYLES,
    build_conversation_lab,
)


MATRIX_PATH = (
    Path(__file__).resolve().parents[1]
    / "knowledge"
    / "sources"
    / "guardian-conversation-lab.json"
)

SCORE_FIELDS = {
    "sympathy",
    "trust",
    "naturalness",
    "listening",
    "summary_accuracy",
    "no_premature_interpretation",
    "no_assumed_intent",
    "follow_up_quality",
    "conversation_flow",
    "svnp_compliance",
}


def matrix():
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def guardian_text(case):
    conversation = case["conversation"]
    return "{} {}".format(
        conversation["guardian_summary"],
        conversation["guardian_follow_up"],
    )


def test_generated_matrix_is_current_and_contains_exactly_100_cases():
    stored = matrix()
    generated = build_conversation_lab()

    assert stored == generated
    assert stored["schema_version"] == "1.0"
    assert stored["principle"] == "SVNP"
    assert stored["case_count"] == 100
    assert len(stored["cases"]) == 100


def test_cases_are_not_repeated_variants_of_one_pattern():
    cases = matrix()["cases"]

    assert len({case["id"] for case in cases}) == 100
    assert len(
        {
            case["conversation"]["user_opening"]
            for case in cases
        }
    ) == 100
    assert len(
        {
            case["conversation"]["guardian_summary"]
            for case in cases
        }
    ) == 100
    assert len(
        {
            case["conversation"]["guardian_follow_up"]
            for case in cases
        }
    ) == 100
    topics = [case["topic"] for case in cases]
    assert len(set(topics)) == 25
    assert max(topics.count(topic) for topic in set(topics)) == 4


def test_required_diversity_dimensions_are_covered():
    cases = matrix()["cases"]
    coverage = [case["coverage"] for case in cases]

    assert {item["communication_style"] for item in coverage} == set(
        STYLES
    )
    assert {item["age_group"] for item in coverage} == set(AGE_GROUPS)
    assert {item["education_context"] for item in coverage} == set(
        EDUCATION_CONTEXTS
    )
    assert {item["emotional_state"] for item in coverage} == set(
        EMOTIONAL_STATES
    )
    assert {
        case["background"]["need_type"] for case in cases
    } == set(NEED_TYPES)
    assert {
        case["background"]["decision_space"] for case in cases
    } == set(DECISION_SPACES)


def test_each_first_turn_listens_summarizes_and_asks_naturally():
    for case in matrix()["cases"]:
        conversation = case["conversation"]
        summary = conversation["guardian_summary"]
        follow_up = conversation["guardian_follow_up"]
        text = guardian_text(case).lower()

        assert conversation["user_opening"].strip()
        assert summary.strip()
        assert "?" not in summary
        assert follow_up.endswith("?")
        assert len(summary.split()) <= 20
        assert len(follow_up.split()) <= 16
        assert "is that right" not in text
        assert "is that correct" not in text
        assert "please confirm" not in text


def test_background_classification_remains_invisible():
    for case in matrix()["cases"]:
        background = case["background"]
        text = guardian_text(case).lower()

        assert background["workflow_checked"] is True
        assert background["workflow_visible_to_user"] is False
        assert "workflow" not in text


def test_known_workflow_is_referenced_only_for_its_existing_space():
    cases = matrix()["cases"]
    matched = [
        case for case in cases
        if case["background"]["workflow_match"] is not None
    ]

    assert len(matched) == 4
    assert {
        case["background"]["workflow_match"] for case in matched
    } == {PowerOfAttorneyWorkflow.WORKFLOW_TYPE}
    assert {case["topic"] for case in matched} == {"power_of_attorney"}
    assert all(
        case["background"]["decision_space"] == "known"
        for case in matched
    )
    assert all(
        case["background"]["workflow_match"] is None
        for case in cases
        if case["background"]["decision_space"] == "new"
    )


def test_guardian_turn_contains_no_solution_price_or_advice_jump():
    forbidden_phrases = (
        "you should",
        "i recommend",
        "buy now",
        "upload",
        "price",
        "payment",
        "upgrade",
        "legally effective",
        "diagnosis",
    )
    for case in matrix()["cases"]:
        text = guardian_text(case).lower()
        assert not any(phrase in text for phrase in forbidden_phrases)
        assert not text.startswith("you need to ")
        assert ". you need to " not in text


def test_cases_contain_no_direct_identifiers_or_sensitive_documents():
    serialized = json.dumps(matrix(), ensure_ascii=False)

    assert not re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        serialized,
        re.IGNORECASE,
    )
    assert not re.search(r"\+?\d[\d ()/-]{8,}\d", serialized)
    assert "document_content" not in serialized
    assert "storage_reference" not in serialized
    assert "data:application" not in serialized


def test_every_case_has_complete_bounded_evaluation():
    for case in matrix()["cases"]:
        evaluation = case["evaluation"]

        assert SCORE_FIELDS <= set(evaluation)
        for field in SCORE_FIELDS:
            assert isinstance(evaluation[field], int)
            assert 1 <= evaluation[field] <= 5
        assert evaluation["risks"]
        assert all(
            isinstance(risk, str) and risk.strip()
            for risk in evaluation["risks"]
        )
        assert evaluation["necessary_improvement"].strip()
