from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0064-governance-decision-incident-evidence-constitution-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0064_is_formal_but_unratified_and_unimplemented():
    text = read(ADR)
    assert "ADR-0064 – Governance Decision and Incident Evidence Constitution v1" in text
    assert "VORGESCHLAGEN – NICHT RATIFIZIERT" in text
    assert "NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text


def test_decision_record_and_incident_evidence_are_separate():
    text = read(ADR)
    assert "## 5. Governance Decision Record" in text
    assert "## 6. Governance Incident Evidence" in text
    assert "Decision Record, Incident Evidence und Prozessdokumentation bleiben getrennt" in text
    assert "fällt selbst keine Entscheidung" in text


def test_incident_classes_are_closed_and_without_personal_effect():
    text = read(ADR)
    for code in (
        "IMPLEMENTATION_BEFORE_RATIFICATION_EVIDENCE",
        "IMPLEMENTATION_BEFORE_IMPLEMENTATION_APPROVAL",
        "IMPLEMENTATION_BEFORE_APPROVAL_PUSH",
        "COMMIT_WITHOUT_COMMIT_APPROVAL",
        "PUSH_WITHOUT_PUSH_APPROVAL",
        "SCOPE_EXCEEDED",
        "GOVERNANCE_EVIDENCE_MISSING",
        "STATUS_MISREPRESENTED",
        "WORK_STATE_RETROACTIVELY_REINTERPRETED",
        "DECISION_TIME_NOT_DOCUMENTED",
        "DECISION_AND_DOCUMENTATION_TIME_NOT_SEPARATED",
    ):
        assert code in text
    assert "Natürliche Personen werden nicht als fachliche" in text
    assert "Mitarbeiter- oder" in text
    assert "Leistungsbewertung" in text


def test_adr_0059_status_and_unknown_times_are_exact():
    text = read(ADR)
    assert "Kategorie 3 – nur indirekte Governance-Evidenz vorhanden" in text
    for field in (
        "historisches Beschlussdatum: `UNBEKANNT`",
        "historische Beschlusszeit: `UNBEKANNT`",
        "historische Zeitzone: `UNBEKANNT`",
        "historische Entscheidungsrolle: `UNBEKANNT`",
    ):
        assert field in text
    assert "wird jetzt weder gefasst noch dokumentiert" in text


def test_canonical_locations_are_proposed_and_separate_from_runtime():
    text = read(ADR)
    assert "governance/decisions/" in text
    assert "governance/incidents/" in text
    assert "erst durch Ratifizierung kanonisch" in text
    assert "ADR-0052 Runtime Incidents" in text
    assert "Operational Memory" in text


def test_no_governance_incident_implementation_or_silent_governance_rule():
    assert not list((ROOT / "governance").glob("*governance*incident*.py"))
    text = read(ADR)
    assert "GOV-NO-FABRICATION-1` bleibt ein offener" in text
    assert "diese ADR ratifiziert ihn nicht" in text
    assert "Antwort: **Nein.**" in text
