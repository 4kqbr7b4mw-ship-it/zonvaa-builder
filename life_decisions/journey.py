from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.clarification import (
    ClarificationResolution,
    ClarificationResolutionType,
)
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
    GuardianLifeDecisionConversationService,
    MissingInformation,
    OrganizationalPreparationStep,
    PowerOfAttorneyConversationInput,
    PowerOfAttorneyConversationPreparation,
    ProfessionalReviewNeed,
    RelevantPersonRole,
    RepresentationAreaReference,
    UserStatementReference,
)
from life_decisions.conversation_turn import (
    GuardianPowerOfAttorneyConversationService,
    PowerOfAttorneyConversationTurn,
    PowerOfAttorneyConversationTurnInput,
    PowerOfAttorneyUnderstandingQuestion,
    understanding_state_content_hash,
)
from life_decisions.models import DocumentReference


class PowerOfAttorneyJourneyType(str, Enum):
    POWER_OF_ATTORNEY_PREPARATION = "POWER_OF_ATTORNEY_PREPARATION"


class PowerOfAttorneyJourneyStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    WAITING_FOR_EXTERNAL_RESOLUTION = "WAITING_FOR_EXTERNAL_RESOLUTION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    BLOCKED_MISSING_CONTROLLED_QUESTION = "BLOCKED_MISSING_CONTROLLED_QUESTION"
    BLOCKED_INCONSISTENT_ARTIFACTS = "BLOCKED_INCONSISTENT_ARTIFACTS"
    CONVERSATION_PREPARATION_READY = "CONVERSATION_PREPARATION_READY"
    PROFESSIONAL_REVIEW_PREPARATION_READY = (
        "PROFESSIONAL_REVIEW_PREPARATION_READY"
    )


class PowerOfAttorneyJourneyAction(str, Enum):
    OBTAIN_USER_ANSWER = "OBTAIN_USER_ANSWER"
    OBTAIN_EXTERNAL_RESOLUTION = "OBTAIN_EXTERNAL_RESOLUTION"
    REVIEW_UNRESOLVED_QUESTION = "REVIEW_UNRESOLVED_QUESTION"
    PROVIDE_CONTROLLED_QUESTION = "PROVIDE_CONTROLLED_QUESTION"
    CORRECT_INCONSISTENT_ARTIFACTS = "CORRECT_INCONSISTENT_ARTIFACTS"
    PREPARE_PROFESSIONAL_REVIEW = "PREPARE_PROFESSIONAL_REVIEW"
    USE_PREPARATION_PACKAGE = "USE_PREPARATION_PACKAGE"


class PowerOfAttorneyGapType(str, Enum):
    AUTHORIZED_PERSON = "AUTHORIZED_PERSON"
    REPRESENTATION_AREAS = "REPRESENTATION_AREAS"
    EXISTING_DOCUMENTS = "EXISTING_DOCUMENTS"
    REPRESENTATION_MODE = "REPRESENTATION_MODE"
    SUBSTITUTE_PERSON = "SUBSTITUTE_PERSON"
    STORAGE_AND_ACCESS = "STORAGE_AND_ACCESS"
    REVOCATION = "REVOCATION"
    PROFESSIONAL_CONSULTATION = "PROFESSIONAL_CONSULTATION"
    MEDICAL_CLARIFICATION = "MEDICAL_CLARIFICATION"


@dataclass(frozen=True)
class PowerOfAttorneyGapBinding:
    missing_information_id: str
    gap_type: PowerOfAttorneyGapType

    def __post_init__(self) -> None:
        _identifier(
            self.missing_information_id,
            "missing_information_id",
            "missing-information",
        )
        _enum(self.gap_type, PowerOfAttorneyGapType, "gap_type")


@dataclass(frozen=True)
class ControlledPowerOfAttorneyQuestion:
    question_id: str
    gap_type: PowerOfAttorneyGapType
    text: str
    required_source_kind: str

    def __post_init__(self) -> None:
        _identifier(self.question_id, "question_id", "understanding-question")
        _enum(self.gap_type, PowerOfAttorneyGapType, "gap_type")
        _question(self.text)
        _text(self.required_source_kind, "required_source_kind")


class PowerOfAttorneyQuestionCatalog:
    """Static questions for explicitly typed, already supported gaps."""

    def __init__(
        self,
        questions: Optional[Tuple[ControlledPowerOfAttorneyQuestion, ...]] = None,
    ) -> None:
        self.questions = questions if questions is not None else _default_questions()
        _items(self.questions, ControlledPowerOfAttorneyQuestion, "questions")
        by_id = {}
        by_gap = {}
        for question in self.questions:
            if question.question_id in by_id and by_id[question.question_id] != question:
                raise ValueError("Duplicate question ID has different content")
            if question.gap_type in by_gap:
                raise ValueError("Each gap type must have exactly one question")
            by_id[question.question_id] = question
            by_gap[question.gap_type] = question
        self._by_gap = by_gap

    def for_gap(
        self,
        gap: MissingInformation,
        binding: PowerOfAttorneyGapBinding,
    ) -> Optional[PowerOfAttorneyUnderstandingQuestion]:
        if gap.information_id != binding.missing_information_id:
            raise ValueError("Gap binding does not reference missing information")
        definition = self._by_gap.get(binding.gap_type)
        if definition is None:
            return None
        return PowerOfAttorneyUnderstandingQuestion(
            definition.question_id,
            gap.information_id,
            definition.text,
            (gap.source_reference,),
        )


@dataclass(frozen=True)
class PowerOfAttorneyExternalClarification:
    source_turn_id: str
    answer_statement: UserStatementReference
    resolution: ClarificationResolution
    revision: Optional[UnderstandingRevision] = None
    revision_reference: Optional[str] = None
    resulting_understanding_state_id: Optional[str] = None
    resulting_understanding_state_hash: Optional[str] = None

    def __post_init__(self) -> None:
        _identifier(self.source_turn_id, "source_turn_id", "poa-turn")
        if not isinstance(self.answer_statement, UserStatementReference):
            raise TypeError("answer_statement is invalid")
        if not isinstance(self.resolution, ClarificationResolution):
            raise TypeError("resolution is invalid")
        selected = self.resolution.resolution_type is (
            ClarificationResolutionType.SELECT_PROPOSAL
        )
        revision_values = (
            self.revision,
            self.revision_reference,
            self.resulting_understanding_state_id,
            self.resulting_understanding_state_hash,
        )
        if selected and not all(item is not None for item in revision_values):
            raise ValueError("Selected proposal requires a complete revision lineage")
        if not selected and any(item is not None for item in revision_values):
            raise ValueError("Only selected proposals can contain a revision lineage")
        if self.revision is not None and not isinstance(
            self.revision, UnderstandingRevision
        ):
            raise TypeError("revision is invalid")
        if self.revision_reference is not None:
            _text(self.revision_reference, "revision_reference")
        if self.resulting_understanding_state_id is not None:
            _identifier(
                self.resulting_understanding_state_id,
                "resulting_understanding_state_id",
                "understanding-state",
            )
        if self.resulting_understanding_state_hash is not None:
            _sha256(self.resulting_understanding_state_hash, "resulting state hash")


@dataclass(frozen=True)
class PowerOfAttorneyJourneyInput:
    understanding_state_id: str
    understanding_state_hash: str
    understanding_state: UnderstandingState
    conversation_input: PowerOfAttorneyConversationInput
    gap_bindings: Tuple[PowerOfAttorneyGapBinding, ...]
    previous_turns: Tuple[PowerOfAttorneyConversationTurn, ...] = ()
    clarifications: Tuple[PowerOfAttorneyExternalClarification, ...] = ()
    create_professional_review_preparation: bool = False

    def __post_init__(self) -> None:
        _identifier(
            self.understanding_state_id,
            "understanding_state_id",
            "understanding-state",
        )
        _sha256(self.understanding_state_hash, "understanding_state_hash")
        if not isinstance(self.understanding_state, UnderstandingState):
            raise TypeError("understanding_state is invalid")
        if not isinstance(self.conversation_input, PowerOfAttorneyConversationInput):
            raise TypeError("conversation_input is invalid")
        _items(self.gap_bindings, PowerOfAttorneyGapBinding, "gap_bindings")
        _items(self.previous_turns, PowerOfAttorneyConversationTurn, "previous_turns")
        _items(
            self.clarifications,
            PowerOfAttorneyExternalClarification,
            "clarifications",
        )
        if not isinstance(self.create_professional_review_preparation, bool):
            raise TypeError("create_professional_review_preparation must be bool")


@dataclass(frozen=True)
class PowerOfAttorneyProfessionalReviewPreparation:
    preparation_id: str
    journey_id: str
    understanding_state_id: str
    source_statements: Tuple[UserStatementReference, ...]
    clarification_resolutions: Tuple[ClarificationResolution, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    people: Tuple[RelevantPersonRole, ...]
    representation_areas: Tuple[RepresentationAreaReference, ...]
    document_references: Tuple[DocumentReference, ...]
    unknowns: Tuple[Unknown, ...]
    unanswered_essential_gaps: Tuple[str, ...]
    deferred_points: Tuple[str, ...]
    closed_without_change_points: Tuple[str, ...]
    missing_controlled_questions: Tuple[str, ...]
    hypotheses: Tuple[Hypothesis, ...]
    contradictions: Tuple[Contradiction, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    professional_boundaries: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.preparation_id, "preparation_id", "poa-review-preparation")
        _identifier(self.journey_id, "journey_id", "poa-journey")
        _identifier(
            self.understanding_state_id,
            "understanding_state_id",
            "understanding-state",
        )
        _items(self.source_statements, UserStatementReference, "source_statements")
        _items(
            self.clarification_resolutions,
            ClarificationResolution,
            "clarification_resolutions",
        )
        _items(self.facts, Fact, "facts")
        _items(self.goals, Goal, "goals")
        _items(self.people, RelevantPersonRole, "people")
        _items(
            self.representation_areas,
            RepresentationAreaReference,
            "representation_areas",
        )
        _items(self.document_references, DocumentReference, "document_references")
        _items(self.unknowns, Unknown, "unknowns")
        _text_items(self.unanswered_essential_gaps, "unanswered_essential_gaps")
        _text_items(self.deferred_points, "deferred_points")
        _text_items(self.closed_without_change_points, "closed points")
        _text_items(self.missing_controlled_questions, "missing questions")
        _items(self.hypotheses, Hypothesis, "hypotheses")
        _items(self.contradictions, Contradiction, "contradictions")
        _items(
            self.organizational_steps,
            OrganizationalPreparationStep,
            "organizational_steps",
        )
        _items(
            self.professional_reviews,
            ProfessionalReviewNeed,
            "professional_reviews",
        )
        _non_empty_text_items(self.professional_boundaries, "boundaries")


@dataclass(frozen=True)
class PowerOfAttorneyJourney:
    journey_id: str
    journey_type: PowerOfAttorneyJourneyType
    understanding_state: UnderstandingState
    understanding_state_id: str
    understanding_state_hash: str
    preparation: Optional[PowerOfAttorneyConversationPreparation]
    turns: Tuple[PowerOfAttorneyConversationTurn, ...]
    referenced_user_statements: Tuple[UserStatementReference, ...]
    clarifications: Tuple[PowerOfAttorneyExternalClarification, ...]
    status: PowerOfAttorneyJourneyStatus
    current_open_gap_id: Optional[str]
    current_question: Optional[PowerOfAttorneyUnderstandingQuestion]
    relevant_previous_turn_id: Optional[str]
    facts: Tuple[Fact, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    goals: Tuple[Goal, ...]
    people: Tuple[RelevantPersonRole, ...]
    representation_areas: Tuple[RepresentationAreaReference, ...]
    document_references: Tuple[DocumentReference, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    open_points: Tuple[str, ...]
    deferred_points: Tuple[str, ...]
    closed_without_change_points: Tuple[str, ...]
    next_action: PowerOfAttorneyJourneyAction
    professional_boundaries: Tuple[str, ...]
    warnings: Tuple[str, ...]
    blockers: Tuple[str, ...]
    review_preparation: Optional[PowerOfAttorneyProfessionalReviewPreparation]

    def __post_init__(self) -> None:
        _identifier(self.journey_id, "journey_id", "poa-journey")
        _enum(self.journey_type, PowerOfAttorneyJourneyType, "journey_type")
        if not isinstance(self.understanding_state, UnderstandingState):
            raise TypeError("understanding_state is invalid")
        _identifier(
            self.understanding_state_id,
            "understanding_state_id",
            "understanding-state",
        )
        _sha256(self.understanding_state_hash, "understanding_state_hash")
        if self.preparation is not None and not isinstance(
            self.preparation, PowerOfAttorneyConversationPreparation
        ):
            raise TypeError("preparation is invalid")
        _items(self.turns, PowerOfAttorneyConversationTurn, "turns")
        _items(
            self.referenced_user_statements,
            UserStatementReference,
            "referenced_user_statements",
        )
        _items(
            self.clarifications,
            PowerOfAttorneyExternalClarification,
            "clarifications",
        )
        _enum(self.status, PowerOfAttorneyJourneyStatus, "status")
        _optional_identifier(
            self.current_open_gap_id,
            "current_open_gap_id",
            "missing-information",
        )
        if self.current_question is not None and not isinstance(
            self.current_question, PowerOfAttorneyUnderstandingQuestion
        ):
            raise TypeError("current_question is invalid")
        _optional_identifier(
            self.relevant_previous_turn_id,
            "relevant_previous_turn_id",
            "poa-turn",
        )
        _items(self.facts, Fact, "facts")
        _items(self.hypotheses, Hypothesis, "hypotheses")
        _items(self.unknowns, Unknown, "unknowns")
        _items(self.contradictions, Contradiction, "contradictions")
        _items(self.goals, Goal, "goals")
        _items(self.people, RelevantPersonRole, "people")
        _items(
            self.representation_areas,
            RepresentationAreaReference,
            "representation_areas",
        )
        _items(self.document_references, DocumentReference, "document_references")
        _items(
            self.organizational_steps,
            OrganizationalPreparationStep,
            "organizational_steps",
        )
        _items(
            self.professional_reviews,
            ProfessionalReviewNeed,
            "professional_reviews",
        )
        for values, name in (
            (self.open_points, "open_points"),
            (self.deferred_points, "deferred_points"),
            (self.closed_without_change_points, "closed points"),
            (self.professional_boundaries, "boundaries"),
            (self.warnings, "warnings"),
            (self.blockers, "blockers"),
        ):
            _text_items(values, name)
        _enum(self.next_action, PowerOfAttorneyJourneyAction, "next_action")
        if self.review_preparation is not None and not isinstance(
            self.review_preparation,
            PowerOfAttorneyProfessionalReviewPreparation,
        ):
            raise TypeError("review_preparation is invalid")


class GuardianPowerOfAttorneyJourneyService:
    """Connects explicit artifacts without interpreting or persisting them."""

    def __init__(
        self,
        catalog: Optional[PowerOfAttorneyQuestionCatalog] = None,
        preparation_service: Optional[GuardianLifeDecisionConversationService] = None,
        turn_service: Optional[GuardianPowerOfAttorneyConversationService] = None,
    ) -> None:
        self.catalog = catalog or PowerOfAttorneyQuestionCatalog()
        self.preparation_service = (
            preparation_service or GuardianLifeDecisionConversationService()
        )
        self.turn_service = turn_service or GuardianPowerOfAttorneyConversationService()

    def build(self, journey_input: PowerOfAttorneyJourneyInput) -> PowerOfAttorneyJourney:
        if not isinstance(journey_input, PowerOfAttorneyJourneyInput):
            raise TypeError("journey_input is invalid")
        journey_id = _journey_id(journey_input.conversation_input)
        try:
            preparation = self._validate_and_prepare(journey_input)
            resolutions = self._validate_clarifications(journey_input)
        except (TypeError, ValueError) as error:
            return self._result(
                journey_input,
                journey_id,
                None,
                PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS,
                PowerOfAttorneyJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS,
                blockers=("{}: {}".format(type(error).__name__, error),),
            )

        closed = tuple(
            item.resolution.question_id
            for item in resolutions
            if item.resolution.resolution_type
            is ClarificationResolutionType.CLOSE_WITHOUT_CHANGE
        )
        closed_gap_ids = tuple(
            turn.missing_information_id
            for turn in journey_input.previous_turns
            if turn.question_id in closed and turn.missing_information_id is not None
        )
        deferred_gap_ids = tuple(
            turn.missing_information_id
            for turn in journey_input.previous_turns
            if turn.missing_information_id is not None
            and any(
                clarification.source_turn_id == turn.turn_id
                and clarification.resolution.resolution_type
                in (
                    ClarificationResolutionType.KEEP_OPEN,
                    ClarificationResolutionType.REJECT_PROPOSALS,
                )
                for clarification in resolutions
            )
        )
        active_gaps = tuple(
            item
            for item in preparation.missing_information
            if item.essential and item.information_id not in closed_gap_ids
        )
        if not active_gaps:
            status = PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
            action = PowerOfAttorneyJourneyAction.PREPARE_PROFESSIONAL_REVIEW
            package = None
            if journey_input.create_professional_review_preparation:
                status = (
                    PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
                )
                action = PowerOfAttorneyJourneyAction.USE_PREPARATION_PACKAGE
                package = self._review_package(
                    journey_id,
                    preparation,
                    resolutions,
                    deferred_gap_ids,
                    closed_gap_ids,
                )
            return self._result(
                journey_input,
                journey_id,
                preparation,
                status,
                action,
                deferred=deferred_gap_ids,
                closed=closed_gap_ids,
                review_preparation=package,
            )

        gap = active_gaps[0]
        binding = next(
            (
                item
                for item in journey_input.gap_bindings
                if item.missing_information_id == gap.information_id
            ),
            None,
        )
        if binding is None:
            return self._result(
                journey_input,
                journey_id,
                preparation,
                PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION,
                PowerOfAttorneyJourneyAction.PROVIDE_CONTROLLED_QUESTION,
                current_gap=gap.information_id,
                blockers=("MISSING_GAP_BINDING",),
                deferred=deferred_gap_ids,
                closed=closed_gap_ids,
            )
        question = self.catalog.for_gap(gap, binding)
        if question is None:
            return self._result(
                journey_input,
                journey_id,
                preparation,
                PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION,
                PowerOfAttorneyJourneyAction.PROVIDE_CONTROLLED_QUESTION,
                current_gap=gap.information_id,
                blockers=("CONTROLLED_QUESTION_NOT_FOUND",),
                deferred=deferred_gap_ids,
                closed=closed_gap_ids,
            )
        if preparation.next_understanding_question != question.text:
            return self._result(
                journey_input,
                journey_id,
                preparation,
                PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS,
                PowerOfAttorneyJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS,
                current_gap=gap.information_id,
                blockers=("PREPARATION_QUESTION_NOT_CONTROLLED",),
                deferred=deferred_gap_ids,
                closed=closed_gap_ids,
            )

        matching = next(
            (
                turn
                for turn in journey_input.previous_turns
                if turn.missing_information_id == gap.information_id
                and turn.question_id == question.question_id
                and turn.understanding_question == question.text
            ),
            None,
        )
        if matching is not None:
            resolution = next(
                (
                    item
                    for item in resolutions
                    if item.source_turn_id == matching.turn_id
                ),
                None,
            )
            if resolution is not None:
                return self._result(
                    journey_input,
                    journey_id,
                    preparation,
                    PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION,
                    PowerOfAttorneyJourneyAction.OBTAIN_EXTERNAL_RESOLUTION,
                    current_gap=gap.information_id,
                    current_question=question,
                    relevant_turn=matching.turn_id,
                    deferred=deferred_gap_ids,
                    closed=closed_gap_ids,
                )
            return self._result(
                journey_input,
                journey_id,
                preparation,
                PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED,
                PowerOfAttorneyJourneyAction.REVIEW_UNRESOLVED_QUESTION,
                current_gap=gap.information_id,
                current_question=question,
                relevant_turn=matching.turn_id,
                deferred=deferred_gap_ids,
                closed=closed_gap_ids,
            )

        selected_lineage = next(
            (
                item
                for item in reversed(resolutions)
                if item.resolution.resolution_type
                is ClarificationResolutionType.SELECT_PROPOSAL
                and journey_input.previous_turns
                and item.source_turn_id == journey_input.previous_turns[-1].turn_id
            ),
            None,
        )
        turn = self.turn_service.next_turn(
            PowerOfAttorneyConversationTurnInput(
                source_understanding_state_id=journey_input.understanding_state_id,
                source_understanding_state_hash=journey_input.understanding_state_hash,
                understanding_state=journey_input.understanding_state,
                preparation=preparation,
                question=question,
                previous_turns=journey_input.previous_turns,
                answer_statement=(
                    selected_lineage.answer_statement
                    if selected_lineage is not None
                    else None
                ),
                resolution=(
                    selected_lineage.resolution
                    if selected_lineage is not None
                    else None
                ),
                revision=(
                    selected_lineage.revision
                    if selected_lineage is not None
                    else None
                ),
                revision_reference=(
                    selected_lineage.revision_reference
                    if selected_lineage is not None
                    else None
                ),
                resulting_understanding_state_id=(
                    selected_lineage.resulting_understanding_state_id
                    if selected_lineage is not None
                    else None
                ),
                resulting_understanding_state_hash=(
                    selected_lineage.resulting_understanding_state_hash
                    if selected_lineage is not None
                    else None
                ),
            )
        )
        return self._result(
            journey_input,
            journey_id,
            preparation,
            PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION,
            PowerOfAttorneyJourneyAction.OBTAIN_USER_ANSWER,
            current_gap=gap.information_id,
            current_question=question,
            turns=journey_input.previous_turns + (turn,),
            deferred=deferred_gap_ids,
            closed=closed_gap_ids,
        )

    def _validate_and_prepare(
        self, journey_input: PowerOfAttorneyJourneyInput
    ) -> PowerOfAttorneyConversationPreparation:
        if journey_input.understanding_state_hash != understanding_state_content_hash(
            journey_input.understanding_state
        ):
            raise ValueError("State hash does not match UnderstandingState")
        conversation_input = journey_input.conversation_input
        if conversation_input.understanding_state_id != journey_input.understanding_state_id:
            raise ValueError("Conversation input belongs to another state")
        if conversation_input.understanding_state != journey_input.understanding_state:
            raise ValueError("Conversation input state does not match journey state")
        identifiers = tuple(item.missing_information_id for item in journey_input.gap_bindings)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Gap bindings must be unique")
        valid_gaps = {item.information_id for item in conversation_input.missing_information}
        if any(identifier not in valid_gaps for identifier in identifiers):
            raise ValueError("Gap binding references foreign missing information")
        if len({turn.turn_id for turn in journey_input.previous_turns}) != len(
            journey_input.previous_turns
        ):
            raise ValueError("Turn history must be unique")
        for turn in journey_input.previous_turns:
            if turn.triggering_statement_id != conversation_input.triggering_statement_id:
                raise ValueError("Turn history belongs to another journey")
            if (
                turn.source_understanding_state_id
                != journey_input.understanding_state_id
                and not any(
                    item.source_turn_id == turn.turn_id
                    for item in journey_input.clarifications
                )
            ):
                raise ValueError("Turn history contains an unlinked foreign state")
        return self.preparation_service.prepare(conversation_input)

    def _validate_clarifications(
        self, journey_input: PowerOfAttorneyJourneyInput
    ) -> Tuple[PowerOfAttorneyExternalClarification, ...]:
        turns = {turn.turn_id: turn for turn in journey_input.previous_turns}
        if len({item.source_turn_id for item in journey_input.clarifications}) != len(
            journey_input.clarifications
        ):
            raise ValueError("Each turn can have only one clarification")
        for item in journey_input.clarifications:
            turn = turns.get(item.source_turn_id)
            if turn is None:
                raise ValueError("Clarification references a foreign turn")
            if item.resolution.question_id != turn.question_id:
                raise ValueError("Resolution answers another turn")
            if item.resolution.understanding_question != turn.understanding_question:
                raise ValueError("Resolution question text does not match turn")
            if (
                item.answer_statement.statement_id
                != item.resolution.answer_statement_id
                or item.answer_statement.text != item.resolution.answer_text
                or item.answer_statement.source_reference
                != item.resolution.source_reference
            ):
                raise ValueError("User answer does not match resolution")
            if item.revision is not None:
                assert item.resulting_understanding_state_hash is not None
                assert item.resulting_understanding_state_id is not None
                if item.resulting_understanding_state_hash != (
                    understanding_state_content_hash(item.revision.state)
                ):
                    raise ValueError("Result state hash does not match revision")
                if item.resolution.selected_operation is None:
                    raise ValueError("Selected resolution lacks operation")
                selected = item.resolution.selected_operation
                if not any(
                    change.operation is selected.operation
                    and change.source_statement == item.answer_statement.text
                    and change.target_text == selected.target_text
                    for change in item.revision.changes
                ):
                    raise ValueError("Revision does not match selected operation")
        selected = tuple(
            item
            for item in journey_input.clarifications
            if item.resolution.resolution_type
            is ClarificationResolutionType.SELECT_PROPOSAL
        )
        if selected:
            turn_order = {
                turn.turn_id: index
                for index, turn in enumerate(journey_input.previous_turns)
            }
            latest = max(selected, key=lambda item: turn_order[item.source_turn_id])
            assert latest.revision is not None
            if latest.revision.state != journey_input.understanding_state:
                raise ValueError("Latest revision does not produce current state")
            if (
                latest.resulting_understanding_state_id
                != journey_input.understanding_state_id
            ):
                raise ValueError("Latest result state ID does not match journey state")
        return journey_input.clarifications

    def _review_package(
        self,
        journey_id: str,
        preparation: PowerOfAttorneyConversationPreparation,
        clarifications: Tuple[PowerOfAttorneyExternalClarification, ...],
        deferred: Tuple[str, ...],
        closed: Tuple[str, ...],
    ) -> PowerOfAttorneyProfessionalReviewPreparation:
        value = PowerOfAttorneyProfessionalReviewPreparation(
            preparation_id="poa-review-preparation-pending",
            journey_id=journey_id,
            understanding_state_id=preparation.understanding_state_id,
            source_statements=preparation.referenced_user_statements,
            clarification_resolutions=tuple(
                item.resolution for item in clarifications
            ),
            facts=preparation.known_situation,
            goals=preparation.goals,
            people=preparation.relevant_people,
            representation_areas=preparation.representation_areas,
            document_references=preparation.existing_documents,
            unknowns=preparation.open_points,
            unanswered_essential_gaps=tuple(
                item.information_id
                for item in preparation.missing_information
                if item.essential and item.information_id not in closed
            ),
            deferred_points=deferred,
            closed_without_change_points=closed,
            missing_controlled_questions=(),
            hypotheses=preparation.hypotheses,
            contradictions=preparation.contradictions,
            organizational_steps=preparation.organizational_steps,
            professional_reviews=preparation.professional_reviews,
            professional_boundaries=preparation.professional_boundaries,
        )
        return PowerOfAttorneyProfessionalReviewPreparation(
            **{
                field.name: (
                    _semantic_id("poa-review-preparation", value)
                    if field.name == "preparation_id"
                    else getattr(value, field.name)
                )
                for field in fields(value)
            }
        )

    def _result(
        self,
        source: PowerOfAttorneyJourneyInput,
        journey_id: str,
        preparation: Optional[PowerOfAttorneyConversationPreparation],
        status: PowerOfAttorneyJourneyStatus,
        action: PowerOfAttorneyJourneyAction,
        current_gap: Optional[str] = None,
        current_question: Optional[PowerOfAttorneyUnderstandingQuestion] = None,
        relevant_turn: Optional[str] = None,
        blockers: Tuple[str, ...] = (),
        turns: Optional[Tuple[PowerOfAttorneyConversationTurn, ...]] = None,
        deferred: Tuple[str, ...] = (),
        closed: Tuple[str, ...] = (),
        review_preparation: Optional[PowerOfAttorneyProfessionalReviewPreparation] = None,
    ) -> PowerOfAttorneyJourney:
        conversation = source.conversation_input
        return PowerOfAttorneyJourney(
            journey_id=journey_id,
            journey_type=PowerOfAttorneyJourneyType.POWER_OF_ATTORNEY_PREPARATION,
            understanding_state=source.understanding_state,
            understanding_state_id=source.understanding_state_id,
            understanding_state_hash=source.understanding_state_hash,
            preparation=preparation,
            turns=source.previous_turns if turns is None else turns,
            referenced_user_statements=conversation.user_statements,
            clarifications=source.clarifications,
            status=status,
            current_open_gap_id=current_gap,
            current_question=current_question,
            relevant_previous_turn_id=relevant_turn,
            facts=conversation.facts,
            hypotheses=conversation.hypotheses,
            unknowns=conversation.unknowns,
            contradictions=conversation.contradictions,
            goals=conversation.goals,
            people=conversation.relevant_people,
            representation_areas=conversation.representation_areas,
            document_references=conversation.existing_documents,
            organizational_steps=conversation.organizational_steps,
            professional_reviews=conversation.professional_reviews,
            open_points=tuple(
                item.information_id
                for item in conversation.missing_information
                if item.essential and item.information_id not in closed
            ),
            deferred_points=deferred,
            closed_without_change_points=closed,
            next_action=action,
            professional_boundaries=(
                preparation.professional_boundaries
                if preparation
                else GuardianLifeDecisionConversationService.PROFESSIONAL_BOUNDARIES
            ),
            warnings=(
                preparation.warnings
                if preparation
                else GuardianLifeDecisionConversationService.WARNINGS
            ),
            blockers=blockers,
            review_preparation=review_preparation,
        )


def _journey_id(value: PowerOfAttorneyConversationInput) -> str:
    statement = next(
        item
        for item in value.user_statements
        if item.statement_id == value.triggering_statement_id
    )
    return _semantic_id(
        "poa-journey",
        (statement.statement_id, statement.text, statement.source_reference),
    )


def _semantic_id(prefix: str, value: object) -> str:
    payload = json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "{}-{}".format(
        prefix,
        hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
    )


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


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix), value) is None:
        raise ValueError("{} is invalid".format(name))


def _optional_identifier(value: object, name: str, prefix: str) -> None:
    if value is not None:
        _identifier(value, name, prefix)


def _sha256(value: object, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("{} must be a SHA-256 hash".format(name))


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _text_items(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for item in value:
        _text(item, name)
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(name))


def _non_empty_text_items(value: object, name: str) -> None:
    _text_items(value, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))


def _question(value: str) -> None:
    _text(value, "question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one controlled question is required")


def _default_questions() -> Tuple[ControlledPowerOfAttorneyQuestion, ...]:
    source_kind = "missing-information-source"
    return (
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-authorized-person",
            PowerOfAttorneyGapType.AUTHORIZED_PERSON,
            "Welche Person möchten Sie für die mögliche Bevollmächtigung ausdrücklich benennen?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-representation-areas",
            PowerOfAttorneyGapType.REPRESENTATION_AREAS,
            "Welchen ausdrücklich genannten Vertretungsbereich möchten Sie als Nächstes klären?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-existing-documents",
            PowerOfAttorneyGapType.EXISTING_DOCUMENTS,
            "Welche bereits vorhandene Vollmacht oder Verfügung möchten Sie referenzieren?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-representation-mode",
            PowerOfAttorneyGapType.REPRESENTATION_MODE,
            "Welche Form der Vertretung möchten Sie organisatorisch klären?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-substitute-person",
            PowerOfAttorneyGapType.SUBSTITUTE_PERSON,
            "Möchten Sie eine mögliche Ersatzperson ausdrücklich benennen?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-storage-access",
            PowerOfAttorneyGapType.STORAGE_AND_ACCESS,
            "Welchen Aufbewahrungsort oder Zugang möchten Sie ausdrücklich festhalten?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-revocation",
            PowerOfAttorneyGapType.REVOCATION,
            "Welchen offenen Punkt zum Widerruf möchten Sie fachlich klären lassen?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-professional-consultation",
            PowerOfAttorneyGapType.PROFESSIONAL_CONSULTATION,
            "Welchen ausdrücklich genannten fachlichen Prüfbedarf möchten Sie vorbereiten?",
            source_kind,
        ),
        ControlledPowerOfAttorneyQuestion(
            "understanding-question-poa-medical-clarification",
            PowerOfAttorneyGapType.MEDICAL_CLARIFICATION,
            "Welchen ausdrücklich benannten medizinischen Klärungsbedarf möchten Sie vorbereiten?",
            source_kind,
        ),
    )
