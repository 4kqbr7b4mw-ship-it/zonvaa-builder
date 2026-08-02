from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = (
    ROOT
    / "knowledge"
    / "adr"
    / "ADR-0050-guardian-capability-invocation-boundary-v1.md"
)
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0050_documents_complete_non_executing_boundary():
    content = normalized(ADR)
    for value in (
        "Invocation Request",
        "Invocation Decision",
        "Invocation Evidence",
        "Invocation Receipt",
        "Resolution Snapshot",
        "Fail-closed-Grundsatz",
        "B1_GENERAL_ORIENTATION",
        "ACCEPTED",
        "REJECTED",
        "BLOCKED",
    ):
        assert value in content


def test_adr_0050_forbids_runtime_persistence_audit_and_activation():
    content = normalized(ADR)
    for value in (
        "keine Runtime",
        "Provider-Ausführung",
        "Capability-Aktivierung",
        "keine Netzwerkzugriffe",
        "Persistenz",
        "Audit Logs",
        "keine Kryptographie",
        "keine Replay-Erkennung",
        "keine Workflow-",
        "keine UI",
    ):
        assert value in content


def test_product_status_records_invocation_boundary_without_execution_power():
    content = normalized(STATUS)
    assert "Guardian Capability Invocation Boundary v1" in content
    assert "ohne Persistenz" in content
    assert "Capability-Aktivierung" in content
    assert "keine Runtime" in content
