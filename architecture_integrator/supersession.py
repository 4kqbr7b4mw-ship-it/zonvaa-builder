import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from architecture_integrator.feedback import stable_identifier
from architecture_integrator.io import write_json
from architecture_integrator.workflow import ArchitectureWorkflowStore


class ArchitectureWorkflowSupersessionError(ValueError):
    pass


@dataclass(frozen=True)
class ArchitectureWorkflowSupersession:
    supersession_id: str
    topic: str
    superseded_workflow_id: str
    canonical_workflow_id: str
    reason: str
    recorded_at: datetime
    recorded_by: str
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported workflow supersession schema")
        _identifier(self.supersession_id, "supersession_id", "supersession")
        _identifier(
            self.superseded_workflow_id,
            "superseded_workflow_id",
            "workflow",
        )
        _identifier(
            self.canonical_workflow_id,
            "canonical_workflow_id",
            "workflow",
        )
        if self.superseded_workflow_id == self.canonical_workflow_id:
            raise ValueError("A workflow cannot supersede itself")
        for value, name in (
            (self.topic, "topic"),
            (self.reason, "reason"),
            (self.recorded_by, "recorded_by"),
        ):
            _text(value, name)
        _aware(self.recorded_at, "recorded_at")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "supersession_id": self.supersession_id,
            "topic": self.topic,
            "superseded_workflow_id": self.superseded_workflow_id,
            "canonical_workflow_id": self.canonical_workflow_id,
            "reason": self.reason,
            "recorded_at": self.recorded_at.isoformat(),
            "recorded_by": self.recorded_by,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ArchitectureWorkflowSupersession":
        expected = {
            "schema_version",
            "supersession_id",
            "topic",
            "superseded_workflow_id",
            "canonical_workflow_id",
            "reason",
            "recorded_at",
            "recorded_by",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Workflow supersession fields are invalid")
        return cls(
            schema_version=data["schema_version"],
            supersession_id=data["supersession_id"],
            topic=data["topic"],
            superseded_workflow_id=data["superseded_workflow_id"],
            canonical_workflow_id=data["canonical_workflow_id"],
            reason=data["reason"],
            recorded_at=datetime.fromisoformat(data["recorded_at"]),
            recorded_by=data["recorded_by"],
        )


class ArchitectureWorkflowSupersessionStore:
    def __init__(
        self,
        workflows: ArchitectureWorkflowStore,
        root: Optional[Path] = None,
    ) -> None:
        self.workflows = workflows
        self.root = (
            root
            if root is not None
            else workflows.root.parent / "architecture_workflow_supersessions"
        )

    def path(self, superseded_workflow_id: str) -> Path:
        _identifier(
            superseded_workflow_id,
            "superseded_workflow_id",
            "workflow",
        )
        return self.root / "{}.json".format(superseded_workflow_id)

    def records(self) -> Tuple[ArchitectureWorkflowSupersession, ...]:
        if not self.root.exists():
            return ()
        self._ensure_root(create=False)
        records = []
        for path in sorted(self.root.glob("workflow-*.json")):
            if path.is_symlink() or not path.is_file():
                raise ArchitectureWorkflowSupersessionError(
                    "Workflow supersession artifact is unavailable or unsafe."
                )
            try:
                record = ArchitectureWorkflowSupersession.from_dict(
                    json.loads(path.read_text(encoding="utf-8"))
                )
            except (OSError, TypeError, ValueError) as error:
                raise ArchitectureWorkflowSupersessionError(
                    "Workflow supersession artifact is invalid: {}".format(
                        error
                    )
                )
            if path != self.path(record.superseded_workflow_id):
                raise ArchitectureWorkflowSupersessionError(
                    "Workflow supersession path is not canonical."
                )
            records.append(record)
        self._validate_graph(tuple(records))
        return tuple(records)

    def for_workflow(
        self,
        workflow_id: str,
    ) -> Optional[ArchitectureWorkflowSupersession]:
        return next(
            (
                item
                for item in self.records()
                if item.superseded_workflow_id == workflow_id
            ),
            None,
        )

    def related(
        self,
        workflow_id: str,
    ) -> Tuple[ArchitectureWorkflowSupersession, ...]:
        return tuple(
            item
            for item in self.records()
            if workflow_id in {
                item.superseded_workflow_id,
                item.canonical_workflow_id,
            }
        )

    def record(
        self,
        superseded_workflow_id: str,
        canonical_workflow_id: str,
        reason: str,
        recorded_at: datetime,
        recorded_by: str = "Chief Architect",
    ) -> ArchitectureWorkflowSupersession:
        _text(reason, "reason")
        _aware(recorded_at, "recorded_at")
        if superseded_workflow_id == canonical_workflow_id:
            raise ArchitectureWorkflowSupersessionError(
                "A workflow cannot supersede itself."
            )
        try:
            superseded = self.workflows.load(superseded_workflow_id)
            canonical = self.workflows.load(canonical_workflow_id)
        except (OSError, TypeError, ValueError) as error:
            raise ArchitectureWorkflowSupersessionError(
                "Workflow supersession reference is invalid: {}".format(
                    error
                )
            )
        superseded_topic = normalize_topic(superseded.topic)
        canonical_topic = normalize_topic(canonical.topic)
        if superseded_topic != canonical_topic:
            raise ArchitectureWorkflowSupersessionError(
                "Workflow topics do not match."
            )
        existing = self.for_workflow(superseded_workflow_id)
        if existing is not None:
            if (
                existing.canonical_workflow_id == canonical_workflow_id
                and existing.reason == reason
                and normalize_topic(existing.topic) == superseded_topic
                and existing.recorded_by == recorded_by
            ):
                return existing
            raise ArchitectureWorkflowSupersessionError(
                "A conflicting workflow supersession already exists."
            )
        records = self.records()
        if any(
            item.superseded_workflow_id == canonical_workflow_id
            for item in records
        ):
            raise ArchitectureWorkflowSupersessionError(
                "A superseded workflow cannot be canonical."
            )
        if any(
            item.canonical_workflow_id == superseded_workflow_id
            for item in records
        ):
            raise ArchitectureWorkflowSupersessionError(
                "A canonical workflow cannot later be superseded."
            )
        record = ArchitectureWorkflowSupersession(
            supersession_id=stable_identifier(
                "supersession",
                superseded_workflow_id,
                canonical_workflow_id,
                reason,
            ),
            topic=canonical.topic,
            superseded_workflow_id=superseded_workflow_id,
            canonical_workflow_id=canonical_workflow_id,
            reason=reason,
            recorded_at=recorded_at,
            recorded_by=recorded_by,
        )
        self._validate_graph(records + (record,))
        path = self.path(superseded_workflow_id)
        if path.exists():
            raise ArchitectureWorkflowSupersessionError(
                "A workflow supersession artifact already exists."
            )
        self._ensure_root(create=True)
        write_json(path, record.to_dict())
        return record

    def _ensure_root(self, create: bool) -> None:
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
        if not self.root.is_dir() or self.root.is_symlink():
            raise ArchitectureWorkflowSupersessionError(
                "Workflow supersession root is unavailable or unsafe."
            )

    def _validate_graph(
        self,
        records: Tuple[ArchitectureWorkflowSupersession, ...],
    ) -> None:
        mapping = {}
        for item in records:
            if item.superseded_workflow_id in mapping:
                raise ArchitectureWorkflowSupersessionError(
                    "A workflow has multiple supersession records."
                )
            mapping[item.superseded_workflow_id] = (
                item.canonical_workflow_id
            )
        for start in mapping:
            seen = set()
            current = start
            while current in mapping:
                if current in seen:
                    raise ArchitectureWorkflowSupersessionError(
                        "Workflow supersession cycle detected."
                    )
                seen.add(current)
                current = mapping[current]


def normalize_topic(value: str) -> str:
    _text(value, "topic")
    return " ".join(value.split()).casefold()


def _text(value: object, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError("{} must be trimmed single-line text".format(name))


def _identifier(value: object, name: str, prefix: str) -> None:
    _text(value, name)
    if not value.startswith(prefix + "-"):
        raise ValueError("{} must start with {}-".format(name, prefix))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))
