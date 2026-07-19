from typing import Any


class ExecutionEngine:
    """Bereitet genehmigte Pläne für die Ausführung vor."""

    def prepare(
        self,
        plan: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                **step,
                "execution_status": "pending",
            }
            for step in plan
        ]
