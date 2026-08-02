from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0060-guardian-b2-authority-authorization-v1.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_adr_0060_is_ratified_without_implementation_approval():
    text = read(ADR)
    assert "Status: RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN" in text
    assert "GOV-RATIFICATION-ADR-0060-V1" in text
    assert "trotz Ratifizierung keine institutionelle Implementierungsfreigabe" in text
    assert "Ratifizierung und Implementierungsfreigabe sind zwei eigenständige" in text
    assert "Eine gesonderte institutionelle Implementierungsfreigabe erstellen. Offen" in text
    assert "separaten, scopegebundenen Codex-Implementierungsauftrag" in text


def test_b2_authority_and_grants_are_structurally_separate_from_b1():
    text = read(ADR)
    for phrase in (
        "B2 ist keine Erweiterung von B1",
        "Eine B1 Authority ist niemals eine B2 Authority",
        "B1 Grant",
        "nicht erweitert, konvertiert, migriert oder hochgestuft",
        "eigene B2 Authority ID",
        "B2 Authority Class",
        "institutionellen Scope",
        "verfassungsmäßige Grundlage",
        "kein `valid`, `active`, `revoked`, `expired`",
    ):
        assert phrase in text


def test_grant_requires_d3_t4_aav_uodl_and_narrow_purpose():
    text = read(ADR)
    for phrase in (
        "genau eine D3-Einwilligung",
        "genau eine T4-Erteilungsquittung",
        "genau eine AAV-Autorisierung",
        "genau eine UODL-Referenz",
        "D3 ist notwendig, aber niemals hinreichend",
        "Gleichheit",
        "Verengung",
        "Erweiterung",
        "Nicht vergleichbar oder inkonsistent",
        "keine automatische Heilung",
    ):
        assert phrase in text


def test_evaluation_uses_explicit_time_and_has_no_hidden_state():
    text = read(ADR)
    for phrase in (
        "timezone-aware",
        "kein `now()`",
        "keine Wanduhr",
        "keinen impliziten Zeitpunkt",
        "deterministisch, zustandslos, rein funktional",
        "kein Repository, Cache, Token oder Session",
        "Identische Eingaben einschließlich Zeitpunkt",
    ):
        assert phrase in text


def test_positive_and_negative_evidence_are_non_personal_point_in_time_receipts():
    text = read(ADR)
    for phrase in (
        "kein Cache, Token, Grant oder fortwirkender",
        "geschlossene typisierte Entscheidungsgründe",
        "Vollständige personenbezogene Eingabeobjekte dürfen nicht eingebettet werden",
        "nicht personenbezogene Verweigerungsquittung",
        "keine personenbezogene Sperre",
        "Governance Evidence ist Nachweis einer verweigerten Evaluation",
        "keine Capability, Operation oder Aktivierungssemantik",
    ):
        assert phrase in text


def test_all_unauthorized_personal_states_and_future_power_are_excluded():
    text = read(ADR)
    for phrase in (
        "Ein unerlaubter personenbezogener Zustand darf",
        "Grant ohne B2 Authority, D3, T4, AAV oder UODL",
        "positive Evaluation ohne aktuelle D3-Wirksamkeit",
        "Evaluation ohne expliziten Zeitpunkt oder mit Wanduhr",
        "B1→B2-Upgrade",
        "automatische Sanktion oder Personenprofil",
        "B2 Provider, Provider Identity, Provider Authorization",
        "Capability Invocation, Runtime",
        "Operational Memory, Metrics, Notifications",
    ):
        assert phrase in text


def test_existing_adr_0059_approval_is_not_extended():
    approval = read(ROOT / "governance/institutional-implementation-approval-adr-0059.md")
    readiness = read(ROOT / "governance/b2-readiness-statement.md")
    assert "- B2 Authority," in approval
    assert "- B2 Authorization Grants," in approval
    assert "| ADR-0060 B2 Authority and Authorization | RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN |" in readiness
    assert "| Institutionelle Implementierungsfreigabe für ADR-0060 | NICHT ERSTELLT |" in readiness
    assert "| B2-Runtime | GESPERRT |" in readiness


def test_no_b2_implementation_files_are_created_by_the_architecture_package():
    assert not (ROOT / "governance/b2_authority.py").exists()
    assert not (ROOT / "governance/b2_authorization.py").exists()


def test_ratification_record_is_separate_and_grants_no_implementation_power():
    text = read(ROOT / "governance/ratification-adr-0060.md")
    for phrase in (
        "GOV-RATIFICATION-ADR-0060-V1",
        "RATIFIZIERUNG DOKUMENTIERT",
        "Institutionsgründer in konstituierender Funktion",
        "bestätigt ausschließlich den Architekturinhalt",
        "keine institutionelle Implementierungsfreigabe",
        "ADR-0059",
        "Alle bislang gesperrten B2-Bereiche bleiben gesperrt",
        "noch nicht gefasster menschlicher Beschluss",
    ):
        assert phrase in text
