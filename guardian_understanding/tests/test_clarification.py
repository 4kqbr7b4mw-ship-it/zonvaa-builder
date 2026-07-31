from dataclasses import fields

import pytest

from guardian_understanding import (
    ClarificationResolutionRequest,
    ClarificationResolutionType,
    Contradiction,
    Fact,
    Goal,
    GuardianClarificationResolutionService,
    GuardianUnderstandingProposalService,
    Hypothesis,
    ProposalDispositionType,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingProposalCandidate,
    UnderstandingState,
    Unknown,
)


STATE = UnderstandingState(
    facts=(Fact("Der Termin ist offen."),),
    hypotheses=(Hypothesis("Der Freitag könnte passen."),),
    unknowns=(Unknown("Welcher Tag passt?"),),
    contradictions=(),
    goals=(Goal("Einen Termin verstehen."),),
)
QUESTION = "Meinen Sie Freitag oder Samstag?"


def candidate(value):
    return UnderstandingProposalCandidate(
        operation=UnderstandingOperation(
            UnderstandingOperationType.ADD_FACT,
            value_text=value,
        ),
        source_reference="conversation:statement-001",
        rationale="Eine ausdrücklich vorbereitete mögliche Einordnung.",
    )


def proposal_set(statement_id="statement-001", statement="Freitag oder Samstag."):
    return GuardianUnderstandingProposalService().create(
        STATE,
        statement_id,
        statement,
        (candidate("Der Termin ist Freitag."), candidate("Der Termin ist Samstag.")),
        QUESTION,
    )


def request(
    proposals,
    resolution_type,
    affected=None,
    selected=None,
    next_question=None,
):
    affected_ids = affected or tuple(
        proposal.proposal_id for proposal in proposals.proposals
    )
    return ClarificationResolutionRequest(
        question_id=proposals.understanding_question_id,
        answer_statement_id="statement-answer-001",
        answer_text="Ich meinte Freitag.",
        affected_proposal_ids=affected_ids,
        resolution_type=resolution_type,
        source_reference="conversation:statement-answer-001",
        rationale="Die Nutzerantwort wurde ausdrücklich typisiert aufgelöst.",
        selected_proposal_id=selected,
        next_understanding_question=next_question,
    )


def resolve(proposals, resolution_request):
    return GuardianClarificationResolutionService().resolve(
        STATE,
        proposals,
        resolution_request,
    )


def test_selects_one_valid_proposal_through_existing_application():
    proposals = proposal_set()
    selected = proposals.proposals[0]

    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )

    assert result.application is not None
    assert result.application.selected_proposal is selected
    assert result.application.revision.state.facts[-1] == Fact(
        "Der Termin ist Freitag."
    )
    assert result.proposal_dispositions[0].disposition is (
        ProposalDispositionType.SELECTED
    )
    assert result.proposal_dispositions[1].disposition is ProposalDispositionType.OPEN


def test_unknown_proposal_id_is_rejected():
    proposals = proposal_set()
    unknown = "understanding-proposal-unknown"

    with pytest.raises(ValueError, match="does not belong"):
        resolve(
            proposals,
            request(
                proposals,
                ClarificationResolutionType.SELECT_PROPOSAL,
                affected=(unknown,),
                selected=unknown,
            ),
        )


def test_proposal_from_another_set_cannot_be_selected():
    proposals = proposal_set()
    other = proposal_set("statement-002", "Ein anderer Satz.")
    foreign = other.proposals[0].proposal_id

    with pytest.raises(ValueError, match="does not belong"):
        resolve(
            proposals,
            request(
                proposals,
                ClarificationResolutionType.SELECT_PROPOSAL,
                affected=(foreign,),
                selected=foreign,
            ),
        )


def test_selected_understanding_operation_is_not_rewritten():
    proposals = proposal_set()
    selected = proposals.proposals[0]

    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )

    assert result.resolution.selected_operation is selected.operation
    assert result.application.selected_proposal.operation is selected.operation
    assert result.application.revision.changes[0].operation is (
        selected.operation.operation
    )


def test_selection_delegates_to_existing_proposal_service_once():
    proposals = proposal_set()
    selected = proposals.proposals[0]

    class RecordingProposalService(GuardianUnderstandingProposalService):
        def __init__(self):
            super().__init__()
            self.calls = []

        def apply(self, existing, selected_set, selection):
            self.calls.append((existing, selected_set, selection))
            return super().apply(existing, selected_set, selection)

    proposal_service = RecordingProposalService()
    service = GuardianClarificationResolutionService(proposal_service)
    result = service.resolve(
        STATE,
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )

    assert len(proposal_service.calls) == 1
    assert proposal_service.calls[0][2].proposal_id == selected.proposal_id
    assert result.application is not None


def test_rejects_one_proposal_without_revision_and_keeps_other_open():
    proposals = proposal_set()
    rejected = proposals.proposals[0]

    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.REJECT_PROPOSALS,
            affected=(rejected.proposal_id,),
        ),
    )

    assert result.application is None
    assert result.proposal_dispositions[0].disposition is ProposalDispositionType.REJECTED
    assert result.proposal_dispositions[1].disposition is ProposalDispositionType.OPEN
    assert STATE.facts == (Fact("Der Termin ist offen."),)


def test_rejects_multiple_alternatives_without_applying_them():
    proposals = proposal_set()

    result = resolve(
        proposals,
        request(proposals, ClarificationResolutionType.REJECT_PROPOSALS),
    )

    assert result.application is None
    assert tuple(item.disposition for item in result.proposal_dispositions) == (
        ProposalDispositionType.REJECTED,
        ProposalDispositionType.REJECTED,
    )


def test_rejected_proposal_needs_a_new_explicit_resolution_to_be_selected():
    proposals = proposal_set()
    selected = proposals.proposals[0]
    rejected = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.REJECT_PROPOSALS,
            affected=(selected.proposal_id,),
        ),
    )

    assert rejected.application is None
    later_selection = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )
    assert later_selection.application is not None
    assert (
        later_selection.resolution.resolution_id
        != rejected.resolution.resolution_id
    )


def test_keep_open_requires_exactly_one_next_question_and_changes_no_state():
    proposals = proposal_set()
    follow_up = "Welcher der beiden Tage war gemeint?"

    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.KEEP_OPEN,
            next_question=follow_up,
        ),
    )

    assert result.application is None
    assert result.resolution.next_understanding_question == follow_up
    assert result.resolution.next_understanding_question.count("?") == 1
    assert all(
        item.disposition is ProposalDispositionType.OPEN
        for item in result.proposal_dispositions
    )
    assert STATE == UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        STATE.unknowns,
        STATE.contradictions,
        STATE.goals,
    )


@pytest.mark.parametrize(
    "next_question",
    [None, "Ist es Freitag? Oder Samstag?"],
)
def test_keep_open_rejects_missing_or_multiple_questions(next_question):
    proposals = proposal_set()
    with pytest.raises(ValueError, match="question"):
        request(
            proposals,
            ClarificationResolutionType.KEEP_OPEN,
            next_question=next_question,
        )


def test_close_without_change_closes_all_proposals_and_runs_no_operation():
    proposals = proposal_set()

    result = resolve(
        proposals,
        request(proposals, ClarificationResolutionType.CLOSE_WITHOUT_CHANGE),
    )

    assert result.application is None
    assert result.resolution.selected_operation is None
    assert all(
        item.disposition is ProposalDispositionType.CLOSED_WITHOUT_CHANGE
        for item in result.proposal_dispositions
    )
    assert "ausdrücklich typisiert" in result.resolution.rationale


def test_user_answer_and_non_selection_resolution_do_not_create_revision():
    proposals = proposal_set()
    clarification = request(
        proposals,
        ClarificationResolutionType.KEEP_OPEN,
        next_question="Welchen Tag meinen Sie?",
    )

    assert not hasattr(clarification, "revision")
    result = resolve(proposals, clarification)
    assert result.application is None
    assert not hasattr(result.resolution, "revision")


def test_complete_source_chain_and_original_question_are_preserved():
    proposals = proposal_set()
    selected = proposals.proposals[0]

    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )
    resolution = result.resolution

    assert resolution.proposal_statement_id == proposals.statement_id
    assert resolution.original_user_statement == proposals.user_statement
    assert resolution.question_id == proposals.understanding_question_id
    assert resolution.understanding_question == QUESTION
    assert resolution.answer_statement_id == "statement-answer-001"
    assert resolution.answer_text == "Ich meinte Freitag."
    assert resolution.source_reference == "conversation:statement-answer-001"
    assert resolution.affected_proposal_ids == (selected.proposal_id,)
    assert resolution.selected_proposal_id == selected.proposal_id
    assert resolution.selected_operation is selected.operation


def test_resolution_question_must_belong_to_proposal_set():
    proposals = proposal_set()
    other = proposal_set("statement-002", "Ein anderer Satz.")
    resolution_request = ClarificationResolutionRequest(
        question_id=other.understanding_question_id,
        answer_statement_id="statement-answer-001",
        answer_text="Ich meinte Freitag.",
        affected_proposal_ids=(proposals.proposals[0].proposal_id,),
        resolution_type=ClarificationResolutionType.SELECT_PROPOSAL,
        source_reference="conversation:statement-answer-001",
        rationale="Explizite Auswahl.",
        selected_proposal_id=proposals.proposals[0].proposal_id,
    )

    with pytest.raises(ValueError, match="Question does not belong"):
        resolve(proposals, resolution_request)


def test_non_selection_adds_no_understanding_items():
    proposals = proposal_set()
    before = STATE

    result = resolve(
        proposals,
        request(proposals, ClarificationResolutionType.REJECT_PROPOSALS),
    )

    assert result.application is None
    assert STATE is before
    assert STATE.facts == before.facts
    assert STATE.hypotheses == before.hypotheses
    assert STATE.unknowns == before.unknowns
    assert STATE.goals == before.goals
    assert STATE.contradictions == before.contradictions


def test_existing_contradictions_remain_visible_after_explicit_selection():
    state = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        STATE.unknowns,
        (Contradiction("Freitag <> Samstag"),),
        STATE.goals,
    )
    proposals = proposal_set()
    selected = proposals.proposals[0]
    result = GuardianClarificationResolutionService().resolve(
        state,
        proposals,
        request(
            proposals,
            ClarificationResolutionType.SELECT_PROPOSAL,
            affected=(selected.proposal_id,),
            selected=selected.proposal_id,
        ),
    )

    assert result.application.revision.state.contradictions == (
        Contradiction("Freitag <> Samstag"),
    )


def test_resolution_contract_has_no_confidence_routing_decision_or_activation():
    proposals = proposal_set()
    result = resolve(
        proposals,
        request(
            proposals,
            ClarificationResolutionType.KEEP_OPEN,
            next_question="Welchen Tag meinen Sie?",
        ),
    )
    forbidden = {
        "confidence",
        "score",
        "probability",
        "rank",
        "routing",
        "decision",
        "workflow",
        "capability",
        "activation",
    }

    assert forbidden.isdisjoint(
        field.name for field in fields(type(result.resolution))
    )
    assert forbidden.isdisjoint(vars(result.resolution))


def test_identical_typed_input_is_deterministic():
    proposals = proposal_set()
    resolution_request = request(
        proposals,
        ClarificationResolutionType.KEEP_OPEN,
        next_question="Welchen Tag meinen Sie?",
    )
    service = GuardianClarificationResolutionService()

    first = service.resolve(STATE, proposals, resolution_request)
    second = service.resolve(STATE, proposals, resolution_request)

    assert first == second
    assert first.resolution.resolution_id == second.resolution.resolution_id
