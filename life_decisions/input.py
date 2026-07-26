from datetime import datetime
from typing import Any, Dict, Tuple

from life_decisions.models import (
    CaseStatus,
    DocumentReference,
    DocumentType,
    FactConfirmationStatus,
    LifeDecisionCase,
    LifeDecisionTopic,
    OpenQuestion,
    OpenQuestionStatus,
    Participant,
    ParticipantRole,
    ProfessionalField,
    ProfessionalReviewRequirement,
    ProfessionalReviewStatus,
    ReviewSchedule,
    ReviewScheduleStatus,
    Uncertainty,
    UncertaintySeverity,
    VerifiedFact,
)
from life_decisions.power_of_attorney import (
    AuthorityArea,
    AuthorityCoverageStatus,
    AuthorityScopeAssessment,
    AuthorizedPersonAssessment,
    ConflictStatus,
    DocumentPresence,
    EvidenceStatus,
    OrganizationalNextAction,
    PowerOfAttorneyDocumentAssessment,
    PowerOfAttorneyWorkflowInput,
    RepresentationMode,
)


def _mapping(value: Any, field: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("{} must be an object".format(field))
    return value


def _list(value: Any, field: str) -> list:
    if not isinstance(value, list):
        raise TypeError("{} must be a list".format(field))
    return value


def _required(value: Dict[str, Any], field: str) -> Any:
    if field not in value:
        raise ValueError("{} is required".format(field))
    return value[field]


def _string(value: Dict[str, Any], field: str) -> str:
    result = _required(value, field)
    if not isinstance(result, str):
        raise TypeError("{} must be a string".format(field))
    return result


def _optional_string(value: Dict[str, Any], field: str):
    result = value.get(field)
    if result is not None and not isinstance(result, str):
        raise TypeError("{} must be a string or null".format(field))
    return result


def _datetime(value: str, field: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ValueError("{} must be ISO-8601".format(field)) from error


def _optional_datetime(value: Dict[str, Any], field: str):
    result = value.get(field)
    return None if result is None else _datetime(result, field)


def _string_tuple(value: Dict[str, Any], field: str) -> Tuple[str, ...]:
    items = _list(_required(value, field), field)
    if not all(isinstance(item, str) for item in items):
        raise TypeError("{} must contain strings".format(field))
    return tuple(items)


def parse_power_of_attorney_input(
    value: Dict[str, Any],
) -> PowerOfAttorneyWorkflowInput:
    data = _mapping(value, "life_decisions_workflow.input")
    case_data = _mapping(_required(data, "case"), "case")
    participants = tuple(
        Participant(
            id=_string(item, "id"),
            label=_string(item, "label"),
            role=ParticipantRole(_string(item, "role")),
        )
        for item in (
            _mapping(entry, "participant")
            for entry in _list(
                _required(case_data, "participants"),
                "participants",
            )
        )
    )
    documents = tuple(
        DocumentReference(
            id=_string(item, "id"),
            document_type=DocumentType(_string(item, "document_type")),
            storage_reference=_string(item, "storage_reference"),
            analysis_authorized=_required(item, "analysis_authorized"),
        )
        for item in (
            _mapping(entry, "document_reference")
            for entry in _list(
                _required(case_data, "document_references"),
                "document_references",
            )
        )
    )
    facts = tuple(
        VerifiedFact(
            id=_string(item, "id"),
            statement=_string(item, "statement"),
            source=_string(item, "source"),
            confirmation_status=FactConfirmationStatus(
                _string(item, "confirmation_status")
            ),
            confirmed_at=_datetime(
                _string(item, "confirmed_at"),
                "confirmed_at",
            ),
        )
        for item in (
            _mapping(entry, "verified_fact")
            for entry in _list(
                _required(case_data, "verified_facts"),
                "verified_facts",
            )
        )
    )
    questions = tuple(
        OpenQuestion(
            id=_string(item, "id"),
            question=_string(item, "question"),
            responsible=_string(item, "responsible"),
            status=OpenQuestionStatus(_string(item, "status")),
            required_clarification=_string(
                item,
                "required_clarification",
            ),
        )
        for item in (
            _mapping(entry, "open_question")
            for entry in _list(
                _required(case_data, "open_questions"),
                "open_questions",
            )
        )
    )
    uncertainties = tuple(
        Uncertainty(
            id=_string(item, "id"),
            description=_string(item, "description"),
            severity=UncertaintySeverity(_string(item, "severity")),
            cause=_string(item, "cause"),
            possible_impact=_string(item, "possible_impact"),
        )
        for item in (
            _mapping(entry, "uncertainty")
            for entry in _list(
                _required(case_data, "uncertainties"),
                "uncertainties",
            )
        )
    )
    reviews = tuple(
        ProfessionalReviewRequirement(
            id=_string(item, "id"),
            field=ProfessionalField(_string(item, "field")),
            reason=_string(item, "reason"),
            status=ProfessionalReviewStatus(_string(item, "status")),
        )
        for item in (
            _mapping(entry, "professional_review")
            for entry in _list(
                _required(case_data, "professional_reviews"),
                "professional_reviews",
            )
        )
    )
    schedules = tuple(
        ReviewSchedule(
            id=_string(item, "id"),
            next_review_at=_datetime(
                _string(item, "next_review_at"),
                "next_review_at",
            ),
            trigger=_string(item, "trigger"),
            status=ReviewScheduleStatus(_string(item, "status")),
        )
        for item in (
            _mapping(entry, "review_schedule")
            for entry in _list(
                _required(case_data, "review_schedules"),
                "review_schedules",
            )
        )
    )
    case = LifeDecisionCase(
        id=_string(case_data, "id"),
        title=_string(case_data, "title"),
        topic=LifeDecisionTopic(_string(case_data, "topic")),
        status=CaseStatus(_string(case_data, "status")),
        owner=_string(case_data, "owner"),
        created_at=_datetime(
            _string(case_data, "created_at"),
            "created_at",
        ),
        updated_at=_datetime(
            _string(case_data, "updated_at"),
            "updated_at",
        ),
        participants=participants,
        document_references=documents,
        verified_facts=facts,
        open_questions=questions,
        uncertainties=uncertainties,
        professional_reviews=reviews,
        review_schedules=schedules,
    )

    document_data = _mapping(_required(data, "document"), "document")
    document = PowerOfAttorneyDocumentAssessment(
        presence=DocumentPresence(_string(document_data, "presence")),
        presence_fact_id=_optional_string(
            document_data,
            "presence_fact_id",
        ),
        document_reference_id=_optional_string(
            document_data,
            "document_reference_id",
        ),
        issued_at=_optional_datetime(document_data, "issued_at"),
        issued_at_fact_id=_optional_string(
            document_data,
            "issued_at_fact_id",
        ),
        last_reviewed_at=_optional_datetime(
            document_data,
            "last_reviewed_at",
        ),
        last_reviewed_fact_id=_optional_string(
            document_data,
            "last_reviewed_fact_id",
        ),
        open_question_ids=_string_tuple(
            document_data,
            "open_question_ids",
        ),
        uncertainty_ids=_string_tuple(
            document_data,
            "uncertainty_ids",
        ),
    )
    persons = tuple(
        AuthorizedPersonAssessment(
            id=_string(item, "id"),
            participant_id=_string(item, "participant_id"),
            order=_required(item, "order"),
            representation_mode=RepresentationMode(
                _string(item, "representation_mode")
            ),
            substitute_for_id=_optional_string(item, "substitute_for_id"),
            willingness=EvidenceStatus(_string(item, "willingness")),
            willingness_fact_id=_optional_string(
                item,
                "willingness_fact_id",
            ),
            willingness_question_id=_optional_string(
                item,
                "willingness_question_id",
            ),
            conflict_status=ConflictStatus(
                _string(item, "conflict_status")
            ),
            conflict_fact_id=_optional_string(item, "conflict_fact_id"),
            conflict_uncertainty_id=_optional_string(
                item,
                "conflict_uncertainty_id",
            ),
        )
        for item in (
            _mapping(entry, "authorized_person")
            for entry in _list(
                _required(data, "authorized_persons"),
                "authorized_persons",
            )
        )
    )
    scopes = tuple(
        AuthorityScopeAssessment(
            id=_string(item, "id"),
            area=AuthorityArea(_string(item, "area")),
            status=AuthorityCoverageStatus(_string(item, "status")),
            fact_id=_optional_string(item, "fact_id"),
            open_question_id=_optional_string(
                item,
                "open_question_id",
            ),
        )
        for item in (
            _mapping(entry, "authority_scope")
            for entry in _list(
                _required(data, "authority_scopes"),
                "authority_scopes",
            )
        )
    )
    actions = tuple(
        OrganizationalNextAction(
            id=_string(item, "id"),
            description=_string(item, "description"),
            related_reference_ids=_string_tuple(
                item,
                "related_reference_ids",
            ),
        )
        for item in (
            _mapping(entry, "next_action")
            for entry in _list(
                _required(data, "next_actions"),
                "next_actions",
            )
        )
    )
    completed_pairs = tuple(
        (
            _string(item, "review_id"),
            _string(item, "fact_id"),
        )
        for item in (
            _mapping(entry, "completed_review_fact")
            for entry in _list(
                _required(data, "completed_review_fact_ids"),
                "completed_review_fact_ids",
            )
        )
    )
    return PowerOfAttorneyWorkflowInput(
        case=case,
        document=document,
        authorized_persons=persons,
        authority_scopes=scopes,
        completed_review_fact_ids=completed_pairs,
        next_actions=actions,
        decision_record_id=_string(data, "decision_record_id"),
        evaluated_at=_datetime(
            _string(data, "evaluated_at"),
            "evaluated_at",
        ),
        decision_version=_string(data, "decision_version"),
    )
