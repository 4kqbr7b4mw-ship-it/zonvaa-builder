from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from architecture_integrator.feedback import (
    ArchitectureFeedbackStore,
    ExecutionAuthorization,
    stable_identifier,
)
from architecture_integrator.io import write_json
from architecture_integrator.workflow import ArchitectureWorkflowStore
from codex_execution.runner import CommandResult, SubprocessCommandRunner


class PreparationWorkingTreeState(str, Enum):
    CLEAN_WORKING_TREE = "CLEAN_WORKING_TREE"
    AUTHORIZED_PREPARATION_CHANGES = "AUTHORIZED_PREPARATION_CHANGES"
    UNAUTHORIZED_DIRTY_WORKING_TREE = "UNAUTHORIZED_DIRTY_WORKING_TREE"


class PreparationGitState(str, Enum):
    UNTRACKED = "UNTRACKED"
    MODIFIED = "MODIFIED"


class PreparationBaselineError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ArchitectureExecutionPreparationFile:
    path: str
    git_state: PreparationGitState
    sha256: str
    size: int

    def __post_init__(self) -> None:
        _relative_path(self.path, "path")
        if not isinstance(self.git_state, PreparationGitState):
            raise TypeError("git_state must be PreparationGitState")
        if (
            len(self.sha256) != 64
            or any(item not in "0123456789abcdef" for item in self.sha256)
        ):
            raise ValueError("sha256 must be a lowercase SHA-256")
        if not isinstance(self.size, int) or self.size < 0:
            raise ValueError("size must be a non-negative integer")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "git_state": self.git_state.value,
            "sha256": self.sha256,
            "size": self.size,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ArchitectureExecutionPreparationFile":
        return cls(
            path=data["path"],
            git_state=PreparationGitState(data["git_state"]),
            sha256=data["sha256"],
            size=data["size"],
        )


@dataclass(frozen=True)
class ArchitectureExecutionPreparationBaseline:
    baseline_id: str
    workflow_id: str
    architecture_run_id: str
    authorization_id: str
    repository_path: str
    branch: str
    base_commit: str
    created_at: datetime
    allowed_paths: Tuple[str, ...]
    files: Tuple[ArchitectureExecutionPreparationFile, ...]
    git_status_entries: Tuple[str, ...]
    content_hashes: Tuple[str, ...]
    staged_paths: Tuple[str, ...]
    untracked_paths: Tuple[str, ...]
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported preparation baseline schema")
        for value, name, prefix in (
            (self.baseline_id, "baseline_id", "preparation-baseline-"),
            (self.workflow_id, "workflow_id", "workflow-"),
            (
                self.architecture_run_id,
                "architecture_run_id",
                "architecture-run-",
            ),
            (
                self.authorization_id,
                "authorization_id",
                "authorization-",
            ),
        ):
            _identifier(value, name, prefix)
        if not isinstance(self.repository_path, str) or not self.repository_path:
            raise ValueError("repository_path is required")
        if not isinstance(self.branch, str) or not self.branch:
            raise ValueError("branch is required")
        if (
            len(self.base_commit) != 40
            or any(item not in "0123456789abcdef" for item in self.base_commit)
        ):
            raise ValueError("base_commit must be a full lowercase SHA")
        if (
            not isinstance(self.created_at, datetime)
            or self.created_at.tzinfo is None
            or self.created_at.utcoffset() is None
        ):
            raise ValueError("created_at must be timezone-aware")
        _paths(self.allowed_paths, "allowed_paths")
        if (
            not isinstance(self.files, tuple)
            or not self.files
            or not all(
                isinstance(item, ArchitectureExecutionPreparationFile)
                for item in self.files
            )
        ):
            raise ValueError("files must contain preparation files")
        file_paths = tuple(item.path for item in self.files)
        if tuple(sorted(file_paths)) != file_paths or len(set(file_paths)) != len(
            file_paths
        ):
            raise ValueError("preparation files must be unique and sorted")
        _strings(self.git_status_entries, "git_status_entries")
        _strings(self.content_hashes, "content_hashes")
        if self.content_hashes != tuple(item.sha256 for item in self.files):
            raise ValueError("content_hashes must match files")
        _paths(self.staged_paths, "staged_paths")
        _paths(self.untracked_paths, "untracked_paths")
        if self.staged_paths:
            raise ValueError("Preparation baseline cannot contain staged paths")
        if self.untracked_paths != tuple(
            item.path
            for item in self.files
            if item.git_state is PreparationGitState.UNTRACKED
        ):
            raise ValueError("untracked_paths must match files")
        if not set(file_paths).issubset(set(self.allowed_paths)):
            raise ValueError("files must be within allowed_paths")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "baseline_id": self.baseline_id,
            "workflow_id": self.workflow_id,
            "architecture_run_id": self.architecture_run_id,
            "authorization_id": self.authorization_id,
            "repository_path": self.repository_path,
            "branch": self.branch,
            "base_commit": self.base_commit,
            "created_at": self.created_at.isoformat(),
            "allowed_paths": list(self.allowed_paths),
            "files": [item.to_dict() for item in self.files],
            "git_status_entries": list(self.git_status_entries),
            "content_hashes": list(self.content_hashes),
            "staged_paths": list(self.staged_paths),
            "untracked_paths": list(self.untracked_paths),
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ArchitectureExecutionPreparationBaseline":
        expected = {
            "schema_version",
            "baseline_id",
            "workflow_id",
            "architecture_run_id",
            "authorization_id",
            "repository_path",
            "branch",
            "base_commit",
            "created_at",
            "allowed_paths",
            "files",
            "git_status_entries",
            "content_hashes",
            "staged_paths",
            "untracked_paths",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Preparation baseline has invalid fields")
        return cls(
            schema_version=data["schema_version"],
            baseline_id=data["baseline_id"],
            workflow_id=data["workflow_id"],
            architecture_run_id=data["architecture_run_id"],
            authorization_id=data["authorization_id"],
            repository_path=data["repository_path"],
            branch=data["branch"],
            base_commit=data["base_commit"],
            created_at=datetime.fromisoformat(data["created_at"]),
            allowed_paths=tuple(data["allowed_paths"]),
            files=tuple(
                ArchitectureExecutionPreparationFile.from_dict(item)
                for item in data["files"]
            ),
            git_status_entries=tuple(data["git_status_entries"]),
            content_hashes=tuple(data["content_hashes"]),
            staged_paths=tuple(data["staged_paths"]),
            untracked_paths=tuple(data["untracked_paths"]),
        )


@dataclass(frozen=True)
class PreparationBaselineAssessment:
    working_tree_state: PreparationWorkingTreeState
    baseline_valid: bool
    hash_match: bool
    preparation_files: Tuple[str, ...]
    codex_result_changes: Tuple[str, ...]
    unauthorized_changes: Tuple[str, ...]
    missing_paths: Tuple[str, ...]
    modified_paths: Tuple[str, ...]
    staged_paths: Tuple[str, ...]
    error_code: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.working_tree_state, PreparationWorkingTreeState):
            raise TypeError("working_tree_state is invalid")
        for value in (self.baseline_valid, self.hash_match):
            if not isinstance(value, bool):
                raise TypeError("assessment flags must be bool")
        for value, name in (
            (self.preparation_files, "preparation_files"),
            (self.codex_result_changes, "codex_result_changes"),
            (self.unauthorized_changes, "unauthorized_changes"),
            (self.missing_paths, "missing_paths"),
            (self.modified_paths, "modified_paths"),
            (self.staged_paths, "staged_paths"),
        ):
            _paths(value, name)
        if self.error_code is not None and (
            not isinstance(self.error_code, str) or not self.error_code
        ):
            raise ValueError("error_code must be text or None")


class ArchitectureExecutionPreparationStore:
    def __init__(self, workflows: ArchitectureWorkflowStore) -> None:
        self.workflows = workflows

    def path(self, workflow_id: str) -> Path:
        return (
            self.workflows.folder(workflow_id)
            / "executions"
            / "preparation-baseline.json"
        )

    def read(
        self,
        workflow_id: str,
    ) -> Optional[ArchitectureExecutionPreparationBaseline]:
        path = self.path(workflow_id)
        if not path.exists():
            return None
        if not path.is_file() or path.is_symlink():
            raise ValueError("Preparation baseline is unsafe")
        import json

        return ArchitectureExecutionPreparationBaseline.from_dict(
            json.loads(path.read_text(encoding="utf-8"))
        )

    def write(
        self,
        baseline: ArchitectureExecutionPreparationBaseline,
    ) -> Path:
        path = self.path(baseline.workflow_id)
        existing = self.read(baseline.workflow_id)
        if existing is not None:
            if existing != baseline:
                raise PreparationBaselineError(
                    "PREPARATION_BASELINE_CONFLICT",
                    "Existing preparation baseline differs.",
                )
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, baseline.to_dict())
        return path


class ArchitectureExecutionPreparationService:
    def __init__(
        self,
        workflows: ArchitectureWorkflowStore,
        repository: Path,
        feedback: Optional[ArchitectureFeedbackStore] = None,
        store: Optional[ArchitectureExecutionPreparationStore] = None,
        runner: Optional[SubprocessCommandRunner] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.workflows = workflows
        self.repository = repository.resolve()
        self.feedback = feedback or ArchitectureFeedbackStore(workflows)
        self.store = store or ArchitectureExecutionPreparationStore(workflows)
        self.runner = runner or SubprocessCommandRunner()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def prepare(
        self,
        workflow_id: str,
    ) -> ArchitectureExecutionPreparationBaseline:
        authorization = self.feedback.authorization(workflow_id)
        if authorization is None:
            raise PreparationBaselineError(
                "AUTHORIZATION_MISSING",
                "Execution Authorization is required.",
            )
        self.workflows.prompt_proof(workflow_id)
        branch = self._required(("git", "branch", "--show-current"))
        head = self._required(("git", "rev-parse", "HEAD"))
        if (
            authorization.repository != str(self.repository)
            or authorization.authorized_branch != branch
            or authorization.expected_base_commit != head
        ):
            raise PreparationBaselineError(
                "PREPARATION_IDENTITY_MISMATCH",
                "Workflow authorization, repository, branch or commit differ.",
            )
        entries = self._status()
        runtime_path = self.store.path(workflow_id).relative_to(
            self.repository
        ).as_posix()
        entries = tuple(
            entry for entry in entries
            if _parse_status(entry)[1] != runtime_path
        )
        parsed = tuple(_parse_status(item) for item in entries)
        staged = tuple(
            sorted(path for state, path, is_staged in parsed if is_staged)
        )
        if staged:
            raise PreparationBaselineError(
                "PREPARATION_STAGED_CHANGES_NOT_ALLOWED",
                "Preparation baseline cannot contain staged changes.",
            )
        expected = self._expected_paths(workflow_id)
        changed_paths = tuple(sorted(path for _, path, _ in parsed))
        unauthorized = tuple(
            path for path in changed_paths if path not in set(expected)
        )
        if unauthorized:
            raise PreparationBaselineError(
                "UNAUTHORIZED_WORKING_TREE_CHANGES",
                "Working tree contains non-workflow changes: {}".format(
                    ", ".join(unauthorized)
                ),
            )
        if not changed_paths:
            raise PreparationBaselineError(
                "PREPARATION_CHANGES_MISSING",
                "Official workflow preparation changes are missing.",
            )
        states = {path: state for state, path, _ in parsed}
        if any(states[path] is not PreparationGitState.UNTRACKED for path in changed_paths):
            raise PreparationBaselineError(
                "PREPARATION_EXISTING_FILE_MODIFIED",
                "Preparation cannot modify existing versioned files.",
            )
        files = tuple(
            self._file(path, states[path]) for path in changed_paths
        )
        baseline_id = stable_identifier(
            "preparation-baseline",
            workflow_id,
            authorization.architecture_run_id,
            authorization.authorization_id,
            branch,
            head,
            *(
                "{}:{}:{}:{}".format(
                    item.path,
                    item.git_state.value,
                    item.sha256,
                    item.size,
                )
                for item in files
            )
        )
        candidate = ArchitectureExecutionPreparationBaseline(
            baseline_id=baseline_id,
            workflow_id=workflow_id,
            architecture_run_id=authorization.architecture_run_id,
            authorization_id=authorization.authorization_id,
            repository_path=str(self.repository),
            branch=branch,
            base_commit=head,
            created_at=self.clock(),
            allowed_paths=expected,
            files=files,
            git_status_entries=entries,
            content_hashes=tuple(item.sha256 for item in files),
            staged_paths=(),
            untracked_paths=tuple(item.path for item in files),
        )
        existing = self.store.read(workflow_id)
        if existing is not None:
            if (
                existing.baseline_id != candidate.baseline_id
                or existing.to_dict()
                != {
                    **candidate.to_dict(),
                    "created_at": existing.created_at.isoformat(),
                }
            ):
                raise PreparationBaselineError(
                    "PREPARATION_BASELINE_CONFLICT",
                    "Preparation state differs from immutable baseline.",
                )
            return existing
        self.store.write(candidate)
        return candidate

    def assess(
        self,
        baseline: ArchitectureExecutionPreparationBaseline,
        authorization: ExecutionAuthorization,
        branch: str,
        head: str,
        status_entries: Tuple[str, ...],
        allow_result_changes: bool,
    ) -> PreparationBaselineAssessment:
        identity_matches = (
            baseline.workflow_id == authorization.workflow_id
            and baseline.architecture_run_id
            == authorization.architecture_run_id
            and baseline.authorization_id == authorization.authorization_id
            and baseline.repository_path == str(self.repository)
            and baseline.branch == branch == authorization.authorized_branch
            and baseline.base_commit
            == head
            == authorization.expected_base_commit
        )
        parsed = tuple(_parse_status(item) for item in status_entries)
        runtime_path = self.store.path(baseline.workflow_id).relative_to(
            self.repository
        ).as_posix()
        parsed = tuple(
            item for item in parsed if item[1] != runtime_path
        )
        current_paths = tuple(sorted(path for _, path, _ in parsed))
        staged = tuple(
            sorted(path for _, path, is_staged in parsed if is_staged)
        )
        baseline_paths = tuple(item.path for item in baseline.files)
        missing = tuple(
            path for path in baseline_paths if path not in current_paths
        )
        modified = []
        for item in baseline.files:
            path = self.repository / item.path
            if (
                not path.is_file()
                or path.is_symlink()
                or _hash(path) != item.sha256
                or path.stat().st_size != item.size
            ):
                modified.append(item.path)
        result_changes = tuple(
            path for path in current_paths if path not in set(baseline_paths)
        )
        unauthorized = result_changes if not allow_result_changes else ()
        hash_match = not modified and not missing
        error_code = None
        if staged:
            error_code = "PREPARATION_STAGED_CHANGES_NOT_ALLOWED"
        elif not identity_matches or missing or modified or unauthorized:
            error_code = "PREPARATION_BASELINE_MISMATCH"
        return PreparationBaselineAssessment(
            working_tree_state=(
                PreparationWorkingTreeState.AUTHORIZED_PREPARATION_CHANGES
                if error_code is None
                else PreparationWorkingTreeState.UNAUTHORIZED_DIRTY_WORKING_TREE
            ),
            baseline_valid=error_code is None,
            hash_match=hash_match,
            preparation_files=baseline_paths,
            codex_result_changes=result_changes,
            unauthorized_changes=unauthorized,
            missing_paths=missing,
            modified_paths=tuple(sorted(modified)),
            staged_paths=staged,
            error_code=error_code,
        )

    def _expected_paths(self, workflow_id: str) -> Tuple[str, ...]:
        workflow = self.workflows.load(workflow_id)
        folder = self.workflows.folder(workflow_id)
        root = folder.relative_to(self.repository).as_posix()
        relatives = (
            "workflow.json",
            *workflow.proposal_files,
            *workflow.analysis_files,
            workflow.decision_template_file,
            *workflow.decision_template_files,
            *(
                "decisions/{}.json".format(item)
                for item in workflow.proposal_ids
            ),
            "prompts/codex-prompt.md",
            "prompts/codex-prompt-proof.json",
            "feedback/execution-authorization.json",
        )
        paths = tuple(sorted(
            "{}/{}".format(root, item) for item in dict.fromkeys(relatives)
        ))
        for relative in paths:
            path = self.repository / relative
            if (
                not path.is_file()
                or path.is_symlink()
                or path.resolve().parent == self.repository.resolve()
            ):
                raise PreparationBaselineError(
                    "PREPARATION_ARTIFACT_MISSING",
                    "Expected workflow artifact is missing or unsafe: {}".format(
                        relative
                    ),
                )
        return paths

    def _file(
        self,
        relative: str,
        state: PreparationGitState,
    ) -> ArchitectureExecutionPreparationFile:
        path = self.repository / relative
        if not path.is_file() or path.is_symlink():
            raise PreparationBaselineError(
                "PREPARATION_ARTIFACT_MISSING",
                "Preparation artifact is missing or unsafe: {}".format(relative),
            )
        return ArchitectureExecutionPreparationFile(
            path=relative,
            git_state=state,
            sha256=_hash(path),
            size=path.stat().st_size,
        )

    def _status(self) -> Tuple[str, ...]:
        return tuple(
            line
            for line in self._required((
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            )).splitlines()
            if line
        )

    def _required(self, arguments: Tuple[str, ...]) -> str:
        result: CommandResult = self.runner.run(
            arguments,
            cwd=self.repository,
        )
        if result.exit_code != 0:
            raise PreparationBaselineError(
                "PREPARATION_GIT_FAILED",
                "{} failed: {}".format(arguments[0], result.output.strip()),
            )
        return result.stdout.rstrip("\r\n")


def _parse_status(
    entry: str,
) -> Tuple[PreparationGitState, str, bool]:
    if not isinstance(entry, str) or len(entry) < 4 or entry[2] != " ":
        raise PreparationBaselineError(
            "PREPARATION_GIT_STATUS_INVALID",
            "Git status entry is invalid.",
        )
    code = entry[:2]
    path = entry[3:]
    if " -> " in path or path.startswith('"'):
        raise PreparationBaselineError(
            "PREPARATION_GIT_STATUS_UNSAFE",
            "Renamed or quoted paths are not supported in preparation v1.",
        )
    _relative_path(path, "git status path")
    staged = code[0] not in {" ", "?"}
    state = (
        PreparationGitState.UNTRACKED
        if code == "??"
        else PreparationGitState.MODIFIED
    )
    return state, path, staged


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identifier(value: object, name: str, prefix: str) -> None:
    if (
        not isinstance(value, str)
        or not value.startswith(prefix)
        or len(value) != len(prefix) + 16
        or any(item not in "0123456789abcdef" for item in value[len(prefix):])
    ):
        raise ValueError("{} is invalid".format(name))


def _relative_path(value: object, name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError("{} is required".format(name))
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value != path.as_posix():
        raise ValueError("{} must be a safe relative path".format(name))


def _paths(value: object, name: str) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(name))
    for item in value:
        _relative_path(item, name)
    if tuple(sorted(value)) != value or len(set(value)) != len(value):
        raise ValueError("{} must be unique and sorted".format(name))


def _strings(value: object, name: str) -> None:
    if (
        not isinstance(value, tuple)
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise TypeError("{} must contain strings".format(name))
