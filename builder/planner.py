from typing import Iterable, Optional

from execution.models import DocumentArtifact


class Planner:

    def create_plan(
        self,
        goal: str,
        document_artifacts: Optional[Iterable[DocumentArtifact]] = None,
    ) -> list[dict]:
        artifacts = list(document_artifacts or [])
        if artifacts:
            document_steps = [
                {
                    "step": index,
                    "agent": "document",
                    "action": "create",
                    "target": artifact.path,
                    "content": artifact.content,
                }
                for index, artifact in enumerate(artifacts, start=1)
            ]
            return document_steps + [
                {
                    "step": len(document_steps) + 1,
                    "agent": "git",
                    "action": "sync",
                    "message": f"Create {goal}",
                }
            ]

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
