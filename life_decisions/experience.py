from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
from typing import Optional, Tuple

from guardian_understanding.clarification import ClarificationResolutionType
from guardian_understanding.models import Contradiction, Fact, Goal, Hypothesis
from life_decisions.conversation import MissingInformation
from life_decisions.conversation_turn import understanding_state_content_hash
from life_decisions.journey import (
    PowerOfAttorneyExternalClarification,
    PowerOfAttorneyJourney,
    PowerOfAttorneyJourneyAction,
    PowerOfAttorneyJourneyStatus,
    PowerOfAttorneyJourneyType,
    PowerOfAttorneyProfessionalReviewPreparation,
)


class PowerOfAttorneyExperienceActionType(str, Enum):
    ANSWER_CURRENT_QUESTION = "ANSWER_CURRENT_QUESTION"
    KEEP_POINT_OPEN = "KEEP_POINT_OPEN"
    CLOSE_POINT_WITHOUT_CHANGE = "CLOSE_POINT_WITHOUT_CHANGE"
    REQUEST_CONTROLLED_CLARIFICATION = "REQUEST_CONTROLLED_CLARIFICATION"
    REVIEW_OPEN_POINTS = "REVIEW_OPEN_POINTS"
    REVIEW_CONTRADICTIONS = "REVIEW_CONTRADICTIONS"
    PREPARE_PROFESSIONAL_REVIEW = "PREPARE_PROFESSIONAL_REVIEW"
    REVIEW_PROFESSIONAL_PREPARATION = "REVIEW_PROFESSIONAL_PREPARATION"
    EXPORT_PROFESSIONAL_PREPARATION = "EXPORT_PROFESSIONAL_PREPARATION"
    NO_ACTION_AVAILABLE = "NO_ACTION_AVAILABLE"


class PowerOfAttorneyExperiencePointDisposition(str, Enum):
    OPEN_ESSENTIAL = "OPEN_ESSENTIAL"
    OPEN_OTHER = "OPEN_OTHER"
    DEFERRED_KEEP_OPEN = "DEFERRED_KEEP_OPEN"
    PROPOSALS_REJECTED_POINT_STILL_OPEN = (
        "PROPOSALS_REJECTED_POINT_STILL_OPEN"
    )
    CLOSED_WITHOUT_CHANGE = "CLOSED_WITHOUT_CHANGE"
    ANSWERED_BY_EXTERNAL_REVISION = "ANSWERED_BY_EXTERNAL_REVISION"


@dataclass(frozen=True)
class PowerOfAttorneyExperienceItem:
    reference_id: str
    text: str
    source_references: Tuple[str, ...]
    lifecycle_status: Optional[str] = None

    def __post_init__(self) -> None:
        _text(self.reference_id, "reference_id")
        _text(self.text, "text")
        _text_items(self.source_references, "source_references")
        if self.lifecycle_status is not None:
            _text(self.lifecycle_status, "lifecycle_status")


@dataclass(frozen=True)
class PowerOfAttorneyExperiencePoint:
    point_id: str
    text: str
    source_references: Tuple[str, ...]
    essential: Optional[bool]
    disposition: PowerOfAttorneyExperiencePointDisposition
    resolution_id: Optional[str] = None

    def __post_init__(self) -> None:
        _identifier(self.point_id, "point_id", "missing-information")
        _text(self.text, "text")
        _text_items(self.source_references, "source_references")
        if self.essential is not None and not isinstance(self.essential, bool):
            raise TypeError("essential must be bool or None")
        _enum(
            self.disposition,
            PowerOfAttorneyExperiencePointDisposition,
            "disposition",
        )
        if self.resolution_id is not None:
            _identifier(
                self.resolution_id,
                "resolution_id",
                "clarification-resolution",
            )


@dataclass(frozen=True)
class PowerOfAttorneyExperienceQuestion:
    question_id: str
    text: str
    missing_information_id: str
    why_needed: str
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.question_id, "question_id", "understanding-question")
        _question(self.text)
        _identifier(
            self.missing_information_id,
            "missing_information_id",
            "missing-information",
        )
        _text(self.why_needed, "why_needed")
        _non_empty_text_items(self.source_references, "source_references")


@dataclass(frozen=True)
class PowerOfAttorneyExperienceAction:
    action_type: PowerOfAttorneyExperienceActionType
    label: str
    artifact_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        _enum(
            self.action_type,
            PowerOfAttorneyExperienceActionType,
            "action_type",
        )
        _text(self.label, "label")
        _text_items(self.artifact_references, "artifact_references")


@dataclass(frozen=True)
class PowerOfAttorneyExperienceTechnicalIssue:
    error_code: str
    affected_artifact_id: str
    expected_reference: Optional[str]
    actual_reference: Optional[str]
    technical_cause: str

    def __post_init__(self) -> None:
        _text(self.error_code, "error_code")
        _text(self.affected_artifact_id, "affected_artifact_id")
        for value, name in (
            (self.expected_reference, "expected_reference"),
            (self.actual_reference, "actual_reference"),
        ):
            if value is not None:
                _text(value, name)
        _text(self.technical_cause, "technical_cause")


@dataclass(frozen=True)
class PowerOfAttorneyProfessionalReviewExperience:
    package_reference: str
    known_situation: Tuple[PowerOfAttorneyExperienceItem, ...]
    goals: Tuple[PowerOfAttorneyExperienceItem, ...]
    people: Tuple[PowerOfAttorneyExperienceItem, ...]
    representation_areas: Tuple[PowerOfAttorneyExperienceItem, ...]
    document_references: Tuple[PowerOfAttorneyExperienceItem, ...]
    open_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    deferred_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    closed_without_change_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    hypotheses: Tuple[PowerOfAttorneyExperienceItem, ...]
    contradictions: Tuple[PowerOfAttorneyExperienceItem, ...]
    organizational_steps: Tuple[PowerOfAttorneyExperienceItem, ...]
    professional_reviews: Tuple[PowerOfAttorneyExperienceItem, ...]
    source_references: Tuple[str, ...]
    professional_boundaries: Tuple[str, ...]


@dataclass(frozen=True)
class PowerOfAttorneyJourneyExperience:
    experience_id: str
    journey_id: str
    journey_type: PowerOfAttorneyJourneyType
    journey_status: PowerOfAttorneyJourneyStatus
    status_heading: str
    status_description: str
    current_question: Optional[PowerOfAttorneyExperienceQuestion]
    unresolved_question_id: Optional[str]
    relevant_previous_turn_id: Optional[str]
    allowed_actions: Tuple[PowerOfAttorneyExperienceAction, ...]
    known_situation: Tuple[PowerOfAttorneyExperienceItem, ...]
    goals: Tuple[PowerOfAttorneyExperienceItem, ...]
    essential_open_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    other_open_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    deferred_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    rejected_proposal_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    closed_without_change_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    answered_points: Tuple[PowerOfAttorneyExperiencePoint, ...]
    hypotheses: Tuple[PowerOfAttorneyExperienceItem, ...]
    contradictions: Tuple[PowerOfAttorneyExperienceItem, ...]
    people: Tuple[PowerOfAttorneyExperienceItem, ...]
    representation_areas: Tuple[PowerOfAttorneyExperienceItem, ...]
    document_references: Tuple[PowerOfAttorneyExperienceItem, ...]
    organizational_steps: Tuple[PowerOfAttorneyExperienceItem, ...]
    professional_reviews: Tuple[PowerOfAttorneyExperienceItem, ...]
    professional_boundaries: Tuple[str, ...]
    warnings: Tuple[str, ...]
    next_action: PowerOfAttorneyExperienceActionType
    professional_review: Optional[PowerOfAttorneyProfessionalReviewExperience]
    technical_issues: Tuple[PowerOfAttorneyExperienceTechnicalIssue, ...]
    source_understanding_state_id: str
    source_understanding_state_hash: str


class PowerOfAttorneyExperienceConsistencyError(ValueError):
    def __init__(
        self,
        issue: PowerOfAttorneyExperienceTechnicalIssue,
        user_message: str,
    ) -> None:
        super().__init__(user_message)
        self.issue = issue
        self.user_message = user_message


class GuardianPowerOfAttorneyExperienceService:
    """Projects one validated journey into stable German presentation data."""

    def present(
        self,
        journey: PowerOfAttorneyJourney,
    ) -> PowerOfAttorneyJourneyExperience:
        if not isinstance(journey, PowerOfAttorneyJourney):
            raise TypeError("journey is invalid")
        self._validate(journey)
        blocked = journey.status is (
            PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
        )
        technical_issues = self._technical_issues(journey)
        if blocked:
            return self._experience(
                journey,
                technical_issues=technical_issues,
                suppress_domain_content=True,
            )
        return self._experience(journey, technical_issues=technical_issues)

    def _validate(self, journey: PowerOfAttorneyJourney) -> None:
        if journey.status is PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS:
            if not journey.blockers:
                self._fail(journey, "MISSING_TECHNICAL_CAUSE", None, "blocker")
            return
        if journey.understanding_state_hash != understanding_state_content_hash(
            journey.understanding_state
        ):
            self._fail(
                journey,
                "STATE_HASH_MISMATCH",
                journey.understanding_state_hash,
                "hash of referenced UnderstandingState",
            )
        if (
            journey.facts != journey.understanding_state.facts
            or journey.hypotheses != journey.understanding_state.hypotheses
            or journey.unknowns != journey.understanding_state.unknowns
            or journey.contradictions != journey.understanding_state.contradictions
            or journey.goals != journey.understanding_state.goals
        ):
            self._fail(
                journey,
                "STATE_CONTENT_MISMATCH",
                "Journey presentation content",
                "UnderstandingState content",
            )
        if journey.preparation is None:
            self._fail(journey, "PREPARATION_MISSING", None, "preparation")
        assert journey.preparation is not None
        if journey.preparation.understanding_state_id != journey.understanding_state_id:
            self._fail(
                journey,
                "PREPARATION_STATE_MISMATCH",
                journey.preparation.understanding_state_id,
                journey.understanding_state_id,
            )
        expected_action = _EXPECTED_JOURNEY_ACTION[journey.status]
        if journey.next_action is not expected_action:
            self._fail(
                journey,
                "NEXT_ACTION_MISMATCH",
                journey.next_action.value,
                expected_action.value,
            )
        if journey.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION:
            self._validate_current_question(journey, require_new_turn=True)
        elif journey.status in (
            PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION,
            PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED,
        ):
            self._validate_current_question(journey, require_new_turn=False)
            if journey.relevant_previous_turn_id is None:
                self._fail(journey, "PREVIOUS_TURN_MISSING", None, "poa-turn")
            if not any(
                turn.turn_id == journey.relevant_previous_turn_id
                for turn in journey.turns
            ):
                self._fail(
                    journey,
                    "PREVIOUS_TURN_NOT_FOUND",
                    journey.relevant_previous_turn_id,
                    "turn in journey history",
                )
        elif journey.status is (
            PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
        ):
            if journey.current_open_gap_id is None or journey.current_question is not None:
                self._fail(
                    journey,
                    "MISSING_QUESTION_BLOCK_INVALID",
                    "question or gap mismatch",
                    "gap without question",
                )
        elif journey.status is (
            PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
        ):
            if journey.current_open_gap_id is not None or journey.current_question is not None:
                self._fail(journey, "READY_WITH_ACTIVE_QUESTION", "question", None)
            if journey.review_preparation is not None:
                self._fail(journey, "UNEXPECTED_REVIEW_PACKAGE", "package", None)
        elif journey.status is (
            PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
        ):
            if journey.review_preparation is None:
                self._fail(journey, "REVIEW_PACKAGE_MISSING", None, "review package")
            self._validate_review_package(journey, journey.review_preparation)

    def _validate_current_question(
        self,
        journey: PowerOfAttorneyJourney,
        require_new_turn: bool,
    ) -> None:
        question = journey.current_question
        if question is None or journey.current_open_gap_id is None:
            self._fail(journey, "CURRENT_QUESTION_MISSING", None, "controlled question")
        assert question is not None
        if question.question_id not in _QUESTION_EXPLANATIONS:
            self._fail(
                journey,
                "QUESTION_EXPLANATION_MISSING",
                question.question_id,
                "controlled German explanation",
            )
        if question.missing_information_id != journey.current_open_gap_id:
            self._fail(
                journey,
                "QUESTION_GAP_MISMATCH",
                question.missing_information_id,
                journey.current_open_gap_id,
            )
        matching = tuple(
            turn
            for turn in journey.turns
            if turn.question_id == question.question_id
            and turn.missing_information_id == question.missing_information_id
            and turn.understanding_question == question.text
        )
        if not matching:
            self._fail(journey, "QUESTION_TURN_MISSING", question.question_id, "turn")
        if require_new_turn and journey.turns[-1] != matching[-1]:
            self._fail(
                journey,
                "CURRENT_TURN_NOT_LAST",
                matching[-1].turn_id,
                journey.turns[-1].turn_id,
            )

    def _validate_review_package(
        self,
        journey: PowerOfAttorneyJourney,
        package: Optional[PowerOfAttorneyProfessionalReviewPreparation],
    ) -> None:
        assert package is not None
        if package.journey_id != journey.journey_id:
            self._fail(
                journey,
                "REVIEW_JOURNEY_MISMATCH",
                package.journey_id,
                journey.journey_id,
            )
        if package.understanding_state_id != journey.understanding_state_id:
            self._fail(
                journey,
                "REVIEW_STATE_MISMATCH",
                package.understanding_state_id,
                journey.understanding_state_id,
            )
        expected_package_id = _semantic_id(
            "poa-review-preparation",
            replace(package, preparation_id="poa-review-preparation-pending"),
        )
        if package.preparation_id != expected_package_id:
            self._fail(
                journey,
                "REVIEW_ID_MISMATCH",
                package.preparation_id,
                expected_package_id,
            )
        for actual, expected, code in (
            (
                package.source_statements,
                journey.referenced_user_statements,
                "REVIEW_STATEMENTS_MISMATCH",
            ),
            (
                package.clarification_resolutions,
                tuple(item.resolution for item in journey.clarifications),
                "REVIEW_RESOLUTIONS_MISMATCH",
            ),
            (package.facts, journey.facts, "REVIEW_FACTS_MISMATCH"),
            (package.goals, journey.goals, "REVIEW_GOALS_MISMATCH"),
            (package.unknowns, journey.unknowns, "REVIEW_UNKNOWNS_MISMATCH"),
            (package.hypotheses, journey.hypotheses, "REVIEW_HYPOTHESES_MISMATCH"),
            (
                package.contradictions,
                journey.contradictions,
                "REVIEW_CONTRADICTIONS_MISMATCH",
            ),
            (package.people, journey.people, "REVIEW_PEOPLE_MISMATCH"),
            (
                package.representation_areas,
                journey.representation_areas,
                "REVIEW_AREAS_MISMATCH",
            ),
            (
                package.document_references,
                journey.document_references,
                "REVIEW_DOCUMENTS_MISMATCH",
            ),
            (
                package.organizational_steps,
                journey.organizational_steps,
                "REVIEW_STEPS_MISMATCH",
            ),
            (
                package.professional_reviews,
                journey.professional_reviews,
                "REVIEW_NEEDS_MISMATCH",
            ),
            (
                package.unanswered_essential_gaps,
                journey.open_points,
                "REVIEW_OPEN_POINTS_MISMATCH",
            ),
            (
                package.deferred_points,
                journey.deferred_points,
                "REVIEW_DEFERRED_POINTS_MISMATCH",
            ),
            (
                package.closed_without_change_points,
                journey.closed_without_change_points,
                "REVIEW_CLOSED_POINTS_MISMATCH",
            ),
            (
                package.missing_controlled_questions,
                (),
                "REVIEW_MISSING_QUESTIONS_MISMATCH",
            ),
            (
                package.professional_boundaries,
                journey.professional_boundaries,
                "REVIEW_BOUNDARIES_MISMATCH",
            ),
        ):
            if actual != expected:
                self._fail(journey, code, "package content", "journey content")

    def _experience(
        self,
        journey: PowerOfAttorneyJourney,
        technical_issues: Tuple[PowerOfAttorneyExperienceTechnicalIssue, ...],
        suppress_domain_content: bool = False,
    ) -> PowerOfAttorneyJourneyExperience:
        status_heading, status_description = _STATUS_TEXT[journey.status]
        state_source = _state_source(journey)
        known = () if suppress_domain_content else tuple(
            _state_item("fact", item, state_source) for item in journey.facts
        )
        goals = () if suppress_domain_content else tuple(
            _state_item("goal", item, state_source) for item in journey.goals
        )
        hypotheses = () if suppress_domain_content else tuple(
            _state_item("hypothesis", item, state_source)
            for item in journey.hypotheses
        )
        contradictions = () if suppress_domain_content else tuple(
            _state_item("contradiction", item, state_source)
            for item in journey.contradictions
        )
        classifications = _classify_points(journey) if not suppress_domain_content else {}
        actions = _actions(journey, suppress_domain_content)
        current_question = None
        if (
            not suppress_domain_content
            and journey.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
        ):
            assert journey.current_question is not None
            current_question = PowerOfAttorneyExperienceQuestion(
                question_id=journey.current_question.question_id,
                text=journey.current_question.text,
                missing_information_id=(
                    journey.current_question.missing_information_id
                ),
                why_needed=_QUESTION_EXPLANATIONS[
                    journey.current_question.question_id
                ],
                source_references=journey.current_question.source_references,
            )
        review = (
            _review_experience(journey, classifications)
            if not suppress_domain_content and journey.review_preparation is not None
            else None
        )
        draft = PowerOfAttorneyJourneyExperience(
            experience_id="poa-experience-pending",
            journey_id=journey.journey_id,
            journey_type=journey.journey_type,
            journey_status=journey.status,
            status_heading=status_heading,
            status_description=status_description,
            current_question=current_question,
            unresolved_question_id=(
                journey.current_question.question_id
                if not suppress_domain_content
                and journey.status
                in (
                    PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION,
                    PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED,
                )
                and journey.current_question is not None
                else None
            ),
            relevant_previous_turn_id=(
                None if suppress_domain_content else journey.relevant_previous_turn_id
            ),
            allowed_actions=actions,
            known_situation=known,
            goals=goals,
            essential_open_points=tuple(classifications.get("essential", ())),
            other_open_points=tuple(classifications.get("other", ())),
            deferred_points=tuple(classifications.get("deferred", ())),
            rejected_proposal_points=tuple(classifications.get("rejected", ())),
            closed_without_change_points=tuple(classifications.get("closed", ())),
            answered_points=tuple(classifications.get("answered", ())),
            hypotheses=hypotheses,
            contradictions=contradictions,
            people=() if suppress_domain_content else _people(journey),
            representation_areas=(
                () if suppress_domain_content else _areas(journey)
            ),
            document_references=(
                () if suppress_domain_content else _documents(journey)
            ),
            organizational_steps=(
                () if suppress_domain_content else _steps(journey)
            ),
            professional_reviews=(
                () if suppress_domain_content else _review_needs(journey)
            ),
            professional_boundaries=_stable_union(
                journey.professional_boundaries,
                _EXPERIENCE_BOUNDARIES,
            ),
            warnings=journey.warnings,
            next_action=actions[0].action_type,
            professional_review=review,
            technical_issues=technical_issues,
            source_understanding_state_id=journey.understanding_state_id,
            source_understanding_state_hash=journey.understanding_state_hash,
        )
        return PowerOfAttorneyJourneyExperience(
            **{
                field.name: (
                    _semantic_id("poa-experience", draft)
                    if field.name == "experience_id"
                    else getattr(draft, field.name)
                )
                for field in fields(draft)
            }
        )

    def _technical_issues(
        self,
        journey: PowerOfAttorneyJourney,
    ) -> Tuple[PowerOfAttorneyExperienceTechnicalIssue, ...]:
        if journey.status not in (
            PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION,
            PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS,
        ):
            return ()
        return tuple(
            PowerOfAttorneyExperienceTechnicalIssue(
                error_code=value.split(":", 1)[0],
                affected_artifact_id=journey.journey_id,
                expected_reference=(
                    "controlled question"
                    if journey.status
                    is PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
                    else "consistent journey artifacts"
                ),
                actual_reference=journey.current_open_gap_id,
                technical_cause=value,
            )
            for value in journey.blockers
        )

    @staticmethod
    def _fail(
        journey: PowerOfAttorneyJourney,
        code: str,
        actual: Optional[str],
        expected: Optional[str],
    ) -> None:
        issue = PowerOfAttorneyExperienceTechnicalIssue(
            code,
            journey.journey_id,
            expected,
            actual,
            "Experience consistency validation failed: {}".format(code),
        )
        raise PowerOfAttorneyExperienceConsistencyError(
            issue,
            "Die Journey kann auf Grundlage der vorliegenden Artefakte nicht zuverlässig dargestellt werden.",
        )


_STATUS_TEXT = {
    PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION: (
        "Eine Angabe ist noch offen",
        "Für die sachliche Vorbereitung ist genau eine kontrollierte Frage offen.",
    ),
    PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: (
        "Klärung wird fachlich aufgelöst",
        "Eine Antwort oder Klärung liegt vor. Die fachliche Auflösung erfolgt außerhalb dieser Darstellung; eine Zustandsänderung wird nicht behauptet.",
    ),
    PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED: (
        "Angabe bleibt ungeklärt",
        "Die Frage wurde bereits gestellt. Sie wird weder automatisch gedeutet noch erneut als neue Frage ausgegeben.",
    ),
    PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: (
        "Kontrollierte Frage fehlt",
        "Für die wesentliche offene Angabe ist keine freigegebene kontrollierte Frage vorhanden. Es wird keine Ersatzfrage formuliert.",
    ),
    PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: (
        "Darstellung derzeit nicht möglich",
        "Die vorliegenden Journey-Artefakte sind nicht konsistent. Fachliche Inhalte werden nicht aus widersprüchlichen Daten dargestellt und nichts wird automatisch repariert.",
    ),
    PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY: (
        "Gesprächsvorbereitung geordnet",
        "Keine ausdrücklich wesentliche Gesprächslücke ist unbearbeitet. Dies ist keine rechtliche oder fachliche Freigabe.",
    ),
    PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY: (
        "Vorbereitungspaket verfügbar",
        "Ein strukturiertes Paket für ein Gespräch mit einer geeigneten Fachperson ist vorhanden. Eine Vollmacht ist dadurch weder fertig noch geprüft oder wirksam.",
    ),
}


_EXPERIENCE_BOUNDARIES = (
    "Die Darstellung ist keine Rechtsberatung und enthält keinen Vollmachtstext.",
    "Sie prüft weder die rechtliche Wirksamkeit noch erteilt sie eine notarielle Freigabe.",
    "Sie bewertet weder bevollmächtigte Personen noch Geschäftsfähigkeit.",
    "Sie enthält keine medizinische oder steuerliche Beratung.",
    "Sie trifft keine automatische Entscheidung und legt Nutzerantworten nicht automatisch aus.",
)


_EXPECTED_JOURNEY_ACTION = {
    PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION: (
        PowerOfAttorneyJourneyAction.OBTAIN_USER_ANSWER
    ),
    PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: (
        PowerOfAttorneyJourneyAction.OBTAIN_EXTERNAL_RESOLUTION
    ),
    PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED: (
        PowerOfAttorneyJourneyAction.REVIEW_UNRESOLVED_QUESTION
    ),
    PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: (
        PowerOfAttorneyJourneyAction.PROVIDE_CONTROLLED_QUESTION
    ),
    PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: (
        PowerOfAttorneyJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS
    ),
    PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY: (
        PowerOfAttorneyJourneyAction.PREPARE_PROFESSIONAL_REVIEW
    ),
    PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY: (
        PowerOfAttorneyJourneyAction.USE_PREPARATION_PACKAGE
    ),
}


_QUESTION_EXPLANATIONS = {
    "understanding-question-poa-authorized-person": (
        "Die mögliche Person ist in der vorhandenen Gesprächsvorbereitung noch nicht ausdrücklich benannt."
    ),
    "understanding-question-poa-representation-areas": (
        "Ein ausdrücklich gewünschter Vertretungsbereich fehlt noch in der vorhandenen Gesprächsvorbereitung."
    ),
    "understanding-question-poa-existing-documents": (
        "Eine vorhandene Vollmacht oder Verfügung ist noch nicht ausdrücklich referenziert."
    ),
    "understanding-question-poa-representation-mode": (
        "Die organisatorische Form der Vertretung ist noch offen."
    ),
    "understanding-question-poa-substitute-person": (
        "Eine mögliche Ersatzperson ist noch nicht ausdrücklich benannt."
    ),
    "understanding-question-poa-storage-access": (
        "Aufbewahrungsort oder Zugang sind noch nicht ausdrücklich festgehalten."
    ),
    "understanding-question-poa-revocation": (
        "Ein ausdrücklich markierter Punkt zum Widerruf bleibt offen."
    ),
    "understanding-question-poa-professional-consultation": (
        "Ein vorhandener fachlicher Prüfbedarf ist noch nicht näher bezeichnet."
    ),
    "understanding-question-poa-medical-clarification": (
        "Ein vorhandener medizinischer Klärungsbedarf ist noch nicht näher bezeichnet."
    ),
}


_ACTION_LABELS = {
    PowerOfAttorneyExperienceActionType.ANSWER_CURRENT_QUESTION: (
        "Die aktuelle kontrollierte Frage beantworten"
    ),
    PowerOfAttorneyExperienceActionType.KEEP_POINT_OPEN: (
        "Den Punkt ausdrücklich offenhalten"
    ),
    PowerOfAttorneyExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE: (
        "Den Punkt ausdrücklich ohne Änderung schließen"
    ),
    PowerOfAttorneyExperienceActionType.REQUEST_CONTROLLED_CLARIFICATION: (
        "Eine kontrollierte externe Klärung veranlassen"
    ),
    PowerOfAttorneyExperienceActionType.REVIEW_OPEN_POINTS: (
        "Offene Punkte ansehen"
    ),
    PowerOfAttorneyExperienceActionType.REVIEW_CONTRADICTIONS: (
        "Widersprüche ansehen"
    ),
    PowerOfAttorneyExperienceActionType.PREPARE_PROFESSIONAL_REVIEW: (
        "Vorbereitungspaket ausdrücklich erzeugen lassen"
    ),
    PowerOfAttorneyExperienceActionType.REVIEW_PROFESSIONAL_PREPARATION: (
        "Vorbereitungspaket ansehen"
    ),
    PowerOfAttorneyExperienceActionType.EXPORT_PROFESSIONAL_PREPARATION: (
        "Vorbereitungspaket nutzerkontrolliert exportieren"
    ),
    PowerOfAttorneyExperienceActionType.NO_ACTION_AVAILABLE: (
        "Keine kontrollierte Folgeaktion verfügbar"
    ),
}


def _actions(
    journey: PowerOfAttorneyJourney,
    suppress_domain_content: bool,
) -> Tuple[PowerOfAttorneyExperienceAction, ...]:
    if suppress_domain_content or journey.status in (
        PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION,
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS,
    ):
        kinds = (PowerOfAttorneyExperienceActionType.NO_ACTION_AVAILABLE,)
    elif journey.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION:
        kinds = (
            PowerOfAttorneyExperienceActionType.ANSWER_CURRENT_QUESTION,
            PowerOfAttorneyExperienceActionType.KEEP_POINT_OPEN,
            PowerOfAttorneyExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
        )
    elif journey.status in (
        PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION,
        PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED,
    ):
        kinds = (
            PowerOfAttorneyExperienceActionType.REQUEST_CONTROLLED_CLARIFICATION,
            PowerOfAttorneyExperienceActionType.KEEP_POINT_OPEN,
            PowerOfAttorneyExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
        )
    elif journey.status is PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY:
        kinds = (PowerOfAttorneyExperienceActionType.PREPARE_PROFESSIONAL_REVIEW,)
        if journey.open_points:
            kinds += (PowerOfAttorneyExperienceActionType.REVIEW_OPEN_POINTS,)
        if journey.contradictions:
            kinds += (PowerOfAttorneyExperienceActionType.REVIEW_CONTRADICTIONS,)
    else:
        kinds = (
            PowerOfAttorneyExperienceActionType.REVIEW_PROFESSIONAL_PREPARATION,
            PowerOfAttorneyExperienceActionType.EXPORT_PROFESSIONAL_PREPARATION,
        )
        if journey.contradictions:
            kinds += (PowerOfAttorneyExperienceActionType.REVIEW_CONTRADICTIONS,)
    references = tuple(
        value
        for value in (
            journey.journey_id,
            journey.current_open_gap_id,
            (
                journey.current_question.question_id
                if journey.current_question is not None
                else None
            ),
            (
                journey.review_preparation.preparation_id
                if journey.review_preparation is not None
                else None
            ),
        )
        if value is not None
    )
    return tuple(
        PowerOfAttorneyExperienceAction(kind, _ACTION_LABELS[kind], references)
        for kind in kinds
    )


def _classify_points(journey: PowerOfAttorneyJourney) -> dict:
    preparation_gaps = {
        item.information_id: item
        for item in (
            journey.preparation.missing_information
            if journey.preparation is not None
            else ()
        )
    }
    resolution_by_gap = {}
    for clarification in journey.clarifications:
        turn = next(
            turn
            for turn in journey.turns
            if turn.turn_id == clarification.source_turn_id
        )
        if turn.missing_information_id is not None:
            resolution_by_gap[turn.missing_information_id] = clarification
    essential = tuple(
        _point(
            journey,
            point_id,
            PowerOfAttorneyExperiencePointDisposition.OPEN_ESSENTIAL,
            preparation_gaps,
            None,
        )
        for point_id in journey.open_points
        if point_id not in journey.deferred_points
    )
    other = tuple(
        _point(
            journey,
            gap.information_id,
            PowerOfAttorneyExperiencePointDisposition.OPEN_OTHER,
            preparation_gaps,
            None,
        )
        for gap in preparation_gaps.values()
        if not gap.essential
    )
    deferred = tuple(
        _point(
            journey,
            point_id,
            PowerOfAttorneyExperiencePointDisposition.DEFERRED_KEEP_OPEN,
            preparation_gaps,
            resolution_by_gap.get(point_id),
        )
        for point_id in journey.deferred_points
        if resolution_by_gap.get(point_id) is not None
        and resolution_by_gap[point_id].resolution.resolution_type
        is ClarificationResolutionType.KEEP_OPEN
    )
    rejected = tuple(
        _point(
            journey,
            point_id,
            PowerOfAttorneyExperiencePointDisposition.PROPOSALS_REJECTED_POINT_STILL_OPEN,
            preparation_gaps,
            resolution_by_gap.get(point_id),
        )
        for point_id in journey.deferred_points
        if resolution_by_gap.get(point_id) is not None
        and resolution_by_gap[point_id].resolution.resolution_type
        is ClarificationResolutionType.REJECT_PROPOSALS
    )
    closed = tuple(
        _point(
            journey,
            point_id,
            PowerOfAttorneyExperiencePointDisposition.CLOSED_WITHOUT_CHANGE,
            preparation_gaps,
            resolution_by_gap.get(point_id),
        )
        for point_id in journey.closed_without_change_points
    )
    answered = tuple(
        _point(
            journey,
            turn.missing_information_id,
            PowerOfAttorneyExperiencePointDisposition.ANSWERED_BY_EXTERNAL_REVISION,
            preparation_gaps,
            clarification,
        )
        for clarification in journey.clarifications
        for turn in journey.turns
        if clarification.source_turn_id == turn.turn_id
        and turn.missing_information_id is not None
        and clarification.resolution.resolution_type
        is ClarificationResolutionType.SELECT_PROPOSAL
    )
    return {
        "essential": essential,
        "other": other,
        "deferred": deferred,
        "rejected": rejected,
        "closed": closed,
        "answered": answered,
    }


def _point(
    journey: PowerOfAttorneyJourney,
    point_id: str,
    disposition: PowerOfAttorneyExperiencePointDisposition,
    preparation_gaps: dict,
    clarification: Optional[PowerOfAttorneyExternalClarification],
) -> PowerOfAttorneyExperiencePoint:
    gap = preparation_gaps.get(point_id)
    turn = next(
        (
            item
            for item in journey.turns
            if item.missing_information_id == point_id
        ),
        None,
    )
    text = (
        gap.description
        if isinstance(gap, MissingInformation)
        else "Punkt zur kontrollierten Frage: {}".format(
            turn.understanding_question if turn is not None else point_id
        )
    )
    sources = (
        (gap.source_reference,)
        if isinstance(gap, MissingInformation)
        else (turn.question_source_references if turn is not None else ())
    )
    return PowerOfAttorneyExperiencePoint(
        point_id=point_id,
        text=text,
        source_references=sources,
        essential=(gap.essential if isinstance(gap, MissingInformation) else None),
        disposition=disposition,
        resolution_id=(
            clarification.resolution.resolution_id
            if clarification is not None
            else None
        ),
    )


def _state_item(kind: str, item: object, state_source: str) -> PowerOfAttorneyExperienceItem:
    text = getattr(item, "text")
    status = getattr(item, "status", None)
    return PowerOfAttorneyExperienceItem(
        reference_id=_semantic_id("experience-{}".format(kind), (text, status)),
        text=text,
        source_references=(state_source,),
        lifecycle_status=(status.value if isinstance(status, Enum) else None),
    )


def _people(journey: PowerOfAttorneyJourney) -> Tuple[PowerOfAttorneyExperienceItem, ...]:
    return tuple(
        PowerOfAttorneyExperienceItem(
            item.reference_id,
            item.label,
            (item.source_reference,),
            item.role.value,
        )
        for item in journey.people
    )


def _areas(journey: PowerOfAttorneyJourney) -> Tuple[PowerOfAttorneyExperienceItem, ...]:
    return tuple(
        PowerOfAttorneyExperienceItem(
            _semantic_id("experience-area", (item.area.value, item.source_reference)),
            item.area.value,
            (item.source_reference,),
        )
        for item in journey.representation_areas
    )


def _documents(journey: PowerOfAttorneyJourney) -> Tuple[PowerOfAttorneyExperienceItem, ...]:
    return tuple(
        PowerOfAttorneyExperienceItem(
            item.id,
            "Dokumentreferenz: {}".format(item.document_type.value),
            (item.storage_reference,),
            "ANALYSIS_AUTHORIZED" if item.analysis_authorized else "REFERENCE_ONLY",
        )
        for item in journey.document_references
    )


def _steps(journey: PowerOfAttorneyJourney) -> Tuple[PowerOfAttorneyExperienceItem, ...]:
    return tuple(
        PowerOfAttorneyExperienceItem(
            item.step_id,
            item.description,
            item.source_references,
            item.step_type.value,
        )
        for item in journey.organizational_steps
    )


def _review_needs(
    journey: PowerOfAttorneyJourney,
) -> Tuple[PowerOfAttorneyExperienceItem, ...]:
    return tuple(
        PowerOfAttorneyExperienceItem(
            item.review_id,
            item.reason,
            item.source_references,
            "{}:{}".format(item.category.value, item.need.value),
        )
        for item in journey.professional_reviews
    )


def _review_experience(
    journey: PowerOfAttorneyJourney,
    classifications: dict,
) -> PowerOfAttorneyProfessionalReviewExperience:
    package = journey.review_preparation
    assert package is not None
    return PowerOfAttorneyProfessionalReviewExperience(
        package_reference=package.preparation_id,
        known_situation=tuple(
            _state_item("review-fact", item, _state_source(journey))
            for item in package.facts
        ),
        goals=tuple(
            _state_item("review-goal", item, _state_source(journey))
            for item in package.goals
        ),
        people=_people(journey),
        representation_areas=_areas(journey),
        document_references=_documents(journey),
        open_points=tuple(classifications.get("essential", ()))
        + tuple(classifications.get("other", ())),
        deferred_points=tuple(classifications.get("deferred", ()))
        + tuple(classifications.get("rejected", ())),
        closed_without_change_points=tuple(classifications.get("closed", ())),
        hypotheses=tuple(
            _state_item("review-hypothesis", item, _state_source(journey))
            for item in package.hypotheses
        ),
        contradictions=tuple(
            _state_item("review-contradiction", item, _state_source(journey))
            for item in package.contradictions
        ),
        organizational_steps=_steps(journey),
        professional_reviews=_review_needs(journey),
        source_references=tuple(
            item.source_reference for item in package.source_statements
        ),
        professional_boundaries=_stable_union(
            package.professional_boundaries,
            _EXPERIENCE_BOUNDARIES,
        ),
    )


def _state_source(journey: PowerOfAttorneyJourney) -> str:
    return "understanding-state:{}#{}".format(
        journey.understanding_state_id,
        journey.understanding_state_hash,
    )


def _stable_union(first: Tuple[str, ...], second: Tuple[str, ...]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(first + second))


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


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise ValueError("{} must be non-empty trimmed text".format(name))


def _text_items(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for item in value:
        _text(item, name)


def _non_empty_text_items(value: object, name: str) -> None:
    _text_items(value, name)
    if not value:
        raise ValueError("{} must not be empty".format(name))


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if re.fullmatch(r"{}-[A-Za-z0-9][A-Za-z0-9._-]*".format(prefix), value) is None:
        raise ValueError("{} is invalid".format(name))


def _question(value: str) -> None:
    _text(value, "question")
    if value.count("?") != 1 or not value.endswith("?"):
        raise ValueError("Exactly one question is required")


def _enum(value: object, enum_type: type, name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError("{} is invalid".format(name))
