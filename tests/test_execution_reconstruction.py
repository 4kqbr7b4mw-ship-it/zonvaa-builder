import json
import subprocess
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from architecture_integrator import (
    ArchitectureIntegrator,
    ArchitectureWorkflowStore,
    FeedbackStatus,
)
from codex_execution import ExecutionOrigin, ExecutionStore
from codex_execution.reconstruction import (
    ExecutionReconstructionAuthorization,
    ExecutionReconstructionError,
    ExecutionReconstructionRequest,
    ExecutionReconstructionService,
    ReconstructionAuthorizationStatus,
    ReconstructionFailureKind,
    ReconstructionSource,
)


NOW = datetime(2026, 7, 27, 17, 0, tzinfo=timezone.utc)


def git(repository, *arguments):
    result = subprocess.run(
        ("git",) + arguments,
        cwd=str(repository),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def repository_fixture(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir(parents=True)
    git(repository, "init", "-q")
    git(repository, "config", "user.name", "Test User")
    git(repository, "config", "user.email", "test@example.invalid")
    (repository / "base.txt").write_text("base\n", encoding="utf-8")
    git(repository, "add", "base.txt")
    git(repository, "commit", "-q", "-m", "Base")
    start = git(repository, "rev-parse", "HEAD")
    handovers = repository / "knowledge" / "handovers"
    handovers.mkdir(parents=True)
    json_relative = "knowledge/handovers/result.json"
    markdown_relative = "knowledge/handovers/result.md"
    payload = {
        "schema_version": "1.0",
        "starting_commit": start,
        "ending_commit": None,
        "changed_files": [json_relative, markdown_relative],
        "checks": [
            {
                "command": "python3 -m pytest -q",
                "status": "passed",
                "result": "10 passed",
            },
            {
                "command": "python3 -m builder.main doctor",
                "status": "passed",
                "result": "Doctor passed",
            },
            {
                "command": "git diff --check",
                "status": "passed",
                "result": "No whitespace errors",
            },
        ],
        "git_status": ["Worktree was clean after commit."],
        "open_risks": ["External verification remains separate."],
        "push_status": "not_pushed",
    }
    (repository / json_relative).write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    (repository / markdown_relative).write_text(
        "# Result handover\n",
        encoding="utf-8",
    )
    git(repository, "add", "knowledge")
    git(repository, "commit", "-q", "-m", "Result")
    result = git(repository, "rev-parse", "HEAD")
    workflows = ArchitectureWorkflowStore(
        repository / "knowledge" / "architecture_workflows"
    )
    workflows.root.mkdir(parents=True)
    authorization = ExecutionReconstructionAuthorization(
        authorization_id="reconstruction-authorization-0123456789abcdef",
        decision_reference="decision:chief-architect-confirmed",
        repository=str(repository),
        expected_start_commit=start,
        expected_result_commit=result,
        expected_handover_paths=(json_relative, markdown_relative),
        allowed_actions=("reconstruct_execution", "create_review"),
        authorized_at=NOW,
        status=ReconstructionAuthorizationStatus.CONFIRMED,
    )
    integrator = object.__new__(ArchitectureIntegrator)
    service = ExecutionReconstructionService(
        repository,
        workflows,
        integrator,
    )
    request = ExecutionReconstructionRequest(
        authorization=authorization,
        reconstructed_at=NOW,
        source=ReconstructionSource.CHIEF_ARCHITECT_AUTHORIZATION,
    )
    return repository, workflows, service, request


def failure(service, request, expected):
    with pytest.raises(ExecutionReconstructionError) as raised:
        service.reconstruct(request)
    assert raised.value.failure.kind is expected
    assert "token=" not in raised.value.failure.message


def rewrite_handover(repository, authorization, transform):
    path = repository / authorization.expected_handover_paths[0]
    payload = json.loads(path.read_text(encoding="utf-8"))
    transform(payload)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_successful_reconstruction_reuses_feedback_loop(tmp_path):
    repository, workflows, service, request = repository_fixture(tmp_path)

    result = service.reconstruct(request)

    assert result.execution.origin is ExecutionOrigin.RECONSTRUCTED
    assert result.execution.attempts == ()
    assert result.execution.started_at is None
    assert result.execution.completed_at is None
    assert result.execution.codex_exit_code is None
    assert result.execution.reconstruction_source == (
        "CHIEF_ARCHITECT_AUTHORIZATION"
    )
    assert result.execution.execution_id.startswith(
        "reconstructed-execution-"
    )
    assert result.feedback.status is (
        FeedbackStatus.CHIEF_ARCHITECT_DECISION_REQUIRED
    )
    feedback = (
        workflows.folder(result.workflow_id)
        / "executions"
        / "feedback"
    )
    assert (feedback / "handover-intake.json").is_file()
    assert (feedback / "integrator-review.json").is_file()


def test_models_are_immutable_and_authorization_is_separate(tmp_path):
    _, _, _, request = repository_fixture(tmp_path)
    with pytest.raises(FrozenInstanceError):
        request.authorization.status = None
    with pytest.raises(TypeError):
        ExecutionReconstructionRequest(
            authorization=None,
            reconstructed_at=NOW,
            source=ReconstructionSource.CHIEF_ARCHITECT_AUTHORIZATION,
        )


def test_missing_or_wrong_authorization_blocks(tmp_path):
    repository, workflows, service, request = repository_fixture(tmp_path)
    failure(service, None, ReconstructionFailureKind.AUTHORIZATION_MISSING)
    wrong = replace(
        request.authorization,
        repository=str(repository / "other"),
    )
    failure(
        service,
        replace(request, authorization=wrong),
        ReconstructionFailureKind.AUTHORIZATION_MISMATCH,
    )


def test_wrong_start_and_missing_result_commit_block(tmp_path):
    _, _, service, request = repository_fixture(tmp_path)
    wrong_start = replace(
        request.authorization,
        expected_start_commit="a" * 40,
    )
    failure(
        service,
        replace(request, authorization=wrong_start),
        ReconstructionFailureKind.BASE_COMMIT_MISMATCH,
    )
    missing_result = replace(
        request.authorization,
        expected_result_commit="b" * 40,
    )
    failure(
        service,
        replace(request, authorization=missing_result),
        ReconstructionFailureKind.RESULT_COMMIT_MISSING,
    )


def test_git_parent_conflict_blocks(tmp_path):
    repository, _, service, request = repository_fixture(tmp_path)
    git(repository, "commit", "--allow-empty", "-q", "-m", "Other")
    other = git(repository, "rev-parse", "HEAD")
    authorization = replace(
        request.authorization,
        expected_result_commit=other,
    )
    failure(
        service,
        replace(request, authorization=authorization),
        ReconstructionFailureKind.GIT_HISTORY_CONFLICT,
    )


def test_missing_unsafe_and_outside_handover_block(tmp_path):
    repository, _, service, request = repository_fixture(tmp_path)
    missing = replace(
        request.authorization,
        expected_handover_paths=(
            "knowledge/handovers/missing.json",
            request.authorization.expected_handover_paths[1],
        ),
    )
    failure(
        service,
        replace(request, authorization=missing),
        ReconstructionFailureKind.HANDOVER_MISSING,
    )
    target = repository / request.authorization.expected_handover_paths[0]
    target.unlink()
    target.symlink_to(repository / "base.txt")
    failure(service, request, ReconstructionFailureKind.HANDOVER_MISSING)

    repository, _, service, request = repository_fixture(tmp_path / "outside")
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    authorization = replace(
        request.authorization,
        expected_handover_paths=(
            str(outside),
            request.authorization.expected_handover_paths[1],
        ),
    )
    failure(
        service,
        replace(request, authorization=authorization),
        ReconstructionFailureKind.HANDOVER_MISSING,
    )


def test_invalid_json_and_handover_commit_conflicts_block(tmp_path):
    repository, _, service, request = repository_fixture(tmp_path)
    path = repository / request.authorization.expected_handover_paths[0]
    path.write_text("{", encoding="utf-8")
    failure(service, request, ReconstructionFailureKind.HANDOVER_INVALID)

    repository, _, service, request = repository_fixture(tmp_path / "second")
    rewrite_handover(
        repository,
        request.authorization,
        lambda payload: payload.update({"starting_commit": "c" * 40}),
    )
    failure(
        service,
        request,
        ReconstructionFailureKind.BASE_COMMIT_MISMATCH,
    )


@pytest.mark.parametrize(
    "mutation,expected",
    (
        (
            lambda payload: payload.update({"checks": []}),
            ReconstructionFailureKind.CHECKS_MISSING,
        ),
        (
            lambda payload: payload["checks"][0].update({"status": "failed"}),
            ReconstructionFailureKind.CHECK_FAILED,
        ),
        (
            lambda payload: payload["checks"][1].update({"status": "failed"}),
            ReconstructionFailureKind.CHECK_FAILED,
        ),
        (
            lambda payload: payload["checks"][2].update({"status": "failed"}),
            ReconstructionFailureKind.CHECK_FAILED,
        ),
        (
            lambda payload: payload["checks"].__setitem__(
                slice(None),
                [
                    item for item in payload["checks"]
                    if "doctor" not in item["command"]
                ],
            ),
            ReconstructionFailureKind.CHECKS_MISSING,
        ),
        (
            lambda payload: payload["checks"].__setitem__(
                slice(None),
                [
                    item for item in payload["checks"]
                    if "diff --check" not in item["command"]
                ],
            ),
            ReconstructionFailureKind.CHECKS_MISSING,
        ),
    ),
)
def test_missing_or_failed_checks_block(tmp_path, mutation, expected):
    repository, _, service, request = repository_fixture(tmp_path)
    rewrite_handover(repository, request.authorization, mutation)
    failure(service, request, expected)


def test_reconstruction_is_idempotent_and_review_is_unique(tmp_path):
    _, workflows, service, request = repository_fixture(tmp_path)
    first = service.reconstruct(request)
    review_path = (
        workflows.folder(first.workflow_id)
        / "executions"
        / "feedback"
        / "integrator-review.json"
    )
    before = review_path.read_bytes()

    second = service.reconstruct(request)

    assert second == first
    assert review_path.read_bytes() == before
    assert len(second.feedback.transitions) == len(first.feedback.transitions)


def test_different_reconstruction_timestamp_conflicts(tmp_path):
    _, _, service, request = repository_fixture(tmp_path)
    service.reconstruct(request)
    changed = replace(
        request,
        reconstructed_at=datetime(2026, 7, 27, 18, 0, tzinfo=timezone.utc),
    )
    failure(
        service,
        changed,
        ReconstructionFailureKind.EXECUTION_CONFLICT,
    )


def test_legacy_execution_record_defaults_to_bridge_origin(tmp_path):
    repository, workflows, service, request = repository_fixture(tmp_path)
    reconstructed = service.reconstruct(request).execution
    store = ExecutionStore(workflows)
    path = store.path(reconstructed.workflow_id, reconstructed.execution_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["execution_id"] = "execution-0123456789abcdef"
    payload.pop("origin")
    payload["prompt_hash"] = "a" * 64
    payload["starting_branch"] = "main"
    payload["starting_git_status"] = []
    payload["started_at"] = NOW.isoformat()
    payload["completed_at"] = NOW.isoformat()
    payload["codex_exit_code"] = 0
    payload.pop("reconstructed_at")
    payload.pop("authorization_reference")
    payload.pop("reconstruction_source")
    path = store.path(reconstructed.workflow_id, payload["execution_id"])
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = store.load(reconstructed.workflow_id, payload["execution_id"])

    assert loaded.origin is ExecutionOrigin.EXECUTION_BRIDGE


def test_cli_returns_machine_readable_reconstruction(tmp_path, monkeypatch):
    repository, _, service, request = repository_fixture(tmp_path)
    authorization_path = tmp_path / "authorization.json"
    authorization_path.write_text(
        json.dumps(request.authorization.to_dict()),
        encoding="utf-8",
    )
    monkeypatch.chdir(repository)
    monkeypatch.setattr(
        architecture_commands,
        "ExecutionReconstructionService",
        lambda **kwargs: service,
    )
    monkeypatch.setattr(
        architecture_commands,
        "ArchitectureContextLoader",
        lambda runtime: object(),
    )
    monkeypatch.setattr(
        architecture_commands,
        "ArchitectureIntegrator",
        lambda loader: service.integrator,
    )
    monkeypatch.setattr(
        architecture_commands,
        "get_runtime",
        lambda: object(),
    )
    result = CliRunner().invoke(
        architecture_commands.execution_app,
        [
            "reconstruct",
            "--authorization",
            str(authorization_path),
            "--reconstructed-at",
            NOW.isoformat(),
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["execution"]["origin"] == "RECONSTRUCTED"
    assert payload["feedback"]["status"] == (
        "CHIEF_ARCHITECT_DECISION_REQUIRED"
    )
