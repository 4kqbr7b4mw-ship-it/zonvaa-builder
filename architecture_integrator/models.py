from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Tuple


class SourceRole(str, Enum):
    KIMI = "KIMI"
    GEMINI = "GEMINI"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"
    INTERNAL = "INTERNAL"
    OTHER = "OTHER"


class ArchitectureLayer(str, Enum):
    GUARDIAN = "GUARDIAN"
    CONVERSATION = "CONVERSATION"
    INTERACTION = "INTERACTION"
    INSTITUTION = "INSTITUTION"
    GOVERNANCE = "GOVERNANCE"
    RUNTIME = "RUNTIME"
    WORKFLOW = "WORKFLOW"
    CROSS_LAYER = "CROSS_LAYER"


class Recommendation(str, Enum):
    ADOPT = "ADOPT"
    ADOPT_WITH_CHANGES = "ADOPT_WITH_CHANGES"
    REJECT = "REJECT"
    DEFER = "DEFER"


class DecisionChoice(str, Enum):
    ADOPT = "ADOPT"
    ADOPT_WITH_CHANGES = "ADOPT_WITH_CHANGES"
    REJECT = "REJECT"
    DEFER = "DEFER"


class NormLevel(str, Enum):
    C1_CONSTITUTION = "C1"
    MDR = "MDR"
    C2_GOVERNANCE = "C2"
    SPECIFICATION = "SPECIFICATION"
    ADR = "ADR"
    C3_OPERATIVE = "C3"
    HISTORICAL = "HISTORICAL"
    HANDOVER = "HANDOVER"
    EXTERNAL = "EXTERNAL"

    @property
    def priority(self) -> int:
        return tuple(NormLevel).index(self)


class SourceStatus(str, Enum):
    BINDING = "BINDING"
    DERIVED = "DERIVED"
    HISTORICAL = "HISTORICAL"
    SUPPLEMENTAL = "SUPPLEMENTAL"
    STATUS_MISSING = "STATUS_MISSING"


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value.strip():
        raise ValueError("{} must not be empty".format(field_name))
    if value != value.strip():
        raise ValueError("{} must be trimmed".format(field_name))
    return value


def _tuple_of(
    value: object,
    item_type: type,
    field_name: str,
) -> tuple:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError(
            "{} must contain {} values".format(
                field_name,
                item_type.__name__,
            )
        )
    return value


def _aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


@dataclass(frozen=True)
class ArchitectureProposal:
    proposal_id: str
    title: str
    source: str
    source_role: SourceRole
    submitted_at: datetime
    content: str
    requested_scope: str
    related_layers: Tuple[ArchitectureLayer, ...]
    known_constraints: Tuple[str, ...]
    source_references: Tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "proposal_id",
            "title",
            "source",
            "content",
            "requested_scope",
        ):
            _text(getattr(self, name), "ArchitectureProposal {}".format(name))
        if not isinstance(self.source_role, SourceRole):
            raise TypeError(
                "ArchitectureProposal source_role must be SourceRole"
            )
        _aware(self.submitted_at, "ArchitectureProposal submitted_at")
        _tuple_of(
            self.related_layers,
            ArchitectureLayer,
            "ArchitectureProposal related_layers",
        )
        if not self.related_layers:
            raise ValueError(
                "ArchitectureProposal related_layers must not be empty"
            )
        for name in ("known_constraints", "source_references"):
            values = _tuple_of(
                getattr(self, name),
                str,
                "ArchitectureProposal {}".format(name),
            )
            for value in values:
                _text(value, "ArchitectureProposal {} item".format(name))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "source": self.source,
            "source_role": self.source_role.value,
            "submitted_at": self.submitted_at.isoformat(),
            "content": self.content,
            "requested_scope": self.requested_scope,
            "related_layers": [
                layer.value for layer in self.related_layers
            ],
            "known_constraints": list(self.known_constraints),
            "source_references": list(self.source_references),
        }


@dataclass(frozen=True)
class ContextSource:
    source_id: str
    path: str
    version: str
    content_hash: str
    norm_level: NormLevel
    status: SourceStatus
    relevance: str
    content: str

    def __post_init__(self) -> None:
        for name in (
            "source_id",
            "path",
            "version",
            "relevance",
        ):
            _text(getattr(self, name), "ContextSource {}".format(name))
        if not isinstance(self.status, SourceStatus):
            raise TypeError("ContextSource status must be SourceStatus")
        if not isinstance(self.content, str):
            raise TypeError("ContextSource content must be a string")
        if not self.content.strip():
            raise ValueError("ContextSource content must not be empty")
        if not isinstance(self.norm_level, NormLevel):
            raise TypeError("ContextSource norm_level must be NormLevel")
        if (
            not isinstance(self.content_hash, str)
            or len(self.content_hash) != 64
            or any(char not in "0123456789abcdef" for char in self.content_hash)
        ):
            raise ValueError(
                "ContextSource content_hash must be a SHA-256 digest"
            )

    def to_dict(self, include_content: bool = False) -> Dict[str, Any]:
        result = {
            "source_id": self.source_id,
            "path": self.path,
            "version": self.version,
            "hash": self.content_hash,
            "norm_level": self.norm_level.value,
            "status": self.status.value,
            "relevance": self.relevance,
        }
        if include_content:
            result["content"] = self.content
        return result


@dataclass(frozen=True)
class Conflict:
    conflict_id: str
    proposed_statement: str
    existing_statement: str
    existing_source: str
    norm_level: NormLevel
    conflict_reason: str
    suggested_resolution: str
    requires_chief_architect_decision: bool

    def __post_init__(self) -> None:
        for name in (
            "conflict_id",
            "proposed_statement",
            "existing_statement",
            "existing_source",
            "conflict_reason",
            "suggested_resolution",
        ):
            _text(getattr(self, name), "Conflict {}".format(name))
        if not isinstance(self.norm_level, NormLevel):
            raise TypeError("Conflict norm_level must be NormLevel")
        if self.requires_chief_architect_decision is not True:
            raise ValueError(
                "Conflict must require a Chief Architect decision"
            )

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["norm_level"] = self.norm_level.value
        return result


@dataclass(frozen=True)
class ArchitectureAnalysis:
    proposal: ArchitectureProposal
    loaded_context_sources: Tuple[ContextSource, ...]
    applicable_norms: Tuple[str, ...]
    proposal_summary: str
    aligned_elements: Tuple[str, ...]
    additive_elements: Tuple[str, ...]
    conflicting_elements: Tuple[Conflict, ...]
    duplicate_elements: Tuple[str, ...]
    unresolved_questions: Tuple[str, ...]
    affected_layers: Tuple[ArchitectureLayer, ...]
    affected_documents: Tuple[str, ...]
    implementation_risks: Tuple[str, ...]
    recommendation: Recommendation
    confidence: float
    decision_required: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, ArchitectureProposal):
            raise TypeError(
                "ArchitectureAnalysis proposal must be ArchitectureProposal"
            )
        _tuple_of(
            self.loaded_context_sources,
            ContextSource,
            "ArchitectureAnalysis loaded_context_sources",
        )
        for name in (
            "applicable_norms",
            "aligned_elements",
            "additive_elements",
            "duplicate_elements",
            "unresolved_questions",
            "affected_documents",
            "implementation_risks",
            "decision_required",
        ):
            values = _tuple_of(
                getattr(self, name),
                str,
                "ArchitectureAnalysis {}".format(name),
            )
            for value in values:
                _text(value, "ArchitectureAnalysis {} item".format(name))
        _text(self.proposal_summary, "ArchitectureAnalysis proposal_summary")
        _tuple_of(
            self.conflicting_elements,
            Conflict,
            "ArchitectureAnalysis conflicting_elements",
        )
        _tuple_of(
            self.affected_layers,
            ArchitectureLayer,
            "ArchitectureAnalysis affected_layers",
        )
        if not isinstance(self.recommendation, Recommendation):
            raise TypeError(
                "ArchitectureAnalysis recommendation must be Recommendation"
            )
        if (
            not isinstance(self.confidence, float)
            or self.confidence < 0.0
            or self.confidence > 1.0
        ):
            raise ValueError(
                "ArchitectureAnalysis confidence must be between 0 and 1"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "proposal": self.proposal.to_dict(),
            "loaded_context_sources": [
                source.to_dict() for source in self.loaded_context_sources
            ],
            "applicable_norms": list(self.applicable_norms),
            "proposal_summary": self.proposal_summary,
            "aligned_elements": list(self.aligned_elements),
            "additive_elements": list(self.additive_elements),
            "conflicting_elements": [
                conflict.to_dict() for conflict in self.conflicting_elements
            ],
            "duplicate_elements": list(self.duplicate_elements),
            "unresolved_questions": list(self.unresolved_questions),
            "affected_layers": [
                layer.value for layer in self.affected_layers
            ],
            "affected_documents": list(self.affected_documents),
            "implementation_risks": list(self.implementation_risks),
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "decision_required": list(self.decision_required),
        }


@dataclass(frozen=True)
class ChiefArchitectDecision:
    decision_id: str
    proposal_id: str
    decision: DecisionChoice
    accepted_elements: Tuple[str, ...]
    modified_elements: Tuple[str, ...]
    rejected_elements: Tuple[str, ...]
    deferred_elements: Tuple[str, ...]
    rationale: str
    decided_by: str
    decided_at: datetime

    def __post_init__(self) -> None:
        for name in ("decision_id", "proposal_id", "rationale", "decided_by"):
            _text(
                getattr(self, name),
                "ChiefArchitectDecision {}".format(name),
            )
        if not isinstance(self.decision, DecisionChoice):
            raise TypeError(
                "ChiefArchitectDecision decision must be DecisionChoice"
            )
        for name in (
            "accepted_elements",
            "modified_elements",
            "rejected_elements",
            "deferred_elements",
        ):
            values = _tuple_of(
                getattr(self, name),
                str,
                "ChiefArchitectDecision {}".format(name),
            )
            for value in values:
                _text(value, "ChiefArchitectDecision {} item".format(name))
        _aware(self.decided_at, "ChiefArchitectDecision decided_at")
