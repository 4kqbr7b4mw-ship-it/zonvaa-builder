from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
ADR = ROOT / "knowledge" / "adr" / "ADR-0046-zonvaa-builder-reset-v2.md"


def section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    return " ".join(text.split(heading, 1)[1].split("\n## ", 1)[0].split())


def test_codex_task_rule_is_canonical_in_agents_and_builder_reset_adr():
    assert "## Codex-Aufträge" in AGENTS.read_text(encoding="utf-8")
    assert "## E7b – Codex-Aufträge" in ADR.read_text(encoding="utf-8")


def test_codex_task_contains_only_directly_executable_content():
    for content in (
        section(AGENTS, "## Codex-Aufträge"),
        section(ADR, "## E7b – Codex-Aufträge"),
    ):
        assert "ausschließlich aus dem direkt ausführbaren Auftrag" in content
        assert "keine Einleitung, Begründung, Zusammenfassung" in content
        assert "Meta-Kommentare" in content
        assert "Prozesskommentare gehören nicht in Codex-Aufträge" in content


def test_architecture_decision_is_followed_immediately_by_the_codex_task():
    for content in (
        section(AGENTS, "## Codex-Aufträge"),
        section(ADR, "## E7b – Codex-Aufträge"),
    ):
        assert "Architekturdiskussion endet mit der Architekturentscheidung" in content
        assert "unmittelbar" in content
        assert "Codex-Auftrag" in content


def test_codex_task_is_minimal_complete_and_implementation_relevant():
    for content in (
        section(AGENTS, "## Codex-Aufträge"),
        section(ADR, "## E7b – Codex-Aufträge"),
    ):
        assert "nicht erneut erklärt" in content
        assert "für die korrekte Implementierung erforderlich" in content
        assert "so kurz wie möglich und so vollständig wie nötig" in content
        assert "konkreten Implementierungswert" in content


def test_chatgpt_keeps_all_five_work_phases_separate():
    for content in (
        section(AGENTS, "## Codex-Aufträge"),
        section(ADR, "## E7b – Codex-Aufträge"),
    ):
        for phase in (
            "Architekturdiskussion",
            "Codex-Auftrag",
            "Bewertung des Codex-Berichts",
            "Commit-Freigabe",
            "Push-Freigabe",
        ):
            assert phase in content
