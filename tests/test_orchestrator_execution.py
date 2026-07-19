from builder.orchestrator import Orchestrator


def test_orchestrator_prepares_execution_after_approved_plan():
    orchestrator = Orchestrator()

    result = orchestrator.run(
        goal="Execution Engine integrieren",
        context={
            "summary": {"git_dirty": False},
            "risks": [],
        },
    )

    assert result["decision"]["status"] == "approved"
    assert result["plan"]
    assert result["execution"][0]["execution_status"] == "pending"
