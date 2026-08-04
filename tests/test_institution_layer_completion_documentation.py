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


def test_founder_acknowledgement_is_documented_with_temporary_role_limit():
    trust = read(
        GOVERNANCE / "trust-council-acknowledgement-adr-0058.md"
    )

    for value in (
        "Dokument-ID: `TRUST-ACK-ADR-0058-V1`",
        "Dokumentversion: 1.0",
        "Kenntnisnahmedatum: 02.08.2026",
        "## Beratungsgegenstand",
        "Vetodomäne 2",
        "### Datenhoheit und Depersonalisierungsgrenze",
        "### Eigenständige Authority- und Grant-Grenze",
        "B1-Grant darf niemals",
        "### Betriebsblock",
        "### Widerruf und AAV/UODL",
        "## Ergebnisfeld der Kenntnisnahme",
        "Ergebnis: `ZUR KENNTNIS GENOMMEN`",
        "Kenntnis genommen durch: Michael Giese",
        "Institutionsgründer in konstituierender Funktion",
        "vor erstmaliger Konstituierung des ordentlichen Vertrauensrats",
        "bestätigt, geändert oder ersetzt werden",
        "## Vorbehalte, Auflagen und Sondervoten",
        "## Provenienz",
        "keine B2-Runtime",
        "keine allgemeine B2-Implementierung",
        "keine B2-Produktfreigabe",
    ):
        assert value in trust
    assert "ordentliche Vertrauensratsbestätigung ausstehend" in trust
    assert "keine allgemeine B2-Implementierung" in trust


def test_adr_0059_implementation_approval_is_separate_and_strictly_bounded():
    approval = read(
        GOVERNANCE / "institutional-implementation-approval-adr-0059.md"
    )

    for value in (
        "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1",
        "Status: `ERTEILT`",
        "Michael Giese",
        "Institutionsgründer in konstituierender Funktion",
        "Guardian B2 Data Corridor and Consent Boundary v1",
        "ADR-0059",
        "immutable B2 Data Corridor Contracts",
        "Consent Boundary",
        "Data Classification",
        "Depersonalization Boundary",
        "deterministischer Validator",
        "read-only Snapshot",
        "B2 Authority",
        "B2 Authorization Grants",
        "B2 Runtime",
        "personenbezogene Verarbeitung",
        "kein Präzedenzfall",
        "Commit und Push bleiben davon getrennt",
    ):
        assert value in approval


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


def test_b2_readiness_allows_only_adr_0059_and_keeps_runtime_blocked():
    readiness = read(GOVERNANCE / "b2-readiness-statement.md")

    for row in (
        "| Betriebsblock | ABGESCHLOSSEN |",
        "| ADR-0058 | RATIFIZIERT |",
        "| Regelquellenklärung | ABGESCHLOSSEN |",
        "| Vertrauensrats-Kenntnisnahme | DOKUMENTIERT DURCH INSTITUTIONSGRÜNDER IN KONSTITUIERENDER FUNKTION |",
        "| Ordentliche Vertrauensratsbestätigung | AUSSTEHEND |",
        "| Institutionelle Implementierungsfreigabe für ADR-0059 | ERTEILT |",
        "| B2 Data Corridor and Consent Boundary v1 | IMPLEMENTIERT UND VALIDIERUNG ABGESCHLOSSEN |",
        "| ADR-0065 Guardian B2 Capability Invocation Constitution | RATIFIZIERT – IMPLEMENTIERUNGSFREIGEGEBEN – IMPLEMENTIERT UND VALIDIERT |",
        "| ADR-0066 Guardian B2 Runtime Air Gap Constitution | VORGESCHLAGEN – NICHT RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT |",
        "| Alle nachgelagerten B2-Pakete | GESPERRT |",
        "| B2-Runtime | GESPERRT |",
    ):
        assert row in readiness


def test_future_package_map_is_non_executing_and_individually_gated():
    package_map = read(GOVERNANCE / "future-b2-package-map.md")

    for package in (
        "B2 Authority and Authorization",
        "B2 Data Corridor and Consent Boundary",
        "B2 Depersonalization and Privacy Boundary",
        "B2 Capability Invocation Constitution",
        "B2 Runtime Air Gap Constitution",
    ):
        assert package in package_map
    assert "Jedes Paket benötigt eine eigene Architekturentscheidung" in package_map
    assert "Nicht Bestandteil dieser Landkarte sind Verträge, Klassen, APIs" in package_map
    assert "Die frühere nicht ratifizierte Zeile „B2 Provider Runtime“" in package_map
    assert "keine Runtime Readiness" in package_map
