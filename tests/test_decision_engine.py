from brain.decision_engine import DecisionEngine


def test_decision_engine_returns_decision():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": False,
        },
        "risks": [],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision["goal"] == "Decision Engine entwickeln"
    assert decision["status"] == "approved"
    assert decision["next_action"] == "plan"


def test_decision_engine_blocks_dirty_repository():
    engine = DecisionEngine()

    context = {
        "summary": {
            "git_dirty": True,
        },
        "risks": [
            "Der aktuelle Arbeitsstand ist noch nicht vollständig versioniert."
        ],
    }

    decision = engine.decide(
        goal="Decision Engine entwickeln",
        context=context,
    )

    assert decision["status"] == "blocked"
    assert decision["next_action"] == "clean_repository"
    assert decision["reasons"]
