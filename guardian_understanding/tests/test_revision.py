from guardian_understanding import (
    Contradiction,
    Fact,
    FactStatus,
    Goal,
    GoalStatus,
    GuardianUnderstandingService,
    Hypothesis,
    HypothesisStatus,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingState,
    UnderstandingUpdate,
    Unknown,
    UnknownStatus,
)


EMPTY = UnderstandingState((), (), (), (), ())


def operation(kind, target=None, value=None):
    return UnderstandingOperation(
        operation=kind,
        target_text=target,
        value_text=value,
    )


def update(statement, *operations):
    return UnderstandingUpdate(statement, tuple(operations))


def test_new_fact_is_added_and_traced_to_statement():
    revision = GuardianUnderstandingService().advance(
        EMPTY,
        update(
            "Ich arbeite jetzt in Köln.",
            operation(
                UnderstandingOperationType.ADD_FACT,
                value="Ich arbeite in Köln.",
            ),
        ),
    )
    assert revision.state.facts == (Fact("Ich arbeite in Köln."),)
    assert revision.changes[0].source_statement == "Ich arbeite jetzt in Köln."


def test_existing_fact_can_be_confirmed_without_duplication():
    state = UnderstandingState(
        (Fact("Der Termin ist am Montag."),),
        (),
        (),
        (),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Ja, Montag stimmt.",
            operation(
                UnderstandingOperationType.CONFIRM_FACT,
                target="Der Termin ist am Montag.",
            ),
        ),
    )
    assert revision.state.facts == (
        Fact("Der Termin ist am Montag.", FactStatus.CONFIRMED),
    )


def test_fact_correction_preserves_old_fact_and_visible_contradiction():
    state = UnderstandingState(
        (Fact("Der Termin ist am Montag."),),
        (),
        (),
        (Contradiction("Ein älterer Widerspruch."),),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Korrektur: Der Termin ist Dienstag.",
            operation(
                UnderstandingOperationType.CORRECT_FACT,
                target="Der Termin ist am Montag.",
                value="Der Termin ist am Dienstag.",
            ),
        ),
    )
    assert revision.state.facts == (
        Fact("Der Termin ist am Montag.", FactStatus.CORRECTED),
        Fact("Der Termin ist am Dienstag."),
    )
    assert revision.state.contradictions == (
        Contradiction("Ein älterer Widerspruch."),
        Contradiction(
            "Der Termin ist am Montag. <> Der Termin ist am Dienstag."
        ),
    )


def test_new_hypothesis_is_added():
    revision = GuardianUnderstandingService().advance(
        EMPTY,
        update(
            "Vielleicht liegt es am Arbeitsweg.",
            operation(
                UnderstandingOperationType.ADD_HYPOTHESIS,
                value="Der Arbeitsweg könnte eine Rolle spielen.",
            ),
        ),
    )
    assert revision.state.hypotheses == (
        Hypothesis("Der Arbeitsweg könnte eine Rolle spielen."),
    )


def test_rejected_hypothesis_remains_visible_as_rejected():
    state = UnderstandingState(
        (),
        (Hypothesis("Ein Umzug könnte helfen."),),
        (),
        (),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Nein, ein Umzug kommt nicht infrage.",
            operation(
                UnderstandingOperationType.REJECT_HYPOTHESIS,
                target="Ein Umzug könnte helfen.",
            ),
        ),
    )
    assert revision.state.hypotheses == (
        Hypothesis(
            "Ein Umzug könnte helfen.",
            HypothesisStatus.REJECTED,
        ),
    )


def test_closed_unknown_remains_visible_as_closed():
    state = UnderstandingState(
        (),
        (),
        (Unknown("Wann findet das Gespräch statt?"),),
        (),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Das Gespräch ist am Freitag.",
            operation(
                UnderstandingOperationType.CLOSE_UNKNOWN,
                target="Wann findet das Gespräch statt?",
            ),
        ),
    )
    assert revision.state.unknowns == (
        Unknown(
            "Wann findet das Gespräch statt?",
            UnknownStatus.CLOSED,
        ),
    )


def test_changed_goal_marks_old_goal_and_keeps_new_goal_current():
    state = UnderstandingState(
        (),
        (),
        (),
        (),
        (Goal("Die Optionen verstehen."),),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Ich möchte zuerst den zeitlichen Ablauf verstehen.",
            operation(
                UnderstandingOperationType.CHANGE_GOAL,
                target="Die Optionen verstehen.",
                value="Den zeitlichen Ablauf verstehen.",
            ),
        ),
    )
    assert revision.state.goals == (
        Goal("Die Optionen verstehen.", GoalStatus.CHANGED),
        Goal("Den zeitlichen Ablauf verstehen."),
    )


def test_unsubstantiated_statement_changes_nothing():
    state = UnderstandingState(
        (Fact("Ich wohne in Bonn."),),
        (),
        (Unknown("Wie lange bleibe ich dort?"),),
        (),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update("Dazu kann ich gerade nichts Weiteres sagen."),
    )
    assert revision.state == state
    assert revision.changes == ()


def test_revision_contains_exactly_one_understanding_question():
    revision = GuardianUnderstandingService().advance(
        EMPTY,
        update(
            "Vielleicht ändere ich meine Arbeitszeit.",
            operation(
                UnderstandingOperationType.ADD_HYPOTHESIS,
                value="Eine andere Arbeitszeit könnte helfen.",
            ),
        ),
    )
    assert revision.understanding_question.count("?") == 1
    assert revision.understanding_question.endswith("?")


def test_revision_exposes_no_decision_routing_or_activation():
    revision = GuardianUnderstandingService().advance(
        EMPTY,
        update("Ich bin noch unsicher."),
    )
    forbidden = {
        "decision",
        "routing",
        "workflow",
        "capability",
        "activation",
    }
    assert forbidden.isdisjoint(vars(revision))
    assert forbidden.isdisjoint(vars(revision.state))


def test_identical_state_and_update_produce_identical_revision():
    state = UnderstandingState(
        (),
        (Hypothesis("Die Entfernung könnte wichtig sein."),),
        (),
        (),
        (),
    )
    change = update(
        "Die Entfernung ist wohl weniger wichtig.",
        operation(
            UnderstandingOperationType.WEAKEN_HYPOTHESIS,
            target="Die Entfernung könnte wichtig sein.",
        ),
    )
    service = GuardianUnderstandingService()
    assert service.advance(state, change) == service.advance(state, change)


def test_fact_can_be_marked_contradictory_without_silent_replacement():
    state = UnderstandingState((Fact("Die Wohnung ist frei."),), (), (), (), ())
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Die Vermieterin sagt, die Wohnung sei belegt.",
            operation(
                UnderstandingOperationType.MARK_FACT_CONTRADICTORY,
                target="Die Wohnung ist frei.",
                value="Die Wohnung ist belegt.",
            ),
        ),
    )
    assert revision.state.facts == (
        Fact("Die Wohnung ist frei.", FactStatus.CONTRADICTED),
    )
    assert revision.state.contradictions == (
        Contradiction("Die Wohnung ist frei. <> Die Wohnung ist belegt."),
    )


def test_hypothesis_can_be_refined_and_then_weakened():
    state = UnderstandingState(
        (),
        (Hypothesis("Die Arbeit könnte belasten."),),
        (),
        (),
        (),
    )
    service = GuardianUnderstandingService()
    refined = service.advance(
        state,
        update(
            "Vor allem die langen Meetings belasten mich.",
            operation(
                UnderstandingOperationType.REFINE_HYPOTHESIS,
                target="Die Arbeit könnte belasten.",
                value="Lange Meetings könnten belasten.",
            ),
        ),
    )
    weakened = service.advance(
        refined.state,
        update(
            "In dieser Woche waren die Meetings weniger belastend.",
            operation(
                UnderstandingOperationType.WEAKEN_HYPOTHESIS,
                target="Lange Meetings könnten belasten.",
            ),
        ),
    )
    assert weakened.state.hypotheses == (
        Hypothesis("Die Arbeit könnte belasten.", HypothesisStatus.REFINED),
        Hypothesis(
            "Lange Meetings könnten belasten.",
            HypothesisStatus.WEAKENED,
        ),
    )


def test_unknown_can_be_refined_without_removing_original():
    state = UnderstandingState(
        (),
        (),
        (Unknown("Welche Unterlagen fehlen?"),),
        (),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Unklar ist nur noch, ob die Vollmacht fehlt.",
            operation(
                UnderstandingOperationType.REFINE_UNKNOWN,
                target="Welche Unterlagen fehlen?",
                value="Fehlt die Vollmacht?",
            ),
        ),
    )
    assert revision.state.unknowns == (
        Unknown("Welche Unterlagen fehlen?", UnknownStatus.REFINED),
        Unknown("Fehlt die Vollmacht?"),
    )


def test_goal_can_be_confirmed_and_later_marked_not_current():
    state = UnderstandingState((), (), (), (), (Goal("Die Lage verstehen."),))
    service = GuardianUnderstandingService()
    confirmed = service.advance(
        state,
        update(
            "Ja, ich möchte die Lage verstehen.",
            operation(
                UnderstandingOperationType.CONFIRM_GOAL,
                target="Die Lage verstehen.",
            ),
        ),
    )
    inactive = service.advance(
        confirmed.state,
        update(
            "Dieses Ziel ist im Moment nicht mehr aktuell.",
            operation(
                UnderstandingOperationType.DEACTIVATE_GOAL,
                target="Die Lage verstehen.",
            ),
        ),
    )
    assert inactive.state.goals == (
        Goal("Die Lage verstehen.", GoalStatus.NOT_CURRENT),
    )


def test_existing_contradictions_survive_unrelated_updates():
    state = UnderstandingState(
        (),
        (),
        (),
        (Contradiction("A <> B"),),
        (),
    )
    revision = GuardianUnderstandingService().advance(
        state,
        update(
            "Außerdem ist heute Donnerstag.",
            operation(
                UnderstandingOperationType.ADD_FACT,
                value="Heute ist Donnerstag.",
            ),
        ),
    )
    assert revision.state.contradictions == (Contradiction("A <> B"),)
