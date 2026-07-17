class Planner:

    def create_plan(self, goal: str) -> list[dict]:

        return [
            {
                "step": 1,
                "agent": "document",
                "action": "create",
                "target": goal,
            },
            {
                "step": 2,
                "agent": "git",
                "action": "sync",
                "message": f"Create {goal}",
            },
        ]