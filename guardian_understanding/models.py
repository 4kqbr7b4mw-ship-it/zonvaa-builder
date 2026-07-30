from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Fact:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


@dataclass(frozen=True)
class Hypothesis:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


@dataclass(frozen=True)
class Unknown:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


@dataclass(frozen=True)
class Contradiction:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


@dataclass(frozen=True)
class Goal:
    text: str

    def __post_init__(self) -> None:
        _validate_text(self.text)


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
