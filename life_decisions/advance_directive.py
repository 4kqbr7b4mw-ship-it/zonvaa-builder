from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass, replace
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
    MissingInformation,
    OrganizationalPreparationStep,
    ProfessionalReviewNeed,
    UserStatementReference,
)
from life_decisions.conversation_turn import understanding_state_content_hash
from life_decisions.models import DocumentReference


class AdvanceDirectiveConversationStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    CONVERSATION_PREPARATION_READY = "CONVERSATION_PREPARATION_READY"


class AdvanceDirectiveJourneyStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    WAITING_FOR_EXTERNAL_RESOLUTION = "WAITING_FOR_EXTERNAL_RESOLUTION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    BLOCKED_MISSING_CONTROLLED_QUESTION = "BLOCKED_MISSING_CONTROLLED_QUESTION"
    BLOCKED_INCONSISTENT_ARTIFACTS = "BLOCKED_INCONSISTENT_ARTIFACTS"
    CONVERSATION_PREPARATION_READY = "CONVERSATION_PREPARATION_READY"
    PROFESSIONAL_REVIEW_PREPARATION_READY = "PROFESSIONAL_REVIEW_PREPARATION_READY"


class AdvanceDirectiveJourneyAction(str, Enum):
    OBTAIN_USER_ANSWER = "OBTAIN_USER_ANSWER"
    OBTAIN_EXTERNAL_RESOLUTION = "OBTAIN_EXTERNAL_RESOLUTION"
    REVIEW_UNRESOLVED_QUESTION = "REVIEW_UNRESOLVED_QUESTION"
    PROVIDE_CONTROLLED_QUESTION = "PROVIDE_CONTROLLED_QUESTION"
    CORRECT_INCONSISTENT_ARTIFACTS = "CORRECT_INCONSISTENT_ARTIFACTS"
    PREPARE_PROFESSIONAL_REVIEW = "PREPARE_PROFESSIONAL_REVIEW"
    USE_PREPARATION_PACKAGE = "USE_PREPARATION_PACKAGE"


class AdvanceDirectivePersonRole(str, Enum):
    TRUSTED_PERSON = "TRUSTED_PERSON"
    AUTHORIZED_PERSON = "AUTHORIZED_PERSON"
    TREATING_PHYSICIAN = "TREATING_PHYSICIAN"
    PRIMARY_CARE_PHYSICIAN = "PRIMARY_CARE_PHYSICIAN"
    FAMILY_MEMBER = "FAMILY_MEMBER"
    OTHER_CONTACT = "OTHER_CONTACT"


class MedicalSituationType(str, Enum):
    PERMANENT_LOSS_OF_DECISION_CAPACITY = "PERMANENT_LOSS_OF_DECISION_CAPACITY"
    IRREVERSIBLE_SEVERE_BRAIN_DAMAGE = "IRREVERSIBLE_SEVERE_BRAIN_DAMAGE"
    ADVANCED_INCURABLE_ILLNESS = "ADVANCED_INCURABLE_ILLNESS"
    DYING_PHASE = "DYING_PHASE"
    PERMANENT_UNCONSCIOUSNESS_OR_COMA = "PERMANENT_UNCONSCIOUSNESS_OR_COMA"
    SEVERE_DEMENTIA = "SEVERE_DEMENTIA"
    OTHER_EXPLICIT = "OTHER_EXPLICIT"


class MedicalMeasureType(str, Enum):
    RESUSCITATION = "RESUSCITATION"
    ARTIFICIAL_VENTILATION = "ARTIFICIAL_VENTILATION"
    ARTIFICIAL_NUTRITION = "ARTIFICIAL_NUTRITION"
    ARTIFICIAL_HYDRATION = "ARTIFICIAL_HYDRATION"
    DIALYSIS = "DIALYSIS"
    ANTIBIOTICS = "ANTIBIOTICS"
    SURGERY = "SURGERY"
    BLOOD_TRANSFUSION = "BLOOD_TRANSFUSION"
    PAIN_AND_SYMPTOM_RELIEF = "PAIN_AND_SYMPTOM_RELIEF"
    SEDATION = "SEDATION"
    INTENSIVE_CARE = "INTENSIVE_CARE"
    ORGAN_DONATION_CONTEXT = "ORGAN_DONATION_CONTEXT"
    OTHER_EXPLICIT = "OTHER_EXPLICIT"


class MedicalMeasurePosition(str, Enum):
    UNSPECIFIED = "UNSPECIFIED"
    WANTS_DISCUSSION = "WANTS_DISCUSSION"
    ACCEPTS = "ACCEPTS"
    REFUSES = "REFUSES"
    ACCEPTS_WITH_CONDITIONS = "ACCEPTS_WITH_CONDITIONS"
    REFUSES_WITH_CONDITIONS = "REFUSES_WITH_CONDITIONS"
    UNCERTAIN = "UNCERTAIN"


class AdvanceDirectiveGapType(str, Enum):
    PREPARATION_GOAL = "PREPARATION_GOAL"
    MEDICAL_SITUATION = "MEDICAL_SITUATION"
    MEASURE_POSITION = "MEASURE_POSITION"
    POSITION_CONDITION = "POSITION_CONDITION"
    PAIN_AND_SYMPTOM_RELIEF = "PAIN_AND_SYMPTOM_RELIEF"
    TRUSTED_PERSON = "TRUSTED_PERSON"
    EXISTING_ADVANCE_DIRECTIVE = "EXISTING_ADVANCE_DIRECTIVE"
    EXISTING_POWER_OF_ATTORNEY = "EXISTING_POWER_OF_ATTORNEY"
    STORAGE_AND_ACCESS = "STORAGE_AND_ACCESS"
    MEDICAL_CONSULTATION = "MEDICAL_CONSULTATION"
    CONTRADICTION = "CONTRADICTION"
    PERSONAL_VALUE = "PERSONAL_VALUE"


class AdvanceDirectiveExperienceActionType(str, Enum):
    ANSWER_CURRENT_QUESTION = "ANSWER_CURRENT_QUESTION"
    KEEP_POINT_OPEN = "KEEP_POINT_OPEN"
    CLOSE_POINT_WITHOUT_CHANGE = "CLOSE_POINT_WITHOUT_CHANGE"
    REQUEST_CONTROLLED_CLARIFICATION = "REQUEST_CONTROLLED_CLARIFICATION"
    REVIEW_OPEN_POINTS = "REVIEW_OPEN_POINTS"
    REVIEW_CONTRADICTIONS = "REVIEW_CONTRADICTIONS"
    REVIEW_MEDICAL_STATEMENTS = "REVIEW_MEDICAL_STATEMENTS"
    REVIEW_PROFESSIONAL_PREPARATION = "REVIEW_PROFESSIONAL_PREPARATION"
    EXPORT_PROFESSIONAL_PREPARATION = "EXPORT_PROFESSIONAL_PREPARATION"
    NO_ACTION_AVAILABLE = "NO_ACTION_AVAILABLE"


@dataclass(frozen=True)
class AdvanceDirectivePersonReference:
    reference_id: str
    label: str
    role: AdvanceDirectivePersonRole
    source_reference: str

    def __post_init__(self) -> None:
        _id(self.reference_id, "reference_id", "advance-directive-person")
        _text(self.label, "label")
        _enum(self.role, AdvanceDirectivePersonRole, "role")
        _text(self.source_reference, "source_reference")


@dataclass(frozen=True)
class MedicalSituationReference:
    situation_id: str
    situation_type: MedicalSituationType
    description: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.situation_id, "situation_id", "medical-situation")
        _enum(self.situation_type, MedicalSituationType, "situation_type")
        _text(self.description, "description")
        _texts(self.source_references, "source_references", required=True)


@dataclass(frozen=True)
class MedicalMeasureStatement:
    statement_id: str
    measure_type: MedicalMeasureType
    position: MedicalMeasurePosition
    conditions: Tuple[str, ...]
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.statement_id, "statement_id", "medical-measure-statement")
        _enum(self.measure_type, MedicalMeasureType, "measure_type")
        _enum(self.position, MedicalMeasurePosition, "position")
        _texts(self.conditions, "conditions")
        _texts(self.source_references, "source_references", required=True)
        conditional = self.position in (
            MedicalMeasurePosition.ACCEPTS_WITH_CONDITIONS,
            MedicalMeasurePosition.REFUSES_WITH_CONDITIONS,
        )
        if conditional != bool(self.conditions):
            raise ValueError("Conditions require and belong to a conditional position")


@dataclass(frozen=True)
class AdvanceDirectiveTextReference:
    reference_id: str
    text: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.reference_id, "reference_id", "advance-directive-text")
        _text(self.text, "text")
        _texts(self.source_references, "source_references", required=True)


@dataclass(frozen=True)
class AdvanceDirectivePreparationInput:
    understanding_state_id: str
    understanding_state: UnderstandingState
    triggering_statement_id: str
    user_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...] = ()
    goals: Tuple[Goal, ...] = ()
    hypotheses: Tuple[Hypothesis, ...] = ()
    unknowns: Tuple[Unknown, ...] = ()
    contradictions: Tuple[Contradiction, ...] = ()
    clarification_resolutions: Tuple[ClarificationResolution, ...] = ()
    people: Tuple[AdvanceDirectivePersonReference, ...] = ()
    documents: Tuple[DocumentReference, ...] = ()
    personal_wishes: Tuple[AdvanceDirectiveTextReference, ...] = ()
    medical_situations: Tuple[MedicalSituationReference, ...] = ()
    medical_measures: Tuple[MedicalMeasureStatement, ...] = ()
    limits_and_refusals: Tuple[AdvanceDirectiveTextReference, ...] = ()
    personal_values: Tuple[AdvanceDirectiveTextReference, ...] = ()
    missing_information: Tuple[MissingInformation, ...] = ()
    organizational_steps: Tuple[OrganizationalPreparationStep, ...] = ()
    professional_reviews: Tuple[ProfessionalReviewNeed, ...] = ()
    next_understanding_question: Optional[str] = None

    def __post_init__(self) -> None:
        _id(self.understanding_state_id, "understanding_state_id", "understanding-state")
        _type(self.understanding_state, UnderstandingState, "understanding_state")
        _id(self.triggering_statement_id, "triggering_statement_id", "statement")
        _items(self.user_statements, UserStatementReference, "user_statements")
        for values, kind, name in (
            (self.facts, Fact, "facts"), (self.goals, Goal, "goals"),
            (self.hypotheses, Hypothesis, "hypotheses"),
            (self.unknowns, Unknown, "unknowns"),
            (self.contradictions, Contradiction, "contradictions"),
            (self.clarification_resolutions, ClarificationResolution, "clarifications"),
            (self.people, AdvanceDirectivePersonReference, "people"),
            (self.documents, DocumentReference, "documents"),
            (self.personal_wishes, AdvanceDirectiveTextReference, "personal_wishes"),
            (self.medical_situations, MedicalSituationReference, "medical_situations"),
            (self.medical_measures, MedicalMeasureStatement, "medical_measures"),
            (self.limits_and_refusals, AdvanceDirectiveTextReference, "limits"),
            (self.personal_values, AdvanceDirectiveTextReference, "personal_values"),
            (self.missing_information, MissingInformation, "missing_information"),
            (self.organizational_steps, OrganizationalPreparationStep, "steps"),
            (self.professional_reviews, ProfessionalReviewNeed, "reviews"),
        ):
            _items(values, kind, name)
        _unique(self.user_statements, "statement_id", "user statements")
        for values, attr, name in (
            (self.people, "reference_id", "people"),
            (self.documents, "id", "documents"),
            (self.personal_wishes, "reference_id", "wishes"),
            (self.medical_situations, "situation_id", "situations"),
            (self.medical_measures, "statement_id", "measures"),
            (self.limits_and_refusals, "reference_id", "limits"),
            (self.personal_values, "reference_id", "values"),
            (self.missing_information, "information_id", "gaps"),
        ):
            _unique(values, attr, name)
        statements = {item.statement_id: item for item in self.user_statements}
        if self.triggering_statement_id not in statements:
            raise ValueError("triggering statement must be referenced")
        for resolution in self.clarification_resolutions:
            original = statements.get(resolution.proposal_statement_id)
            answer = statements.get(resolution.answer_statement_id)
            if original is None or original.text != resolution.original_user_statement:
                raise ValueError("clarification original statement must be referenced")
            if answer is None or answer.text != resolution.answer_text:
                raise ValueError("clarification answer statement must be referenced")
        for values, state_values, name in (
            (self.facts, self.understanding_state.facts, "fact"),
            (self.goals, self.understanding_state.goals, "goal"),
            (self.hypotheses, self.understanding_state.hypotheses, "hypothesis"),
            (self.unknowns, self.understanding_state.unknowns, "unknown"),
            (self.contradictions, self.understanding_state.contradictions, "contradiction"),
        ):
            if any(item not in state_values for item in values):
                raise ValueError("Referenced {} is outside UnderstandingState".format(name))
        essential = any(item.essential for item in self.missing_information)
        if essential != (self.next_understanding_question is not None):
            raise ValueError("Essential gap and next question must occur together")
        if self.next_understanding_question is not None:
            _question(self.next_understanding_question)


@dataclass(frozen=True)
class AdvanceDirectivePreparation:
    preparation_id: str
    understanding_state_id: str
    understanding_state_hash: str
    triggering_statement: UserStatementReference
    referenced_user_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    people: Tuple[AdvanceDirectivePersonReference, ...]
    documents: Tuple[DocumentReference, ...]
    personal_wishes: Tuple[AdvanceDirectiveTextReference, ...]
    medical_situations: Tuple[MedicalSituationReference, ...]
    medical_measures: Tuple[MedicalMeasureStatement, ...]
    limits_and_refusals: Tuple[AdvanceDirectiveTextReference, ...]
    personal_values: Tuple[AdvanceDirectiveTextReference, ...]
    missing_information: Tuple[MissingInformation, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    clarification_resolution_ids: Tuple[str, ...]
    status: AdvanceDirectiveConversationStatus
    next_understanding_question: Optional[str]
    professional_boundaries: Tuple[str, ...]
    warnings: Tuple[str, ...]


class GuardianAdvanceDirectivePreparationService:
    PROFESSIONAL_BOUNDARIES = (
        "Diese Vorbereitung ist keine medizinische oder rechtliche Beratung.",
        "Sie erzeugt keinen Patientenverfügungstext und trifft keine Behandlungsentscheidung.",
        "Sie prüft weder Einwilligungsfähigkeit noch rechtliche Wirksamkeit.",
        "Sie empfiehlt keine medizinische Maßnahme und bewertet keine Person.",
        "Nutzerantworten und persönliche Werte werden nicht automatisch ausgelegt.",
    )
    WARNINGS = (
        "Situationen, Maßnahmen, Haltungen, Bedingungen und Prüfbedarfe stammen ausschließlich aus ausdrücklich typisierten Eingaben.",
        "UNSPECIFIED ist keine Zustimmung; UNCERTAIN ist keine Ablehnung.",
        "Hypothesen, Unknowns und Widersprüche bleiben getrennt sichtbar.",
    )

    def prepare(self, source: AdvanceDirectivePreparationInput) -> AdvanceDirectivePreparation:
        _type(source, AdvanceDirectivePreparationInput, "source")
        statements = {item.statement_id: item for item in source.user_statements}
        status = (
            AdvanceDirectiveConversationStatus.NEEDS_CLARIFICATION
            if any(item.essential for item in source.missing_information)
            else AdvanceDirectiveConversationStatus.CONVERSATION_PREPARATION_READY
        )
        draft = AdvanceDirectivePreparation(
            "advance-directive-preparation-pending",
            source.understanding_state_id,
            understanding_state_content_hash(source.understanding_state),
            statements[source.triggering_statement_id],
            source.user_statements,
            source.facts, source.goals, source.hypotheses, source.unknowns,
            source.contradictions, source.people, source.documents,
            source.personal_wishes, source.medical_situations,
            source.medical_measures, source.limits_and_refusals,
            source.personal_values, source.missing_information,
            source.organizational_steps, source.professional_reviews,
            tuple(item.resolution_id for item in source.clarification_resolutions),
            status, source.next_understanding_question,
            self.PROFESSIONAL_BOUNDARIES, self.WARNINGS,
        )
        return replace(draft, preparation_id=_semantic_id("advance-directive-preparation", draft))


@dataclass(frozen=True)
class AdvanceDirectiveGapBinding:
    missing_information_id: str
    gap_type: AdvanceDirectiveGapType

    def __post_init__(self) -> None:
        _id(self.missing_information_id, "missing_information_id", "missing-information")
        _enum(self.gap_type, AdvanceDirectiveGapType, "gap_type")


@dataclass(frozen=True)
class ControlledAdvanceDirectiveQuestion:
    question_id: str
    gap_type: AdvanceDirectiveGapType
    text: str

    def __post_init__(self) -> None:
        _id(self.question_id, "question_id", "understanding-question")
        _enum(self.gap_type, AdvanceDirectiveGapType, "gap_type")
        _question(self.text)


@dataclass(frozen=True)
class AdvanceDirectiveQuestion:
    question_id: str
    missing_information_id: str
    text: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.question_id, "question_id", "understanding-question")
        _id(self.missing_information_id, "missing_information_id", "missing-information")
        _question(self.text)
        _texts(self.source_references, "source_references", required=True)


class AdvanceDirectiveQuestionCatalog:
    def __init__(self, questions: Optional[Tuple[ControlledAdvanceDirectiveQuestion, ...]] = None) -> None:
        self.questions = questions if questions is not None else _default_questions()
        _items(self.questions, ControlledAdvanceDirectiveQuestion, "questions")
        if len({item.gap_type for item in self.questions}) != len(self.questions):
            raise ValueError("Each gap type has at most one controlled question")

    def for_gap(self, gap: MissingInformation, binding: AdvanceDirectiveGapBinding) -> Optional[AdvanceDirectiveQuestion]:
        if gap.information_id != binding.missing_information_id:
            raise ValueError("Gap binding mismatch")
        definition = next((item for item in self.questions if item.gap_type is binding.gap_type), None)
        if definition is None:
            return None
        return AdvanceDirectiveQuestion(definition.question_id, gap.information_id, definition.text, (gap.source_reference,))


@dataclass(frozen=True)
class AdvanceDirectiveConversationTurn:
    turn_id: str
    status: AdvanceDirectiveConversationStatus
    preparation_id: str
    source_understanding_state_id: str
    source_understanding_state_hash: str
    missing_information_id: Optional[str]
    question_id: Optional[str]
    question: Optional[str]
    question_source_references: Tuple[str, ...]
    previous_turn_id: Optional[str]
    answer_statement_id: Optional[str] = None
    resolution_id: Optional[str] = None
    revision_reference: Optional[str] = None
    resulting_understanding_state_id: Optional[str] = None
    resulting_understanding_state_hash: Optional[str] = None
    state_changed_by_turn: bool = False

    def __post_init__(self) -> None:
        if self.state_changed_by_turn:
            raise ValueError("Conversation turn cannot change state")


@dataclass(frozen=True)
class AdvanceDirectiveConversationTurnInput:
    preparation: AdvanceDirectivePreparation
    understanding_state: UnderstandingState
    question: Optional[AdvanceDirectiveQuestion]
    previous_turns: Tuple[AdvanceDirectiveConversationTurn, ...] = ()


class GuardianAdvanceDirectiveConversationService:
    def advance(self, source: AdvanceDirectiveConversationTurnInput) -> AdvanceDirectiveConversationTurn:
        _type(source, AdvanceDirectiveConversationTurnInput, "source")
        preparation = source.preparation
        if preparation.understanding_state_hash != understanding_state_content_hash(source.understanding_state):
            raise ValueError("Preparation state hash mismatch")
        _items(source.previous_turns, AdvanceDirectiveConversationTurn, "previous_turns")
        if source.question is None:
            if any(item.essential for item in preparation.missing_information):
                raise ValueError("Essential gap requires controlled question")
            status = AdvanceDirectiveConversationStatus.CONVERSATION_PREPARATION_READY
            gap_id = question_id = question_text = None
            refs = ()
        else:
            gap_id = source.question.missing_information_id
            if not any(item.information_id == gap_id and item.essential for item in preparation.missing_information):
                raise ValueError("Question does not belong to an essential gap")
            repeated = next((turn for turn in source.previous_turns if turn.question_id == source.question.question_id and turn.missing_information_id == gap_id and turn.question == source.question.text), None)
            status = (AdvanceDirectiveConversationStatus.QUESTION_UNRESOLVED if repeated else AdvanceDirectiveConversationStatus.NEEDS_CLARIFICATION)
            question_id = source.question.question_id
            question_text = source.question.text
            refs = source.question.source_references
        draft = AdvanceDirectiveConversationTurn(
            "advance-directive-turn-pending", status, preparation.preparation_id,
            preparation.understanding_state_id, preparation.understanding_state_hash,
            gap_id, question_id, question_text, refs,
            source.previous_turns[-1].turn_id if source.previous_turns else None,
        )
        return replace(draft, turn_id=_semantic_id("advance-directive-turn", draft))


@dataclass(frozen=True)
class AdvanceDirectiveExternalClarification:
    source_turn_id: str
    answer_statement: UserStatementReference
    resolution: Optional[ClarificationResolution] = None
    revision: Optional[UnderstandingRevision] = None
    revision_reference: Optional[str] = None
    resulting_understanding_state_id: Optional[str] = None
    resulting_understanding_state_hash: Optional[str] = None

    def __post_init__(self) -> None:
        _id(self.source_turn_id, "source_turn_id", "advance-directive-turn")
        _type(self.answer_statement, UserStatementReference, "answer_statement")
        if self.resolution is not None:
            _type(self.resolution, ClarificationResolution, "resolution")
        if self.revision is not None:
            _type(self.revision, UnderstandingRevision, "revision")
        if self.revision_reference is not None:
            _text(self.revision_reference, "revision_reference")
        if self.resulting_understanding_state_id is not None:
            _id(self.resulting_understanding_state_id, "resulting_understanding_state_id", "understanding-state")
        if self.resulting_understanding_state_hash is not None and re.fullmatch(r"[0-9a-f]{64}", self.resulting_understanding_state_hash) is None:
            raise ValueError("resulting_understanding_state_hash is invalid")


@dataclass(frozen=True)
class AdvanceDirectiveProfessionalReviewPreparation:
    package_id: str
    journey_id: str
    understanding_state_id: str
    source_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    personal_wishes: Tuple[AdvanceDirectiveTextReference, ...]
    people: Tuple[AdvanceDirectivePersonReference, ...]
    documents: Tuple[DocumentReference, ...]
    medical_situations: Tuple[MedicalSituationReference, ...]
    medical_measures: Tuple[MedicalMeasureStatement, ...]
    personal_values: Tuple[AdvanceDirectiveTextReference, ...]
    limits_and_refusals: Tuple[AdvanceDirectiveTextReference, ...]
    unknowns: Tuple[Unknown, ...]
    deferred_points: Tuple[str, ...]
    rejected_proposal_points: Tuple[str, ...]
    closed_without_change_points: Tuple[str, ...]
    missing_controlled_questions: Tuple[str, ...]
    hypotheses: Tuple[Hypothesis, ...]
    contradictions: Tuple[Contradiction, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    professional_boundaries: Tuple[str, ...]


@dataclass(frozen=True)
class AdvanceDirectiveJourneyInput:
    preparation: AdvanceDirectivePreparation
    understanding_state: UnderstandingState
    gap_bindings: Tuple[AdvanceDirectiveGapBinding, ...]
    previous_turns: Tuple[AdvanceDirectiveConversationTurn, ...] = ()
    clarifications: Tuple[AdvanceDirectiveExternalClarification, ...] = ()
    create_professional_review_preparation: bool = False

    def __post_init__(self) -> None:
        _type(self.preparation, AdvanceDirectivePreparation, "preparation")
        _type(self.understanding_state, UnderstandingState, "understanding_state")
        _items(self.gap_bindings, AdvanceDirectiveGapBinding, "gap_bindings")
        _items(self.previous_turns, AdvanceDirectiveConversationTurn, "previous_turns")
        _items(self.clarifications, AdvanceDirectiveExternalClarification, "clarifications")
        if len({item.turn_id for item in self.previous_turns}) != len(self.previous_turns):
            raise ValueError("previous_turns must use unique IDs")
        if not isinstance(self.create_professional_review_preparation, bool):
            raise TypeError("create_professional_review_preparation must be bool")


@dataclass(frozen=True)
class AdvanceDirectiveJourney:
    journey_id: str
    status: AdvanceDirectiveJourneyStatus
    next_action: AdvanceDirectiveJourneyAction
    preparation: AdvanceDirectivePreparation
    understanding_state: UnderstandingState
    turns: Tuple[AdvanceDirectiveConversationTurn, ...]
    clarifications: Tuple[AdvanceDirectiveExternalClarification, ...]
    current_open_gap_id: Optional[str]
    current_question: Optional[AdvanceDirectiveQuestion]
    relevant_previous_turn_id: Optional[str]
    deferred_points: Tuple[str, ...]
    rejected_proposal_points: Tuple[str, ...]
    closed_without_change_points: Tuple[str, ...]
    blockers: Tuple[str, ...]
    professional_review: Optional[AdvanceDirectiveProfessionalReviewPreparation]


class GuardianAdvanceDirectiveJourneyService:
    def __init__(self, catalog: Optional[AdvanceDirectiveQuestionCatalog] = None) -> None:
        self.catalog = catalog or AdvanceDirectiveQuestionCatalog()
        self.conversation = GuardianAdvanceDirectiveConversationService()

    def build(self, source: AdvanceDirectiveJourneyInput) -> AdvanceDirectiveJourney:
        _type(source, AdvanceDirectiveJourneyInput, "source")
        prep = source.preparation
        journey_id = _semantic_id("advance-directive-journey", (prep.preparation_id, prep.triggering_statement.statement_id))
        expected_preparation_id = _semantic_id(
            "advance-directive-preparation",
            replace(prep, preparation_id="advance-directive-preparation-pending"),
        )
        if prep.preparation_id != expected_preparation_id:
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, AdvanceDirectiveJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=("PREPARATION_ID_MISMATCH",))
        if prep.understanding_state_hash != understanding_state_content_hash(source.understanding_state):
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, AdvanceDirectiveJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=("STATE_HASH_MISMATCH",))
        try:
            deferred, rejected, closed = self._validate_clarifications(source)
        except ValueError as error:
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, AdvanceDirectiveJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=(str(error),))
        open_gap = next((item for item in prep.missing_information if item.essential and item.information_id not in closed and item.information_id not in deferred), None)
        if open_gap is None:
            if source.create_professional_review_preparation:
                package = self._review(journey_id, prep, deferred, rejected, closed)
                return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY, AdvanceDirectiveJourneyAction.USE_PREPARATION_PACKAGE, deferred=deferred, rejected=rejected, closed=closed, review=package)
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY, AdvanceDirectiveJourneyAction.PREPARE_PROFESSIONAL_REVIEW, deferred=deferred, rejected=rejected, closed=closed)
        binding = next((item for item in source.gap_bindings if item.missing_information_id == open_gap.information_id), None)
        if binding is None:
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, AdvanceDirectiveJourneyAction.PROVIDE_CONTROLLED_QUESTION, gap=open_gap.information_id, blockers=("MISSING_GAP_BINDING",), deferred=deferred, rejected=rejected, closed=closed)
        question = self.catalog.for_gap(open_gap, binding)
        if question is None:
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, AdvanceDirectiveJourneyAction.PROVIDE_CONTROLLED_QUESTION, gap=open_gap.information_id, blockers=("MISSING_CONTROLLED_QUESTION",), deferred=deferred, rejected=rejected, closed=closed)
        if prep.next_understanding_question != question.text:
            return self._result(source, journey_id, AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, AdvanceDirectiveJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, gap=open_gap.information_id, blockers=("PREPARATION_QUESTION_MISMATCH",), deferred=deferred, rejected=rejected, closed=closed)
        turn = self.conversation.advance(AdvanceDirectiveConversationTurnInput(prep, source.understanding_state, question, source.previous_turns))
        turns = source.previous_turns if turn.status is AdvanceDirectiveConversationStatus.QUESTION_UNRESOLVED else source.previous_turns + (turn,)
        status = (AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED if turn.status is AdvanceDirectiveConversationStatus.QUESTION_UNRESOLVED else AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION)
        action = (AdvanceDirectiveJourneyAction.REVIEW_UNRESOLVED_QUESTION if status is AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED else AdvanceDirectiveJourneyAction.OBTAIN_USER_ANSWER)
        relevant = next((item.turn_id for item in source.previous_turns if item.question_id == question.question_id and item.missing_information_id == question.missing_information_id), None)
        if source.clarifications and source.clarifications[-1].source_turn_id == (relevant or turn.turn_id) and source.clarifications[-1].revision is None:
            status = AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION
            action = AdvanceDirectiveJourneyAction.OBTAIN_EXTERNAL_RESOLUTION
        return self._result(source, journey_id, status, action, gap=open_gap.information_id, question=question, relevant=relevant, turns=turns, deferred=deferred, rejected=rejected, closed=closed)

    def _validate_clarifications(self, source: AdvanceDirectiveJourneyInput) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
        turns = {item.turn_id: item for item in source.previous_turns}
        deferred = []
        rejected = []
        closed = []
        for item in source.clarifications:
            turn = turns.get(item.source_turn_id)
            if turn is None:
                raise ValueError("CLARIFICATION_TURN_MISMATCH")
            resolution = item.resolution
            if resolution is None:
                if any(value is not None for value in (item.revision, item.revision_reference, item.resulting_understanding_state_id, item.resulting_understanding_state_hash)):
                    raise ValueError("PARTIAL_EXTERNAL_ARTIFACT_CHAIN")
                continue
            if resolution.question_id != turn.question_id or resolution.answer_statement_id != item.answer_statement.statement_id or resolution.answer_text != item.answer_statement.text:
                raise ValueError("CLARIFICATION_REFERENCE_MISMATCH")
            selected = resolution.resolution_type is ClarificationResolutionType.SELECT_PROPOSAL
            complete_revision = all(value is not None for value in (item.revision, item.revision_reference, item.resulting_understanding_state_id, item.resulting_understanding_state_hash))
            if selected != complete_revision:
                raise ValueError("PARTIAL_EXTERNAL_ARTIFACT_CHAIN")
            if selected:
                assert item.revision is not None
                if resolution.selected_proposal_id is None or resolution.selected_operation is None:
                    raise ValueError("SELECTED_PROPOSAL_CONTRACT_MISSING")
                operation = resolution.selected_operation
                if not any(
                    change.operation is operation.operation
                    and change.source_statement == item.answer_statement.text
                    and change.target_text == operation.target_text
                    and change.result_text == operation.value_text
                    for change in item.revision.changes
                ):
                    raise ValueError("REVISION_OPERATION_MISMATCH")
                if item.revision.state != source.understanding_state or item.resulting_understanding_state_hash != understanding_state_content_hash(item.revision.state):
                    raise ValueError("RESULTING_STATE_MISMATCH")
            elif resolution.resolution_type is ClarificationResolutionType.KEEP_OPEN:
                deferred.append(turn.missing_information_id)
            elif resolution.resolution_type is ClarificationResolutionType.REJECT_PROPOSALS:
                deferred.append(turn.missing_information_id)
                rejected.append(turn.missing_information_id)
            elif resolution.resolution_type is ClarificationResolutionType.CLOSE_WITHOUT_CHANGE:
                closed.append(turn.missing_information_id)
        return tuple(value for value in deferred if value), tuple(value for value in rejected if value), tuple(value for value in closed if value)

    def _review(self, journey_id: str, prep: AdvanceDirectivePreparation, deferred: Tuple[str, ...], rejected: Tuple[str, ...], closed: Tuple[str, ...]) -> AdvanceDirectiveProfessionalReviewPreparation:
        draft = AdvanceDirectiveProfessionalReviewPreparation(
            "advance-directive-review-pending", journey_id,
            prep.understanding_state_id, prep.referenced_user_statements,
            prep.facts, prep.goals, prep.personal_wishes, prep.people,
            prep.documents, prep.medical_situations, prep.medical_measures,
            prep.personal_values, prep.limits_and_refusals, prep.unknowns,
            deferred, rejected, closed, (),
            prep.hypotheses, prep.contradictions, prep.organizational_steps,
            prep.professional_reviews, prep.professional_boundaries,
        )
        return replace(draft, package_id=_semantic_id("advance-directive-review", draft))

    @staticmethod
    def _result(source: AdvanceDirectiveJourneyInput, journey_id: str, status: AdvanceDirectiveJourneyStatus, action: AdvanceDirectiveJourneyAction, gap: Optional[str] = None, question: Optional[AdvanceDirectiveQuestion] = None, relevant: Optional[str] = None, turns: Optional[Tuple[AdvanceDirectiveConversationTurn, ...]] = None, blockers: Tuple[str, ...] = (), deferred: Tuple[str, ...] = (), rejected: Tuple[str, ...] = (), closed: Tuple[str, ...] = (), review: Optional[AdvanceDirectiveProfessionalReviewPreparation] = None) -> AdvanceDirectiveJourney:
        return AdvanceDirectiveJourney(journey_id, status, action, source.preparation, source.understanding_state, source.previous_turns if turns is None else turns, source.clarifications, gap, question, relevant, deferred, rejected, closed, blockers, review)


@dataclass(frozen=True)
class AdvanceDirectiveExperienceItem:
    reference_id: str
    text: str
    source_references: Tuple[str, ...]
    status: Optional[str] = None


@dataclass(frozen=True)
class AdvanceDirectiveExperience:
    experience_id: str
    journey_id: str
    journey_status: AdvanceDirectiveJourneyStatus
    status_heading: str
    status_description: str
    current_question: Optional[AdvanceDirectiveQuestion]
    allowed_actions: Tuple[AdvanceDirectiveExperienceActionType, ...]
    facts: Tuple[AdvanceDirectiveExperienceItem, ...]
    goals: Tuple[AdvanceDirectiveExperienceItem, ...]
    hypotheses: Tuple[AdvanceDirectiveExperienceItem, ...]
    unknowns: Tuple[AdvanceDirectiveExperienceItem, ...]
    contradictions: Tuple[AdvanceDirectiveExperienceItem, ...]
    people: Tuple[AdvanceDirectiveExperienceItem, ...]
    medical_situations: Tuple[AdvanceDirectiveExperienceItem, ...]
    medical_measures: Tuple[AdvanceDirectiveExperienceItem, ...]
    documents: Tuple[AdvanceDirectiveExperienceItem, ...]
    personal_wishes: Tuple[AdvanceDirectiveExperienceItem, ...]
    personal_values: Tuple[AdvanceDirectiveExperienceItem, ...]
    limits_and_refusals: Tuple[AdvanceDirectiveExperienceItem, ...]
    open_essential_points: Tuple[AdvanceDirectiveExperienceItem, ...]
    other_open_points: Tuple[AdvanceDirectiveExperienceItem, ...]
    organizational_steps: Tuple[AdvanceDirectiveExperienceItem, ...]
    deferred_points: Tuple[str, ...]
    rejected_proposal_points: Tuple[str, ...]
    closed_without_change_points: Tuple[str, ...]
    professional_reviews: Tuple[AdvanceDirectiveExperienceItem, ...]
    professional_boundaries: Tuple[str, ...]
    technical_errors: Tuple[str, ...]
    professional_review: Optional[AdvanceDirectiveProfessionalReviewPreparation]


class GuardianAdvanceDirectiveExperienceService:
    def present(self, journey: AdvanceDirectiveJourney) -> AdvanceDirectiveExperience:
        _type(journey, AdvanceDirectiveJourney, "journey")
        blocked = journey.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
        if not blocked:
            if journey.preparation.understanding_state_hash != understanding_state_content_hash(journey.understanding_state):
                raise ValueError("Experience cannot present inconsistent state")
            expected_action = {
                AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION: AdvanceDirectiveJourneyAction.OBTAIN_USER_ANSWER,
                AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: AdvanceDirectiveJourneyAction.OBTAIN_EXTERNAL_RESOLUTION,
                AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED: AdvanceDirectiveJourneyAction.REVIEW_UNRESOLVED_QUESTION,
                AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: AdvanceDirectiveJourneyAction.PROVIDE_CONTROLLED_QUESTION,
                AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY: AdvanceDirectiveJourneyAction.PREPARE_PROFESSIONAL_REVIEW,
                AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY: AdvanceDirectiveJourneyAction.USE_PREPARATION_PACKAGE,
            }[journey.status]
            if journey.next_action is not expected_action:
                raise ValueError("Experience detected incompatible next action")
            if journey.current_question is not None and journey.current_question.missing_information_id != journey.current_open_gap_id:
                raise ValueError("Experience detected question/gap mismatch")
            if journey.status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION and journey.current_question is None:
                raise ValueError("Experience requires the controlled question")
            if journey.status is AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY:
                package = journey.professional_review
                if package is None or package.journey_id != journey.journey_id or package.understanding_state_id != journey.preparation.understanding_state_id:
                    raise ValueError("Experience detected review package mismatch")
                expected_package_id = _semantic_id(
                    "advance-directive-review",
                    replace(package, package_id="advance-directive-review-pending"),
                )
                if package.package_id != expected_package_id:
                    raise ValueError("Experience detected review package ID mismatch")
        heading, description = _STATUS_TEXT[journey.status]
        prep = journey.preparation
        question = journey.current_question if journey.status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION else None
        actions = _experience_actions(journey)
        def state_items(prefix: str, values: tuple) -> tuple:
            return tuple(AdvanceDirectiveExperienceItem(_semantic_id(prefix, item), item.text, ("understanding-state:{}".format(prep.understanding_state_id),), getattr(getattr(item, "status", None), "value", None)) for item in values)
        if blocked:
            facts = goals = hypotheses = unknowns = contradictions = people = situations = measures = documents = wishes = values = limits = essential = other = steps = reviews = ()
        else:
            facts = state_items("advance-directive-fact", prep.facts)
            goals = state_items("advance-directive-goal", prep.goals)
            hypotheses = state_items("advance-directive-hypothesis", prep.hypotheses)
            unknowns = state_items("advance-directive-unknown", prep.unknowns)
            contradictions = state_items("advance-directive-contradiction", prep.contradictions)
            people = tuple(AdvanceDirectiveExperienceItem(item.reference_id, item.label, (item.source_reference,), item.role.value) for item in prep.people)
            situations = tuple(AdvanceDirectiveExperienceItem(item.situation_id, item.description, item.source_references, item.situation_type.value) for item in prep.medical_situations)
            measures = tuple(AdvanceDirectiveExperienceItem(item.statement_id, item.measure_type.value, item.source_references, item.position.value + ((":" + " | ".join(item.conditions)) if item.conditions else "")) for item in prep.medical_measures)
            documents = tuple(AdvanceDirectiveExperienceItem(item.id, item.document_type.value, (item.storage_reference,), "REFERENCE_ONLY") for item in prep.documents)
            wishes = tuple(AdvanceDirectiveExperienceItem(item.reference_id, item.text, item.source_references) for item in prep.personal_wishes)
            values = tuple(AdvanceDirectiveExperienceItem(item.reference_id, item.text, item.source_references) for item in prep.personal_values)
            limits = tuple(AdvanceDirectiveExperienceItem(item.reference_id, item.text, item.source_references) for item in prep.limits_and_refusals)
            active_gaps = tuple(item for item in prep.missing_information if item.information_id not in journey.deferred_points and item.information_id not in journey.closed_without_change_points)
            essential = tuple(AdvanceDirectiveExperienceItem(item.information_id, item.description, (item.source_reference,), "OPEN_ESSENTIAL") for item in active_gaps if item.essential)
            other = tuple(AdvanceDirectiveExperienceItem(item.information_id, item.description, (item.source_reference,), "OPEN_OTHER") for item in active_gaps if not item.essential)
            steps = tuple(AdvanceDirectiveExperienceItem(item.step_id, item.description, item.source_references, item.step_type.value) for item in prep.organizational_steps)
            reviews = tuple(AdvanceDirectiveExperienceItem(item.review_id, item.reason, item.source_references, item.need.value) for item in prep.professional_reviews)
        draft = AdvanceDirectiveExperience(
            "advance-directive-experience-pending", journey.journey_id,
            journey.status, heading, description, question, actions,
            facts, goals, hypotheses, unknowns, contradictions, people,
            situations, measures, documents, wishes, values, limits,
            essential, other, steps, journey.deferred_points,
            journey.rejected_proposal_points, journey.closed_without_change_points,
            reviews, prep.professional_boundaries, journey.blockers,
            journey.professional_review if not blocked else None,
        )
        return replace(draft, experience_id=_semantic_id("advance-directive-experience", draft))


def _experience_actions(journey: AdvanceDirectiveJourney) -> Tuple[AdvanceDirectiveExperienceActionType, ...]:
    status = journey.status
    if status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION:
        return (AdvanceDirectiveExperienceActionType.ANSWER_CURRENT_QUESTION, AdvanceDirectiveExperienceActionType.KEEP_POINT_OPEN, AdvanceDirectiveExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE)
    if status in (AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION, AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED):
        return (AdvanceDirectiveExperienceActionType.REQUEST_CONTROLLED_CLARIFICATION, AdvanceDirectiveExperienceActionType.KEEP_POINT_OPEN, AdvanceDirectiveExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE)
    if status in (AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS):
        return (AdvanceDirectiveExperienceActionType.NO_ACTION_AVAILABLE,)
    if status is AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY:
        return (AdvanceDirectiveExperienceActionType.REVIEW_OPEN_POINTS, AdvanceDirectiveExperienceActionType.REVIEW_CONTRADICTIONS, AdvanceDirectiveExperienceActionType.REVIEW_MEDICAL_STATEMENTS)
    return (AdvanceDirectiveExperienceActionType.REVIEW_PROFESSIONAL_PREPARATION, AdvanceDirectiveExperienceActionType.EXPORT_PROFESSIONAL_PREPARATION)


_STATUS_TEXT = {
    AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION: ("Eine Angabe ist noch offen", "Genau eine kontrollierte Frage ist für die Gesprächsvorbereitung offen."),
    AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: ("Klärung liegt vor", "Die fachliche Auflösung erfolgt außerhalb dieser Darstellung; keine Zustandsänderung wird behauptet."),
    AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED: ("Angabe bleibt ungeklärt", "Die bereits gestellte Frage wird nicht erneut ausgegeben oder automatisch gedeutet."),
    AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: ("Kontrollierte Frage fehlt", "Für die offene Angabe besteht keine freigegebene Frage; es wird keine Ersatzfrage formuliert."),
    AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: ("Darstellung nicht möglich", "Die Artefakte sind inkonsistent; Fachinhalte werden nicht teilweise dargestellt."),
    AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY: ("Gesprächsvorbereitung geordnet", "Keine ausdrücklich wesentliche Lücke ist unbearbeitet; dies ist keine medizinische oder rechtliche Freigabe."),
    AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY: ("Fachgespräch kann vorbereitet werden", "Ein strukturiertes Paket liegt vor; eine Patientenverfügung ist weder erstellt noch geprüft oder wirksam."),
}


def _default_questions() -> Tuple[ControlledAdvanceDirectiveQuestion, ...]:
    values = (
        ("goal", AdvanceDirectiveGapType.PREPARATION_GOAL, "Welches Ziel möchten Sie mit der Vorbereitung ausdrücklich verfolgen?"),
        ("situation", AdvanceDirectiveGapType.MEDICAL_SITUATION, "Welche medizinische Situation möchten Sie ausdrücklich besprechen?"),
        ("measure", AdvanceDirectiveGapType.MEASURE_POSITION, "Welche Haltung möchten Sie zu der ausdrücklich genannten Maßnahme festhalten?"),
        ("condition", AdvanceDirectiveGapType.POSITION_CONDITION, "Welche ausdrücklich genannte Bedingung gehört zu dieser Haltung?"),
        ("pain", AdvanceDirectiveGapType.PAIN_AND_SYMPTOM_RELIEF, "Was möchten Sie zur Schmerz- und Symptombehandlung ausdrücklich klären?"),
        ("person", AdvanceDirectiveGapType.TRUSTED_PERSON, "Welche Vertrauens- oder Bezugsperson möchten Sie ausdrücklich benennen?"),
        ("document", AdvanceDirectiveGapType.EXISTING_ADVANCE_DIRECTIVE, "Besteht bereits eine Patientenverfügung, die Sie referenzieren möchten?"),
        ("poa", AdvanceDirectiveGapType.EXISTING_POWER_OF_ATTORNEY, "Besteht eine Vorsorgevollmacht, die Sie ausdrücklich einbeziehen möchten?"),
        ("storage", AdvanceDirectiveGapType.STORAGE_AND_ACCESS, "Was möchten Sie zu Aufbewahrung und Zugänglichkeit ausdrücklich festhalten?"),
        ("consultation", AdvanceDirectiveGapType.MEDICAL_CONSULTATION, "Welchen ausdrücklich gewünschten ärztlichen Klärungsbedarf möchten Sie vorbereiten?"),
        ("contradiction", AdvanceDirectiveGapType.CONTRADICTION, "Welche widersprüchliche Angabe möchten Sie kontrolliert weiter klären?"),
        ("value", AdvanceDirectiveGapType.PERSONAL_VALUE, "Welchen persönlichen Wert möchten Sie ausdrücklich weiter klären?"),
    )
    return tuple(ControlledAdvanceDirectiveQuestion("understanding-question-advance-directive-" + key, gap, text) for key, gap, text in values)


def _semantic_id(prefix: str, value: object) -> str:
    payload = json.dumps(_canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "{}-{}".format(prefix, hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16])


def _canonical(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return tuple(_canonical(item) for item in value)
    return value


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _question(value: str) -> None:
    _text(value, "question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one question is required")


def _texts(value: object, name: str, required: bool = False) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be tuple".format(name))
    if required and not value:
        raise ValueError("{} must not be empty".format(name))
    for item in value:
        _text(item, name)


def _items(value: object, kind: type, name: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, kind) for item in value):
        raise TypeError("{} contains invalid items".format(name))


def _unique(value: tuple, attribute: str, name: str) -> None:
    identifiers = tuple(getattr(item, attribute) for item in value)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("{} must use unique IDs".format(name))


def _id(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix), value) is None:
        raise ValueError("{} is invalid".format(name))


def _enum(value: object, kind: type, name: str) -> None:
    if not isinstance(value, kind):
        raise TypeError("{} is invalid".format(name))


def _type(value: object, kind: type, name: str) -> None:
    if not isinstance(value, kind):
        raise TypeError("{} is invalid".format(name))
