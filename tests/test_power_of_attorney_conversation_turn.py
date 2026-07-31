from dataclasses import fields

import pytest

from guardian_understanding.clarification import (
    ClarificationResolution,
    ClarificationResolutionType,
)
from guardian_understanding.models import (
    Contradiction,
    Fact,
    Goal,
    Hypothesis,
    UnderstandingChange,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingRevision,
    UnderstandingState,
    Unknown,
)
from life_decisions.conversation import (
    GuardianLifeDecisionConversationService,
    MissingInformation,
    PowerOfAttorneyConversationInput,
    PowerOfAttorneyConversationStatus,
    UserStatementReference,
)
from life_decisions.conversation_turn import (
    GuardianPowerOfAttorneyConversationService,
    PowerOfAttorneyConversationTurnInput,
    PowerOfAttorneyUnderstandingQuestion,
    understanding_state_content_hash,
)


FACT = Fact("Eine Vorsorgevollmacht soll vorbereitet werden.")
HYPOTHESIS = Hypothesis("Alex könnte als bevollmächtigte Person infrage kommen.")
UNKNOWN_PERSON = Unknown("Die bevollmächtigte Person ist noch offen.")
UNKNOWN_AREAS = Unknown("Die Vertretungsbereiche sind noch offen.")
CONTRADICTION = Contradiction(
    "Eine frühere Vollmacht existiert. <> Eine frühere Vollmacht existiert nicht."
)
GOAL = Goal("Das Gespräch über eine Vorsorgevollmacht vorbereiten.")
STATE = UnderstandingState(
    (FACT,),
    (HYPOTHESIS,),
    (UNKNOWN_PERSON, UNKNOWN_AREAS),
    (CONTRADICTION,),
    (GOAL,),
)
TRIGGER = UserStatementReference(
    "statement-trigger",
    "Ich möchte eine Vorsorgevollmacht besprechen.",
    "conversation:statement-trigger",
)
PERSON_GAP = MissingInformation(
    "missing-information-person",
    "Eine bevollmächtigte Person ist noch nicht benannt.",
    True,
    "understanding:unknown-person",
)
AREA_GAP = MissingInformation(
    "missing-information-areas",
    "Die Vertretungsbereiche sind noch nicht benannt.",
    True,
    "understanding:unknown-areas",
)


def preparation(state=STATE, state_id="understanding-state-001", gaps=(PERSON_GAP,)):
    question = None
    if gaps:
        question = {
            PERSON_GAP.information_id: "Welche Person möchten Sie in Betracht ziehen?",
            AREA_GAP.information_id: "Welche Vertretungsbereiche möchten Sie klären?",
        }[next(item for item in gaps if item.essential).information_id]
    return GuardianLifeDecisionConversationService().prepare(
        PowerOfAttorneyConversationInput(
            understanding_state_id=state_id,
            understanding_state=state,
            triggering_statement_id=TRIGGER.statement_id,
            user_statements=(TRIGGER,),
            facts=state.facts,
            hypotheses=state.hypotheses,
            unknowns=state.unknowns,
            contradictions=state.contradictions,
            goals=state.goals,
            clarification_resolutions=(),
            relevant_people=(),
            representation_areas=(),
            existing_documents=(),
            missing_information=gaps,
            organizational_steps=(),
            professional_reviews=(),
            next_understanding_question=question,
        )
    )


def question(gap=PERSON_GAP, text=None):
    texts = {
        PERSON_GAP.information_id: "Welche Person möchten Sie in Betracht ziehen?",
        AREA_GAP.information_id: "Welche Vertretungsbereiche möchten Sie klären?",
    }
    return PowerOfAttorneyUnderstandingQuestion(
        "understanding-question-{}".format(gap.information_id),
        gap.information_id,
        text or texts[gap.information_id],
        (gap.source_reference,),
    )


def request(**changes):
    values = dict(
        source_understanding_state_id="understanding-state-001",
        source_understanding_state_hash=understanding_state_content_hash(STATE),
        understanding_state=STATE,
        preparation=preparation(),
        question=question(),
    )
    values.update(changes)
    return PowerOfAttorneyConversationTurnInput(**values)


def next_turn(value=None):
    return GuardianPowerOfAttorneyConversationService().next_turn(
        value or request()
    )


def external_lineage(previous):
    answer = UserStatementReference(
        "statement-answer",
        "Alex soll in Betracht gezogen werden.",
        "conversation:statement-answer",
    )
    operation = UnderstandingOperation(
        UnderstandingOperationType.CLOSE_UNKNOWN,
        target_text=UNKNOWN_PERSON.text,
    )
    resolution = ClarificationResolution(
        "clarification-resolution-001",
        "statement-trigger",
        TRIGGER.text,
        previous.question_id,
        previous.understanding_question,
        answer.statement_id,
        answer.text,
        ("understanding-proposal-001",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        answer.source_reference,
        "Ausdrücklich extern ausgewählt.",
        "understanding-proposal-001",
        operation,
        None,
    )
    new_state = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        (UNKNOWN_AREAS,),
        STATE.contradictions,
        STATE.goals,
    )
    revision = UnderstandingRevision(
        new_state,
        (
            UnderstandingChange(
                UnderstandingOperationType.CLOSE_UNKNOWN,
                answer.text,
                UNKNOWN_PERSON.text,
                UNKNOWN_PERSON.text,
            ),
        ),
        "Welche Vertretungsbereiche möchten Sie klären?",
    )
    return answer, resolution, revision, new_state


def test_first_open_essential_gap_produces_one_explicit_question():
    result = next_turn()

    assert result.status is PowerOfAttorneyConversationStatus.NEEDS_CLARIFICATION
    assert result.missing_information_id == PERSON_GAP.information_id
    assert result.understanding_question == question().text
    assert result.understanding_question.count("?") == 1


def test_multiple_gaps_use_first_tuple_entry_without_ranking():
    prepared = preparation(gaps=(PERSON_GAP, AREA_GAP))
    result = next_turn(request(preparation=prepared))

    assert result.missing_information_id == PERSON_GAP.information_id
    assert not hasattr(result, "ranking")
    assert not hasattr(result, "score")
    with pytest.raises(ValueError, match="first essential gap"):
        request(preparation=prepared, question=question(AREA_GAP))


def test_missing_explicit_question_is_rejected_for_an_essential_gap():
    with pytest.raises(ValueError, match="requires a question"):
        request(question=None)


def test_ready_preparation_rejects_an_unrequested_question():
    with pytest.raises(ValueError, match="cannot contain a question"):
        request(preparation=preparation(gaps=()))


def test_question_text_must_match_the_existing_preparation():
    with pytest.raises(ValueError, match="match the preparation question"):
        request(
            question=question(
                text="Welche andere ausdrücklich formulierte Frage gilt?"
            )
        )


def test_tuple_order_not_set_or_hash_order_selects_the_question():
    reversed_preparation = preparation(gaps=(AREA_GAP, PERSON_GAP))
    result = next_turn(
        request(
            preparation=reversed_preparation,
            question=question(AREA_GAP),
        )
    )

    assert result.missing_information_id == AREA_GAP.information_id


def test_identical_input_produces_identical_question_and_stable_turn_id():
    value = request()
    first = next_turn(value)
    second = next_turn(value)

    assert first == second
    assert first.turn_id == second.turn_id


def test_turn_does_not_change_state_or_create_understanding_artifacts():
    before = STATE
    result = next_turn()

    assert STATE is before
    assert result.state_changed_by_turn is False
    assert not hasattr(result, "operation")
    assert not hasattr(result, "revision")
    assert not hasattr(result, "proposal")


def test_answer_without_external_resolution_is_not_interpreted():
    with pytest.raises(ValueError, match="lineage must be complete"):
        request(
            answer_statement=UserStatementReference(
                "statement-answer",
                "Alex.",
                "conversation:statement-answer",
            )
        )


def test_resolution_must_reference_the_previous_question():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    foreign = ClarificationResolution(
        resolution.resolution_id,
        resolution.proposal_statement_id,
        resolution.original_user_statement,
        "understanding-question-foreign",
        resolution.understanding_question,
        resolution.answer_statement_id,
        resolution.answer_text,
        resolution.affected_proposal_ids,
        resolution.resolution_type,
        resolution.source_reference,
        resolution.rationale,
        resolution.selected_proposal_id,
        resolution.selected_operation,
        resolution.next_understanding_question,
    )
    with pytest.raises(ValueError, match="does not answer the previous turn"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=preparation(
                new_state,
                "understanding-state-002",
                (AREA_GAP,),
            ),
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=foreign,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-002",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )


def test_answer_text_must_match_the_external_resolution():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    mismatched = UserStatementReference(
        answer.statement_id,
        "Eine andere Antwort.",
        answer.source_reference,
    )
    with pytest.raises(ValueError, match="does not match resolution"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=preparation(
                new_state,
                "understanding-state-002",
                (AREA_GAP,),
            ),
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=mismatched,
            resolution=resolution,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-002",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )


def test_continuation_consumes_external_resolution_and_revision_then_asks_next_gap():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    prepared = preparation(
        state=new_state,
        state_id="understanding-state-002",
        gaps=(AREA_GAP,),
    )
    result = next_turn(
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=prepared,
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=resolution,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-002",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )
    )

    assert result.missing_information_id == AREA_GAP.information_id
    assert result.answer_statement_id == answer.statement_id
    assert result.resolution_id == resolution.resolution_id
    assert result.revision_reference == "understanding-revision-001"
    assert result.resulting_understanding_state_id == "understanding-state-002"
    assert result.previous_turn_id == previous.turn_id
    assert result.state_changed_by_turn is False


def test_unchanged_open_question_becomes_question_unresolved_without_repetition():
    previous = next_turn()
    result = next_turn(request(previous_turns=(previous,)))

    assert result.status is PowerOfAttorneyConversationStatus.QUESTION_UNRESOLVED
    assert result.question_id == previous.question_id
    assert result.previous_turn_id == previous.turn_id
    assert result.state_changed_by_turn is False


def test_question_unresolved_does_not_create_a_replacement_question():
    previous = next_turn()
    result = next_turn(request(previous_turns=(previous,)))

    assert result.understanding_question == previous.understanding_question
    assert result.question_id == previous.question_id
    assert not hasattr(result, "replacement_question")


def test_non_adjacent_identical_open_question_is_also_unresolved():
    question_a = next_turn()
    turn_b = next_turn(
        request(
            preparation=preparation(gaps=(AREA_GAP,)),
            question=question(AREA_GAP),
            previous_turns=(question_a,),
        )
    )
    repeated_a = next_turn(request(previous_turns=(question_a, turn_b)))

    assert repeated_a.status is PowerOfAttorneyConversationStatus.QUESTION_UNRESOLVED
    assert repeated_a.previous_turn_id == question_a.turn_id
    assert repeated_a.question_id == question_a.question_id


def test_visible_contradiction_does_not_alone_block_ready_status():
    ready = preparation(gaps=())
    result = next_turn(request(preparation=ready, question=None))

    assert result.status is (
        PowerOfAttorneyConversationStatus.CONVERSATION_PREPARATION_READY
    )
    assert result.contradictions == (CONTRADICTION,)
    assert result.understanding_question is None


def test_contradiction_with_essential_gap_still_requires_clarification():
    result = next_turn()

    assert result.contradictions == (CONTRADICTION,)
    assert result.status is PowerOfAttorneyConversationStatus.NEEDS_CLARIFICATION


def test_hypothesis_is_never_presented_as_fact():
    result = next_turn()

    assert result.known_situation == (FACT,)
    assert result.hypotheses == (HYPOTHESIS,)
    assert HYPOTHESIS not in result.known_situation


def test_foreign_question_and_source_state_references_are_rejected():
    with pytest.raises(ValueError, match="missing-information source"):
        request(
            question=PowerOfAttorneyUnderstandingQuestion(
                question().question_id,
                PERSON_GAP.information_id,
                question().text,
                ("foreign:source",),
            )
        )
    with pytest.raises(ValueError, match="does not belong to source state"):
        request(source_understanding_state_id="understanding-state-foreign")


def test_source_state_hash_is_bound_to_actual_state_content():
    assert next_turn().source_understanding_state_hash == (
        understanding_state_content_hash(STATE)
    )
    with pytest.raises(ValueError, match="does not match UnderstandingState"):
        request(source_understanding_state_hash="0" * 64)


def test_previous_turn_from_another_source_state_is_rejected():
    previous = next_turn()
    foreign_preparation = preparation(state_id="understanding-state-002")
    with pytest.raises(ValueError, match="Previous turn does not belong"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(STATE),
            preparation=foreign_preparation,
            previous_turns=(previous,),
        )


def test_inconsistent_resolution_or_revision_references_are_rejected():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    with pytest.raises(ValueError, match="Revision state does not match"):
        request(
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=resolution,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-001",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )
    assert new_state != STATE


def test_revision_must_match_the_selected_external_operation():
    previous = next_turn()
    answer, resolution, _, new_state = external_lineage(previous)
    wrong_revision = UnderstandingRevision(
        new_state,
        (
            UnderstandingChange(
                UnderstandingOperationType.ADD_GOAL,
                answer.text,
                None,
                "Ein anderes Ziel.",
            ),
        ),
        "Welche Vertretungsbereiche möchten Sie klären?",
    )
    with pytest.raises(ValueError, match="does not match selected operation"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=preparation(
                new_state,
                "understanding-state-002",
                (AREA_GAP,),
            ),
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=resolution,
            revision=wrong_revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-002",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )


def test_foreign_operation_target_is_rejected_even_with_same_operation_type():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    foreign_resolution = ClarificationResolution(
        resolution.resolution_id,
        resolution.proposal_statement_id,
        resolution.original_user_statement,
        resolution.question_id,
        resolution.understanding_question,
        resolution.answer_statement_id,
        resolution.answer_text,
        resolution.affected_proposal_ids,
        resolution.resolution_type,
        resolution.source_reference,
        resolution.rationale,
        resolution.selected_proposal_id,
        UnderstandingOperation(
            UnderstandingOperationType.CLOSE_UNKNOWN,
            target_text="Ein fremder offener Punkt.",
        ),
        None,
    )
    with pytest.raises(ValueError, match="outside source state"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=preparation(
                new_state,
                "understanding-state-002",
                (AREA_GAP,),
            ),
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=foreign_resolution,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-002",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )


def test_resulting_state_reference_must_match_the_current_source_state():
    previous = next_turn()
    answer, resolution, revision, new_state = external_lineage(previous)
    with pytest.raises(ValueError, match="Resulting state reference"):
        request(
            source_understanding_state_id="understanding-state-002",
            source_understanding_state_hash=understanding_state_content_hash(new_state),
            understanding_state=new_state,
            preparation=preparation(
                new_state,
                "understanding-state-002",
                (AREA_GAP,),
            ),
            question=question(AREA_GAP),
            previous_turns=(previous,),
            answer_statement=answer,
            resolution=resolution,
            revision=revision,
            revision_reference="understanding-revision-001",
            resulting_understanding_state_id="understanding-state-foreign",
            resulting_understanding_state_hash=understanding_state_content_hash(new_state),
        )


def test_duplicate_previous_turn_references_are_rejected():
    previous = next_turn()
    with pytest.raises(ValueError, match="previous_turns must be unique"):
        request(previous_turns=(previous, previous))


def test_no_hidden_defaults_add_people_areas_steps_or_reviews():
    prepared = preparation()
    result = next_turn(request(preparation=prepared))

    assert prepared.relevant_people == ()
    assert prepared.representation_areas == ()
    assert prepared.organizational_steps == ()
    assert prepared.professional_reviews == ()
    assert not hasattr(result, "recommendations")


def test_service_is_stateless_and_models_expose_no_forbidden_mechanisms():
    service = GuardianPowerOfAttorneyConversationService()
    forbidden = {
        "operation",
        "proposal",
        "routing",
        "workflow",
        "capability",
        "activation",
        "persistence",
        "memory",
        "confidence",
        "score",
        "ranking",
        "priority",
    }

    assert service.__dict__ == {}
    assert forbidden.isdisjoint(
        field.name for field in fields(PowerOfAttorneyConversationTurnInput)
    )
    assert forbidden.isdisjoint(
        field.name for field in fields(type(next_turn()))
    )
