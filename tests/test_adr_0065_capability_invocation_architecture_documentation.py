from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0065-guardian-b2-capability-invocation-constitution-v1.md"
VALIDATION = ROOT / "governance/adr-0065-architecture-validation.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_adr_0065_is_ratified_approved_implemented_and_validated():
    content = text(ADR)
    assert ADR.is_file()
    for marker in (
        "RATIFIZIERT",
        "IMPLEMENTIERUNGSFREIGEGEBEN",
        "IMPLEMENTIERT UND VALIDIERT",
        "GOV-RATIFICATION-ADR-0065-V1",
        "GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1",
    ):
        assert marker in content
    assert "governance/b2_capability_invocation.py" in content
    assert "kontrollierten Stopp" in content
    assert "kein\nAufruf, Befehl, technischer Zugriff" in content


def test_b1_and_b2_invocation_remain_separate():
    content = text(ADR)
    assert "ADR-0050 ist der tatsächliche kanonische B1-ADR" in content
    assert "Keine B1-Klasse" in content
    assert "keinen B1→B2-Upgradepfad" in content
    assert "keine zusätzliche Intent-Enum" in content


def test_request_references_only_existing_b2_constitutions():
    content = text(ADR)
    for marker in (
        "B2 Data Corridor Reference",
        "B2 Authority Reference",
        "B2 Grant Reference",
        "B2 Provider Identity Reference",
        "B2 Provider Authorization Reference",
        "B2 Purpose Binding Reference",
        "B2 UODL Mapping Reference",
        "ADR-0061 Capability Descriptor Reference",
        "B2PurposeScope",
    ):
        assert marker in content
    assert "keine zweite Purpose-Liste" in content
    assert "zusätzliche Operation" in content
    chain = (
        "B2 Data Corridor",
        "B2 Authority",
        "B2 Grant",
        "B2 Provider Identity",
        "B2 Provider Authorization",
        "B2 Purpose Binding",
        "B2 UODL Mapping",
        "B2 Capability Invocation",
        "kontrollierter Stopp",
    )
    documented_chain = content.split("Die vollständige Verfassungskette lautet:", 1)[1]
    positions = tuple(documented_chain.index(marker) for marker in chain)
    assert positions == tuple(sorted(positions))


def test_decision_receipt_and_snapshot_are_non_executing():
    content = text(ADR)
    assert "CONSISTENT_FOR_NON_EXECUTING_RESOLUTION" in content
    assert "REJECTED_WITH_CONTROLLED_STOP" in content
    assert "ACCEPTED` wird" in content
    assert "NO_EXECUTION_OCCURRED" in content
    assert "CONTROLLED_STOP" in content
    assert "keine Fortsetzungsadresse" in content


def test_runtime_air_gap_and_personal_data_boundary_are_complete():
    content = text(ADR)
    for marker in (
        "Tool, MCP-Server, Agent",
        "Queue, Event Bus, Scheduler",
        "Token, Key, Session",
        "execute()`",
        "invoke()`",
        "run()`",
        "dispatch()`",
        "send()`",
        "start()`",
        "natürliche Personen",
        "personenbezogene Inhalte",
        "Tracking, Monitoring, Telemetrie",
        "Operational Memory",
        "Metrics",
        "Notifications",
    ):
        assert marker in content


def test_authorization_governance_and_invocation_decisions_are_separate():
    content = text(ADR)
    assert "Authorization entscheidet, ob eine Invocation geprüft werden darf" in content
    assert "Invocation entscheidet nicht, ob technisch ausgeführt wird" in content
    assert "Governance Decision, B2 Authorization und Invocation Decision" in content
    assert "erzeugt kein Governance\nIncident" in content


def test_validation_answers_zero_question_with_no():
    content = text(VALIDATION)
    assert "GOV-ADR-0065-ARCHITECTURE-VALIDATION-V1" in content
    assert "Runtime Air Gap" in content
    assert "kontrollierten\nStopp" in content
    assert "Antwort: **Nein.**" in content
    assert "kein Adapter oder Runtime-Baustein" in content
    assert "ADR RATIFIZIERT" in content
    assert "IMPLEMENTIERUNGSFREIGEGEBEN" in content
    assert "IMPLEMENTIERT UND VALIDIERT" in content


def test_only_the_non_executing_adr_0065_module_exists():
    assert (ROOT / "governance/b2_capability_invocation.py").is_file()
    forbidden = (
        ROOT / "governance/adr_0065.py",
        ROOT / "guardian_b2/capability_invocation.py",
        ROOT / "governance/b2_capability_invocation_runtime.py",
    )
    assert all(not path.exists() for path in forbidden)
