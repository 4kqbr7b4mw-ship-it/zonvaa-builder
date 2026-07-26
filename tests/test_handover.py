import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

import builder.main as main_module
from builder.main import app
from builder.handover import (
    CheckResult,
    HandoverRecord,
    HandoverWriter,
    load_handover_input,
)


NOW = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
runner = CliRunner()


def record():
    return HandoverRecord(
        timestamp=NOW,
        task="Codex context foundation",
        starting_commit="abc1234",
        ending_commit=None,
        changed_files=("builder/preflight.py",),
        functional_changes=("Added mandatory local preflight.",),
        technical_changes=("Extended the existing RuntimeManager.",),
        decisions=("No second knowledge store.",),
        relevant_adrs=("ADR-0020",),
        checks=(
            CheckResult(
                "python3 -m pytest -q",
                "passed",
                "10 passed",
            ),
        ),
        open_risks=("Ending commit is unavailable before commit.",),
        intentionally_not_implemented=("No network handover.",),
        recommended_next_step="Integrate mission context into later workflows.",
        git_status=("M builder/runtime.py",),
        push_status="not_pushed",
    )


def input_payload():
    data = record().to_dict()
    del data["schema_version"]
    return data


def test_handover_writes_machine_and_human_readable_views(tmp_path):
    json_path, markdown_path = HandoverWriter(tmp_path).write(record())

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["schema_version"] == "1.0"
    assert payload["task"] == "Codex context foundation"
    assert payload["ending_commit"] is None
    assert payload["checks"][0]["result"] == "10 passed"
    assert "# Handover: Codex context foundation" in markdown
    assert "10 passed" in markdown
    assert "missing" in markdown


def test_handover_does_not_overwrite_existing_file(tmp_path):
    writer = HandoverWriter(tmp_path)
    writer.write(record())

    with pytest.raises(FileExistsError):
        writer.write(record())


def test_handover_models_are_immutable():
    with pytest.raises(Exception) as error:
        record().task = "Changed"
    assert type(error.value).__name__ == "FrozenInstanceError"


def test_handover_timestamp_must_be_timezone_aware():
    values = record().__dict__.copy()
    values["timestamp"] = datetime(2026, 7, 26, 12, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        HandoverRecord(**values)


def test_handover_commit_ids_are_validated():
    values = record().__dict__.copy()
    values["starting_commit"] = "main"
    with pytest.raises(ValueError, match="Git commit id"):
        HandoverRecord(**values)


def test_handover_input_requires_complete_stable_schema(tmp_path):
    payload = input_payload()
    del payload["open_risks"]
    input_file = tmp_path / "handover.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="missing"):
        load_handover_input(input_file)


def test_handover_input_rejects_invalid_check_instead_of_dropping_it(
    tmp_path,
):
    payload = input_payload()
    payload["checks"] = [{"command": "pytest", "status": "passed"}]
    input_file = tmp_path / "handover.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Each check"):
        load_handover_input(input_file)


def test_handover_cli_uses_local_end_to_end_path(monkeypatch):
    monkeypatch.setattr(main_module, "get_runtime", lambda: object())
    with runner.isolated_filesystem():
        input_file = Path("handover-input.json")
        input_file.write_text(
            json.dumps(input_payload()),
            encoding="utf-8",
        )

        result = runner.invoke(
            app,
            ["handover", "--input", str(input_file)],
        )

        assert result.exit_code == 0, result.output
        json_files = list(Path("knowledge/handovers").glob("*.json"))
        markdown_files = list(Path("knowledge/handovers").glob("*.md"))
        assert len(json_files) == 1
        assert len(markdown_files) == 1
        assert json.loads(
            json_files[0].read_text(encoding="utf-8")
        )["push_status"] == "not_pushed"


def test_handover_schema_has_no_document_content_field():
    payload = record().to_dict()
    assert "content" not in payload
    assert "documents" not in payload


@pytest.mark.parametrize("status", ["passed", "failed", "not_run"])
def test_check_statuses_are_explicit(status):
    check = CheckResult("command", status, "result")
    assert check.status == status
