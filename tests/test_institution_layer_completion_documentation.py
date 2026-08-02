from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = PROJECT_ROOT / "governance"
ADR = PROJECT_ROOT / "knowledge" / "adr"


def read(path):
    return path.read_text(encoding="utf-8")


def test_i4_analysis_records_search_status_variants_and_decision():
    analysis = read(GOVERNANCE / "i4-canonical-source-analysis.md")

    for value in (
        "sämtliche ADRs ADR-0002 bis ADR-0058",
        "Eine direkte historische oder kanonische Norm mit der Bezeichnung `I4` wurde",
        "## Vollständige Referenzkette",
        "### Variante A – neue C1-Verfassungsregel",
        "### Variante B – kanonische Referenz unterhalb C1",
        "Variante B wird gewählt",
        "Analyse ist keine Verfassungsänderung",
    ):
        assert value in analysis


def test_canonical_rule_is_new_c2_reference_not_historical_i4():
    rule = read(GOVERNANCE / "system-behavior-only-rule.md")

    for value in (
        "GOV-SYSTEM-BEHAVIOR-ONLY-1",
        "historische Regel `I4`",
        "keine C1-Verfassungsänderung",
        "Nutzerprofilbildung",
        "Nutzungsstatistik oder Häufigkeitsauswertung pro Nutzer",
        "themen- oder lebensbereichsbezogene Nutzeranalyse",
        "Aggregation von Gesprächsinhalten",
        "Zweckentfremdung technischer Betriebsnachweise",
        "GEERBT",
        "VERSCHÄRFT",
        "UNVERÄNDERT",
    ):
        assert value in rule


def test_affected_adrs_reference_one_canonical_rule_without_weakening():
    for number in (47, 53, 54, 55, 56, 57, 58):
        path = next(ADR.glob("ADR-{:04d}-*.md".format(number)))
        content = read(path)
        assert "GOV-SYSTEM-BEHAVIOR-ONLY-1" in content

    for number in (53, 54, 55, 56, 57, 58):
        path = next(ADR.glob("ADR-{:04d}-*.md".format(number)))
        assert "unverändert" in read(path)


def test_trust_council_document_is_complete_but_unfilled():
    trust = read(
        GOVERNANCE / "trust-council-acknowledgement-adr-0058.md"
    )

    for value in (
        "Dokument-ID: `TRUST-ACK-ADR-0058-V1`",
        "Dokumentversion: 1.0",
        "Kenntnisnahmedatum: _auszufüllen_",
        "## Beratungsgegenstand",
        "Vetodomäne 2",
        "### Datenhoheit und Depersonalisierungsgrenze",
        "### Eigenständige Authority- und Grant-Grenze",
        "B1-Grant darf niemals",
        "### Betriebsblock",
        "### Widerruf und AAV/UODL",
        "## Ergebnisfeld der Kenntnisnahme",
        "Ergebnis: `OFFEN`",
        "## Vorbehalte, Auflagen und Sondervoten",
        "## Provenienz",
        "keine Runtime-Freigabe",
        "keine Implementierungsfreigabe",
        "keine Produktfreigabe",
    ):
        assert value in trust
    assert "Beschluss- oder Kenntnisnahmeprovenienz: _nicht vorhanden" in trust


def test_institutional_process_separates_roles_documents_and_gates():
    process = read(GOVERNANCE / "institutional-approval-process.md")

    for step in (
        "1. Gutachterliche Analyse",
        "2. Chief-Architect-Entscheidung",
        "3. GOV-40-Verfassungsentscheidung",
        "4. Vertrauensrats-Kenntnisnahme",
        "5. Institutionelle Implementierungsfreigabe",
        "6. Codex-Implementierungsauftrag",
    ):
        assert step in process
    assert "keine Workflow-Engine" in process
    assert "automatisch abgeleitet werden" in process


def test_b2_readiness_keeps_human_gates_and_runtime_blocked():
    readiness = read(GOVERNANCE / "b2-readiness-statement.md")

    for row in (
        "| Betriebsblock | ABGESCHLOSSEN |",
        "| ADR-0058 | RATIFIZIERT |",
        "| I4-/Regelquellenklärung | GEKLÄRT OHNE HISTORISCHE I4-REKONSTRUKTION |",
        "| Vertrauensratsunterlage | VORBEREITET UND UNAUSGEFÜLLT |",
        "| Vertrauensrats-Kenntnisnahme | OFFEN |",
        "| Institutionelle Implementierungsfreigabe | OFFEN |",
        "| B2-Implementierung | GESPERRT |",
        "| B2-Runtime | GESPERRT |",
    ):
        assert row in readiness


def test_future_package_map_is_non_executing_and_individually_gated():
    package_map = read(GOVERNANCE / "future-b2-package-map.md")

    for package in (
        "B2 Authority and Authorization",
        "B2 Data Corridor and Consent Boundary",
        "B2 Depersonalization and Privacy Boundary",
        "B2 Invocation Boundary",
        "B2 Provider Runtime",
        "B2 Observation, Audit and User-Owned Storage Integration",
    ):
        assert package in package_map
    assert "Jedes Paket benötigt eine eigene Architekturentscheidung" in package_map
    assert "Nicht Bestandteil dieser Landkarte sind Verträge, Klassen, APIs" in package_map
