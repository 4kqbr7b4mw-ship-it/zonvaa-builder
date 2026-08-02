from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge" / "adr" / "ADR-0051-read-only-b1-provider-runtime-v1.md"
STATUS = ROOT / "knowledge" / "project" / "current-product-status.md"
README = ROOT / "guardian_understanding" / "README.md"


def normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def test_adr_0051_documents_the_complete_narrow_runtime_boundary():
    content = normalized(ADR)
    for value in (
        "erste reale Machtgrenze",
        "B1_GENERAL_ORIENTATION",
        "READ_ONLY",
        "ACCEPTED",
        "Provider-Adapter",
        "Runtime Result",
        "Output Boundary",
        "Execution Evidence",
        "RuntimeExecutionReceipt",
        "Fail-closed-Verhalten",
        "kontrollierte Degradation",
    ):
        assert value in content


def test_adr_0051_documents_depersonalization_and_strict_non_goals():
    content = normalized(ADR)
    for value in (
        "NON_PERSONAL",
        "DEPERSONALIZED",
        "keine B2- oder B3-Runtime",
        "keine Provider-Auswahl",
        "kein Fallback",
        "keine Retry-Logik",
        "keine Persistenz",
        "kein Audit Log",
        "keine automatische Guardian-Antwort",
    ):
        assert value in content


def test_documentation_records_missing_external_provider_without_improvisation():
    content = normalized(ADR)
    assert "kein kanonisch autorisierter" in content
    assert "keine externe Anbindung improvisiert" in content
    assert "kontrollierten Testadapter" in content


def test_project_status_and_guardian_readme_record_runtime_and_power_limit():
    status = normalized(STATUS)
    readme = normalized(README)
    for content in (status, readme):
        assert "Read-only B1 Provider Runtime v1" in content
        assert "B1" in content
        assert "READ_ONLY" in content
        assert "keine B2- oder B3-Runtime" in content
