from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence, Tuple

from builder_task.models import (
    ApprovalAction,
    CommitApproval,
    ImmutableTask,
    PushApproval,
    RunResult,
    VetoClassification,
)
from builder_task.service import BuilderTaskService, TaskRunError


@dataclass(frozen=True)
class DevelopmentReport:
    goal: str
    codex_answer: str
    changed_files: Tuple[str, ...]
    tests: str
    doctor: str
    diff_status: str
    git_status: Tuple[str, ...]
    blockers: Tuple[str, ...]
    commit_ready: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "Ziel": self.goal,
            "Codex-Antwort": self.codex_answer,
            "Geänderte Dateien": list(self.changed_files),
            "Tests": self.tests,
            "Doctor": self.doctor,
            "Diff-Status": self.diff_status,
            "Git-Status": list(self.git_status),
            "Blocker": list(self.blockers),
            "Commit bereit": (
                "Kein Commit erforderlich"
                if not self.changed_files
                else ("Ja" if self.commit_ready else "Nein")
            ),
        }


class DevelopmentService:
    """A presentation layer over the single Builder Reset v2 execution core."""

    VETO_TERMS = (
        "autorisierung",
        "authorization",
        "governance",
        "datenhoheit",
        "data sovereignty",
        "execution security",
        "sicherheitskritische ausführung",
    )

    def __init__(
        self,
        repository: Path,
        core_factory: Callable[[Path], BuilderTaskService] = BuilderTaskService,
        now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.repository = repository.resolve()
        self.core_factory = core_factory
        self.now = now

    def run(
        self,
        goal: str,
        branch: Optional[str] = None,
        paths: Sequence[str] = (),
        veto: Optional[VetoClassification] = None,
        no_commit: bool = False,
        no_tests: bool = False,
    ) -> DevelopmentReport:
        goal = _text(goal, "goal")
        core = self.core_factory(self.repository)
        actual_branch = core._git("branch", "--show-current").stdout.strip()
        actual_head = core._git("rev-parse", "HEAD").stdout.strip()
        selected_branch = branch or actual_branch
        allowed_paths = tuple(sorted(set(paths or (".",))))
        classification = veto or self._classify_veto(goal)

        if classification is not VetoClassification.NO_VETO:
            blocker = (
                "PLAN_APPROVAL_REQUIRED"
                if classification is VetoClassification.VETO_REQUIRED
                else "VETO_CLASSIFICATION_REQUIRED"
            )
            return DevelopmentReport(
                goal=goal,
                codex_answer="Nicht ausgeführt",
                changed_files=(),
                tests="Nicht ausgeführt",
                doctor="Nicht ausgeführt",
                diff_status="Nicht geprüft",
                git_status=core._status_entries(),
                blockers=(blocker,),
                commit_ready=False,
            )

        if no_tests:
            return DevelopmentReport(
                goal=goal,
                codex_answer="Nicht ausgeführt",
                changed_files=(),
                tests="Nicht ausgeführt",
                doctor="Nicht ausgeführt",
                diff_status="Nicht geprüft",
                git_status=core._status_entries(),
                blockers=("TESTS_REQUIRED_BY_GIT_GATE",),
                commit_ready=False,
            )

        task = ImmutableTask(
            task_id=_task_id(
                self.repository,
                selected_branch,
                actual_head,
                goal,
                allowed_paths,
                classification,
                not no_commit,
            ),
            repository=str(self.repository),
            branch=selected_branch,
            start_head=actual_head,
            goal=goal,
            allowed_paths=allowed_paths,
            non_goals=(
                "Do not choose a workflow.",
                "Do not stage, commit, or push during execution.",
            ),
            veto_classification=classification,
            commit_permitted=not no_commit,
            push_permitted=True,
        )
        try:
            receipt = core.run(task)
        except TaskRunError as error:
            return DevelopmentReport(
                goal=goal,
                codex_answer="Nicht ausgeführt",
                changed_files=(),
                tests="Nicht ausgeführt",
                doctor="Nicht ausgeführt",
                diff_status="Nicht geprüft",
                git_status=core._status_entries(),
                blockers=(error.code,),
                commit_ready=False,
            )

        checks = {check.command: check for check in receipt.checks}
        tests = checks.get(("python3", "-m", "pytest", "-q"))
        doctor = checks.get(("python3", "-m", "builder.main", "doctor"))
        diff = checks.get(("git", "diff", "--check"))
        blockers = tuple(receipt.git_gate.blockers)
        if receipt.result is not RunResult.COMPLETED:
            blockers = tuple(sorted(set(blockers + ("EXECUTION_FAILED",))))
        return DevelopmentReport(
            goal=goal,
            codex_answer=(
                core.store.task_dir(task.task_id) / "stdout.log"
            ).read_text(encoding="utf-8"),
            changed_files=receipt.git_gate.changed_paths,
            tests=_check_label(tests),
            doctor=_check_label(doctor),
            diff_status=_check_label(diff),
            git_status=core._status_entries(),
            blockers=blockers,
            commit_ready=(
                receipt.result is RunResult.COMPLETED
                and receipt.git_gate.passed
                and task.commit_permitted
                and bool(receipt.git_gate.changed_paths)
            ),
        )

    def commit(self, message: Optional[str] = None, approved_by: str = "Human") -> str:
        core, task = self._current_task(before_commit=True)
        receipt = core.store.load_receipt(task.task_id)
        if receipt is None:
            raise TaskRunError("COMMIT_NOT_READY", "No completed development run")
        approval = CommitApproval(
            task_id=task.task_id,
            branch=task.branch,
            head=task.start_head,
            diff_hash=core.diff_hash(),
            action=ApprovalAction.COMMIT,
            approved_at=self.now(),
            approved_by=_text(approved_by, "approved_by"),
        )
        return core.commit(
            task.task_id,
            approval,
            message or _commit_message(task.goal),
        )

    def push(
        self,
        remote: str = "origin",
        remote_branch: Optional[str] = None,
        approved_by: str = "Human",
    ) -> str:
        core, task = self._current_task(before_commit=False)
        head = core._git("rev-parse", "HEAD").stdout.strip()
        branch = core._git("branch", "--show-current").stdout.strip()
        approval = PushApproval(
            task_id=task.task_id,
            branch=branch,
            commit=head,
            remote=_text(remote, "remote"),
            remote_branch=remote_branch or branch,
            action=ApprovalAction.PUSH,
            approved_at=self.now(),
            approved_by=_text(approved_by, "approved_by"),
        )
        return core.push(task.task_id, approval)

    def _current_task(self, before_commit: bool) -> Tuple[BuilderTaskService, ImmutableTask]:
        core = self.core_factory(self.repository)
        branch = core._git("branch", "--show-current").stdout.strip()
        head = core._git("rev-parse", "HEAD").stdout.strip()
        candidates = []
        if core.store.root.exists():
            for directory in sorted(core.store.root.iterdir()):
                task_path = directory / "task.json"
                receipt_path = directory / "receipt.json"
                if not task_path.is_file() or not receipt_path.is_file():
                    continue
                task = core.store.load_task(directory.name)
                receipt = core.store.load_receipt(task.task_id)
                if (
                    task.repository != str(self.repository)
                    or task.branch != branch
                    or receipt is None
                    or not receipt.git_gate.passed
                ):
                    continue
                if before_commit:
                    if task.start_head == head and core.diff_hash() == receipt.git_gate.diff_hash:
                        candidates.append(task)
                else:
                    parent = core._git("rev-parse", "{}^".format(head))
                    if (
                        receipt.result is RunResult.COMPLETED
                        and task.commit_permitted
                        and receipt.git_gate.changed_paths
                        and parent.exit_code == 0
                        and parent.stdout.strip() == task.start_head
                    ):
                        candidates.append(task)
        if len(candidates) != 1:
            raise TaskRunError(
                "DEVELOPMENT_CONTEXT_AMBIGUOUS",
                "Expected one matching completed development task",
            )
        return core, candidates[0]

    @classmethod
    def _classify_veto(cls, goal: str) -> VetoClassification:
        lowered = goal.casefold()
        if any(term in lowered for term in cls.VETO_TERMS):
            return VetoClassification.VETO_REQUIRED
        return VetoClassification.NO_VETO


def _task_id(
    repository: Path,
    branch: str,
    head: str,
    goal: str,
    paths: Sequence[str],
    veto: VetoClassification,
    commit_permitted: bool,
) -> str:
    payload = json.dumps(
        {
            "repository": str(repository),
            "branch": branch,
            "head": head,
            "goal": goal,
            "paths": list(paths),
            "veto": veto.value,
            "commit_permitted": commit_permitted,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "task-develop-{}".format(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16])


def _check_label(check: object) -> str:
    if check is None:
        return "Nicht ausgeführt"
    return "Erfolgreich" if check.passed else "Fehlgeschlagen"


def _commit_message(goal: str) -> str:
    normalized = goal.strip().rstrip(".")
    return normalized[0].upper() + normalized[1:]


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("{} must be non-empty trimmed text".format(name))
    return value
