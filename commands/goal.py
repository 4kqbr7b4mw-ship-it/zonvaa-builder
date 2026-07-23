import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from builder.goal_application_service import GoalApplicationService
from builder.runtime import get_runtime
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)


class GoalInputError(ValueError):
    """Expected validation error in a goal run input document."""


def _mapping(value: Any, field: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise GoalInputError("'{}' muss ein JSON-Objekt sein.".format(field))
    return value


def _required(mapping: Dict[str, Any], field: str) -> Any:
    if field not in mapping:
        raise GoalInputError("Pflichtfeld '{}' fehlt.".format(field))
    return mapping[field]


def _string(mapping: Dict[str, Any], field: str) -> str:
    value = _required(mapping, field)
    if not isinstance(value, str):
        raise GoalInputError("'{}' muss ein String sein.".format(field))
    return value


def _string_list(mapping: Dict[str, Any], field: str) -> List[str]:
    value = _required(mapping, field)
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise GoalInputError("'{}' muss eine Liste von Strings sein.".format(field))
    return value


def _load_input(input_file: Path) -> Dict[str, Any]:
    try:
        content = input_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise GoalInputError(
            "Eingabedatei kann nicht gelesen werden: {}".format(exc)
        ) from exc

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GoalInputError(
            "Eingabedatei enthält ungültiges JSON: Zeile {}, Spalte {}.".format(
                exc.lineno,
                exc.colno,
            )
        ) from exc

    return _mapping(payload, "input")


def _create_goal(payload: Dict[str, Any]) -> Goal:
    goal_data = _mapping(_required(payload, "goal"), "goal")
    created_at_text = _string(goal_data, "created_at")
    try:
        created_at = datetime.fromisoformat(created_at_text)
    except ValueError as exc:
        raise GoalInputError(
            "'goal.created_at' muss ein gültiger ISO-8601-Zeitpunkt sein."
        ) from exc

    return Goal(
        id=_string(goal_data, "id"),
        title=_string(goal_data, "title"),
        description=_string(goal_data, "description"),
        project=_string(goal_data, "project"),
        priority=_string(goal_data, "priority"),
        status=_string(goal_data, "status"),
        owner=_string(goal_data, "owner"),
        created_at=created_at,
    )


def _create_assessment(
    payload: Dict[str, Any],
    goal: Goal,
    identity_version: str,
) -> Optional[WhyAssessment]:
    assessment_value = payload.get("why_assessment")
    if assessment_value is None:
        return None

    assessment_data = _mapping(assessment_value, "why_assessment")
    evidence = assessment_data.get("evidence", [])
    if not isinstance(evidence, list) or not all(
        isinstance(item, str) for item in evidence
    ):
        raise GoalInputError(
            "'why_assessment.evidence' muss eine Liste von Strings sein."
        )

    return WhyAssessment(
        goal=goal,
        identity_version=identity_version,
        status=WhyAssessmentStatus(_string(assessment_data, "status")),
        reason=WhyAssessmentReason(_string(assessment_data, "reason")),
        evidence=tuple(evidence),
    )


def run_goal(
    input_file: Path = typer.Option(
        ...,
        "--input",
        help="UTF-8-JSON-Datei mit Goal und Laufkontext.",
    ),
) -> None:
    """Führt ein vorhandenes Goal über den Goal Application Service aus."""
    try:
        payload = _load_input(input_file)
        goal = _create_goal(payload)
        role = _string(payload, "role")
        memory_types = _string_list(payload, "memory_types")
        constitution_rules = _string_list(payload, "constitution_rules")
    except (GoalInputError, TypeError, ValueError) as exc:
        raise typer.BadParameter(str(exc), param_hint="--input") from None

    try:
        runtime = get_runtime()
    except (OSError, UnicodeError, RuntimeError) as exc:
        raise typer.BadParameter(
            "Runtime konnte nicht gestartet werden: {}".format(exc),
            param_hint="--input",
        ) from None

    try:
        assessment = _create_assessment(
            payload,
            goal,
            runtime.identity_context.version,
        )
        result = GoalApplicationService(runtime).run(
            goal=goal,
            role=role,
            memory_types=memory_types,
            constitution_rules=constitution_rules,
            why_assessment=assessment,
        )
    except (GoalInputError, TypeError, ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc), param_hint="--input") from None

    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
