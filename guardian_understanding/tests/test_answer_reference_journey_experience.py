from dataclasses import replace
import inspect

from guardian_understanding.answer_boundary import AnswerOperatingMode
from guardian_understanding.answer_reference_journey import (
    GuardianAnswerExperienceAction,
    GuardianAnswerExperienceProjector,
)
from guardian_understanding.personal_preparation import (
    OpenQuestionEntry,
    OptionForConsiderationEntry,
    UncertaintyEntry,
)
from guardian_understanding.professional_decision_boundary import UrgencyStatus
from guardian_understanding.source_chain import SourceChainReference
from guardian_understanding import answer_reference_journey as module
from guardian_understanding.tests.test_answer_reference_journey_end_to_end import (
    b1_stage,
    b2_stage,
    b3_stage,
    journey_envelope,
)


PROJECTOR = GuardianAnswerExperienceProjector()


def detailed_complete_journey():
    b1 = b1_stage()
    base_b2 = b2_stage(b1)
    source = base_b2.preparation.source_chain_references[0]
    preparation = replace(
        base_b2.preparation,
        open_questions=(
            OpenQuestionEntry("question-b2", "Bereitgestellte offene Frage.", (source,)),
        ),
        options_for_consideration=(
            OptionForConsiderationEntry(
                "option-b2",
                "Bereitgestellte zu prüfende Option.",
                (source,),
            ),
        ),
        uncertainties=(
            UncertaintyEntry("uncertainty-b2", "Bereitgestellte Unsicherheit.", (source,)),
        ),
    )
    b2 = replace(base_b2, preparation=preparation)
    b3 = b3_stage(
        b1,
        b2,
        urgency=UrgencyStatus.IMMEDIATE_HELP_REQUIRED,
        urgent_help_notice="Bereitgestellter Soforthilfehinweis.",
    )
    return journey_envelope(b1=b1, b2=b2, b3=b3)


def test_complete_experience_projects_existing_objects_and_content_only():
    value = detailed_complete_journey()
    experience = PROJECTOR.project(value, experience_id="experience-1")
    assert experience.journey is value.journey
    assert experience.general_orientation is value.general_orientation.orientation
    assert experience.personal_preparation is value.personal_preparation.preparation
    assert experience.professional_boundary is value.professional_boundary.professional_boundary
    assert experience.known_facts is value.personal_preparation.preparation.known_facts
    assert experience.open_questions is value.personal_preparation.preparation.open_questions
    assert experience.options_for_consideration is value.personal_preparation.preparation.options_for_consideration
    assert experience.uncertainties is value.personal_preparation.preparation.uncertainties
    assert experience.boundary_review_topics is value.professional_boundary.professional_boundary.professional_review_topics
    assert experience.answer_boundaries == (
        value.general_orientation.foundation.boundary_contract,
        value.personal_preparation.foundation.boundary_contract,
        value.professional_boundary.foundation.boundary_contract,
    )
    assert experience.current_protection_level is AnswerOperatingMode.B3_PROFESSIONAL_DECISION_REQUIRED
    assert experience.urgency_status is UrgencyStatus.IMMEDIATE_HELP_REQUIRED
    assert experience.urgent_help_notice == "Bereitgestellter Soforthilfehinweis."
    assert experience.provider_reference == value.journey.provider_reference
    assert experience.limitations == (
        value.general_orientation.orientation.limitations,
        value.professional_boundary.professional_boundary.professional_boundary,
    )


def test_partial_b1_experience_has_no_invented_b2_or_b3_content():
    b1 = b1_stage()
    value = journey_envelope(b1=b1)
    experience = PROJECTOR.project(value, experience_id="experience-b1")
    assert experience.general_orientation is b1.orientation
    assert experience.personal_preparation is None
    assert experience.professional_boundary is None
    assert experience.known_facts == ()
    assert experience.open_questions == ()
    assert experience.options_for_consideration == ()
    assert experience.uncertainties == ()
    assert experience.urgency_status is None
    assert experience.urgent_help_notice is None


def test_sources_remain_original_contract_objects_in_stable_stage_order():
    value = detailed_complete_journey()
    experience = PROJECTOR.project(value, experience_id="experience-sources")
    expected = (
        value.general_orientation.foundation.source_chain_contracts[0],
        value.personal_preparation.foundation.source_chain_contracts[0],
        value.professional_boundary.foundation.source_chain_contracts[0],
    )
    assert experience.source_chain_contracts == expected
    assert all(actual is original for actual, original in zip(experience.source_chain_contracts, expected))


def test_actions_are_declarative_visibility_options_without_execution_methods():
    experience = PROJECTOR.project(
        detailed_complete_journey(),
        experience_id="experience-actions",
    )
    assert experience.available_actions == (
        GuardianAnswerExperienceAction.VIEW_GENERAL_ORIENTATION,
        GuardianAnswerExperienceAction.VIEW_PERSONAL_PREPARATION,
        GuardianAnswerExperienceAction.VIEW_PROFESSIONAL_BOUNDARY,
        GuardianAnswerExperienceAction.ACKNOWLEDGE_BOUNDARY,
        GuardianAnswerExperienceAction.VIEW_SOURCES,
        GuardianAnswerExperienceAction.VIEW_UNCERTAINTIES,
        GuardianAnswerExperienceAction.VIEW_PROFESSIONAL_REVIEW_TOPICS,
    )
    assert all(not callable(action.value) for action in experience.available_actions)


def test_projection_is_deterministic_and_does_not_generate_or_rewrite_text():
    value = detailed_complete_journey()
    first = PROJECTOR.project(value, experience_id="experience-stable")
    second = PROJECTOR.project(value, experience_id="experience-stable")
    assert first == second
    assert first.general_orientation.general_information == value.general_orientation.orientation.general_information
    assert first.personal_preparation.preparation_goal == value.personal_preparation.preparation.preparation_goal
    assert first.professional_boundary.non_confirmation_text == value.professional_boundary.professional_boundary.non_confirmation_text
    source = inspect.getsource(module.GuardianAnswerExperienceProjector)
    for forbidden in ("summarize", "translate", "interpret", "prioritize", "select("):
        assert forbidden not in source
