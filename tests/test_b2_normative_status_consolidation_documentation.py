from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "knowledge/adr"

ADRS = {
    "0060": ADR_DIR / "ADR-0060-guardian-b2-authority-authorization-v1.md",
    "0061": ADR_DIR / "ADR-0061-guardian-b2-provider-identity-v1.md",
    "0062": ADR_DIR / "ADR-0062-guardian-b2-provider-authorization-v1.md",
    "0063": ADR_DIR / "ADR-0063-b2-purpose-uodl-binding-constitution-v1.md",
    "0065": ADR_DIR / "ADR-0065-guardian-b2-capability-invocation-constitution-v1.md",
    "0066": ADR_DIR / "ADR-0066-guardian-b2-runtime-air-gap-constitution-v1.md",
}


def read(key: str) -> str:
    return ADRS[key].read_text(encoding="utf-8")


def normalized(key: str) -> str:
    return " ".join(read(key).split())


def test_every_target_adr_separates_normative_time_and_evidence_layers():
    for key in ADRS:
        text = read(key)
        evidence_heading = (
            "Implementierungs- und Validierungsevidenz"
            if key != "0066"
            else "Vollendungs- und Validierungsevidenz"
        )
        for marker in (
            "## Normativer Zeitstand und Evidenz",
            "Ursprünglicher Entscheidungsinhalt",
            "Historischer damaliger Governance-Zustand",
            "Gegenwärtiger normativer Status",
            evidence_heading,
            "Commit- und Push-Evidenz",
        ):
            assert marker in text


def test_adr_0060_current_implementation_is_not_open():
    text = normalized("0060")
    assert "IMPLEMENTIERT UND VALIDIERT" in text
    assert "Codex-Implementierungsauftrag erteilen. Offen." not in text
    assert "Zum damaligen Dokumentationszeitstand offen" in text
    assert "ebc050d1ebb9e15f828f918b1d9cd2ff8c970b0f" in text


def test_adr_0061_no_longer_denies_existing_provider_identity_implementation():
    text = normalized("0061")
    assert "IMPLEMENTIERT UND VALIDIERT" in text
    assert "Diese ADR implementiert keine Klasse" not in text
    assert "Der ursprüngliche Architekturakt implementierte keine Klasse" in text
    assert "governance/b2_provider_identity.py" in text
    assert "1c4fc5566c2b5c05bcf0065da01268d2b7870654" in text


def test_adr_0062_has_no_unresolved_current_implementation_contradiction():
    text = normalized("0062")
    assert "IMPLEMENTIERT UND VALIDIERT" in text
    assert "Sie implementiert keine Klasse" not in text
    assert "Der ursprüngliche ADR-0062-Architekturakt" in text
    assert "5ca8bf8452e240917f547e3975f5c15c4a78b73d" in text


def test_adr_0063_and_0065_mark_gate_requirements_historical_and_fulfilled():
    for key, approval in (
        ("0063", "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0063-V1"),
        ("0065", "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1"),
    ):
        text = read(key)
        assert "Historische Ratifikationsanforderungen und heutige Evidenz" in text
        assert "Historische Implementierungsfreigabeanforderungen und heutige Evidenz" in text
        assert approval in text
        assert "Diese Anforderung" in text or "Diese Anforderungen" in text


def test_adr_0066_records_pushed_declarative_completion_without_runtime():
    text = normalized("0066")
    assert "noch nicht committed und noch nicht gepusht" not in text
    assert "f77a9529e127ed9fddd088320ce465bf4bbc6e0c" in text
    assert "im aktuellen `origin/builder-reset-v2` nachweisbar gepusht" in text
    for marker in (
        "Runtime Air Gap ist keine Software",
        "keine produktive technische Komponente",
        "Runtime Readiness bleiben ausgeschlossen",
        "B2 Invocation Resolution Snapshot → CONTROLLED_STOP → ENDE",
    ):
        assert marker in text


def test_historical_gates_and_process_incident_remain_visible():
    assert "damaliger Gate-Zustand" in normalized("0060")
    assert "dokumentierte Prozessvorfall" in normalized("0061")
    assert "Implementierungsbeginn vor dem kanonischen Freigabe-Push" in normalized("0062")
    assert "ohne rückwirkende Legitimierung" in normalized("0061")


def test_no_technical_adr_0066_or_runtime_readiness_component_exists():
    forbidden = (
        ROOT / "governance/b2_runtime_air_gap.py",
        ROOT / "governance/runtime_air_gap_validator.py",
        ROOT / "governance/runtime_readiness.py",
        ROOT / "governance/b2_runtime.py",
    )
    assert all(not path.exists() for path in forbidden)
