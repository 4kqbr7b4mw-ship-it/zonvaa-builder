from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.models import (
    UnderstandingOperation,
    UnderstandingState,
)
from guardian_understanding.proposal import (
    GuardianUnderstandingProposalService,
    UnderstandingProposalApplication,
    UnderstandingProposalSelection,
    UnderstandingProposalSet,
)


class ClarificationResolutionType(str, Enum):
    SELECT_PROPOSAL = "SELECT_PROPOSAL"
    REJECT_PROPOSALS = "REJECT_PROPOSALS"
    KEEP_OPEN = "KEEP_OPEN"
    CLOSE_WITHOUT_CHANGE = "CLOSE_WITHOUT_CHANGE"


class ProposalDispositionType(str, Enum):
    OPEN = "OPEN"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    CLOSED_WITHOUT_CHANGE = "CLOSED_WITHOUT_CHANGE"


@dataclass(frozen=True)
class ClarificationResolutionRequest:
    question_id: str
    answer_statement_id: str
    answer_text: str
    affected_proposal_ids: Tuple[str, ...]
    resolution_type: ClarificationResolutionType
    source_reference: str
    rationale: str
    selected_proposal_id: Optional[str] = None
    next_understanding_question: Optional[str] = None

    def __post_init__(self) -> None:
        _identifier(self.question_id, "question_id", "understanding-question")
        _identifier(
            self.answer_statement_id,
            "answer_statement_id",
            "statement",
        )
        _text(self.answer_text, "answer_text")
        _proposal_ids(self.affected_proposal_ids)
        if not isinstance(self.resolution_type, ClarificationResolutionType):
            raise TypeError("resolution_type is invalid")
        _text(self.source_reference, "source_reference")
        _text(self.rationale, "rationale")
        if self.selected_proposal_id is not None:
            _identifier(
                self.selected_proposal_id,
                "selected_proposal_id",
                "understanding-proposal",
            )
        if self.next_understanding_question is not None:
            _question(self.next_understanding_question)
        self._validate_resolution_shape()

    def _validate_resolution_shape(self) -> None:
        if self.resolution_type is ClarificationResolutionType.SELECT_PROPOSAL:
            if self.selected_proposal_id is None:
                raise ValueError("SELECT_PROPOSAL requires one selection")
            if self.affected_proposal_ids != (self.selected_proposal_id,):
                raise ValueError(
                    "SELECT_PROPOSAL must affect exactly the selected proposal"
                )
            if self.next_understanding_question is not None:
                raise ValueError(
                    "SELECT_PROPOSAL cannot contain a next question"
                )
        elif self.resolution_type is ClarificationResolutionType.KEEP_OPEN:
            if self.selected_proposal_id is not None:
                raise ValueError("KEEP_OPEN cannot select a proposal")
            if self.next_understanding_question is None:
                raise ValueError("KEEP_OPEN requires exactly one next question")
        else:
            if self.selected_proposal_id is not None:
                raise ValueError(
                    "Only SELECT_PROPOSAL can select a proposal"
                )
            if self.next_understanding_question is not None:
                raise ValueError(
                    "Only KEEP_OPEN can contain a next question"
                )


@dataclass(frozen=True)
class ProposalDisposition:
    proposal_id: str
    disposition: ProposalDispositionType

    def __post_init__(self) -> None:
        _identifier(
            self.proposal_id,
            "proposal_id",
            "understanding-proposal",
        )
        if not isinstance(self.disposition, ProposalDispositionType):
            raise TypeError("disposition is invalid")


@dataclass(frozen=True)
class ClarificationResolution:
    resolution_id: str
    proposal_statement_id: str
    original_user_statement: str
    question_id: str
    understanding_question: str
    answer_statement_id: str
    answer_text: str
    affected_proposal_ids: Tuple[str, ...]
    resolution_type: ClarificationResolutionType
    source_reference: str
    rationale: str
    selected_proposal_id: Optional[str]
    selected_operation: Optional[UnderstandingOperation]
    next_understanding_question: Optional[str]

    def __post_init__(self) -> None:
        _identifier(
            self.resolution_id,
            "resolution_id",
            "clarification-resolution",
        )
        _identifier(
            self.proposal_statement_id,
            "proposal_statement_id",
            "statement",
        )
        _text(self.original_user_statement, "original_user_statement")
        _identifier(self.question_id, "question_id", "understanding-question")
        _question(self.understanding_question)
        _identifier(
            self.answer_statement_id,
            "answer_statement_id",
            "statement",
        )
        _text(self.answer_text, "answer_text")
        _proposal_ids(self.affected_proposal_ids)
        if not isinstance(self.resolution_type, ClarificationResolutionType):
            raise TypeError("resolution_type is invalid")
        _text(self.source_reference, "source_reference")
        _text(self.rationale, "rationale")
        if self.selected_proposal_id is not None:
            _identifier(
                self.selected_proposal_id,
                "selected_proposal_id",
                "understanding-proposal",
            )
        if self.selected_operation is not None and not isinstance(
            self.selected_operation,
            UnderstandingOperation,
        ):
            raise TypeError("selected_operation is invalid")
        if self.next_understanding_question is not None:
            _question(self.next_understanding_question)


@dataclass(frozen=True)
class ClarificationResolutionResult:
    resolution: ClarificationResolution
    proposal_dispositions: Tuple[ProposalDisposition, ...]
    application: Optional[UnderstandingProposalApplication]

    def __post_init__(self) -> None:
        if not isinstance(self.resolution, ClarificationResolution):
            raise TypeError("resolution is invalid")
        if not isinstance(self.proposal_dispositions, tuple) or not all(
            isinstance(item, ProposalDisposition)
            for item in self.proposal_dispositions
        ):
            raise TypeError("proposal_dispositions contains invalid items")
        if self.application is not None and not isinstance(
            self.application,
            UnderstandingProposalApplication,
        ):
            raise TypeError("application is invalid")
        selected = self.resolution.resolution_type is (
            ClarificationResolutionType.SELECT_PROPOSAL
        )
        if selected != (self.application is not None):
            raise ValueError(
                "Only SELECT_PROPOSAL can contain a proposal application"
            )


class GuardianClarificationResolutionService:
    """Resolves explicit clarification input without interpreting language."""

    def __init__(
        self,
        proposals: Optional[GuardianUnderstandingProposalService] = None,
    ) -> None:
        self.proposals = proposals or GuardianUnderstandingProposalService()

    def resolve(
        self,
        existing: UnderstandingState,
        proposal_set: UnderstandingProposalSet,
        request: ClarificationResolutionRequest,
    ) -> ClarificationResolutionResult:
        if not isinstance(existing, UnderstandingState):
            raise TypeError("existing must be an UnderstandingState")
        if not isinstance(proposal_set, UnderstandingProposalSet):
            raise TypeError("proposal_set is invalid")
        if not isinstance(request, ClarificationResolutionRequest):
            raise TypeError("request is invalid")
        if proposal_set.understanding_question is None:
            raise ValueError("Proposal set has no understanding question")
        if proposal_set.understanding_question_id != request.question_id:
            raise ValueError("Question does not belong to proposal set")

        proposals_by_id = {
            proposal.proposal_id: proposal
            for proposal in proposal_set.proposals
        }
        unknown = tuple(
            proposal_id
            for proposal_id in request.affected_proposal_ids
            if proposal_id not in proposals_by_id
        )
        if unknown:
            raise ValueError("Proposal does not belong to proposal set")
        if (
            request.resolution_type
            is ClarificationResolutionType.CLOSE_WITHOUT_CHANGE
            and set(request.affected_proposal_ids) != set(proposals_by_id)
        ):
            raise ValueError(
                "CLOSE_WITHOUT_CHANGE must close the complete proposal set"
            )

        selected = (
            proposals_by_id[request.selected_proposal_id]
            if request.selected_proposal_id is not None
            else None
        )
        resolution = ClarificationResolution(
            resolution_id=_resolution_id(proposal_set, request),
            proposal_statement_id=proposal_set.statement_id,
            original_user_statement=proposal_set.user_statement,
            question_id=request.question_id,
            understanding_question=proposal_set.understanding_question,
            answer_statement_id=request.answer_statement_id,
            answer_text=request.answer_text,
            affected_proposal_ids=request.affected_proposal_ids,
            resolution_type=request.resolution_type,
            source_reference=request.source_reference,
            rationale=request.rationale,
            selected_proposal_id=request.selected_proposal_id,
            selected_operation=(selected.operation if selected else None),
            next_understanding_question=request.next_understanding_question,
        )
        application = None
        if selected is not None:
            application = self.proposals.apply(
                existing,
                proposal_set,
                UnderstandingProposalSelection(selected.proposal_id),
            )
        return ClarificationResolutionResult(
            resolution=resolution,
            proposal_dispositions=_dispositions(proposal_set, request),
            application=application,
        )


def _dispositions(
    proposal_set: UnderstandingProposalSet,
    request: ClarificationResolutionRequest,
) -> Tuple[ProposalDisposition, ...]:
    affected = set(request.affected_proposal_ids)
    result = []
    for proposal in proposal_set.proposals:
        disposition = ProposalDispositionType.OPEN
        if proposal.proposal_id in affected:
            if request.resolution_type is ClarificationResolutionType.SELECT_PROPOSAL:
                disposition = ProposalDispositionType.SELECTED
            elif request.resolution_type is ClarificationResolutionType.REJECT_PROPOSALS:
                disposition = ProposalDispositionType.REJECTED
            elif request.resolution_type is ClarificationResolutionType.CLOSE_WITHOUT_CHANGE:
                disposition = ProposalDispositionType.CLOSED_WITHOUT_CHANGE
        result.append(ProposalDisposition(proposal.proposal_id, disposition))
    return tuple(result)


def _resolution_id(
    proposal_set: UnderstandingProposalSet,
    request: ClarificationResolutionRequest,
) -> str:
    payload = json.dumps(
        {
            "proposal_statement_id": proposal_set.statement_id,
            "original_user_statement": proposal_set.user_statement,
            "question_id": request.question_id,
            "understanding_question": proposal_set.understanding_question,
            "answer_statement_id": request.answer_statement_id,
            "answer_text": request.answer_text,
            "affected_proposal_ids": request.affected_proposal_ids,
            "resolution_type": request.resolution_type.value,
            "source_reference": request.source_reference,
            "rationale": request.rationale,
            "selected_proposal_id": request.selected_proposal_id,
            "next_understanding_question": request.next_understanding_question,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "clarification-resolution-{}".format(digest[:16])


def _proposal_ids(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("affected_proposal_ids must be a non-empty tuple")
    if len(set(value)) != len(value):
        raise ValueError("affected_proposal_ids must be unique")
    for proposal_id in value:
        _identifier(
            proposal_id,
            "affected proposal ID",
            "understanding-proposal",
        )


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
    _text(value, "understanding question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one understanding question is required")
