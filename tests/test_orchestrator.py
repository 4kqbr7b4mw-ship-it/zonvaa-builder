from builder.orchestrator import Orchestrator


def test_orchestrator_returns_blocked_decision_without_plan():
    orchestrator = Orchestrator()

    result = orchestrator.run(
        goal="Decision Engine integrieren",
        context={
            "summary": {"git_dirty": True},
            "risks": ["Repository ist nicht sauber."],
        },
    )

    assert result["decision"]["status"] == "blocked"
    assert result["plan"] == []


def test_orchestrator_creates_plan_for_approved_decision():
    orchestrator = Orchestrator()

    result = orchestrator.run(
        goal="Decision Engine integrieren",
        context={
            "summary": {"git_dirty": False},
            "risks": [],
        },
    )

    assert result["decision"]["status"] == "approved"
    assert result["plan"]
