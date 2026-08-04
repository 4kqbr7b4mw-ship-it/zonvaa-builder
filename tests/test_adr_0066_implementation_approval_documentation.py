from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "governance/institutional-implementation-approval-adr-0066.md"
ADR = ROOT / "knowledge/adr/ADR-0066-guardian-b2-runtime-air-gap-constitution-v1.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_approval_identity_time_and_role_are_explicit_and_separate():
    content = text(APPROVAL)
    normalized = " ".join(content.split())
    assert APPROVAL.is_file()
    for marker in (
        "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0066-V1",
        "04.08.2026, 13:17:32 Uhr",
        "04.08.2026, 13:17:38 Uhr",
        "Europe/Berlin (CEST, UTC+02:00)",
        "Institutionsgründer",
        "gegenwärtigen menschlichen Implementierungsfreigabe",
        "nicht rückwirkend",
    ):
        assert marker in normalized


def test_approval_scope_is_documentation_and_absence_tests_only():
    content = text(APPROVAL)
    for marker in (
        "kanonische Status- und Governance-Dokumentation",
        "Architekturkarte und B2-Readiness",
        "Produktstatus und Handover",
        "dokumentarische Architektur-, Governance- und Regressionstests",
        "kein produktives ADR-0066-Modul",
        "kein Runtime-Air-Gap-Validator",
        "keine Bridge, kein Adapter und kein Runtime-Readiness-Vertrag",
        "keine technische Fortsetzung nach dem ADR-0065 Resolution Snapshot",
    ):
        assert marker in content
    assert "simulieren keine\nRuntime" in content


def test_approval_excludes_every_technical_component():
    content = text(APPROVAL)
    for marker in (
        "Runtime-Air-Gap-Klasse, Validator, Evaluator oder Service",
        "Adapter, Bridge, Gateway, Interface oder Protocol",
        "Runtime-Readiness-Engine oder Runtime-Readiness-Contract",
        "Runtime Request, Runtime Command, Runtime Token, Execution Token",
        "Provider-, Tool-, API-, MCP- oder Agent-Aufrufe",
        "Queue-, Event-, Scheduler- oder Prozesssemantik",
        "Sessions, Tokens, Caches oder Schlüsselmaterial",
        "Key Custody, Entschlüsselung oder Inhaltszugriff",
        "Observation, Runtime Audit, Operational Memory, Metrics oder Notifications",
        "natürliche Personen, personenbezogene Verarbeitung oder Speicherung",
        "Runtime, ein neuer Runtime-ADR oder ADR-0067",
    ):
        assert marker in content


def test_adr_0065_end_sequence_and_runtime_block_remain_binding():
    content = text(APPROVAL)
    assert "ADR-0065 bleibt allein kanonisch für Invocation und Controlled Stop" in content
    assert "B2 Invocation Resolution Snapshot → CONTROLLED_STOP → ENDE" in content
    assert "Runtime bleibt nicht existent und vollständig gesperrt" in content
    assert "auch ihre vollständige Erfüllung löst nichts automatisch" in content


def test_separate_completion_order_is_required():
    content = text(APPROVAL)
    assert "separater deklaratorischer Vollendungsauftrag" in content
    assert "Commit und nachweisbarem Push" in content
    assert "selbst keine Vollendung oder Implementierung" in content


def test_current_status_is_approved_and_declaratively_completed():
    content = text(ADR)
    assert "RATIFIZIERT – AUSSCHLIESSLICH DOKUMENTARISCH IMPLEMENTIERUNGSFREIGEGEBEN" in content
    assert "DEKLARATORISCH VOLLENDET UND VALIDIERT" in content
    assert "OHNE PRODUKTIVE TECHNISCHE KOMPONENTE" in content
    assert "AUSSCHLIESSLICH DOKUMENTARISCH" in content
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0066-V1" in content


def test_no_productive_adr_0066_component_exists():
    forbidden = (
        ROOT / "governance/b2_runtime_air_gap.py",
        ROOT / "governance/adr_0066.py",
        ROOT / "governance/runtime_air_gap_validator.py",
        ROOT / "governance/b2_runtime.py",
    )
    assert all(not path.exists() for path in forbidden)
