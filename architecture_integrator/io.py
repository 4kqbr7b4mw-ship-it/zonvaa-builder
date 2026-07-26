import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from architecture_integrator.models import (
    ArchitectureAnalysis,
    ArchitectureLayer,
    ArchitectureProposal,
    ChiefArchitectDecision,
    Conflict,
    ContextSource,
    DecisionChoice,
    NormLevel,
    Recommendation,
    SourceRole,
    SourceStatus,
)


def load_proposal(path: Path) -> ArchitectureProposal:
    data = _object(path)
    _fields(
        data,
        {
            "proposal_id",
            "title",
            "source",
            "source_role",
            "submitted_at",
            "content",
            "requested_scope",
            "related_layers",
            "known_constraints",
            "source_references",
        },
        "proposal",
    )
    return ArchitectureProposal(
        proposal_id=data["proposal_id"],
        title=data["title"],
        source=data["source"],
        source_role=_enum(SourceRole, data["source_role"], "source_role"),
        submitted_at=_datetime(data["submitted_at"], "submitted_at"),
        content=data["content"],
        requested_scope=data["requested_scope"],
        related_layers=_enums(
            ArchitectureLayer,
            data["related_layers"],
            "related_layers",
        ),
        known_constraints=_strings(
            data["known_constraints"],
            "known_constraints",
        ),
        source_references=_strings(
            data["source_references"],
            "source_references",
        ),
    )


def load_decision(path: Path) -> ChiefArchitectDecision:
    data = _object(path)
    _fields(
        data,
        {
            "decision_id",
            "proposal_id",
            "decision",
            "accepted_elements",
            "modified_elements",
            "rejected_elements",
            "deferred_elements",
            "rationale",
            "decided_by",
            "decided_at",
        },
        "decision",
    )
    return ChiefArchitectDecision(
        decision_id=data["decision_id"],
        proposal_id=data["proposal_id"],
        decision=_enum(
            DecisionChoice,
            data["decision"],
            "decision",
        ),
        accepted_elements=_strings(
            data["accepted_elements"],
            "accepted_elements",
        ),
        modified_elements=_strings(
            data["modified_elements"],
            "modified_elements",
        ),
        rejected_elements=_strings(
            data["rejected_elements"],
            "rejected_elements",
        ),
        deferred_elements=_strings(
            data["deferred_elements"],
            "deferred_elements",
        ),
        rationale=data["rationale"],
        decided_by=data["decided_by"],
        decided_at=_datetime(data["decided_at"], "decided_at"),
    )


def load_analysis(path: Path) -> ArchitectureAnalysis:
    data = _object(path)
    _fields(
        data,
        {
            "schema_version",
            "proposal",
            "loaded_context_sources",
            "applicable_norms",
            "proposal_summary",
            "aligned_elements",
            "additive_elements",
            "conflicting_elements",
            "duplicate_elements",
            "unresolved_questions",
            "affected_layers",
            "affected_documents",
            "implementation_risks",
            "recommendation",
            "confidence",
            "decision_required",
        },
        "analysis",
    )
    if data["schema_version"] != "1.0":
        raise ValueError("Unsupported analysis schema_version")
    proposal = _proposal_object(data["proposal"])
    sources = tuple(
        _context_source(item) for item in _list(data["loaded_context_sources"])
    )
    conflicts = tuple(
        _conflict(item) for item in _list(data["conflicting_elements"])
    )
    return ArchitectureAnalysis(
        proposal=proposal,
        loaded_context_sources=sources,
        applicable_norms=_strings(data["applicable_norms"], "applicable_norms"),
        proposal_summary=data["proposal_summary"],
        aligned_elements=_strings(
            data["aligned_elements"],
            "aligned_elements",
        ),
        additive_elements=_strings(
            data["additive_elements"],
            "additive_elements",
        ),
        conflicting_elements=conflicts,
        duplicate_elements=_strings(
            data["duplicate_elements"],
            "duplicate_elements",
        ),
        unresolved_questions=_strings(
            data["unresolved_questions"],
            "unresolved_questions",
        ),
        affected_layers=_enums(
            ArchitectureLayer,
            data["affected_layers"],
            "affected_layers",
        ),
        affected_documents=_strings(
            data["affected_documents"],
            "affected_documents",
        ),
        implementation_risks=_strings(
            data["implementation_risks"],
            "implementation_risks",
        ),
        recommendation=_enum(
            Recommendation,
            data["recommendation"],
            "recommendation",
        ),
        confidence=data["confidence"],
        decision_required=_strings(
            data["decision_required"],
            "decision_required",
        ),
    )


def write_json(path: Path, data: Dict[str, Any]) -> None:
    content = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    write_text_atomic(path, content)


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=".architecture-integrator-",
        suffix=".tmp",
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_name, path)
        os.unlink(temporary_name)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _proposal_object(data: object) -> ArchitectureProposal:
    if not isinstance(data, dict):
        raise TypeError("proposal must be an object")
    _fields(
        data,
        {
            "proposal_id",
            "title",
            "source",
            "source_role",
            "submitted_at",
            "content",
            "requested_scope",
            "related_layers",
            "known_constraints",
            "source_references",
        },
        "analysis proposal",
    )
    return ArchitectureProposal(
        proposal_id=data["proposal_id"],
        title=data["title"],
        source=data["source"],
        source_role=_enum(SourceRole, data["source_role"], "source_role"),
        submitted_at=_datetime(data["submitted_at"], "submitted_at"),
        content=data["content"],
        requested_scope=data["requested_scope"],
        related_layers=_enums(
            ArchitectureLayer,
            data["related_layers"],
            "related_layers",
        ),
        known_constraints=_strings(
            data["known_constraints"],
            "known_constraints",
        ),
        source_references=_strings(
            data["source_references"],
            "source_references",
        ),
    )


def _context_source(data: object) -> ContextSource:
    if not isinstance(data, dict):
        raise TypeError("context source must be an object")
    _fields(
        data,
        {
            "source_id",
            "path",
            "version",
            "hash",
            "norm_level",
            "status",
            "relevance",
        },
        "context source",
    )
    return ContextSource(
        source_id=data["source_id"],
        path=data["path"],
        version=data["version"],
        content_hash=data["hash"],
        norm_level=_enum(NormLevel, data["norm_level"], "norm_level"),
        status=_enum(SourceStatus, data["status"], "status"),
        relevance=data["relevance"],
        content="Content omitted from persisted analysis.",
    )


def _conflict(data: object) -> Conflict:
    if not isinstance(data, dict):
        raise TypeError("conflict must be an object")
    _fields(
        data,
        {
            "conflict_id",
            "proposed_statement",
            "existing_statement",
            "existing_source",
            "norm_level",
            "conflict_reason",
            "suggested_resolution",
            "requires_chief_architect_decision",
        },
        "conflict",
    )
    return Conflict(
        conflict_id=data["conflict_id"],
        proposed_statement=data["proposed_statement"],
        existing_statement=data["existing_statement"],
        existing_source=data["existing_source"],
        norm_level=_enum(NormLevel, data["norm_level"], "norm_level"),
        conflict_reason=data["conflict_reason"],
        suggested_resolution=data["suggested_resolution"],
        requires_chief_architect_decision=data[
            "requires_chief_architect_decision"
        ],
    )


def _object(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("{} must contain a JSON object".format(path))
    return data


def _fields(data: dict, expected: set, label: str) -> None:
    missing = expected - set(data)
    unknown = set(data) - expected
    if missing or unknown:
        raise ValueError(
            "Invalid {} fields; missing={}, unknown={}".format(
                label,
                sorted(missing),
                sorted(unknown),
            )
        )


def _enum(enum_type: type, value: object, field_name: str):
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValueError("{} has an unknown value".format(field_name)) from exc


def _enums(
    enum_type: type,
    values: object,
    field_name: str,
) -> tuple:
    return tuple(
        _enum(enum_type, value, field_name)
        for value in _list(values)
    )


def _strings(values: object, field_name: str) -> Tuple[str, ...]:
    result = tuple(_list(values))
    if not all(isinstance(value, str) for value in result):
        raise TypeError("{} must contain strings".format(field_name))
    return result


def _list(value: object) -> list:
    if not isinstance(value, list):
        raise TypeError("Expected a JSON array")
    return value


def _datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("{} is not ISO-8601".format(field_name)) from exc
