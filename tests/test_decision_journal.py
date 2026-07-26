import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import builder.journal as journal_module
from builder.journal import DecisionJournal
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)
from identity.models import IdentityContext
from knowledge.memory import MemoryType


def create_record_data():
    goal = Goal(
        id="goal-journal",
        title="Record a decision",
        description="Persist an explicit completed result.",
        project="zonvaa-builder",
        priority="high",
        status="active",
        owner="builder",
        created_at=datetime(2026, 7, 23, 10, 0, tzinfo=timezone.utc),
    )
    identity = IdentityContext(
        content="SECRET WHY CONTENT",
        source=Path("WHY.md"),
        version="identity-version",
    )
    assessment = WhyAssessment(
        goal=goal,
        identity_version=identity.version,
        status=WhyAssessmentStatus.ALIGNED,
        reason=WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
        evidence=("Explicit evidence",),
    )
    result = {
        "decision": {"status": "approved", "why_status": "aligned"},
        "plan": [{"step": 1}],
        "execution": [{"step": 1, "execution_status": "pending"}],
    }
    return goal, identity, assessment, result


def test_decision_journal_writes_exclusive_versioned_json(tmp_path):
    goal, identity, assessment, result = create_record_data()

    path = DecisionJournal(tmp_path).record(
        goal=goal,
        role="builder",
        memory_types=[MemoryType.PROJECT],
        constitution_rules=["Follow the WHY"],
        identity_context=identity,
        why_assessment=assessment,
        result=result,
        input_file=tmp_path / "input.json",
    )

    record = json.loads(path.read_text(encoding="utf-8"))
    assert path.parent == tmp_path
    assert record["record_version"] == "2.0"
    assert record["apply"] == {
        "requested": False,
        "status": "not_requested",
    }
    assert record["execution"] == {
        "status": "not_requested",
        "steps": result["execution"],
        "error": None,
        "rollback": {
            "rolled_back_steps": [],
            "errors": [],
        },
        "remaining_resources": [],
    }
    assert record["goal"]["id"] == goal.id
    assert record["identity"] == {
        "source": "WHY.md",
        "version": "identity-version",
    }
    assert "SECRET WHY CONTENT" not in path.read_text(encoding="utf-8")


def test_decision_journal_never_overwrites_existing_filename(
    tmp_path,
    monkeypatch,
):
    goal, identity, assessment, result = create_record_data()
    fixed_time = datetime(2026, 7, 23, 10, 0, tzinfo=timezone.utc)

    class FixedDateTime:
        @classmethod
        def now(cls, tz):
            return fixed_time

    monkeypatch.setattr(journal_module, "datetime", FixedDateTime)
    journal = DecisionJournal(tmp_path)
    journal.record(
        goal,
        "builder",
        ["project_memory"],
        [],
        identity,
        assessment,
        result,
        tmp_path / "input.json",
    )

    with pytest.raises(FileExistsError):
        journal.record(
            goal,
            "builder",
            ["project_memory"],
            [],
            identity,
            assessment,
            result,
            tmp_path / "input.json",
        )

    assert len(list(tmp_path.glob("*.json"))) == 1
