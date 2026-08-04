from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATIFICATION = ROOT / "governance/ratification-adr-0066.md"
ADR = ROOT / "knowledge/adr/ADR-0066-guardian-b2-runtime-air-gap-constitution-v1.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ratification_identity_time_and_role_are_explicit_and_separate():
    content = text(RATIFICATION)
    assert RATIFICATION.is_file()
    for marker in (
        "GOV-RATIFICATION-ADR-0066-V1",
        "04.08.2026, 12:48:38 Uhr",
        "04.08.2026, 12:48:46 Uhr",
        "Europe/Berlin (CEST, UTC+02:00)",
        "Institutionsgründer",
        "gegenwärtige menschliche Entscheidung",
        "keine rückwirkende Freigabe",
    ):
        assert marker in content


def test_ratified_scope_is_declarative_and_ends_at_controlled_stop():
    content = text(RATIFICATION)
    for marker in (
        "ausschließlich deklaratorische Charakter",
        "B2 Invocation Resolution Snapshot → CONTROLLED_STOP",
        "→ ENDE",
        "Invocation→Runtime-Übergangs",
        "Runtime nicht aus Invocation ableitbar",
        "keine positive Invocation Decision Runtime-Reife",
        "Verbot jeder Runtime Preparation",
        "Negative Runtime-Air-Gap-Rules",
        "Prüffrage Null mit der Antwort **Nein**",
    ):
        assert marker in content


def test_ratification_is_not_approval_or_implementation():
    content = text(RATIFICATION)
    assert "KEINE IMPLEMENTIERUNGSFREIGABE – KEINE IMPLEMENTIERUNG" in content
    for marker in (
        "produktives ADR-0066-Python-Modul",
        "Validator",
        "statische Analyse als",
        "Runtime-Readiness-Engine",
        "Adapter, Bridge, Gateway, Interface, Protocol oder API",
        "Runtime Request, Runtime Command, Runtime Token, Execution Token",
        "Provider-, Tool-, API-, MCP- oder Agent-Aufrufe",
        "Key Custody, Entschlüsselung oder Inhaltszugriff",
        "Observation, Runtime Audit, Operational Memory, Metrics oder Notifications",
        "natürliche Personen, personenbezogene Verarbeitung oder Speicherung",
        "ADR-0067",
    ):
        assert marker in content


def test_any_later_approval_is_permanently_documentation_only():
    content = text(RATIFICATION)
    assert "sieht dauerhaft keine produktive technische Komponente vor" in content
    assert "kanonische Dokumentationsanpassungen und dokumentarische Regressionstests" in content
    assert "kein Modul, keinen Validator, Evaluator, Service, Adapter" in content
    assert "keine Runtime-Readiness-Komponente" in content


def test_runtime_discussion_preconditions_never_activate_anything():
    content = text(RATIFICATION)
    assert "Keine Runtime-Diskussionsvoraussetzung besitzt Aktivierungs-, Freigabe- oder" in content
    assert "nichts automatisch aktiviert, freigibt oder ausführt" in content
    assert "neuen ausdrücklichen menschlichen institutionellen" in content


def test_runtime_and_registered_candidates_remain_closed():
    content = text(RATIFICATION)
    assert "Runtime bleibt nicht existent und vollständig gesperrt" in content
    assert "Guardian Key Custody /\nKey Master" in content
    assert "Guardian Accountability & Explanation" in content
    assert "registrierte ruhende Kandidaten" in content


def test_adr_status_preserves_ratification_and_separate_approval():
    content = text(ADR)
    assert "RATIFIZIERT – IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT" in content
    assert "GOV-RATIFICATION-ADR-0066-V1" in content
    assert "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0066-V1" in content
    assert "implementiert nichts" in content


def test_no_productive_adr_0066_component_exists():
    forbidden = (
        ROOT / "governance/b2_runtime_air_gap.py",
        ROOT / "governance/adr_0066.py",
        ROOT / "governance/runtime_air_gap_validator.py",
        ROOT / "governance/b2_runtime.py",
    )
    assert all(not path.exists() for path in forbidden)
