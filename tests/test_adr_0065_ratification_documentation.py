from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION = ROOT / "governance/ratification-adr-0065.md"
ADR = ROOT / "knowledge/adr/ADR-0065-guardian-b2-capability-invocation-constitution-v1.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ratification_identity_role_and_times_are_exact_and_separate():
    text = read(RATIFICATION)
    assert "GOV-RATIFICATION-ADR-0065-V1" in text
    assert "RATIFIZIERUNG DOKUMENTIERT – KEINE IMPLEMENTIERUNGSFREIGABE" in text
    assert "04.08.2026, 10:01:15 Uhr" in text
    assert "04.08.2026, 10:01:29 Uhr" in text
    assert "Europe/Berlin (CEST, UTC+02:00)" in text
    assert "Entscheidungsrolle: Institutionsgründer" in text
    assert "gegenwärtige menschliche Entscheidung" in text
    assert "keine rückwirkende" in text


def test_ratified_scope_is_complete_and_non_executing():
    text = read(RATIFICATION)
    for marker in (
        "Capability Invocation Binding",
        "Invocation Request",
        "Invocation Decision",
        "Invocation Evidence",
        "Invocation Receipt",
        "Invocation Resolution Snapshot",
        "Runtime Air Gap",
        "Data Corridor",
        "Provider Authorization",
        "Purpose Binding",
        "UODL Mapping",
        "Negative Invocation Rules",
        "Prüffrage Null",
    ):
        assert marker in text
    assert "keine technische Freigabe" in text
    assert "NO_EXECUTION_OCCURRED" in text
    assert "CONTROLLED_STOP" in text


def test_no_implementation_approval_or_runtime_is_granted():
    text = read(RATIFICATION)
    assert "## Ausdrücklich nicht freigegeben" in text
    assert "institutionelle Implementierungsfreigabe und Implementierung" in text
    assert "Runtime bleibt vollständig gesperrt" in text
    assert "Provider-, Tool-, API- oder MCP-Aufrufe" in text
    assert "Agents, ChatGPT-App-Anbindung oder OpenAI-Adapter" in text
    assert "personenbezogene Verarbeitung" in text
    assert "ADR-0066" in text
    assert "Commit und Push" in text


def test_authorization_invocation_and_runtime_remain_separate():
    text = read(RATIFICATION)
    assert "Authorization,\nInvocation und Runtime bleiben drei getrennte Verfassungsstufen" in text
    assert "positive\nInvocation Decision" in text
    assert "Receipt quittiert nur" in text
    assert "Resolution Snapshot beendet ausschließlich" in text


def test_ratification_remains_referenced_after_later_approval_without_implementation():
    text = read(ADR)
    assert "RATIFIZIERT – IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in text
    assert "GOV-RATIFICATION-ADR-0065-V1" in text
    assert "keine\nImplementierung" in text


def test_historical_stash_remains_independent_and_unchanged():
    text = read(RATIFICATION)
    assert "fachlich unabhängig und unverändert" in text
    assert "stash@{0}" in text
    assert "f1e6f58aedf31d8617c83b68f9ea899c9aae9e43" in text
    assert "wendet ihn\nnicht an" in text


def test_no_productive_adr_0065_module_was_created():
    forbidden = (
        ROOT / "governance/b2_capability_invocation.py",
        ROOT / "governance/adr_0065.py",
        ROOT / "guardian_b2/capability_invocation.py",
    )
    assert all(not path.exists() for path in forbidden)
