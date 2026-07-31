from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.clarification import ClarificationResolution
from guardian_understanding.models import (
    Contradiction,
    Fact,
    Goal,
    Hypothesis,
    UnderstandingRevision,
    UnderstandingState,
    Unknown,
)
from life_decisions.conversation import (
    MissingInformation,
    PowerOfAttorneyConversationPreparation,
    PowerOfAttorneyConversationStatus,
    UserStatementReference,
)


@dataclass(frozen=True)
class PowerOfAttorneyUnderstandingQuestion:
    question_id: str
    missing_information_id: str
    text: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(
            self.question_id,
            "question_id",
            "understanding-question",
        )
        _identifier(
            self.missing_information_id,
            "missing_information_id",
            "missing-information",
        )
        _question(self.text)
        _text_tuple(self.source_references, "source_references")


@dataclass(frozen=True)
class PowerOfAttorneyConversationTurn:
    turn_id: str
    status: PowerOfAttorneyConversationStatus
    source_understanding_state_id: str
    source_understanding_state_hash: str
    preparation_id: str
    triggering_statement_id: str
    missing_information_id: Optional[str]
    question_id: Optional[str]
    understanding_question: Optional[str]
    question_source_references: Tuple[str, ...]
    answer_statement_id: Optional[str]
    resolution_id: Optional[str]
    revision_reference: Optional[str]
    resulting_understanding_state_id: Optional[str]
    resulting_understanding_state_hash: Optional[str]
    previous_turn_id: Optional[str]
    state_changed_by_turn: bool
    known_situation: Tuple[Fact, ...]
    hypotheses: Tuple[Hypothesis, ...]
    open_points: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    goals: Tuple[Goal, ...]

    def __post_init__(self) -> None:
        _identifier(self.turn_id, "turn_id", "poa-turn")
        if not isinstance(self.status, PowerOfAttorneyConversationStatus):
            raise TypeError("status is invalid")
        _identifier(
            self.source_understanding_state_id,
            "source_understanding_state_id",
            "understanding-state",
        )
        _sha256(self.source_understanding_state_hash, "source state hash")
        _identifier(self.preparation_id, "preparation_id", "poa-preparation")
        _identifier(
            self.triggering_statement_id,
            "triggering_statement_id",
            "statement",
        )
        _optional_identifier(
            self.missing_information_id,
            "missing_information_id",
            "missing-information",
        )
        if self.resulting_understanding_state_hash is not None:
            _sha256(
                self.resulting_understanding_state_hash,
                "resulting state hash",
            )
        _optional_identifier(
            self.question_id,
            "question_id",
            "understanding-question",
        )
        if self.understanding_question is not None:
            _question(self.understanding_question)
        _optional_text_tuple(
            self.question_source_references,
            "question_source_references",
        )
        _optional_identifier(
            self.answer_statement_id,
            "answer_statement_id",
            "statement",
        )
        _optional_identifier(
            self.resolution_id,
            "resolution_id",
            "clarification-resolution",
        )
        if self.revision_reference is not None:
            _text(self.revision_reference, "revision_reference")
        _optional_identifier(
            self.resulting_understanding_state_id,
            "resulting_understanding_state_id",
            "understanding-state",
        )
        _optional_identifier(
            self.previous_turn_id,
            "previous_turn_id",
            "poa-turn",
        )
        if self.state_changed_by_turn is not False:
            raise ValueError("A conversation turn cannot change state")
        _items(self.known_situation, Fact, "known_situation")
        _items(self.hypotheses, Hypothesis, "hypotheses")
        _items(self.open_points, Unknown, "open_points")
        _items(self.contradictions, Contradiction, "contradictions")
        _items(self.goals, Goal, "goals")
        actual_hash = understanding_state_content_hash(
            UnderstandingState(
                self.known_situation,
                self.hypotheses,
                self.open_points,
                self.contradictions,
                self.goals,
            )
        )
        if self.source_understanding_state_hash != actual_hash:
            raise ValueError("Source state hash does not match turn content")
        if (
            self.resulting_understanding_state_hash is not None
            and self.resulting_understanding_state_hash != actual_hash
        ):
            raise ValueError("Resulting state hash does not match turn content")


@dataclass(frozen=True)
class PowerOfAttorneyConversationTurnInput:
    source_understanding_state_id: str
    source_understanding_state_hash: str
    understanding_state: UnderstandingState
    preparation: PowerOfAttorneyConversationPreparation
    question: Optional[PowerOfAttorneyUnderstandingQuestion]
    previous_turns: Tuple[PowerOfAttorneyConversationTurn, ...] = ()
    answer_statement: Optional[UserStatementReference] = None
    resolution: Optional[ClarificationResolution] = None
    revision: Optional[UnderstandingRevision] = None
    revision_reference: Optional[str] = None
    resulting_understanding_state_id: Optional[str] = None
    resulting_understanding_state_hash: Optional[str] = None

    def __post_init__(self) -> None:
        _identifier(
            self.source_understanding_state_id,
            "source_understanding_state_id",
            "understanding-state",
        )
        if not isinstance(self.understanding_state, UnderstandingState):
            raise TypeError("understanding_state is invalid")
        _sha256(self.source_understanding_state_hash, "source state hash")
        if self.source_understanding_state_hash != understanding_state_content_hash(
            self.understanding_state
        ):
            raise ValueError("Source state hash does not match UnderstandingState")
        if not isinstance(
            self.preparation,
            PowerOfAttorneyConversationPreparation,
        ):
            raise TypeError("preparation is invalid")
        if self.preparation.understanding_state_id != self.source_understanding_state_id:
            raise ValueError("Preparation does not belong to source state")
        if self.question is not None and not isinstance(
            self.question,
            PowerOfAttorneyUnderstandingQuestion,
        ):
            raise TypeError("question is invalid")
        _items(
            self.previous_turns,
            PowerOfAttorneyConversationTurn,
            "previous_turns",
        )
        if len({turn.turn_id for turn in self.previous_turns}) != len(
            self.previous_turns
        ):
            raise ValueError("previous_turns must be unique")
        if self.answer_statement is not None and not isinstance(
            self.answer_statement,
            UserStatementReference,
        ):
            raise TypeError("answer_statement is invalid")
        if self.resolution is not None and not isinstance(
            self.resolution,
            ClarificationResolution,
        ):
            raise TypeError("resolution is invalid")
        if self.revision is not None and not isinstance(
            self.revision,
            UnderstandingRevision,
        ):
            raise TypeError("revision is invalid")
        self._validate_question()
        self._validate_lineage()

    def _validate_question(self) -> None:
        essential = tuple(
            item for item in self.preparation.missing_information if item.essential
        )
        if not essential:
            if self.question is not None:
                raise ValueError("Ready preparation cannot contain a question")
            return
        if self.question is None:
            raise ValueError("Essential missing information requires a question")
        first = essential[0]
        if self.question.missing_information_id != first.information_id:
            raise ValueError("Question must reference the first essential gap")
        if first.source_reference not in self.question.source_references:
            raise ValueError("Question must retain the missing-information source")
        if self.preparation.next_understanding_question != self.question.text:
            raise ValueError("Question must match the preparation question")

    def _validate_lineage(self) -> None:
        lineage = (
            self.answer_statement,
            self.resolution,
            self.revision,
            self.revision_reference,
            self.resulting_understanding_state_id,
            self.resulting_understanding_state_hash,
        )
        if not any(item is not None for item in lineage):
            if (
                self.previous_turns
                and self.previous_turns[-1].source_understanding_state_id
                != self.source_understanding_state_id
            ):
                raise ValueError("Previous turn does not belong to source state")
            return
        if not all(item is not None for item in lineage):
            raise ValueError("External clarification lineage must be complete")
        if not self.previous_turns:
            raise ValueError("External clarification requires a previous turn")
        previous = self.previous_turns[-1]
        assert self.answer_statement is not None
        assert self.resolution is not None
        assert self.revision is not None
        assert self.resulting_understanding_state_id is not None
        assert self.resulting_understanding_state_hash is not None
        if previous.question_id != self.resolution.question_id:
            raise ValueError("Resolution does not answer the previous turn")
        if (
            self.answer_statement.statement_id != self.resolution.answer_statement_id
            or self.answer_statement.text != self.resolution.answer_text
        ):
            raise ValueError("Answer statement does not match resolution")
        if self.revision.state != self.understanding_state:
            raise ValueError("Revision state does not match current state")
        if self.resolution.selected_operation is None or not self.revision.changes:
            raise ValueError("Clarification did not produce a revision")
        selected = self.resolution.selected_operation
        source_texts = tuple(
            item.text
            for collection in (
                previous.known_situation,
                previous.hypotheses,
                previous.open_points,
                previous.contradictions,
                previous.goals,
            )
            for item in collection
        )
        if selected.target_text is not None and selected.target_text not in source_texts:
            raise ValueError("Selected operation target is outside source state")
        if not any(
            change.operation is selected.operation
            and change.source_statement == self.answer_statement.text
            and change.target_text == selected.target_text
            and (
                selected.value_text is None
                or change.result_text == selected.value_text
            )
            for change in self.revision.changes
        ):
            raise ValueError("Revision does not match selected operation")
        if self.resulting_understanding_state_id != self.source_understanding_state_id:
            raise ValueError("Resulting state reference does not match source state")
        if self.resulting_understanding_state_hash != self.source_understanding_state_hash:
            raise ValueError("Resulting state hash does not match source state")


class GuardianPowerOfAttorneyConversationService:
    """Produces one explicit turn without interpreting answers or changing state."""

    def next_turn(
        self,
        turn_input: PowerOfAttorneyConversationTurnInput,
    ) -> PowerOfAttorneyConversationTurn:
        if not isinstance(turn_input, PowerOfAttorneyConversationTurnInput):
            raise TypeError("turn_input is invalid")
        preparation = turn_input.preparation
        question = turn_input.question
        status = preparation.status
        matching_turns = tuple(
            turn
            for turn in turn_input.previous_turns
            if question is not None
            and turn.missing_information_id == question.missing_information_id
            and turn.question_id == question.question_id
            and turn.understanding_question == question.text
        )
        relevant_previous = matching_turns[0] if matching_turns else None
        if relevant_previous is not None:
            status = PowerOfAttorneyConversationStatus.QUESTION_UNRESOLVED
        return PowerOfAttorneyConversationTurn(
            turn_id=_turn_id(turn_input, status),
            status=status,
            source_understanding_state_id=turn_input.source_understanding_state_id,
            source_understanding_state_hash=(
                turn_input.source_understanding_state_hash
            ),
            preparation_id=preparation.preparation_id,
            triggering_statement_id=preparation.triggering_statement.statement_id,
            missing_information_id=(
                question.missing_information_id if question is not None else None
            ),
            question_id=question.question_id if question is not None else None,
            understanding_question=question.text if question is not None else None,
            question_source_references=(
                question.source_references if question is not None else ()
            ),
            answer_statement_id=(
                turn_input.answer_statement.statement_id
                if turn_input.answer_statement is not None
                else None
            ),
            resolution_id=(
                turn_input.resolution.resolution_id
                if turn_input.resolution is not None
                else None
            ),
            revision_reference=turn_input.revision_reference,
            resulting_understanding_state_id=(
                turn_input.resulting_understanding_state_id
            ),
            resulting_understanding_state_hash=(
                turn_input.resulting_understanding_state_hash
            ),
            previous_turn_id=(
                relevant_previous.turn_id
                if relevant_previous is not None
                else (
                    turn_input.previous_turns[-1].turn_id
                    if turn_input.previous_turns
                    else None
                )
            ),
            state_changed_by_turn=False,
            known_situation=preparation.known_situation,
            hypotheses=preparation.hypotheses,
            open_points=preparation.open_points,
            contradictions=preparation.contradictions,
            goals=preparation.goals,
        )


def _turn_id(
    value: PowerOfAttorneyConversationTurnInput,
    status: PowerOfAttorneyConversationStatus,
) -> str:
    payload = json.dumps(
        {"input": _canonical(value), "status": status.value},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "poa-turn-{}".format(digest[:16])


def understanding_state_content_hash(state: UnderstandingState) -> str:
    if not isinstance(state, UnderstandingState):
        raise TypeError("state must be an UnderstandingState")
    payload = json.dumps(
        _canonical(state),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return tuple(_canonical(item) for item in value)
    return value


def _items(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid items".format(name))


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _text_tuple(value: object, name: str) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("{} must be a non-empty tuple".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(name))


def _optional_text_tuple(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(name))


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(
        r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix),
        value,
    ) is None:
        raise ValueError("{} is invalid".format(name))


def _optional_identifier(value: object, name: str, prefix: str) -> None:
    if value is not None:
        _identifier(value, name, prefix)


def _question(value: str) -> None:
    _text(value, "understanding question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one understanding question is required")


def _sha256(value: object, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("{} must be a lowercase SHA-256 hash".format(name))
