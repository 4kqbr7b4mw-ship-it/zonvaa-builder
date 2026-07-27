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
from typing import Any, Dict, Optional, Tuple

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
    topic: str = ""
    decision_template_file: str = ""
    schema_version: str = "1.0"

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
        if self.schema_version not in {"1.0", "2.0"}:
            raise ValueError(
                "ArchitectureWorkflow schema_version is unsupported"
            )
        if self.schema_version == "2.0":
            _text(self.topic, "ArchitectureWorkflow topic")
            if (
                self.decision_template_file
                != "decision_proposals/decision-proposal.md"
            ):
                raise ValueError(
                    "ArchitectureWorkflow decision template path is not "
                    "canonical"
                )
        elif self.topic or self.decision_template_file:
            raise ValueError(
                "ArchitectureWorkflow 1.0 cannot contain v2 fields"
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
            )
        ):
            raise ValueError("ArchitectureWorkflow file lists must align")
        if self.schema_version == "1.0":
            if len(self.decision_template_files) != count:
                raise ValueError(
                    "ArchitectureWorkflow 1.0 templates must align"
                )
        elif self.decision_template_files:
            raise ValueError(
                "ArchitectureWorkflow 2.0 uses one decision template"
            )
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
            or (
                self.schema_version == "1.0"
                and self.decision_template_files != expected_templates
            )
        ):
            raise ValueError(
                "ArchitectureWorkflow file paths are not canonical"
            )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat(),
            "proposal_ids": list(self.proposal_ids),
            "proposal_files": list(self.proposal_files),
            "analysis_files": list(self.analysis_files),
            "decision_template_files": list(
                self.decision_template_files
            ),
        }
        if self.schema_version == "2.0":
            result["topic"] = self.topic
            result["decision_template_file"] = self.decision_template_file
        return result


@dataclass(frozen=True)
class ArchitectureRunResult:
    workflow: ArchitectureWorkflow
    status: WorkflowStatus
    decision_template: Optional[str] = None
    codex_prompt: Optional[Path] = None

    def __post_init__(self) -> None:
        if not isinstance(self.workflow, ArchitectureWorkflow):
            raise TypeError("workflow must be ArchitectureWorkflow")
        if not isinstance(self.status, WorkflowStatus):
            raise TypeError("status must be WorkflowStatus")
        if self.decision_template is not None and not isinstance(
            self.decision_template,
            str,
        ):
            raise TypeError("decision_template must be a string or None")
        if self.codex_prompt is not None and not isinstance(
            self.codex_prompt,
            Path,
        ):
            raise TypeError("codex_prompt must be a Path or None")
        if self.status is WorkflowStatus.WAITING_FOR_DECISION:
            if not self.decision_template or self.codex_prompt is not None:
                raise ValueError(
                    "Waiting run must contain only a decision template"
                )
        elif self.status is WorkflowStatus.CODEX_PROMPT_GENERATED:
            if self.decision_template is not None or self.codex_prompt is None:
                raise ValueError(
                    "Completed run must contain only a Codex prompt path"
                )
        else:
            raise ValueError(
                "Architecture run cannot stop at READY_FOR_CODEX"
            )


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
        decision_template: str,
    ) -> Path:
        if not isinstance(workflow, ArchitectureWorkflow):
            raise TypeError("workflow must be ArchitectureWorkflow")
        if tuple(item.proposal_id for item in proposals) != workflow.proposal_ids:
            raise ValueError("Proposal order does not match workflow")
        if tuple(item.proposal.proposal_id for item in analyses) != (
            workflow.proposal_ids
        ):
            raise ValueError("Analysis order does not match workflow")
        if workflow.schema_version != "2.0":
            raise ValueError("Only workflow schema 2.0 can be created")
        if not isinstance(decision_template, str) or not decision_template:
            raise ValueError("Decision template must not be empty")

        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / workflow.workflow_id
        if target.exists():
            if self._matches(
                workflow,
                proposals,
                analyses,
                decision_template,
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
                temporary / workflow.decision_template_file,
                decision_template + "\n",
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
        base_fields = {
            "schema_version",
            "workflow_id",
            "created_at",
            "proposal_ids",
            "proposal_files",
            "analysis_files",
            "decision_template_files",
        }
        if not isinstance(data, dict):
            raise ValueError("Workflow manifest has invalid fields")
        if data.get("schema_version") == "1.0":
            expected = base_fields
        elif data.get("schema_version") == "2.0":
            expected = base_fields | {"topic", "decision_template_file"}
        else:
            raise ValueError("Unsupported workflow schema_version")
        if set(data) != expected:
            raise ValueError("Workflow manifest has invalid fields")
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
            topic=data.get("topic", ""),
            decision_template_file=data.get("decision_template_file", ""),
            schema_version=data["schema_version"],
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

    def decision_template(self, workflow_id: str) -> str:
        workflow = self.load(workflow_id)
        if workflow.schema_version == "2.0":
            path = self._safe_artifact(
                workflow_id,
                workflow.decision_template_file,
            )
            return path.read_text(encoding="utf-8").rstrip("\n")
        return "\n\n---\n\n".join(
            self._safe_artifact(workflow_id, relative)
            .read_text(encoding="utf-8")
            .rstrip("\n")
            for relative in workflow.decision_template_files
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

    def decisions_if_present(
        self,
        workflow_id: str,
    ) -> Tuple[ChiefArchitectDecision, ...]:
        workflow = self.load(workflow_id)
        return tuple(
            load_decision(path)
            for path in self._decision_paths(workflow)
            if path.is_file()
        )

    def write_prompt(self, workflow_id: str, content: str) -> Path:
        if self.status(workflow_id) is not WorkflowStatus.READY_FOR_CODEX:
            raise RuntimeError(
                "Workflow is not ready for Codex prompt generation"
            )
        path = self.prompt_path(workflow_id)
        serialized = content + "\n"
        decisions = self.decisions(workflow_id)
        write_text_atomic(path, serialized)
        try:
            write_json(
                self.prompt_proof_path(workflow_id),
                {
                    "schema_version": "1.0",
                    "workflow_id": workflow_id,
                    "prompt_path": "prompts/codex-prompt.md",
                    "prompt_hash": hashlib.sha256(
                        serialized.encode("utf-8")
                    ).hexdigest(),
                    "decision_ids": [
                        decision.decision_id for decision in decisions
                    ],
                },
            )
        except BaseException:
            path.unlink()
            raise
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

    def prompt_proof_path(self, workflow_id: str) -> Path:
        _workflow_id(workflow_id)
        return self._safe_subfolder(
            workflow_id,
            "prompts",
        ) / "codex-prompt-proof.json"

    def prompt_proof(self, workflow_id: str) -> Dict[str, Any]:
        path = self.prompt_proof_path(workflow_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        expected = {
            "schema_version",
            "workflow_id",
            "prompt_path",
            "prompt_hash",
            "decision_ids",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Codex prompt proof has invalid fields")
        if (
            data["schema_version"] != "1.0"
            or data["workflow_id"] != workflow_id
            or data["prompt_path"] != "prompts/codex-prompt.md"
        ):
            raise ValueError("Codex prompt proof is invalid")
        decisions = self.decisions(workflow_id)
        if data["decision_ids"] != [
            decision.decision_id for decision in decisions
        ]:
            raise ValueError("Codex prompt proof decisions changed")
        prompt_hash = hashlib.sha256(
            self.prompt_path(workflow_id).read_bytes()
        ).hexdigest()
        if data["prompt_hash"] != prompt_hash:
            raise ValueError("Codex prompt hash changed")
        return data

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
        decision_template: str,
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
                workflow.decision_template_file,
            ).read_text(encoding="utf-8") != decision_template + "\n":
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
        topic: Optional[str] = None,
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
        resolved_topic = (
            topic
            if topic is not None
            else " / ".join(item.title for item in ordered)
        )
        _text(resolved_topic, "Architecture workflow topic")
        analyses = tuple(
            self.integrator.analyze(item) for item in ordered
        )
        workflow_id = self._workflow_id(
            ordered,
            analyses,
            resolved_topic,
        )
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
            decision_template_files=(),
            topic=resolved_topic,
            decision_template_file=(
                "decision_proposals/decision-proposal.md"
            ),
            schema_version="2.0",
        )
        decision_template = self._decision_template(workflow, analyses)
        self.store.create(
            workflow,
            ordered,
            analyses,
            decision_template,
        )
        return workflow

    def run(
        self,
        proposals: Tuple[ArchitectureProposal, ...] = (),
        topic: Optional[str] = None,
        workflow_id: Optional[str] = None,
        decisions: Tuple[ChiefArchitectDecision, ...] = (),
    ) -> ArchitectureRunResult:
        if not isinstance(proposals, tuple) or not all(
            isinstance(item, ArchitectureProposal) for item in proposals
        ):
            raise TypeError("proposals must contain ArchitectureProposal")
        if not isinstance(decisions, tuple) or not all(
            isinstance(item, ChiefArchitectDecision) for item in decisions
        ):
            raise TypeError(
                "decisions must contain ChiefArchitectDecision"
            )
        if proposals and workflow_id is not None:
            raise ValueError(
                "New proposals and workflow_id are mutually exclusive"
            )
        if proposals:
            workflow = self.analyze(proposals, topic=topic)
        else:
            if workflow_id is None:
                raise ValueError(
                    "Proposals or an existing workflow_id are required"
                )
            if topic is not None:
                raise ValueError(
                    "topic cannot change an existing workflow"
                )
            workflow = self.store.load(workflow_id)

        status = self.store.status(workflow.workflow_id)
        if decisions:
            if status is WorkflowStatus.CODEX_PROMPT_GENERATED:
                raise RuntimeError(
                    "Workflow already generated a Codex prompt"
                )
            self._validate_decisions(workflow, decisions)
            for decision in decisions:
                self.decide(workflow.workflow_id, decision)
            status = self.store.status(workflow.workflow_id)

        if status is WorkflowStatus.READY_FOR_CODEX:
            prompt_path = self.generate_codex(workflow.workflow_id)
            return ArchitectureRunResult(
                workflow=workflow,
                status=WorkflowStatus.CODEX_PROMPT_GENERATED,
                codex_prompt=prompt_path,
            )
        if status is WorkflowStatus.CODEX_PROMPT_GENERATED:
            return ArchitectureRunResult(
                workflow=workflow,
                status=status,
                codex_prompt=self.store.prompt_path(workflow.workflow_id),
            )
        return ArchitectureRunResult(
            workflow=workflow,
            status=status,
            decision_template=self.store.decision_template(
                workflow.workflow_id
            ),
        )

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

    def _decision_template(
        self,
        workflow: ArchitectureWorkflow,
        analyses: Tuple[ArchitectureAnalysis, ...],
    ) -> str:
        recommendations = tuple(
            item.recommendation for item in analyses
        )
        recommendation = (
            recommendations[0].value
            if len(set(recommendations)) == 1
            else "ADOPT_WITH_CHANGES"
        )
        accepted = self._unique(tuple(
            statement
            for analysis in analyses
            for statement in (
                analysis.aligned_elements + analysis.additive_elements
            )
        ))
        changed = self._unique(tuple(
            conflict.suggested_resolution
            for analysis in analyses
            for conflict in analysis.conflicting_elements
        ))
        open_decisions = self._unique(tuple(
            "{}: {} [{}; {}]".format(
                conflict.conflict_id,
                conflict.conflict_reason,
                conflict.existing_source,
                conflict.norm_level.value,
            )
            for analysis in analyses
            for conflict in analysis.conflicting_elements
        ) + tuple(
            item
            for analysis in analyses
            for item in analysis.decision_required
        ))
        open_decisions += (
            "Record one explicit Chief Architect decision for each proposal "
            "in workflow {}.".format(workflow.workflow_id),
        )
        return "\n".join(
            (
                "# ENTSCHEIDUNGSVORLAGE",
                "",
                "## Empfehlung",
                recommendation,
                "",
                "## Übernehmen",
                self._lines(accepted),
                "",
                "## Ändern",
                self._lines(changed),
                "",
                "## Ablehnen",
                self._lines(()),
                "",
                "## Offene Entscheidungen",
                self._lines(open_decisions),
            )
        )

    def _validate_decisions(
        self,
        workflow: ArchitectureWorkflow,
        decisions: Tuple[ChiefArchitectDecision, ...],
    ) -> None:
        proposal_ids = tuple(item.proposal_id for item in decisions)
        if len(set(proposal_ids)) != len(proposal_ids):
            raise ValueError("Decision proposal IDs must be unique")
        unrelated = sorted(set(proposal_ids) - set(workflow.proposal_ids))
        if unrelated:
            raise ValueError(
                "Decision proposal_id is not part of workflow: {}".format(
                    ", ".join(unrelated)
                )
            )
        existing = {
            item.proposal_id for item in self.store.decisions_if_present(
                workflow.workflow_id
            )
        }
        duplicates = sorted(existing & set(proposal_ids))
        if duplicates:
            raise FileExistsError(
                "Decisions already exist for: {}".format(
                    ", ".join(duplicates)
                )
            )

    def _lines(self, values: Tuple[str, ...]) -> str:
        if not values:
            return "- Keine."
        return "\n".join("- {}".format(value) for value in values)

    def _unique(self, values: Tuple[str, ...]) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(values))

    def _workflow_id(
        self,
        proposals: Tuple[ArchitectureProposal, ...],
        analyses: Tuple[ArchitectureAnalysis, ...],
        topic: str,
    ) -> str:
        canonical = json.dumps(
            {
                "topic": topic,
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


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value or value.strip() != value:
        raise ValueError("{} must be non-empty and trimmed".format(field_name))
    return value
