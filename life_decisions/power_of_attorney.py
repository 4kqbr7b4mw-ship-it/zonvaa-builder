from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Optional, Tuple, Union

from builder.goal_application_service import GoalApplicationService
from goal.models import Goal
from goal.why_assessment import WhyAssessment
from knowledge.memory import MemoryType
from life_decisions.models import (
    DecisionRecord,
    DecisionReviewStatus,
    LifeDecisionCase,
    LifeDecisionTopic,
    ProfessionalReviewStatus,
)


class PowerOfAttorneyWorkflowError(RuntimeError):
    """The approved application flow cannot produce a domain overview."""


class PowerOfAttorneyWorkflowStatus(str, Enum):
    NEEDS_CLARIFICATION = "needs_clarification"
    STRUCTURED_OVERVIEW_READY = "structured_overview_ready"


class DocumentPresence(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"


class EvidenceStatus(str, Enum):
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"
    UNKNOWN = "unknown"


class ConflictStatus(str, Enum):
    NONE_CONFIRMED = "none_confirmed"
    POSSIBLE = "possible"
    UNKNOWN = "unknown"


class RepresentationMode(str, Enum):
    INDIVIDUAL = "individual"
    JOINT = "joint"


class AuthorityArea(str, Enum):
    ASSETS = "assets"
    BANKING_AND_FINANCE = "banking_and_finance"
    AUTHORITIES_AND_INSURANCE = "authorities_and_insurance"
    HEALTH_AND_CARE = "health_and_care"
    RESIDENCE_AND_HOUSING = "residence_and_housing"
    POST_AND_TELECOMMUNICATIONS = "post_and_telecommunications"
    REAL_ESTATE = "real_estate"
    DIGITAL_ACCOUNTS_AND_ASSETS = "digital_accounts_and_assets"
    SUBDELEGATION = "subdelegation"
    COURT_REPRESENTATION = "court_representation"


class AuthorityCoverageStatus(str, Enum):
    CONFIRMED_INCLUDED = "confirmed_included"
    CONFIRMED_EXCLUDED = "confirmed_excluded"
    UNKNOWN = "unknown"


def _text(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value.strip():
        raise ValueError("{} must not be empty".format(field_name))


def _aware(value: object, field_name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))


def _tuple_of(value: object, item_type: type, field_name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError(
            "{} items must be {}".format(field_name, item_type.__name__)
        )


def _unique(values: Iterable[str], field_name: str) -> None:
    identifiers = tuple(values)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("{} must be unique".format(field_name))


@dataclass(frozen=True)
class PowerOfAttorneyDocumentAssessment:
    presence: DocumentPresence
    presence_fact_id: Optional[str]
    document_reference_id: Optional[str]
    issued_at: Optional[datetime]
    issued_at_fact_id: Optional[str]
    last_reviewed_at: Optional[datetime]
    last_reviewed_fact_id: Optional[str]
    open_question_ids: Tuple[str, ...] = ()
    uncertainty_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.presence, DocumentPresence):
            raise TypeError("presence must be DocumentPresence")
        for value, field_name in (
            (self.presence_fact_id, "presence_fact_id"),
            (self.document_reference_id, "document_reference_id"),
            (self.issued_at_fact_id, "issued_at_fact_id"),
            (self.last_reviewed_fact_id, "last_reviewed_fact_id"),
        ):
            if value is not None:
                _text(value, field_name)
        for value, fact_id, field_name in (
            (self.issued_at, self.issued_at_fact_id, "issued_at"),
            (
                self.last_reviewed_at,
                self.last_reviewed_fact_id,
                "last_reviewed_at",
            ),
        ):
            if value is not None:
                _aware(value, field_name)
            if (value is None) != (fact_id is None):
                raise ValueError(
                    "{} and its fact id must be provided together".format(
                        field_name
                    )
                )
        _tuple_of(self.open_question_ids, str, "open_question_ids")
        _tuple_of(self.uncertainty_ids, str, "uncertainty_ids")
        _unique(self.open_question_ids, "open_question_ids")
        _unique(self.uncertainty_ids, "uncertainty_ids")
        if self.presence is DocumentPresence.PRESENT:
            if self.document_reference_id is None:
                raise ValueError(
                    "present document requires document_reference_id"
                )
        elif self.document_reference_id is not None:
            raise ValueError(
                "absent or unknown document cannot reference a document"
            )
        if self.presence is DocumentPresence.UNKNOWN:
            if self.presence_fact_id is not None:
                raise ValueError(
                    "unknown document presence cannot reference a fact"
                )
        elif self.presence_fact_id is None:
            raise ValueError(
                "confirmed document presence requires a verified fact"
            )
        if (
            self.presence is not DocumentPresence.PRESENT
            and not self.open_question_ids
        ):
            raise ValueError(
                "absent or unknown document requires an open question"
            )
        if self.presence is DocumentPresence.PRESENT:
            if (
                self.issued_at is None or self.last_reviewed_at is None
            ) and not self.open_question_ids:
                raise ValueError(
                    "unknown document dates require an open question"
                )
            if (
                self.last_reviewed_at is None
                and not self.uncertainty_ids
            ):
                raise ValueError(
                    "unknown document review date requires an uncertainty"
                )


@dataclass(frozen=True)
class AuthorizedPersonAssessment:
    id: str
    participant_id: str
    order: int
    representation_mode: RepresentationMode
    substitute_for_id: Optional[str]
    willingness: EvidenceStatus
    willingness_fact_id: Optional[str]
    willingness_question_id: Optional[str]
    conflict_status: ConflictStatus
    conflict_fact_id: Optional[str]
    conflict_uncertainty_id: Optional[str]

    def __post_init__(self) -> None:
        _text(self.id, "AuthorizedPersonAssessment id")
        _text(self.participant_id, "participant_id")
        if not isinstance(self.order, int) or isinstance(self.order, bool):
            raise TypeError("order must be an integer")
        if self.order < 1:
            raise ValueError("order must be positive")
        if not isinstance(self.representation_mode, RepresentationMode):
            raise TypeError("representation_mode must be RepresentationMode")
        if self.substitute_for_id is not None:
            _text(self.substitute_for_id, "substitute_for_id")
        if not isinstance(self.willingness, EvidenceStatus):
            raise TypeError("willingness must be EvidenceStatus")
        if not isinstance(self.conflict_status, ConflictStatus):
            raise TypeError("conflict_status must be ConflictStatus")
        for value, field_name in (
            (self.willingness_fact_id, "willingness_fact_id"),
            (self.willingness_question_id, "willingness_question_id"),
            (self.conflict_fact_id, "conflict_fact_id"),
            (
                self.conflict_uncertainty_id,
                "conflict_uncertainty_id",
            ),
        ):
            if value is not None:
                _text(value, field_name)
        if self.willingness is EvidenceStatus.CONFIRMED:
            if self.willingness_fact_id is None:
                raise ValueError(
                    "confirmed willingness requires a verified fact"
                )
            if self.willingness_question_id is not None:
                raise ValueError(
                    "confirmed willingness cannot reference an open question"
                )
        else:
            if self.willingness_question_id is None:
                raise ValueError(
                    "unconfirmed willingness requires an open question"
                )
            if self.willingness_fact_id is not None:
                raise ValueError(
                    "unconfirmed willingness cannot reference a fact"
                )
        if self.conflict_status is ConflictStatus.NONE_CONFIRMED:
            if self.conflict_fact_id is None:
                raise ValueError(
                    "confirmed absence of conflict requires a verified fact"
                )
            if self.conflict_uncertainty_id is not None:
                raise ValueError(
                    "confirmed absence of conflict cannot reference an "
                    "uncertainty"
                )
        else:
            if self.conflict_uncertainty_id is None:
                raise ValueError(
                    "possible or unknown conflict requires an uncertainty"
                )
            if self.conflict_fact_id is not None:
                raise ValueError(
                    "possible or unknown conflict cannot reference a fact"
                )


@dataclass(frozen=True)
class AuthorityScopeAssessment:
    id: str
    area: AuthorityArea
    status: AuthorityCoverageStatus
    fact_id: Optional[str]
    open_question_id: Optional[str]

    def __post_init__(self) -> None:
        _text(self.id, "AuthorityScopeAssessment id")
        if not isinstance(self.area, AuthorityArea):
            raise TypeError("area must be AuthorityArea")
        if not isinstance(self.status, AuthorityCoverageStatus):
            raise TypeError("status must be AuthorityCoverageStatus")
        if self.fact_id is not None:
            _text(self.fact_id, "fact_id")
        if self.open_question_id is not None:
            _text(self.open_question_id, "open_question_id")
        if self.status is AuthorityCoverageStatus.UNKNOWN:
            if self.open_question_id is None:
                raise ValueError("unknown authority area requires a question")
            if self.fact_id is not None:
                raise ValueError(
                    "unknown authority area cannot reference a fact"
                )
        else:
            if self.fact_id is None:
                raise ValueError(
                    "confirmed authority area requires a verified fact"
                )
            if self.open_question_id is not None:
                raise ValueError(
                    "confirmed authority area cannot reference a question"
                )


@dataclass(frozen=True)
class OrganizationalNextAction:
    id: str
    description: str
    related_reference_ids: Tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.id, "OrganizationalNextAction id")
        _text(self.description, "OrganizationalNextAction description")
        _tuple_of(
            self.related_reference_ids,
            str,
            "related_reference_ids",
        )
        for reference in self.related_reference_ids:
            _text(reference, "related_reference_ids item")
        _unique(self.related_reference_ids, "related_reference_ids")


@dataclass(frozen=True)
class PowerOfAttorneyWorkflowInput:
    case: LifeDecisionCase
    document: PowerOfAttorneyDocumentAssessment
    authorized_persons: Tuple[AuthorizedPersonAssessment, ...]
    authority_scopes: Tuple[AuthorityScopeAssessment, ...]
    completed_review_fact_ids: Tuple[Tuple[str, str], ...]
    next_actions: Tuple[OrganizationalNextAction, ...]
    decision_record_id: str
    evaluated_at: datetime
    decision_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.case, LifeDecisionCase):
            raise TypeError("case must be LifeDecisionCase")
        if self.case.topic is not LifeDecisionTopic.POWER_OF_ATTORNEY:
            raise ValueError("case topic must be power_of_attorney")
        if not isinstance(
            self.document,
            PowerOfAttorneyDocumentAssessment,
        ):
            raise TypeError(
                "document must be PowerOfAttorneyDocumentAssessment"
            )
        _tuple_of(
            self.authorized_persons,
            AuthorizedPersonAssessment,
            "authorized_persons",
        )
        _tuple_of(
            self.authority_scopes,
            AuthorityScopeAssessment,
            "authority_scopes",
        )
        _tuple_of(
            self.next_actions,
            OrganizationalNextAction,
            "next_actions",
        )
        if not isinstance(self.completed_review_fact_ids, tuple) or not all(
            isinstance(pair, tuple)
            and len(pair) == 2
            and all(isinstance(item, str) for item in pair)
            for pair in self.completed_review_fact_ids
        ):
            raise TypeError(
                "completed_review_fact_ids must contain id pairs"
            )
        _text(self.decision_record_id, "decision_record_id")
        _aware(self.evaluated_at, "evaluated_at")
        _text(self.decision_version, "decision_version")
        self._validate_references()

    def _validate_references(self) -> None:
        participant_ids = {item.id for item in self.case.participants}
        document_ids = {
            item.id for item in self.case.document_references
        }
        fact_ids = {item.id for item in self.case.verified_facts}
        question_ids = {item.id for item in self.case.open_questions}
        uncertainty_ids = {item.id for item in self.case.uncertainties}
        review_by_id = {
            item.id: item for item in self.case.professional_reviews
        }
        schedule_ids = {item.id for item in self.case.review_schedules}

        if self.case.owner not in participant_ids:
            raise ValueError("case owner must reference a participant")
        if (
            self.document.document_reference_id is not None
            and self.document.document_reference_id not in document_ids
        ):
            raise ValueError("document reference is outside the case")
        for fact_id in (
            self.document.presence_fact_id,
            self.document.issued_at_fact_id,
            self.document.last_reviewed_fact_id,
        ):
            if fact_id is not None and fact_id not in fact_ids:
                raise ValueError("document fact is outside the case")
        if not set(self.document.open_question_ids) <= question_ids:
            raise ValueError("document question is outside the case")
        if not set(self.document.uncertainty_ids) <= uncertainty_ids:
            raise ValueError("document uncertainty is outside the case")

        _unique(
            (item.id for item in self.authorized_persons),
            "authorized_person ids",
        )
        _unique(
            (str(item.order) for item in self.authorized_persons),
            "authorized_person order",
        )
        assessment_ids = {item.id for item in self.authorized_persons}
        for person in self.authorized_persons:
            if person.participant_id not in participant_ids:
                raise ValueError("authorized person is outside the case")
            if person.substitute_for_id is not None:
                if (
                    person.substitute_for_id not in assessment_ids
                    or person.substitute_for_id == person.id
                ):
                    raise ValueError(
                        "substitute_for_id must reference another assessment"
                    )
            if (
                person.willingness_fact_id is not None
                and person.willingness_fact_id not in fact_ids
            ):
                raise ValueError("willingness fact is outside the case")
            if (
                person.willingness_question_id is not None
                and person.willingness_question_id not in question_ids
            ):
                raise ValueError("willingness question is outside the case")
            if (
                person.conflict_fact_id is not None
                and person.conflict_fact_id not in fact_ids
            ):
                raise ValueError("conflict fact is outside the case")
            if (
                person.conflict_uncertainty_id is not None
                and person.conflict_uncertainty_id not in uncertainty_ids
            ):
                raise ValueError("conflict uncertainty is outside the case")

        _unique(
            (item.id for item in self.authority_scopes),
            "authority scope ids",
        )
        areas = tuple(item.area for item in self.authority_scopes)
        if set(areas) != set(AuthorityArea) or len(areas) != len(AuthorityArea):
            raise ValueError(
                "authority_scopes must cover every authority area once"
            )
        for scope in self.authority_scopes:
            if scope.fact_id is not None and scope.fact_id not in fact_ids:
                raise ValueError("authority fact is outside the case")
            if (
                scope.open_question_id is not None
                and scope.open_question_id not in question_ids
            ):
                raise ValueError("authority question is outside the case")

        confirmation_pairs = dict(self.completed_review_fact_ids)
        if len(confirmation_pairs) != len(self.completed_review_fact_ids):
            raise ValueError("completed review ids must be unique")
        for review_id, fact_id in confirmation_pairs.items():
            if review_id not in review_by_id:
                raise ValueError("professional review is outside the case")
            if fact_id not in fact_ids:
                raise ValueError(
                    "professional review confirmation fact is outside the case"
                )
        for review_id, review in review_by_id.items():
            has_confirmation = review_id in confirmation_pairs
            if (
                review.status is ProfessionalReviewStatus.COMPLETED
                and not has_confirmation
            ):
                raise ValueError(
                    "completed professional review requires a verified fact"
                )
            if (
                review.status is not ProfessionalReviewStatus.COMPLETED
                and has_confirmation
            ):
                raise ValueError(
                    "open professional review cannot have completion fact"
                )

        _unique((item.id for item in self.next_actions), "next_action ids")
        allowed_references = (
            question_ids
            | uncertainty_ids
            | set(review_by_id)
            | schedule_ids
        )
        for action in self.next_actions:
            if not set(action.related_reference_ids) <= allowed_references:
                raise ValueError("next action reference is outside the case")
        if self.decision_record_id in {
            item.id for item in self.case.decisions
        }:
            raise ValueError("decision_record_id already exists")


@dataclass(frozen=True)
class PowerOfAttorneyWorkflowResult:
    case_id: str
    workflow_type: str
    workflow_status: PowerOfAttorneyWorkflowStatus
    verified_fact_ids: Tuple[str, ...]
    open_question_ids: Tuple[str, ...]
    uncertainty_ids: Tuple[str, ...]
    professional_review_requirement_ids: Tuple[str, ...]
    decision_record_id: str
    review_schedule_ids: Tuple[str, ...]
    next_action_ids: Tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "workflow_type": self.workflow_type,
            "workflow_status": self.workflow_status.value,
            "verified_fact_ids": list(self.verified_fact_ids),
            "open_question_ids": list(self.open_question_ids),
            "uncertainty_ids": list(self.uncertainty_ids),
            "professional_review_requirement_ids": list(
                self.professional_review_requirement_ids
            ),
            "decision_record_id": self.decision_record_id,
            "review_schedule_ids": list(self.review_schedule_ids),
            "next_action_ids": list(self.next_action_ids),
        }


class PowerOfAttorneyWorkflow:
    WORKFLOW_TYPE = "power_of_attorney_preparation_review"

    def __init__(self, application_service: GoalApplicationService) -> None:
        if not isinstance(application_service, GoalApplicationService):
            raise TypeError(
                "PowerOfAttorneyWorkflow requires GoalApplicationService"
            )
        self.application_service = application_service

    def run(
        self,
        workflow_input: PowerOfAttorneyWorkflowInput,
        goal: Goal,
        role: str,
        memory_types: Iterable[Union[MemoryType, str]],
        constitution_rules: Iterable[str],
        why_assessment: Optional[WhyAssessment],
    ) -> PowerOfAttorneyWorkflowResult:
        if not isinstance(workflow_input, PowerOfAttorneyWorkflowInput):
            raise TypeError(
                "workflow_input must be PowerOfAttorneyWorkflowInput"
            )
        application_result = self.application_service.run(
            goal=goal,
            role=role,
            memory_types=memory_types,
            constitution_rules=constitution_rules,
            why_assessment=why_assessment,
        )
        if application_result["decision"]["status"] != "approved":
            raise PowerOfAttorneyWorkflowError(
                "Life Decisions workflow requires an approved goal decision"
            )

        case = workflow_input.case
        review_status = DecisionReviewStatus.UNREVIEWED
        if case.professional_reviews:
            if all(
                review.status is ProfessionalReviewStatus.COMPLETED
                for review in case.professional_reviews
            ):
                review_status = (
                    DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
                )
            else:
                review_status = DecisionReviewStatus.REVIEW_REQUIRED
        decision = DecisionRecord(
            id=workflow_input.decision_record_id,
            decision=(
                "Structured case overview prepared for organizational "
                "follow-up."
            ),
            rationale=(
                "Confirmed facts, open questions, uncertainties, and "
                "professional review requirements remain separate; no legal "
                "effectiveness is assessed."
            ),
            used_fact_ids=tuple(item.id for item in case.verified_facts),
            open_uncertainty_ids=tuple(
                item.id for item in case.uncertainties
            ),
            professional_review_ids=tuple(
                item.id for item in case.professional_reviews
            ),
            review_status=review_status,
            decided_at=workflow_input.evaluated_at,
            version=workflow_input.decision_version,
        )
        replace(case, decisions=case.decisions + (decision,))

        workflow_status = (
            PowerOfAttorneyWorkflowStatus.NEEDS_CLARIFICATION
            if case.open_questions
            or case.uncertainties
            or any(
                review.status is not ProfessionalReviewStatus.COMPLETED
                for review in case.professional_reviews
            )
            else PowerOfAttorneyWorkflowStatus.STRUCTURED_OVERVIEW_READY
        )
        return PowerOfAttorneyWorkflowResult(
            case_id=case.id,
            workflow_type=self.WORKFLOW_TYPE,
            workflow_status=workflow_status,
            verified_fact_ids=tuple(
                item.id for item in case.verified_facts
            ),
            open_question_ids=tuple(
                item.id for item in case.open_questions
            ),
            uncertainty_ids=tuple(item.id for item in case.uncertainties),
            professional_review_requirement_ids=tuple(
                item.id for item in case.professional_reviews
            ),
            decision_record_id=decision.id,
            review_schedule_ids=tuple(
                item.id for item in case.review_schedules
            ),
            next_action_ids=tuple(
                item.id for item in workflow_input.next_actions
            ),
        )
