from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Optional, Tuple

from guardian_understanding.models import (
    UnderstandingOperation,
    UnderstandingRevision,
    UnderstandingState,
    UnderstandingUpdate,
)
from guardian_understanding.service import GuardianUnderstandingService


@dataclass(frozen=True)
class UnderstandingProposalCandidate:
    operation: UnderstandingOperation
    source_reference: str
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.operation, UnderstandingOperation):
            raise TypeError("operation must be an UnderstandingOperation")
        _text(self.source_reference, "source_reference")
        _text(self.rationale, "rationale")


@dataclass(frozen=True)
class UnderstandingProposal:
    proposal_id: str
    statement_id: str
    user_statement: str
    operation: UnderstandingOperation
    source_reference: str
    rationale: str
    is_fact: bool = False
    changes_state: bool = False

    def __post_init__(self) -> None:
        _identifier(self.proposal_id, "proposal_id", "understanding-proposal")
        _identifier(self.statement_id, "statement_id", "statement")
        _text(self.user_statement, "user_statement")
        if not isinstance(self.operation, UnderstandingOperation):
            raise TypeError("operation must be an UnderstandingOperation")
        _text(self.source_reference, "source_reference")
        _text(self.rationale, "rationale")
        if self.is_fact is not False:
            raise ValueError("A proposal must never be marked as a fact")
        if self.changes_state is not False:
            raise ValueError("A proposal must never claim a state change")


@dataclass(frozen=True)
class UnderstandingProposalSet:
    statement_id: str
    user_statement: str
    proposals: Tuple[UnderstandingProposal, ...]
    understanding_question: Optional[str]
    understanding_question_id: Optional[str]

    def __post_init__(self) -> None:
        _identifier(self.statement_id, "statement_id", "statement")
        _text(self.user_statement, "user_statement")
        if not isinstance(self.proposals, tuple) or not self.proposals:
            raise ValueError("proposals must be a non-empty tuple")
        if not all(
            isinstance(proposal, UnderstandingProposal)
            for proposal in self.proposals
        ):
            raise TypeError("proposals contains invalid items")
        if len({proposal.proposal_id for proposal in self.proposals}) != len(
            self.proposals
        ):
            raise ValueError("proposal IDs must be unique")
        if any(
            proposal.statement_id != self.statement_id
            or proposal.user_statement != self.user_statement
            for proposal in self.proposals
        ):
            raise ValueError("All proposals must reference the same statement")
        if self.understanding_question is not None:
            _question(self.understanding_question)
            _identifier(
                self.understanding_question_id,
                "understanding_question_id",
                "understanding-question",
            )
        elif self.understanding_question_id is not None:
            raise ValueError(
                "A question ID requires an understanding question"
            )
        if len(self.proposals) > 1 and self.understanding_question is None:
            raise ValueError(
                "Alternative proposals require one understanding question"
            )


@dataclass(frozen=True)
class UnderstandingProposalSelection:
    proposal_id: str

    def __post_init__(self) -> None:
        _identifier(self.proposal_id, "proposal_id", "understanding-proposal")


@dataclass(frozen=True)
class UnderstandingProposalApplication:
    selection: UnderstandingProposalSelection
    selected_proposal: UnderstandingProposal
    revision: UnderstandingRevision

    def __post_init__(self) -> None:
        if not isinstance(self.selection, UnderstandingProposalSelection):
            raise TypeError("selection is invalid")
        if not isinstance(self.selected_proposal, UnderstandingProposal):
            raise TypeError("selected_proposal is invalid")
        if not isinstance(self.revision, UnderstandingRevision):
            raise TypeError("revision is invalid")
        if self.selection.proposal_id != self.selected_proposal.proposal_id:
            raise ValueError("Selection and proposal do not match")


class GuardianUnderstandingProposalService:
    """Separates possible interpretation from deterministic state revision."""

    def __init__(
        self,
        understanding: Optional[GuardianUnderstandingService] = None,
    ) -> None:
        self.understanding = understanding or GuardianUnderstandingService()

    def create(
        self,
        existing: UnderstandingState,
        statement_id: str,
        user_statement: str,
        candidates: Tuple[UnderstandingProposalCandidate, ...],
        understanding_question: Optional[str] = None,
        understanding_question_id: Optional[str] = None,
    ) -> UnderstandingProposalSet:
        if not isinstance(existing, UnderstandingState):
            raise TypeError("existing must be an UnderstandingState")
        _identifier(statement_id, "statement_id", "statement")
        _text(user_statement, "user_statement")
        if not isinstance(candidates, tuple) or not candidates:
            raise ValueError("candidates must be a non-empty tuple")
        if not all(
            isinstance(candidate, UnderstandingProposalCandidate)
            for candidate in candidates
        ):
            raise TypeError("candidates contains invalid items")
        question = understanding_question
        if len(candidates) > 1 and question is None:
            question = (
                "Welche dieser möglichen Einordnungen trifft Ihre Aussage "
                "am besten?"
            )
        proposals = tuple(
            UnderstandingProposal(
                proposal_id=_proposal_id(
                    statement_id,
                    user_statement,
                    candidate,
                ),
                statement_id=statement_id,
                user_statement=user_statement,
                operation=candidate.operation,
                source_reference=candidate.source_reference,
                rationale=candidate.rationale,
            )
            for candidate in candidates
        )
        if understanding_question_id is not None:
            if question is None:
                raise ValueError("A controlled question ID requires a question")
            _identifier(
                understanding_question_id,
                "understanding_question_id",
                "understanding-question",
            )
        return UnderstandingProposalSet(
            statement_id=statement_id,
            user_statement=user_statement,
            proposals=proposals,
            understanding_question=question,
            understanding_question_id=(
                understanding_question_id
                if understanding_question_id is not None
                else (
                    _question_id(statement_id, question, proposals)
                    if question is not None
                    else None
                )
            ),
        )

    def apply(
        self,
        existing: UnderstandingState,
        proposal_set: UnderstandingProposalSet,
        selection: UnderstandingProposalSelection,
    ) -> UnderstandingProposalApplication:
        if not isinstance(existing, UnderstandingState):
            raise TypeError("existing must be an UnderstandingState")
        if not isinstance(proposal_set, UnderstandingProposalSet):
            raise TypeError("proposal_set is invalid")
        if not isinstance(selection, UnderstandingProposalSelection):
            raise TypeError("selection is invalid")
        matches = tuple(
            proposal
            for proposal in proposal_set.proposals
            if proposal.proposal_id == selection.proposal_id
        )
        if len(matches) != 1:
            raise ValueError("Unknown proposal ID")
        selected = matches[0]
        revision = self.understanding.advance(
            existing,
            UnderstandingUpdate(
                user_statement=selected.user_statement,
                operations=(selected.operation,),
            ),
        )
        return UnderstandingProposalApplication(
            selection=selection,
            selected_proposal=selected,
            revision=revision,
        )


def _proposal_id(
    statement_id: str,
    user_statement: str,
    candidate: UnderstandingProposalCandidate,
) -> str:
    payload = json.dumps(
        {
            "statement_id": statement_id,
            "user_statement": user_statement,
            "operation": candidate.operation.operation.value,
            "target_text": candidate.operation.target_text,
            "value_text": candidate.operation.value_text,
            "source_reference": candidate.source_reference,
            "rationale": candidate.rationale,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "understanding-proposal-{}".format(digest[:16])


def _question_id(
    statement_id: str,
    question: str,
    proposals: Tuple[UnderstandingProposal, ...],
) -> str:
    payload = json.dumps(
        {
            "statement_id": statement_id,
            "question": question,
            "proposal_ids": tuple(
                proposal.proposal_id for proposal in proposals
            ),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "understanding-question-{}".format(digest[:16])


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(
        r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix),
        value,
    ) is None:
        raise ValueError("{} is invalid".format(name))


def _question(value: str) -> None:
    _text(value, "understanding_question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one understanding question is required")
