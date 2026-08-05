from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md"
VALIDATION = ROOT / "governance/adr-0064-a1-architecture-validation.md"
RECOVERY = ROOT / "governance/adr-0064-implementation-blockers.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0064_a1_is_ratified_approved_implemented_and_validated():
    text = read(ADR)
    normalized = " ".join(text.split())
    assert "ADR-0064-A1 – Governance Decision and Incident Closed Taxonomies v1" in text
    assert "RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in text
    assert "GOV-RATIFICATION-ADR-0064-A1-V1" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1" in text
    assert "ADR-0064 bleibt der ratifizierte Haupt-ADR" in normalized


def test_all_closed_taxonomy_families_are_documented():
    text = read(ADR)
    for heading in (
        "Governance Decision Classes",
        "Institutionelle Entscheidungsrollen",
        "Governance-Schritte",
        "Scope-Verfassung",
        "Governance-Abweichungscodes",
        "Vorhandene Evidence-Arten",
        "Missing-Evidence-Arten und Status",
        "Auswirkungscodes",
        "Korrekturfolgeschritte",
        "Dokumentationsstände",
        "Beobachtungs- und Aussageumfänge",
        "Provenienz-Artefaktklassen und Kontexte",
        "Offene Entscheidungsfragen",
    ):
        assert heading in text


def test_decision_classes_and_roles_are_minimal_and_closed():
    text = read(ADR)
    for code in (
        "ARCHITECTURE_RATIFICATION",
        "INSTITUTIONAL_IMPLEMENTATION_APPROVAL",
        "COMMIT_APPROVAL",
        "PUSH_APPROVAL",
        "INSTITUTION_FOUNDER",
        "CHIEF_ARCHITECT",
        "REVIEWER",
    ):
        assert f"`{code}`" in text
    assert "REVIEWER` | reine Gutachter" in text
    assert "keine Decision Class" in text
    assert "Rollen sind geschlossene institutionelle Rollen" in text


def test_governance_sequence_is_exactly_eighteen_steps():
    text = read(ADR)
    sequence = text.split("## 7. Governance-Schritte", 1)[1].split("## 8.", 1)[0]
    assert "exakt 18" in sequence
    assert sequence.count("| 1 |") == 1
    for number in range(2, 19):
        assert f"| {number} |" in sequence
    assert "`IMPLEMENTATION_APPROVAL_PUSH`" in sequence
    assert "`SEPARATE_IMPLEMENTATION_ORDER`" in sequence


def test_scope_has_no_free_or_global_semantics():
    text = read(ADR)
    assert "Gewählt wird Variante D" in text
    assert "`GRANTED_SCOPE`" in text
    assert "`EXCLUDED_SCOPE`" in text
    assert "Fehlende Nennung ist Nichtfreigabe" in text
    assert "globale Fachcodeliste wäre eine zweite Scope-Verfassung" in text
    assert "freie Strings sind weder beweisbar noch geschlossen" in text


def test_each_code_family_has_source_and_negative_boundary():
    text = read(ADR)
    for phrase in (
        "Quelle | Unzulässige Verwendung",
        "Quelle und Negativabgrenzung",
        "Quelle | Negativabgrenzung",
        "Kann nicht bestätigen",
        "Nicht bestätigbare Aussage",
        "Unzulässige Deutung",
        "Keine Wirkung",
    ):
        assert phrase in text
    assert "Jeder v1-Wert besitzt eine benennbare Grundlage" in text


def test_evidence_and_missing_evidence_remain_separate():
    text = read(ADR)
    assert "Commit-Identität und Git-Inhalt" in text
    assert "menschliche Entscheidung oder damaligen Push" in text
    assert "`HISTORICALLY_NOT_RECONSTRUCTABLE`" in text
    assert "verändert aber Incident und Historie nicht" in text
    assert "Provenienz ist keine Evidence-Art" in text


def test_no_personal_sanction_or_automatic_power():
    text = " ".join(read(ADR).split())
    for phrase in (
        "niemals Namen, Konten, E-Mail-Adressen oder Personenobjekte",
        "keine Schweregrade, Risikoscores oder Sanktionsvorschläge",
        "keine automatische Record- oder Incident-Erzeugung",
        "Capability Invocation",
        "Runtime",
        "personenbezogene Verarbeitung",
    ):
        assert phrase in text


def test_stash_was_rechecked_and_remains_non_canonical_recovery_evidence():
    text = read(ADR)
    assert "Der Stash ist keine kanonische Implementierung" in text
    assert "Eine spätere bloße Wiederanwendung wäre keine" in text
    assert "Implementierungsgenehmigung" in text
    assert "vollständige Neuprüfung" in text


def test_validation_is_completed_non_executing_and_null_question_is_no():
    text = read(VALIDATION)
    assert "ARCHITEKTUR VALIDIERT – RATIFIZIERT – IMPLEMENTIERUNG FREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT" in text
    assert "kontrolliert" in text
    assert "neu gegen beide ADRs geprüft" in text
    assert "Antwort: **Nein.**" in text
    assert "ADR-0065 bleibt nicht begonnen und" in text
    assert "gesperrt" in text


def test_productive_contract_and_empty_documentation_locations_exist():
    assert (ROOT / "governance/governance_decision_incident_evidence.py").is_file()
    assert (ROOT / "governance/decisions/README.md").is_file()
    assert (ROOT / "governance/incidents/README.md").is_file()
    assert {path.name for path in (ROOT / "governance/decisions").iterdir()} == {
        "README.md",
        "GOV-B2-NORMATIVE-STATUS-CONSOLIDATION-APPROVAL-V1.md",
    }
    assert tuple((ROOT / "governance/incidents").iterdir()) == (ROOT / "governance/incidents/README.md",)


def test_stash_recovery_rechecks_all_twenty_files_without_automatic_adoption():
    text = read(RECOVERY)
    assert "GOV-ADR-0064-IMPLEMENTATION-RECOVERY-V1" in text
    assert "f1e6f58aedf31d8617c83b68f9ea899c9aae9e43" in text
    assert text.count("| `") == 20
    assert "unverändert kompatibel" in text
    assert "angepasst" in text
    assert "ersetzt" in text
    assert "keine historischen Decision Records" in text
    assert "ADR-0065 bleibt nicht begonnen und gesperrt" in text
