from execution.engine import ExecutionEngine


def test_execution_engine_prepares_plan():
    engine = ExecutionEngine()

    plan = [
        {
            "step": 1,
            "agent": "document",
            "action": "create",
            "target": "ADR-0006",
        }
    ]

    result = engine.prepare(plan)

    assert result[0]["step"] == 1
    assert result[0]["execution_status"] == "pending"
