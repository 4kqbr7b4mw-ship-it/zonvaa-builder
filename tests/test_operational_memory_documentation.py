from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0055-operational-memory-v1.md"
PLANS = ROOT / "PLANS.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0055_defines_audit_first_immutable_operational_evidence_only():
    content = normalized(ADR)
    for value in (
        "Persistenz folgt Audit, niemals umgekehrt",
        "Alle Speicherverträge sind immutable",
        "Laufzeitobjekte und Speicherobjekte bleiben vollständig getrennt",
        "maschinengenerierter Betriebsartefakte",
        "geschlossene Katalog",
        "erzeugt, ergänzt, interpretiert oder verändert keinen Nachweis",
    ):
        assert value in content


def test_adr_0055_documents_user_data_aav_uodl_and_physical_storage_boundary():
    content = normalized(ADR)
    for value in (
        "Nutzerdaten, Gesprächsinhalte, Nutzerprofile",
        "Nutzungsmuster",
        "themenbezogene Nutzungsinformationen",
        "personenbezogene Artefakte",
        "Nicht-Nutzerdaten-Grenze aus ADR-0053",
        "AAV",
        "UODL",
        "keine kanonische, begrenzte physische Persistenzschnittstelle",
        "keine Datenbank, Dateiablage",
    ):
        assert value in content


def test_adr_0055_records_open_lifecycle_decisions_and_trigger():
    content = normalized(ADR)
    for value in (
        "Lösch- und Verfallsstrategie",
        "Archivierungsstrategie",
        "gesetzliche oder vertragliche Aufbewahrungsfristen",
        "technische Replikations- und Wiederherstellungsstrategie",
        "bevor der erste Artefakttyp",
        "vor dem ersten produktiven Betrieb",
        "je nachdem, welches Ereignis zuerst eintritt",
        "nicht stillschweigend als dauerhafte Append-only-Strategie",
    ):
        assert value in content


def test_b2_b3_gate_remains_closed_and_status_and_plan_are_current():
    for content in (normalized(ADR), normalized(STATUS)):
        assert "B2" in content and "B3" in content
        assert "Metriken" in content
        assert "Benachrichtigungen" in content
        assert "Gate" in content
    assert "Operational Memory v1" in normalized(PLANS)
