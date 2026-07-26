from dataclasses import FrozenInstanceError, asdict, is_dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Tuple, get_type_hints

import pytest
from typer.testing import CliRunner

import commands.goal as goal_command
from brain.context_collector import ContextCollector
from builder.goal_application_service import GoalApplicationService
from builder.main import app
from builder.preflight import PreflightError
from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from goal.models import Goal
from identity.models import IdentityContext
from life_decisions import (
    AuthorityArea,
    AuthorityCoverageStatus,
    AuthorityScopeAssessment,
    AuthorizedPersonAssessment,
    CaseStatus,
    ConflictStatus,
    DecisionReviewStatus,
    DocumentPresence,
    DocumentReference,
    DocumentType,
    EvidenceStatus,
    FactConfirmationStatus,
    LifeDecisionCase,
    LifeDecisionTopic,
    OpenQuestion,
    OpenQuestionStatus,
    OrganizationalNextAction,
    Participant,
    ParticipantRole,
    PowerOfAttorneyDocumentAssessment,
    PowerOfAttorneyWorkflow,
    PowerOfAttorneyWorkflowInput,
    PowerOfAttorneyWorkflowStatus,
    ProfessionalField,
    ProfessionalReviewRequirement,
    ProfessionalReviewStatus,
    RepresentationMode,
    ReviewSchedule,
    ReviewScheduleStatus,
    Uncertainty,
    UncertaintySeverity,
    VerifiedFact,
)


NOW = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
runner = CliRunner()


class ApprovedApplicationService(GoalApplicationService):
    def __init__(self):
        pass

    def run(self, **kwargs):
        return {
            "decision": {"status": "approved"},
            "plan": [],
            "execution": [],
        }


def fact(identifier):
    return VerifiedFact(
        identifier,
        "Explicitly confirmed case information.",
        "user-confirmed-input",
        FactConfirmationStatus.USER_CONFIRMED,
        NOW,
    )


def question(identifier):
    return OpenQuestion(
        identifier,
        "Which information still needs clarification?",
        "participant-owner",
        OpenQuestionStatus.OPEN,
        "Obtain an explicit answer from the responsible person.",
    )


def uncertainty(identifier):
    return Uncertainty(
        identifier,
        "A relevant detail remains uncertain.",
        UncertaintySeverity.MEDIUM,
        "No confirmed information is available.",
        "The case overview may remain incomplete.",
    )


def complete_input(
    *,
    questions=(),
    uncertainties=(),
    document_presence=DocumentPresence.PRESENT,
    document_reference_id="document-poa",
    document_question_ids=(),
    document_uncertainty_ids=(),
    willingness=EvidenceStatus.CONFIRMED,
    willingness_fact_id="fact-willingness",
    willingness_question_id=None,
    conflict_status=ConflictStatus.NONE_CONFIRMED,
    conflict_fact_id="fact-conflict-none",
    conflict_uncertainty_id=None,
    review_status=ProfessionalReviewStatus.COMPLETED,
):
    authority_facts = tuple(
        fact("fact-area-{}".format(area.value))
        for area in AuthorityArea
    )
    base_facts = (
        fact("fact-document"),
        fact("fact-issued"),
        fact("fact-reviewed"),
        fact("fact-willingness"),
        fact("fact-conflict-none"),
        fact("fact-review-complete"),
    ) + authority_facts
    documents = (
        (
            DocumentReference(
                "document-poa",
                DocumentType.POWER_OF_ATTORNEY,
                "user-storage://documents/poa-1",
                False,
            ),
        )
        if document_presence is DocumentPresence.PRESENT
        else ()
    )
    review = ProfessionalReviewRequirement(
        "review-legal",
        ProfessionalField.LEGAL,
        "User requested an independent professional review.",
        review_status,
    )
    case = LifeDecisionCase(
        id="case-poa",
        title="Power of attorney preparation",
        topic=LifeDecisionTopic.POWER_OF_ATTORNEY,
        status=CaseStatus.ACTIVE,
        owner="participant-owner",
        created_at=NOW,
        updated_at=NOW,
        participants=(
            Participant(
                "participant-owner",
                "Affected person",
                ParticipantRole.CASE_OWNER,
            ),
            Participant(
                "participant-agent",
                "Authorized person",
                ParticipantRole.TRUSTED_CONTACT,
            ),
        ),
        document_references=documents,
        verified_facts=base_facts,
        open_questions=questions,
        uncertainties=uncertainties,
        professional_reviews=(review,),
        review_schedules=(
            ReviewSchedule(
                "schedule-annual",
                NOW,
                "Annual organizational review",
                ReviewScheduleStatus.SCHEDULED,
            ),
        ),
    )
    document = PowerOfAttorneyDocumentAssessment(
        presence=document_presence,
        presence_fact_id=(
            None
            if document_presence is DocumentPresence.UNKNOWN
            else "fact-document"
        ),
        document_reference_id=document_reference_id,
        issued_at=NOW if document_presence is DocumentPresence.PRESENT else None,
        issued_at_fact_id=(
            "fact-issued"
            if document_presence is DocumentPresence.PRESENT
            else None
        ),
        last_reviewed_at=(
            NOW if document_presence is DocumentPresence.PRESENT else None
        ),
        last_reviewed_fact_id=(
            "fact-reviewed"
            if document_presence is DocumentPresence.PRESENT
            else None
        ),
        open_question_ids=document_question_ids,
        uncertainty_ids=document_uncertainty_ids,
    )
    persons = (
        AuthorizedPersonAssessment(
            "appointment-primary",
            "participant-agent",
            1,
            RepresentationMode.INDIVIDUAL,
            None,
            willingness,
            willingness_fact_id,
            willingness_question_id,
            conflict_status,
            conflict_fact_id,
            conflict_uncertainty_id,
        ),
    )
    scopes = tuple(
        AuthorityScopeAssessment(
            "scope-{}".format(area.value),
            area,
            AuthorityCoverageStatus.CONFIRMED_INCLUDED,
            "fact-area-{}".format(area.value),
            None,
        )
        for area in AuthorityArea
    )
    return PowerOfAttorneyWorkflowInput(
        case=case,
        document=document,
        authorized_persons=persons,
        authority_scopes=scopes,
        completed_review_fact_ids=(
            (("review-legal", "fact-review-complete"),)
            if review_status is ProfessionalReviewStatus.COMPLETED
            else ()
        ),
        next_actions=(
            OrganizationalNextAction(
                "action-review",
                "Attend the explicitly requested professional review.",
                ("review-legal", "schedule-annual"),
            ),
        ),
        decision_record_id="decision-poa-overview",
        evaluated_at=NOW,
        decision_version="1",
    )


def run(workflow_input):
    workflow = PowerOfAttorneyWorkflow(ApprovedApplicationService())
    return workflow.run(
        workflow_input,
        Goal(
            "goal-poa",
            "Prepare power of attorney overview",
            "Create a structured organizational overview.",
            "zonvaa-builder",
            "high",
            "active",
            "architect",
            NOW,
        ),
        "architect",
        ("project_memory",),
        ("No legal advice",),
        None,
    )


def test_complete_case_returns_stable_machine_readable_overview():
    result = run(complete_input())
    assert result.workflow_status is (
        PowerOfAttorneyWorkflowStatus.STRUCTURED_OVERVIEW_READY
    )
    assert result.case_id == "case-poa"
    assert result.decision_record_id == "decision-poa-overview"
    assert result.review_schedule_ids == ("schedule-annual",)
    assert result.next_action_ids == ("action-review",)


def test_missing_power_of_attorney_is_visible_as_question():
    result = run(
        complete_input(
            questions=(question("question-document"),),
            document_presence=DocumentPresence.ABSENT,
            document_reference_id=None,
            document_question_ids=("question-document",),
        )
    )
    assert result.workflow_status is (
        PowerOfAttorneyWorkflowStatus.NEEDS_CLARIFICATION
    )
    assert result.open_question_ids == ("question-document",)


def test_present_but_unreviewed_document_remains_uncertain():
    workflow_input = complete_input(
        questions=(question("question-review-date"),),
        uncertainties=(uncertainty("uncertainty-currentness"),),
        document_question_ids=("question-review-date",),
        document_uncertainty_ids=("uncertainty-currentness",),
    )
    workflow_input = replace(
        workflow_input,
        document=replace(
            workflow_input.document,
            last_reviewed_at=None,
            last_reviewed_fact_id=None,
        ),
    )
    result = run(workflow_input)
    assert "uncertainty-currentness" in result.uncertainty_ids
    assert result.workflow_status.value == "needs_clarification"


def test_unknown_willingness_requires_explicit_question():
    result = run(
        complete_input(
            questions=(question("question-willingness"),),
            willingness=EvidenceStatus.UNKNOWN,
            willingness_fact_id=None,
            willingness_question_id="question-willingness",
        )
    )
    assert result.open_question_ids == ("question-willingness",)


def test_possible_conflict_remains_an_uncertainty():
    result = run(
        complete_input(
            uncertainties=(uncertainty("uncertainty-conflict"),),
            conflict_status=ConflictStatus.POSSIBLE,
            conflict_fact_id=None,
            conflict_uncertainty_id="uncertainty-conflict",
        )
    )
    assert result.uncertainty_ids == ("uncertainty-conflict",)


def test_present_document_requires_case_document_reference():
    with pytest.raises(
        ValueError,
        match="present document requires",
    ):
        complete_input(document_reference_id=None)

    with pytest.raises(ValueError, match="outside the case"):
        complete_input(document_reference_id="foreign-document")


def test_foreign_fact_question_and_review_ids_are_rejected():
    workflow_input = complete_input()
    bad_scope = replace(
        workflow_input.authority_scopes[0],
        fact_id="foreign-fact",
    )
    with pytest.raises(ValueError, match="authority fact"):
        replace(
            workflow_input,
            authority_scopes=(
                bad_scope,
            ) + workflow_input.authority_scopes[1:],
        )


def test_duplicate_workflow_ids_are_rejected():
    workflow_input = complete_input()
    duplicate = replace(
        workflow_input.authorized_persons[0],
        participant_id="participant-owner",
    )
    with pytest.raises(ValueError, match="authorized_person ids"):
        replace(
            workflow_input,
            authorized_persons=(
                workflow_input.authorized_persons[0],
                duplicate,
            ),
        )


def test_completed_review_does_not_hide_open_uncertainty():
    result = run(
        complete_input(
            uncertainties=(uncertainty("uncertainty-scope"),),
        )
    )
    assert result.workflow_status.value == "needs_clarification"
    assert result.uncertainty_ids == ("uncertainty-scope",)


def test_output_contains_no_legal_effectiveness_claim_or_document_content():
    output = run(complete_input()).to_dict()
    serialized = json.dumps(output)
    assert "content" not in serialized
    assert "storage_reference" not in serialized
    assert "effective" not in serialized
    assert set(output) == {
        "case_id",
        "workflow_type",
        "workflow_status",
        "verified_fact_ids",
        "open_question_ids",
        "uncertainty_ids",
        "professional_review_requirement_ids",
        "decision_record_id",
        "review_schedule_ids",
        "next_action_ids",
    }


def test_output_is_deterministic_and_result_is_immutable():
    workflow_input = complete_input()
    first = run(workflow_input)
    second = run(workflow_input)
    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.case_id = "changed"


def test_input_is_immutable():
    workflow_input = complete_input()
    with pytest.raises(FrozenInstanceError):
        workflow_input.decision_record_id = "changed"


def test_python_39_typing_uses_tuple():
    hints = get_type_hints(PowerOfAttorneyWorkflowInput)
    assert hints["authority_scopes"] == Tuple[AuthorityScopeAssessment, ...]


def test_workflow_cannot_be_constructed_without_mission_context():
    runtime = RuntimeManager()
    runtime.identity_context = IdentityContext(
        content="# WHY",
        source=Path(__file__),
        version="identity-version",
    )
    runtime.goal_engine = GoalEngine()
    with pytest.raises(PreflightError, match="MissionContext"):
        GoalApplicationService(runtime)


def _json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if is_dataclass(value):
        return {
            key: _json_value(item)
            for key, item in asdict(value).items()
        }
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _json_value(item)
            for key, item in value.items()
        }
    return value


def test_existing_goal_cli_runs_power_of_attorney_workflow(
    tmp_path,
    monkeypatch,
):
    domain_input = complete_input()
    workflow_json = _json_value(domain_input)
    workflow_json["completed_review_fact_ids"] = [
        {"review_id": review_id, "fact_id": fact_id}
        for review_id, fact_id in domain_input.completed_review_fact_ids
    ]
    runtime = RuntimeManager()
    runtime.identity_context = IdentityContext(
        content="# WHY",
        source=tmp_path / "WHY.md",
        version="identity-version",
    )
    runtime.constitution = "# Constitution\n\nVersion: 1.0"
    runtime.knowledge = {
        "adr": [],
        "protocols": [],
        "handovers": [],
        "project": [],
        "sessions": [],
        "sources": [],
        "verified_facts": {},
    }
    runtime.latest_context = None
    runtime.verified_facts = {}
    runtime.project_state = {
        "python_version": "3.9.6",
        "pytest_version": "8.4.2",
        "git_branch": "main",
        "git_commit": "e627b4f",
        "git_clean": True,
        "verified_facts": {},
    }
    runtime.goal_engine = GoalEngine()
    monkeypatch.setattr(goal_command, "get_runtime", lambda: runtime)

    def clean_git(self, command):
        if command[:2] == ["git", "status"]:
            return "Keine Ausgabe."
        if command[:2] == ["git", "log"]:
            return "e627b4f Deployment"
        raise AssertionError("Unexpected command")

    monkeypatch.setattr(ContextCollector, "_run_command", clean_git)
    payload = {
        "goal": {
            "id": "goal-poa",
            "title": "Prepare power of attorney overview",
            "description": "Create a structured organizational overview.",
            "project": "zonvaa-builder",
            "priority": "high",
            "status": "active",
            "owner": "architect",
            "created_at": NOW.isoformat(),
        },
        "role": "architect",
        "memory_types": ["project_memory"],
        "constitution_rules": ["No legal advice"],
        "why_assessment": {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": [],
        },
        "life_decisions_workflow": {
            "workflow_type": (
                "power_of_attorney_preparation_review"
            ),
            "input": workflow_json,
        },
    }
    input_file = tmp_path / "goal.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    result = runner.invoke(
        app,
        ["goal", "run", "--input", str(input_file)],
    )

    assert result.exit_code == 0, result.output
    output = json.loads(result.stdout)
    assert output["case_id"] == "case-poa"
    assert output["workflow_type"] == (
        "power_of_attorney_preparation_review"
    )
    assert "storage_reference" not in result.stdout
    assert "Affected person" not in result.stdout
