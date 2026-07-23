import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

import commands.goal as goal_command
from brain.context_collector import ContextCollector
from builder.journal import DecisionJournal
from builder.main import app
from builder.runtime import RuntimeManager
from goal.engine import GoalEngine
from identity.models import IdentityContext


runner = CliRunner()


def input_data(assessment=None):
    return {
        "goal": {
            "id": "goal-cli",
            "title": "Run a goal from the CLI",
            "description": "Use existing application components.",
            "project": "zonvaa-builder",
            "priority": "high",
            "status": "active",
            "owner": "builder",
            "created_at": "2026-07-23T10:00:00+02:00",
        },
        "role": "builder",
        "memory_types": ["project_memory"],
        "constitution_rules": ["Follow the WHY"],
        "why_assessment": assessment,
    }


def create_runtime():
    runtime = RuntimeManager()
    runtime.identity_context = IdentityContext(
        content="# WHY",
        source=Path("WHY.md"),
        version="identity-version",
    )
    runtime.constitution = "Full constitution"
    runtime.verified_facts = {"tests": "passing"}
    runtime.project_state = {
        "git_clean": True,
        "verified_facts": runtime.verified_facts,
    }
    runtime.goal_engine = GoalEngine()
    return runtime


@pytest.fixture
def clean_cli(monkeypatch):
    runtime = create_runtime()
    monkeypatch.setattr(goal_command, "get_runtime", lambda: runtime)

    def clean_git(self, command):
        if command[:2] == ["git", "status"]:
            return "Keine Ausgabe."
        if command[:2] == ["git", "log"]:
            return "32922f3 Add goal application service"
        raise AssertionError("Unexpected command: {}".format(command))

    monkeypatch.setattr(ContextCollector, "_run_command", clean_git)
    return runtime


def invoke_json(tmp_path, payload):
    input_file = tmp_path / "goal.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")
    return runner.invoke(app, ["goal", "run", "--input", str(input_file)])


def invoke_recorded_json(tmp_path, payload):
    input_file = tmp_path / "goal.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")
    return runner.invoke(
        app,
        ["goal", "run", "--input", str(input_file), "--record"],
    )


def output_json(result):
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_help_contains_goal_command():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "goal" in result.stdout


def test_missing_input_file_is_rejected():
    result = runner.invoke(
        app,
        ["goal", "run", "--input", "/missing/goal.json"],
    )

    assert result.exit_code != 0
    assert "Eingabedatei kann nicht gelesen werden" in result.output
    assert "Traceback" not in result.output


def test_invalid_json_is_rejected(tmp_path):
    input_file = tmp_path / "goal.json"
    input_file.write_text("{invalid", encoding="utf-8")

    result = runner.invoke(app, ["goal", "run", "--input", str(input_file)])

    assert result.exit_code != 0
    assert "ungültiges JSON" in result.output
    assert "Traceback" not in result.output


def test_missing_goal_field_is_rejected(tmp_path):
    payload = input_data()
    del payload["goal"]["owner"]

    result = invoke_json(tmp_path, payload)

    assert result.exit_code != 0
    assert "Pflichtfeld 'owner' fehlt" in result.output


@pytest.mark.parametrize(
    "field, value, expected",
    [
        ("role", 42, "'role' muss ein String sein"),
        ("memory_types", "project_memory", "Liste von Strings"),
        ("constitution_rules", [42], "Liste von Strings"),
    ],
)
def test_invalid_invocation_field_types_are_rejected(
    tmp_path,
    field,
    value,
    expected,
):
    payload = input_data()
    payload[field] = value

    result = invoke_json(tmp_path, payload)

    assert result.exit_code != 0
    assert expected in result.output
    assert "Traceback" not in result.output


def test_without_assessment_needs_review_without_plan(clean_cli, tmp_path):
    result = output_json(invoke_json(tmp_path, input_data()))

    assert result["decision"]["status"] == "needs_review"
    assert result["decision"]["why_status"] is None
    assert result["plan"] == []
    assert result["execution"] == []


def test_aligned_assessment_returns_plan_and_pending_execution(clean_cli, tmp_path):
    payload = input_data(
        {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": [],
        }
    )

    result = output_json(invoke_json(tmp_path, payload))

    assert result["decision"]["status"] == "approved"
    assert result["decision"]["why_status"] == "aligned"
    assert result["decision"]["why_reason"] == "explicit_alignment_confirmed"
    assert result["plan"]
    assert all(step["execution_status"] == "pending" for step in result["execution"])


def test_conflicting_assessment_blocks_without_plan(clean_cli, tmp_path):
    payload = input_data(
        {
            "status": "conflicting",
            "reason": "explicit_conflict_confirmed",
            "evidence": [],
        }
    )

    result = output_json(invoke_json(tmp_path, payload))

    assert result["decision"]["status"] == "blocked"
    assert result["decision"]["why_status"] == "conflicting"
    assert result["plan"] == []
    assert result["execution"] == []


def test_not_evaluable_assessment_needs_review(clean_cli, tmp_path):
    payload = input_data(
        {
            "status": "not_evaluable",
            "reason": "insufficient_assessment_basis",
            "evidence": [],
        }
    )

    result = output_json(invoke_json(tmp_path, payload))

    assert result["decision"]["status"] == "needs_review"
    assert result["decision"]["why_status"] == "not_evaluable"
    assert result["plan"] == []
    assert result["execution"] == []


@pytest.mark.parametrize(
    "assessment, expected",
    [
        (
            {"status": "unknown", "reason": "explicit_alignment_confirmed"},
            "unknown",
        ),
        (
            {"status": "aligned", "reason": "unknown_reason"},
            "unknown_reason",
        ),
        (
            {
                "status": "aligned",
                "reason": "explicit_conflict_confirmed",
            },
            "status/reason combination",
        ),
    ],
)
def test_invalid_assessment_is_rejected(clean_cli, tmp_path, assessment, expected):
    result = invoke_json(tmp_path, input_data(assessment))

    assert result.exit_code != 0
    assert expected in result.output
    assert "Traceback" not in result.output


def test_evidence_is_forwarded_but_does_not_change_result(clean_cli, tmp_path):
    first_payload = input_data(
        {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": [],
        }
    )
    second_payload = input_data(
        {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": ["Explicit review evidence"],
        }
    )

    first = output_json(invoke_json(tmp_path, first_payload))
    second = output_json(invoke_json(tmp_path, second_payload))

    assert first == second


def test_evidence_elements_are_preserved_in_assessment(clean_cli, tmp_path, monkeypatch):
    service = Mock()
    service.run.return_value = {
        "decision": {"status": "approved"},
        "plan": [],
        "execution": [],
    }
    monkeypatch.setattr(
        goal_command,
        "GoalApplicationService",
        Mock(return_value=service),
    )
    evidence = ["First explicit statement", "Second explicit statement"]
    payload = input_data(
        {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": evidence,
        }
    )

    result = invoke_json(tmp_path, payload)

    assert result.exit_code == 0
    assessment = service.run.call_args.kwargs["why_assessment"]
    assert assessment.evidence == tuple(evidence)


def test_goal_application_service_is_used(clean_cli, tmp_path, monkeypatch):
    service = Mock()
    service.run.return_value = {
        "decision": {"status": "needs_review"},
        "plan": [],
        "execution": [],
    }
    service_class = Mock(return_value=service)
    monkeypatch.setattr(goal_command, "GoalApplicationService", service_class)

    result = invoke_json(tmp_path, input_data())

    assert result.exit_code == 0
    service_class.assert_called_once_with(clean_cli)
    service.run.assert_called_once()


def test_cli_does_not_load_second_identity(clean_cli, tmp_path, monkeypatch):
    import identity.loader

    monkeypatch.setattr(
        identity.loader.IdentityLoader,
        "load",
        lambda self: pytest.fail("identity must not be loaded again"),
    )

    result = invoke_json(tmp_path, input_data())

    assert result.exit_code == 0


def test_runtime_boot_error_is_reported_without_traceback(tmp_path, monkeypatch):
    def fail_runtime():
        raise FileNotFoundError("WHY.md fehlt")

    monkeypatch.setattr(goal_command, "get_runtime", fail_runtime)

    result = invoke_json(tmp_path, input_data())

    assert result.exit_code != 0
    assert "Runtime konnte nicht gestartet werden" in result.output
    assert "Traceback" not in result.output


def test_without_record_keeps_output_and_writes_no_file(
    clean_cli,
    tmp_path,
    monkeypatch,
):
    record_folder = tmp_path / "records"
    monkeypatch.setattr(DecisionJournal, "DEFAULT_FOLDER", record_folder)

    result = output_json(invoke_json(tmp_path, input_data()))

    assert set(result) == {"decision", "plan", "execution"}
    assert not record_folder.exists()


def test_recorded_approved_flow_contains_complete_record(
    clean_cli,
    tmp_path,
    monkeypatch,
):
    record_folder = tmp_path / "records"
    monkeypatch.setattr(DecisionJournal, "DEFAULT_FOLDER", record_folder)
    evidence = ["Explicit first statement", "Explicit second statement"]
    payload = input_data(
        {
            "status": "aligned",
            "reason": "explicit_alignment_confirmed",
            "evidence": evidence,
        }
    )

    output = output_json(invoke_recorded_json(tmp_path, payload))
    files = list(record_folder.glob("*.json"))

    assert len(files) == 1
    assert output["record_path"] == str(files[0])
    record = json.loads(files[0].read_text(encoding="utf-8"))
    assert record["record_version"] == "1.0"
    assert record["created_at"].endswith("+00:00")
    assert record["goal"] == payload["goal"]
    assert record["invocation"] == {
        "role": payload["role"],
        "memory_types": payload["memory_types"],
        "constitution_rules": payload["constitution_rules"],
    }
    assert record["identity"] == {
        "source": "WHY.md",
        "version": clean_cli.identity_context.version,
    }
    assert "content" not in record["identity"]
    assert "# WHY" not in files[0].read_text(encoding="utf-8")
    assert record["why_assessment"] == payload["why_assessment"]
    assert record["decision"] == output["decision"]
    assert record["plan"] == output["plan"]
    assert record["execution"] == output["execution"]
    assert record["source"]["input_file"] == str(
        (tmp_path / "goal.json").resolve()
    )


@pytest.mark.parametrize(
    "assessment, expected_status",
    [
        (None, "needs_review"),
        (
            {
                "status": "conflicting",
                "reason": "explicit_conflict_confirmed",
                "evidence": [],
            },
            "blocked",
        ),
        (
            {
                "status": "not_evaluable",
                "reason": "insufficient_assessment_basis",
                "evidence": [],
            },
            "needs_review",
        ),
    ],
)
def test_recorded_non_approved_flows(
    clean_cli,
    tmp_path,
    monkeypatch,
    assessment,
    expected_status,
):
    record_folder = tmp_path / "records"
    monkeypatch.setattr(DecisionJournal, "DEFAULT_FOLDER", record_folder)

    output = output_json(
        invoke_recorded_json(tmp_path, input_data(assessment))
    )
    record_file = next(record_folder.glob("*.json"))
    record = json.loads(record_file.read_text(encoding="utf-8"))

    assert output["decision"]["status"] == expected_status
    assert record["decision"]["status"] == expected_status
    assert record["why_assessment"] == assessment
    assert record["plan"] == []
    assert record["execution"] == []


def test_two_recorded_runs_do_not_overwrite_each_other(
    clean_cli,
    tmp_path,
    monkeypatch,
):
    record_folder = tmp_path / "records"
    monkeypatch.setattr(DecisionJournal, "DEFAULT_FOLDER", record_folder)

    first = output_json(invoke_recorded_json(tmp_path, input_data()))
    second = output_json(invoke_recorded_json(tmp_path, input_data()))

    assert first["record_path"] != second["record_path"]
    assert len(list(record_folder.glob("*.json"))) == 2


def test_existing_journal_file_remains_unchanged(
    clean_cli,
    tmp_path,
    monkeypatch,
):
    record_folder = tmp_path / "records"
    record_folder.mkdir()
    existing = record_folder / "existing.json"
    existing.write_text('{"existing": true}\n', encoding="utf-8")
    monkeypatch.setattr(DecisionJournal, "DEFAULT_FOLDER", record_folder)

    result = invoke_recorded_json(tmp_path, input_data())

    assert result.exit_code == 0
    assert existing.read_text(encoding="utf-8") == '{"existing": true}\n'
    assert len(list(record_folder.glob("*.json"))) == 2


def test_record_write_error_is_reported(clean_cli, tmp_path, monkeypatch):
    def fail_record(self, **kwargs):
        raise PermissionError("read-only journal")

    monkeypatch.setattr(DecisionJournal, "record", fail_record)

    result = invoke_recorded_json(tmp_path, input_data())

    assert result.exit_code != 0
    assert "Decision Record konnte nicht gespeichert werden" in result.output
    assert "Traceback" not in result.output


def test_failed_goal_flow_creates_no_record(clean_cli, tmp_path, monkeypatch):
    journal = Mock()
    monkeypatch.setattr(
        goal_command,
        "DecisionJournal",
        Mock(return_value=journal),
    )
    service = Mock()
    service.run.side_effect = ValueError("invalid assessment binding")
    monkeypatch.setattr(
        goal_command,
        "GoalApplicationService",
        Mock(return_value=service),
    )

    result = invoke_recorded_json(tmp_path, input_data())

    assert result.exit_code != 0
    journal.record.assert_not_called()
