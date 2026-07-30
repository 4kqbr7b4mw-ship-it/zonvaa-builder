from dataclasses import FrozenInstanceError, fields

import pytest

from guardian_understanding import (
    Fact,
    Goal,
    GuardianUnderstandingService,
    Hypothesis,
    UnderstandingState,
    Unknown,
)


def understand(text: str):
    return GuardianUnderstandingService().understand(text)


def test_simple_conversation_start_is_kept_as_fact():
    result = understand("Ich bin heute ziemlich erschöpft.")
    assert result.state.facts == (Fact("Ich bin heute ziemlich erschöpft."),)
    assert result.state.hypotheses == ()


def test_real_estate_example_remains_an_open_hypothesis():
    result = understand("Wir überlegen, ein Haus zu kaufen.")
    assert result.state.hypotheses == (
        Hypothesis("Wir überlegen, ein Haus zu kaufen."),
    )
    assert result.state.goals == ()


def test_incomplete_information_is_unknown():
    result = understand("Ich weiß nicht, ob die Unterlagen vollständig sind.")
    assert result.state.unknowns == (
        Unknown("Ich weiß nicht, ob die Unterlagen vollständig sind."),
    )


def test_multiple_possible_hypotheses_remain_separate():
    result = understand(
        "Vielleicht ziehe ich um. Möglicherweise bleibe ich aber auch hier."
    )
    assert len(result.state.hypotheses) == 2
    assert result.state.facts == ()


def test_explicit_contradiction_is_preserved():
    result = understand(
        "Einerseits möchte ich wechseln, andererseits möchte ich bleiben."
    )
    assert len(result.state.contradictions) == 1
    assert result.state.facts == ()


def test_unknowns_do_not_become_hypotheses_or_facts():
    result = understand("Unklar ist, wann meine Schwester Zeit hat.")
    assert len(result.state.unknowns) == 1
    assert result.state.hypotheses == ()
    assert result.state.facts == ()


def test_explicit_conversation_goal_is_recorded():
    result = understand("Ich möchte besser verstehen, warum mich das belastet.")
    assert result.state.goals == (
        Goal("Ich möchte besser verstehen, warum mich das belastet."),
    )


def test_result_contains_exactly_one_understanding_question():
    result = understand("Mein Bruder hat gestern angerufen.")
    assert result.understanding_question.count("?") == 1
    assert result.understanding_question.endswith("?")


def test_state_has_exactly_the_five_approved_categories():
    assert tuple(item.name for item in fields(UnderstandingState)) == (
        "facts",
        "hypotheses",
        "unknowns",
        "contradictions",
        "goals",
    )


def test_state_is_immutable():
    result = understand("Ich habe heute frei.")
    with pytest.raises(FrozenInstanceError):
        result.state.facts = ()


def test_no_routing_or_decision_is_exposed():
    result = understand("Vielleicht wechsle ich den Beruf.")
    forbidden = {
        "route",
        "routing",
        "intent",
        "decision",
        "workflow",
        "capability",
    }
    assert forbidden.isdisjoint(vars(result.state))
    assert forbidden.isdisjoint(vars(result))


def test_question_contains_no_workflow_or_routing_terms():
    result = understand("Ich weiß nicht, wie es weitergeht.")
    lowered = result.understanding_question.casefold()
    assert "workflow" not in lowered
    assert "routing" not in lowered
    assert "fähigkeit" not in lowered


def test_mixed_input_populates_categories_without_weighting():
    result = understand(
        "Ich habe eine Wohnung. Vielleicht möchte ich umziehen. "
        "Ich weiß nicht, wann. Mein Ziel ist, die Situation besser zu verstehen."
    )
    assert len(result.state.facts) == 1
    assert len(result.state.hypotheses) == 1
    assert len(result.state.unknowns) == 1
    assert len(result.state.goals) == 1
    assert all(
        not hasattr(item, "confidence")
        and not hasattr(item, "score")
        and not hasattr(item, "priority")
        for category in (
            result.state.facts,
            result.state.hypotheses,
            result.state.unknowns,
            result.state.goals,
        )
        for item in category
    )
