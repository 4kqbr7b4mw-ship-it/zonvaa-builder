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
    OrganizationalPreparationStep,
    ProfessionalReviewNeed,
    UserStatementReference,
)
from life_decisions.conversation_turn import understanding_state_content_hash
from life_decisions.models import DocumentReference


class FamilyCareSituationType(str, Enum):
    FAMILY_CARE = "FAMILY_CARE"


class FamilyCareDomainType(str, Enum):
    CARE_AND_SUPPORT = "CARE_AND_SUPPORT"
    HEALTH_AND_MEDICAL_ORGANIZATION = "HEALTH_AND_MEDICAL_ORGANIZATION"
    LIFE_DECISIONS_AND_REPRESENTATION = "LIFE_DECISIONS_AND_REPRESENTATION"
    HOUSING_AND_REAL_ESTATE = "HOUSING_AND_REAL_ESTATE"
    FINANCES_AND_COSTS = "FINANCES_AND_COSTS"
    FAMILY_AND_ROLES = "FAMILY_AND_ROLES"
    DOCUMENTS_AND_ORGANIZATION = "DOCUMENTS_AND_ORGANIZATION"


class FamilyCareGapType(str, Enum):
    PERSON_NEEDING_SUPPORT = "PERSON_NEEDING_SUPPORT"
    RELATIONSHIP_TO_USER = "RELATIONSHIP_TO_USER"
    CURRENT_LOCATION = "CURRENT_LOCATION"
    HOUSING_TYPE = "HOUSING_TYPE"
    SUPPORT_NEED = "SUPPORT_NEED"
    EXISTING_CARE_SUPPORT = "EXISTING_CARE_SUPPORT"
    MEDICAL_CONTACT = "MEDICAL_CONTACT"
    POWER_OF_ATTORNEY = "POWER_OF_ATTORNEY"
    ADVANCE_DIRECTIVE = "ADVANCE_DIRECTIVE"
    REPRESENTATIVE = "REPRESENTATIVE"
    FAMILY_SUPPORT = "FAMILY_SUPPORT"
    ROLE_DISTRIBUTION = "ROLE_DISTRIBUTION"
    FINANCIAL_BURDEN = "FINANCIAL_BURDEN"
    INSURANCE_OR_BENEFITS = "INSURANCE_OR_BENEFITS"
    PROPERTY_OR_TENANCY = "PROPERTY_OR_TENANCY"
    ORGANIZATIONAL_DEADLINE = "ORGANIZATIONAL_DEADLINE"
    DOCUMENTS = "DOCUMENTS"
    IMMEDIATE_GOAL = "IMMEDIATE_GOAL"


class FamilyCarePointStatus(str, Enum):
    OPEN = "OPEN"
    DEFERRED = "DEFERRED"
    PROPOSALS_REJECTED = "PROPOSALS_REJECTED"
    CLOSED_WITHOUT_CHANGE = "CLOSED_WITHOUT_CHANGE"
    ANSWERED_BY_REVISION = "ANSWERED_BY_REVISION"


class FamilyCareConversationStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    SITUATION_PREPARATION_READY = "SITUATION_PREPARATION_READY"


class FamilyCareJourneyStatus(str, Enum):
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    WAITING_FOR_EXTERNAL_RESOLUTION = "WAITING_FOR_EXTERNAL_RESOLUTION"
    QUESTION_UNRESOLVED = "QUESTION_UNRESOLVED"
    BLOCKED_MISSING_CONTROLLED_QUESTION = "BLOCKED_MISSING_CONTROLLED_QUESTION"
    BLOCKED_INCONSISTENT_ARTIFACTS = "BLOCKED_INCONSISTENT_ARTIFACTS"
    SITUATION_PREPARATION_READY = "SITUATION_PREPARATION_READY"
    CROSS_DOMAIN_REVIEW_PREPARATION_READY = "CROSS_DOMAIN_REVIEW_PREPARATION_READY"


class FamilyCareJourneyAction(str, Enum):
    OBTAIN_USER_ANSWER = "OBTAIN_USER_ANSWER"
    OBTAIN_EXTERNAL_RESOLUTION = "OBTAIN_EXTERNAL_RESOLUTION"
    REVIEW_UNRESOLVED_QUESTION = "REVIEW_UNRESOLVED_QUESTION"
    PROVIDE_CONTROLLED_QUESTION = "PROVIDE_CONTROLLED_QUESTION"
    CORRECT_INCONSISTENT_ARTIFACTS = "CORRECT_INCONSISTENT_ARTIFACTS"
    PREPARE_CROSS_DOMAIN_REVIEW = "PREPARE_CROSS_DOMAIN_REVIEW"
    USE_REVIEW_PACKAGE = "USE_REVIEW_PACKAGE"


class FamilyCareExperienceActionType(str, Enum):
    ANSWER_CURRENT_QUESTION = "ANSWER_CURRENT_QUESTION"
    KEEP_POINT_OPEN = "KEEP_POINT_OPEN"
    REJECT_OPEN_PROPOSALS = "REJECT_OPEN_PROPOSALS"
    CLOSE_POINT_WITHOUT_CHANGE = "CLOSE_POINT_WITHOUT_CHANGE"
    REQUEST_CONTROLLED_CLARIFICATION = "REQUEST_CONTROLLED_CLARIFICATION"
    REVIEW_OPEN_POINTS = "REVIEW_OPEN_POINTS"
    REVIEW_CONTRADICTIONS = "REVIEW_CONTRADICTIONS"
    REVIEW_DOMAIN_CONTRIBUTIONS = "REVIEW_DOMAIN_CONTRIBUTIONS"
    REVIEW_CROSS_DOMAIN_DEPENDENCIES = "REVIEW_CROSS_DOMAIN_DEPENDENCIES"
    REVIEW_PROFESSIONAL_PREPARATION = "REVIEW_PROFESSIONAL_PREPARATION"
    EXPORT_PROFESSIONAL_PREPARATION = "EXPORT_PROFESSIONAL_PREPARATION"
    NO_ACTION_AVAILABLE = "NO_ACTION_AVAILABLE"


@dataclass(frozen=True)
class FamilyCareTextReference:
    reference_id: str
    text: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.reference_id, "reference_id", "family-care-text")
        _text(self.text, "text")
        _texts(self.source_references, "source_references", True)


@dataclass(frozen=True)
class FamilyCarePersonReference:
    reference_id: str
    label: str
    role: str
    relationship: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.reference_id, "reference_id", "family-care-person")
        _text(self.label, "label")
        _text(self.role, "role")
        _text(self.relationship, "relationship")
        _texts(self.source_references, "source_references", True)


@dataclass(frozen=True)
class FamilyCareOpenPoint:
    point_id: str
    text: str
    source_references: Tuple[str, ...]
    domains: Tuple[FamilyCareDomainType, ...]
    essential: bool
    status: FamilyCarePointStatus = FamilyCarePointStatus.OPEN
    clarification_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _id(self.point_id, "point_id", "family-care-point")
        _text(self.text, "text")
        _texts(self.source_references, "source_references", True)
        _enums(self.domains, FamilyCareDomainType, "domains", True)
        if not isinstance(self.essential, bool):
            raise TypeError("essential must be bool")
        _enum(self.status, FamilyCarePointStatus, "status")
        _texts(self.clarification_references, "clarification_references")


@dataclass(frozen=True)
class FamilyCareDependency:
    dependency_id: str
    source_point_id: str
    target_point_id: str
    domains: Tuple[FamilyCareDomainType, ...]
    description: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.dependency_id, "dependency_id", "family-care-dependency")
        _id(self.source_point_id, "source_point_id", "family-care-point")
        _id(self.target_point_id, "target_point_id", "family-care-point")
        if self.source_point_id == self.target_point_id:
            raise ValueError("dependency must connect different points")
        _enums(self.domains, FamilyCareDomainType, "domains", True)
        _text(self.description, "description")
        _texts(self.source_references, "source_references", True)


@dataclass(frozen=True)
class FamilyCareDomainContributionInput:
    domain: FamilyCareDomainType
    facts: Tuple[Fact, ...] = ()
    goals: Tuple[Goal, ...] = ()
    hypotheses: Tuple[Hypothesis, ...] = ()
    unknowns: Tuple[Unknown, ...] = ()
    contradictions: Tuple[Contradiction, ...] = ()
    explicit_entries: Tuple[FamilyCareTextReference, ...] = ()
    essential_point_ids: Tuple[str, ...] = ()
    other_point_ids: Tuple[str, ...] = ()
    deferred_point_ids: Tuple[str, ...] = ()
    professional_reviews: Tuple[ProfessionalReviewNeed, ...] = ()
    organizational_steps: Tuple[OrganizationalPreparationStep, ...] = ()
    dependency_ids: Tuple[str, ...] = ()
    professional_boundaries: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _enum(self.domain, FamilyCareDomainType, "domain")
        for values, kind, name in (
            (self.facts, Fact, "facts"), (self.goals, Goal, "goals"),
            (self.hypotheses, Hypothesis, "hypotheses"),
            (self.unknowns, Unknown, "unknowns"),
            (self.contradictions, Contradiction, "contradictions"),
            (self.explicit_entries, FamilyCareTextReference, "explicit_entries"),
            (self.professional_reviews, ProfessionalReviewNeed, "professional_reviews"),
            (self.organizational_steps, OrganizationalPreparationStep, "organizational_steps"),
        ):
            _items(values, kind, name)
        for values, name in (
            (self.essential_point_ids, "essential_point_ids"),
            (self.other_point_ids, "other_point_ids"),
            (self.deferred_point_ids, "deferred_point_ids"),
            (self.dependency_ids, "dependency_ids"),
            (self.professional_boundaries, "professional_boundaries"),
        ):
            _texts(values, name)


@dataclass(frozen=True)
class FamilyCareDomainContribution:
    contribution_id: str
    situation_id: str
    domain: FamilyCareDomainType
    shared_understanding_state_id: str
    shared_understanding_state_hash: str
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    explicit_entries: Tuple[FamilyCareTextReference, ...]
    essential_open_points: Tuple[FamilyCareOpenPoint, ...]
    other_open_points: Tuple[FamilyCareOpenPoint, ...]
    deferred_points: Tuple[FamilyCareOpenPoint, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    dependency_ids: Tuple[str, ...]
    professional_boundaries: Tuple[str, ...]


@dataclass(frozen=True)
class FamilyCareSituationInput:
    understanding_state_id: str
    understanding_state: UnderstandingState
    triggering_statement_id: str
    user_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    people: Tuple[FamilyCarePersonReference, ...]
    support_needs: Tuple[FamilyCareTextReference, ...]
    housing_and_property: Tuple[FamilyCareTextReference, ...]
    financial_and_organizational: Tuple[FamilyCareTextReference, ...]
    care_and_health_documents: Tuple[FamilyCareTextReference, ...]
    documents: Tuple[DocumentReference, ...]
    open_points: Tuple[FamilyCareOpenPoint, ...]
    dependencies: Tuple[FamilyCareDependency, ...]
    contribution_inputs: Tuple[FamilyCareDomainContributionInput, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    clarification_resolutions: Tuple[ClarificationResolution, ...] = ()

    def __post_init__(self) -> None:
        _id(self.understanding_state_id, "understanding_state_id", "understanding-state")
        _type(self.understanding_state, UnderstandingState, "understanding_state")
        _id(self.triggering_statement_id, "triggering_statement_id", "statement")
        for values, kind, name in (
            (self.user_statements, UserStatementReference, "user_statements"),
            (self.facts, Fact, "facts"), (self.goals, Goal, "goals"),
            (self.hypotheses, Hypothesis, "hypotheses"),
            (self.unknowns, Unknown, "unknowns"),
            (self.contradictions, Contradiction, "contradictions"),
            (self.people, FamilyCarePersonReference, "people"),
            (self.support_needs, FamilyCareTextReference, "support_needs"),
            (self.housing_and_property, FamilyCareTextReference, "housing"),
            (self.financial_and_organizational, FamilyCareTextReference, "finances"),
            (self.care_and_health_documents, FamilyCareTextReference, "care_documents"),
            (self.documents, DocumentReference, "documents"),
            (self.open_points, FamilyCareOpenPoint, "open_points"),
            (self.dependencies, FamilyCareDependency, "dependencies"),
            (self.contribution_inputs, FamilyCareDomainContributionInput, "contributions"),
            (self.professional_reviews, ProfessionalReviewNeed, "professional_reviews"),
            (self.organizational_steps, OrganizationalPreparationStep, "organizational_steps"),
            (self.clarification_resolutions, ClarificationResolution, "clarifications"),
        ):
            _items(values, kind, name)
        _unique(self.user_statements, "statement_id", "user statements")
        if self.triggering_statement_id not in {item.statement_id for item in self.user_statements}:
            raise ValueError("triggering statement must be referenced")
        for values, attr, name in (
            (self.people, "reference_id", "people"),
            (self.documents, "id", "documents"),
            (self.open_points, "point_id", "open points"),
            (self.dependencies, "dependency_id", "dependencies"),
            (self.contribution_inputs, "domain", "contribution domains"),
        ):
            _unique(values, attr, name)
        for values, state_values, name in (
            (self.facts, self.understanding_state.facts, "facts"),
            (self.goals, self.understanding_state.goals, "goals"),
            (self.hypotheses, self.understanding_state.hypotheses, "hypotheses"),
            (self.unknowns, self.understanding_state.unknowns, "unknowns"),
            (self.contradictions, self.understanding_state.contradictions, "contradictions"),
        ):
            if any(item not in state_values for item in values):
                raise ValueError("Contribution source {} is outside UnderstandingState".format(name))
        points = {item.point_id: item for item in self.open_points}
        dependencies = {item.dependency_id: item for item in self.dependencies}
        for dependency in self.dependencies:
            if dependency.source_point_id not in points or dependency.target_point_id not in points:
                raise ValueError("dependency references unknown point")
        for contribution in self.contribution_inputs:
            for values, state_values in (
                (contribution.facts, self.facts), (contribution.goals, self.goals),
                (contribution.hypotheses, self.hypotheses),
                (contribution.unknowns, self.unknowns),
                (contribution.contradictions, self.contradictions),
            ):
                if any(item not in state_values for item in values):
                    raise ValueError("contribution references content outside situation")
            for point_id in contribution.essential_point_ids + contribution.other_point_ids + contribution.deferred_point_ids:
                if point_id not in points or contribution.domain not in points[point_id].domains:
                    raise ValueError("contribution references incompatible point")
            if any(item not in dependencies for item in contribution.dependency_ids):
                raise ValueError("contribution references unknown dependency")


@dataclass(frozen=True)
class FamilyCareSituation:
    situation_id: str
    situation_type: FamilyCareSituationType
    understanding_state_id: str
    understanding_state_hash: str
    understanding_state: UnderstandingState
    triggering_statement: UserStatementReference
    referenced_user_statements: Tuple[UserStatementReference, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    hypotheses: Tuple[Hypothesis, ...]
    unknowns: Tuple[Unknown, ...]
    contradictions: Tuple[Contradiction, ...]
    people: Tuple[FamilyCarePersonReference, ...]
    support_needs: Tuple[FamilyCareTextReference, ...]
    housing_and_property: Tuple[FamilyCareTextReference, ...]
    financial_and_organizational: Tuple[FamilyCareTextReference, ...]
    care_and_health_documents: Tuple[FamilyCareTextReference, ...]
    documents: Tuple[DocumentReference, ...]
    contributions: Tuple[FamilyCareDomainContribution, ...]
    open_points: Tuple[FamilyCareOpenPoint, ...]
    dependencies: Tuple[FamilyCareDependency, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_boundaries: Tuple[str, ...]
    warnings: Tuple[str, ...]


class GuardianFamilyCarePreparationService:
    BOUNDARIES = (
        "Diese Übersicht ist keine Pflegeberatung, medizinische oder rechtliche Beratung.",
        "Sie ist keine Steuer-, Finanz- oder Immobilienberatung und keine Immobilienbewertung.",
        "Sie trifft keine Leistungsentscheidung und nimmt keine Pflegegradeinstufung vor.",
        "Sie bewertet keine Person und erstellt keinen automatischen Maßnahmenplan.",
        "Der Guardian trifft keine automatische Entscheidung und aktiviert keine Domäne automatisch.",
    )
    WARNINGS = (
        "Alle Domain Contributions und Abhängigkeiten stammen ausschließlich aus expliziten Eingaben.",
        "Hypothesen, Unknowns und Widersprüche bleiben getrennt und unbewertet.",
        "Die Beiträge besitzen keine eigene Persönlichkeit und keinen eigenen Understanding State.",
    )

    def prepare(self, source: FamilyCareSituationInput) -> FamilyCareSituation:
        _type(source, FamilyCareSituationInput, "source")
        state_hash = understanding_state_content_hash(source.understanding_state)
        situation_seed = (source, state_hash)
        situation_id = _semantic_id("family-care-situation", situation_seed)
        point_map = {item.point_id: item for item in source.open_points}
        contributions = tuple(
            self._contribution(item, situation_id, source, point_map, state_hash)
            for item in source.contribution_inputs
        )
        statement = next(item for item in source.user_statements if item.statement_id == source.triggering_statement_id)
        return FamilyCareSituation(
            situation_id, FamilyCareSituationType.FAMILY_CARE,
            source.understanding_state_id, state_hash, source.understanding_state,
            statement, source.user_statements, source.facts, source.goals,
            source.hypotheses, source.unknowns, source.contradictions,
            source.people, source.support_needs, source.housing_and_property,
            source.financial_and_organizational, source.care_and_health_documents,
            source.documents, contributions, source.open_points,
            source.dependencies, source.professional_reviews,
            source.organizational_steps, self.BOUNDARIES, self.WARNINGS,
        )

    def _contribution(self, source: FamilyCareDomainContributionInput, situation_id: str, whole: FamilyCareSituationInput, points: dict, state_hash: str) -> FamilyCareDomainContribution:
        draft = FamilyCareDomainContribution(
            "family-care-contribution-pending", situation_id, source.domain,
            whole.understanding_state_id, state_hash, source.facts, source.goals,
            source.hypotheses, source.unknowns, source.contradictions,
            source.explicit_entries,
            tuple(points[item] for item in source.essential_point_ids),
            tuple(points[item] for item in source.other_point_ids),
            tuple(points[item] for item in source.deferred_point_ids),
            source.professional_reviews, source.organizational_steps,
            source.dependency_ids, source.professional_boundaries,
        )
        return replace(draft, contribution_id=_semantic_id("family-care-contribution", draft))


@dataclass(frozen=True)
class FamilyCareGapBinding:
    point_id: str
    gap_type: FamilyCareGapType

    def __post_init__(self) -> None:
        _id(self.point_id, "point_id", "family-care-point")
        _enum(self.gap_type, FamilyCareGapType, "gap_type")


@dataclass(frozen=True)
class ControlledFamilyCareQuestion:
    question_id: str
    gap_type: FamilyCareGapType
    text: str

    def __post_init__(self) -> None:
        _id(self.question_id, "question_id", "understanding-question")
        _enum(self.gap_type, FamilyCareGapType, "gap_type")
        _question(self.text)


@dataclass(frozen=True)
class FamilyCareQuestion:
    question_id: str
    point_id: str
    text: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _id(self.question_id, "question_id", "understanding-question")
        _id(self.point_id, "point_id", "family-care-point")
        _question(self.text)
        _texts(self.source_references, "source_references", True)


class FamilyCareQuestionCatalog:
    def __init__(self, questions: Optional[Tuple[ControlledFamilyCareQuestion, ...]] = None) -> None:
        self.questions = questions if questions is not None else _questions()
        _items(self.questions, ControlledFamilyCareQuestion, "questions")
        if len({item.gap_type for item in self.questions}) != len(self.questions):
            raise ValueError("Each gap type has at most one question")

    def for_point(self, point: FamilyCareOpenPoint, binding: FamilyCareGapBinding) -> Optional[FamilyCareQuestion]:
        if point.point_id != binding.point_id:
            raise ValueError("binding does not belong to point")
        definition = next((item for item in self.questions if item.gap_type is binding.gap_type), None)
        if definition is None:
            return None
        return FamilyCareQuestion(definition.question_id, point.point_id, definition.text, point.source_references)


@dataclass(frozen=True)
class FamilyCareConversationTurn:
    turn_id: str
    status: FamilyCareConversationStatus
    situation_id: str
    understanding_state_id: str
    understanding_state_hash: str
    point_id: Optional[str]
    question_id: Optional[str]
    question: Optional[str]
    question_source_references: Tuple[str, ...]
    previous_turn_id: Optional[str]
    state_changed_by_turn: bool = False

    def __post_init__(self) -> None:
        if self.state_changed_by_turn:
            raise ValueError("turn cannot change shared state")


class GuardianFamilyCareConversationService:
    def advance(self, situation: FamilyCareSituation, question: Optional[FamilyCareQuestion], previous_turns: Tuple[FamilyCareConversationTurn, ...]) -> FamilyCareConversationTurn:
        _type(situation, FamilyCareSituation, "situation")
        _items(previous_turns, FamilyCareConversationTurn, "previous_turns")
        if situation.understanding_state_hash != understanding_state_content_hash(situation.understanding_state):
            raise ValueError("situation state hash mismatch")
        if question is None:
            status = FamilyCareConversationStatus.SITUATION_PREPARATION_READY
            point_id = question_id = text = None
            refs = ()
        else:
            point_id, question_id, text, refs = question.point_id, question.question_id, question.text, question.source_references
            repeated = any(item.question_id == question.question_id and item.point_id == question.point_id and item.question == question.text for item in previous_turns)
            status = FamilyCareConversationStatus.QUESTION_UNRESOLVED if repeated else FamilyCareConversationStatus.NEEDS_CLARIFICATION
        draft = FamilyCareConversationTurn(
            "family-care-turn-pending", status, situation.situation_id,
            situation.understanding_state_id, situation.understanding_state_hash,
            point_id, question_id, text, refs,
            previous_turns[-1].turn_id if previous_turns else None,
        )
        return replace(draft, turn_id=_semantic_id("family-care-turn", draft))


@dataclass(frozen=True)
class FamilyCareExternalClarification:
    source_turn_id: str
    answer_statement: UserStatementReference
    resolution: Optional[ClarificationResolution] = None
    revision: Optional[UnderstandingRevision] = None
    revision_reference: Optional[str] = None
    resulting_understanding_state_id: Optional[str] = None
    resulting_understanding_state_hash: Optional[str] = None

    def __post_init__(self) -> None:
        _id(self.source_turn_id, "source_turn_id", "family-care-turn")
        _type(self.answer_statement, UserStatementReference, "answer_statement")
        if self.resolution is not None: _type(self.resolution, ClarificationResolution, "resolution")
        if self.revision is not None: _type(self.revision, UnderstandingRevision, "revision")


@dataclass(frozen=True)
class FamilyCareProfessionalReviewPreparation:
    package_id: str
    journey_id: str
    situation_id: str
    understanding_state_id: str
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    people: Tuple[FamilyCarePersonReference, ...]
    referenced_user_statements: Tuple[UserStatementReference, ...]
    contributions: Tuple[FamilyCareDomainContribution, ...]
    dependencies: Tuple[FamilyCareDependency, ...]
    essential_open_points: Tuple[FamilyCareOpenPoint, ...]
    other_open_points: Tuple[FamilyCareOpenPoint, ...]
    deferred_points: Tuple[FamilyCareOpenPoint, ...]
    rejected_proposal_points: Tuple[FamilyCareOpenPoint, ...]
    closed_without_change_points: Tuple[FamilyCareOpenPoint, ...]
    answered_by_revision_points: Tuple[FamilyCareOpenPoint, ...]
    hypotheses: Tuple[Hypothesis, ...]
    contradictions: Tuple[Contradiction, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_boundaries: Tuple[str, ...]


@dataclass(frozen=True)
class FamilyCareJourneyInput:
    situation: FamilyCareSituation
    gap_bindings: Tuple[FamilyCareGapBinding, ...]
    previous_turns: Tuple[FamilyCareConversationTurn, ...] = ()
    clarifications: Tuple[FamilyCareExternalClarification, ...] = ()
    create_review_preparation: bool = False

    def __post_init__(self) -> None:
        _type(self.situation, FamilyCareSituation, "situation")
        _items(self.gap_bindings, FamilyCareGapBinding, "gap_bindings")
        _items(self.previous_turns, FamilyCareConversationTurn, "previous_turns")
        _items(self.clarifications, FamilyCareExternalClarification, "clarifications")
        if len({item.turn_id for item in self.previous_turns}) != len(self.previous_turns):
            raise ValueError("previous_turns must use unique IDs")
        if not isinstance(self.create_review_preparation, bool):
            raise TypeError("create_review_preparation must be bool")


@dataclass(frozen=True)
class FamilyCareJourney:
    journey_id: str
    situation: FamilyCareSituation
    status: FamilyCareJourneyStatus
    next_action: FamilyCareJourneyAction
    turns: Tuple[FamilyCareConversationTurn, ...]
    clarifications: Tuple[FamilyCareExternalClarification, ...]
    current_open_point: Optional[FamilyCareOpenPoint]
    current_question: Optional[FamilyCareQuestion]
    relevant_previous_turn_id: Optional[str]
    essential_open_points: Tuple[FamilyCareOpenPoint, ...]
    other_open_points: Tuple[FamilyCareOpenPoint, ...]
    deferred_points: Tuple[FamilyCareOpenPoint, ...]
    rejected_proposal_points: Tuple[FamilyCareOpenPoint, ...]
    closed_without_change_points: Tuple[FamilyCareOpenPoint, ...]
    answered_by_revision_points: Tuple[FamilyCareOpenPoint, ...]
    blockers: Tuple[str, ...]
    professional_review: Optional[FamilyCareProfessionalReviewPreparation]


class GuardianFamilyCareJourneyService:
    def __init__(self, catalog: Optional[FamilyCareQuestionCatalog] = None) -> None:
        self.catalog = catalog or FamilyCareQuestionCatalog()
        self.conversation = GuardianFamilyCareConversationService()

    def build(self, source: FamilyCareJourneyInput) -> FamilyCareJourney:
        _type(source, FamilyCareJourneyInput, "source")
        situation = source.situation
        journey_id = _semantic_id("family-care-journey", situation.situation_id)
        if situation.understanding_state_hash != understanding_state_content_hash(situation.understanding_state):
            return self._result(source, journey_id, FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, FamilyCareJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=("STATE_HASH_MISMATCH",))
        if any(item.situation_id != situation.situation_id or item.shared_understanding_state_id != situation.understanding_state_id or item.shared_understanding_state_hash != situation.understanding_state_hash for item in situation.contributions):
            return self._result(source, journey_id, FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, FamilyCareJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=("CONTRIBUTION_BINDING_MISMATCH",))
        try:
            self._validate_history(source)
            deferred_ids, rejected_ids, closed_ids, answered_ids = self._clarifications(source)
        except ValueError as error:
            return self._result(source, journey_id, FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, FamilyCareJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, blockers=(str(error),))
        deferred_ids = tuple(dict.fromkeys(deferred_ids + tuple(item.point_id for item in situation.open_points if item.status in (FamilyCarePointStatus.DEFERRED, FamilyCarePointStatus.PROPOSALS_REJECTED))))
        rejected_ids = tuple(dict.fromkeys(rejected_ids + tuple(item.point_id for item in situation.open_points if item.status is FamilyCarePointStatus.PROPOSALS_REJECTED)))
        closed_ids = tuple(dict.fromkeys(closed_ids + tuple(item.point_id for item in situation.open_points if item.status is FamilyCarePointStatus.CLOSED_WITHOUT_CHANGE)))
        answered_ids = tuple(dict.fromkeys(answered_ids + tuple(item.point_id for item in situation.open_points if item.status is FamilyCarePointStatus.ANSWERED_BY_REVISION)))
        active = tuple(item for item in situation.open_points if item.status is FamilyCarePointStatus.OPEN and item.point_id not in deferred_ids and item.point_id not in closed_ids and item.point_id not in answered_ids)
        essential = tuple(item for item in active if item.essential)
        other = tuple(item for item in active if not item.essential)
        deferred = tuple(item for item in situation.open_points if item.point_id in deferred_ids)
        rejected = tuple(item for item in situation.open_points if item.point_id in rejected_ids)
        closed = tuple(item for item in situation.open_points if item.point_id in closed_ids)
        answered = tuple(replace(item, status=FamilyCarePointStatus.ANSWERED_BY_REVISION) for item in situation.open_points if item.point_id in answered_ids)
        if not essential:
            if source.create_review_preparation:
                review = self._review(journey_id, situation, essential, other, deferred, rejected, closed, answered)
                return self._result(source, journey_id, FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY, FamilyCareJourneyAction.USE_REVIEW_PACKAGE, essential=essential, other=other, deferred=deferred, rejected=rejected, closed=closed, answered=answered, review=review)
            return self._result(source, journey_id, FamilyCareJourneyStatus.SITUATION_PREPARATION_READY, FamilyCareJourneyAction.PREPARE_CROSS_DOMAIN_REVIEW, essential=essential, other=other, deferred=deferred, rejected=rejected, closed=closed, answered=answered)
        point = essential[0]
        binding = next((item for item in source.gap_bindings if item.point_id == point.point_id), None)
        if binding is None:
            return self._result(source, journey_id, FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, FamilyCareJourneyAction.PROVIDE_CONTROLLED_QUESTION, point=point, essential=essential, other=other, blockers=("MISSING_GAP_BINDING",))
        question = self.catalog.for_point(point, binding)
        if question is None:
            return self._result(source, journey_id, FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, FamilyCareJourneyAction.PROVIDE_CONTROLLED_QUESTION, point=point, essential=essential, other=other, blockers=("MISSING_CONTROLLED_QUESTION",))
        turn = self.conversation.advance(situation, question, source.previous_turns)
        repeated = turn.status is FamilyCareConversationStatus.QUESTION_UNRESOLVED
        turns = source.previous_turns if repeated else source.previous_turns + (turn,)
        relevant = next((item.turn_id for item in source.previous_turns if item.question_id == question.question_id and item.point_id == question.point_id), None)
        status = FamilyCareJourneyStatus.QUESTION_UNRESOLVED if repeated else FamilyCareJourneyStatus.NEEDS_CLARIFICATION
        action = FamilyCareJourneyAction.REVIEW_UNRESOLVED_QUESTION if repeated else FamilyCareJourneyAction.OBTAIN_USER_ANSWER
        if source.clarifications and source.clarifications[-1].resolution is None and source.clarifications[-1].source_turn_id == (relevant or turn.turn_id):
            status, action = FamilyCareJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION, FamilyCareJourneyAction.OBTAIN_EXTERNAL_RESOLUTION
        return self._result(source, journey_id, status, action, turns, point, question, relevant, essential, other, deferred, rejected, closed, answered)

    @staticmethod
    def _validate_history(source: FamilyCareJourneyInput) -> None:
        points = {item.point_id for item in source.situation.open_points}
        if len({item.point_id for item in source.gap_bindings}) != len(source.gap_bindings):
            raise ValueError("DUPLICATE_GAP_BINDING")
        if any(item.point_id not in points for item in source.gap_bindings):
            raise ValueError("FOREIGN_GAP_BINDING")
        previous = None
        for turn in source.previous_turns:
            if (
                turn.point_id not in points
                or turn.previous_turn_id != previous
            ):
                raise ValueError("TURN_HISTORY_MISMATCH")
            previous = turn.turn_id
        if len({item.source_turn_id for item in source.clarifications}) != len(source.clarifications):
            raise ValueError("DUPLICATE_TURN_CLARIFICATION")

    def _clarifications(self, source: FamilyCareJourneyInput) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
        turns = {item.turn_id: item for item in source.previous_turns}
        deferred, rejected, closed, answered = [], [], [], []
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
            complete = all(value is not None for value in (item.revision, item.revision_reference, item.resulting_understanding_state_id, item.resulting_understanding_state_hash))
            if selected != complete:
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
                if (
                    item.revision.state != source.situation.understanding_state
                    or item.resulting_understanding_state_id != source.situation.understanding_state_id
                    or item.resulting_understanding_state_hash != understanding_state_content_hash(item.revision.state)
                ):
                    raise ValueError("RESULTING_STATE_MISMATCH")
                answered.append(turn.point_id)
            elif resolution.resolution_type is ClarificationResolutionType.KEEP_OPEN:
                deferred.append(turn.point_id)
            elif resolution.resolution_type is ClarificationResolutionType.REJECT_PROPOSALS:
                deferred.append(turn.point_id); rejected.append(turn.point_id)
            elif resolution.resolution_type is ClarificationResolutionType.CLOSE_WITHOUT_CHANGE:
                closed.append(turn.point_id)
        return tuple(item for item in deferred if item), tuple(item for item in rejected if item), tuple(item for item in closed if item), tuple(item for item in answered if item)

    @staticmethod
    def _review(journey_id: str, situation: FamilyCareSituation, essential: tuple, other: tuple, deferred: tuple, rejected: tuple, closed: tuple, answered: tuple) -> FamilyCareProfessionalReviewPreparation:
        draft = FamilyCareProfessionalReviewPreparation(
            "family-care-review-pending", journey_id, situation.situation_id,
            situation.understanding_state_id, situation.facts, situation.goals,
            situation.people, situation.referenced_user_statements,
            situation.contributions, situation.dependencies, essential, other,
            deferred, rejected, closed, answered, situation.hypotheses,
            situation.contradictions, situation.professional_reviews,
            situation.organizational_steps, situation.professional_boundaries,
        )
        return replace(draft, package_id=_semantic_id("family-care-review", draft))

    @staticmethod
    def _result(source: FamilyCareJourneyInput, journey_id: str, status: FamilyCareJourneyStatus, action: FamilyCareJourneyAction, turns: Optional[Tuple[FamilyCareConversationTurn, ...]] = None, point: Optional[FamilyCareOpenPoint] = None, question: Optional[FamilyCareQuestion] = None, relevant: Optional[str] = None, essential: Tuple[FamilyCareOpenPoint, ...] = (), other: Tuple[FamilyCareOpenPoint, ...] = (), deferred: Tuple[FamilyCareOpenPoint, ...] = (), rejected: Tuple[FamilyCareOpenPoint, ...] = (), closed: Tuple[FamilyCareOpenPoint, ...] = (), answered: Tuple[FamilyCareOpenPoint, ...] = (), blockers: Tuple[str, ...] = (), review: Optional[FamilyCareProfessionalReviewPreparation] = None) -> FamilyCareJourney:
        return FamilyCareJourney(journey_id, source.situation, status, action, source.previous_turns if turns is None else turns, source.clarifications, point, question, relevant, essential, other, deferred, rejected, closed, answered, blockers, review)


@dataclass(frozen=True)
class FamilyCareExperience:
    experience_id: str
    journey_id: str
    status: FamilyCareJourneyStatus
    status_heading: str
    status_description: str
    current_question: Optional[FamilyCareQuestion]
    allowed_actions: Tuple[FamilyCareExperienceActionType, ...]
    facts: Tuple[Fact, ...]
    goals: Tuple[Goal, ...]
    contributions: Tuple[FamilyCareDomainContribution, ...]
    dependencies: Tuple[FamilyCareDependency, ...]
    essential_open_points: Tuple[FamilyCareOpenPoint, ...]
    other_open_points: Tuple[FamilyCareOpenPoint, ...]
    deferred_points: Tuple[FamilyCareOpenPoint, ...]
    rejected_proposal_points: Tuple[FamilyCareOpenPoint, ...]
    closed_without_change_points: Tuple[FamilyCareOpenPoint, ...]
    answered_by_revision_points: Tuple[FamilyCareOpenPoint, ...]
    hypotheses: Tuple[Hypothesis, ...]
    contradictions: Tuple[Contradiction, ...]
    people: Tuple[FamilyCarePersonReference, ...]
    documents: Tuple[DocumentReference, ...]
    organizational_steps: Tuple[OrganizationalPreparationStep, ...]
    professional_reviews: Tuple[ProfessionalReviewNeed, ...]
    professional_boundaries: Tuple[str, ...]
    technical_errors: Tuple[str, ...]
    professional_review: Optional[FamilyCareProfessionalReviewPreparation]


class GuardianFamilyCareExperienceService:
    def present(self, journey: FamilyCareJourney) -> FamilyCareExperience:
        _type(journey, FamilyCareJourney, "journey")
        if journey.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION and journey.current_question is None:
            raise ValueError("experience requires controlled question")
        if journey.status is not FamilyCareJourneyStatus.NEEDS_CLARIFICATION and journey.current_question is not None:
            raise ValueError("experience cannot expose question for this status")
        if journey.status is FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY:
            package = journey.professional_review
            if package is None or package.journey_id != journey.journey_id or package.situation_id != journey.situation.situation_id:
                raise ValueError("experience professional review mismatch")
        blocked = journey.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
        heading, description = _STATUS[journey.status]
        question = journey.current_question if journey.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION else None
        situation = journey.situation
        if blocked:
            facts = goals = contributions = dependencies = essential = other = deferred = rejected = closed = answered = hypotheses = contradictions = people = documents = steps = reviews = ()
            package = None
        else:
            if situation.understanding_state_hash != understanding_state_content_hash(situation.understanding_state):
                raise ValueError("experience state mismatch")
            facts, goals = situation.facts, situation.goals
            contributions, dependencies = situation.contributions, situation.dependencies
            essential, other = journey.essential_open_points, journey.other_open_points
            deferred, rejected, closed = journey.deferred_points, journey.rejected_proposal_points, journey.closed_without_change_points
            answered = journey.answered_by_revision_points
            hypotheses, contradictions = situation.hypotheses, situation.contradictions
            people, documents = situation.people, situation.documents
            steps, reviews = situation.organizational_steps, situation.professional_reviews
            package = journey.professional_review
        draft = FamilyCareExperience(
            "family-care-experience-pending", journey.journey_id, journey.status,
            heading, description, question, _actions(journey.status), facts,
            goals, contributions, dependencies, essential, other, deferred,
            rejected, closed, answered, hypotheses, contradictions, people, documents,
            steps, reviews, situation.professional_boundaries,
            journey.blockers, package,
        )
        return replace(draft, experience_id=_semantic_id("family-care-experience", draft))


def _actions(status: FamilyCareJourneyStatus) -> Tuple[FamilyCareExperienceActionType, ...]:
    if status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION:
        return (FamilyCareExperienceActionType.ANSWER_CURRENT_QUESTION, FamilyCareExperienceActionType.KEEP_POINT_OPEN, FamilyCareExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE)
    if status in (FamilyCareJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION, FamilyCareJourneyStatus.QUESTION_UNRESOLVED):
        return (FamilyCareExperienceActionType.REQUEST_CONTROLLED_CLARIFICATION, FamilyCareExperienceActionType.KEEP_POINT_OPEN, FamilyCareExperienceActionType.REJECT_OPEN_PROPOSALS, FamilyCareExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE)
    if status in (FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION, FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS):
        return (FamilyCareExperienceActionType.NO_ACTION_AVAILABLE,)
    if status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY:
        return (FamilyCareExperienceActionType.REVIEW_DOMAIN_CONTRIBUTIONS, FamilyCareExperienceActionType.REVIEW_CROSS_DOMAIN_DEPENDENCIES, FamilyCareExperienceActionType.REVIEW_OPEN_POINTS, FamilyCareExperienceActionType.REVIEW_CONTRADICTIONS)
    return (FamilyCareExperienceActionType.REVIEW_PROFESSIONAL_PREPARATION, FamilyCareExperienceActionType.EXPORT_PROFESSIONAL_PREPARATION)


_STATUS = {
    FamilyCareJourneyStatus.NEEDS_CLARIFICATION: ("Eine Angabe ist noch offen", "Genau eine kontrollierte Guardian-Frage ist offen."),
    FamilyCareJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: ("Klärung liegt vor", "Die externe fachliche Auflösung steht noch aus; keine Zustandsänderung wird behauptet."),
    FamilyCareJourneyStatus.QUESTION_UNRESOLVED: ("Angabe bleibt ungeklärt", "Die bereits gestellte Frage wird nicht erneut ausgegeben oder automatisch gedeutet."),
    FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: ("Kontrollierte Frage fehlt", "Für den offenen Punkt besteht keine freigegebene Frage; es wird keine Ersatzfrage erzeugt."),
    FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: ("Übersicht nicht zuverlässig darstellbar", "Inkonsistente Artefakte werden nicht teilweise dargestellt oder automatisch repariert."),
    FamilyCareJourneyStatus.SITUATION_PREPARATION_READY: ("Lebenslage ist strukturiert", "Keine ausdrücklich wesentliche Lücke ist unbearbeitet; dies ist keine fachliche Freigabe."),
    FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY: ("Fachübergreifende Gesprächsvorbereitung verfügbar", "Das Paket bereitet Fachgespräche vor und ist weder Beratung noch Maßnahmenplan."),
}


def _questions() -> Tuple[ControlledFamilyCareQuestion, ...]:
    values = (
        ("person", FamilyCareGapType.PERSON_NEEDING_SUPPORT, "Wer benötigt ausdrücklich Unterstützung?"),
        ("relationship", FamilyCareGapType.RELATIONSHIP_TO_USER, "Welche Beziehung besteht ausdrücklich zu der unterstützungsbedürftigen Person?"),
        ("location", FamilyCareGapType.CURRENT_LOCATION, "Wo hält sich die Person derzeit auf?"),
        ("housing", FamilyCareGapType.HOUSING_TYPE, "Welche aktuelle Wohnform ist ausdrücklich bekannt?"),
        ("support", FamilyCareGapType.SUPPORT_NEED, "Welcher konkrete Unterstützungsbedarf ist ausdrücklich bekannt?"),
        ("care", FamilyCareGapType.EXISTING_CARE_SUPPORT, "Welche pflegerische Unterstützung besteht bereits?"),
        ("medical", FamilyCareGapType.MEDICAL_CONTACT, "Welche medizinische Ansprechperson ist ausdrücklich bekannt?"),
        ("poa", FamilyCareGapType.POWER_OF_ATTORNEY, "Ist eine Vorsorgevollmacht ausdrücklich bekannt?"),
        ("directive", FamilyCareGapType.ADVANCE_DIRECTIVE, "Ist eine Patientenverfügung ausdrücklich bekannt?"),
        ("representative", FamilyCareGapType.REPRESENTATIVE, "Welche vertretungsberechtigte Person ist ausdrücklich bekannt?"),
        ("family", FamilyCareGapType.FAMILY_SUPPORT, "Welche Angehörigen oder Unterstützenden sind ausdrücklich bekannt?"),
        ("roles", FamilyCareGapType.ROLE_DISTRIBUTION, "Welche aktuelle Rollenverteilung ist ausdrücklich vereinbart?"),
        ("finance", FamilyCareGapType.FINANCIAL_BURDEN, "Welche wesentliche finanzielle Belastung ist ausdrücklich bekannt?"),
        ("benefits", FamilyCareGapType.INSURANCE_OR_BENEFITS, "Welche Versicherungs- oder Leistungsinformation liegt ausdrücklich vor?"),
        ("property", FamilyCareGapType.PROPERTY_OR_TENANCY, "Welche Eigentums- oder Mietsituation ist ausdrücklich bekannt?"),
        ("deadline", FamilyCareGapType.ORGANIZATIONAL_DEADLINE, "Welche akute organisatorische Frist wurde ausdrücklich genannt?"),
        ("documents", FamilyCareGapType.DOCUMENTS, "Welche vorhandenen Dokumente sind ausdrücklich bekannt?"),
        ("goal", FamilyCareGapType.IMMEDIATE_GOAL, "Welches unmittelbare Ziel möchten Sie ausdrücklich verfolgen?"),
    )
    return tuple(ControlledFamilyCareQuestion("understanding-question-family-care-" + key, gap, text) for key, gap, text in values)


def _semantic_id(prefix: str, value: object) -> str:
    payload = json.dumps(_canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "{}-{}".format(prefix, hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16])


def _canonical(value: object) -> object:
    if isinstance(value, Enum): return value.value
    if is_dataclass(value): return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple): return tuple(_canonical(item) for item in value)
    return value


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _question(value: str) -> None:
    _text(value, "question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one question is required")


def _texts(value: object, name: str, required: bool = False) -> None:
    if not isinstance(value, tuple): raise TypeError("{} must be tuple".format(name))
    if required and not value: raise ValueError("{} must not be empty".format(name))
    for item in value: _text(item, name)


def _items(value: object, kind: type, name: str) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, kind) for item in value): raise TypeError("{} contains invalid items".format(name))


def _unique(value: tuple, attribute: str, name: str) -> None:
    identifiers = tuple(getattr(item, attribute) for item in value)
    if len(set(identifiers)) != len(identifiers): raise ValueError("{} must be unique".format(name))


def _id(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix), value) is None: raise ValueError("{} is invalid".format(name))


def _enum(value: object, kind: type, name: str) -> None:
    if not isinstance(value, kind): raise TypeError("{} is invalid".format(name))


def _enums(value: object, kind: type, name: str, required: bool = False) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, kind) for item in value): raise TypeError("{} contains invalid values".format(name))
    if required and not value: raise ValueError("{} must not be empty".format(name))


def _type(value: object, kind: type, name: str) -> None:
    if not isinstance(value, kind): raise TypeError("{} is invalid".format(name))
