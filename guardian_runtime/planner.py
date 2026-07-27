import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from guardian_runtime.models import (
    GuardianMemory,
    GuardianRuntimeSnapshot,
    KnowledgeConflict,
    KnowledgeItem,
    KnowledgeTransition,
    RetentionClass,
    TransitionType,
)


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if (
        not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError(
            "{} must be a trimmed single line".format(field_name)
        )
    return value


@dataclass(frozen=True)
class KnowledgeTransitionRequest:
    transition_type: TransitionType
    knowledge_id: str
    candidate_item: Optional[KnowledgeItem]
    trigger: str
    authorization_reference: str
    requested_at: datetime
    reason: str
    source_references: Tuple[str, ...]
    expected_snapshot_version: int
    conflict: Optional[KnowledgeConflict] = None

    def __post_init__(self) -> None:
        if not isinstance(self.transition_type, TransitionType):
            raise TypeError("transition_type must be TransitionType")
        _text(self.knowledge_id, "knowledge_id")
        if self.candidate_item is not None and not isinstance(
            self.candidate_item,
            KnowledgeItem,
        ):
            raise TypeError("candidate_item must be KnowledgeItem or None")
        _text(self.trigger, "trigger")
        _text(self.authorization_reference, "authorization_reference")
        if (
            not isinstance(self.requested_at, datetime)
            or self.requested_at.tzinfo is None
            or self.requested_at.utcoffset() is None
        ):
            raise ValueError("requested_at must be timezone-aware")
        _text(self.reason, "reason")
        if not isinstance(self.source_references, tuple):
            raise TypeError("source_references must be a tuple")
        for reference in self.source_references:
            _text(reference, "source_references item")
        if len(self.source_references) != len(set(self.source_references)):
            raise ValueError("source_references must be unique")
        if not self.source_references:
            raise ValueError("source_references must not be empty")
        if (
            not isinstance(self.expected_snapshot_version, int)
            or isinstance(self.expected_snapshot_version, bool)
        ):
            raise TypeError("expected_snapshot_version must be an int")
        if self.expected_snapshot_version < 0:
            raise ValueError("expected_snapshot_version must not be negative")
        if self.conflict is not None and not isinstance(
            self.conflict,
            KnowledgeConflict,
        ):
            raise TypeError("conflict must be KnowledgeConflict or None")
        if (
            self.transition_type is TransitionType.CONTRADICTION_DETECTED
        ) != (self.conflict is not None):
            raise ValueError(
                "contradiction_detected requires exactly one conflict"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_type": self.transition_type.value,
            "knowledge_id": self.knowledge_id,
            "candidate_item": (
                self.candidate_item.to_dict()
                if self.candidate_item is not None
                else None
            ),
            "trigger": self.trigger,
            "authorization_reference": self.authorization_reference,
            "requested_at": self.requested_at.isoformat(),
            "reason": self.reason,
            "source_references": list(self.source_references),
            "expected_snapshot_version": self.expected_snapshot_version,
            "conflict": (
                self.conflict.to_dict()
                if self.conflict is not None
                else None
            ),
        }


@dataclass(frozen=True)
class KnowledgeTransitionPlan:
    transition: KnowledgeTransition
    resulting_snapshot: GuardianRuntimeSnapshot

    def __post_init__(self) -> None:
        if not isinstance(self.transition, KnowledgeTransition):
            raise TypeError("transition must be KnowledgeTransition")
        if not isinstance(
            self.resulting_snapshot,
            GuardianRuntimeSnapshot,
        ):
            raise TypeError(
                "resulting_snapshot must be GuardianRuntimeSnapshot"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition": self.transition.to_dict(),
            "resulting_snapshot": self.resulting_snapshot.to_dict(),
        }


class GuardianRuntimeTransitionPlanner:
    """Plans one authorized mutation without persistence or execution."""

    _CREATION_TYPES = {
        TransitionType.STATEMENT_RECORDED,
        TransitionType.HYPOTHESIS_CREATED,
        TransitionType.INTERPRETATION_ADDED,
    }

    def plan(
        self,
        snapshot: GuardianRuntimeSnapshot,
        request: KnowledgeTransitionRequest,
    ) -> KnowledgeTransitionPlan:
        if not isinstance(snapshot, GuardianRuntimeSnapshot):
            raise TypeError("snapshot must be GuardianRuntimeSnapshot")
        if not isinstance(request, KnowledgeTransitionRequest):
            raise TypeError("request must be KnowledgeTransitionRequest")
        if snapshot.active_subject_id is None:
            raise ValueError("Unbound Guardian Runtime cannot plan transitions")
        if (
            request.expected_snapshot_version
            != snapshot.knowledge_snapshot_version
        ):
            raise ValueError("Knowledge snapshot version changed")
        if request.requested_at < snapshot.captured_at:
            raise ValueError(
                "Transition cannot precede the current snapshot"
            )
        authorization = next(
            (
                item
                for item in snapshot.active_authorizations
                if item.authorization_id
                == request.authorization_reference
            ),
            None,
        )
        if authorization is None:
            raise ValueError(
                "Transition lacks an active authorization reference"
            )
        if request.knowledge_id not in authorization.knowledge_ids:
            raise ValueError(
                "Transition exceeds the authorized knowledge scope"
            )
        if (
            authorization.authorization.granted_at
            > request.requested_at
        ):
            raise ValueError(
                "Transition authorization was not active at request time"
            )
        items = {
            item.knowledge_id: item for item in snapshot.knowledge_items
        }
        before = items.get(request.knowledge_id)
        after = request.candidate_item
        if request.transition_type in self._CREATION_TYPES:
            if before is not None:
                raise ValueError("Knowledge ID already exists")
        elif before is None:
            raise ValueError("Knowledge item does not exist")
        if after is not None:
            if after.knowledge_id != request.knowledge_id:
                raise ValueError("Candidate knowledge_id does not match")
            if (
                after.owner_id != snapshot.active_subject_id
                or after.subject_id != snapshot.active_subject_id
            ):
                raise ValueError(
                    "Candidate crosses the person-bound context"
                )
        if request.transition_type in {
            TransitionType.RETENTION_CHANGED,
            TransitionType.KNOWLEDGE_DELETED,
        }:
            will_delete = (
                request.transition_type is TransitionType.KNOWLEDGE_DELETED
                or (
                    after is not None
                    and after.retention_class is RetentionClass.DELETE
                )
            )
            if will_delete:
                dependencies = self._dependencies(
                    snapshot,
                    request.knowledge_id,
                )
                if dependencies:
                    raise ValueError(
                        "Derived or related knowledge requires reevaluation: "
                        + ", ".join(dependencies)
                    )
        transition = KnowledgeTransition(
            transition_id=self._transition_id(snapshot, request, before),
            transition_type=request.transition_type,
            previous_item=before,
            new_item=after,
            trigger=request.trigger,
            authorization_reference=request.authorization_reference,
            occurred_at=request.requested_at,
            reason=request.reason,
            source_references=request.source_references,
        )
        resulting_items = dict(items)
        if after is None:
            resulting_items.pop(request.knowledge_id)
        else:
            resulting_items[request.knowledge_id] = after
        conflicts = {
            item.conflict_id: item
            for item in snapshot.unresolved_conflicts
        }
        if request.conflict is not None:
            if request.conflict.conflict_id in conflicts:
                raise ValueError("Conflict ID already exists")
            if request.knowledge_id not in request.conflict.knowledge_ids:
                raise ValueError("Conflict does not include changed knowledge")
            conflicts[request.conflict.conflict_id] = request.conflict
        result_snapshot = GuardianRuntimeSnapshot.create(
            captured_at=request.requested_at,
            active_guardian_id=snapshot.active_guardian_id,
            active_subject_id=snapshot.active_subject_id,
            knowledge_snapshot_version=(
                snapshot.knowledge_snapshot_version + 1
            ),
            applicable_memory_scope=snapshot.applicable_memory_scope,
            knowledge_items=tuple(resulting_items.values()),
            memory=self._updated_memory(
                snapshot,
                request.knowledge_id,
                after,
            ),
            unresolved_conflicts=tuple(conflicts.values()),
            active_authorizations=snapshot.active_authorizations,
            transitions=snapshot.transitions + (transition,),
        )
        return KnowledgeTransitionPlan(
            transition=transition,
            resulting_snapshot=result_snapshot,
        )

    def _dependencies(
        self,
        snapshot: GuardianRuntimeSnapshot,
        knowledge_id: str,
    ) -> Tuple[str, ...]:
        dependencies = {
            item.knowledge_id
            for item in snapshot.knowledge_items
            if item.knowledge_id != knowledge_id
            and knowledge_id
            in (
                item.source_references
                + item.supersedes
                + item.contradicted_by
            )
        }
        dependencies.update(
            conflict.conflict_id
            for conflict in snapshot.unresolved_conflicts
            if knowledge_id in conflict.knowledge_ids
        )
        return tuple(sorted(dependencies))

    def _updated_memory(
        self,
        snapshot: GuardianRuntimeSnapshot,
        knowledge_id: str,
        candidate: Optional[KnowledgeItem],
    ) -> GuardianMemory:
        if candidate is not None:
            return snapshot.memory
        return GuardianMemory(
            episodic_ids=tuple(
                item
                for item in snapshot.memory.episodic_ids
                if item != knowledge_id
            ),
            semantic_ids=tuple(
                item
                for item in snapshot.memory.semantic_ids
                if item != knowledge_id
            ),
            preference_ids=tuple(
                item
                for item in snapshot.memory.preference_ids
                if item != knowledge_id
            ),
            decision_ids=tuple(
                item
                for item in snapshot.memory.decision_ids
                if item != knowledge_id
            ),
            commitment_ids=tuple(
                item
                for item in snapshot.memory.commitment_ids
                if item != knowledge_id
            ),
            relationship_trust_ids=tuple(
                item
                for item in snapshot.memory.relationship_trust_ids
                if item != knowledge_id
            ),
            historical_ids=tuple(
                item
                for item in snapshot.memory.historical_ids
                if item != knowledge_id
            ),
        )

    def _transition_id(
        self,
        snapshot: GuardianRuntimeSnapshot,
        request: KnowledgeTransitionRequest,
        before: Optional[KnowledgeItem],
    ) -> str:
        canonical = json.dumps(
            {
                "runtime_context_hash": snapshot.runtime_context_hash,
                "request": request.to_dict(),
                "previous_item": (
                    before.to_dict() if before is not None else None
                ),
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return "knowledge-transition-{}".format(
            hashlib.sha256(canonical).hexdigest()[:20]
        )
