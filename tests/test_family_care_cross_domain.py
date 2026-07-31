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
    FamilyCareExperience,
    FamilyCareExperienceActionType,
    FamilyCareExternalClarification,
    FamilyCareGapBinding,
    FamilyCareGapType,
    FamilyCareJourneyAction,
    FamilyCareJourneyInput,
    FamilyCareJourneyStatus,
    FamilyCareOpenPoint,
    FamilyCarePersonReference,
    FamilyCarePointStatus,
    FamilyCareQuestionCatalog,
    FamilyCareSituationInput,
    FamilyCareTextReference,
    GuardianFamilyCareExperienceService,
    GuardianFamilyCareJourneyService,
    GuardianFamilyCarePreparationService,
)
from life_decisions.models import DocumentReference, DocumentType


FACT = Fact("Eine nahestehende Person benötigt zunehmend Unterstützung.")
GOAL = Goal("Die familiäre Pflegesituation sachlich ordnen.")
HYPOTHESIS = Hypothesis("Die bisherige Unterstützung könnte nicht ausreichen.")
UNKNOWN = Unknown("Welche Unterstützung ist im Alltag konkret nötig?")
CONTRADICTION = Contradiction("Die Person lebt selbstständig. <> Sie benötigt tägliche Hilfe.")
STATE = UnderstandingState((FACT,), (HYPOTHESIS,), (UNKNOWN,), (CONTRADICTION,), (GOAL,))
TRIGGER = UserStatementReference(
    "statement-family-care-trigger",
    "In unserer Familie ist ein Pflegefall entstanden.",
    "conversation:family-care-trigger",
)
ANSWER = UserStatementReference(
    "statement-family-care-answer",
    "Diesen Punkt möchte ich noch offenlassen.",
    "conversation:family-care-answer",
)
PERSON = FamilyCarePersonReference(
    "family-care-person-mother",
    "Mutter",
    "unterstützungsbedürftige Person",
    "Mutter des Nutzers",
    ("conversation:person",),
)
SUPPORT = FamilyCareTextReference(
    "family-care-text-support-mobility",
    "Unterstützung bei der Mobilität wurde ausdrücklich genannt.",
    ("conversation:support",),
)
HOUSING = FamilyCareTextReference(
    "family-care-text-housing-alone",
    "Die Person lebt ausdrücklich allein in einer eigenen Wohnung.",
    ("conversation:housing",),
)
FINANCE = FamilyCareTextReference(
    "family-care-text-finance-costs",
    "Laufende Wohnkosten wurden ausdrücklich genannt.",
    ("conversation:finance",),
)
DOCUMENT_NOTE = FamilyCareTextReference(
    "family-care-text-document-poa",
    "Eine bestehende Vorsorgevollmacht wurde ausdrücklich erwähnt.",
    ("conversation:document",),
)
DOCUMENT = DocumentReference(
    "document-family-care-poa",
    DocumentType.POWER_OF_ATTORNEY,
    "user-vault://family-care/poa",
    False,
)
POINT_SUPPORT = FamilyCareOpenPoint(
    "family-care-point-support-need",
    "Der konkrete Unterstützungsbedarf ist offen.",
    ("conversation:point-support",),
    (FamilyCareDomainType.CARE_AND_SUPPORT,),
    True,
)
POINT_HOUSING = FamilyCareOpenPoint(
    "family-care-point-housing",
    "Die organisatorische Wohnsituation ist offen.",
    ("conversation:point-housing",),
    (FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,),
    False,
)
DEPENDENCY = FamilyCareDependency(
    "family-care-dependency-support-housing",
    POINT_SUPPORT.point_id,
    POINT_HOUSING.point_id,
    (
        FamilyCareDomainType.CARE_AND_SUPPORT,
        FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,
    ),
    "Der ausdrücklich erfasste Unterstützungsbedarf ist mit der offenen Wohnorganisation verbunden.",
    ("conversation:dependency",),
)
STEP = OrganizationalPreparationStep(
    "preparation-step-family-care-contact",
    PreparationStepType.OTHER,
    "Den ausdrücklich genannten Fachkontakt bereithalten.",
    ("conversation:step",),
)
REVIEW = ProfessionalReviewNeed(
    "professional-review-family-care-legal",
    ProfessionalReviewCategory.LEGAL,
    ReviewNeed.REQUIRED,
    "Eine ausdrücklich gewünschte rechtliche Prüfung vorbereiten.",
    ("conversation:review",),
)


def contributions():
    return (
        FamilyCareDomainContributionInput(
            FamilyCareDomainType.CARE_AND_SUPPORT,
            facts=(FACT,), unknowns=(UNKNOWN,), contradictions=(CONTRADICTION,),
            explicit_entries=(SUPPORT,),
            essential_point_ids=(POINT_SUPPORT.point_id,),
            professional_boundaries=("Keine Pflegegradeinstufung.",),
        ),
        FamilyCareDomainContributionInput(
            FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,
            goals=(GOAL,), explicit_entries=(HOUSING,),
            other_point_ids=(POINT_HOUSING.point_id,),
            dependency_ids=(DEPENDENCY.dependency_id,),
            professional_boundaries=("Keine Immobilienbewertung.",),
        ),
        FamilyCareDomainContributionInput(
            FamilyCareDomainType.FINANCES_AND_COSTS,
            hypotheses=(HYPOTHESIS,), explicit_entries=(FINANCE,),
            professional_boundaries=("Keine Finanzberatung.",),
        ),
        FamilyCareDomainContributionInput(
            FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION,
            explicit_entries=(DOCUMENT_NOTE,),
            professional_reviews=(REVIEW,),
            professional_boundaries=("Keine Rechtsberatung.",),
        ),
    )


def situation_input(**changes):
    values = dict(
        understanding_state_id="understanding-state-family-care",
        understanding_state=STATE,
        triggering_statement_id=TRIGGER.statement_id,
        user_statements=(TRIGGER,),
        facts=(FACT,), goals=(GOAL,), hypotheses=(HYPOTHESIS,),
        unknowns=(UNKNOWN,), contradictions=(CONTRADICTION,),
        people=(PERSON,), support_needs=(SUPPORT,),
        housing_and_property=(HOUSING,),
        financial_and_organizational=(FINANCE,),
        care_and_health_documents=(DOCUMENT_NOTE,), documents=(DOCUMENT,),
        open_points=(POINT_SUPPORT, POINT_HOUSING),
        dependencies=(DEPENDENCY,), contribution_inputs=contributions(),
        professional_reviews=(REVIEW,), organizational_steps=(STEP,),
    )
    values.update(changes)
    return FamilyCareSituationInput(**values)


def prepare(**changes):
    if changes.get("dependencies") == () and "contribution_inputs" not in changes:
        changes["contribution_inputs"] = tuple(
            replace(item, dependency_ids=()) for item in contributions()
        )
    return GuardianFamilyCarePreparationService().prepare(situation_input(**changes))


BINDING = FamilyCareGapBinding(POINT_SUPPORT.point_id, FamilyCareGapType.SUPPORT_NEED)


def journey(situation=None, **changes):
    values = dict(situation=situation or prepare(), gap_bindings=(BINDING,))
    values.update(changes)
    return GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(**values))


def resolution(turn, kind):
    return ClarificationResolution(
        "clarification-resolution-family-care-" + kind.value.lower(),
        TRIGGER.statement_id,
        TRIGGER.text,
        turn.question_id,
        turn.question,
        ANSWER.statement_id,
        ANSWER.text,
        ("understanding-proposal-family-care",),
        kind,
        ANSWER.source_reference,
        "Ausdrückliche externe Klärung.",
        None,
        None,
        "Welche Angabe möchten Sie weiter klären?" if kind is ClarificationResolutionType.KEEP_OPEN else None,
    )


def test_valid_situation_is_deterministic_and_keeps_understanding_categories_separate():
    first = prepare()
    second = prepare()

    assert first == second
    assert first.situation_id == second.situation_id
    assert first.facts == (FACT,)
    assert first.goals == (GOAL,)
    assert first.hypotheses == (HYPOTHESIS,)
    assert first.unknowns == (UNKNOWN,)
    assert first.contradictions == (CONTRADICTION,)


def test_domain_contributions_share_one_state_and_have_no_domain_state():
    result = prepare()

    assert len(result.contributions) == 4
    assert {item.shared_understanding_state_id for item in result.contributions} == {result.understanding_state_id}
    assert {item.shared_understanding_state_hash for item in result.contributions} == {result.understanding_state_hash}
    assert all(not hasattr(item, "understanding_state") for item in result.contributions)
    assert result.understanding_state == STATE


def test_only_explicit_contributions_and_entries_are_present():
    result = prepare(contribution_inputs=(), support_needs=(), housing_and_property=(), financial_and_organizational=(), care_and_health_documents=())

    assert result.contributions == ()
    assert result.support_needs == ()
    assert result.housing_and_property == ()
    assert result.financial_and_organizational == ()
    assert result.care_and_health_documents == ()


def test_contract_supports_exactly_the_seven_authorized_domains():
    assert tuple(FamilyCareDomainType) == (
        FamilyCareDomainType.CARE_AND_SUPPORT,
        FamilyCareDomainType.HEALTH_AND_MEDICAL_ORGANIZATION,
        FamilyCareDomainType.LIFE_DECISIONS_AND_REPRESENTATION,
        FamilyCareDomainType.HOUSING_AND_REAL_ESTATE,
        FamilyCareDomainType.FINANCES_AND_COSTS,
        FamilyCareDomainType.FAMILY_AND_ROLES,
        FamilyCareDomainType.DOCUMENTS_AND_ORGANIZATION,
    )


def test_contributions_filter_but_never_create_or_change_state_content():
    result = prepare()
    care = result.contributions[0]
    finance = result.contributions[2]

    assert care.facts == (FACT,)
    assert finance.facts == ()
    assert finance.hypotheses == (HYPOTHESIS,)
    assert result.understanding_state == STATE
    assert ANSWER.text not in tuple(item.text for item in result.facts)


def test_domain_texts_remain_uninterpreted_and_unrated():
    result = prepare()

    assert result.support_needs == (SUPPORT,)
    assert result.housing_and_property == (HOUSING,)
    assert result.financial_and_organizational == (FINANCE,)
    assert not hasattr(result, "care_grade")
    assert not hasattr(result, "property_value")
    assert not hasattr(result, "benefit_amount")
    assert not hasattr(result, "financing")
    assert not hasattr(result.people[0], "suitability")
    assert not hasattr(result.people[0], "assigned_responsibility")


def test_dependencies_are_exclusively_explicit_and_preserve_order():
    assert prepare().dependencies == (DEPENDENCY,)
    assert prepare(dependencies=()).dependencies == ()


def test_unknown_dependency_or_point_reference_is_rejected():
    unknown = replace(DEPENDENCY, target_point_id="family-care-point-unknown")
    with pytest.raises(ValueError, match="unknown point"):
        situation_input(dependencies=(unknown,))
    bad_contribution = replace(contributions()[0], essential_point_ids=("family-care-point-unknown",))
    with pytest.raises(ValueError, match="incompatible point"):
        situation_input(contribution_inputs=(bad_contribution,))


def test_first_active_essential_point_gets_exactly_one_controlled_question():
    result = journey()

    assert result.status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION
    assert result.current_open_point == POINT_SUPPORT
    assert result.current_question is not None
    assert result.current_question.point_id == POINT_SUPPORT.point_id
    assert result.current_question.text.count("?") == 1
    assert len(result.turns) == 1


def test_missing_binding_or_catalog_question_blocks_without_replacement():
    missing_binding = GuardianFamilyCareJourneyService().build(FamilyCareJourneyInput(prepare(), ()))
    assert missing_binding.status is FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    assert missing_binding.current_question is None
    assert missing_binding.blockers == ("MISSING_GAP_BINDING",)

    no_catalog = GuardianFamilyCareJourneyService(FamilyCareQuestionCatalog(())).build(FamilyCareJourneyInput(prepare(), (BINDING,)))
    assert no_catalog.status is FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION
    assert no_catalog.blockers == ("MISSING_CONTROLLED_QUESTION",)


def test_turn_and_answer_alone_never_change_shared_state():
    first = journey()
    turn = first.turns[0]
    assert turn.state_changed_by_turn is False
    with pytest.raises(FrozenInstanceError):
        turn.state_changed_by_turn = True

    pending = FamilyCareExternalClarification(turn.turn_id, ANSWER)
    result = journey(previous_turns=first.turns, clarifications=(pending,))
    assert result.status is FamilyCareJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION
    assert result.situation.understanding_state == STATE


def test_partial_or_foreign_external_artifact_chain_is_blocked():
    first = journey()
    selected = resolution(first.turns[0], ClarificationResolutionType.SELECT_PROPOSAL)
    partial = FamilyCareExternalClarification(first.turns[0].turn_id, ANSWER, selected)
    result = journey(previous_turns=first.turns, clarifications=(partial,))
    assert result.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "PARTIAL_EXTERNAL_ARTIFACT_CHAIN" in result.blockers

    foreign = replace(partial, source_turn_id="family-care-turn-foreign")
    result = journey(previous_turns=first.turns, clarifications=(foreign,))
    assert result.status is FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS
    assert "CLARIFICATION_TURN_MISMATCH" in result.blockers


def test_question_is_not_repeated_even_after_an_intervening_turn():
    first = journey()
    other = replace(first.turns[0], turn_id="family-care-turn-other", question_id="understanding-question-family-care-other", question="Welche andere Angabe ist offen?", previous_turn_id=first.turns[0].turn_id)
    result = journey(previous_turns=(first.turns[0], other))

    assert result.status is FamilyCareJourneyStatus.QUESTION_UNRESOLVED
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
def test_nonselecting_clarifications_remain_visible_and_never_become_facts(kind, field):
    first = journey()
    external = FamilyCareExternalClarification(first.turns[0].turn_id, ANSWER, resolution(first.turns[0], kind))
    result = journey(previous_turns=first.turns, clarifications=(external,))

    assert POINT_SUPPORT in getattr(result, field)
    assert result.situation.facts == (FACT,)
    assert ANSWER.text not in tuple(item.text for item in result.situation.facts)


def test_explicit_point_lifecycle_is_preserved_without_reclassification_as_fact():
    deferred_point = replace(POINT_SUPPORT, status=FamilyCarePointStatus.DEFERRED)
    result = journey(prepare(open_points=(deferred_point, POINT_HOUSING)))

    assert result.status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY
    assert result.deferred_points == (deferred_point,)
    assert deferred_point not in result.situation.facts


def test_nonblocking_contradiction_does_not_prevent_readiness():
    closed_support = replace(POINT_SUPPORT, essential=False)
    ready = prepare(
        open_points=(closed_support, POINT_HOUSING),
        contribution_inputs=(
            replace(contributions()[0], essential_point_ids=(), other_point_ids=(closed_support.point_id,)),
            contributions()[1], contributions()[2], contributions()[3],
        ),
    )
    result = journey(ready)

    assert result.status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY
    assert result.situation.contradictions == (CONTRADICTION,)


def test_professional_review_contains_only_explicit_cross_domain_content():
    no_essential = replace(POINT_SUPPORT, essential=False)
    ready = prepare(
        open_points=(no_essential, POINT_HOUSING),
        contribution_inputs=(
            replace(contributions()[0], essential_point_ids=(), other_point_ids=(no_essential.point_id,)),
            contributions()[1], contributions()[2], contributions()[3],
        ),
    )
    result = journey(ready, create_review_preparation=True)
    package = result.professional_review

    assert result.status is FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY
    assert package is not None
    assert package.contributions == ready.contributions
    assert package.dependencies == (DEPENDENCY,)
    assert package.people == (PERSON,)
    assert package.professional_reviews == (REVIEW,)
    assert not hasattr(package, "checklist")
    assert not hasattr(package, "recommendations")


@pytest.mark.parametrize("status", tuple(FamilyCareJourneyStatus))
def test_experience_supports_every_journey_status_without_second_guardian(status):
    if status is FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY:
        ready = prepare(open_points=(replace(POINT_SUPPORT, essential=False), POINT_HOUSING))
        base = GuardianFamilyCareJourneyService().build(
            FamilyCareJourneyInput(ready, (), create_review_preparation=True)
        )
    else:
        base = journey()
    actions = {
        FamilyCareJourneyStatus.NEEDS_CLARIFICATION: FamilyCareJourneyAction.OBTAIN_USER_ANSWER,
        FamilyCareJourneyStatus.WAITING_FOR_EXTERNAL_RESOLUTION: FamilyCareJourneyAction.OBTAIN_EXTERNAL_RESOLUTION,
        FamilyCareJourneyStatus.QUESTION_UNRESOLVED: FamilyCareJourneyAction.REVIEW_UNRESOLVED_QUESTION,
        FamilyCareJourneyStatus.BLOCKED_MISSING_CONTROLLED_QUESTION: FamilyCareJourneyAction.PROVIDE_CONTROLLED_QUESTION,
        FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS: FamilyCareJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS,
        FamilyCareJourneyStatus.SITUATION_PREPARATION_READY: FamilyCareJourneyAction.PREPARE_CROSS_DOMAIN_REVIEW,
        FamilyCareJourneyStatus.CROSS_DOMAIN_REVIEW_PREPARATION_READY: FamilyCareJourneyAction.USE_REVIEW_PACKAGE,
    }
    altered = replace(base, status=status, next_action=actions[status], current_question=base.current_question if status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION else None, blockers=("TEST_INCONSISTENCY",) if "BLOCKED" in status.value else ())
    result = GuardianFamilyCareExperienceService().present(altered)

    assert result.status is status
    assert (result.current_question is not None) is (status is FamilyCareJourneyStatus.NEEDS_CLARIFICATION)
    assert not hasattr(result, "guardian_agents")
    assert not hasattr(result, "agent_messages")


def test_complete_selected_external_chain_closes_point_by_revision_without_rewriting_operation():
    first = journey()
    turn = first.turns[-1]
    operation = UnderstandingOperation(
        UnderstandingOperationType.CONFIRM_FACT,
        target_text=FACT.text,
        value_text=FACT.text,
    )
    resolution_value = ClarificationResolution(
        "clarification-resolution-family-care-selected",
        TRIGGER.statement_id,
        TRIGGER.text,
        turn.question_id,
        turn.question,
        ANSWER.statement_id,
        ANSWER.text,
        ("understanding-proposal-family-care-selected",),
        ClarificationResolutionType.SELECT_PROPOSAL,
        ANSWER.source_reference,
        "Die Auswahl wurde ausdrücklich übergeben.",
        "understanding-proposal-family-care-selected",
        operation,
        None,
    )
    revision = UnderstandingRevision(
        STATE,
        (
            UnderstandingChange(
                operation.operation,
                ANSWER.text,
                operation.target_text,
                operation.value_text,
            ),
        ),
        "Welche Angabe möchten Sie als Nächstes klären?",
    )
    external = FamilyCareExternalClarification(
        turn.turn_id,
        ANSWER,
        resolution_value,
        revision,
        "understanding-revision-family-care-selected",
        "understanding-state-family-care",
        prepare().understanding_state_hash,
    )
    result = journey(previous_turns=(turn,), clarifications=(external,))

    assert result.status is FamilyCareJourneyStatus.SITUATION_PREPARATION_READY
    assert result.current_question is None
    assert result.answered_by_revision_points[0].point_id == POINT_SUPPORT.point_id
    assert result.answered_by_revision_points[0].status is FamilyCarePointStatus.ANSWERED_BY_REVISION
    assert resolution_value.selected_operation is operation


def test_experience_keeps_contributions_dependencies_and_uncertainty_separate():
    result = GuardianFamilyCareExperienceService().present(journey())

    assert result.contributions == prepare().contributions
    assert result.dependencies == (DEPENDENCY,)
    assert result.hypotheses == (HYPOTHESIS,)
    assert result.contradictions == (CONTRADICTION,)
    assert HYPOTHESIS not in result.facts
    assert result.allowed_actions == (
        FamilyCareExperienceActionType.ANSWER_CURRENT_QUESTION,
        FamilyCareExperienceActionType.KEEP_POINT_OPEN,
        FamilyCareExperienceActionType.CLOSE_POINT_WITHOUT_CHANGE,
    )


def test_blocked_experience_hides_domain_content_and_separates_error():
    blocked = replace(journey(), status=FamilyCareJourneyStatus.BLOCKED_INCONSISTENT_ARTIFACTS, next_action=FamilyCareJourneyAction.CORRECT_INCONSISTENT_ARTIFACTS, current_question=None, blockers=("STATE_HASH_MISMATCH",))
    result = GuardianFamilyCareExperienceService().present(blocked)

    assert result.contributions == ()
    assert result.dependencies == ()
    assert result.facts == ()
    assert result.technical_errors == ("STATE_HASH_MISMATCH",)
    assert "STATE_HASH_MISMATCH" not in result.status_description


def test_visible_boundaries_cover_all_prohibited_advice_and_decisions():
    text = " ".join(prepare().professional_boundaries)
    for phrase in (
        "keine Pflegeberatung", "medizinische oder rechtliche Beratung",
        "keine Steuer-, Finanz- oder Immobilienberatung",
        "keine Immobilienbewertung", "keine Leistungsentscheidung",
        "keine Pflegegradeinstufung", "keine Person",
        "keinen automatischen Maßnahmenplan", "keine automatische Entscheidung",
        "aktiviert keine Domäne automatisch",
    ):
        assert phrase in text


def test_experience_id_is_semantic_stable_and_time_independent():
    service = GuardianFamilyCareExperienceService()
    first = service.present(journey())
    second = service.present(journey())
    changed = service.present(journey(prepare(dependencies=())))

    assert first == second
    assert first.experience_id == second.experience_id
    assert first.experience_id != changed.experience_id
    assert not hasattr(first, "created_at")
    assert not hasattr(first, "timestamp")


def test_services_are_stateless_and_use_no_file_network_llm_or_agent_runtime(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("side effect")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    preparation_service = GuardianFamilyCarePreparationService()
    experience_service = GuardianFamilyCareExperienceService()
    assert preparation_service.__dict__ == {}
    assert experience_service.__dict__ == {}
    experience_service.present(journey())


def test_contract_has_no_routing_scoring_advice_or_agent_framework_fields():
    forbidden = {
        "routing", "route", "confidence", "score", "ranking", "recommendation",
        "agent", "agents", "agent_messages", "care_grade", "benefit_amount",
        "property_value", "financing_decision", "llm", "persistence",
    }
    assert forbidden.isdisjoint(field.name for field in fields(FamilyCareExperience))
