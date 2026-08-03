from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/guardian-life-domain-model-candidate.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_candidate_is_registered_dormant_and_unapproved():
    text = read(CANDIDATE)
    for phrase in (
        "Registriert",
        "Nicht geplant",
        "Nicht implementiert",
        "Kein Implementierungsauftrag",
        "Keine Implementierungsfreigabe",
        "Vorher bleibt der Kandidat ausdrücklich ruhend",
    ):
        assert phrase in text


def test_e6_exception_is_limited_to_registration():
    text = read(CANDIDATE)
    assert "dokumentierte Ausnahme zu ADR-0046 E6" in text
    assert "Ausnahme gilt ausschließlich für die Registrierung" in text
    assert "ADR-0046 und E6 bleiben unverändert" in text


def test_constitutional_core_is_jurisdiction_faithful_and_language_neutral():
    text = read(CANDIDATE)
    for phrase in (
        "kanonische Typ-ID",
        "Jurisdiktionskennzeichen",
        "definierte Wirksamkeitsregeln",
        "typisierte Relationen",
        "Sprache ist ausschließlich Darstellung",
        "Rechtsnatur, Wirksamkeitsbedingungen",
        "Semantik oder Identität",
    ):
        assert phrase in text


def test_model_grows_only_from_real_cases_and_starts_with_power_of_attorney():
    text = " ".join(read(CANDIDATE).split())
    for phrase in (
        "realer Lebensbereiche und validierter Journeys",
        "Theoretische Universalmodelle",
        "abstrakte Vollontologie",
        "Erster registrierter Kernbereich: Vorsorgevollmacht",
    ):
        assert phrase in text


def test_international_legal_institutes_require_distinct_objects_and_evidence():
    text = " ".join(read(CANDIDATE).split())
    for phrase in (
        "Internationale Rechtsinstitute sind keine Synonyme",
        "eigenständige typisierte Domänenobjekte",
        "eigene typisierte Mapping-Objekte und eigene Evidenz",
    ):
        assert phrase in text


def test_activation_and_implementation_boundaries_are_complete():
    text = read(CANDIDATE)
    for phrase in (
        "produktive B2-Runtime",
        "stabile Conversation-Architektur",
        "dokumentierter Aktivierungsbeschluss",
        "keine Runtime, APIs, Datenbankmodelle",
        "juristischen Inhalte, Gesprächsführungen oder Implementierungsaufträge",
    ):
        assert phrase in text
    assert "keine ADR" in text
    assert not (ROOT / "governance/guardian_life_domain_model.py").exists()
