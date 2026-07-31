from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
import socket

import pytest

from guardian_understanding import (
    ClarificationResolution,
    ClarificationResolutionType,
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
from life_decisions.advance_directive import (
    AdvanceDirectiveConversationStatus,
    AdvanceDirectiveConversationTurnInput,
    AdvanceDirectiveExperienceActionType,
    AdvanceDirectiveExternalClarification,
    AdvanceDirectiveGapBinding,
    AdvanceDirectiveGapType,
    AdvanceDirectiveJourneyInput,
    AdvanceDirectiveJourneyAction,
    AdvanceDirectiveJourneyStatus,
    AdvanceDirectivePersonReference,
    AdvanceDirectivePersonRole,
    AdvanceDirectivePreparationInput,
    AdvanceDirectiveQuestionCatalog,
    AdvanceDirectiveTextReference,
    GuardianAdvanceDirectiveConversationService,
    GuardianAdvanceDirectiveExperienceService,
    GuardianAdvanceDirectiveJourneyService,
    GuardianAdvanceDirectivePreparationService,
    MedicalMeasurePosition,
    MedicalMeasureStatement,
    MedicalMeasureType,
    MedicalSituationReference,
    MedicalSituationType,
)
from life_decisions.conversation import (
    MissingInformation,
    OrganizationalPreparationStep,
    PreparationStepType,
    ProfessionalReviewCategory,
    ProfessionalReviewNeed,
    ReviewNeed,
    UserStatementReference,
)
from life_decisions.models import DocumentReference, DocumentType


FACT = Fact("Eine Patientenverfügung soll vorbereitet werden.")
GOAL = Goal("Ein Gespräch mit medizinischen und rechtlichen Fachpersonen vorbereiten.")
HYPOTHESIS = Hypothesis("Eine vorhandene Verfügung könnte nicht mehr aktuell sein.")
UNKNOWN = Unknown("Welche medizinische Situation soll besprochen werden?")
CONTRADICTION = Contradiction("Beatmung wird gewünscht. <> Beatmung wird abgelehnt.")
STATE = UnderstandingState((FACT,), (HYPOTHESIS,), (UNKNOWN,), (CONTRADICTION,), (GOAL,))
TRIGGER = UserStatementReference(
    "statement-advance-directive-trigger",
    "Ich möchte eine Patientenverfügung vorbereiten.",
    "conversation:advance-directive-trigger",
)
ANSWER = UserStatementReference(
    "statement-advance-directive-answer",
    "Ich möchte diesen Punkt noch offenlassen.",
    "conversation:advance-directive-answer",
)
PERSON = AdvanceDirectivePersonReference(
    "advance-directive-person-alex",
    "Alex",
    AdvanceDirectivePersonRole.TRUSTED_PERSON,
    "conversation:person-alex",
)
SITUATION = MedicalSituationReference(
    "medical-situation-dying-phase",
    MedicalSituationType.DYING_PHASE,
    "Eine ausdrücklich genannte Sterbephase.",
    ("conversation:situation",),
)
MEASURE = MedicalMeasureStatement(
    "medical-measure-statement-ventilation",
    MedicalMeasureType.ARTIFICIAL_VENTILATION,
    MedicalMeasurePosition.UNCERTAIN,
    (),
    ("conversation:measure",),
)
WISH = AdvanceDirectiveTextReference(
    "advance-directive-text-self-determination",
    "Selbstbestimmung soll ausdrücklich berücksichtigt werden.",
    ("conversation:wish",),
)
DOCUMENT = DocumentReference(
    "document-existing-advance-directive",
    DocumentType.ADVANCE_DIRECTIVE,
    "user-vault://advance-directive",
    False,
)
STEP = OrganizationalPreparationStep(
    "preparation-step-medical-conversation",
    PreparationStepType.PREPARE_MEDICAL_CLARIFICATION,
    "Das ausdrücklich gewünschte ärztliche Gespräch vorbereiten.",
    ("conversation:medical-review",),
)
REVIEW = ProfessionalReviewNeed(
    "professional-review-medical",
    ProfessionalReviewCategory.MEDICAL,
    ReviewNeed.REQUIRED,
    "Ein ausdrücklich gewünschtes ärztliches Beratungsgespräch.",
    ("conversation:medical-review",),
)
GAP = MissingInformation(
    "missing-information-medical-situation",
    "Die relevante medizinische Situation ist noch offen.",
    True,
    "conversation:missing-situation",
)
BINDING = AdvanceDirectiveGapBinding(
    GAP.information_id,
    AdvanceDirectiveGapType.MEDICAL_SITUATION,
)


def preparation_input(**changes):
    values = dict(
        understanding_state_id="understanding-state-advance-directive",
        understanding_state=STATE,
        triggering_statement_id=TRIGGER.statement_id,
        user_statements=(TRIGGER,),
        facts=(FACT,),
        goals=(GOAL,),
        hypotheses=(HYPOTHESIS,),
        unknowns=(UNKNOWN,),
        contradictions=(CONTRADICTION,),
        people=(PERSON,),
        documents=(DOCUMENT,),
        personal_wishes=(WISH,),
        medical_situations=(SITUATION,),
        medical_measures=(MEASURE,),
        personal_values=(WISH,),
        missing_information=(GAP,),
        organizational_steps=(STEP,),
        professional_reviews=(REVIEW,),
        next_understanding_question="Welche medizinische Situation möchten Sie ausdrücklich besprechen?",
    )
    values.update(changes)
    return AdvanceDirectivePreparationInput(**values)


def prepare(**changes):
    return GuardianAdvanceDirectivePreparationService().prepare(preparation_input(**changes))


def journey(preparation=None, **changes):
    values = dict(
        preparation=preparation or prepare(),
        understanding_state=STATE,
        gap_bindings=(BINDING,),
    )
    values.update(changes)
    return GuardianAdvanceDirectiveJourneyService().build(AdvanceDirectiveJourneyInput(**values))


def resolution(turn, kind=ClarificationResolutionType.KEEP_OPEN):
    return ClarificationResolution(
        "clarification-resolution-advance-directive",
        TRIGGER.statement_id,
        TRIGGER.text,
        turn.question_id,
        turn.question,
        ANSWER.statement_id,
        ANSWER.text,
        ("understanding-proposal-advance-directive",),
        kind,
        ANSWER.source_reference,
        "Ausdrückliche externe Klärung.",
        None,
        None,
        "Welche Angabe möchten Sie als Nächstes klären?" if kind is ClarificationResolutionType.KEEP_OPEN else None,
    )


def selected_chain():
    first = journey()
    added = Fact("Die medizinische Situation wurde ausdrücklich benannt.")
    new_state = UnderstandingState(
        (FACT, added), (HYPOTHESIS,), (UNKNOWN,), (CONTRADICTION,), (GOAL,)
    )
    operation = UnderstandingOperation(
        UnderstandingOperationType.ADD_FACT,
        value_text=added.text,
    )
    selected = ClarificationResolution(
        "clarification-resolution-advance-directive-selected",
        TRIGGER.statement_id,
        TRIGGER.text,
        first.turns[0].question_id,
        first.turns[0].question,
        ANSWER.statement_id,
        ANSWER.text,
        ("understanding-proposal-advance-directive",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        ANSWER.source_reference,
        "Ausdrückliche Proposal-Auswahl.",
        "understanding-proposal-advance-directive",
        operation,
        None,
    )
    revision = UnderstandingRevision(
        new_state,
        (
            UnderstandingChange(
                UnderstandingOperationType.ADD_FACT,
                ANSWER.text,
                None,
                added.text,
            ),
        ),
        "Welche Angabe möchten Sie als Nächstes klären?",
    )
    new_input = preparation_input(
        understanding_state=new_state,
        user_statements=(TRIGGER, ANSWER),
        facts=(FACT, added),
        clarification_resolutions=(selected,),
        missing_information=(),
        next_understanding_question=None,
    )
    new_preparation = GuardianAdvanceDirectivePreparationService().prepare(new_input)
    external = AdvanceDirectiveExternalClarification(
        first.turns[0].turn_id,
        ANSWER,
        selected,
        revision,
        "understanding-revision:advance-directive",
        new_preparation.understanding_state_id,
        new_preparation.understanding_state_hash,
    )
    return first, new_state, new_preparation, external


def test_valid_preparation_is_complete_stable_and_separates_understanding_content():
    first = prepare()
    second = prepare()

    assert first == second
    assert first.preparation_id == second.preparation_id
    assert first.facts == (FACT,)
    assert first.goals == (GOAL,)
    assert first.hypotheses == (HYPOTHESIS,)
    assert first.unknowns == (UNKNOWN,)
    assert first.contradictions == (CONTRADICTION,)
    assert first.status is AdvanceDirectiveConversationStatus.NEEDS_CLARIFICATION


def test_preparation_copies_only_explicit_medical_and_personal_inputs():
    empty = prepare(
        people=(), documents=(), personal_wishes=(), medical_situations=(),
        medical_measures=(), limits_and_refusals=(), personal_values=(),
        organizational_steps=(), professional_reviews=(),
    )

    assert empty.people == ()
    assert empty.medical_situations == ()
    assert empty.medical_measures == ()
    assert empty.personal_wishes == ()
    assert empty.personal_values == ()
    assert empty.organizational_steps == ()
    assert empty.professional_reviews == ()


@pytest.mark.parametrize(
    "position",
    (MedicalMeasurePosition.UNSPECIFIED, MedicalMeasurePosition.UNCERTAIN),
)
def test_unspecified_and_uncertain_positions_remain_neutral(position):
    statement = replace(MEASURE, position=position)
    result = prepare(medical_measures=(statement,))

    assert result.medical_measures[0].position is position
    assert result.medical_measures[0].conditions == ()
    assert result.medical_measures[0].position not in (
        MedicalMeasurePosition.ACCEPTS,
        MedicalMeasurePosition.REFUSES,
    )


def test_conditions_require_an_explicit_conditional_position():
    conditional = replace(
        MEASURE,
        position=MedicalMeasurePosition.REFUSES_WITH_CONDITIONS,
        conditions=("Nur für die ausdrücklich genannte Situation.",),
    )
    assert prepare(medical_measures=(conditional,)).medical_measures == (conditional,)
    with pytest.raises(ValueError):
        replace(MEASURE, conditions=("Nicht zugeordnet.",))
    with pytest.raises(ValueError):
        replace(MEASURE, position=MedicalMeasurePosition.ACCEPTS_WITH_CONDITIONS)


def test_first_essential_gap_selects_exactly_one_controlled_question():
    result = journey()

    assert result.status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_question is not None
    assert result.current_question.missing_information_id == GAP.information_id
    assert result.current_question.text == preparation_input().next_understanding_question
    assert result.current_question.text.count("?") == 1
    assert len(result.turns) == 1


def test_missing_binding_blocks_without_free_replacement_question():
    result = GuardianAdvanceDirectiveJourneyService().build(
        AdvanceDirectiveJourneyInput(prepare(), STATE, ())
    )

    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    assert result.current_question is None
    assert result.blockers == ("MISSING_GAP_BINDING",)


def test_missing_catalog_question_blocks_without_dynamic_question():
    result = GuardianAdvanceDirectiveJourneyService(
        AdvanceDirectiveQuestionCatalog(())
    ).build(AdvanceDirectiveJourneyInput(prepare(), STATE, (BINDING,)))

    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    assert result.current_question is None
    assert result.blockers == ("MISSING_CONTROLLED_QUESTION",)


def test_tampered_preparation_id_or_question_is_blocked_without_defaults():
    tampered_id = replace(prepare(), preparation_id="advance-directive-preparation-tampered")
    result = journey(tampered_id)
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert result.blockers == ("PREPARATION_ID_MISMATCH",)

    tampered_question = prepare(
        next_understanding_question="Welche andere einzelne Angabe ist offen?"
    )
    result = journey(tampered_question)
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert result.blockers == ("PREPARATION_QUESTION_MISMATCH",)


def test_conversation_turn_is_immutable_and_never_changes_state():
    built = journey()
    turn = built.turns[0]

    assert turn.state_changed_by_turn is False
    assert turn.source_understanding_state_hash == built.preparation.understanding_state_hash
    with pytest.raises(FrozenInstanceError):
        turn.state_changed_by_turn = True


def test_answer_without_resolution_waits_without_state_change():
    first = journey()
    pending = AdvanceDirectiveExternalClarification(first.turns[0].turn_id, ANSWER)
    result = journey(previous_turns=first.turns, clarifications=(pending,))

    assert result.status is AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION
    assert result.understanding_state == STATE
    assert len(result.turns) == 1


def test_partial_or_foreign_external_chain_is_blocked():
    first = journey()
    selected = resolution(first.turns[0], ClarificationResolutionType.SELECT_PROPOSAL)
    partial = AdvanceDirectiveExternalClarification(first.turns[0].turn_id, ANSWER, selected)
    result = journey(previous_turns=first.turns, clarifications=(partial,))
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "PARTIAL_EXTERNAL_ARTIFACT_CHAIN" in result.blockers

    foreign = replace(partial, source_turn_id="advance-directive-turn-foreign")
    result = journey(previous_turns=first.turns, clarifications=(foreign,))
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "CLARIFICATION_TURN_MISMATCH" in result.blockers


def test_complete_external_chain_is_validated_and_uses_updated_preparation():
    first, new_state, new_preparation, external = selected_chain()
    result = journey(
        new_preparation,
        understanding_state=new_state,
        previous_turns=first.turns,
        clarifications=(external,),
    )

    assert result.status is AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY
    assert result.understanding_state == new_state
    assert result.preparation == new_preparation
    assert result.turns == first.turns


def test_wrong_result_hash_or_foreign_revision_is_blocked():
    first, new_state, new_preparation, external = selected_chain()
    wrong_hash = replace(external, resulting_understanding_state_hash="0" * 64)
    result = journey(
        new_preparation,
        understanding_state=new_state,
        previous_turns=first.turns,
        clarifications=(wrong_hash,),
    )
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "RESULTING_STATE_MISMATCH" in result.blockers

    wrong_change = replace(
        external,
        revision=replace(external.revision, changes=()),
    )
    result = journey(
        new_preparation,
        understanding_state=new_state,
        previous_turns=first.turns,
        clarifications=(wrong_change,),
    )
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "REVISION_OPERATION_MISMATCH" in result.blockers

    foreign_revision = replace(
        external,
        revision=replace(external.revision, state=STATE),
    )
    result = journey(
        new_preparation,
        understanding_state=new_state,
        previous_turns=first.turns,
        clarifications=(foreign_revision,),
    )
    assert result.status is AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "RESULTING_STATE_MISMATCH" in result.blockers


def test_unchanged_question_is_never_repeated_even_after_other_turns():
    first = journey()
    other = replace(first.turns[0], turn_id="advance-directive-turn-other", question_id="understanding-question-other", question="Welche andere Angabe bleibt offen?")
    result = journey(previous_turns=(first.turns[0], other))

    assert result.status is AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED
    assert result.current_question is not None
    assert result.relevant_previous_turn_id == first.turns[0].turn_id
    assert len(result.turns) == 2


@pytest.mark.parametrize(
    ("kind", "field"),
    (
        (ClarificationResolutionType.KEEP_OPEN, "deferred_points"),
        (ClarificationResolutionType.REJECT_PROPOSALS, "rejected_proposal_points"),
        (ClarificationResolutionType.CLOSE_WITHOUT_CHANGE, "closed_without_change_points"),
    ),
)
def test_nonselecting_resolutions_never_become_facts(kind, field):
    first = journey()
    item = AdvanceDirectiveExternalClarification(first.turns[0].turn_id, ANSWER, resolution(first.turns[0], kind))
    result = journey(previous_turns=first.turns, clarifications=(item,))

    assert GAP.information_id in getattr(result, field)
    assert result.preparation.facts == (FACT,)
    assert ANSWER.text not in tuple(fact.text for fact in result.preparation.facts)


def test_contradictions_and_distinct_measure_positions_are_not_resolved():
    accepts = replace(MEASURE, statement_id="medical-measure-statement-accepts", position=MedicalMeasurePosition.ACCEPTS)
    refuses = replace(MEASURE, statement_id="medical-measure-statement-refuses", position=MedicalMeasurePosition.REFUSES)
    ready = prepare(medical_measures=(accepts, refuses), missing_information=(), next_understanding_question=None)
    result = journey(ready)

    assert result.status is AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY
    assert result.preparation.medical_measures == (accepts, refuses)
    assert result.preparation.contradictions == (CONTRADICTION,)


def test_essential_gap_blocks_readiness_but_nonblocking_contradiction_does_not():
    assert journey().status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION
    ready = prepare(missing_information=(), next_understanding_question=None)
    assert journey(ready).status is AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY
    assert ready.contradictions == (CONTRADICTION,)


def test_professional_review_contains_only_explicit_content_and_no_checklist():
    ready = prepare(missing_information=(), next_understanding_question=None)
    result = journey(ready, create_professional_review_preparation=True)
    package = result.professional_review

    assert result.status is AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
    assert package is not None
    assert package.medical_situations == (SITUATION,)
    assert package.medical_measures == (MEASURE,)
    assert package.people == (PERSON,)
    assert package.professional_reviews == (REVIEW,)
    assert not hasattr(package, "checklist")
    assert not hasattr(package, "recommendations")


@pytest.mark.parametrize("status", tuple(AdvanceDirectiveJourneyStatus))
def test_ui_neutral_experience_supports_every_journey_status(status):
    base = journey()
    actions = {
        AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION: AdvanceDirectiveJourneyAction.OBTAIN_USER_ANSWER,
        AdvanceDirectiveJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: AdvanceDirectiveJourneyAction.OBTAIN_EXTERNAL_RESOLUTION,
        AdvanceDirectiveJourneyStatus.QUESTION_UNRESOLVED: AdvanceDirectiveJourneyAction.REVIEW_UNRESOLVED_QUESTION,
        AdvanceDirectiveJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: AdvanceDirectiveJourneyAction.PROVIDE_CONTROLLED_QUESTION,
        AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: AdvanceDirectiveJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS,
        AdvanceDirectiveJourneyStatus.CONVERSATION_PREPARATION_READY: AdvanceDirectiveJourneyAction.PREPARE_PROFESSIONAL_REVIEW,
        AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY: AdvanceDirectiveJourneyAction.USE_PREPARATION_PACKAGE,
    }
    if status is AdvanceDirectiveJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY:
        ready = prepare(missing_information=(), next_understanding_question=None)
        base = journey(ready, create_professional_review_preparation=True)
    altered = replace(
        base,
        status=status,
        next_action=actions[status],
        blockers=("TECHNICAL_TEST",) if "BLOCKED" in status.value else (),
        current_question=base.current_question if status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION else None,
    )
    result = GuardianAdvanceDirectiveExperienceService().present(altered)

    assert result.journey_status is status
    assert result.status_heading
    assert result.status_description
    assert (result.current_question is not None) is (status is AdvanceDirectiveJourneyStatus.NEEDS_CLARIFICATION)


def test_experience_preserves_explicit_medical_content_and_neutral_positions():
    result = GuardianAdvanceDirectiveExperienceService().present(journey())

    assert result.medical_situations[0].text == SITUATION.description
    assert result.medical_measures[0].text == MedicalMeasureType.ARTIFICIAL_VENTILATION.value
    assert result.medical_measures[0].status == MedicalMeasurePosition.UNCERTAIN.value
    assert result.hypotheses[0].text == HYPOTHESIS.text
    assert result.contradictions[0].text == CONTRADICTION.text
    assert HYPOTHESIS.text not in tuple(item.text for item in result.facts)


def test_experience_has_one_question_no_example_and_only_compatible_actions():
    result = GuardianAdvanceDirectiveExperienceService().present(journey())

    assert result.current_question is not None
    assert result.current_question.text.count("?") == 1
    assert not hasattr(result.current_question, "example_answer")
    assert result.allowed_actions == (
        AdvanceDirectiveExperienceActionType.ANSWER_CURRENT_QUESTION,
        AdvanceDirectiveExperienceActionType.KEEP_POINT_OPEN,
        AdvanceDirectiveExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
    )


def test_blocked_experience_separates_technical_error_and_hides_domain_content():
    blocked = replace(
        journey(),
        status=AdvanceDirectiveJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS,
        blockers=("STATE_HASH_MISMATCH",),
        current_question=None,
    )
    result = GuardianAdvanceDirectiveExperienceService().present(blocked)

    assert result.technical_errors == ("STATE_HASH_MISMATCH",)
    assert result.facts == ()
    assert result.medical_situations == ()
    assert "STATE_HASH_MISMATCH" not in result.status_description


def test_experience_and_review_show_all_required_professional_boundaries():
    ready = prepare(missing_information=(), next_understanding_question=None)
    result = GuardianAdvanceDirectiveExperienceService().present(
        journey(ready, create_professional_review_preparation=True)
    )
    text = " ".join(result.professional_boundaries)

    for phrase in (
        "keine medizinische oder rechtliche Beratung",
        "keinen Patientenverfügungstext",
        "keine Behandlungsentscheidung",
        "Einwilligungsfähigkeit",
        "rechtliche Wirksamkeit",
        "empfiehlt keine medizinische Maßnahme",
        "nicht automatisch ausgelegt",
    ):
        assert phrase in text


def test_experience_ids_are_semantic_deterministic_and_time_independent():
    service = GuardianAdvanceDirectiveExperienceService()
    first = service.present(journey())
    second = service.present(journey())
    changed = service.present(journey(prepare(medical_measures=())))

    assert first == second
    assert first.experience_id == second.experience_id
    assert first.experience_id != changed.experience_id
    assert not hasattr(first, "created_at")
    assert not hasattr(first, "timestamp")


def test_services_are_stateless_and_do_not_write_or_use_network(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("side effect")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    services = (
        GuardianAdvanceDirectivePreparationService(),
        GuardianAdvanceDirectiveConversationService(),
        GuardianAdvanceDirectiveExperienceService(),
    )
    assert all(service.__dict__ == {} for service in services)
    GuardianAdvanceDirectiveExperienceService().present(journey())


def test_contract_contains_no_decision_routing_llm_or_confidence_fields():
    forbidden = {"confidence", "score", "ranking", "routing", "workflow", "llm", "recommendation", "medical_advice", "legal_advice"}
    from life_decisions.advance_directive import AdvanceDirectiveExperience

    assert forbidden.isdisjoint(field.name for field in fields(AdvanceDirectiveExperience))
