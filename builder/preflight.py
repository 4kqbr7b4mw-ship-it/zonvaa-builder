import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Dict, Mapping, Tuple

from builder.runtime import RuntimeManager
from governance import GovernanceContext
from institution import InstitutionContext
from interaction import InteractionContext


class PreflightError(RuntimeError):
    """Raised when mandatory project context is structurally incomplete."""


_VALIDATED_MISSION = object()


@dataclass(frozen=True, init=False)
class WorkflowContext:
    schema_version: str
    generated_at: datetime
    project_root: str
    git_branch: str
    git_commit: str

    @classmethod
    def _from_mission(
        cls,
        mission_context: "MissionContext",
    ) -> "WorkflowContext":
        instance = object.__new__(cls)
        object.__setattr__(
            instance,
            "schema_version",
            mission_context.schema_version,
        )
        object.__setattr__(
            instance,
            "generated_at",
            mission_context.generated_at,
        )
        object.__setattr__(
            instance,
            "project_root",
            mission_context.project_root,
        )
        object.__setattr__(
            instance,
            "git_branch",
            mission_context.git["branch"],
        )
        object.__setattr__(
            instance,
            "git_commit",
            mission_context.git["commit"],
        )
        return instance


@dataclass(frozen=True)
class MissionContext:
    schema_version: str
    generated_at: datetime
    project_root: str
    governance: Mapping[str, Any]
    institution: Mapping[str, Any]
    interaction: Mapping[str, Any]
    constitution: Mapping[str, Any]
    knowledge: Mapping[str, Any]
    verified_facts: Mapping[str, Any]
    project_state: Mapping[str, Any]
    latest_context: Mapping[str, Any]
    working_rules: Tuple[str, ...]
    git: Mapping[str, Any]
    _validation_token: object = field(
        init=False,
        repr=False,
        compare=False,
        default=None,
    )

    def __post_init__(self) -> None:
        if self.schema_version != "1.3":
            raise ValueError("MissionContext schema_version must be 1.3")
        if not isinstance(self.generated_at, datetime):
            raise TypeError("MissionContext generated_at must be a datetime")
        if (
            self.generated_at.tzinfo is None
            or self.generated_at.utcoffset() is None
        ):
            raise ValueError(
                "MissionContext generated_at must be timezone-aware"
            )
        if not isinstance(self.project_root, str) or not self.project_root:
            raise ValueError("MissionContext project_root must not be empty")
        if not isinstance(self.working_rules, tuple) or not all(
            isinstance(rule, str) and rule
            for rule in self.working_rules
        ):
            raise TypeError(
                "MissionContext working_rules must be a tuple of strings"
            )
        for field_name in (
            "governance",
            "institution",
            "interaction",
            "constitution",
            "knowledge",
            "verified_facts",
            "project_state",
            "latest_context",
            "git",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Mapping):
                raise TypeError(
                    "MissionContext {} must be a mapping".format(field_name)
                )
            object.__setattr__(self, field_name, _deep_freeze(value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at.isoformat(),
            "project_root": self.project_root,
            "governance": _deep_thaw(self.governance),
            "institution": _deep_thaw(self.institution),
            "interaction": _deep_thaw(self.interaction),
            "constitution": _deep_thaw(self.constitution),
            "knowledge": _deep_thaw(self.knowledge),
            "verified_facts": _deep_thaw(self.verified_facts),
            "project_state": _deep_thaw(self.project_state),
            "latest_context": _deep_thaw(self.latest_context),
            "working_rules": list(self.working_rules),
            "git": _deep_thaw(self.git),
        }

    def for_workflow(self) -> WorkflowContext:
        if self._validation_token is not _VALIDATED_MISSION:
            raise PreflightError(
                "WorkflowContext requires a validated MissionContext"
            )
        return WorkflowContext._from_mission(self)


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                key: _deep_freeze(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _deep_thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _deep_thaw(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_deep_thaw(item) for item in value]
    return value


class PreflightService:
    MAX_CONTEXT_AGE = timedelta(minutes=5)
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

    def __init__(
        self,
        runtime: RuntimeManager,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.runtime = runtime
        self.clock = clock

    def build(self) -> MissionContext:
        institution = getattr(self.runtime, "institution_context", None)
        if not isinstance(institution, InstitutionContext):
            raise PreflightError("Institution is missing or invalid")
        interaction = getattr(self.runtime, "interaction_context", None)
        if not isinstance(interaction, InteractionContext):
            raise PreflightError("Interaction is missing or invalid")
        constitution = self.runtime.constitution
        if not isinstance(constitution, str) or not constitution.strip():
            raise PreflightError("Constitution is missing or empty")
        governance = getattr(self.runtime, "governance_context", None)
        if not isinstance(governance, GovernanceContext):
            raise PreflightError("Governance is missing or invalid")
        if (
            hashlib.sha256(constitution.encode("utf-8")).hexdigest()
            != governance.constitution_hash
        ):
            raise PreflightError(
                "Governance does not match the loaded Constitution"
            )

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
        context = MissionContext(
            schema_version="1.3",
            generated_at=self.clock(),
            project_root=str(Path.cwd()),
            governance={
                "status": "loaded",
                "constitution": {
                    "path": "constitution/constitution.md",
                    "version": constitution_version,
                    "content_hash": governance.constitution_hash,
                },
                "charter": {
                    "path": "governance/charter.md",
                    "version": governance.charter_version,
                    "content_hash": governance.charter_hash,
                },
                "operative_rules": {
                    "path": "governance/operative-rules.md",
                    "version": governance.operative_rules_version,
                    "content_hash": governance.operative_rules_hash,
                },
                "norm_levels": [
                    level.value for level in governance.norm_levels
                ],
                "protection_goals": [
                    goal.value for goal in governance.protection_goals
                ],
                "bodies": [
                    body.value for body in governance.bodies
                ],
                "trust_domains": [
                    domain.value for domain in governance.trust_domains
                ],
            },
            institution={
                "status": "loaded",
                "path": "institution/institution.md",
                "version": institution.version,
                "content_hash": institution.content_hash,
                "guarantees": [
                    guarantee.value
                    for guarantee in institution.guarantees
                ],
            },
            interaction={
                "status": "loaded",
                "path": "interaction/interaction.md",
                "version": interaction.version,
                "content_hash": interaction.content_hash,
                "principles": [
                    principle.value
                    for principle in interaction.principles
                ],
            },
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
        self._validate(context, require_token=False)
        object.__setattr__(
            context,
            "_validation_token",
            _VALIDATED_MISSION,
        )
        return context

    def validate(self, context: MissionContext) -> None:
        self._validate(context, require_token=True)

    def _validate(
        self,
        context: MissionContext,
        require_token: bool,
    ) -> None:
        if not isinstance(context, MissionContext):
            raise PreflightError(
                "Goal workflow requires a validated MissionContext"
            )
        if (
            require_token
            and context._validation_token is not _VALIDATED_MISSION
        ):
            raise PreflightError(
                "Goal workflow requires a validated MissionContext"
            )
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise RuntimeError("Preflight clock must be timezone-aware")
        age = now - context.generated_at
        if age < timedelta(seconds=-5) or age > self.MAX_CONTEXT_AGE:
            raise PreflightError("MissionContext is stale")
        expected_root = str(Path.cwd())
        if context.project_root != expected_root:
            raise PreflightError("MissionContext project root changed")
        if context.constitution.get("status") != "loaded":
            raise PreflightError("MissionContext Constitution is invalid")
        if context.governance.get("status") != "loaded":
            raise PreflightError("MissionContext Governance is invalid")
        governance = getattr(self.runtime, "governance_context", None)
        if not isinstance(governance, GovernanceContext):
            raise PreflightError("Runtime Governance changed")
        expected_governance = {
            "status": "loaded",
            "constitution": {
                "path": "constitution/constitution.md",
                "version": self._constitution_version(
                    self.runtime.constitution
                ),
                "content_hash": governance.constitution_hash,
            },
            "charter": {
                "path": "governance/charter.md",
                "version": governance.charter_version,
                "content_hash": governance.charter_hash,
            },
            "operative_rules": {
                "path": "governance/operative-rules.md",
                "version": governance.operative_rules_version,
                "content_hash": governance.operative_rules_hash,
            },
            "norm_levels": [
                level.value for level in governance.norm_levels
            ],
            "protection_goals": [
                goal.value for goal in governance.protection_goals
            ],
            "bodies": [
                body.value for body in governance.bodies
            ],
            "trust_domains": [
                domain.value for domain in governance.trust_domains
            ],
        }
        if context.governance != _deep_freeze(expected_governance):
            raise PreflightError("MissionContext Governance changed")
        if context.institution.get("status") != "loaded":
            raise PreflightError("MissionContext Institution is invalid")
        institution = getattr(self.runtime, "institution_context", None)
        if not isinstance(institution, InstitutionContext):
            raise PreflightError("Runtime Institution changed")
        if (
            context.institution.get("version") != institution.version
            or context.institution.get("content_hash")
            != institution.content_hash
            or tuple(context.institution.get("guarantees", ()))
            != tuple(
                guarantee.value
                for guarantee in institution.guarantees
            )
        ):
            raise PreflightError("MissionContext Institution changed")
        if context.interaction.get("status") != "loaded":
            raise PreflightError("MissionContext Interaction is invalid")
        interaction = getattr(self.runtime, "interaction_context", None)
        if not isinstance(interaction, InteractionContext):
            raise PreflightError("Runtime Interaction changed")
        if (
            context.interaction.get("version") != interaction.version
            or context.interaction.get("content_hash")
            != interaction.content_hash
            or tuple(context.interaction.get("principles", ()))
            != tuple(
                principle.value
                for principle in interaction.principles
            )
        ):
            raise PreflightError("MissionContext Interaction changed")
        if context.knowledge.get("status") != "loaded":
            raise PreflightError("MissionContext Knowledge is invalid")
        if context.git.get("branch") != self.runtime.project_state.get(
            "git_branch"
        ):
            raise PreflightError("MissionContext Git branch changed")
        if context.git.get("commit") != self.runtime.project_state.get(
            "git_commit"
        ):
            raise PreflightError("MissionContext Git commit changed")
        if context.project_state != _deep_freeze(
            self.runtime.project_state
        ):
            raise PreflightError("MissionContext Project State changed")
        if (
            context.verified_facts
            != _deep_freeze(self.runtime.verified_facts)
        ):
            raise PreflightError("MissionContext Verified Facts changed")

    def _constitution_version(self, content: str) -> str:
        match = re.search(r"^Version:\s*(.+?)\s*$", content, re.MULTILINE)
        return match.group(1) if match else "missing"

    def _working_rules(self) -> Tuple[str, ...]:
        agents_path = Path("AGENTS.md")
        if not agents_path.exists():
            agents_path = self.runtime.project_root / "AGENTS.md"
        if not agents_path.exists():
            raise PreflightError("AGENTS.md is missing")
        rules = []
        for line in agents_path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\d+\.\s+(.+)$", line)
            if match:
                rules.append(match.group(1))
        if not rules:
            raise PreflightError("AGENTS.md contains no numbered rules")
        return tuple(rules)
