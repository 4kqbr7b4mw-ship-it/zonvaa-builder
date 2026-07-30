from __future__ import annotations

import re
from typing import Iterable, Tuple

from guardian_understanding.models import (
    Contradiction,
    Fact,
    Goal,
    Hypothesis,
    UnderstandingResult,
    UnderstandingState,
    Unknown,
)


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")
_CONTRADICTION_MARKERS = (
    "einerseits",
    "andererseits",
    "aber gleichzeitig",
    "zugleich aber",
    "eigentlich",
)
_UNKNOWN_MARKERS = (
    "ich weiss nicht",
    "wir wissen nicht",
    "unklar",
    "keine ahnung",
    "noch offen",
    "offen ist",
)
_HYPOTHESIS_MARKERS = (
    "vielleicht",
    "eventuell",
    "möglicherweise",
    "ich glaube",
    "wir glauben",
    "ich vermute",
    "wir vermuten",
    "ich überlege",
    "wir überlegen",
    "könnte",
    "könnten",
)
_GOAL_MARKERS = (
    "ich möchte",
    "wir möchten",
    "ich will",
    "wir wollen",
    "mein ziel",
    "unser ziel",
    "mir geht es darum",
    "uns geht es darum",
)
_FORBIDDEN_QUESTION_TERMS = (
    "workflow",
    "routing",
    "intent",
    "entscheidung starten",
    "fähigkeit aktivieren",
)


class GuardianUnderstandingService:
    """Builds transient understanding without choosing or doing anything."""

    def understand(self, user_input: str) -> UnderstandingResult:
        normalized = _normalize_input(user_input)
        facts = []
        hypotheses = []
        unknowns = []
        contradictions = []
        goals = []

        for statement in _statements(normalized):
            lowered = statement.casefold()
            if _is_contradiction(lowered):
                contradictions.append(Contradiction(statement))
            elif _contains(lowered, _UNKNOWN_MARKERS):
                unknowns.append(Unknown(statement))
            elif _contains(lowered, _GOAL_MARKERS):
                goals.append(Goal(statement))
            elif _contains(lowered, _HYPOTHESIS_MARKERS):
                hypotheses.append(Hypothesis(statement))
            else:
                facts.append(Fact(statement))

        state = UnderstandingState(
            facts=tuple(facts),
            hypotheses=tuple(hypotheses),
            unknowns=tuple(unknowns),
            contradictions=tuple(contradictions),
            goals=tuple(goals),
        )
        return UnderstandingResult(
            state=state,
            understanding_question=_understanding_question(state),
        )


def _normalize_input(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("user_input must be text")
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("user_input must not be empty")
    if "\x00" in normalized:
        raise ValueError("user_input contains invalid data")
    return normalized


def _statements(value: str) -> Tuple[str, ...]:
    return tuple(
        statement.strip()
        for statement in _SENTENCE_BOUNDARY.split(value)
        if statement.strip()
    )


def _contains(value: str, markers: Iterable[str]) -> bool:
    return any(marker in value for marker in markers)


def _is_contradiction(value: str) -> bool:
    return (
        ("einerseits" in value and "andererseits" in value)
        or ("eigentlich" in value and "aber" in value)
        or _contains(value, ("aber gleichzeitig", "zugleich aber"))
    )


def _understanding_question(state: UnderstandingState) -> str:
    if state.contradictions:
        question = "Welche der widersprüchlichen Aussagen beschreibt Ihre Situation im Moment am besten?"
    elif state.unknowns:
        question = "Was davon wäre für Ihr Verständnis jetzt am wichtigsten zu klären?"
    elif state.hypotheses:
        question = "Was davon ist für Sie bereits sicher und was noch eine Vermutung?"
    elif state.goals:
        question = "Was möchten Sie daran zuerst besser verstehen?"
    else:
        question = "Was ist Ihnen daran im Moment am wichtigsten?"
    lowered = question.casefold()
    if _contains(lowered, _FORBIDDEN_QUESTION_TERMS):
        raise RuntimeError("Understanding question contains forbidden system language")
    return question
