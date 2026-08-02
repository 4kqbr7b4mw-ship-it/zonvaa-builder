from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/guardian-accountability-explanation-candidate.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_candidate_is_registered_but_dormant_and_unapproved():
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
    assert "E6 bleibt unverändert in Kraft" in text


def test_constitutional_core_requires_evidence_references_and_no_second_truth():
    text = read(CANDIDATE)
    for phrase in (
        "vollständig aus vorhandenen Evidenzartefakten ableitbar",
        "Beobachtungsumfang überschreiten",
        "Jede Aussage trägt ihre Artefaktreferenz",
        "Eine Erklärung ohne Referenz kompiliert nicht",
        "Die Erklärung entscheidet nichts",
        "Die Erklärung weiß nichts",
        "Die Erklärung liest",
        "kein zweites Modell der Wahrheit",
    ):
        assert phrase in text


def test_no_fabrication_is_only_an_open_consolidation_candidate():
    text = read(CANDIDATE)
    for phrase in (
        "GOV-NO-FABRICATION-1",
        "offener Konsolidierungskandidat; keine Governance-Regel",
        "keine erfundenen Quellen",
        "keine erfundenen Gefühle",
        "keine erfundenen Nachweise",
        "keine erfundene Rechenschaft",
        "nicht auf einem benennbaren Artefakt",
        "weder bindend noch freigegeben",
    ):
        assert phrase in text


def test_activation_requires_runtime_accountability_and_a_decision():
    text = read(CANDIDATE)
    for phrase in (
        "produktive B2-Runtime",
        "erste reale Rechenschaftspflichten",
        "dokumentierter Aktivierungsbeschluss",
        "Keine Runtime, API oder Erklärungsschicht",
    ):
        assert phrase in text


def test_no_adr_contract_api_or_implementation_file_is_added():
    text = read(CANDIDATE)
    assert "keine ADR" in text
    assert "keine Governance-Regel" in text
    assert not (ROOT / "governance/accountability_explanation.py").exists()
