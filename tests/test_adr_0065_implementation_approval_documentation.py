from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "governance/institutional-implementation-approval-adr-0065.md"
ADR = ROOT / "knowledge/adr/ADR-0065-guardian-b2-capability-invocation-constitution-v1.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_approval_identity_role_and_times_are_exact_and_separate():
    text = read(APPROVAL)
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1" in text
    assert "INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG" in text
    assert "04.08.2026, 10:15:02 Uhr" in text
    assert "04.08.2026, 10:15:03 Uhr" in text
    assert "Europe/Berlin (CEST" in text
    assert "Entscheidungsrolle: Institutionsgründer" in text
    assert "gegenwärtigen menschlichen Implementierungsfreigabe" in text
    assert "nicht rückwirkend" in text


def test_approved_scope_is_complete_and_non_executing():
    text = read(APPROVAL)
    for marker in (
        "Capability Invocation Binding",
        "Invocation Request",
        "Invocation Decision",
        "Invocation Evidence",
        "Invocation Receipt",
        "Invocation Resolution Snapshot",
        "Runtime Air Gap",
        "deterministische und zustandslose Validatoren",
        "Public API",
        "Positiv-, Negativ-, Integrations-, Public-API-",
    ):
        assert marker in text
    assert "NO_EXECUTION_OCCURRED" in text
    assert "CONTROLLED_STOP" in text


def test_runtime_and_expansion_remain_excluded():
    text = read(APPROVAL)
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "Runtime, technische Ausführung oder Capability-Ausführung" in text
    assert "Provider-, Tool-, API- oder MCP-Aufrufe" in text
    assert "automatische Provider-Auswahl" in text
    assert "neue Autorisierungs-, Purpose- oder UODL-Semantik" in text
    assert "personenbezogene Verarbeitung" in text
    assert "ADR-0066" in text
    assert "Commit und Push" in text


def test_approval_has_no_technical_effect_and_requires_later_order():
    text = read(APPROVAL)
    assert "erzeugt selbst keine Runtime" in text
    assert "keine technische Freigabewirkung" in text
    assert "Runtime bleibt vollständig gesperrt" in text
    assert "erst nach Dokumentation, eigenem\nCommit und nachweisbarem Push" in text
    assert "Diese Freigabe ist\nselbst keine Implementierung" in text


def test_adr_status_is_approved_but_not_implemented():
    text = read(ADR)
    assert "RATIFIZIERT – IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1" in text
    assert "keine Implementierung" in text


def test_stash_remains_independent_and_unchanged():
    text = read(APPROVAL)
    assert "fachlich unabhängig und unverändert" in text
    assert "stash@{0}" in text
    assert "f1e6f58aedf31d8617c83b68f9ea899c9aae9e43" in text
    assert "wendet ihn nicht\nan" in text


def test_no_productive_adr_0065_module_was_created():
    forbidden = (
        ROOT / "governance/b2_capability_invocation.py",
        ROOT / "governance/adr_0065.py",
        ROOT / "guardian_b2/capability_invocation.py",
    )
    assert all(not path.exists() for path in forbidden)
