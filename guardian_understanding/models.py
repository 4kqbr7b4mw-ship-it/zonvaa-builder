from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from typing import Tuple


class FactStatus(str, Enum):
    ASSERTED = "ASSERTED"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    CONTRADICTED = "CONTRADICTED"


class HypothesisStatus(str, Enum):
    OPEN = "OPEN"
    REFINED = "REFINED"
    WEAKENED = "WEAKENED"
    REJECTED = "REJECTED"


class UnknownStatus(str, Enum):
    OPEN = "OPEN"
    REFINED = "REFINED"
    CLOSED = "CLOSED"


class GoalStatus(str, Enum):
    CURRENT = "CURRENT"
    CONFIRMED = "CONFIRMED"
    CHANGED = "CHANGED"
    NOT_CURRENT = "NOT_CURRENT"


@dataclass(frozen=True)
class Fact:
    text: str
    status: FactStatus = FactStatus.ASSERTED

    def __post_init__(self) -> None:
        _validate_text(self.text)
        _validate_enum(self.status, FactStatus, "fact status")


@dataclass(frozen=True)
class Hypothesis:
    text: str
    status: HypothesisStatus = HypothesisStatus.OPEN

    def __post_init__(self) -> None:
        _validate_text(self.text)
        _validate_enum(self.status, HypothesisStatus, "hypothesis status")


@dataclass(frozen=True)
class Unknown:
    text: str
    status: UnknownStatus = UnknownStatus.OPEN

    def __post_init__(self) -> None:
        _validate_text(self.text)
        _validate_enum(self.status, UnknownStatus, "unknown status")


@dataclass(frozen=True)
class Contradiction:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


@dataclass(frozen=True)
class Goal:
    text: str
    status: GoalStatus = GoalStatus.CURRENT

    def __post_init__(self) -> None:
        _validate_text(self.text)
        _validate_enum(self.status, GoalStatus, "goal status")


@dataclass(frozen=True)
class UnderstandingState:
    facts: Tuple[Fact, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    goals: Tuple[Goal, ...]

    def __post_init__(self) -> None:
        _validate_items(self.facts, Fact, "facts")
        _validate_items(self.hypotheses, Hypothesis, "hypotheses")
        _validate_items(self.unknowns, Unknown, "unknowns")
        _validate_items(self.contradictions, Contradiction, "contradictions")
        _validate_items(self.goals, Goal, "goals")


@dataclass(frozen=True)
class UnderstandingResult:
    state: UnderstandingState
    understanding_question: str

    def __post_init__(self) -> None:
        if not isinstance(self.state, UnderstandingState):
            raise TypeError("state must be an UnderstandingState")
        _validate_text(self.understanding_question)
        if self.understanding_question.count("?") != 1:
            raise ValueError("Exactly one understanding question is required")
        if not self.understanding_question.endswith("?"):
            raise ValueError("The understanding question must end with '?'")


class UnderstandingOperationType(str, Enum):
    ADD_FACT = "ADD_FACT"
    CONFIRM_FACT = "CONFIRM_FACT"
    CORRECT_FACT = "CORRECT_FACT"
    MARK_FACT_CONTRADICTORY = "MARK_FACT_CONTRADICTORY"
    ADD_HYPOTHESIS = "ADD_HYPOTHESIS"
    REFINE_HYPOTHESIS = "REFINE_HYPOTHESIS"
    WEAKEN_HYPOTHESIS = "WEAKEN_HYPOTHESIS"
    REJECT_HYPOTHESIS = "REJECT_HYPOTHESIS"
    ADD_UNKNOWN = "ADD_UNKNOWN"
    REFINE_UNKNOWN = "REFINE_UNKNOWN"
    CLOSE_UNKNOWN = "CLOSE_UNKNOWN"
    ADD_CONTRADICTION = "ADD_CONTRADICTION"
    ADD_GOAL = "ADD_GOAL"
    CHANGE_GOAL = "CHANGE_GOAL"
    CONFIRM_GOAL = "CONFIRM_GOAL"
    DEACTIVATE_GOAL = "DEACTIVATE_GOAL"


@dataclass(frozen=True)
class UnderstandingOperation:
    operation: UnderstandingOperationType
    target_text: Optional[str] = None
    value_text: Optional[str] = None

    def __post_init__(self) -> None:
        _validate_enum(
            self.operation,
            UnderstandingOperationType,
            "understanding operation",
        )
        if self.target_text is not None:
            _validate_text(self.target_text)
        if self.value_text is not None:
            _validate_text(self.value_text)


@dataclass(frozen=True)
class UnderstandingUpdate:
    user_statement: str
    operations: Tuple[UnderstandingOperation, ...]

    def __post_init__(self) -> None:
        _validate_text(self.user_statement)
        _validate_items(
            self.operations,
            UnderstandingOperation,
            "operations",
        )


@dataclass(frozen=True)
class UnderstandingChange:
    operation: UnderstandingOperationType
    source_statement: str
    target_text: Optional[str]
    result_text: Optional[str]

    def __post_init__(self) -> None:
        _validate_enum(
            self.operation,
            UnderstandingOperationType,
            "understanding operation",
        )
        _validate_text(self.source_statement)
        if self.target_text is not None:
            _validate_text(self.target_text)
        if self.result_text is not None:
            _validate_text(self.result_text)


@dataclass(frozen=True)
class UnderstandingRevision:
    state: UnderstandingState
    changes: Tuple[UnderstandingChange, ...]
    understanding_question: str

    def __post_init__(self) -> None:
        if not isinstance(self.state, UnderstandingState):
            raise TypeError("state must be an UnderstandingState")
        _validate_items(self.changes, UnderstandingChange, "changes")
        _validate_text(self.understanding_question)
        if self.understanding_question.count("?") != 1:
            raise ValueError("Exactly one understanding question is required")
        if not self.understanding_question.endswith("?"):
            raise ValueError("The understanding question must end with '?'")


def _validate_text(value: object) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("text must be non-empty trimmed text")


def _validate_items(value: object, item_type: type, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError("{} contains invalid items".format(name))


def _validate_enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))
