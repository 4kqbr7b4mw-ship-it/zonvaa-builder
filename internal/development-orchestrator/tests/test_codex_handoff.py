from __future__ import annotations

import json
from pathlib import Path

import pytest

from development_orchestrator.backends import OfflineContractBackend
from development_orchestrator.codex_handoff import (
    CodexCommandResult,
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


def handoff_service(isolated_repository, runner) -> CodexHandoffService:
    repository, tool_root = isolated_repository
    return CodexHandoffService(
        repository,
        tool_root,
        authorized_branch="main",
        runner=runner,
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

    record = service.handoff_reviewed_run(
        run_id,
        approved=True,
        founder_review_approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    assert record.status is CodexHandoffStatus.SUCCEEDED


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
    record = service.handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )

    assert record.status is CodexHandoffStatus.SUCCEEDED
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
    assert audit["status"] == "SUCCEEDED"
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
    record = handoff_service(isolated_repository, runner).handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    assert record.status is CodexHandoffStatus.FAILED
    assert "outside authorized paths" in record.failure_reason


def test_runner_failure_is_audited_fail_closed(isolated_repository) -> None:
    run_id = completed_run(isolated_repository)
    record = handoff_service(
        isolated_repository,
        RecordingRunner(failure=RuntimeError("synthetic failure")),
    ).handoff_reviewed_run(
        run_id,
        approved=True,
        allowed_repository_paths=["docs/output.md"],
    )
    assert record.status is CodexHandoffStatus.FAILED
    assert record.failure_reason == "synthetic failure"


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
