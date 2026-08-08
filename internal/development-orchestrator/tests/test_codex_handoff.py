from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

import pytest

from development_orchestrator.backends import OfflineContractBackend
from development_orchestrator.codex_handoff import (
    CodexCommandResult,
    DetachedCodexJobLauncher,
    CodexHandoffError,
    CodexHandoffService,
    LocalCodexRunner,
)
from development_orchestrator.front_door import (
    ContextCandidate,
    FrontDoorService,
)
from development_orchestrator.schemas import CodexHandoffStatus, WorkRequest


class RecordingRunner:
    def __init__(self, mutation=None, failure: Exception | None = None) -> None:
        self.mutation = mutation
        self.failure = failure
        self.calls: list[tuple[Path, str]] = []

    def run(self, repository: Path, prompt: str) -> CodexCommandResult:
        self.calls.append((repository, prompt))
        if self.failure:
            raise self.failure
        if self.mutation:
            self.mutation(repository)
        return CodexCommandResult(
            exit_code=0,
            stdout=(
                '{"type":"item.completed","item":{"type":"agent_message",'
                '"text":"Synthetic Codex result."}}\n'
            ),
            stderr="",
        )


class RecordingLauncher:
    def __init__(self, process_id: int = 424242) -> None:
        self.process_id = process_id
        self.calls = []

    def start(
        self, repository, tool_root, run_id, job_id, authorized_branch
    ) -> int:
        self.calls.append(
            (repository, tool_root, run_id, job_id, authorized_branch)
        )
        return self.process_id


def request() -> WorkRequest:
    return WorkRequest(
        goal="Prepare one synthetic reviewed implementation package",
        scope=["synthetic package only"],
        requested_output="reviewable local changes",
        approval_constraints=["no commit", "no push"],
        max_iterations=2,
    )


def completed_run(isolated_repository) -> str:
    repository, tool_root = isolated_repository
    front = FrontDoorService(
        repository,
        tool_root,
        lambda: OfflineContractBackend(),
    )
    pending = front.submit_work(
        request(),
        [
            ContextCandidate(
                path="docs/research.md",
                reason="Synthetic reviewed evidence.",
            )
        ],
    )
    completed = front.approve_context(
        pending.run_id,
        ["docs/research.md"],
        approved=True,
    )
    assert completed.status.value == "COMPLETED"
    return completed.run_id


def handoff_service(
    isolated_repository,
    runner,
    launcher=None,
    process_exists=None,
) -> CodexHandoffService:
    repository, tool_root = isolated_repository
    return CodexHandoffService(
        repository,
        tool_root,
        authorized_branch="main",
        runner=runner,
        job_launcher=launcher or RecordingLauncher(),
        process_exists=process_exists,
    )


def test_handoff_without_explicit_approval_is_blocked(isolated_repository) -> None:
    run_id = completed_run(isolated_repository)
    with pytest.raises(CodexHandoffError, match="explicit human"):
        handoff_service(isolated_repository, RecordingRunner()).handoff_reviewed_run(
            run_id,
            approved=False,
            allowed_repository_paths=["docs/output.md"],
        )


def test_unknown_run_and_unreviewed_run_are_blocked(isolated_repository) -> None:
    service = handoff_service(isolated_repository, RecordingRunner())
    with pytest.raises(CodexHandoffError, match="incomplete"):
        service.handoff_reviewed_run(
            "run-unknown",
            approved=True,
            allowed_repository_paths=["docs/output.md"],
        )

    repository, tool_root = isolated_repository
    pending = FrontDoorService(
        repository, tool_root, lambda: OfflineContractBackend()
    ).submit_work(
        request(),
        [ContextCandidate(path="README.md", reason="Synthetic context")],
    )
    with pytest.raises(CodexHandoffError, match="incomplete"):
        service.handoff_reviewed_run(
            pending.run_id,
            approved=True,
            allowed_repository_paths=["docs/output.md"],
        )


def test_open_founder_review_requires_explicit_coverage(isolated_repository) -> None:
    run_id = completed_run(isolated_repository)
    _, tool_root = isolated_repository
    root = tool_root / "runs" / run_id
    result = json.loads((root / "result.json").read_text(encoding="utf-8"))
    result["founder_decision_required"] = True
    (root / "result.json").write_text(json.dumps(result), encoding="utf-8")
    front = json.loads((root / "front-door.json").read_text(encoding="utf-8"))
    front["open_decision"] = "Founder review is required."
    (root / "front-door.json").write_text(json.dumps(front), encoding="utf-8")
    service = handoff_service(isolated_repository, RecordingRunner())

    with pytest.raises(CodexHandoffError, match="founder review"):
        service.handoff_reviewed_run(
            run_id,
            approved=True,
            allowed_repository_paths=["docs/output.md"],
        )

    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        founder_review_approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    record = service.run_job(run_id, accepted.job_id)
    assert record.status is CodexHandoffStatus.COMPLETED


def test_one_reviewed_run_creates_audited_one_shot_handoff(
    isolated_repository,
) -> None:
    run_id = completed_run(isolated_repository)
    runner = RecordingRunner(
        lambda repository: (repository / "docs" / "output.md").write_text(
            "synthetic\n", encoding="utf-8"
        )
    )
    service = handoff_service(isolated_repository, runner)
    started = time.monotonic()
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )

    assert time.monotonic() - started < 2
    assert accepted.result == "ACCEPTED"
    assert accepted.status is CodexHandoffStatus.RUNNING
    assert not runner.calls
    record = service.run_job(run_id, accepted.job_id)
    assert record.status is CodexHandoffStatus.COMPLETED
    assert record.human_approved is True
    assert record.exit_code == 0
    assert runner.calls[0][0] == isolated_repository[0]
    prompt = runner.calls[0][1]
    assert "Run ID: {}".format(run_id) in prompt
    assert "Do not commit, push" in prompt
    assert "docs/output.md" in prompt
    run_root = isolated_repository[1] / "runs" / run_id
    assert (run_root / "codex-handoff.md").is_file()
    audit = json.loads((run_root / "codex-handoff.json").read_text(encoding="utf-8"))
    assert audit["status"] == "COMPLETED"
    assert set(audit["evidence_sha256"]) == set(service.EVIDENCE_FILES)

    with pytest.raises(CodexHandoffError, match="already"):
        service.handoff_reviewed_run(
            run_id,
            approved=True,
            allowed_repository_paths=["docs/output.md"],
        )


@pytest.mark.parametrize(
    "path",
    [".", "../escape.md", "/tmp/escape.md", ".git/config"],
)
def test_handoff_rejects_broad_or_escaping_write_scope(
    isolated_repository, path: str
) -> None:
    run_id = completed_run(isolated_repository)
    with pytest.raises(CodexHandoffError):
        handoff_service(isolated_repository, RecordingRunner()).handoff_reviewed_run(
            run_id,
            approved=True,
            allowed_repository_paths=[path],
        )


def test_out_of_scope_write_fails_closed(isolated_repository) -> None:
    run_id = completed_run(isolated_repository)
    runner = RecordingRunner(
        lambda repository: (repository / "outside.md").write_text(
            "forbidden\n", encoding="utf-8"
        )
    )
    service = handoff_service(isolated_repository, runner)
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    record = service.run_job(run_id, accepted.job_id)
    assert record.status is CodexHandoffStatus.FAILED
    assert "outside authorized paths" in record.failure_reason


def test_runner_failure_is_audited_fail_closed(isolated_repository) -> None:
    run_id = completed_run(isolated_repository)
    service = handoff_service(
        isolated_repository,
        RecordingRunner(failure=RuntimeError("synthetic failure")),
    )
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    record = service.run_job(run_id, accepted.job_id)
    assert record.status is CodexHandoffStatus.FAILED
    assert record.failure_reason == "synthetic failure"


def test_nonzero_runner_exit_is_audited_with_exit_code(isolated_repository) -> None:
    class FailingRunner:
        def run(self, repository, prompt):
            return CodexCommandResult(7, "", "synthetic command failure")

    run_id = completed_run(isolated_repository)
    service = handoff_service(isolated_repository, FailingRunner())
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    record = service.run_job(run_id, accepted.job_id)
    assert record.status is CodexHandoffStatus.FAILED
    assert record.exit_code == 7
    assert "synthetic command failure" in record.failure_reason


def test_running_job_status_identifies_missing_worker_as_orphaned(
    isolated_repository,
) -> None:
    run_id = completed_run(isolated_repository)
    service = handoff_service(
        isolated_repository,
        RecordingRunner(),
        process_exists=lambda process_id: False,
    )
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    running = service._read_handoff_record(run_id).model_copy(
        update={"worker_pid": 999999}
    )
    service._write_record(running)

    status = service.get_handoff_status(run_id)
    assert status is not None
    assert status.record.status is CodexHandoffStatus.RUNNING
    assert status.worker_alive is False
    assert status.orphaned is True


def test_existing_terminal_handoff_record_stays_one_shot(
    isolated_repository,
) -> None:
    run_id = completed_run(isolated_repository)
    service = handoff_service(
        isolated_repository,
        RecordingRunner(failure=RuntimeError("terminal synthetic failure")),
    )
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    assert service.run_job(run_id, accepted.job_id).status is CodexHandoffStatus.FAILED

    with pytest.raises(CodexHandoffError, match="already"):
        service.handoff_reviewed_run(
            run_id,
            approved=True,
            allowed_repository_paths=["docs/output.md"],
        )


def test_parallel_handoff_requests_create_exactly_one_job(
    isolated_repository,
) -> None:
    run_id = completed_run(isolated_repository)
    services = [
        handoff_service(isolated_repository, RecordingRunner()),
        handoff_service(isolated_repository, RecordingRunner()),
    ]
    barrier = threading.Barrier(2)
    for service in services:
        create_json = service.writer.create_json

        def synchronized_create(target, value, create_json=create_json):
            barrier.wait(timeout=5)
            return create_json(target, value)

        service.writer.create_json = synchronized_create

    def submit(service):
        try:
            return service.handoff_reviewed_run(
                run_id,
                approved=True,
                allowed_repository_paths=["docs/output.md"],
            )
        except CodexHandoffError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(submit, services))

    accepted = [result for result in results if not isinstance(result, Exception)]
    rejected = [result for result in results if isinstance(result, Exception)]
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert "already has" in str(rejected[0])


def test_detached_launcher_does_not_bind_worker_to_client_stdio(
    isolated_repository, monkeypatch
) -> None:
    captured = {}
    monkeypatch.setenv("CONTROL_PLANE_API_KEY", "must-not-reach-worker")

    class Process:
        pid = 321

    def fake_popen(arguments, **options):
        captured["arguments"] = arguments
        captured["options"] = options
        return Process()

    monkeypatch.setattr(
        "development_orchestrator.codex_handoff.subprocess.Popen", fake_popen
    )
    repository, tool_root = isolated_repository
    process_id = DetachedCodexJobLauncher().start(
        repository,
        tool_root,
        "run-synthetic",
        "job-synthetic",
        "main",
    )

    assert process_id == 321
    assert captured["options"]["start_new_session"] is True
    assert captured["options"]["close_fds"] is True
    assert captured["options"]["stdin"] is subprocess.DEVNULL
    assert captured["options"]["stdout"] is subprocess.DEVNULL
    assert captured["options"]["stderr"] is subprocess.DEVNULL
    assert "CONTROL_PLANE_API_KEY" not in captured["options"]["env"]
    assert "--run-id" in captured["arguments"]
    assert "run-synthetic" in captured["arguments"]


def test_detached_worker_completes_after_service_scope_ends(
    isolated_repository, tmp_path, monkeypatch
) -> None:
    executable_directory = tmp_path / "bin"
    executable_directory.mkdir()
    executable = executable_directory / "codex"
    executable.write_text(
        "#!{}\n".format(sys.executable)
        + "import json, sys, time\n"
        + "sys.stdin.read()\n"
        + "time.sleep(0.25)\n"
        + "print(json.dumps({'type': 'item.completed', 'item': "
        + "{'type': 'agent_message', 'text': 'Detached synthetic result.'}}))\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv(
        "PATH", "{}:{}".format(executable_directory, os.environ.get("PATH", ""))
    )
    run_id = completed_run(isolated_repository)
    repository, tool_root = isolated_repository
    service = CodexHandoffService(
        repository,
        tool_root,
        authorized_branch="main",
    )
    accepted = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    del service

    record_path = tool_root / "runs" / run_id / "codex-handoff.json"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        audit = json.loads(record_path.read_text(encoding="utf-8"))
        if audit["status"] != "RUNNING":
            break
        time.sleep(0.05)

    assert audit["status"] == "COMPLETED"
    assert audit["job_id"] == accepted.job_id
    assert audit["exit_code"] == 0
    assert audit["result_summary"] == "Detached synthetic result."
    changed = git_status(repository).splitlines()
    assert changed
    assert all("internal/development-orchestrator/runs/" in line for line in changed)
    assert not (repository / "docs" / "output.md").exists()


def git_status(repository: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_handoff_has_no_generic_command_or_git_interface() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "development_orchestrator"
        / "codex_handoff.py"
    )
    text = source.read_text(encoding="utf-8")
    assert "shell=True" not in text
    assert "git commit" not in text
    assert "git push" not in text
    assert "command:" not in text


def test_local_codex_runner_uses_fixed_noninteractive_fail_closed_contract(
    isolated_repository, monkeypatch
) -> None:
    captured = {}

    def fake_run(arguments, **options):
        captured["arguments"] = arguments
        captured["options"] = options
        return type(
            "Completed",
            (),
            {"returncode": 0, "stdout": "", "stderr": ""},
        )()

    monkeypatch.setattr(
        "development_orchestrator.codex_handoff.subprocess.run", fake_run
    )
    repository, _ = isolated_repository
    LocalCodexRunner(executable_resolver=lambda: "/usr/local/bin/codex").run(
        repository, "reviewed prompt"
    )
    arguments = captured["arguments"]
    assert arguments[:2] == ["/usr/local/bin/codex", "exec"]
    assert "workspace-write" in arguments
    assert "--ignore-user-config" in arguments
    assert "--ephemeral" in arguments
    assert 'approval_policy="never"' in arguments
    assert "sandbox_workspace_write.network_access=false" in arguments
    assert "shell_environment_policy.ignore_default_excludes=false" in arguments
    assert "agents.enabled=false" in arguments
    assert captured["options"]["input"] == "reviewed prompt"
    assert captured["options"]["cwd"] == str(repository)
    assert "commit" not in arguments
    assert "push" not in arguments
