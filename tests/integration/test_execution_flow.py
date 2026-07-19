from brain.context_analyzer import ContextAnalyzer
from brain.context_collector import ContextCollector
from builder.orchestrator import Orchestrator


def test_clean_context_reaches_execution(monkeypatch):
    collector = ContextCollector()

    def fake_run_command(command: list[str]) -> str:
        if command[:2] == ["git", "status"]:
            return "Keine Ausgabe."

        if command[:2] == ["git", "log"]:
            return "15a6e6f Integrate decision and execution engines"

        raise AssertionError(f"Unerwarteter Befehl: {command}")

    monkeypatch.setattr(
        collector,
        "_run_command",
        fake_run_command,
    )

    project_context = collector.collect()
    analysis = ContextAnalyzer().analyze(project_context)

    result = Orchestrator().run(
        goal="Execution Flow integrieren",
        context=analysis,
    )

    assert analysis["summary"]["git_dirty"] is False
    assert result["decision"]["status"] == "approved"
    assert result["decision"]["next_action"] == "plan"
    assert len(result["plan"]) == 2
    assert len(result["execution"]) == 2
    assert all(
        step["execution_status"] == "pending"
        for step in result["execution"]
    )


def test_dirty_context_stops_before_execution(monkeypatch):
    collector = ContextCollector()

    def fake_run_command(command: list[str]) -> str:
        if command[:2] == ["git", "status"]:
            return " M builder/orchestrator.py"

        if command[:2] == ["git", "log"]:
            return "15a6e6f Integrate decision and execution engines"

        raise AssertionError(f"Unerwarteter Befehl: {command}")

    monkeypatch.setattr(
        collector,
        "_run_command",
        fake_run_command,
    )

    project_context = collector.collect()
    analysis = ContextAnalyzer().analyze(project_context)

    result = Orchestrator().run(
        goal="Execution Flow integrieren",
        context=analysis,
    )

    assert analysis["summary"]["git_dirty"] is True
    assert result["decision"]["status"] == "blocked"
    assert result["decision"]["next_action"] == "clean_repository"
    assert result["plan"] == []
    assert result["execution"] == []
