from dataclasses import fields

import pytest

from guardian_understanding import (
    Fact,
    Goal,
    GuardianUnderstandingProposalService,
    Hypothesis,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingProposalCandidate,
    UnderstandingProposalSelection,
    UnderstandingState,
    Unknown,
)


EMPTY = UnderstandingState((), (), (), (), ())
STATEMENT_ID = "statement-001"
SOURCE = "conversation-turn-001"


def candidate(kind, rationale, target=None, value=None, source=SOURCE):
    return UnderstandingProposalCandidate(
        operation=UnderstandingOperation(
            operation=kind,
            target_text=target,
            value_text=value,
        ),
        source_reference=source,
        rationale=rationale,
    )


def proposals(state, statement, *candidates, question=None):
    return GuardianUnderstandingProposalService().create(
        state,
        STATEMENT_ID,
        statement,
        tuple(candidates),
        question,
    )


def select(proposal_set, index=0):
    proposal = proposal_set.proposals[index]
    return UnderstandingProposalSelection(proposal.proposal_id)


def test_proposal_for_new_fact_is_not_a_fact_or_state_change():
    proposal_set = proposals(
        EMPTY,
        "Ich wohne jetzt in Köln.",
        candidate(
            UnderstandingOperationType.ADD_FACT,
            "Die Aussage benennt einen möglichen neuen Sachverhalt.",
            value="Ich wohne in Köln.",
        ),
    )
    proposal = proposal_set.proposals[0]
    assert proposal.operation.operation is UnderstandingOperationType.ADD_FACT
    assert proposal.is_fact is False
    assert proposal.changes_state is False


def test_proposal_for_fact_correction_preserves_requested_operation():
    state = UnderstandingState((Fact("Der Termin ist Montag."),), (), (), (), ())
    requested = candidate(
        UnderstandingOperationType.CORRECT_FACT,
        "Die neue Aussage bezeichnet die frühere Angabe als Korrektur.",
        target="Der Termin ist Montag.",
        value="Der Termin ist Dienstag.",
    )
    proposal = proposals(
        state,
        "Korrektur: Der Termin ist Dienstag.",
        requested,
    ).proposals[0]
    assert proposal.operation is requested.operation


def test_proposal_for_hypothesis():
    proposal = proposals(
        EMPTY,
        "Vielleicht ist der Arbeitsweg zu lang.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Die Aussage formuliert eine mögliche, noch offene Erklärung.",
            value="Der Arbeitsweg könnte zu lang sein.",
        ),
    ).proposals[0]
    assert proposal.operation.operation is UnderstandingOperationType.ADD_HYPOTHESIS


def test_proposal_to_close_unknown():
    state = UnderstandingState(
        (),
        (),
        (Unknown("Wann ist der Termin?"),),
        (),
        (),
    )
    proposal = proposals(
        state,
        "Der Termin ist Freitag.",
        candidate(
            UnderstandingOperationType.CLOSE_UNKNOWN,
            "Die neue Aussage könnte die offene Frage beantworten.",
            target="Wann ist der Termin?",
        ),
    ).proposals[0]
    assert proposal.operation.operation is UnderstandingOperationType.CLOSE_UNKNOWN


def test_proposal_to_change_goal():
    state = UnderstandingState((), (), (), (), (Goal("Optionen verstehen."),))
    proposal = proposals(
        state,
        "Ich möchte zuerst den Ablauf verstehen.",
        candidate(
            UnderstandingOperationType.CHANGE_GOAL,
            "Die Aussage benennt möglicherweise ein geändertes Gesprächsziel.",
            target="Optionen verstehen.",
            value="Den Ablauf verstehen.",
        ),
    ).proposals[0]
    assert proposal.operation.operation is UnderstandingOperationType.CHANGE_GOAL


def test_alternative_proposals_remain_independent_for_same_statement():
    proposal_set = proposals(
        EMPTY,
        "Es könnte an der Entfernung liegen.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Die Aussage kann eine neue Hypothese ausdrücken.",
            value="Die Entfernung könnte wichtig sein.",
        ),
        candidate(
            UnderstandingOperationType.ADD_UNKNOWN,
            "Die Aussage kann eine noch offene Frage sichtbar machen.",
            value="Welche Rolle spielt die Entfernung?",
        ),
    )
    first, second = proposal_set.proposals
    assert first.proposal_id != second.proposal_id
    assert first.operation != second.operation
    assert first.statement_id == second.statement_id == STATEMENT_ID
    assert first.user_statement == second.user_statement


def test_contradictory_alternatives_are_not_merged():
    proposal_set = proposals(
        EMPTY,
        "Vielleicht bleibe ich, vielleicht gehe ich.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Eine mögliche Lesart ist das Bleiben.",
            value="Ich könnte bleiben.",
        ),
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Eine andere mögliche Lesart ist das Gehen.",
            value="Ich könnte gehen.",
        ),
    )
    assert tuple(
        proposal.operation.value_text
        for proposal in proposal_set.proposals
    ) == ("Ich könnte bleiben.", "Ich könnte gehen.")


def test_creating_proposals_does_not_change_understanding_state():
    state = UnderstandingState((Fact("Ich wohne in Bonn."),), (), (), (), ())
    before = state
    proposals(
        state,
        "Vielleicht ziehe ich um.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Die Aussage beschreibt eine Möglichkeit.",
            value="Ein Umzug ist möglich.",
        ),
    )
    assert state == before


def test_proposal_without_selection_has_no_revision():
    proposal_set = proposals(
        EMPTY,
        "Ich arbeite in Köln.",
        candidate(
            UnderstandingOperationType.ADD_FACT,
            "Eine mögliche neue Tatsache.",
            value="Ich arbeite in Köln.",
        ),
    )
    assert not hasattr(proposal_set, "revision")
    assert EMPTY.facts == ()


def test_explicit_selection_uses_existing_revision_mechanism():
    proposal_set = proposals(
        EMPTY,
        "Ich arbeite in Köln.",
        candidate(
            UnderstandingOperationType.ADD_FACT,
            "Eine mögliche neue Tatsache.",
            value="Ich arbeite in Köln.",
        ),
    )
    application = GuardianUnderstandingProposalService().apply(
        EMPTY,
        proposal_set,
        select(proposal_set),
    )
    assert application.revision.state.facts == (Fact("Ich arbeite in Köln."),)
    assert len(application.revision.changes) == 1


def test_unknown_proposal_id_is_rejected():
    proposal_set = proposals(
        EMPTY,
        "Ich arbeite in Köln.",
        candidate(
            UnderstandingOperationType.ADD_FACT,
            "Eine mögliche neue Tatsache.",
            value="Ich arbeite in Köln.",
        ),
    )
    with pytest.raises(ValueError, match="Unknown proposal ID"):
        GuardianUnderstandingProposalService().apply(
            EMPTY,
            proposal_set,
            UnderstandingProposalSelection(
                "understanding-proposal-unknown"
            ),
        )


def test_selected_operation_is_passed_without_modification():
    proposal_set = proposals(
        EMPTY,
        "Vielleicht ist die Strecke wichtig.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Eine mögliche Hypothese.",
            value="Die Strecke könnte wichtig sein.",
        ),
    )
    proposal = proposal_set.proposals[0]
    application = GuardianUnderstandingProposalService().apply(
        EMPTY,
        proposal_set,
        select(proposal_set),
    )
    assert application.selected_proposal.operation is proposal.operation
    assert (
        application.revision.changes[0].operation
        is proposal.operation.operation
    )
    assert (
        application.revision.changes[0].result_text
        == proposal.operation.value_text
    )


def test_source_reference_and_statement_are_preserved():
    proposal_set = proposals(
        EMPTY,
        "Ich arbeite in Köln.",
        candidate(
            UnderstandingOperationType.ADD_FACT,
            "Eine mögliche neue Tatsache.",
            value="Ich arbeite in Köln.",
            source="message-store:statement-001",
        ),
    )
    proposal = proposal_set.proposals[0]
    application = GuardianUnderstandingProposalService().apply(
        EMPTY,
        proposal_set,
        select(proposal_set),
    )
    assert proposal.source_reference == "message-store:statement-001"
    assert proposal.user_statement == "Ich arbeite in Köln."
    assert (
        application.revision.changes[0].source_statement
        == "Ich arbeite in Köln."
    )


def test_multiple_alternatives_have_exactly_one_understanding_question():
    proposal_set = proposals(
        EMPTY,
        "Vielleicht bleibe ich, vielleicht gehe ich.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Mögliche Lesart eins.",
            value="Ich könnte bleiben.",
        ),
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Mögliche Lesart zwei.",
            value="Ich könnte gehen.",
        ),
    )
    assert proposal_set.understanding_question is not None
    assert proposal_set.understanding_question.count("?") == 1
    assert proposal_set.understanding_question.endswith("?")


def test_single_proposal_may_carry_one_clarifying_question():
    proposal_set = proposals(
        EMPTY,
        "Es könnte bald sein.",
        candidate(
            UnderstandingOperationType.ADD_UNKNOWN,
            "Der Zeitpunkt bleibt offen.",
            value="Wann genau ist es?",
        ),
        question="Welchen Zeitpunkt meinen Sie genau?",
    )
    assert proposal_set.understanding_question == (
        "Welchen Zeitpunkt meinen Sie genau?"
    )


def test_proposal_contract_has_no_confidence_or_ranking():
    proposal_set = proposals(
        EMPTY,
        "Vielleicht ist die Strecke wichtig.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Eine mögliche Hypothese.",
            value="Die Strecke könnte wichtig sein.",
        ),
    )
    forbidden = {"confidence", "score", "probability", "rank", "priority"}
    assert forbidden.isdisjoint(
        field.name for field in fields(type(proposal_set.proposals[0]))
    )
    assert forbidden.isdisjoint(
        field.name for field in fields(type(proposal_set))
    )


def test_proposal_contract_exposes_no_decision_routing_or_activation():
    proposal_set = proposals(
        EMPTY,
        "Vielleicht ist die Strecke wichtig.",
        candidate(
            UnderstandingOperationType.ADD_HYPOTHESIS,
            "Eine mögliche Hypothese.",
            value="Die Strecke könnte wichtig sein.",
        ),
    )
    forbidden = {
        "decision",
        "routing",
        "workflow",
        "capability",
        "activation",
    }
    assert forbidden.isdisjoint(vars(proposal_set))
    assert forbidden.isdisjoint(vars(proposal_set.proposals[0]))


def test_proposal_generation_is_deterministic():
    service = GuardianUnderstandingProposalService()
    item = candidate(
        UnderstandingOperationType.ADD_HYPOTHESIS,
        "Eine mögliche Hypothese.",
        value="Die Strecke könnte wichtig sein.",
    )
    first = service.create(
        EMPTY,
        STATEMENT_ID,
        "Vielleicht ist die Strecke wichtig.",
        (item,),
    )
    second = service.create(
        EMPTY,
        STATEMENT_ID,
        "Vielleicht ist die Strecke wichtig.",
        (item,),
    )
    assert first == second
