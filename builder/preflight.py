import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

from builder.runtime import RuntimeManager


class PreflightError(RuntimeError):
    """Raised when mandatory project context is structurally incomplete."""


@dataclass(frozen=True)
class MissionContext:
    schema_version: str
    generated_at: datetime
    project_root: str
    constitution: Dict[str, Any]
    knowledge: Dict[str, Any]
    verified_facts: Dict[str, Any]
    project_state: Dict[str, Any]
    latest_context: Dict[str, Any]
    working_rules: Tuple[str, ...]
    git: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at.isoformat(),
            "project_root": self.project_root,
            "constitution": self.constitution,
            "knowledge": self.knowledge,
            "verified_facts": self.verified_facts,
            "project_state": self.project_state,
            "latest_context": self.latest_context,
            "working_rules": list(self.working_rules),
            "git": self.git,
        }


class PreflightService:
    REQUIRED_KNOWLEDGE_AREAS = {
        "adr",
        "protocols",
        "handovers",
        "project",
        "sessions",
        "sources",
        "verified_facts",
    }
    REQUIRED_PROJECT_STATE = {
        "python_version",
        "pytest_version",
        "git_branch",
        "git_commit",
        "git_clean",
        "verified_facts",
    }

    def __init__(self, runtime: RuntimeManager) -> None:
        self.runtime = runtime

    def build(self) -> MissionContext:
        constitution = self.runtime.constitution
        if not isinstance(constitution, str) or not constitution.strip():
            raise PreflightError("Constitution is missing or empty")

        missing_areas = self.REQUIRED_KNOWLEDGE_AREAS - set(
            self.runtime.knowledge
        )
        if missing_areas:
            raise PreflightError(
                "Knowledge areas are missing: {}".format(
                    ", ".join(sorted(missing_areas))
                )
            )

        missing_state = self.REQUIRED_PROJECT_STATE - set(
            self.runtime.project_state
        )
        if missing_state:
            raise PreflightError(
                "Project state fields are missing: {}".format(
                    ", ".join(sorted(missing_state))
                )
            )
        branch = self.runtime.project_state.get("git_branch")
        commit = self.runtime.project_state.get("git_commit")
        if not branch or not commit:
            raise PreflightError("Git branch or commit is missing")

        context_path = self.runtime.latest_context
        constitution_version = self._constitution_version(constitution)
        rules = self._working_rules()
        knowledge_summary = {
            key: (
                len(value)
                if isinstance(value, list)
                else "loaded"
            )
            for key, value in self.runtime.knowledge.items()
        }
        return MissionContext(
            schema_version="1.0",
            generated_at=datetime.now(timezone.utc),
            project_root=str(Path.cwd()),
            constitution={
                "status": "loaded",
                "path": "constitution/constitution.md",
                "version": constitution_version,
            },
            knowledge={
                "status": "loaded",
                "areas": knowledge_summary,
            },
            verified_facts=self.runtime.verified_facts,
            project_state=self.runtime.project_state,
            latest_context={
                "status": "loaded" if context_path is not None else "missing",
                "path": (
                    str(context_path)
                    if context_path is not None
                    else None
                ),
                "kind": (
                    context_path.parent.name
                    if context_path is not None
                    else None
                ),
            },
            working_rules=rules,
            git={
                "branch": branch,
                "commit": commit,
                "clean": self.runtime.project_state["git_clean"],
            },
        )

    def _constitution_version(self, content: str) -> str:
        match = re.search(r"^Version:\s*(.+?)\s*$", content, re.MULTILINE)
        return match.group(1) if match else "missing"

    def _working_rules(self) -> Tuple[str, ...]:
        agents_path = Path("AGENTS.md")
        if not agents_path.exists():
            return ("AGENTS.md: missing",)
        rules = []
        for line in agents_path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\d+\.\s+(.+)$", line)
            if match:
                rules.append(match.group(1))
        return tuple(rules) if rules else ("AGENTS.md: no numbered rules",)
