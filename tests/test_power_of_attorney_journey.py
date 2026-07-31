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
    MissingInformation,
    PowerOfAttorneyConversationInput,
    UserStatementReference,
)
from life_decisions.conversation_turn import understanding_state_content_hash
from life_decisions.journey import (
    ControlledPowerOfAttorneyQuestion,
    GuardianPowerOfAttorneyJourneyService,
    PowerOfAttorneyExternalClarification,
    PowerOfAttorneyGapBinding,
    PowerOfAttorneyGapType,
    PowerOfAttorneyJourneyAction,
    PowerOfAttorneyJourneyInput,
    PowerOfAttorneyJourneyStatus,
    PowerOfAttorneyQuestionCatalog,
)


FACT = Fact("Eine Vorsorgevollmacht soll vorbereitet werden.")
HYPOTHESIS = Hypothesis("Alex könnte als bevollmächtigte Person infrage kommen.")
UNKNOWN_PERSON = Unknown("Die bevollmächtigte Person ist noch offen.")
UNKNOWN_AREA = Unknown("Die Vertretungsbereiche sind noch offen.")
CONTRADICTION = Contradiction(
    "Eine Vollmacht existiert. <> Eine Vollmacht existiert nicht."
)
GOAL = Goal("Ein Fachgespräch sachlich vorbereiten.")
STATE = UnderstandingState(
    (FACT,),
    (HYPOTHESIS,),
    (UNKNOWN_PERSON, UNKNOWN_AREA),
    (CONTRADICTION,),
    (GOAL,),
)
TRIGGER = UserStatementReference(
    "statement-journey-start",
    "Ich möchte meine Vorsorgevollmacht vorbereiten.",
    "conversation:statement-journey-start",
)
PERSON_GAP = MissingInformation(
    "missing-information-person",
    "Eine mögliche bevollmächtigte Person ist noch offen.",
    True,
    "understanding:unknown-person",
)
AREA_GAP = MissingInformation(
    "missing-information-areas",
    "Die Vertretungsbereiche sind noch offen.",
    True,
    "understanding:unknown-areas",
)
PERSON_BINDING = PowerOfAttorneyGapBinding(
    PERSON_GAP.information_id,
    PowerOfAttorneyGapType.AUTHORIZED_PERSON,
)
AREA_BINDING = PowerOfAttorneyGapBinding(
    AREA_GAP.information_id,
    PowerOfAttorneyGapType.REPRESENTATION_AREAS,
)
PERSON_QUESTION = PowerOfAttorneyQuestionCatalog().for_gap(
    PERSON_GAP,
    PERSON_BINDING,
)
AREA_QUESTION = PowerOfAttorneyQuestionCatalog().for_gap(
    AREA_GAP,
    AREA_BINDING,
)
assert PERSON_QUESTION is not None
assert AREA_QUESTION is not None


def conversation_input(
    state=STATE,
    state_id="understanding-state-journey",
    gaps=(PERSON_GAP, AREA_GAP),
    question=PERSON_QUESTION.text,
):
    return PowerOfAttorneyConversationInput(
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
        next_understanding_question=question if any(g.essential for g in gaps) else None,
    )


def journey_input(**changes):
    state = changes.pop("understanding_state", STATE)
    state_id = changes.pop("understanding_state_id", "understanding-state-journey")
    values = dict(
        understanding_state_id=state_id,
        understanding_state_hash=understanding_state_content_hash(state),
        understanding_state=state,
        conversation_input=conversation_input(state, state_id),
        gap_bindings=(PERSON_BINDING, AREA_BINDING),
    )
    values.update(changes)
    return PowerOfAttorneyJourneyInput(**values)


def build(value=None, service=None):
    return (service or GuardianPowerOfAttorneyJourneyService()).build(
        value or journey_input()
    )


def resolution(turn, kind):
    next_question = (
        "Welche weitere ausdrückliche Angabe möchten Sie zur offenen Frage ergänzen?"
        if kind is ClarificationResolutionType.KEEP_OPEN
        else None
    )
    return ClarificationResolution(
        "clarification-resolution-journey-{}".format(kind.value.lower()),
        TRIGGER.statement_id,
        TRIGGER.text,
        turn.question_id,
        turn.understanding_question,
        "statement-answer-{}".format(kind.value.lower()),
        "Die Klärung wird ausdrücklich so behandelt.",
        ("understanding-proposal-journey",),
        kind,
        "conversation:answer-{}".format(kind.value.lower()),
        "Ausdrückliche externe Resolution.",
        None,
        None,
        next_question,
    )


def external(turn, kind):
    item = resolution(turn, kind)
    return PowerOfAttorneyExternalClarification(
        turn.turn_id,
        UserStatementReference(
            item.answer_statement_id,
            item.answer_text,
            item.source_reference,
        ),
        item,
    )


def selected_external(turn, new_state, state_id="understanding-state-revised"):
    answer = UserStatementReference(
        "statement-selected-answer",
        "Alex wird ausdrücklich als mögliche Person genannt.",
        "conversation:selected-answer",
    )
    operation = UnderstandingOperation(
        UnderstandingOperationType.CLOSE_UNKNOWN,
        target_text=UNKNOWN_PERSON.text,
    )
    selected = ClarificationResolution(
        "clarification-resolution-selected-journey",
        TRIGGER.statement_id,
        TRIGGER.text,
        turn.question_id,
        turn.understanding_question,
        answer.statement_id,
        answer.text,
        ("understanding-proposal-selected-journey",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        answer.source_reference,
        "Extern und ausdrücklich ausgewählt.",
        "understanding-proposal-selected-journey",
        operation,
        None,
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
        AREA_QUESTION.text,
    )
    return PowerOfAttorneyExternalClarification(
        turn.turn_id,
        answer,
        selected,
        revision,
        "understanding-revision-selected-journey",
        state_id,
        understanding_state_content_hash(new_state),
    )


def test_valid_journey_starts_with_first_controlled_question():
    result = build()

    assert result.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_question == PERSON_QUESTION
    assert result.current_open_gap_id == PERSON_GAP.information_id
    assert result.next_action is PowerOfAttorneyJourneyAction.OBTAIN_USER_ANSWER
    assert len(result.turns) == 1


def test_stable_preparation_order_selects_first_essential_gap_without_ranking():
    current = conversation_input(
        gaps=(AREA_GAP, PERSON_GAP),
        question=AREA_QUESTION.text,
    )
    result = build(
        journey_input(
            conversation_input=current,
            gap_bindings=(AREA_BINDING, PERSON_BINDING),
        )
    )

    assert result.current_question == AREA_QUESTION
    assert not hasattr(result, "ranking")
    assert not hasattr(result, "score")


def test_nonessential_gap_is_skipped_and_ready_is_bounded():
    nonessential = MissingInformation(
        "missing-information-optional",
        "Ein nicht wesentlicher Punkt bleibt sichtbar.",
        False,
        "understanding:optional",
    )
    current = conversation_input(gaps=(nonessential,), question=None)
    result = build(
        journey_input(conversation_input=current, gap_bindings=())
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
    )
    assert result.review_preparation is None
    assert result.contradictions == (CONTRADICTION,)
    assert result.next_action is PowerOfAttorneyJourneyAction.PREPARE_PROFESSIONAL_REVIEW


def test_missing_controlled_question_blocks_without_free_replacement():
    result = build(journey_input(gap_bindings=(AREA_BINDING,)))

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    )
    assert result.current_question is None
    assert result.blockers == ("MISSING_GAP_BINDING",)


def test_catalog_without_known_question_blocks_visibly():
    service = GuardianPowerOfAttorneyJourneyService(
        catalog=PowerOfAttorneyQuestionCatalog(questions=())
    )
    result = build(service=service)

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    )
    assert result.blockers == ("CONTROLLED_QUESTION_NOT_FOUND",)


def test_duplicate_question_id_with_different_content_is_rejected():
    first = ControlledPowerOfAttorneyQuestion(
        "understanding-question-duplicate",
        PowerOfAttorneyGapType.AUTHORIZED_PERSON,
        "Welche Person ist ausdrücklich gemeint?",
        "source",
    )
    second = ControlledPowerOfAttorneyQuestion(
        first.question_id,
        PowerOfAttorneyGapType.REPRESENTATION_AREAS,
        "Welcher Bereich ist ausdrücklich gemeint?",
        "source",
    )
    with pytest.raises(ValueError, match="different content"):
        PowerOfAttorneyQuestionCatalog((first, second))


def test_turn_and_user_answer_alone_do_not_change_state():
    first = build()
    assert first.turns[-1].state_changed_by_turn is False
    with pytest.raises(ValueError, match="revision lineage"):
        PowerOfAttorneyExternalClarification(
            first.turns[-1].turn_id,
            UserStatementReference(
                "statement-answer",
                "Alex.",
                "conversation:answer",
            ),
            ClarificationResolution(
                "clarification-resolution-selected",
                TRIGGER.statement_id,
                TRIGGER.text,
                first.turns[-1].question_id,
                first.turns[-1].understanding_question,
                "statement-answer",
                "Alex.",
                ("understanding-proposal-selected",),
                ClarificationResolutionType.SELECT_PROPOSAL,
                "conversation:answer",
                "Extern ausgewählt.",
                "understanding-proposal-selected",
                UnderstandingOperation(
                    UnderstandingOperationType.CLOSE_UNKNOWN,
                    target_text=UNKNOWN_PERSON.text,
                ),
                None,
            ),
        )
    assert first.understanding_state == STATE


def test_partial_external_chain_is_rejected_before_service_execution():
    first = build()
    selected = ClarificationResolution(
        "clarification-resolution-selected",
        TRIGGER.statement_id,
        TRIGGER.text,
        first.turns[-1].question_id,
        first.turns[-1].understanding_question,
        "statement-selected-answer",
        "Alex wird ausdrücklich genannt.",
        ("understanding-proposal-selected",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        "conversation:selected-answer",
        "Extern ausgewählt.",
        "understanding-proposal-selected",
        UnderstandingOperation(
            UnderstandingOperationType.CLOSE_UNKNOWN,
            target_text=UNKNOWN_PERSON.text,
        ),
        None,
    )
    with pytest.raises(ValueError, match="complete revision lineage"):
        PowerOfAttorneyExternalClarification(
            first.turns[-1].turn_id,
            UserStatementReference(
                selected.answer_statement_id,
                selected.answer_text,
                selected.source_reference,
            ),
            selected,
        )


def test_complete_selected_chain_is_validated_before_the_next_question():
    first = build()
    new_state = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        (UNKNOWN_AREA,),
        STATE.contradictions,
        STATE.goals,
    )
    clarification = selected_external(first.turns[-1], new_state)
    current = conversation_input(
        new_state,
        "understanding-state-revised",
        (AREA_GAP,),
        AREA_QUESTION.text,
    )
    result = build(
        journey_input(
            understanding_state=new_state,
            understanding_state_id="understanding-state-revised",
            conversation_input=current,
            gap_bindings=(AREA_BINDING,),
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )

    assert result.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_question == AREA_QUESTION
    assert result.understanding_state == new_state
    assert result.turns[-1].previous_turn_id == first.turns[-1].turn_id
    assert len(result.turns) == 2


def test_wrong_revision_result_state_is_blocked():
    first = build()
    new_state = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        (UNKNOWN_AREA,),
        STATE.contradictions,
        STATE.goals,
    )
    clarification = selected_external(first.turns[-1], new_state)
    result = build(
        journey_input(
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    assert "Latest revision does not produce current state" in result.blockers[0]


def test_multiple_historical_revisions_remain_valid_and_auditable():
    first = build()
    state_after_person = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        (UNKNOWN_AREA,),
        STATE.contradictions,
        STATE.goals,
    )
    first_clarification = selected_external(
        first.turns[-1],
        state_after_person,
        "understanding-state-after-person",
    )
    area_input = conversation_input(
        state_after_person,
        "understanding-state-after-person",
        (AREA_GAP,),
        AREA_QUESTION.text,
    )
    second = build(
        journey_input(
            understanding_state=state_after_person,
            understanding_state_id="understanding-state-after-person",
            conversation_input=area_input,
            gap_bindings=(AREA_BINDING,),
            previous_turns=first.turns,
            clarifications=(first_clarification,),
        )
    )
    state_ready = UnderstandingState(
        STATE.facts,
        STATE.hypotheses,
        (),
        STATE.contradictions,
        STATE.goals,
    )
    answer = UserStatementReference(
        "statement-area-answer",
        "Die Vertretungsbereiche wurden extern ausdrücklich geklärt.",
        "conversation:area-answer",
    )
    operation = UnderstandingOperation(
        UnderstandingOperationType.CLOSE_UNKNOWN,
        target_text=UNKNOWN_AREA.text,
    )
    selected = ClarificationResolution(
        "clarification-resolution-area-selected",
        TRIGGER.statement_id,
        TRIGGER.text,
        second.turns[-1].question_id,
        second.turns[-1].understanding_question,
        answer.statement_id,
        answer.text,
        ("understanding-proposal-area-selected",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        answer.source_reference,
        "Extern ausgewählt.",
        "understanding-proposal-area-selected",
        operation,
        None,
    )
    revision = UnderstandingRevision(
        state_ready,
        (
            UnderstandingChange(
                UnderstandingOperationType.CLOSE_UNKNOWN,
                answer.text,
                UNKNOWN_AREA.text,
                UNKNOWN_AREA.text,
            ),
        ),
        "Welche Vorbereitung möchten Sie fachlich prüfen lassen?",
    )
    second_clarification = PowerOfAttorneyExternalClarification(
        second.turns[-1].turn_id,
        answer,
        selected,
        revision,
        "understanding-revision-area-selected",
        "understanding-state-ready",
        understanding_state_content_hash(state_ready),
    )
    ready_input = conversation_input(
        state_ready,
        "understanding-state-ready",
        (),
        None,
    )
    result = build(
        journey_input(
            understanding_state=state_ready,
            understanding_state_id="understanding-state-ready",
            conversation_input=ready_input,
            gap_bindings=(),
            previous_turns=second.turns,
            clarifications=(first_clarification, second_clarification),
            create_professional_review_preparation=True,
        )
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
    )
    assert result.clarifications == (
        first_clarification,
        second_clarification,
    )
    assert result.review_preparation is not None
    assert result.review_preparation.clarification_resolutions == (
        first_clarification.resolution,
        second_clarification.resolution,
    )


def test_foreign_resolution_is_blocked_as_inconsistent():
    first = build()
    clarification = external(first.turns[-1], ClarificationResolutionType.KEEP_OPEN)
    foreign = PowerOfAttorneyExternalClarification(
        "poa-turn-foreign",
        clarification.answer_statement,
        clarification.resolution,
    )
    result = build(
        journey_input(
            previous_turns=first.turns,
            clarifications=(foreign,),
        )
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    assert "foreign turn" in result.blockers[0]


def test_same_unchanged_question_is_unresolved_without_new_turn():
    first = build()
    second = build(journey_input(previous_turns=first.turns))

    assert second.status is PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED
    assert second.turns == first.turns
    assert second.relevant_previous_turn_id == first.turns[-1].turn_id
    assert second.current_question == first.current_question


def test_full_history_detects_non_adjacent_unresolved_question():
    first = build()
    area_conversation = conversation_input(
        gaps=(AREA_GAP, PERSON_GAP),
        question=AREA_QUESTION.text,
    )
    area = build(
        journey_input(
            conversation_input=area_conversation,
            gap_bindings=(AREA_BINDING, PERSON_BINDING),
            previous_turns=first.turns,
        )
    )
    repeated = build(
        journey_input(previous_turns=area.turns)
    )

    assert repeated.status is PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED
    assert repeated.relevant_previous_turn_id == first.turns[0].turn_id
    assert len(repeated.turns) == 2


@pytest.mark.parametrize(
    "kind",
    (
        ClarificationResolutionType.KEEP_OPEN,
        ClarificationResolutionType.REJECT_PROPOSALS,
    ),
)
def test_open_or_rejected_resolution_waits_without_state_change(kind):
    first = build()
    clarification = external(first.turns[-1], kind)
    result = build(
        journey_input(
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION
    )
    assert result.deferred_points == (PERSON_GAP.information_id,)
    assert result.understanding_state == STATE
    assert len(result.turns) == 1


def test_close_without_change_skips_gap_but_never_creates_fact():
    first = build()
    clarification = external(
        first.turns[-1],
        ClarificationResolutionType.CLOSE_WITHOUT_CHANGE,
    )
    current = conversation_input(
        gaps=(AREA_GAP,),
        question=AREA_QUESTION.text,
    )
    result = build(
        journey_input(
            conversation_input=current,
            gap_bindings=(AREA_BINDING,),
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )

    assert result.closed_without_change_points == (PERSON_GAP.information_id,)
    assert result.current_open_gap_id == AREA_GAP.information_id
    assert result.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_question == AREA_QUESTION
    assert result.facts == (FACT,)
    assert UNKNOWN_PERSON not in result.facts
    assert result.clarifications == (clarification,)


def test_wrong_state_hash_and_preparation_state_are_blocked():
    wrong_hash = PowerOfAttorneyJourneyInput(
        understanding_state_id="understanding-state-journey",
        understanding_state_hash="0" * 64,
        understanding_state=STATE,
        conversation_input=conversation_input(),
        gap_bindings=(PERSON_BINDING, AREA_BINDING),
    )
    assert build(wrong_hash).status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    foreign_conversation = conversation_input(state_id="understanding-state-foreign")
    assert build(journey_input(conversation_input=foreign_conversation)).status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )


def test_unlinked_foreign_state_in_turn_history_is_blocked():
    first = build()
    current = conversation_input(
        state_id="understanding-state-other",
        gaps=(PERSON_GAP, AREA_GAP),
        question=PERSON_QUESTION.text,
    )
    result = build(
        journey_input(
            understanding_state_id="understanding-state-other",
            conversation_input=current,
            previous_turns=first.turns,
        )
    )

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    assert "unlinked foreign state" in result.blockers[0]


def test_question_must_match_controlled_catalog_and_gap_source():
    uncontrolled = conversation_input(
        question="Welche frei formulierte Ersatzfrage möchten Sie beantworten?"
    )
    result = build(journey_input(conversation_input=uncontrolled))

    assert result.status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    assert result.blockers == ("PREPARATION_QUESTION_NOT_CONTROLLED",)


def test_conversation_ready_and_review_ready_are_not_legal_approval():
    ready_input = conversation_input(gaps=(), question=None)
    conversation_ready = build(
        journey_input(conversation_input=ready_input, gap_bindings=())
    )
    review_ready = build(
        journey_input(
            conversation_input=ready_input,
            gap_bindings=(),
            create_professional_review_preparation=True,
        )
    )

    assert conversation_ready.status is (
        PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
    )
    assert review_ready.status is (
        PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
    )
    assert review_ready.review_preparation is not None
    boundaries = " ".join(review_ready.review_preparation.professional_boundaries)
    assert "keine Rechtsberatung" in boundaries
    assert "weder eine Vorsorgevollmacht" in boundaries
    assert "rechtlichen Wirksamkeit" in boundaries


def test_review_package_contains_only_explicit_preparation_content():
    ready_input = conversation_input(gaps=(), question=None)
    result = build(
        journey_input(
            conversation_input=ready_input,
            gap_bindings=(),
            create_professional_review_preparation=True,
        )
    )
    package = result.review_preparation
    assert package is not None
    assert package.source_statements == (TRIGGER,)
    assert package.clarification_resolutions == ()
    assert package.facts == (FACT,)
    assert package.hypotheses == (HYPOTHESIS,)
    assert package.unknowns == (UNKNOWN_PERSON, UNKNOWN_AREA)
    assert package.contradictions == (CONTRADICTION,)
    assert package.people == ()
    assert package.representation_areas == ()
    assert package.document_references == ()
    assert package.organizational_steps == ()
    assert package.professional_reviews == ()


def test_contradiction_is_visible_and_only_its_essential_gap_blocks():
    open_result = build()
    ready_input = conversation_input(gaps=(), question=None)
    ready_result = build(
        journey_input(conversation_input=ready_input, gap_bindings=())
    )

    assert open_result.contradictions == (CONTRADICTION,)
    assert open_result.status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
    assert ready_result.contradictions == (CONTRADICTION,)
    assert ready_result.status is (
        PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
    )


def test_hypotheses_never_become_facts_and_no_defaults_are_added():
    result = build()

    assert result.facts == (FACT,)
    assert result.hypotheses == (HYPOTHESIS,)
    assert HYPOTHESIS not in result.facts
    assert result.people == ()
    assert result.representation_areas == ()
    assert result.organizational_steps == ()
    assert result.professional_reviews == ()


def test_identical_inputs_have_stable_ids_and_different_inputs_differ():
    value = journey_input()
    first = build(value)
    second = build(value)
    changed = build(
        journey_input(
            conversation_input=conversation_input(
                gaps=(AREA_GAP, PERSON_GAP),
                question=AREA_QUESTION.text,
            )
        )
    )

    assert first == second
    assert first.journey_id == second.journey_id
    assert first.turns[-1].turn_id == second.turns[-1].turn_id
    assert first.turns[-1].turn_id != changed.turns[-1].turn_id


def test_services_are_stateless_and_models_have_no_forbidden_mechanisms():
    service = GuardianPowerOfAttorneyJourneyService()
    forbidden = {
        "confidence",
        "score",
        "ranking",
        "routing",
        "workflow",
        "capability",
        "activation",
        "persistence",
        "memory",
        "llm",
        "network",
        "recommendation",
    }

    assert set(service.__dict__) == {
        "catalog",
        "preparation_service",
        "turn_service",
    }
    assert forbidden.isdisjoint(field.name for field in fields(PowerOfAttorneyJourneyInput))
    assert forbidden.isdisjoint(field.name for field in fields(type(build())))
