import json
import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from typer.testing import CliRunner

import commands.architecture as architecture_commands
from builder.main import app
from codex_execution import (
    ArchitectureExecutionPreparationService,
    PreparationBaselineError,
)
from tests.test_codex_execution_orchestration import (
    BASE,
    WORKFLOW,
    workflow_fixture,
)


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git",) + arguments,
        cwd=str(repository),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def prepared_repository(tmp_path: Path):
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.email", "tests@example.invalid")
    git(tmp_path, "config", "user.name", "Tests")
    (tmp_path / "README.md").write_text("baseline\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-m", "baseline")
    actual_head = git(tmp_path, "rev-parse", "HEAD").strip()
    workflows = workflow_fixture(tmp_path)
    folder = workflows.folder(WORKFLOW)
    for relative, content in (
        ("proposals/proposal-a.json", "{}\n"),
        ("analyses/proposal-a.json", "{}\n"),
        ("decision_proposals/decision-proposal.md", "# Decision\n"),
    ):
        path = folder / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    authorization_path = folder / "feedback" / "execution-authorization.json"
    data = json.loads(authorization_path.read_text(encoding="utf-8"))
    data["expected_base_commit"] = actual_head
    data["authorization_id"] = "authorization-1111111111111111"
    authorization_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return (
        ArchitectureExecutionPreparationService(workflows, tmp_path),
        workflows,
        actual_head,
    )


def test_official_workflow_preparation_is_typed_hashed_and_idempotent(tmp_path):
    service, _, head = prepared_repository(tmp_path)

    first = service.prepare(WORKFLOW)
    second = service.prepare(WORKFLOW)

    assert first == second
    assert first.base_commit == head
    assert first.branch == "main"
    assert first.authorization_id == "authorization-1111111111111111"
    assert first.files
    assert first.staged_paths == ()
    assert first.untracked_paths == tuple(item.path for item in first.files)
    assert first.content_hashes == tuple(item.sha256 for item in first.files)
    assert all(item.size >= 2 for item in first.files)
    assert service.store.path(WORKFLOW).is_file()
    with pytest.raises(FrozenInstanceError):
        first.branch = "other"


def test_preparation_baseline_rejects_unknown_existing_and_staged_changes(tmp_path):
    service, _, _ = prepared_repository(tmp_path)
    (tmp_path / "unknown.txt").write_text("unknown\n", encoding="utf-8")
    with pytest.raises(PreparationBaselineError) as unknown:
        service.prepare(WORKFLOW)
    assert unknown.value.code == "UNAUTHORIZED_WORKING_TREE_CHANGES"

    (tmp_path / "unknown.txt").unlink()
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    with pytest.raises(PreparationBaselineError) as existing:
        service.prepare(WORKFLOW)
    assert existing.value.code == "UNAUTHORIZED_WORKING_TREE_CHANGES"

    (tmp_path / "README.md").write_text("baseline\n", encoding="utf-8")
    git(tmp_path, "add", "knowledge")
    with pytest.raises(PreparationBaselineError) as staged:
        service.prepare(WORKFLOW)
    assert staged.value.code == "PREPARATION_STAGED_CHANGES_NOT_ALLOWED"


@pytest.mark.parametrize("mutation", ["modify", "delete", "additional"])
def test_assessment_rejects_baseline_drift(tmp_path, mutation):
    service, _, head = prepared_repository(tmp_path)
    baseline = service.prepare(WORKFLOW)
    target = tmp_path / baseline.files[0].path
    if mutation == "modify":
        target.write_text("changed\n", encoding="utf-8")
    elif mutation == "delete":
        target.unlink()
    else:
        (tmp_path / "unexpected.txt").write_text("new\n", encoding="utf-8")
    authorization = service.feedback.authorization(WORKFLOW)
    entries = tuple(
        git(
            tmp_path,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).splitlines()
    )

    result = service.assess(
        baseline, authorization, "main", head, entries, False
    )

    assert not result.baseline_valid
    assert result.error_code == "PREPARATION_BASELINE_MISMATCH"


def test_assessment_separates_unchanged_preparation_from_codex_result(tmp_path):
    service, _, head = prepared_repository(tmp_path)
    baseline = service.prepare(WORKFLOW)
    result_path = tmp_path / "builder" / "result.py"
    result_path.parent.mkdir()
    result_path.write_text("VALUE = 1\n", encoding="utf-8")
    authorization = service.feedback.authorization(WORKFLOW)
    entries = tuple(
        git(
            tmp_path,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).splitlines()
    )

    result = service.assess(
        baseline, authorization, "main", head, entries, True
    )

    assert result.baseline_valid
    assert result.hash_match
    assert result.preparation_files == tuple(
        item.path for item in baseline.files
    )
    assert result.codex_result_changes == ("builder/result.py",)


def test_prepare_cli_and_read_only_status_use_the_same_baseline(
    tmp_path, monkeypatch
):
    service, _, _ = prepared_repository(tmp_path)
    monkeypatch.setattr(
        architecture_commands, "_preparation_service", lambda: service
    )
    runner = CliRunner()

    prepared = runner.invoke(
        app,
        ["architecture", "execution", "prepare", "--workflow-id", WORKFLOW],
    )
    before = service.store.path(WORKFLOW).read_bytes()
    status = runner.invoke(
        app,
        [
            "architecture",
            "execution",
            "preparation-status",
            "--workflow-id",
            WORKFLOW,
        ],
    )

    assert prepared.exit_code == 0
    assert status.exit_code == 0
    assert json.loads(prepared.stdout)["baseline_id"] == json.loads(
        status.stdout
    )["baseline_id"]
    assert service.store.path(WORKFLOW).read_bytes() == before
