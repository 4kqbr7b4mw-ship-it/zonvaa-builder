from dataclasses import replace
from pathlib import Path
import socket

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
from life_decisions.conversation import (
    OrganizationalPreparationStep,
    PreparationStepType,
    ProfessionalReviewCategory,
    ProfessionalReviewNeed,
    ReviewNeed,
    UserStatementReference,
)
from life_decisions.conversation_turn import understanding_state_content_hash
from life_decisions.family_care import (
    FamilyCareDependency,
    FamilyCareDomainContributionInput,
    FamilyCareDomainType,
    FamilyCareExternalClarification,
    FamilyCareGapBinding,
    FamilyCareGapType,
    FamilyCareJourneyAction,
    FamilyCareJourneyInput,
    FamilyCareJourneyStatus,
    FamilyCareOpenPoint,
    FamilyCarePersonReference,
    FamilyCarePointStatus,
    FamilyCareSituationInput,
    FamilyCareTextReference,
    GuardianFamilyCareExperienceService,
    GuardianFamilyCareJourneyService,
    GuardianFamilyCarePreparationService,
)
from life_decisions.models import DocumentReference, DocumentType


STATE_ID = "understanding-state-family-care-reference"
TRIGGER = UserStatementReference(
    "statement-family-care-reference-start",
    "Ein älterer Elternteil kehrt nach einem Krankenhausaufenthalt in das eigene Haus zurück; mehrere organisatorische Fragen sind offen.",
    "reference-journey:start",
)
INITIAL_FACTS = (
    Fact("Ein älterer Elternteil wurde aus dem Krankenhaus entlassen."),
    Fact("Die Rückkehr in das eigene Haus ist grundsätzlich vorgesehen."),
    Fact("Mehrere erwachsene Angehörige sind beteiligt."),
)
INITIAL_HYPOTHESES = (
    Hypothesis("Eine kognitive Einschränkung könnte bestehen."),
)
INITIAL_UNKNOWNS = (
    Unknown("Welcher Unterstützungsbedarf besteht nach der Entlassung?"),
    Unknown("Wie sind die Rollen innerhalb der Familie verteilt?"),
    Unknown("Welche Vertretungsgrundlage besteht?"),
    Unknown("Wer übernimmt medizinische Organisation und Nachsorge?"),
    Unknown("Ist die Wohnsituation dauerhaft geeignet?"),
    Unknown("Welche zusätzlichen Kosten und Belastungen bestehen?"),
)
INITIAL_CONTRADICTIONS = (
    Contradiction("Angehörige A beschreibt tägliche Hilfe als nötig. <> Angehörige B hält Unterstützung nur gelegentlich für nötig."),
)
INITIAL_GOALS = (
    Goal("Die familiäre Pflegesituation schrittweise und ohne automatische Entscheidung ordnen."),
)
INITIAL_STATE = UnderstandingState(
    INITIAL_FACTS,
    INITIAL_HYPOTHESES,
    INITIAL_UNKNOWNS,
    INITIAL_CONTRADICTIONS,
    INITIAL_GOALS,
)


POINTS = (
    FamilyCareOpenPoint(
        "family-care-point-reference-support",
        "Der konkrete Unterstützungsbedarf nach der Entlassung ist offen.",
        ("reference-journey:gap:support",),
        (FamilyCareDomainType.CARE_AND_SUPPORT,),
        True,
    ),
    FamilyCareOpenPoint(
        "family-care-point-reference-roles",
        "Die Rollenverteilung unter den Angehörigen ist offen.",
        ("reference-journey:gap:roles",),
        (FamilyCareDomainType.FAMILY_AND_ROLES,),
        True,
    ),
    FamilyCareOpenPoint(
        "family-care-point-reference-representation",
        "Die bestehende Vertretungsgrundlage ist offen.",
        ("reference-journey:gap:representation",),
        (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION,),
        True,
    ),
    FamilyCareOpenPoint(
        "family-care-point-reference-medical",
        "Die medizinische Ansprechperson und Nachsorge sind offen.",
        ("reference-journey:gap:medical",),
        (FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION,),
        True,
    ),
    FamilyCareOpenPoint(
        "family-care-point-reference-housing",
        "Die weitere Eignung der Wohnsituation ist offen.",
        ("reference-journey:gap:housing",),
        (FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,),
        True,
    ),
    FamilyCareOpenPoint(
        "family-care-point-reference-costs",
        "Zusätzliche Kosten und finanzielle Belastungen sind offen.",
        ("reference-journey:gap:costs",),
        (FamilyCareDomainType.FINANCES_AND_COSTS,),
        True,
    ),
)
GAPS = (
    FamilyCareGapType.SUPPORT_NEED,
    FamilyCareGapType.ROLE_DISTRIBUTION,
    FamilyCareGapType.REPRESENTATIVE,
    FamilyCareGapType.MEDICAL_CONTACT,
    FamilyCareGapType.HOUSING_TYPE,
    FamilyCareGapType.FINANCIAL_BURDEN,
)
ANSWERS = (
    "Nach der Entlassung wurden Hilfe bei Mobilität, Mahlzeiten und Medikamentenorganisation ausdrücklich genannt.",
    "Angehörige A koordiniert ausdrücklich Termine; Angehörige B übernimmt ausdrücklich Einkäufe; weitere Verantwortung ist nicht festgelegt.",
    "Eine Vorsorgevollmacht wird als möglicherweise vorhanden referenziert; ihr aktueller Stand und die Vertretungsberechtigung sind ungeklärt.",
    "Die Hausarztpraxis wurde ausdrücklich als medizinische Ansprechstelle genannt; die Nachsorgetermine sind noch nicht vollständig vereinbart.",
    "Das eigene Haus bleibt als Wohnort vorgesehen; ein möglicher Anpassungsbedarf soll ausdrücklich extern geprüft werden.",
    "Laufende Wohnkosten sind bekannt; zusätzliche Pflegekosten und ihre Finanzierung bleiben ausdrücklich offen.",
)
ANSWER_DOMAINS = (
    FamilyCareDomainType.CARE_AND_SUPPORT,
    FamilyCareDomainType.FAMILY_AND_ROLES,
    FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION,
    FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION,
    FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,
    FamilyCareDomainType.FINANCES_AND_COSTS,
)
RESOLUTION_TYPES = (
    ClarificationResolutionType.SELECT_PROPOSAL,
    ClarificationResolutionType.SELECT_PROPOSAL,
    ClarificationResolutionType.KEEP_OPEN,
    ClarificationResolutionType.SELECT_PROPOSAL,
    ClarificationResolutionType.KEEP_OPEN,
    ClarificationResolutionType.KEEP_OPEN,
)


PEOPLE = (
    FamilyCarePersonReference(
        "family-care-person-reference-parent",
        "Elternteil",
        "unterstützungsbedürftige Person",
        "Elternteil des Nutzers",
        ("reference-journey:person:parent",),
    ),
    FamilyCarePersonReference(
        "family-care-person-reference-relative-a",
        "Angehörige A",
        "erwachsene angehörige Person",
        "Angehörige Person",
        ("reference-journey:person:a",),
    ),
    FamilyCarePersonReference(
        "family-care-person-reference-relative-b",
        "Angehörige B",
        "erwachsene angehörige Person",
        "Angehörige Person",
        ("reference-journey:person:b",),
    ),
)
DOCUMENT = DocumentReference(
    "document-family-care-reference-poa",
    DocumentType.POWER_OF_ATTORNEY,
    "user-vault://family-care-reference/poa",
    False,
)
DOMAIN_ENTRIES = {
    domain: FamilyCareTextReference(
        "family-care-text-reference-" + domain.value.lower().replace("_", "-"),
        "Ausdrücklich typisierter Referenzbeitrag für {}.".format(domain.value),
        ("reference-journey:domain:" + domain.value,),
    )
    for domain in FamilyCareDomainType
}
DEPENDENCIES = (
    FamilyCareDependency(
        "family-care-dependency-reference-support-housing",
        POINTS[0].point_id,
        POINTS[4].point_id,
        (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.HOUSING_AND_REAL_ESTATE),
        "Unterstützungsbedarf und Wohnorganisation wurden ausdrücklich verbunden.",
        ("reference-journey:dependency:support-housing",),
    ),
    FamilyCareDependency(
        "family-care-dependency-reference-representation-documents",
        POINTS[2].point_id,
        POINTS[1].point_id,
        (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION, FamilyCareDomainType.FAMILY_AND_ROLES),
        "Vertretungsgrundlage und familiäre Rollen wurden ausdrücklich verbunden.",
        ("reference-journey:dependency:representation-roles",),
    ),
)
REVIEWS = (
    ProfessionalReviewNeed(
        "professional-review-reference-document",
        ProfessionalReviewCategory.EXISTING_DOCUMENTS,
        ReviewNeed.REQUIRED,
        "Die Prüfung der ausdrücklich referenzierten Vorsorgevollmacht wurde angefordert.",
        ("reference-journey:review:document",),
    ),
    ProfessionalReviewNeed(
        "professional-review-reference-medical",
        ProfessionalReviewCategory.MEDICAL,
        ReviewNeed.REQUIRED,
        "Die medizinische Nachsorge soll ausdrücklich fachlich geklärt werden.",
        ("reference-journey:review:medical",),
    ),
    ProfessionalReviewNeed(
        "professional-review-reference-housing",
        ProfessionalReviewCategory.REAL_ESTATE,
        ReviewNeed.RECOMMENDED,
        "Ein ausdrücklich genannter Anpassungsbedarf am Haus soll fachlich geprüft werden.",
        ("reference-journey:review:housing",),
    ),
    ProfessionalReviewNeed(
        "professional-review-reference-financial",
        ProfessionalReviewCategory.FINANCIAL,
        ReviewNeed.REQUIRED,
        "Die ausdrücklich offenen zusätzlichen Kosten sollen fachlich geprüft werden.",
        ("reference-journey:review:financial",),
    ),
)
STEPS = (
    OrganizationalPreparationStep(
        "preparation-step-reference-documents",
        PreparationStepType.OTHER,
        "Die nutzerkontrollierten Dokumentreferenzen für die externe Prüfung bereithalten.",
        ("reference-journey:step:documents",),
    ),
    OrganizationalPreparationStep(
        "preparation-step-reference-appointments",
        PreparationStepType.OTHER,
        "Die ausdrücklich genannten medizinischen Kontakte und Termine zusammenstellen.",
        ("reference-journey:step:appointments",),
    ),
)


def contributions(domain_facts):
    result = []
    for domain in FamilyCareDomainType:
        result.append(
            FamilyCareDomainContributionInput(
                domain,
                facts=tuple(domain_facts.get(domain, ())),
                hypotheses=INITIAL_HYPOTHESES if domain is FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION else (),
                unknowns=INITIAL_UNKNOWS_FOR_DOMAIN[domain],
                contradictions=INITIAL_CONTRADICTIONS if domain is FamilyCareDomainType.FAMILY_AND_ROLES else (),
                explicit_entries=(DOMAIN_ENTRIES[domain],),
                essential_point_ids=tuple(point.point_id for point in POINTS if domain in point.domains),
                professional_reviews=tuple(review for review in REVIEWS if review.category in REVIEW_CATEGORIES_BY_DOMAIN[domain]),
                organizational_steps=STEPS if domain is FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION else (),
                dependency_ids=tuple(item.dependency_id for item in DEPENDENCIES if domain in item.domains),
                professional_boundaries=("Keine automatische Bewertung in {}.".format(domain.value),),
            )
        )
    return tuple(result)


INITIAL_UNKNOWS_FOR_DOMAIN = {
    FamilyCareDomainType.CARE_AND_SUPPORT: (INITIAL_UNKNOWNS[0],),
    FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION: (INITIAL_UNKNOWNS[3],),
    FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION: (INITIAL_UNKNOWNS[2],),
    FamilyCareDomainType.HOUSING_AND_REAL_ESTATE: (INITIAL_UNKNOWNS[4],),
    FamilyCareDomainType.FINANCES_AND_COSTS: (INITIAL_UNKNOWNS[5],),
    FamilyCareDomainType.FAMILY_AND_ROLES: (INITIAL_UNKNOWNS[1],),
    FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION: (INITIAL_UNKNOWNS[2],),
}
REVIEW_CATEGORIES_BY_DOMAIN = {
    FamilyCareDomainType.CARE_AND_SUPPORT: (),
    FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION: (ProfessionalReviewCategory.MEDICAL,),
    FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION: (ProfessionalReviewCategory.EXISTING_DOCUMENTS,),
    FamilyCareDomainType.HOUSING_AND_REAL_ESTATE: (ProfessionalReviewCategory.REAL_ESTATE,),
    FamilyCareDomainType.FINANCES_AND_COSTS: (ProfessionalReviewCategory.FINANCIAL,),
    FamilyCareDomainType.FAMILY_AND_ROLES: (),
    FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION: (ProfessionalReviewCategory.EXISTING_DOCUMENTS,),
}


def situation(state, statements, domain_facts):
    source = FamilyCareSituationInput(
        STATE_ID,
        state,
        TRIGGER.statement_id,
        tuple(statements),
        state.facts,
        state.goals,
        state.hypotheses,
        state.unknowns,
        state.contradictions,
        PEOPLE,
        (DOMAIN_ENTRIES[FamilyCareDomainType.CARE_AND_SUPPORT],),
        (DOMAIN_ENTRIES[FamilyCareDomainType.HOUSING_AND_REAL_ESTATE],),
        (DOMAIN_ENTRIES[FamilyCareDomainType.FINANCES_AND_COSTS],),
        (
            DOMAIN_ENTRIES[FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION],
            DOMAIN_ENTRIES[FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION],
            DOMAIN_ENTRIES[FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION],
        ),
        (DOCUMENT,),
        POINTS,
        DEPENDENCIES,
        contributions(domain_facts),
        REVIEWS,
        STEPS,
    )
    return GuardianFamilyCarePreparationService().prepare(source)


def build_reference_journey():
    proposal_service = GuardianUnderstandingProposalService()
    resolution_service = GuardianClarificationResolutionService(proposal_service)
    journey_service = GuardianFamilyCareJourneyService()
    state = INITIAL_STATE
    statements = [TRIGGER]
    turns = []
    clarifications = []
    proposal_sets = []
    resolution_results = []
    journeys = []
    domain_facts = {
        FamilyCareDomainType.CARE_AND_SUPPORT: (INITIAL_FACTS[0],),
        FamilyCareDomainType.HOUSING_AND_REAL_ESTATE: (INITIAL_FACTS[1],),
        FamilyCareDomainType.FAMILY_AND_ROLES: (INITIAL_FACTS[2],),
    }
    bindings = tuple(FamilyCareGapBinding(point.point_id, gap) for point, gap in zip(POINTS, GAPS))

    for index, (point, answer_text, domain, resolution_type) in enumerate(
        zip(POINTS, ANSWERS, ANSWER_DOMAINS, RESOLUTION_TYPES), 1
    ):
        current = situation(state, statements, domain_facts)
        current_journey = journey_service.build(
            FamilyCareJourneyInput(current, bindings, tuple(turns), tuple(clarifications))
        )
        assert current_journey.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION
        assert current_journey.current_open_point.point_id == point.point_id
        assert current_journey.current_question is not None
        turn = current_journey.turns[-1]
        answer = UserStatementReference(
            "statement-family-care-reference-answer-{}".format(index),
            answer_text,
            "reference-journey:answer:{}".format(index),
        )
        candidate = UnderstandingProposalCandidate(
            UnderstandingOperation(UnderstandingOperationType.ADD_FACT, value_text=answer_text),
            answer.source_reference,
            "Die typisierte Antwort kann ausschließlich als ausdrücklich ausgewählte Tatsache ergänzt werden.",
        )
        proposal_set = proposal_service.create(
            state,
            answer.statement_id,
            answer.text,
            (candidate,),
            current_journey.current_question.text,
            current_journey.current_question.question_id,
        )
        selected = proposal_set.proposals[0]
        request = ClarificationResolutionRequest(
            proposal_set.understanding_question_id,
            answer.statement_id,
            answer.text,
            (selected.proposal_id,),
            resolution_type,
            answer.source_reference,
            (
                "Die vorhandene Proposal-Operation wurde ausdrücklich ausgewählt."
                if resolution_type is ClarificationResolutionType.SELECT_PROPOSAL
                else "Der Punkt bleibt ausdrücklich offen und wird nicht als geklärt behandelt."
            ),
            selected.proposal_id if resolution_type is ClarificationResolutionType.SELECT_PROPOSAL else None,
            "Welche ausdrücklich typisierte Angabe soll den weiterhin offenen Punkt klären?"
            if resolution_type is ClarificationResolutionType.KEEP_OPEN
            else None,
        )
        resolution_result = resolution_service.resolve(state, proposal_set, request)
        if resolution_type is ClarificationResolutionType.SELECT_PROPOSAL:
            revision = resolution_result.application.revision
            external = FamilyCareExternalClarification(
                turn.turn_id,
                answer,
                resolution_result.resolution,
                revision,
                "understanding-revision-family-care-reference-{}".format(index),
                STATE_ID,
                understanding_state_content_hash(revision.state),
            )
            state = revision.state
            domain_facts[domain] = domain_facts.get(domain, ()) + (Fact(answer_text),)
        else:
            external = FamilyCareExternalClarification(turn.turn_id, answer, resolution_result.resolution)
        turns.append(turn)
        clarifications.append(external)
        statements.append(answer)
        proposal_sets.append(proposal_set)
        resolution_results.append(resolution_result)
        journeys.append(current_journey)

    final_situation = situation(state, statements, domain_facts)
    final_journey = journey_service.build(
        FamilyCareJourneyInput(
            final_situation,
            bindings,
            tuple(turns),
            tuple(clarifications),
            create_review_preparation=True,
        )
    )
    experience = GuardianFamilyCareExperienceService().present(final_journey)
    return {
        "state": state,
        "statements": tuple(statements),
        "turns": tuple(turns),
        "clarifications": tuple(clarifications),
        "proposal_sets": tuple(proposal_sets),
        "resolution_results": tuple(resolution_results),
        "journeys": tuple(journeys),
        "situation": final_situation,
        "journey": final_journey,
        "experience": experience,
        "bindings": bindings,
    }


def test_six_controlled_turns_use_existing_end_to_end_contracts():
    reference = build_reference_journey()

    assert len(reference["turns"]) == 6
    assert len(reference["proposal_sets"]) == 6
    assert len(reference["clarifications"]) == 6
    assert tuple(item.current_open_point.point_id for item in reference["journeys"]) == tuple(item.point_id for item in POINTS)
    assert all(item.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION for item in reference["journeys"])
    assert all(item.current_question is not None for item in reference["journeys"])
    assert len({item.current_question.question_id for item in reference["journeys"]}) == 6
    assert tuple(turn.previous_turn_id for turn in reference["turns"]) == (None,) + tuple(turn.turn_id for turn in reference["turns"][:-1])


def test_every_turn_preserves_complete_source_chain_and_unchanged_operation():
    reference = build_reference_journey()

    for index, (turn, proposal_set, result, external) in enumerate(
        zip(reference["turns"], reference["proposal_sets"], reference["resolution_results"], reference["clarifications"]),
        1,
    ):
        answer = reference["statements"][index]
        selected = proposal_set.proposals[0]
        assert turn.point_id == POINTS[index - 1].point_id
        assert turn.question_id == proposal_set.understanding_question_id
        assert proposal_set.statement_id == answer.statement_id
        assert proposal_set.user_statement == answer.text
        assert selected.source_reference == answer.source_reference
        assert result.resolution.resolution_type is RESOLUTION_TYPES[index - 1]
        assert external.answer_statement is answer
        if result.resolution.resolution_type is ClarificationResolutionType.SELECT_PROPOSAL:
            assert result.resolution.selected_proposal_id == selected.proposal_id
            assert result.resolution.selected_operation is selected.operation
            assert external.revision is result.application.revision
            assert external.resulting_understanding_state_hash == understanding_state_content_hash(external.revision.state)
        else:
            assert result.application is None
            assert external.revision is None
            assert external.resulting_understanding_state_hash is None


def test_final_journey_review_and_experience_are_consistent_and_bounded():
    reference = build_reference_journey()
    journey = reference["journey"]
    experience = reference["experience"]

    assert journey.status is FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY
    assert journey.next_action is FamilyCareJourneyAction.USE_REVIEW_PACKAGE
    assert journey.current_question is None
    assert len(journey.answered_by_revision_points) == 3
    assert all(item.status is FamilyCarePointStatus.ANSWERED_BY_REVISION for item in journey.answered_by_revision_points)
    assert journey.deferred_points == (POINTS[2], POINTS[4], POINTS[5])
    assert journey.essential_open_points == ()
    assert journey.professional_review.professional_reviews == REVIEWS
    assert experience.current_question is None
    assert experience.professional_review is journey.professional_review
    assert experience.contradictions == INITIAL_CONTRADICTIONS
    assert experience.hypotheses == INITIAL_HYPOTHESES
    assert experience.dependencies == DEPENDENCIES
    assert experience.organizational_steps == STEPS
    assert len(experience.contributions) == len(FamilyCareDomainType)
    assert not hasattr(experience, "ranking")
    assert not hasattr(experience, "recommendations")


def test_no_question_is_repeated_or_skipped_and_only_one_is_visible():
    reference = build_reference_journey()
    for expected_index, journey in enumerate(reference["journeys"]):
        assert journey.current_open_point == POINTS[expected_index]
        assert journey.current_question.point_id == POINTS[expected_index].point_id
        assert sum(item is not None for item in (journey.current_question,)) == 1
        expected_answered = tuple(
            point.point_id
            for point, resolution_type in zip(POINTS[:expected_index], RESOLUTION_TYPES[:expected_index])
            if resolution_type is ClarificationResolutionType.SELECT_PROPOSAL
        )
        assert tuple(item.point_id for item in journey.answered_by_revision_points) == expected_answered
    assert reference["journey"].current_question is None


def test_answers_proposals_and_resolutions_never_change_state_automatically():
    proposals = GuardianUnderstandingProposalService()
    answer = UserStatementReference("statement-family-care-reference-safety", "Eine ausdrücklich typisierte Testantwort.", "reference-journey:safety")
    candidate = UnderstandingProposalCandidate(
        UnderstandingOperation(UnderstandingOperationType.ADD_FACT, value_text=answer.text),
        answer.source_reference,
        "Eine nicht autoritative mögliche Operation.",
    )
    proposal_set = proposals.create(INITIAL_STATE, answer.statement_id, answer.text, (candidate,), "Welche Angabe wurde ausdrücklich bestätigt?", "understanding-question-family-care-safety")

    assert INITIAL_STATE.facts == INITIAL_FACTS
    assert not hasattr(proposal_set, "revision")
    assert proposal_set.proposals[0].changes_state is False


def test_missing_revision_foreign_proposal_and_duplicate_resolution_are_blocked():
    reference = build_reference_journey()
    first = reference["clarifications"][0]
    missing = replace(first, revision=None, revision_reference=None, resulting_understanding_state_id=None, resulting_understanding_state_hash=None)
    blocked = GuardianFamilyCareJourneyService().build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], reference["turns"], (missing,))
    )
    assert blocked.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "PARTIAL_EXTERNAL_ARTIFACT_CHAIN" in blocked.blockers

    proposals = reference["proposal_sets"][0]
    with pytest.raises(ValueError, match="does not belong"):
        GuardianClarificationResolutionService().resolve(
            INITIAL_STATE,
            proposals,
            ClarificationResolutionRequest(
                proposals.understanding_question_id,
                "statement-family-care-reference-foreign-answer",
                "Fremde Antwort.",
                ("understanding-proposal-foreign",),
                ClarificationResolutionType.SELECT_PROPOSAL,
                "reference-journey:foreign",
                "Fremde Auswahl.",
                "understanding-proposal-foreign",
            ),
        )

    duplicate = GuardianFamilyCareJourneyService().build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], reference["turns"], (first, first))
    )
    assert duplicate.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "DUPLICATE_TURN_CLARIFICATION" in duplicate.blockers

    other_answer = UserStatementReference(
        "statement-family-care-reference-duplicate-answer",
        "Eine zweite typisierte Antwort auf dieselbe Frage.",
        "reference-journey:duplicate-answer",
    )
    other_resolution = replace(
        first.resolution,
        answer_statement_id=other_answer.statement_id,
        answer_text=other_answer.text,
        source_reference=other_answer.source_reference,
    )
    duplicate_answer = replace(
        first,
        answer_statement=other_answer,
        resolution=other_resolution,
    )
    blocked_duplicate_answer = GuardianFamilyCareJourneyService().build(
        FamilyCareJourneyInput(
            reference["situation"],
            reference["bindings"],
            reference["turns"],
            (first, duplicate_answer),
        )
    )
    assert blocked_duplicate_answer.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "DUPLICATE_TURN_CLARIFICATION" in blocked_duplicate_answer.blockers


def test_missing_turn_wrong_order_foreign_statement_and_broken_revision_chain_are_blocked():
    reference = build_reference_journey()
    service = GuardianFamilyCareJourneyService()
    missing_turn = service.build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], reference["turns"][1:], reference["clarifications"])
    )
    assert missing_turn.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    wrong_order = service.build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], reference["turns"], tuple(reversed(reference["clarifications"])))
    )
    assert wrong_order.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "CLARIFICATION_ORDER_MISMATCH" in wrong_order.blockers

    foreign_resolution = replace(reference["clarifications"][0].resolution, proposal_statement_id="statement-family-care-reference-foreign")
    foreign = replace(reference["clarifications"][0], resolution=foreign_resolution)
    blocked = service.build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], reference["turns"], (foreign,))
    )
    assert blocked.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "PROPOSAL_ORIGIN_MISMATCH" in blocked.blockers

    broken_turn = replace(reference["turns"][1], understanding_state_hash="0" * 64)
    broken = service.build(
        FamilyCareJourneyInput(reference["situation"], reference["bindings"], (reference["turns"][0], broken_turn) + reference["turns"][2:], reference["clarifications"])
    )
    assert broken.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "REVISION_CHAIN_MISMATCH" in broken.blockers


def test_foreign_review_and_inconsistent_experience_are_rejected():
    reference = build_reference_journey()
    journey = reference["journey"]
    foreign_package = replace(journey.professional_review, journey_id="family-care-journey-foreign")
    with pytest.raises(ValueError, match="professional review mismatch"):
        GuardianFamilyCareExperienceService().present(replace(journey, professional_review=foreign_package))
    with pytest.raises(ValueError, match="requires controlled question"):
        GuardianFamilyCareExperienceService().present(
            replace(journey, status=FamilyCareJourneyStatus.NEEDS_CLARIFICATION, professional_review=None)
        )


def test_identical_reference_input_is_deterministic_and_has_no_side_effects(monkeypatch):
    first = build_reference_journey()
    second = build_reference_journey()
    assert first == second
    assert first["journey"].journey_id == second["journey"].journey_id
    assert first["experience"].experience_id == second["experience"].experience_id

    def forbidden(*_args, **_kwargs):
        raise AssertionError("side effect")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    build_reference_journey()
    assert not hasattr(first["experience"], "route")
    assert not hasattr(first["experience"], "execute")
