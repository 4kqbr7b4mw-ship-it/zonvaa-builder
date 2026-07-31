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
    UnderstandingState,
    Unknown,
)
from life_decisions.models import DocumentReference


class PowerOfAttorneyConversationStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    CONVERSATION_PREPARATION_READY = "CONVERSATION_PREPARATION_READY"


class PowerOfAttorneyPersonRole(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    POSSIBLE_AUTHORIZED_PERSON = "POSSIBLE_AUTHORIZED_PERSON"
    POSSIBLE_SUBSTITUTE = "POSSIBLE_SUBSTITUTE"
    PROFESSIONAL_ADVISOR = "PROFESSIONAL_ADVISOR"
    OTHER = "OTHER"


class RepresentationArea(str, Enum):
    ASSETS = "ASSETS"
    BANKING = "BANKING"
    AUTHORITIES = "AUTHORITIES"
    HEALTH = "HEALTH"
    CARE = "CARE"
    RESIDENCE = "RESIDENCE"
    HOUSING = "HOUSING"
    POST_AND_TELECOMMUNICATIONS = "POST_AND_TELECOMMUNICATIONS"
    DIGITAL = "DIGITAL"
    BUSINESS_AND_CORPORATE = "BUSINESS_AND_CORPORATE"


class PreparationStepType(str, Enum):
    COLLECT_EXISTING_DOCUMENTS = "COLLECT_EXISTING_DOCUMENTS"
    CLARIFY_REPRESENTATION_AREAS = "CLARIFY_REPRESENTATION_AREAS"
    SPEAK_WITH_POSSIBLE_PERSONS = "SPEAK_WITH_POSSIBLE_PERSONS"
    CLARIFY_REPRESENTATION_MODE = "CLARIFY_REPRESENTATION_MODE"
    CONSIDER_SUBSTITUTE = "CONSIDER_SUBSTITUTE"
    CLARIFY_STORAGE_AND_ACCESS = "CLARIFY_STORAGE_AND_ACCESS"
    DISCUSS_REVOCATION = "DISCUSS_REVOCATION"
    PREPARE_PROFESSIONAL_CONSULTATION = "PREPARE_PROFESSIONAL_CONSULTATION"
    PREPARE_MEDICAL_CLARIFICATION = "PREPARE_MEDICAL_CLARIFICATION"
    OTHER = "OTHER"


class ProfessionalReviewCategory(str, Enum):
    NOTARIAL = "NOTARIAL"
    LEGAL = "LEGAL"
    MEDICAL = "MEDICAL"
    TAX = "TAX"
    CORPORATE_LAW = "CORPORATE_LAW"
    EXISTING_DOCUMENTS = "EXISTING_DOCUMENTS"
    ABUSE_OR_CONFLICT = "ABUSE_OR_CONFLICT"
    CARE = "CARE"
    SOCIAL_LAW = "SOCIAL_LAW"
    FINANCIAL = "FINANCIAL"
    REAL_ESTATE = "REAL_ESTATE"
    FAMILY_AND_ROLES = "FAMILY_AND_ROLES"


class ReviewNeed(str, Enum):
    REQUIRED = "REQUIRED"
    RECOMMENDED = "RECOMMENDED"


@dataclass(frozen=True)
class UserStatementReference:
    statement_id: str
    text: str
    source_reference: str

    def __post_init__(self) -> None:
        _identifier(self.statement_id, "statement_id", "statement")
        _text(self.text, "statement text")
        _text(self.source_reference, "statement source_reference")


@dataclass(frozen=True)
class RelevantPersonRole:
    reference_id: str
    label: str
    role: PowerOfAttorneyPersonRole
    source_reference: str

    def __post_init__(self) -> None:
        _identifier(self.reference_id, "person reference_id", "person")
        _text(self.label, "person label")
        _enum(self.role, PowerOfAttorneyPersonRole, "person role")
        _text(self.source_reference, "person source_reference")


@dataclass(frozen=True)
class RepresentationAreaReference:
    area: RepresentationArea
    source_reference: str

    def __post_init__(self) -> None:
        _enum(self.area, RepresentationArea, "representation area")
        _text(self.source_reference, "area source_reference")


@dataclass(frozen=True)
class MissingInformation:
    information_id: str
    description: str
    essential: bool
    source_reference: str

    def __post_init__(self) -> None:
        _identifier(
            self.information_id,
            "information_id",
            "missing-information",
        )
        _text(self.description, "missing information description")
        if not isinstance(self.essential, bool):
            raise TypeError("essential must be bool")
        _text(self.source_reference, "missing information source_reference")


@dataclass(frozen=True)
class OrganizationalPreparationStep:
    step_id: str
    step_type: PreparationStepType
    description: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.step_id, "step_id", "preparation-step")
        _enum(self.step_type, PreparationStepType, "step_type")
        _text(self.description, "step description")
        _text_tuple(self.source_references, "step source_references")


@dataclass(frozen=True)
class ProfessionalReviewNeed:
    review_id: str
    category: ProfessionalReviewCategory
    need: ReviewNeed
    reason: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.review_id, "review_id", "professional-review")
        _enum(self.category, ProfessionalReviewCategory, "review category")
        _enum(self.need, ReviewNeed, "review need")
        _text(self.reason, "review reason")
        _text_tuple(self.source_references, "review source_references")


@dataclass(frozen=True)
class PowerOfAttorneyConversationInput:
    understanding_state_id: str
    understanding_state: UnderstandingState
    triggering_statement_id: str
    user_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    goals: Tuple[Goal, ...]
    clarification_resolutions: Tuple[ClarificationResolution, ...]
    relevant_people: Tuple[RelevantPersonRole, ...]
    representation_areas: Tuple[RepresentationAreaReference, ...]
    existing_documents: Tuple[DocumentReference, ...]
    missing_information: Tuple[MissingInformation, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    next_understanding_question: Optional[str]

    def __post_init__(self) -> None:
        _identifier(
            self.understanding_state_id,
            "understanding_state_id",
            "understanding-state",
        )
        if not isinstance(self.understanding_state, UnderstandingState):
            raise TypeError("understanding_state is invalid")
        _identifier(
            self.triggering_statement_id,
            "triggering_statement_id",
            "statement",
        )
        _items(self.user_statements, UserStatementReference, "user_statements")
        _items(self.facts, Fact, "facts")
        _items(self.hypotheses, Hypothesis, "hypotheses")
        _items(self.unknowns, Unknown, "unknowns")
        _items(self.contradictions, Contradiction, "contradictions")
        _items(self.goals, Goal, "goals")
        _items(
            self.clarification_resolutions,
            ClarificationResolution,
            "clarification_resolutions",
        )
        _items(self.relevant_people, RelevantPersonRole, "relevant_people")
        _items(
            self.representation_areas,
            RepresentationAreaReference,
            "representation_areas",
        )
        _items(
            self.existing_documents,
            DocumentReference,
            "existing_documents",
        )
        _items(
            self.missing_information,
            MissingInformation,
            "missing_information",
        )
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
        self._validate_references()
        self._validate_completeness()

    def _validate_references(self) -> None:
        _unique_ids(self.user_statements, "statement_id", "user statements")
        _unique_ids(self.relevant_people, "reference_id", "relevant people")
        _unique_enum_values(
            self.representation_areas,
            "area",
            "representation areas",
        )
        _unique_ids(self.existing_documents, "id", "existing documents")
        _unique_ids(
            self.missing_information,
            "information_id",
            "missing information",
        )
        _unique_ids(self.organizational_steps, "step_id", "steps")
        _unique_ids(self.professional_reviews, "review_id", "reviews")
        statements = {
            statement.statement_id: statement
            for statement in self.user_statements
        }
        if self.triggering_statement_id not in statements:
            raise ValueError("triggering statement must be referenced")
        for resolution in self.clarification_resolutions:
            original = statements.get(resolution.proposal_statement_id)
            answer = statements.get(resolution.answer_statement_id)
            if (
                original is None
                or original.text != resolution.original_user_statement
            ):
                raise ValueError(
                    "clarification original statement must be referenced"
                )
            if answer is None or answer.text != resolution.answer_text:
                raise ValueError(
                    "clarification answer statement must be referenced"
                )
        for values, state_values, name in (
            (self.facts, self.understanding_state.facts, "fact"),
            (
                self.hypotheses,
                self.understanding_state.hypotheses,
                "hypothesis",
            ),
            (self.unknowns, self.understanding_state.unknowns, "unknown"),
            (
                self.contradictions,
                self.understanding_state.contradictions,
                "contradiction",
            ),
            (self.goals, self.understanding_state.goals, "goal"),
        ):
            if any(item not in state_values for item in values):
                raise ValueError(
                    "Referenced {} is outside the UnderstandingState".format(
                        name
                    )
                )

    def _validate_completeness(self) -> None:
        has_essential_gap = any(
            item.essential for item in self.missing_information
        )
        if has_essential_gap:
            if self.next_understanding_question is None:
                raise ValueError(
                    "Essential missing information requires one question"
                )
            _question(self.next_understanding_question)
        elif self.next_understanding_question is not None:
            raise ValueError(
                "A next question requires essential missing information"
            )


@dataclass(frozen=True)
class PowerOfAttorneyConversationPreparation:
    preparation_id: str
    understanding_state_id: str
    triggering_statement: UserStatementReference
    referenced_user_statements: Tuple[UserStatementReference, ...]
    known_situation: Tuple[Fact, ...]
    hypotheses: Tuple[Hypothesis, ...]
    goals: Tuple[Goal, ...]
    open_points: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    clarification_resolution_ids: Tuple[str, ...]
    relevant_people: Tuple[RelevantPersonRole, ...]
    representation_areas: Tuple[RepresentationAreaReference, ...]
    existing_documents: Tuple[DocumentReference, ...]
    missing_information: Tuple[MissingInformation, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    status: PowerOfAttorneyConversationStatus
    next_understanding_question: Optional[str]
    professional_boundaries: Tuple[str, ...]
    warnings: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.preparation_id, "preparation_id", "poa-preparation")
        _identifier(
            self.understanding_state_id,
            "understanding_state_id",
            "understanding-state",
        )
        if not isinstance(self.triggering_statement, UserStatementReference):
            raise TypeError("triggering_statement is invalid")
        _items(
            self.referenced_user_statements,
            UserStatementReference,
            "referenced_user_statements",
        )
        _items(self.known_situation, Fact, "known_situation")
        _items(self.hypotheses, Hypothesis, "hypotheses")
        _items(self.goals, Goal, "goals")
        _items(self.open_points, Unknown, "open_points")
        _items(self.contradictions, Contradiction, "contradictions")
        _optional_text_tuple(
            self.clarification_resolution_ids,
            "clarification_resolution_ids",
        )
        _items(self.relevant_people, RelevantPersonRole, "relevant_people")
        _items(
            self.representation_areas,
            RepresentationAreaReference,
            "representation_areas",
        )
        _items(
            self.existing_documents,
            DocumentReference,
            "existing_documents",
        )
        _items(
            self.missing_information,
            MissingInformation,
            "missing_information",
        )
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
        _enum(self.status, PowerOfAttorneyConversationStatus, "status")
        if self.next_understanding_question is not None:
            _question(self.next_understanding_question)
        _text_tuple(self.professional_boundaries, "professional_boundaries")
        _text_tuple(self.warnings, "warnings")


class GuardianLifeDecisionConversationService:
    """Prepares explicit Understanding references without interpreting them."""

    PROFESSIONAL_BOUNDARIES = (
        "Diese Vorbereitung ist keine Rechtsberatung und keine Aussage zur rechtlichen Wirksamkeit.",
        "Sie erzeugt weder eine Vorsorgevollmacht noch Vertrags- oder Urkundentext.",
        "Notare, Rechtsanwälte, Ärzte, Steuerberater und andere Fachpersonen werden nicht ersetzt.",
    )
    WARNINGS = (
        "Personen, Vertretungsbereiche und Fachprüfungen sind nur ausdrücklich bereitgestellte Angaben.",
        "Hypothesen, offene Punkte und Widersprüche bleiben als solche sichtbar.",
        "Die Vorbereitung bewertet weder Geschäftsfähigkeit noch Eignung, Missbrauch oder Interessenkonflikte.",
    )

    def prepare(
        self,
        preparation_input: PowerOfAttorneyConversationInput,
    ) -> PowerOfAttorneyConversationPreparation:
        if not isinstance(
            preparation_input,
            PowerOfAttorneyConversationInput,
        ):
            raise TypeError("preparation_input is invalid")
        statements = {
            statement.statement_id: statement
            for statement in preparation_input.user_statements
        }
        has_essential_gap = any(
            item.essential
            for item in preparation_input.missing_information
        )
        status = (
            PowerOfAttorneyConversationStatus.NEEDS_CLARIFICATION
            if has_essential_gap
            else PowerOfAttorneyConversationStatus.CONVERSATION_PREPARATION_READY
        )
        return PowerOfAttorneyConversationPreparation(
            preparation_id=_preparation_id(preparation_input),
            understanding_state_id=preparation_input.understanding_state_id,
            triggering_statement=statements[
                preparation_input.triggering_statement_id
            ],
            referenced_user_statements=preparation_input.user_statements,
            known_situation=preparation_input.facts,
            hypotheses=preparation_input.hypotheses,
            goals=preparation_input.goals,
            open_points=preparation_input.unknowns,
            contradictions=preparation_input.contradictions,
            clarification_resolution_ids=tuple(
                resolution.resolution_id
                for resolution in preparation_input.clarification_resolutions
            ),
            relevant_people=preparation_input.relevant_people,
            representation_areas=preparation_input.representation_areas,
            existing_documents=preparation_input.existing_documents,
            missing_information=preparation_input.missing_information,
            organizational_steps=preparation_input.organizational_steps,
            professional_reviews=preparation_input.professional_reviews,
            status=status,
            next_understanding_question=(
                preparation_input.next_understanding_question
            ),
            professional_boundaries=self.PROFESSIONAL_BOUNDARIES,
            warnings=self.WARNINGS,
        )


def _preparation_id(value: PowerOfAttorneyConversationInput) -> str:
    payload = json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return "poa-preparation-{}".format(digest[:16])


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


def _unique_ids(values: tuple, field_name: str, name: str) -> None:
    identifiers = tuple(getattr(item, field_name) for item in values)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("{} must have unique IDs".format(name))


def _unique_enum_values(values: tuple, field_name: str, name: str) -> None:
    enum_values = tuple(getattr(item, field_name) for item in values)
    if len(enum_values) != len(set(enum_values)):
        raise ValueError("{} must be unique".format(name))


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


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))


def _question(value: str) -> None:
    _text(value, "next_understanding_question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one understanding question is required")
