from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION = ROOT / "governance/ratification-adr-0064-a1.md"
ADR = ROOT / "knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_ratification_has_exact_identity_status_role_and_times():
    text = read(RATIFICATION)
    assert "GOV-RATIFICATION-ADR-0064-A1-V1" in text
    assert "RATIFIZIERUNG DOKUMENTIERT – KEINE IMPLEMENTIERUNGSFREIGABE" in text
    assert "03.08.2026, 21:56:17 Uhr" in text
    assert "03.08.2026, 21:57:10 Uhr" in text
    assert "Europe/Berlin (CEST, UTC+02:00)" in text
    assert "Entscheidungsrolle: Institutionsgründer" in text
    assert "gegenwärtig und keine rückwirkende Entscheidung" in text


def test_ratification_confirms_closed_scope_and_role_boundaries():
    text = read(RATIFICATION)
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
    assert "REVIEWER` ohne Decision Class" in text
    assert "ohne neue institutionelle Entscheidungsbefugnis" in text
    assert "fehlende Nennung Nichtfreigabe bedeutet" in text


def test_ratification_does_not_approve_implementation_or_stash_application():
    text = read(RATIFICATION)
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "institutionelle Implementierungsfreigabe oder Implementierung" in text
    assert "Anwendung, Teilanwendung oder technische Übernahme" in text
    assert "Stash-Anwendung gilt niemals als Implementierungsgenehmigung" in text
    assert "Fortsetzung der ADR-0064-Implementierung" in text
    assert "ADR-0065 bleibt nicht begonnen und gesperrt" in text


def test_stash_identity_and_recovery_sequence_are_documented():
    text = read(RATIFICATION)
    assert "ADR-0064 partial implementation blocked before closed taxonomies" in text
    assert "stash@{0}" in text
    assert "f1e6f58aedf31d8617c83b68f9ea899c9aae9e43" in text
    for phrase in (
        "gesonderte institutionelle Implementierungsfreigabe",
        "Dokumentation dieser Freigabe",
        "Commit",
        "Push",
        "separater Implementierungsauftrag",
        "vollständige Neuprüfung des Stash",
    ):
        assert phrase in text


def test_ratification_remains_separate_from_later_implementation_approval():
    text = read(ADR)
    ratification = read(RATIFICATION)
    assert "RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in text
    assert "GOV-RATIFICATION-ADR-0064-A1-V1" in text
    assert "KEINE IMPLEMENTIERUNGSFREIGABE" in ratification
    assert "Stash an" in ratification
    assert "übernimmt keine Primitive" in ratification


def test_ratification_has_no_personal_or_executing_power():
    text = read(RATIFICATION)
    for phrase in (
        "natürliche Personen",
        "Leistungsbewertungen",
        "Sanktion",
        "Observation",
        "Capability Invocation",
        "Runtime",
        "personenbezogene Verarbeitung",
    ):
        assert phrase in text
    assert "Prüffrage Null bleibt verbindlich" in text


def test_ratification_document_did_not_itself_create_productive_implementation():
    text = read(RATIFICATION)
    assert "keine implementierung" in text.lower()
    assert (ROOT / "governance/governance_decision_incident_evidence.py").is_file()
    assert tuple((ROOT / "governance/decisions").iterdir()) == (ROOT / "governance/decisions/README.md",)
    assert tuple((ROOT / "governance/incidents").iterdir()) == (ROOT / "governance/incidents/README.md",)
