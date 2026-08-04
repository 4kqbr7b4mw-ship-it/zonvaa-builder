from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0064-governance-decision-incident-evidence-constitution-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0064_is_ratified_approved_implemented_and_validated():
    text = read(ADR)
    assert "ADR-0064 – Governance Decision and Incident Evidence Constitution v1" in text
    assert (
        "RATIFIZIERT – IMPLEMENTIERUNG BEGRENZT FREIGEGEBEN – "
        "IMPLEMENTIERT UND VALIDIERT"
    ) in text
    assert "GOV-RATIFICATION-ADR-0064-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-V1" in text


def test_adr_0064_implementation_approval_is_scoped_and_non_executing():
    text = read(ROOT / "governance/institutional-implementation-approval-adr-0064.md")
    normalized = " ".join(text.split())
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG" in text
    assert "03.08.2026, 20:36:55 Uhr" in text
    assert "03.08.2026, 20:37:16 Uhr" in text
    assert "## Freigegeben" in text
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "weiterhin nicht implementiert" in text
    assert "keinen Governance Decision Record" in normalized
    assert "keine Governance Incident Evidence" in normalized
    assert "ADR-0065" in text
    assert "nach nachweisbarem Push" in text


def test_adr_0064_ratification_record_separates_scope_and_times():
    text = read(ROOT / "governance/ratification-adr-0064.md")
    assert "RATIFIZIERUNG DOKUMENTIERT – KEINE IMPLEMENTIERUNGSFREIGABE" in text
    assert "03.08.2026, 19:34:23 Uhr" in text
    assert "03.08.2026, 19:34:28 Uhr" in text
    assert "## Freigegeben" in text
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "Änderung des ADR-0059-Nachweisstatus" in text
    assert "heutige institutionelle Bestätigung von ADR-0059" in text
    assert "Commit" in text
    assert "Push" in text


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
    assert "ratifizierten Verwahrorte sind kanonisch" in text
    assert "ADR-0052 Runtime Incidents" in text
    assert "Operational Memory" in text


def test_complete_implementation_is_bounded_by_both_ratified_adrs():
    module = ROOT / "governance/governance_decision_incident_evidence.py"
    recovery = ROOT / "governance/adr-0064-implementation-blockers.md"
    assert module.is_file()
    assert recovery.is_file()
    source = read(module)
    assert "class GovernanceIncidentClass" in source
    assert "class GovernanceDecisionRecord" in source
    assert "class GovernanceIncidentEvidence" in source
    assert "class GovernanceDecisionClass" in source
    text = read(ADR)
    assert "GOV-NO-FABRICATION-1` bleibt ein offener" in text
    assert "diese ADR ratifiziert ihn nicht" in text
    assert "Antwort: **Nein.**" in text


def test_adr_0064_a1_is_separately_ratified_approved_and_implemented():
    supplement = " ".join(
        read(
            ROOT
            / "knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md"
        ).split()
    )
    assert "RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in supplement
    assert "GOV-RATIFICATION-ADR-0064-A1-V1" in supplement
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1" in supplement
    assert "ADR-0064 bleibt der ratifizierte Haupt-ADR" in supplement
    assert "ADR-0065" in supplement
