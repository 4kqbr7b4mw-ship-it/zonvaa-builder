from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "governance/guardian-accountability-explanation-candidate.md"
REFERENCE = ROOT / "governance/no-fabrication-reference-consolidation.md"
APPROVAL = (
    ROOT
    / "governance/decisions/GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-APPROVAL-V1.md"
)
PROCESS = ROOT / "governance/institutional-approval-process.md"
REPORT = ROOT / "governance/b2-constitution-v1.0-completion-report.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_candidate_name_and_completed_reference_document_id_are_distinct():
    candidate = read(CANDIDATE)
    reference = read(REFERENCE)
    assert "`GOV-NO-FABRICATION-1` bleibt unverändert der historische Arbeitstitel" in candidate
    assert "Er ist keine Dokument-ID" in candidate
    assert "`GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-V1`" in candidate
    assert "Dieses abgeschlossene Referenzartefakt wird ausschließlich durch die\nDokument-ID" in reference
    assert "Seine Existenz aktiviert den historischen Kandidaten\nnicht" in reference


def test_historical_scope_targets_resolve_to_realized_repository_artifacts():
    reference = read(REFERENCE)
    mappings = {
        "governance/no-fabrication-reference-map": ROOT
        / "governance/no-fabrication-reference-consolidation.md",
        "tests/no-fabrication-reference-consolidation-documentation": ROOT
        / "tests/test_no_fabrication_reference_consolidation_documentation.py",
        "governance-candidate:GOV-NO-FABRICATION-1": ROOT
        / "governance/guardian-accountability-explanation-candidate.md",
    }
    for historical_reference, realized_path in mappings.items():
        assert historical_reference in read(APPROVAL)
        assert historical_reference in reference
        assert realized_path.relative_to(ROOT).as_posix() in reference
        assert realized_path.is_file()
    assert "ersetzt oder\nändert keine historische Scope-Referenz" in reference


def test_adr_0066_process_separates_historical_gate_from_current_status():
    process = read(PROCESS)
    assert "Historischer damaliger Gate-Zustand" in process
    assert "noch nicht erfolgte Gates" in process
    assert "Gegenwärtiger nachweisbarer Abschlussstatus" in process
    assert "f77a9529e127ed9fddd088320ce465bf4bbc6e0c" in process
    assert "im aktuellen `origin/builder-reset-v2` enthalten" in process
    assert "legitimiert keinen früheren Gate-Zustand\nrückwirkend" in process


def test_completion_report_references_existing_adr_0059_file():
    report = read(REPORT)
    correct = "knowledge/adr/ADR-0059-guardian-b2-data-corridor-consent-boundary-v1.md"
    wrong = "knowledge/adr/ADR-0059-guardian-b2-data-corridor-and-consent-boundary.md"
    assert correct in report
    assert wrong not in report
    assert (ROOT / correct).is_file()


def test_completion_report_candidate_inventory_is_explicitly_bounded_and_complete():
    report = read(REPORT)
    assert "Das Inventar dieses Berichts ist auf die in" in report
    for marker in (
        "Guardian Accountability & Explanation",
        "Guardian Life Domain Model",
        "Guardian Key Custody / Key Master",
        "nicht aktiviert, nicht als Folgepaket eingeplant und nicht\nimplementiert",
    ):
        assert marker in report
    assert (ROOT / "governance/guardian-accountability-explanation-candidate.md").is_file()
    assert (ROOT / "governance/guardian-life-domain-model-candidate.md").is_file()


def test_maintenance_remains_documentary_without_new_power_or_runtime():
    combined = "\n".join(read(path) for path in (CANDIDATE, REFERENCE, PROCESS, REPORT))
    normalized = " ".join(combined.split())
    for marker in (
        "noch eine neue Regel, Taxonomie, Priorität oder materielle Wirkung",
        "erzeugt weder Vorrang noch materielle Zuständigkeit",
        "erzeugt weder Runtime, Runtime Readiness noch technische Ausführung",
        "keine neue Vertragssemantik, Invariante, Machtwirkung",
    ):
        assert marker in normalized
    forbidden = (
        ROOT / "governance/runtime_readiness.py",
        ROOT / "governance/runtime_bridge.py",
        ROOT / "governance/no_fabrication_validator.py",
    )
    assert all(not path.exists() for path in forbidden)
