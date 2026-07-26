import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

from goal.models import Goal
from goal.why_assessment import WhyAssessment
from identity.models import IdentityContext
from knowledge.memory import MemoryType


class RuntimeJournal:
    """Schreibt bestätigte Ereignisse einer Builder-Session."""

    def __init__(self) -> None:
        self.folder = Path("knowledge/protocols")
        self.folder.mkdir(parents=True, exist_ok=True)

        self.file = self.folder / "runtime.md"

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.file.open("a", encoding="utf-8") as f:
            f.write(f"- {timestamp} {message}\n")


class DecisionJournal:
    """Stores immutable goal decision records for success and apply failure."""

    RECORD_VERSION = "2.0"
    APPLY_STATUSES = {
        "not_requested",
        "not_executed",
        "completed",
        "failed",
    }
    DEFAULT_FOLDER = Path("knowledge/protocols")

    def __init__(self, folder: Optional[Path] = None) -> None:
        self.folder = folder if folder is not None else self.DEFAULT_FOLDER

    def record(
        self,
        goal: Goal,
        role: str,
        memory_types: Iterable[Union[MemoryType, str]],
        constitution_rules: Iterable[str],
        identity_context: IdentityContext,
        why_assessment: Optional[WhyAssessment],
        result: Dict[str, Any],
        input_file: Path,
        apply_status: str = "not_requested",
    ) -> Path:
        if apply_status not in self.APPLY_STATUSES:
            raise ValueError("Unknown apply status: {}".format(apply_status))
        created_at = datetime.now(timezone.utc)
        record = {
            "record_version": self.RECORD_VERSION,
            "created_at": created_at.isoformat(),
            "source": {
                "input_file": str(input_file.resolve()),
            },
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "project": goal.project,
                "priority": goal.priority.value,
                "status": goal.status.value,
                "owner": goal.owner,
                "created_at": goal.created_at.isoformat(),
            },
            "invocation": {
                "role": role,
                "memory_types": [
                    memory_type.value
                    if isinstance(memory_type, MemoryType)
                    else memory_type
                    for memory_type in memory_types
                ],
                "constitution_rules": list(constitution_rules),
            },
            "identity": {
                "source": str(identity_context.source),
                "version": identity_context.version,
            },
            "why_assessment": self._assessment_record(why_assessment),
            "decision": result["decision"],
            "plan": self._redacted_plan(result["plan"]),
            "apply": {
                "requested": apply_status != "not_requested",
                "status": apply_status,
            },
            "execution": self._execution_record(
                result["execution"],
                apply_status,
            ),
        }

        self.folder.mkdir(parents=True, exist_ok=True)
        filename = self.folder / "{}_goal-decision.json".format(
            created_at.strftime("%Y-%m-%d_%H-%M-%S-%f")
        )
        serialized = json.dumps(record, ensure_ascii=False, indent=2)
        with filename.open("x", encoding="utf-8") as record_file:
            record_file.write(serialized)
            record_file.write("\n")

        return filename

    def _execution_record(
        self,
        execution: Any,
        apply_status: str,
    ) -> Dict[str, Any]:
        if isinstance(execution, list):
            return {
                "status": apply_status,
                "steps": self._redacted_plan(execution),
                "error": None,
                "rollback": {
                    "rolled_back_steps": [],
                    "errors": [],
                },
                "remaining_resources": [],
            }

        error = execution.get("error") or {}
        return {
            "status": apply_status,
            "steps": [
                {
                    "target": target,
                    "execution_status": "completed",
                }
                for target in execution.get("completed_steps", [])
            ],
            "error": {
                "type": error.get("type"),
                "message": error.get("message"),
            },
            "rollback": {
                "rolled_back_steps": execution.get("rolled_back_steps", []),
                "errors": error.get("rollback_errors", []),
            },
            "remaining_resources": execution.get("remaining_resources", []),
        }

    def _redacted_plan(self, plan: Iterable[Dict[str, Any]]) -> list:
        return [
            {key: value for key, value in step.items() if key != "content"}
            for step in plan
        ]

    def _assessment_record(
        self,
        assessment: Optional[WhyAssessment],
    ) -> Optional[Dict[str, Any]]:
        if assessment is None:
            return None
        return {
            "status": assessment.status.value,
            "reason": assessment.reason.value,
            "evidence": list(assessment.evidence),
        }
