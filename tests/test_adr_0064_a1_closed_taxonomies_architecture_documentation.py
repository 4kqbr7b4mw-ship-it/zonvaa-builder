from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0064-A1-governance-decision-incident-closed-taxonomies-v1.md"
VALIDATION = ROOT / "governance/adr-0064-a1-architecture-validation.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0064_a1_is_ratified_and_approved_but_not_implemented():
    text = read(ADR)
    normalized = " ".join(text.split())
    assert "ADR-0064-A1 – Governance Decision and Incident Closed Taxonomies v1" in text
    assert "RATIFIZIERT – INSTITUTIONELL IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text
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


def test_stash_is_not_implementation_or_approval():
    text = read(ADR)
    assert "Der Stash ist keine kanonische Implementierung" in text
    assert "Eine spätere bloße Wiederanwendung wäre keine" in text
    assert "Implementierungsgenehmigung" in text
    assert "vollständige Neuprüfung" in text


def test_validation_is_non_executing_and_null_question_is_no():
    text = read(VALIDATION)
    assert "ARCHITEKTUR VALIDIERT – RATIFIZIERT – IMPLEMENTIERUNG FREIGEGEBEN – NICHT IMPLEMENTIERT" in text
    assert "wenden den Stash nicht an" in text
    assert "nicht angewendet" in text
    assert "Antwort: **Nein.**" in text
    assert "ADR-0065 bleibt nicht begonnen und gesperrt" in text


def test_no_productive_implementation_file_exists_in_worktree():
    assert not (ROOT / "governance/governance_decision_incident_evidence.py").exists()
    assert not (ROOT / "governance/decisions").exists()
    assert not (ROOT / "governance/incidents").exists()
