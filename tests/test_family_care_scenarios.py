from dataclasses import replace
from pathlib import Path
import socket
from typing import NamedTuple, Tuple

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
from life_decisions.conversation import (
    OrganizationalPreparationStep,
    PreparationStepType,
    ProfessionalReviewCategory,
    ProfessionalReviewNeed,
    ReviewNeed,
    UserStatementReference,
)
from life_decisions.family_care import (
    FamilyCareDependency,
    FamilyCareDomainContributionInput,
    FamilyCareDomainType,
    FamilyCareExperienceActionType,
    FamilyCareExternalClarification,
    FamilyCareGapBinding,
    FamilyCareGapType,
    FamilyCareJourneyAction,
    FamilyCareJourneyInput,
    FamilyCareJourneyStatus,
    FamilyCareOpenPoint,
    FamilyCarePointStatus,
    FamilyCareProfessionalReviewPreparation,
    FamilyCareSituationInput,
    FamilyCareTextReference,
    GuardianFamilyCareExperienceService,
    GuardianFamilyCareJourneyService,
    GuardianFamilyCarePreparationService,
)
from life_decisions.models import DocumentReference, DocumentType

from tests.test_family_care_cross_domain import (
    ANSWER,
    BINDING,
    FACT,
    POINT_SUPPORT,
    STATE,
    TRIGGER,
    prepare as base_prepare,
    journey as base_journey,
)


class Scenario(NamedTuple):
    slug: str
    facts: Tuple[str, ...]
    goals: Tuple[str, ...]
    hypotheses: Tuple[str, ...]
    unknowns: Tuple[str, ...]
    contradictions: Tuple[str, ...]
    domains: Tuple[FamilyCareDomainType, ...]
    gaps: Tuple[Tuple[FamilyCareGapType, Tuple[FamilyCareDomainType, ...]], ...]
    reviews: Tuple[Tuple[ProfessionalReviewCategory, str], ...] = ()
    dependency: bool = False
    document_type: DocumentType = None


SCENARIOS = (
    Scenario(
        "hospital-discharge",
        ("Eine nahestehende Person wurde nach einem Krankenhausaufenthalt entlassen.",),
        ("Die weitere Organisation sachlich vorbereiten.",), (),
        ("Die Versorgung nach der Entlassung ist ungeklärt.",), (),
        (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION, FamilyCareDomainType.HOUSING_AND_REAL_ESTATE, FamilyCareDomainType.FAMILY_AND_ROLES),
        ((FamilyCareGapType.SUPPORT_NEED, (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION)), (FamilyCareGapType.ROLE_DISTRIBUTION, (FamilyCareDomainType.FAMILY_AND_ROLES,))),
        dependency=True,
    ),
    Scenario(
        "caregiver-overload",
        ("Eine angehörige Person übernimmt bereits Pflege und hat eigene Überlastung ausdrücklich benannt.",),
        ("Die bestehende Organisation überprüfen.",), (),
        ("Die künftige Rollenverteilung ist offen.",), (),
        (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.FAMILY_AND_ROLES, FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION),
        ((FamilyCareGapType.ROLE_DISTRIBUTION, (FamilyCareDomainType.FAMILY_AND_ROLES,)),),
        ((ProfessionalReviewCategory.CARE, "pflegefachliche Beratung"), (ProfessionalReviewCategory.FAMILY_AND_ROLES, "Familien- oder Rollenklärung")),
    ),
    Scenario(
        "unclear-representation",
        ("Ein Elternteil benötigt Unterstützung.",), ("Vertretungsfragen klären.",), (),
        ("Eine vertretungsberechtigte Person ist nicht belegt.",),
        ("Eine Vollmacht wird als vorhanden und zugleich als unbekannt beschrieben.",),
        (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION, FamilyCareDomainType.FAMILY_AND_ROLES, FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION),
        ((FamilyCareGapType.REPRESENTATIVE, (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION,)),),
        ((ProfessionalReviewCategory.LEGAL, "rechtliche Prüfung"),), False, DocumentType.POWER_OF_ATTORNEY,
    ),
    Scenario(
        "family-dispute",
        ("Mehrere Angehörige haben unterschiedliche Vorstellungen zur Versorgung genannt.",),
        ("Die Aussagen getrennt sichtbar halten.",), (),
        ("Die Rollenverteilung ist offen.",),
        ("Eine Person befürwortet häusliche Unterstützung; eine andere lehnt sie ab.", "Die Kosten werden als tragbar und zugleich als ungeklärt bezeichnet."),
        (FamilyCareDomainType.FAMILY_AND_ROLES, FamilyCareDomainType.FINANCES_AND_COSTS, FamilyCareDomainType.CARE_AND_SUPPORT),
        ((FamilyCareGapType.ROLE_DISTRIBUTION, (FamilyCareDomainType.FAMILY_AND_ROLES,)),),
    ),
    Scenario(
        "own-house",
        ("Die unterstützungsbedürftige Person lebt im eigenen Haus.",),
        ("Die Wohnorganisation prüfen.",), (), ("Mögliche Barrieren sind ungeklärt.",), (),
        (FamilyCareDomainType.HOUSING_AND_REAL_ESTATE, FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.FINANCES_AND_COSTS),
        ((FamilyCareGapType.HOUSING_TYPE, (FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,)),),
        ((ProfessionalReviewCategory.REAL_ESTATE, "ausdrücklich gewünschte Immobilienprüfung"),),
    ),
    Scenario(
        "possible-stationary-move",
        ("Ein möglicher Umzug in eine stationäre Einrichtung wurde angesprochen.",),
        ("Die offenen Grundlagen ohne Vorauswahl sammeln.",),
        ("Ein Umzug könnte erwogen werden.",), ("Der konkrete Unterstützungsbedarf ist offen.", "Die finanzielle Tragbarkeit ist offen."), (),
        (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.HOUSING_AND_REAL_ESTATE, FamilyCareDomainType.FINANCES_AND_COSTS, FamilyCareDomainType.FAMILY_AND_ROLES),
        ((FamilyCareGapType.SUPPORT_NEED, (FamilyCareDomainType.CARE_AND_SUPPORT,)), (FamilyCareGapType.FINANCIAL_BURDEN, (FamilyCareDomainType.FINANCES_AND_COSTS,))),
        dependency=True,
    ),
    Scenario(
        "medical-uncertainty",
        (), ("Medizinische Angaben fachlich klären lassen.",),
        ("Eine kognitive Einschränkung oder Demenz wird vermutet.",),
        ("Eine medizinische Ansprechperson ist nicht bekannt.",), (),
        (FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION, FamilyCareDomainType.CARE_AND_SUPPORT),
        ((FamilyCareGapType.MEDICAL_CONTACT, (FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION,)),),
        ((ProfessionalReviewCategory.MEDICAL, "ärztliche Klärung"),),
    ),
    Scenario(
        "several-relatives",
        ("Drei Angehörige haben jeweils eigene Aussagen abgegeben.",),
        ("Die Aussagen quellengetrennt erfassen.",), (), ("Die Rollenverteilung ist offen.",),
        ("Angehörige A benennt Angehörige B; Angehörige C widerspricht dieser Rollenangabe.",),
        (FamilyCareDomainType.FAMILY_AND_ROLES,),
        ((FamilyCareGapType.ROLE_DISTRIBUTION, (FamilyCareDomainType.FAMILY_AND_ROLES,)),),
    ),
    Scenario(
        "documents-unclear",
        ("Eine ältere Vorsorgevollmacht wurde als Referenz benannt.",),
        ("Den Stand vorhandener Dokumente extern prüfen lassen.",), (),
        ("Bearbeitungsstand und Wirksamkeit des Dokuments sind unbekannt.",), (),
        (FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION, FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION),
        ((FamilyCareGapType.DOCUMENTS, (FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION,)),),
        ((ProfessionalReviewCategory.EXISTING_DOCUMENTS, "Dokumentprüfung"),), False, DocumentType.POWER_OF_ATTORNEY,
    ),
    Scenario(
        "multiple-essential-gaps",
        ("Mehrere organisatorische Grundlagen fehlen gleichzeitig.",),
        ("Die Lücken nacheinander klären.",), (),
        ("Unterstützungsbedarf und finanzielle Belastung sind offen.",), (),
        (FamilyCareDomainType.CARE_AND_SUPPORT, FamilyCareDomainType.FINANCES_AND_COSTS),
        ((FamilyCareGapType.SUPPORT_NEED, (FamilyCareDomainType.CARE_AND_SUPPORT,)), (FamilyCareGapType.FINANCIAL_BURDEN, (FamilyCareDomainType.FINANCES_AND_COSTS,))),
    ),
    Scenario(
        "answered-gap",
        ("Ein Unterstützungsbedarf wurde ausdrücklich bestätigt.",),
        ("Nur verbleibende Lücken weiter klären.",), (), (), (),
        (FamilyCareDomainType.CARE_AND_SUPPORT,),
        ((FamilyCareGapType.SUPPORT_NEED, (FamilyCareDomainType.CARE_AND_SUPPORT,)),),
    ),
    Scenario(
        "self-appointed-representative",
        ("Eine Person hat sich selbst als allein entscheidungsbefugt bezeichnet.",),
        ("Die Vertretungsgrundlage ohne Personenbewertung klären.",), (),
        ("Eine belegte Vertretungsgrundlage fehlt.",), (),
        (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION, FamilyCareDomainType.FAMILY_AND_ROLES),
        ((FamilyCareGapType.REPRESENTATIVE, (FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION, FamilyCareDomainType.FAMILY_AND_ROLES)),),
        ((ProfessionalReviewCategory.ABUSE_OR_CONFLICT, "ausdrücklich gewünschte Interessenkonfliktprüfung"),),
    ),
)


def build_scenario(scenario: Scenario):
    facts = tuple(Fact(text) for text in scenario.facts)
    goals = tuple(Goal(text) for text in scenario.goals)
    hypotheses = tuple(Hypothesis(text) for text in scenario.hypotheses)
    unknowns = tuple(Unknown(text) for text in scenario.unknowns)
    contradictions = tuple(Contradiction(text) for text in scenario.contradictions)
    state = UnderstandingState(facts, hypotheses, unknowns, contradictions, goals)
    statement = UserStatementReference(
        "statement-family-care-scenario-" + scenario.slug,
        "Anonymisierte typisierte Eingabe für " + scenario.slug + ".",
        "scenario:" + scenario.slug,
    )
    points = tuple(
        FamilyCareOpenPoint(
            "family-care-point-{}-{}".format(scenario.slug, gap.value.lower().replace("_", "-")),
            "Die typisierte Angabe {} ist offen.".format(gap.value),
            ("scenario:{}:gap:{}".format(scenario.slug, gap.value),),
            domains,
            True,
        )
        for gap, domains in scenario.gaps
    )
    entries = {
        domain: FamilyCareTextReference(
            "family-care-text-{}-{}".format(scenario.slug, domain.value.lower().replace("_", "-")),
            "Ausdrücklich typisierter Beitrag für {}.".format(domain.value),
            ("scenario:{}:domain:{}".format(scenario.slug, domain.value),),
        )
        for domain in scenario.domains
    }
    dependencies = ()
    if scenario.dependency:
        dependencies = (
            FamilyCareDependency(
                "family-care-dependency-" + scenario.slug,
                points[0].point_id,
                points[1].point_id,
                tuple(dict.fromkeys(points[0].domains + points[1].domains)),
                "Die ausdrücklich typisierten offenen Punkte wurden miteinander verbunden.",
                ("scenario:{}:dependency".format(scenario.slug),),
            ),
        )
    contributions = tuple(
        FamilyCareDomainContributionInput(
            domain,
            facts=facts if index == 0 else (),
            goals=goals if index == 0 else (),
            hypotheses=hypotheses if index == 0 else (),
            unknowns=unknowns if index == 0 else (),
            contradictions=contradictions if index == 0 else (),
            explicit_entries=(entries[domain],),
            essential_point_ids=tuple(point.point_id for point in points if domain in point.domains),
            dependency_ids=tuple(item.dependency_id for item in dependencies if domain in item.domains),
            professional_boundaries=("Keine automatische fachliche Bewertung in {}.".format(domain.value),),
        )
        for index, domain in enumerate(scenario.domains)
    )
    reviews = tuple(
        ProfessionalReviewNeed(
            "professional-review-{}-{}".format(scenario.slug, index),
            category,
            ReviewNeed.REQUIRED,
            label,
            ("scenario:{}:review:{}".format(scenario.slug, index),),
        )
        for index, (category, label) in enumerate(scenario.reviews, 1)
    )
    steps = (
        OrganizationalPreparationStep(
            "preparation-step-" + scenario.slug,
            PreparationStepType.OTHER,
            "Den ausdrücklich genannten Sachstand für das Fachgespräch bereithalten.",
            ("scenario:{}:step".format(scenario.slug),),
        ),
    )
    documents = ()
    if scenario.document_type is not None:
        documents = (
            DocumentReference(
                "document-family-care-scenario-" + scenario.slug,
                scenario.document_type,
                "user-vault://family-care/" + scenario.slug,
                False,
            ),
        )
    source = FamilyCareSituationInput(
        "understanding-state-family-care-scenario-" + scenario.slug,
        state,
        statement.statement_id,
        (statement,),
        facts,
        goals,
        hypotheses,
        unknowns,
        contradictions,
        (),
        tuple(entries[domain] for domain in scenario.domains if domain is FamilyCareDomainType.CARE_AND_SUPPORT),
        tuple(entries[domain] for domain in scenario.domains if domain is FamilyCareDomainType.HOUSING_AND_REAL_ESTATE),
        tuple(entries[domain] for domain in scenario.domains if domain is FamilyCareDomainType.FINANCES_AND_COSTS),
        tuple(entries[domain] for domain in scenario.domains if domain in (FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION, FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION, FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION)),
        documents,
        points,
        dependencies,
        contributions,
        reviews,
        steps,
    )
    situation = GuardianFamilyCarePreparationService().prepare(source)
    bindings = tuple(FamilyCareGapBinding(point.point_id, gap) for point, (gap, _domains) in zip(points, scenario.gaps))
    journey = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(situation, bindings))
    experience = GuardianFamilyCareExperienceService().present(journey)
    return source, situation, journey, experience


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item.slug)
def test_anonymized_family_care_scenarios_preserve_only_explicit_content(scenario):
    source, situation, journey, experience = build_scenario(scenario)

    assert situation.facts == source.facts
    assert situation.goals == source.goals
    assert situation.hypotheses == source.hypotheses
    assert situation.unknowns == source.unknowns
    assert situation.contradictions == source.contradictions
    assert tuple(item.domain for item in situation.contributions) == scenario.domains
    assert situation.dependencies == source.dependencies
    assert journey.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION
    assert journey.current_open_point == situation.open_points[0]
    assert journey.current_question.point_id == situation.open_points[0].point_id
    assert len(tuple(item for item in (experience.current_question,) if item is not None)) == 1
    assert experience.contributions == situation.contributions
    assert experience.dependencies == situation.dependencies
    assert experience.professional_reviews == source.professional_reviews
    assert situation.understanding_state == source.understanding_state


def test_scenario_specific_safety_claims_remain_mechanical_and_uninterpreted():
    by_name = {item.slug: build_scenario(item) for item in SCENARIOS}

    medical = by_name["medical-uncertainty"][1]
    assert medical.facts == ()
    assert medical.hypotheses[0].text.startswith("Eine kognitive Einschränkung")
    dispute = by_name["family-dispute"][1]
    assert len(dispute.contradictions) == 2
    assert not hasattr(dispute, "preferred_person")
    house = by_name["own-house"][1]
    assert not hasattr(house, "renovation_cost")
    move = by_name["possible-stationary-move"][1]
    assert not hasattr(move, "recommended_care_setting")
    documents = by_name["documents-unclear"][1]
    assert documents.documents[0].storage_reference.startswith("user-vault://")
    assert not hasattr(documents, "document_contents")
    abuse = by_name["self-appointed-representative"][1]
    assert not hasattr(abuse, "abuse_detected")
    assert abuse.professional_reviews[0].reason == "ausdrücklich gewünschte Interessenkonfliktprüfung"
    overload = by_name["caregiver-overload"][1]
    assert tuple(item.category for item in overload.professional_reviews) == (
        ProfessionalReviewCategory.CARE,
        ProfessionalReviewCategory.FAMILY_AND_ROLES,
    )


def test_multiple_essential_gaps_follow_input_order_and_never_create_second_question():
    scenario = next(item for item in SCENARIOS if item.slug == "multiple-essential-gaps")
    source, _situation, first, first_experience = build_scenario(scenario)
    reversed_source = replace(
        source,
        open_points=tuple(reversed(source.open_points)),
        contribution_inputs=tuple(
            replace(item, essential_point_ids=tuple(reversed(item.essential_point_ids)))
            for item in source.contribution_inputs
        ),
    )
    reversed_situation = GuardianFamilyCarePreparationService().prepare(reversed_source)
    bindings = tuple(
        FamilyCareGapBinding(point.point_id, gap)
        for point, (gap, _domains) in zip(reversed_situation.open_points, reversed(scenario.gaps))
    )
    second = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(reversed_situation, bindings))

    assert first.current_open_point == source.open_points[0]
    assert second.current_open_point == reversed_source.open_points[0]
    assert first.current_question != second.current_question
    assert first_experience.current_question == first.current_question


def test_empty_but_formally_valid_case_stays_empty_and_ready():
    statement = UserStatementReference("statement-family-care-empty", "Es wurden noch keine fachlichen Angaben übergeben.", "scenario:empty")
    state = UnderstandingState((), (), (), (), ())
    source = FamilyCareSituationInput(
        "understanding-state-family-care-empty", state, statement.statement_id,
        (statement,), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (), (),
    )
    situation = GuardianFamilyCarePreparationService().prepare(source)
    journey = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(situation, ()))

    assert situation.contributions == ()
    assert situation.dependencies == ()
    assert journey.status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY
    assert journey.current_question is None


def test_empty_domain_contribution_is_rejected_as_unsubstantiated_activation():
    with pytest.raises(ValueError, match="explicit content"):
        FamilyCareDomainContributionInput(FamilyCareDomainType.FINANCES_AND_COSTS)


def test_dependency_cannot_name_a_domain_without_an_explicit_contribution():
    source, _situation, _journey, _experience = build_scenario(SCENARIOS[0])
    contributions = tuple(item for item in source.contribution_inputs if item.domain is not FamilyCareDomainType.FAMILY_AND_ROLES)
    with pytest.raises(ValueError, match="dependency domain"):
        replace(source, contribution_inputs=contributions)


def test_foreign_gap_duplicate_clarification_and_incomplete_history_are_blocked():
    first = base_journey()
    foreign = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(base_prepare(), (FamilyCareGapBinding("family-care-point-foreign", FamilyCareGapType.SUPPORT_NEED),)))
    assert foreign.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    unresolved = ClarificationResolution(
        "clarification-resolution-family-care-scenario-open", TRIGGER.statement_id,
        TRIGGER.text, first.turns[0].question_id, first.turns[0].question,
        ANSWER.statement_id, ANSWER.text, ("understanding-proposal-family-care",),
        ClarificationResolutionType.KEEP_OPEN, ANSWER.source_reference,
        "Der Punkt bleibt ausdrücklich offen.", None, None,
        "Welche Angabe möchten Sie später ausdrücklich klären?",
    )
    clarification = FamilyCareExternalClarification(first.turns[0].turn_id, ANSWER, unresolved)
    duplicate = base_journey(previous_turns=first.turns, clarifications=(clarification, clarification))
    assert duplicate.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    broken_turn = replace(first.turns[0], previous_turn_id="family-care-turn-missing")
    broken = base_journey(previous_turns=(broken_turn,))
    assert broken.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS


def test_foreign_proposal_origin_and_contradictory_revision_are_blocked():
    first = base_journey()
    turn = first.turns[0]
    operation = UnderstandingOperation(UnderstandingOperationType.CONFIRM_FACT, FACT.text, FACT.text)
    resolution = ClarificationResolution(
        "clarification-resolution-family-care-scenario-selected",
        "statement-foreign-proposal-origin", "Fremde Aussage.", turn.question_id,
        turn.question, ANSWER.statement_id, ANSWER.text,
        ("understanding-proposal-family-care-scenario",),
        ClarificationResolutionType.SELECT_PROPOSAL, ANSWER.source_reference,
        "Ausdrücklich übergebene Auswahl.",
        "understanding-proposal-family-care-scenario", operation, None,
    )
    revision = UnderstandingRevision(
        STATE,
        (UnderstandingChange(operation.operation, ANSWER.text, operation.target_text, operation.value_text),),
        "Welche Angabe möchten Sie als Nächstes klären?",
    )
    external = FamilyCareExternalClarification(
        turn.turn_id, ANSWER, resolution, revision,
        "understanding-revision-family-care-scenario",
        "understanding-state-family-care", base_prepare().understanding_state_hash,
    )
    result = base_journey(previous_turns=(turn,), clarifications=(external,))
    assert result.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "PROPOSAL_ORIGIN_MISMATCH" in result.blockers

    wrong_state = UnderstandingState((), (), (), (), ())
    contradictory = replace(external, resolution=replace(resolution, proposal_statement_id=TRIGGER.statement_id, original_user_statement=TRIGGER.text), revision=replace(revision, state=wrong_state), resulting_understanding_state_hash=base_prepare().understanding_state_hash)
    result = base_journey(previous_turns=(turn,), clarifications=(contradictory,))
    assert result.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "RESULTING_STATE_MISMATCH" in result.blockers


def test_answered_scenario_remains_answered_by_revision_and_is_not_reasked():
    first = base_journey()
    turn = first.turns[0]
    operation = UnderstandingOperation(UnderstandingOperationType.CONFIRM_FACT, FACT.text, FACT.text)
    resolution = ClarificationResolution(
        "clarification-resolution-family-care-scenario-answered",
        TRIGGER.statement_id, TRIGGER.text, turn.question_id, turn.question,
        ANSWER.statement_id, ANSWER.text,
        ("understanding-proposal-family-care-scenario-answered",),
        ClarificationResolutionType.SELECT_PROPOSAL, ANSWER.source_reference,
        "Die vorhandene typisierte Operation wurde ausdrücklich ausgewählt.",
        "understanding-proposal-family-care-scenario-answered", operation, None,
    )
    revision = UnderstandingRevision(
        STATE,
        (UnderstandingChange(operation.operation, ANSWER.text, operation.target_text, operation.value_text),),
        "Welche Angabe möchten Sie als Nächstes klären?",
    )
    external = FamilyCareExternalClarification(
        turn.turn_id, ANSWER, resolution, revision,
        "understanding-revision-family-care-scenario-answered",
        "understanding-state-family-care", base_prepare().understanding_state_hash,
    )
    result = base_journey(previous_turns=(turn,), clarifications=(external,))

    assert result.status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY
    assert result.current_question is None
    assert result.answered_by_revision_points == (
        replace(POINT_SUPPORT, status=FamilyCarePointStatus.ANSWERED_BY_REVISION),
    )
    assert result.turns == (turn,)


def test_professional_review_is_never_added_or_packaged_without_explicit_input():
    scenario = next(item for item in SCENARIOS if item.slug == "multiple-essential-gaps")
    source, situation, _journey, experience = build_scenario(scenario)
    assert source.professional_reviews == ()
    assert situation.professional_reviews == ()
    assert experience.professional_reviews == ()
    assert experience.professional_review is None


def test_foreign_contribution_and_wrong_review_package_are_rejected():
    situation = base_prepare()
    foreign = replace(situation.contributions[0], shared_understanding_state_id="understanding-state-foreign")
    result = base_journey(replace(situation, contributions=(foreign,) + situation.contributions[1:]))
    assert result.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS

    ready_source = replace(POINT_SUPPORT, essential=False)
    ready = base_prepare(
        open_points=(ready_source,),
        dependencies=(),
        contribution_inputs=(replace(situation_input_contribution(), essential_point_ids=(), other_point_ids=(ready_source.point_id,), dependency_ids=()),),
    )
    review_journey = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(ready, (), create_review_preparation=True))
    wrong_package = replace(review_journey.professional_review, situation_id="family-care-situation-foreign")
    with pytest.raises(ValueError, match="professional review mismatch"):
        GuardianFamilyCareExperienceService().present(replace(review_journey, professional_review=wrong_package))


def situation_input_contribution():
    return FamilyCareDomainContributionInput(
        FamilyCareDomainType.CARE_AND_SUPPORT,
        facts=(FACT,),
        explicit_entries=(FamilyCareTextReference("family-care-text-review-fixture", "Explizite Testangabe.", ("scenario:review",)),),
        essential_point_ids=(POINT_SUPPORT.point_id,),
    )


def test_identical_inputs_are_deterministic_and_services_have_no_execution_side_effects(monkeypatch):
    scenario = SCENARIOS[0]
    first = build_scenario(scenario)
    second = build_scenario(scenario)
    assert first == second
    assert first[1].situation_id == second[1].situation_id
    assert first[3].experience_id == second[3].experience_id

    def forbidden(*_args, **_kwargs):
        raise AssertionError("side effect")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    build_scenario(scenario)
    experience = first[3]
    assert not hasattr(experience, "execute")
    assert not hasattr(experience, "route")
    assert FamilyCareExperienceActionType.ANSWER_CURRENT_QUESTION in experience.allowed_actions
