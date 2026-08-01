from pathlib import Path
import json
import socket

from family_care_review_ui import FamilyCareReviewSession
from family_care_review_ui.web import HTML


def test_reference_case_is_loaded_and_marked_anonymized():
    view = FamilyCareReviewSession().view()
    assert view["case"]["anonymized"] is True
    assert "Anonymisierte" in view["case"]["notice"]


def test_understanding_categories_remain_separate_and_visible():
    view = FamilyCareReviewSession().view()["understanding"]
    assert "Eine kognitive Einschränkung könnte bestehen." in view["hypotheses"]
    assert "Eine kognitive Einschränkung könnte bestehen." not in view["facts"]
    assert view["unknowns"]
    assert view["contradictions"]


def test_only_explicit_contributions_dependencies_people_and_documents_are_shown():
    view = FamilyCareReviewSession().view()["cross_domain"]
    assert len(view["contributions"]) == 7
    assert len(view["dependencies"]) == 2
    assert len(view["people"]) == 3
    assert view["documents"] == ("user-vault://family-care-reference/poa",)


def test_exactly_one_current_question_and_answered_questions_do_not_repeat():
    session = FamilyCareReviewSession()
    questions = []
    for _ in range(6):
        view = session.view()
        assert isinstance(view["conversation"]["current_question"], str)
        questions.append(view["conversation"]["current_question"])
        session.advance()
    assert len(set(questions)) == 6
    assert session.view()["conversation"]["current_question"] is None


def test_reference_questions_are_clear_and_keep_ids_and_bindings():
    from tests.test_family_care_end_to_end_reference import POINTS, build_reference_journey

    reference = build_reference_journey()
    expected = (
        (
            "understanding-question-family-care-support",
            "Welche Hilfe braucht die betroffene Person nach der Entlassung konkret?",
        ),
        (
            "understanding-question-family-care-roles",
            "Ist geklärt, wer in der Familie welche Aufgaben übernimmt?",
        ),
        (
            "understanding-question-family-care-representative",
            "Ist geklärt, wer Entscheidungen übernehmen darf, wenn die betroffene Person das selbst nicht kann?",
        ),
        (
            "understanding-question-family-care-medical",
            "Wer ist die Ansprechperson für die medizinische Nachsorge?",
        ),
        (
            "understanding-question-family-care-housing",
            "Wie wohnt die betroffene Person aktuell?",
        ),
        (
            "understanding-question-family-care-finance",
            "Welche zusätzlichen Kosten oder finanziellen Belastungen sind bereits bekannt?",
        ),
    )

    actual = tuple(
        (journey.current_question.question_id, journey.current_question.text)
        for journey in reference["journeys"]
    )
    assert actual == expected
    assert tuple(
        journey.current_question.point_id for journey in reference["journeys"]
    ) == tuple(point.point_id for point in POINTS)
    assert tuple(turn.question_id for turn in reference["turns"]) == tuple(
        question_id for question_id, _ in expected
    )


def test_human_main_view_questions_use_no_internal_terms():
    forbidden = (
        "Vertretungsgrundlage",
        "Domain Contribution",
        "Dependency",
        "Professional Review",
        "Wohneignung",
        "Understanding State",
    )
    session = FamilyCareReviewSession()
    questions = []
    for _ in range(6):
        question = session.view()["conversation"]["current_question"]
        assert question is not None
        assert question.count("?") == 1
        questions.append(question)
        session.advance()
    assert len(questions) == 6
    assert not any(term in question for term in forbidden for question in questions)
    guardian_text = json.dumps(
        FamilyCareReviewSession().view()["guardian_view"], ensure_ascii=False
    )
    assert not any(term in guardian_text for term in forbidden)


def test_prepared_step_uses_existing_services_without_automatic_state_change():
    calls = []
    from tests.test_family_care_end_to_end_reference import build_reference_journey

    def factory():
        calls.append("build")
        return build_reference_journey()

    session = FamilyCareReviewSession(factory)
    before = session.view()["understanding"]["facts"]
    assert len(calls) == 1
    session.advance()
    assert len(calls) == 2
    assert len(session.view()["understanding"]["facts"]) == len(before) + 1


def test_no_automatic_proposal_resolution_or_revision_is_exposed():
    session = FamilyCareReviewSession()
    initial = session.view()["source_chain"]
    assert initial["proposal"] is None
    assert initial["resolution"] is None
    assert initial["revision"] is None
    assert session.step == 0


def test_journey_status_and_professional_reviews_follow_existing_bindings():
    session = FamilyCareReviewSession()
    assert session.view()["journey"]["status"] == "NEEDS_CLARIFICATION"
    for _ in range(6): session.advance()
    view = session.view()
    assert view["journey"]["status"] == "CROSS_DOMAIN_REVIEW_PREPARATION_READY"
    assert len(view["cross_domain"]["reviews"]) == 4
    assert view["journey"]["professional_review"] is not None


def test_source_chain_is_complete_or_transparently_empty():
    session = FamilyCareReviewSession()
    assert all(value is None for value in session.view()["source_chain"].values())
    session.advance()
    chain = session.view()["source_chain"]
    assert all(chain[key] is not None for key in ("statement", "understanding_element", "open_point", "question", "answer", "proposal", "resolution", "revision", "updated_state"))
    session.advance(); session.advance()
    assert session.view()["source_chain"]["revision"] is None
    assert session.view()["source_chain"]["updated_state"] is None


def test_reset_restores_initial_in_memory_state():
    session = FamilyCareReviewSession(); initial = session.view()
    session.advance(); session.advance()
    assert session.step == 2
    assert session.reset() == initial


def test_identical_state_renders_deterministically():
    assert FamilyCareReviewSession().view() == FamilyCareReviewSession().view()


def test_guardian_view_uses_only_existing_typed_content():
    session = FamilyCareReviewSession()
    view = session.view()
    guardian = view["guardian_view"]
    cross_domain = view["cross_domain"]

    assert guardian["summary"] in view["understanding"]["statements"]
    assert guardian["known"] == view["understanding"]["facts"]
    assert len(guardian["open"]) == len(cross_domain["open_points"] + cross_domain["deferred_points"])
    assert guardian["open"][2] == (
        "Es ist noch offen, wer Entscheidungen übernehmen darf, wenn die "
        "betroffene Person das selbst nicht kann."
    )
    assert guardian["next_checks"] == cross_domain["reviews"] + cross_domain["steps"]
    assert guardian["involved"] == cross_domain["people"]


def test_guardian_view_has_exactly_one_current_question_and_stable_progress():
    session = FamilyCareReviewSession()
    for step in range(6):
        view = session.view()
        assert isinstance(view["conversation"]["current_question"], str)
        assert view["guardian_view"]["progress"] == f"Schritt {step} von 6"
        session.advance()
    assert session.view()["conversation"]["current_question"] is None
    assert session.view()["guardian_view"]["progress"] == "Schritt 6 von 6"


def test_technical_review_view_remains_complete_behind_details():
    assert "Prüfansicht · Details anzeigen" in HTML
    for heading in (
        "Understanding",
        "Cross-Domain",
        "Journey und Review",
        "Fachliche Grenzen",
        "Quellenkette des letzten Schritts",
        "Technische Referenzen",
    ):
        assert heading in HTML


def test_human_guardian_sections_are_static_and_present_once():
    for heading in (
        "Was wir bereits wissen",
        "Was noch offen ist",
        "Was als Nächstes geprüft werden sollte",
        "Wer einbezogen werden muss",
    ):
        assert HTML.count(heading) == 1
    assert HTML.count("Aktuelle Guardian-Frage") == 1


def test_review_usage_has_no_file_or_network_side_effects(monkeypatch, tmp_path):
    before = tuple(Path.cwd().glob("**/*"))
    def forbidden(*args, **kwargs): raise AssertionError("side effect")
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    session = FamilyCareReviewSession(); session.advance(); session.reset()
    assert tuple(Path.cwd().glob("**/*")) == before
