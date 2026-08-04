from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR = ROOT / "knowledge/adr/ADR-0066-guardian-b2-runtime-air-gap-constitution-v1.md"
VALIDATION = ROOT / "governance/adr-0066-architecture-validation.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_adr_0066_is_ratified_without_approval_or_implementation():
    content = text(ADR)
    assert ADR.is_file()
    for marker in (
        "RATIFIZIERT",
        "NICHT IMPLEMENTIERUNGSFREIGEGEBEN",
        "NICHT IMPLEMENTIERT",
        "GOV-RATIFICATION-ADR-0066-V1",
    ):
        assert marker in content
    assert "Nicht eröffnet ist eine Runtime-\nArchitekturdiskussion" in content
    assert "sieht dauerhaft keine produktive technische\nKomponente vor" in content


def test_adr_0066_has_an_independent_declarative_purpose():
    content = text(ADR)
    assert "## 5. Eigenständiger Zweck" in content
    assert "keine zweite Wahrheit über Invocation" in content
    assert "ADR-0065 bleibt allein\nkanonisch für Invocation" in content
    assert "kein nächster technischer\nZustand" in content


def test_chain_ends_after_controlled_stop():
    content = text(ADR)
    assert "Invocation endet vollständig" in content
    assert "Runtime kann nicht aus Invocation abgeleitet" in content
    assert "Der Resolution Snapshot endet" in content
    assert "keinen nachgelagerten Empfänger" in content
    assert "`CONTROLLED_STOP` und ENDE" in content


def test_no_technical_component_is_planned():
    content = text(ADR)
    for marker in (
        "kein Python-Modul",
        "keine Air-Gap-Klasse",
        "keinen Validator",
        "Adapter, Bridge, Gateway, Interface",
        "Queue, Event, Message, Command",
        "Tool, Agent, MCP- oder Provider-Verbindung",
        "Mock Runtime",
        "Execution Stub",
    ):
        assert marker in content
    forbidden = (
        ROOT / "governance/b2_runtime_air_gap.py",
        ROOT / "governance/adr_0066.py",
        ROOT / "governance/b2_runtime.py",
        ROOT / "governance/runtime_air_gap_validator.py",
    )
    assert all(not path.exists() for path in forbidden)


def test_no_implicit_runtime_continuation_or_readiness():
    content = text(ADR)
    for marker in (
        "ready_for_runtime",
        "execution_ready",
        "dispatchable",
        "pending_execution",
        "awaiting_runtime",
        "runtime_candidate",
        "Keine Bedingung löst automatisch",
        "keine\nRuntime-Readiness",
    ):
        assert marker in content
    assert "Ein ausdrücklicher gegenwärtiger menschlicher institutioneller Beschluss" in content


def test_discussion_preconditions_do_not_prepare_runtime():
    content = text(ADR)
    for marker in (
        "keine offenen Architekturblocker",
        "Runtime-Risikobewertung",
        "Datenschutz-/Personenbezogenheits-",
        "Key-Custody- und Inhaltszugriffsgrenzen",
        "Observation, Runtime Audit, Incident/Accountability",
        "eigenen neuen ADR",
        "eigene menschliche Ratifizierung",
        "institutionelle Implementierungsfreigabe",
    ):
        assert marker in content
    assert "Aktivierungsbedingungen für eine Diskussion" in content


def test_personal_data_key_custody_and_content_access_remain_closed():
    content = text(ADR)
    assert "vollständig datenblind" in content
    assert "keine personenbezogenen Daten" in content
    assert "keinen Key-Custody-, Entschlüsselungs- oder Inhaltszugriffspfad" in content
    assert "Guardian Key Custody / Key Master" in content
    assert "keine Aktivierung,\nPlanung oder Implementierung" in content


def test_governance_and_accountability_do_not_open_runtime():
    content = text(ADR)
    assert "Ein Diskussionsbeschluss ist keine Runtime-Freigabe" in content
    assert "Implementierungsfreigabe keine technische\nAusführung" in content
    assert "Guardian Accountability & Explanation Layer" in content
    assert "weder\naktiviert noch implementiert" in content


def test_four_variants_and_choice_are_documented():
    content = text(ADR)
    for marker in (
        "Variante A – kein ADR-0066",
        "Variante B – deklaratorischer ADR ohne technische Komponenten",
        "Variante C – technischer Runtime Boundary Validator",
        "Variante D – Runtime Readiness Contract",
        "Variante B besitzt den kleinsten eigenständigen Zweck",
    ):
        assert marker in content


def test_validation_answers_zero_question_with_no():
    content = text(VALIDATION)
    assert "GOV-ADR-0066-ARCHITECTURE-VALIDATION-V1" in content
    assert "ADR RATIFIZIERT" in content
    assert "GOV-RATIFICATION-ADR-0066-V1" in content
    assert "NICHT IMPLEMENTIERUNGSFREIGEGEBEN" in content
    assert "NICHT IMPLEMENTIERT" in content
    assert "keine technische Air-Gap-Schicht" in content
    assert "Antwort: **Nein.**" in content
    assert "kein produktives ADR-0066-Python-Modul" in content


def test_stash_identity_is_documented_without_becoming_a_source():
    content = text(VALIDATION)
    assert "historische Recovery-\nStash" in content
    assert "fachlich unabhängig und unverändert" in content


def test_canonical_status_documents_keep_adr_0066_declarative():
    paths = (
        ROOT / "PLANS.md",
        ROOT / "governance/architecture-map.md",
        ROOT / "governance/b2-readiness-statement.md",
        ROOT / "governance/future-b2-package-map.md",
        ROOT / "governance/institutional-approval-process.md",
        ROOT / "governance/b2-constitutional-architecture-review.md",
        ROOT / "knowledge/project/current-product-status.md",
    )
    for path in paths:
        content = text(path)
        assert "ADR-0066" in content
        assert "ratifiziert" in content.lower()
        assert "nicht implement" in content.lower()
    readiness = text(ROOT / "governance/b2-readiness-statement.md")
    assert "Runtime ist kein nächster Zustand" in readiness
    assert "ADR-0067 | NICHT BEGONNEN" in readiness


def test_future_map_removes_runtime_as_a_follow_on_package():
    package_map = text(ROOT / "governance/future-b2-package-map.md")
    assert "| B2 Provider Runtime |" not in package_map
    assert "| B2 Observation, Audit and User-Owned Storage Integration |" not in package_map
    assert "| B2 Runtime Air Gap Constitution |" in package_map
    assert "Invocation→Runtime-Übergangs" in package_map
