from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
import socket

import pytest

from guardian_understanding.clarification import ClarificationResolutionType
from life_decisions.conversation import (
    OrganizationalPreparationStep,
    PowerOfAttorneyPersonRole,
    PreparationStepType,
    ProfessionalReviewCategory,
    ProfessionalReviewNeed,
    RelevantPersonRole,
    RepresentationArea,
    RepresentationAreaReference,
    ReviewNeed,
)
from life_decisions.experience import (
    GuardianPowerOfAttorneyExperienceService,
    PowerOfAttorneyExperienceActionType,
    PowerOfAttorneyExperienceConsistencyError,
    PowerOfAttorneyJourneyExperience,
)
import life_decisions
from life_decisions.journey import (
    PowerOfAttorneyJourneyAction,
    PowerOfAttorneyJourneyStatus,
)
from life_decisions.models import DocumentReference, DocumentType
from tests.test_power_of_attorney_journey import (
    AREA_BINDING,
    AREA_GAP,
    AREA_QUESTION,
    CONTRADICTION,
    FACT,
    GOAL,
    HYPOTHESIS,
    PERSON_BINDING,
    PERSON_GAP,
    PERSON_QUESTION,
    STATE,
    TRIGGER,
    build,
    conversation_input,
    external,
    journey_input,
)


def present(journey=None):
    return GuardianPowerOfAttorneyExperienceService().present(journey or build())


def ready_journey(review=False, conversation=None):
    current = conversation or conversation_input(gaps=(), question=None)
    return build(
        journey_input(
            conversation_input=current,
            gap_bindings=(),
            create_professional_review_preparation=review,
        )
    )


def test_needs_clarification_shows_exactly_the_controlled_question():
    journey = build()
    result = present(journey)

    assert result.journey_status is PowerOfAttorneyJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_question is not None
    assert result.current_question.question_id == journey.current_question.question_id
    assert result.current_question.text == journey.current_question.text
    assert result.current_question.missing_information_id == PERSON_GAP.information_id
    assert result.current_question.source_references == (
        PERSON_GAP.source_reference,
    )
    assert result.current_question.text.count("?") == 1


def test_question_has_neutral_gap_explanation_but_no_second_question_or_answer():
    result = present()
    question = result.current_question
    assert question is not None

    assert "noch nicht ausdrücklich benannt" in question.why_needed
    assert "?" not in question.why_needed
    assert not hasattr(question, "example_answer")
    assert not hasattr(question, "recommended_answer")
    assert sum(value.count("?") for value in (question.text, question.why_needed)) == 1


def test_needs_clarification_actions_are_limited_and_do_not_execute():
    result = present()
    kinds = tuple(item.action_type for item in result.allowed_actions)

    assert kinds == (
        PowerOfAttorneyExperienceActionType.ANSWER_CURRENT_QUESTION,
        PowerOfAttorneyExperienceActionType.KEEP_POINT_OPEN,
        PowerOfAttorneyExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
    )
    assert result.next_action is (
        PowerOfAttorneyExperienceActionType.ANSWER_CURRENT_QUESTION
    )
    assert not hasattr(result, "resolution")
    assert not hasattr(result, "revision")


def test_waiting_for_external_resolution_claims_no_state_change():
    first = build()
    clarification = external(
        first.turns[-1], ClarificationResolutionType.KEEP_OPEN
    )
    journey = build(
        journey_input(
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )
    result = present(journey)

    assert result.journey_status is (
        PowerOfAttorneyJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION
    )
    assert result.current_question is None
    assert result.unresolved_question_id == first.turns[-1].question_id
    assert "Zustandsänderung wird nicht behauptet" in result.status_description
    assert result.source_understanding_state_hash == journey.understanding_state_hash


def test_question_unresolved_references_previous_turn_without_repeating_question():
    first = build()
    journey = build(journey_input(previous_turns=first.turns))
    result = present(journey)

    assert result.journey_status is PowerOfAttorneyJourneyStatus.QUESTION_UNRESOLVED
    assert result.current_question is None
    assert result.unresolved_question_id == first.turns[-1].question_id
    assert result.relevant_previous_turn_id == first.turns[-1].turn_id
    assert "weder automatisch gedeutet noch erneut" in result.status_description
    assert "erneut" in result.status_description


def test_unresolved_status_exposes_only_controlled_nonexecuting_actions():
    first = build()
    result = present(build(journey_input(previous_turns=first.turns)))

    assert tuple(action.action_type for action in result.allowed_actions) == (
        PowerOfAttorneyExperienceActionType.REQUEST_CONTROLLED_CLARIFICATION,
        PowerOfAttorneyExperienceActionType.KEEP_POINT_OPEN,
        PowerOfAttorneyExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
    )
    assert PowerOfAttorneyExperienceActionType.EXPORT_PROFESSIONAL_PREPARATION not in (
        action.action_type for action in result.allowed_actions
    )


def test_missing_controlled_question_is_a_safe_user_blocker():
    journey = build(journey_input(gap_bindings=(AREA_BINDING,)))
    result = present(journey)

    assert result.journey_status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    )
    assert result.current_question is None
    assert "keine freigegebene kontrollierte Frage" in result.status_description
    assert tuple(item.action_type for item in result.allowed_actions) == (
        PowerOfAttorneyExperienceActionType.NO_ACTION_AVAILABLE,
    )
    assert result.technical_issues[0].error_code == "MISSING_GAP_BINDING"


def test_inconsistent_journey_suppresses_domain_content_and_separates_error_details():
    invalid_input = replace(
        journey_input(),
        understanding_state_hash="0" * 64,
    )
    journey = build(invalid_input)
    result = present(journey)

    assert result.journey_status is (
        PowerOfAttorneyJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    )
    assert result.known_situation == ()
    assert result.goals == ()
    assert result.hypotheses == ()
    assert result.contradictions == ()
    assert result.people == ()
    assert "nicht zuverlässig" not in result.technical_issues[0].technical_cause
    assert "nicht konsistent" in result.status_description
    assert result.technical_issues[0].technical_cause not in result.status_description


def test_additional_experience_consistency_mismatch_is_structured():
    journey = build()
    inconsistent = replace(
        journey,
        next_action=PowerOfAttorneyJourneyAction.PREPARE_PROFESSIONAL_REVIEW,
    )
    with pytest.raises(PowerOfAttorneyExperienceConsistencyError) as raised:
        present(inconsistent)

    assert raised.value.issue.error_code == "NEXT_ACTION_MISMATCH"
    assert "nicht zuverlässig dargestellt" in raised.value.user_message
    assert raised.value.issue.technical_cause not in raised.value.user_message


def test_conversation_ready_preserves_uncertainties_and_is_not_legal_approval():
    result = present(ready_journey())

    assert result.journey_status is (
        PowerOfAttorneyJourneyStatus.CONVERSATION_PREPARATION_READY
    )
    assert result.current_question is None
    assert result.hypotheses[0].text == HYPOTHESIS.text
    assert result.contradictions[0].text == CONTRADICTION.text
    assert "keine rechtliche oder fachliche Freigabe" in result.status_description
    assert result.next_action is (
        PowerOfAttorneyExperienceActionType.PREPARE_PROFESSIONAL_REVIEW
    )


def test_professional_review_ready_is_complete_but_not_effectiveness_claim():
    result = present(ready_journey(review=True))

    assert result.journey_status is (
        PowerOfAttorneyJourneyStatus.PROFESSIONAL_REVIEW_PREPARATION_READY
    )
    assert result.professional_review is not None
    assert "weder fertig noch geprüft oder wirksam" in result.status_description
    assert result.next_action is (
        PowerOfAttorneyExperienceActionType.REVIEW_PROFESSIONAL_PREPARATION
    )


def test_review_projection_uses_only_explicit_people_areas_documents_steps_and_needs():
    person = RelevantPersonRole(
        "person-explicit-alex",
        "Alex",
        PowerOfAttorneyPersonRole.POSSIBLE_AUTHORIZED_PERSON,
        "conversation:person-alex",
    )
    area = RepresentationAreaReference(
        RepresentationArea.BANKING,
        "conversation:area-banking",
    )
    document = DocumentReference(
        "document-explicit-poa",
        DocumentType.POWER_OF_ATTORNEY,
        "user-vault://documents/poa",
        False,
    )
    step = OrganizationalPreparationStep(
        "preparation-step-explicit-document",
        PreparationStepType.COLLECT_EXISTING_DOCUMENTS,
        "Vorhandenes Dokument ausdrücklich bereitlegen.",
        ("document-explicit-poa",),
    )
    need = ProfessionalReviewNeed(
        "professional-review-explicit-legal",
        ProfessionalReviewCategory.LEGAL,
        ReviewNeed.RECOMMENDED,
        "Eine ausdrücklich gewünschte anwaltliche Prüfung vorbereiten.",
        (TRIGGER.source_reference,),
    )
    current = replace(
        conversation_input(gaps=(), question=None),
        relevant_people=(person,),
        representation_areas=(area,),
        existing_documents=(document,),
        organizational_steps=(step,),
        professional_reviews=(need,),
    )
    result = present(ready_journey(review=True, conversation=current))
    review = result.professional_review
    assert review is not None

    assert tuple(item.text for item in review.people) == ("Alex",)
    assert tuple(item.text for item in review.representation_areas) == ("BANKING",)
    assert tuple(item.reference_id for item in review.document_references) == (
        document.id,
    )
    assert tuple(item.text for item in review.organizational_steps) == (
        step.description,
    )
    assert tuple(item.text for item in review.professional_reviews) == (
        need.reason,
    )
    assert len(review.people) == len(current.relevant_people)
    assert len(review.professional_reviews) == len(current.professional_reviews)


def test_empty_explicit_sections_do_not_gain_defaults_or_checklists():
    result = present(ready_journey(review=True))
    review = result.professional_review
    assert review is not None

    assert review.people == ()
    assert review.representation_areas == ()
    assert review.document_references == ()
    assert review.organizational_steps == ()
    assert review.professional_reviews == ()
    assert not hasattr(review, "checklist")
    assert not hasattr(review, "recommendations")


def test_open_essential_and_nonessential_points_remain_separate_and_ordered():
    optional = replace(
        AREA_GAP,
        information_id="missing-information-optional-area",
        essential=False,
    )
    current = conversation_input(
        gaps=(PERSON_GAP, optional),
        question=PERSON_QUESTION.text,
    )
    result = present(
        build(
            journey_input(
                conversation_input=current,
                gap_bindings=(PERSON_BINDING,),
            )
        )
    )

    assert tuple(item.point_id for item in result.essential_open_points) == (
        PERSON_GAP.information_id,
    )
    assert tuple(item.point_id for item in result.other_open_points) == (
        optional.information_id,
    )
    assert result.essential_open_points[0].disposition == "OPEN_ESSENTIAL"
    assert result.other_open_points[0].disposition == "OPEN_OTHER"


@pytest.mark.parametrize(
    ("resolution_type", "field_name", "disposition"),
    (
        (
            ClarificationResolutionType.KEEP_OPEN,
            "deferred_points",
            "DEFERRED_KEEP_OPEN",
        ),
        (
            ClarificationResolutionType.REJECT_PROPOSALS,
            "rejected_proposal_points",
            "PROPOSALS_REJECTED_POINT_STILL_OPEN",
        ),
    ),
)
def test_deferred_and_rejected_proposals_remain_visibly_unresolved(
    resolution_type,
    field_name,
    disposition,
):
    first = build()
    clarification = external(first.turns[-1], resolution_type)
    journey = build(
        journey_input(
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )
    result = present(journey)
    points = getattr(result, field_name)

    assert len(points) == 1
    assert points[0].point_id == PERSON_GAP.information_id
    assert points[0].disposition == disposition
    assert points[0].resolution_id == clarification.resolution.resolution_id
    assert points[0] not in result.known_situation


def test_close_without_change_is_not_fact_or_answer():
    first = build()
    clarification = external(
        first.turns[-1],
        ClarificationResolutionType.CLOSE_WITHOUT_CHANGE,
    )
    current = conversation_input(
        gaps=(AREA_GAP,),
        question=AREA_QUESTION.text,
    )
    journey = build(
        journey_input(
            conversation_input=current,
            gap_bindings=(AREA_BINDING,),
            previous_turns=first.turns,
            clarifications=(clarification,),
        )
    )
    result = present(journey)

    assert result.closed_without_change_points[0].disposition == (
        "CLOSED_WITHOUT_CHANGE"
    )
    assert result.answered_points == ()
    assert all(
        item.text != result.closed_without_change_points[0].text
        for item in result.known_situation
    )


def test_hypotheses_and_contradictions_keep_content_order_and_lifecycle():
    result = present()

    assert tuple(item.text for item in result.known_situation) == (FACT.text,)
    assert tuple(item.text for item in result.hypotheses) == (HYPOTHESIS.text,)
    assert tuple(item.text for item in result.contradictions) == (
        CONTRADICTION.text,
    )
    assert result.hypotheses[0].lifecycle_status == HYPOTHESIS.status.value
    assert result.hypotheses[0].source_references
    assert result.contradictions[0].source_references
    assert HYPOTHESIS.text not in tuple(item.text for item in result.known_situation)


def test_visible_professional_boundaries_cover_all_required_limits():
    text = " ".join(present().professional_boundaries + present().warnings)

    for phrase in (
        "keine Rechtsberatung",
        "weder eine Vorsorgevollmacht",
        "rechtlichen Wirksamkeit",
        "Notare",
        "Ärzte",
        "Steuerberater",
        "Geschäftsfähigkeit",
        "Eignung",
        "ausdrücklich bereitgestellte Angaben",
        "keine automatische Entscheidung",
        "Nutzerantworten nicht automatisch",
        "medizinische oder steuerliche Beratung",
    ):
        assert phrase in text


def test_public_contract_is_exported_and_immutable():
    result = present()

    assert life_decisions.GuardianPowerOfAttorneyExperienceService is (
        GuardianPowerOfAttorneyExperienceService
    )
    assert life_decisions.PowerOfAttorneyJourneyExperience is (
        PowerOfAttorneyJourneyExperience
    )
    with pytest.raises(FrozenInstanceError):
        result.status_heading = "Geändert"


def test_presentation_performs_no_file_write_or_network_access(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("external side effect")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    result = present()

    assert result.journey_id == build().journey_id


def test_stable_german_product_texts_have_no_chatbot_or_sales_language():
    result = present()
    text = " ".join(
        (
            result.status_heading,
            result.status_description,
            result.current_question.why_needed,
        )
        + tuple(item.label for item in result.allowed_actions)
    )

    assert "ich empfehle" not in text.casefold()
    assert "garantiert" not in text.casefold()
    assert "keine Sorge" not in text.casefold()
    assert "als KI" not in text


def test_identical_input_is_deterministic_and_semantic_change_changes_id():
    journey = build()
    first = present(journey)
    second = present(journey)
    changed = present(
        build(
            journey_input(
                conversation_input=conversation_input(
                    gaps=(AREA_GAP, PERSON_GAP),
                    question=AREA_QUESTION.text,
                ),
                gap_bindings=(AREA_BINDING, PERSON_BINDING),
            )
        )
    )

    assert first == second
    assert first.experience_id == second.experience_id
    assert first.experience_id != changed.experience_id
    assert not hasattr(first, "created_at")
    assert not hasattr(first, "timestamp")


def test_service_is_stateless_and_contract_has_no_forbidden_mechanisms():
    service = GuardianPowerOfAttorneyExperienceService()
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
        "profile",
        "llm",
        "network",
        "recommendation",
        "pdf",
        "docx",
    }

    assert service.__dict__ == {}
    assert forbidden.isdisjoint(
        field.name for field in fields(PowerOfAttorneyJourneyExperience)
    )
    before = build()
    present(before)
    assert before == build()
