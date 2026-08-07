"""End-to-end conformance of canonical Family Care scenarios and answer contracts."""

from dataclasses import replace
from pathlib import Path
import socket

import pytest

from guardian_understanding.answer_boundary import (
    AnswerOperatingMode,
    ClassificationReference,
    GuardianAnswerBoundaryValidator,
)
from guardian_understanding.answer_foundation import (
    GuardianAnswerFoundationIntegration,
    GuardianAnswerFoundationIntegrationValidator,
)
from guardian_understanding.answer_reference_journey import (
    GuardianAnswerReferenceJourneyValidator,
)
from guardian_understanding.classification import (
    ClassificationUncertaintyStatus,
    GuardianClassificationValidator,
)
from guardian_understanding.personal_preparation import (
    B2PersonalPreparationContractValidator,
    BoundaryReference,
    KnownFactEntry,
    PersonalPreparationEnvelope,
    PersonalContextReference,
    ProfessionalReviewTopicEntry,
    SourceChainReference,
)
from guardian_understanding.source_chain import (
    GuardianAnswerContextReference,
    GuardianSourceChainValidator,
    SourceUncertaintyStatus,
)
from guardian_understanding.tests.test_answer_boundary import contract as boundary
from guardian_understanding.tests.test_answer_reference_journey_end_to_end import (
    journey_envelope,
)
from guardian_understanding.tests.test_classification import classification
from guardian_understanding.tests.test_personal_preparation_contract import preparation
from guardian_understanding.tests.test_source_chain import source_chain
from tests.test_family_care_scenarios import SCENARIOS, build_scenario


def _validate(scenario_slug, contract_name, validator, value):
    try:
        result = validator.validate(value)
    except Exception as error:  # pragma: no cover - exercised only on conformance failure
        code = getattr(error, "code", type(error).__name__)
        pytest.fail(
            "scenario {!r} violates {} contract [{}]: {}".format(
                scenario_slug, contract_name, code, error
            ),
            pytrace=True,
        )
    assert result is value, "scenario {!r}: {} validator replaced its input".format(
        scenario_slug, contract_name
    )


def _answer_journey_for(scenario, situation):
    slug = scenario.slug
    statement = situation.triggering_statement
    context = statement.source_reference
    source_id = "source-family-care-{}".format(slug)
    classification_id = "classification-family-care-{}".format(slug)
    boundary_id = "boundary-family-care-{}".format(slug)

    classification_contract = classification(
        classification_id=classification_id,
        provided_minimum_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        candidate_levels=(AnswerOperatingMode.B2_PERSONAL_PREPARATION,),
        effective_level=AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        professional_decision_requested=False,
        conversation_context_reference=context,
        uncertainty_status=ClassificationUncertaintyStatus.UNCERTAIN,
        source_chain_references=(SourceChainReference(source_id),),
    )
    boundary_contract = boundary(
        AnswerOperatingMode.B2_PERSONAL_PREPARATION,
        boundary_id=boundary_id,
        affected_domains=tuple(item.value for item in scenario.domains),
        classification_reference=ClassificationReference(classification_id),
    )
    source_contract = source_chain(
        source_chain_id=source_id,
        source_name=statement.statement_id,
        publisher=statement.source_reference,
        source_authority=statement.source_reference,
        source_reference=statement.source_reference,
        publication_or_version=None,
        supported_statement=statement.text,
        jurisdiction_or_scope=statement.source_reference,
        declared_contradictions=(),
        uncertainty_status=SourceUncertaintyStatus.UNCONFIRMED,
        answer_context_reference=GuardianAnswerContextReference(
            guardian_answer_id="answer-family-care-{}".format(slug),
            conversation_context_id=context,
        ),
        provenance_reference=statement.source_reference,
    )
    foundation = GuardianAnswerFoundationIntegration(
        boundary_contract=boundary_contract,
        classification_contract=classification_contract,
        source_chain_contracts=(source_contract,),
        require_complete_source_chain_set=True,
    )
    preparation_contract = preparation(
        preparation_id="preparation-family-care-{}".format(slug),
        classification_reference=ClassificationReference(classification_id),
        boundary_reference=BoundaryReference(boundary_id),
        source_chain_references=(SourceChainReference(source_id),),
        personal_context_reference=PersonalContextReference(context),
        preparation_goal=scenario.goals[0],
        known_facts=(
            KnownFactEntry(
                "fact-family-care-{}".format(slug),
                statement.text,
                (SourceChainReference(source_id),),
            ),
        ),
        professional_review_topics=(
            ProfessionalReviewTopicEntry(
                "review-family-care-{}".format(slug),
                situation.professional_boundaries[0],
            ),
        ),
        provider_reference="adapter:family-care-conformance-{}".format(slug),
    )
    stage = PersonalPreparationEnvelope(
        foundation=foundation,
        preparation=preparation_contract,
        general_orientation=None,
    )
    envelope = journey_envelope(b2=stage)
    return replace(
        envelope,
        journey=replace(
            envelope.journey,
            conversation_context_reference=context,
            provider_reference="adapter:family-care-conformance-{}".format(slug),
            provenance="provenance:family-care-conformance-{}".format(slug),
        ),
    )


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item.slug)
def test_all_family_care_scenarios_conform_to_guardian_answer_contracts(
    scenario, monkeypatch
):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("conformance validation must remain read-only")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    source, situation, family_journey, experience = build_scenario(scenario)
    assert situation.understanding_state is source.understanding_state
    assert family_journey.situation is situation
    assert experience.journey_id == family_journey.journey_id

    answer_envelope = _answer_journey_for(scenario, situation)
    foundation = answer_envelope.current_foundation
    source_contract = foundation.source_chain_contracts[0]

    assert source_contract.source_reference == situation.triggering_statement.source_reference
    assert source_contract.supported_statement == situation.triggering_statement.text
    assert foundation.boundary_contract.affected_domains == tuple(
        item.value for item in scenario.domains
    )

    checks = (
        ("classification", GuardianClassificationValidator(), foundation.classification_contract),
        ("answer-boundary", GuardianAnswerBoundaryValidator(), foundation.boundary_contract),
        ("source-chain", GuardianSourceChainValidator(), source_contract),
        ("answer-foundation", GuardianAnswerFoundationIntegrationValidator(), foundation),
        ("personal-preparation", B2PersonalPreparationContractValidator(), answer_envelope.personal_preparation.preparation),
        ("answer-reference-journey", GuardianAnswerReferenceJourneyValidator(), answer_envelope),
    )
    for contract_name, validator, value in checks:
        _validate(scenario.slug, contract_name, validator, value)


def test_family_care_conformance_covers_exactly_the_twelve_canonical_scenarios():
    assert len(SCENARIOS) == 12
    assert len({scenario.slug for scenario in SCENARIOS}) == 12
