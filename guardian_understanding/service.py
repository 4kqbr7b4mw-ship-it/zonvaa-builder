from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable, Tuple

from guardian_understanding.models import (
    Contradiction,
    Fact,
    FactStatus,
    Goal,
    GoalStatus,
    Hypothesis,
    HypothesisStatus,
    UnderstandingChange,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingRevision,
    UnderstandingResult,
    UnderstandingState,
    UnderstandingUpdate,
    Unknown,
    UnknownStatus,
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

    def advance(
        self,
        existing: UnderstandingState,
        update: UnderstandingUpdate,
    ) -> UnderstandingRevision:
        if not isinstance(existing, UnderstandingState):
            raise TypeError("existing must be an UnderstandingState")
        if not isinstance(update, UnderstandingUpdate):
            raise TypeError("update must be an UnderstandingUpdate")

        state = existing
        changes = []
        for operation in update.operations:
            state, change = _apply_operation(
                state,
                operation,
                update.user_statement,
            )
            changes.append(change)
        return UnderstandingRevision(
            state=state,
            changes=tuple(changes),
            understanding_question=_understanding_question(state),
        )


def _apply_operation(
    state: UnderstandingState,
    requested: UnderstandingOperation,
    source_statement: str,
) -> Tuple[UnderstandingState, UnderstandingChange]:
    operation = requested.operation
    target = requested.target_text
    value = requested.value_text

    if operation is UnderstandingOperationType.ADD_FACT:
        value = _required(value, operation)
        state = replace(state, facts=_append_unique(state.facts, Fact(value)))
    elif operation is UnderstandingOperationType.CONFIRM_FACT:
        target = _required(target, operation)
        state = replace(
            state,
            facts=_replace_status(state.facts, target, FactStatus.CONFIRMED),
        )
        value = target
    elif operation is UnderstandingOperationType.CORRECT_FACT:
        target = _required(target, operation)
        value = _required(value, operation)
        corrected = _replace_status(state.facts, target, FactStatus.CORRECTED)
        corrected = _append_unique(corrected, Fact(value))
        state = replace(
            state,
            facts=corrected,
            contradictions=_append_unique(
                state.contradictions,
                Contradiction("{} <> {}".format(target, value)),
            ),
        )
    elif operation is UnderstandingOperationType.MARK_FACT_CONTRADICTORY:
        target = _required(target, operation)
        value = _required(value, operation)
        state = replace(
            state,
            facts=_replace_status(
                state.facts,
                target,
                FactStatus.CONTRADICTED,
            ),
            contradictions=_append_unique(
                state.contradictions,
                Contradiction("{} <> {}".format(target, value)),
            ),
        )
    elif operation is UnderstandingOperationType.ADD_HYPOTHESIS:
        value = _required(value, operation)
        state = replace(
            state,
            hypotheses=_append_unique(
                state.hypotheses,
                Hypothesis(value),
            ),
        )
    elif operation is UnderstandingOperationType.REFINE_HYPOTHESIS:
        target = _required(target, operation)
        value = _required(value, operation)
        hypotheses = _replace_status(
            state.hypotheses,
            target,
            HypothesisStatus.REFINED,
        )
        state = replace(
            state,
            hypotheses=_append_unique(hypotheses, Hypothesis(value)),
        )
    elif operation is UnderstandingOperationType.WEAKEN_HYPOTHESIS:
        target = _required(target, operation)
        state = replace(
            state,
            hypotheses=_replace_status(
                state.hypotheses,
                target,
                HypothesisStatus.WEAKENED,
            ),
        )
        value = target
    elif operation is UnderstandingOperationType.REJECT_HYPOTHESIS:
        target = _required(target, operation)
        state = replace(
            state,
            hypotheses=_replace_status(
                state.hypotheses,
                target,
                HypothesisStatus.REJECTED,
            ),
        )
    elif operation is UnderstandingOperationType.ADD_UNKNOWN:
        value = _required(value, operation)
        state = replace(
            state,
            unknowns=_append_unique(state.unknowns, Unknown(value)),
        )
    elif operation is UnderstandingOperationType.REFINE_UNKNOWN:
        target = _required(target, operation)
        value = _required(value, operation)
        unknowns = _replace_status(
            state.unknowns,
            target,
            UnknownStatus.REFINED,
        )
        state = replace(
            state,
            unknowns=_append_unique(unknowns, Unknown(value)),
        )
    elif operation is UnderstandingOperationType.CLOSE_UNKNOWN:
        target = _required(target, operation)
        state = replace(
            state,
            unknowns=_replace_status(
                state.unknowns,
                target,
                UnknownStatus.CLOSED,
            ),
        )
    elif operation is UnderstandingOperationType.ADD_CONTRADICTION:
        value = _required(value, operation)
        state = replace(
            state,
            contradictions=_append_unique(
                state.contradictions,
                Contradiction(value),
            ),
        )
    elif operation is UnderstandingOperationType.ADD_GOAL:
        value = _required(value, operation)
        state = replace(
            state,
            goals=_append_unique(state.goals, Goal(value)),
        )
    elif operation is UnderstandingOperationType.CHANGE_GOAL:
        target = _required(target, operation)
        value = _required(value, operation)
        goals = _replace_status(state.goals, target, GoalStatus.CHANGED)
        state = replace(state, goals=_append_unique(goals, Goal(value)))
    elif operation is UnderstandingOperationType.CONFIRM_GOAL:
        target = _required(target, operation)
        state = replace(
            state,
            goals=_replace_status(
                state.goals,
                target,
                GoalStatus.CONFIRMED,
            ),
        )
        value = target
    elif operation is UnderstandingOperationType.DEACTIVATE_GOAL:
        target = _required(target, operation)
        state = replace(
            state,
            goals=_replace_status(
                state.goals,
                target,
                GoalStatus.NOT_CURRENT,
            ),
        )
    else:
        raise ValueError("Unsupported understanding operation")

    return state, UnderstandingChange(
        operation=operation,
        source_statement=source_statement,
        target_text=target,
        result_text=value,
    )


def _required(value: object, operation: UnderstandingOperationType) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} requires a text value".format(operation.value))
    return value


def _append_unique(items: Tuple[object, ...], item: object) -> Tuple[object, ...]:
    if item in items:
        return items
    return items + (item,)


def _replace_status(
    items: Tuple[object, ...],
    target_text: str,
    status: object,
) -> Tuple[object, ...]:
    matches = tuple(
        index
        for index, item in enumerate(items)
        if getattr(item, "text", None) == target_text
    )
    if len(matches) != 1:
        raise ValueError(
            "Operation target must match exactly one existing item: {}".format(
                target_text
            )
        )
    index = matches[0]
    return items[:index] + (replace(items[index], status=status),) + items[index + 1:]


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
    elif any(item.status is not UnknownStatus.CLOSED for item in state.unknowns):
        question = "Was davon wäre für Ihr Verständnis jetzt am wichtigsten zu klären?"
    elif any(
        item.status is not HypothesisStatus.REJECTED
        for item in state.hypotheses
    ):
        question = "Was davon ist für Sie bereits sicher und was noch eine Vermutung?"
    elif any(
        item.status in (GoalStatus.CURRENT, GoalStatus.CONFIRMED)
        for item in state.goals
    ):
        question = "Was möchten Sie daran zuerst besser verstehen?"
    else:
        question = "Was ist Ihnen daran im Moment am wichtigsten?"
    lowered = question.casefold()
    if _contains(lowered, _FORBIDDEN_QUESTION_TERMS):
        raise RuntimeError("Understanding question contains forbidden system language")
    return question
