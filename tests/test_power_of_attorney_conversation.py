from dataclasses import fields, replace

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
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingProposalCandidate,
    UnderstandingState,
    Unknown,
)
from life_decisions import (
    DocumentReference,
    DocumentType,
    GuardianLifeDecisionConversationService,
    MissingInformation,
    OrganizationalPreparationStep,
    PowerOfAttorneyConversationInput,
    PowerOfAttorneyConversationStatus,
    PowerOfAttorneyPersonRole,
    PreparationStepType,
    ProfessionalReviewCategory,
    ProfessionalReviewNeed,
    RelevantPersonRole,
    RepresentationArea,
    RepresentationAreaReference,
    ReviewNeed,
    UserStatementReference,
)


FACT = Fact("Eine Vorsorgevollmacht soll vorbereitet werden.")
HYPOTHESIS = Hypothesis("Eine gemeinsame Vertretung könnte gewünscht sein.")
UNKNOWN = Unknown("Wie soll die Vertretung organisiert sein?")
CONTRADICTION = Contradiction(
    "Es gibt eine frühere Vollmacht. <> Es gibt keine frühere Vollmacht."
)
GOAL = Goal("Ein Gespräch mit einer Fachperson vorbereiten.")
STATE = UnderstandingState(
    (FACT,),
    (HYPOTHESIS,),
    (UNKNOWN,),
    (CONTRADICTION,),
    (GOAL,),
)
TRIGGER = UserStatementReference(
    "statement-trigger",
    "Ich möchte eine Vorsorgevollmacht besprechen.",
    "conversation:statement-trigger",
)
PERSON = RelevantPersonRole(
    "person-alex",
    "Alex",
    PowerOfAttorneyPersonRole.POSSIBLE_AUTHORIZED_PERSON,
    "conversation:statement-person",
)
AREAS = (
    RepresentationAreaReference(
        RepresentationArea.BANKING,
        "conversation:statement-area-banking",
    ),
    RepresentationAreaReference(
        RepresentationArea.HEALTH,
        "conversation:statement-area-health",
    ),
)
DOCUMENT = DocumentReference(
    id="document-existing-poa",
    document_type=DocumentType.POWER_OF_ATTORNEY,
    storage_reference="user-vault://documents/existing-poa",
    analysis_authorized=False,
)
STEP = OrganizationalPreparationStep(
    "preparation-step-documents",
    PreparationStepType.COLLECT_EXISTING_DOCUMENTS,
    "Vorhandene Vollmachten und Verfügungen zusammensuchen.",
    ("document-existing-poa",),
)
REVIEW = ProfessionalReviewNeed(
    "professional-review-legal",
    ProfessionalReviewCategory.LEGAL,
    ReviewNeed.RECOMMENDED,
    "Eine anwaltliche Prüfung kann ausdrücklich vorbereitet werden.",
    ("conversation:statement-trigger",),
)


def gap(identifier, description, essential=True):
    return MissingInformation(
        "missing-information-{}".format(identifier),
        description,
        essential,
        "understanding:unknown-{}".format(identifier),
    )


def complete_input(**changes):
    values = dict(
        understanding_state_id="understanding-state-001",
        understanding_state=STATE,
        triggering_statement_id=TRIGGER.statement_id,
        user_statements=(TRIGGER,),
        facts=(FACT,),
        hypotheses=(HYPOTHESIS,),
        unknowns=(),
        contradictions=(),
        goals=(GOAL,),
        clarification_resolutions=(),
        relevant_people=(PERSON,),
        representation_areas=AREAS,
        existing_documents=(DOCUMENT,),
        missing_information=(),
        organizational_steps=(STEP,),
        professional_reviews=(REVIEW,),
        next_understanding_question=None,
    )
    values.update(changes)
    return PowerOfAttorneyConversationInput(**values)


def prepare(value=None):
    return GuardianLifeDecisionConversationService().prepare(
        value or complete_input()
    )


def test_complete_known_situation_is_ready_for_conversation():
    result = prepare()

    assert result.status is (
        PowerOfAttorneyConversationStatus.CONVERSATION_PREPARATION_READY
    )
    assert result.known_situation == (FACT,)
    assert result.goals == (GOAL,)
    assert result.next_understanding_question is None


def test_missing_authorized_person_remains_visible_and_requires_question():
    missing = gap("person", "Eine bevollmächtigte Person ist noch nicht benannt.")
    result = prepare(
        complete_input(
            relevant_people=(),
            missing_information=(missing,),
            next_understanding_question=(
                "Welche Person oder welche Personen möchten Sie erwägen?"
            ),
        )
    )

    assert result.relevant_people == ()
    assert result.missing_information == (missing,)
    assert result.status is PowerOfAttorneyConversationStatus.NEEDS_CLARIFICATION


def test_multiple_possible_people_are_not_selected_or_ranked():
    second = RelevantPersonRole(
        "person-sam",
        "Sam",
        PowerOfAttorneyPersonRole.POSSIBLE_AUTHORIZED_PERSON,
        "conversation:statement-person",
    )
    missing = gap("selection", "Zwischen den möglichen Personen ist nichts ausgewählt.")
    result = prepare(
        complete_input(
            relevant_people=(PERSON, second),
            missing_information=(missing,),
            next_understanding_question=(
                "Möchten Sie eine Person auswählen oder beide offenhalten?"
            ),
        )
    )

    assert result.relevant_people == (PERSON, second)
    assert not hasattr(result, "selected_person")
    assert not hasattr(result, "ranking")


def test_unknown_representation_areas_are_not_filled_in():
    missing = gap("areas", "Die gewünschten Vertretungsbereiche sind unbekannt.")
    result = prepare(
        complete_input(
            representation_areas=(),
            missing_information=(missing,),
            next_understanding_question=(
                "Welche Vertretungsbereiche möchten Sie zunächst klären?"
            ),
        )
    )

    assert result.representation_areas == ()
    assert result.missing_information == (missing,)


def test_known_representation_areas_are_preserved_exactly():
    result = prepare()
    assert result.representation_areas is AREAS
    assert tuple(item.area for item in result.representation_areas) == (
        RepresentationArea.BANKING,
        RepresentationArea.HEALTH,
    )


def test_existing_power_of_attorney_remains_only_a_reference():
    result = prepare()

    assert result.existing_documents == (DOCUMENT,)
    assert result.existing_documents[0].storage_reference == (
        "user-vault://documents/existing-poa"
    )
    assert not hasattr(result.existing_documents[0], "content")


def test_contradictory_existing_document_information_stays_visible():
    result = prepare(
        complete_input(
            contradictions=(CONTRADICTION,),
            unknowns=(UNKNOWN,),
            missing_information=(
                gap("document", "Die Angaben zur früheren Vollmacht widersprechen sich."),
            ),
            next_understanding_question=(
                "Gibt es eine frühere Vollmacht, die Sie auffinden können?"
            ),
        )
    )

    assert result.contradictions == (CONTRADICTION,)
    assert result.open_points == (UNKNOWN,)


def test_hypothesis_unknown_contradiction_and_goal_keep_their_types():
    result = prepare(
        complete_input(
            unknowns=(UNKNOWN,),
            contradictions=(CONTRADICTION,),
            missing_information=(
                gap("mode", "Die Vertretungsorganisation ist noch offen."),
            ),
            next_understanding_question=(
                "Wie möchten Sie die Vertretung organisieren?"
            ),
        )
    )

    assert result.hypotheses == (HYPOTHESIS,)
    assert result.known_situation == (FACT,)
    assert HYPOTHESIS not in result.known_situation
    assert result.open_points == (UNKNOWN,)
    assert result.contradictions == (CONTRADICTION,)
    assert result.goals == (GOAL,)
    assert isinstance(result.hypotheses[0], Hypothesis)
    assert isinstance(result.open_points[0], Unknown)


def test_essential_gap_requires_exactly_one_understanding_question():
    missing = gap("person", "Eine Person fehlt.")
    with pytest.raises(ValueError, match="requires one question"):
        complete_input(missing_information=(missing,))
    with pytest.raises(ValueError, match="Exactly one"):
        complete_input(
            missing_information=(missing,),
            next_understanding_question="Wer? Oder jemand anderes?",
        )


def test_multiple_essential_gaps_still_produce_exactly_one_total_question():
    result = prepare(
        complete_input(
            missing_information=(
                gap("person", "Eine bevollmächtigte Person fehlt."),
                gap("areas", "Die Vertretungsbereiche fehlen."),
            ),
            next_understanding_question=(
                "Wen möchten Sie zunächst für welche Bereiche in Betracht ziehen?"
            ),
        )
    )

    assert len(result.missing_information) == 2
    assert result.next_understanding_question == (
        "Wen möchten Sie zunächst für welche Bereiche in Betracht ziehen?"
    )
    assert result.next_understanding_question.count("?") == 1


def test_no_question_is_allowed_without_an_essential_gap():
    with pytest.raises(ValueError, match="requires essential"):
        complete_input(next_understanding_question="Was fehlt noch?")


def test_professional_limits_are_explicit_without_legal_advice_or_document_text():
    result = prepare()
    boundaries = " ".join(result.professional_boundaries)

    assert "keine Rechtsberatung" in boundaries
    assert "keine Aussage zur rechtlichen Wirksamkeit" in boundaries
    assert "weder eine Vorsorgevollmacht noch Vertrags- oder Urkundentext" in boundaries
    assert not hasattr(result, "power_of_attorney_text")
    assert result.professional_reviews == (REVIEW,)


def test_people_are_not_evaluated_for_suitability_or_abuse():
    result = prepare()
    warning = " ".join(result.warnings)

    assert "weder Geschäftsfähigkeit noch Eignung" in warning
    assert "Missbrauch oder Interessenkonflikte" in warning
    assert not hasattr(result.relevant_people[0], "suitable")


def test_organizational_steps_and_reviews_are_explicit_inputs_only():
    result = prepare()

    assert result.organizational_steps == (STEP,)
    assert result.professional_reviews == (REVIEW,)
    empty = prepare(
        complete_input(organizational_steps=(), professional_reviews=())
    )
    assert empty.organizational_steps == ()
    assert empty.professional_reviews == ()


def test_referenced_item_must_belong_to_understanding_state():
    with pytest.raises(ValueError, match="outside the UnderstandingState"):
        complete_input(facts=(Fact("Eine nicht belegte Ergänzung."),))


def test_clarification_resolution_and_its_statements_remain_referenced():
    proposal_service = GuardianUnderstandingProposalService()
    proposal_set = proposal_service.create(
        STATE,
        "statement-original",
        "Freitag oder Samstag.",
        (
            UnderstandingProposalCandidate(
                UnderstandingOperation(
                    UnderstandingOperationType.ADD_FACT,
                    value_text="Freitag ist gewünscht.",
                ),
                "conversation:statement-original",
                "Eine ausdrücklich vorbereitete Alternative.",
            ),
            UnderstandingProposalCandidate(
                UnderstandingOperation(
                    UnderstandingOperationType.ADD_FACT,
                    value_text="Samstag ist gewünscht.",
                ),
                "conversation:statement-original",
                "Eine zweite ausdrücklich vorbereitete Alternative.",
            ),
        ),
        "Welcher Tag ist gemeint?",
    )
    clarification = GuardianClarificationResolutionService().resolve(
        STATE,
        proposal_set,
        ClarificationResolutionRequest(
            question_id=proposal_set.understanding_question_id,
            answer_statement_id="statement-answer",
            answer_text="Freitag.",
            affected_proposal_ids=(proposal_set.proposals[0].proposal_id,),
            resolution_type=ClarificationResolutionType.SELECT_PROPOSAL,
            source_reference="conversation:statement-answer",
            rationale="Ausdrückliche Auswahl.",
            selected_proposal_id=proposal_set.proposals[0].proposal_id,
        ),
    ).resolution
    original = UserStatementReference(
        "statement-original",
        "Freitag oder Samstag.",
        "conversation:statement-original",
    )
    answer = UserStatementReference(
        "statement-answer",
        "Freitag.",
        "conversation:statement-answer",
    )
    result = prepare(
        complete_input(
            user_statements=(TRIGGER, original, answer),
            clarification_resolutions=(clarification,),
        )
    )

    assert result.referenced_user_statements == (TRIGGER, original, answer)
    assert result.clarification_resolution_ids == (
        clarification.resolution_id,
    )


def test_input_and_result_expose_no_operation_routing_workflow_or_persistence():
    result = prepare()
    forbidden = {
        "operation",
        "operations",
        "routing",
        "workflow",
        "capability",
        "activation",
        "persistence",
        "memory",
        "confidence",
        "score",
        "probability",
    }

    assert forbidden.isdisjoint(
        field.name for field in fields(PowerOfAttorneyConversationInput)
    )
    assert forbidden.isdisjoint(
        field.name for field in fields(type(result))
    )


def test_preparation_does_not_change_understanding_state():
    before = STATE
    result = prepare()

    assert STATE is before
    assert result.known_situation == before.facts
    assert not hasattr(result, "revision")


def test_identical_typed_input_produces_deterministic_output():
    value = complete_input()
    service = GuardianLifeDecisionConversationService()

    first = service.prepare(value)
    second = service.prepare(value)

    assert first == second
    assert first.preparation_id == second.preparation_id
