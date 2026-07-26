import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from builder.goal_application_service import GoalApplicationService
from builder.journal import DecisionJournal
from builder.orchestrator import GoalApplyError
from builder.runtime import get_runtime
from execution.models import DocumentArtifact
from goal.models import Goal
from goal.why_assessment import (
    WhyAssessment,
    WhyAssessmentReason,
    WhyAssessmentStatus,
)


class GoalInputError(ValueError):
    """Expected validation error in a goal run input document."""


def _apply_status(apply: bool, result: Dict[str, Any]) -> str:
    if not apply:
        return "not_requested"
    if result["decision"]["status"] != "approved":
        return "not_executed"
    if not any(
        step.get("agent") == "document"
        and step.get("execution_status") == "completed"
        for step in result["execution"]
    ):
        return "not_executed"
    return "completed"


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


def _create_artifacts(
    payload: Dict[str, Any],
) -> Optional[List[DocumentArtifact]]:
    artifact_values = payload.get("artifacts")
    if artifact_values is None:
        return None
    if not isinstance(artifact_values, list):
        raise GoalInputError("'artifacts' muss eine Liste sein.")

    artifacts = []
    for index, artifact_value in enumerate(artifact_values):
        field = "artifacts[{}]".format(index)
        artifact_data = _mapping(artifact_value, field)
        artifacts.append(
            DocumentArtifact(
                action=_string(artifact_data, "action"),
                path=_string(artifact_data, "path"),
                content=_string(artifact_data, "content"),
            )
        )
    return artifacts


def run_goal(
    input_file: Path = typer.Option(
        ...,
        "--input",
        help="UTF-8-JSON-Datei mit Goal und Laufkontext.",
    ),
    record: bool = typer.Option(
        False,
        "--record",
        help="Speichert einen unveränderlichen Decision Record.",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Erzeugt freigegebene neue Dokumente unter knowledge/.",
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
        artifacts = _create_artifacts(payload)
    except (GoalInputError, TypeError, ValueError) as exc:
        raise typer.BadParameter(str(exc), param_hint="--input") from None

    try:
        result = GoalApplicationService(runtime).run(
            goal=goal,
            role=role,
            memory_types=memory_types,
            constitution_rules=constitution_rules,
            why_assessment=assessment,
            document_artifacts=artifacts,
            apply=apply,
        )
    except GoalApplyError as exc:
        if record:
            try:
                record_path = DecisionJournal().record(
                    goal=goal,
                    role=role,
                    memory_types=memory_types,
                    constitution_rules=constitution_rules,
                    identity_context=runtime.identity_context,
                    why_assessment=assessment,
                    result=exc.result,
                    input_file=input_file,
                    apply_status="failed",
                )
            except OSError as record_exc:
                raise typer.BadParameter(
                    "Apply fehlgeschlagen; Decision Record konnte nicht "
                    "gespeichert werden: {}".format(record_exc),
                    param_hint="--record",
                ) from None
            raise typer.BadParameter(
                "{}; Decision Record: {}".format(exc, record_path),
                param_hint="--apply",
            ) from None
        raise typer.BadParameter(str(exc), param_hint="--apply") from None
    except (TypeError, ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc), param_hint="--input") from None

    output = result
    if record:
        try:
            record_path = DecisionJournal().record(
                goal=goal,
                role=role,
                memory_types=memory_types,
                constitution_rules=constitution_rules,
                identity_context=runtime.identity_context,
                why_assessment=assessment,
                result=result,
                input_file=input_file,
                apply_status=_apply_status(apply, result),
            )
        except OSError as exc:
            raise typer.BadParameter(
                "Decision Record konnte nicht gespeichert werden: {}".format(exc),
                param_hint="--record",
            ) from None
        output = dict(result)
        output["record_path"] = str(record_path)

    typer.echo(json.dumps(output, ensure_ascii=False, indent=2))
