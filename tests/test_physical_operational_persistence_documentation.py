from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0056-physical-operational-persistence-v1.md"
PLANS = ROOT / "PLANS.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0056_defines_operational_memory_first_and_medium_separation():
    content = normalized(ADR)
    for value in (
        "Physical Operational Persistence folgt Operational Memory, niemals umgekehrt",
        "Logisches Gedächtnis und physisches Speichermedium bleiben strikt getrennt",
        "keine Datenbank-, Datei-, Cloud-",
        "einzige medienneutrale Port-Schnittstelle",
        "keine konkrete Port-Implementierung",
    ):
        assert value in content


def test_adr_0056_documents_backup_recovery_and_non_execution_boundaries():
    content = normalized(ADR)
    for value in (
        "Backup und Recovery gehören ab dieser Stufe zur Betriebsarchitektur",
        "weder Backup noch Recovery",
        "Persistenz besitzt keine Runtime- oder Governance-Macht",
        "keine Metriken",
        "keine Nutzerdaten",
        "Gate aus ADR-0054 und ADR-0055 bleibt daher ausdrücklich geschlossen",
    ):
        assert value in content


def test_project_documents_physical_operational_persistence_as_bounded_v1():
    for content in (normalized(PLANS), normalized(STATUS)):
        assert "Physical Operational Persistence v1" in content
        assert "Operational Memory" in content
        assert "Backup" in content
        assert "Recovery" in content
