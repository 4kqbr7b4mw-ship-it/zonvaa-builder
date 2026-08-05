from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "governance/institutional-implementation-approval-adr-0064-a1.md"
ADR = ROOT / "knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_approval_has_exact_identity_status_role_and_times():
    text = read(APPROVAL)
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1" in text
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG – NOCH NICHT IMPLEMENTIERT" in text
    assert "03.08.2026, 23:04:51 Uhr" in text
    assert "03.08.2026, 23:05:39 Uhr" in text
    assert "Europe/Berlin" in text
    assert "Entscheidungsrolle: Institutionsgründer" in text
    assert "Der Beschluss ist nicht rückwirkend" in text


def test_approval_is_exactly_scoped_to_ratified_taxonomies():
    text = " ".join(read(APPROVAL).split())
    for code in (
        "ARCHITECTURE_RATIFICATION",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL",
        "COMMIT_APPROVAL",
        "PUSH_APPROVAL",
        "INSTITUTION_FOUNDER",
        "CHIEF_ARCHITECT",
        "REVIEWER",
        "GRANTED_SCOPE",
        "EXCLUDED_SCOPE",
    ):
        assert code in text
    assert "18 getrennten Governance-Schritte" in text
    assert "fehlende Nennung als Nichtfreigabe" in text
    assert "ohne neue institutionelle Entscheidungsbefugnis" in text


def test_approval_does_not_implement_or_apply_stash():
    text = " ".join(read(APPROVAL).split())
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "Fortsetzung der Implementierung in diesem Auftrag" in text
    assert "Anwendung, Pop, Drop, Umbenennung oder Veränderung" in text
    assert "Stash-Anwendung gilt niemals als Implementierungsgenehmigung" in text
    assert "Unvereinbare Bestandteile dürfen nicht übernommen werden" in text
    assert "erst nach ausdrücklicher Einzelprüfung" in text


def test_approval_requires_push_before_separate_implementation_order():
    text = read(APPROVAL)
    assert "erst nach Commit und nachweisbarem" in text
    assert "Push dieser Freigabe" in text
    assert "separater Implementierungsauftrag" in text
    assert "vollständigen Stash gegen" in text
    assert "ADR-0064 und ADR-0064-A1 neu prüfen" in text


def test_stash_identity_and_noncanonical_status_are_exact():
    text = read(APPROVAL)
    assert "ADR-0064 partial implementation blocked before closed taxonomies" in text
    assert "stash@{0}" in text
    assert "f1e6f58aedf31d8617c83b68f9ea899c9aae9e43" in text
    assert "nicht kanonischer" in text


def test_adr_status_records_the_later_separate_implementation():
    text = " ".join(read(ADR).split())
    assert "RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in text
    assert "GOV-RATIFICATION-ADR-0064-A1-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1" in text
    assert "NOCH NICHT IMPLEMENTIERT" in read(APPROVAL)


def test_approval_excludes_power_personal_data_and_adr_0065():
    text = read(APPROVAL)
    for phrase in (
        "automatische Entscheidungen",
        "natürliche Personen",
        "Leistungsbewertungen",
        "Sanktionen",
        "Observation",
        "Capability Invocation",
        "Runtime",
        "personenbezogene Verarbeitung",
        "ADR-0065 bleibt nicht begonnen und gesperrt",
    ):
        assert phrase in text


def test_approval_document_did_not_itself_create_productive_implementation():
    text = read(APPROVAL)
    assert "NOCH NICHT IMPLEMENTIERT" in text
    assert (ROOT / "governance/governance_decision_incident_evidence.py").is_file()
    assert {path.name for path in (ROOT / "governance/decisions").iterdir()} == {
        "README.md",
        "GOV-B2-NORMATIVE-STATUS-CONSOLIDATION-APPROVAL-V1.md",
        "GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1.md",
    }
    assert tuple((ROOT / "governance/incidents").iterdir()) == (ROOT / "governance/incidents/README.md",)
