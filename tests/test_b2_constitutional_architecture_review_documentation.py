from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "governance/b2-constitutional-architecture-review.md"


def read(path):
    return path.read_text(encoding="utf-8")


def test_review_covers_all_fifteen_points_without_new_governance_power():
    text = read(REVIEW)
    assert "GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1" in text
    for number in range(1, 16):
        assert "### {}.".format(number) in text
    for phrase in (
        "weder ADR noch Ratifizierung oder Freigabe",
        "keine neue Semantik",
        "Capability Invocation",
        "Runtime",
        "Antwort: **Nein.**",
    ):
        assert phrase in text


def test_review_keeps_canonical_rules_separate_and_names_reuse():
    text = read(REVIEW)
    for phrase in (
        "ADR-0059 für Corridor- und Negativgrenzen",
        "ADR-0060 für Authority, Grant, Purpose Scope",
        "ADR-0061 für Provider Identity",
        "ADR-0062 für deren punktuelle Anwendung",
        "B2DataCorridorValidator",
        "B2AuthorizationEvaluator",
        "B2ProviderAuthorizationValidator",
        "keine zweite",
    ):
        assert phrase in text


def test_review_records_blockers_without_inventing_resolution():
    text = read(REVIEW)
    for phrase in (
        "Corridor-Purpose und typisierter Purpose Scope",
        "UODL-Operationsnamen",
        "Historische Governance-Evidenz",
        "nicht ratifiziert",
        "nicht rekonstruiert",
    ):
        assert phrase in text


def test_review_contains_test_matrix_and_keeps_execution_unstarted():
    text = " ".join(read(REVIEW).split())
    assert "| Kanonische Invariante | ADR | Implementierung | Positiver Test |" in text
    assert "ADR-0063 und ADR-0064 sind getrennt ratifiziert" in text
    assert "Ausschließlich ADR-0063 ist begrenzt implementierungsfreigegeben" in text
    assert "Capability Invocation und Runtime wurden nicht begonnen" in text
    assert (ROOT / "knowledge/adr/ADR-0063-b2-purpose-uodl-binding-constitution-v1.md").is_file()
    assert not list((ROOT / "governance").glob("*b2*capability*invocation*.py"))
    assert not list((ROOT / "governance").glob("*b2*runtime*.py"))


def test_readiness_and_status_reference_review_without_opening_runtime():
    readiness = read(ROOT / "governance/b2-readiness-statement.md")
    status = read(ROOT / "knowledge/project/current-product-status.md")
    for text in (readiness, status):
        assert "GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1" in text
        assert "Capability Invocation" in text
        assert "B2-Runtime" in text
