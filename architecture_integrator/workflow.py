import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from architecture_integrator.integrator import ArchitectureIntegrator
from architecture_integrator.io import (
    load_analysis,
    load_decision,
    write_json,
    write_text_atomic,
)
from architecture_integrator.models import (
    ArchitectureAnalysis,
    ArchitectureProposal,
    ChiefArchitectDecision,
)
from architecture_integrator.prompt import CodexPromptBuilder


class WorkflowStatus(str, Enum):
    WAITING_FOR_DECISION = "WAITING_FOR_DECISION"
    READY_FOR_CODEX = "READY_FOR_CODEX"
    CODEX_PROMPT_GENERATED = "CODEX_PROMPT_GENERATED"


@dataclass(frozen=True)
class ArchitectureWorkflow:
    workflow_id: str
    created_at: datetime
    proposal_ids: Tuple[str, ...]
    proposal_files: Tuple[str, ...]
    analysis_files: Tuple[str, ...]
    decision_template_files: Tuple[str, ...]

    def __post_init__(self) -> None:
        _workflow_id(self.workflow_id)
        if (
            not isinstance(self.created_at, datetime)
            or self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError(
                "ArchitectureWorkflow created_at must be timezone-aware"
            )
        for field_name in (
            "proposal_ids",
            "proposal_files",
            "analysis_files",
            "decision_template_files",
        ):
            values = getattr(self, field_name)
            if not isinstance(values, tuple) or not all(
                isinstance(value, str) and value.strip() == value and value
                for value in values
            ):
                raise TypeError(
                    "ArchitectureWorkflow {} must contain strings".format(
                        field_name
                    )
                )
        count = len(self.proposal_ids)
        if count == 0:
            raise ValueError(
                "ArchitectureWorkflow must contain at least one proposal"
            )
        if len(set(self.proposal_ids)) != count:
            raise ValueError("ArchitectureWorkflow proposal IDs must be unique")
        if any(
            len(values) != count
            for values in (
                self.proposal_files,
                self.analysis_files,
                self.decision_template_files,
            )
        ):
            raise ValueError("ArchitectureWorkflow file lists must align")
        expected_proposals = tuple(
            "proposals/{}.json".format(item) for item in self.proposal_ids
        )
        expected_analyses = tuple(
            "analyses/{}.json".format(item) for item in self.proposal_ids
        )
        expected_templates = tuple(
            "decision_proposals/{}.md".format(item)
            for item in self.proposal_ids
        )
        if (
            self.proposal_files != expected_proposals
            or self.analysis_files != expected_analyses
            or self.decision_template_files != expected_templates
        ):
            raise ValueError(
                "ArchitectureWorkflow file paths are not canonical"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat(),
            "proposal_ids": list(self.proposal_ids),
            "proposal_files": list(self.proposal_files),
            "analysis_files": list(self.analysis_files),
            "decision_template_files": list(
                self.decision_template_files
            ),
        }


class ArchitectureWorkflowStore:
    """Persists non-binding workflow artifacts outside normative sources."""

    def __init__(
        self,
        root: Path = Path("knowledge/architecture_workflows"),
    ) -> None:
        self.root = root

    def create(
        self,
        workflow: ArchitectureWorkflow,
        proposals: Tuple[ArchitectureProposal, ...],
        analyses: Tuple[ArchitectureAnalysis, ...],
        templates: Tuple[str, ...],
    ) -> Path:
        if not isinstance(workflow, ArchitectureWorkflow):
            raise TypeError("workflow must be ArchitectureWorkflow")
        if tuple(item.proposal_id for item in proposals) != workflow.proposal_ids:
            raise ValueError("Proposal order does not match workflow")
        if tuple(item.proposal.proposal_id for item in analyses) != (
            workflow.proposal_ids
        ):
            raise ValueError("Analysis order does not match workflow")
        if len(templates) != len(workflow.proposal_ids):
            raise ValueError("Decision template count does not match workflow")

        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / workflow.workflow_id
        if target.exists():
            if self._matches(
                workflow,
                proposals,
                analyses,
                templates,
            ):
                return target
            raise RuntimeError(
                "Workflow ID already exists with different artifacts"
            )
        temporary = Path(
            tempfile.mkdtemp(
                dir=str(self.root),
                prefix=".architecture-workflow-",
            )
        )
        try:
            (temporary / "proposals").mkdir()
            (temporary / "analyses").mkdir()
            (temporary / "decision_proposals").mkdir()
            (temporary / "decisions").mkdir()
            (temporary / "prompts").mkdir()
            self._write(
                temporary / "workflow.json",
                workflow.to_dict(),
            )
            for index, proposal in enumerate(proposals):
                self._write(
                    temporary / workflow.proposal_files[index],
                    proposal.to_dict(),
                )
                self._write(
                    temporary / workflow.analysis_files[index],
                    analyses[index].to_dict(),
                )
                self._write_text(
                    temporary / workflow.decision_template_files[index],
                    templates[index] + "\n",
                )
            os.rename(temporary, target)
        except BaseException:
            if temporary.exists():
                shutil.rmtree(temporary)
            raise
        return target

    def load(self, workflow_id: str) -> ArchitectureWorkflow:
        data = json.loads(
            self._safe_artifact(
                workflow_id,
                "workflow.json",
            ).read_text(encoding="utf-8")
        )
        expected = {
            "schema_version",
            "workflow_id",
            "created_at",
            "proposal_ids",
            "proposal_files",
            "analysis_files",
            "decision_template_files",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Workflow manifest has invalid fields")
        if data["schema_version"] != "1.0":
            raise ValueError("Unsupported workflow schema_version")
        try:
            created_at = datetime.fromisoformat(data["created_at"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Workflow created_at is invalid") from exc
        return ArchitectureWorkflow(
            workflow_id=data["workflow_id"],
            created_at=created_at,
            proposal_ids=self._strings(data["proposal_ids"]),
            proposal_files=self._strings(data["proposal_files"]),
            analysis_files=self._strings(data["analysis_files"]),
            decision_template_files=self._strings(
                data["decision_template_files"]
            ),
        )

    def record_decision(
        self,
        workflow_id: str,
        decision: ChiefArchitectDecision,
    ) -> Path:
        workflow = self.load(workflow_id)
        if not isinstance(decision, ChiefArchitectDecision):
            raise TypeError("decision must be ChiefArchitectDecision")
        if decision.proposal_id not in workflow.proposal_ids:
            raise ValueError("Decision proposal_id is not part of workflow")
        if self.prompt_path(workflow_id).exists():
            raise RuntimeError(
                "Workflow already generated a Codex prompt"
            )
        path = self._safe_subfolder(
            workflow_id,
            "decisions",
        ) / "{}.json".format(decision.proposal_id)
        if path.exists():
            if load_decision(path) == decision:
                return path
            raise FileExistsError(
                "A different decision already exists for {}".format(
                    decision.proposal_id
                )
            )
        write_json(path, decision.to_dict())
        return path

    def status(self, workflow_id: str) -> WorkflowStatus:
        workflow = self.load(workflow_id)
        if self.prompt_path(workflow_id).is_file():
            return WorkflowStatus.CODEX_PROMPT_GENERATED
        decisions = self._decision_paths(workflow)
        if all(path.is_file() for path in decisions):
            return WorkflowStatus.READY_FOR_CODEX
        return WorkflowStatus.WAITING_FOR_DECISION

    def analyses(
        self,
        workflow_id: str,
    ) -> Tuple[ArchitectureAnalysis, ...]:
        workflow = self.load(workflow_id)
        return tuple(
            load_analysis(self._safe_artifact(workflow_id, relative))
            for relative in workflow.analysis_files
        )

    def decisions(
        self,
        workflow_id: str,
    ) -> Tuple[ChiefArchitectDecision, ...]:
        workflow = self.load(workflow_id)
        missing = [
            path
            for path in self._decision_paths(workflow)
            if not path.is_file()
        ]
        if missing:
            raise RuntimeError(
                "Chief Architect decisions are missing for: {}".format(
                    ", ".join(path.stem for path in missing)
                )
            )
        return tuple(
            load_decision(path) for path in self._decision_paths(workflow)
        )

    def write_prompt(self, workflow_id: str, content: str) -> Path:
        if self.status(workflow_id) is not WorkflowStatus.READY_FOR_CODEX:
            raise RuntimeError(
                "Workflow is not ready for Codex prompt generation"
            )
        path = self.prompt_path(workflow_id)
        write_text_atomic(path, content + "\n")
        return path

    def folder(self, workflow_id: str) -> Path:
        _workflow_id(workflow_id)
        folder = self.root / workflow_id
        if not folder.is_dir() or folder.is_symlink():
            raise FileNotFoundError(str(folder))
        try:
            folder.resolve().relative_to(self.root.resolve())
        except ValueError as exc:
            raise ValueError("Workflow folder escapes its root") from exc
        return folder

    def prompt_path(self, workflow_id: str) -> Path:
        _workflow_id(workflow_id)
        return self._safe_subfolder(
            workflow_id,
            "prompts",
        ) / "codex-prompt.md"

    def _decision_paths(
        self,
        workflow: ArchitectureWorkflow,
    ) -> Tuple[Path, ...]:
        folder = self._safe_subfolder(
            workflow.workflow_id,
            "decisions",
        )
        return tuple(
            folder / "{}.json".format(proposal_id)
            for proposal_id in workflow.proposal_ids
        )

    def _safe_artifact(self, workflow_id: str, relative: str) -> Path:
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("Workflow artifact path is unsafe")
        folder = self.folder(workflow_id)
        candidate = folder / relative
        try:
            candidate.resolve().relative_to(folder.resolve())
        except ValueError as exc:
            raise ValueError("Workflow artifact escapes its folder") from exc
        for parent in candidate.parents:
            if parent == folder.parent:
                break
            if parent.is_symlink():
                raise ValueError("Workflow artifact path contains a symlink")
        return candidate

    def _safe_subfolder(self, workflow_id: str, name: str) -> Path:
        folder = self.folder(workflow_id)
        target = folder / name
        if not target.is_dir() or target.is_symlink():
            raise ValueError("Workflow subfolder is unavailable or unsafe")
        return target

    def _write(self, path: Path, data: Dict[str, Any]) -> None:
        path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_text(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def _matches(
        self,
        workflow: ArchitectureWorkflow,
        proposals: Tuple[ArchitectureProposal, ...],
        analyses: Tuple[ArchitectureAnalysis, ...],
        templates: Tuple[str, ...],
    ) -> bool:
        try:
            if self.load(workflow.workflow_id) != workflow:
                return False
            for index, proposal in enumerate(proposals):
                if json.loads(
                    self._safe_artifact(
                        workflow.workflow_id,
                        workflow.proposal_files[index],
                    ).read_text(encoding="utf-8")
                ) != proposal.to_dict():
                    return False
                if json.loads(
                    self._safe_artifact(
                        workflow.workflow_id,
                        workflow.analysis_files[index],
                    ).read_text(encoding="utf-8")
                ) != analyses[index].to_dict():
                    return False
                if self._safe_artifact(
                    workflow.workflow_id,
                    workflow.decision_template_files[index],
                ).read_text(encoding="utf-8") != templates[index] + "\n":
                    return False
            return True
        except (OSError, TypeError, ValueError):
            return False

    def _strings(self, value: object) -> Tuple[str, ...]:
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise TypeError("Workflow manifest lists must contain strings")
        return tuple(value)


class ArchitectureWorkflowOrchestrator:
    """Orchestrates Integrator stages without architecture authority."""

    def __init__(
        self,
        integrator: ArchitectureIntegrator,
        store: ArchitectureWorkflowStore,
        prompt_builder: CodexPromptBuilder = CodexPromptBuilder(),
    ) -> None:
        if not isinstance(integrator, ArchitectureIntegrator):
            raise TypeError("integrator must be ArchitectureIntegrator")
        if not isinstance(store, ArchitectureWorkflowStore):
            raise TypeError("store must be ArchitectureWorkflowStore")
        if not isinstance(prompt_builder, CodexPromptBuilder):
            raise TypeError("prompt_builder must be CodexPromptBuilder")
        self.integrator = integrator
        self.store = store
        self.prompt_builder = prompt_builder

    def analyze(
        self,
        proposals: Tuple[ArchitectureProposal, ...],
    ) -> ArchitectureWorkflow:
        if not isinstance(proposals, tuple) or not all(
            isinstance(item, ArchitectureProposal) for item in proposals
        ):
            raise TypeError("proposals must contain ArchitectureProposal")
        if not proposals:
            raise ValueError("At least one proposal is required")
        ordered = tuple(sorted(proposals, key=lambda item: item.proposal_id))
        proposal_ids = tuple(item.proposal_id for item in ordered)
        if len(set(proposal_ids)) != len(proposal_ids):
            raise ValueError("Proposal IDs must be unique")
        analyses = tuple(
            self.integrator.analyze(item) for item in ordered
        )
        templates = tuple(
            self.integrator.render_decision_template(item)
            for item in analyses
        )
        workflow_id = self._workflow_id(ordered, analyses)
        workflow = ArchitectureWorkflow(
            workflow_id=workflow_id,
            created_at=max(item.submitted_at for item in ordered),
            proposal_ids=proposal_ids,
            proposal_files=tuple(
                "proposals/{}.json".format(item) for item in proposal_ids
            ),
            analysis_files=tuple(
                "analyses/{}.json".format(item) for item in proposal_ids
            ),
            decision_template_files=tuple(
                "decision_proposals/{}.md".format(item)
                for item in proposal_ids
            ),
        )
        self.store.create(workflow, ordered, analyses, templates)
        return workflow

    def decide(
        self,
        workflow_id: str,
        decision: ChiefArchitectDecision,
    ) -> WorkflowStatus:
        self.store.record_decision(workflow_id, decision)
        return self.store.status(workflow_id)

    def generate_codex(self, workflow_id: str) -> Path:
        analyses = self.store.analyses(workflow_id)
        decisions = self.store.decisions(workflow_id)
        sections = [
            "# CODEX ARCHITECTURE WORKFLOW ORDER",
            "",
            "Workflow: `{}`".format(workflow_id),
            "",
            "Every section below is based on a separate confirmed Chief "
            "Architect decision. The workflow made no decision.",
        ]
        for analysis, decision in zip(analyses, decisions):
            order = self.prompt_builder.build(analysis, decision)
            order_without_commit = order.split(
                "\n## Commit\n",
                1,
            )[0]
            sections.extend(
                (
                    "",
                    "---",
                    "",
                    order_without_commit,
                )
            )
        sections.extend(
            (
                "",
                "## Workflow commit",
                "",
                "Implement all confirmed sections as one coherent work "
                "package.",
                "Run the required complete tests and Doctor checks once after "
                "the integrated change.",
                "Create one commit only after all checks pass.",
                "Suggested message: `Integrate confirmed architecture "
                "workflow`",
                "",
                "Do not push.",
            )
        )
        return self.store.write_prompt(
            workflow_id,
            "\n".join(sections),
        )

    def _workflow_id(
        self,
        proposals: Tuple[ArchitectureProposal, ...],
        analyses: Tuple[ArchitectureAnalysis, ...],
    ) -> str:
        canonical = json.dumps(
            {
                "proposals": [item.to_dict() for item in proposals],
                "analyses": [item.to_dict() for item in analyses],
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return "workflow-{}".format(
            hashlib.sha256(canonical).hexdigest()[:16]
        )


def _workflow_id(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("workflow_id must be a string")
    if re.fullmatch(r"workflow-[0-9a-f]{16}", value) is None:
        raise ValueError("workflow_id has an invalid format")
    return value
