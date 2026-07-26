from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple


class InteractionPrinciple(str, Enum):
    CONVERSATION_ENGINE = "conversation_engine"
    INSTITUTION_BOARD = "institution_board"
    DUAL_SPACE = "dual_space"
    CONVERSATION_INSTITUTION_TRANSITION = (
        "conversation_institution_transition"
    )
    ARTIFACT_ARCHITECTURE = "artifact_architecture"
    ARTIFACT_ISLAND = "artifact_island"
    AUTHORIZATION_BOUNDARY = "authorization_boundary"
    GUARDIAN_INSTANCE_ISOLATION = "guardian_instance_isolation"
    MULTI_PARTY_GRAPH = "multi_party_graph"
    SHARED_SAFE = "shared_safe"
    NEUTRALITY_GUARANTEE = "neutrality_guarantee"
    INACTIVITY_IS_SUCCESS = "inactivity_is_success"
    OFFBOARDING_NO_LOCK_IN = "offboarding_no_lock_in"
    UNAVAILABILITY_CLAUSE = "unavailability_clause"
    SYSTEM_LIMIT_HANDOVER = "system_limit_handover"


@dataclass(frozen=True)
class InteractionContext:
    """Versioned interaction boundaries without operational UI logic."""

    content: str
    source: Path
    version: str
    content_hash: str
    principles: Tuple[InteractionPrinciple, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("InteractionContext content must be a string")
        if not self.content.strip():
            raise ValueError("InteractionContext content must not be empty")
        if not isinstance(self.source, Path):
            raise TypeError("InteractionContext source must be a Path")
        if not isinstance(self.version, str):
            raise TypeError("InteractionContext version must be a string")
        if not self.version.strip():
            raise ValueError("InteractionContext version must not be empty")
        if not isinstance(self.content_hash, str):
            raise TypeError(
                "InteractionContext content_hash must be a string"
            )
        if (
            len(self.content_hash) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.content_hash
            )
        ):
            raise ValueError(
                "InteractionContext content_hash must be a SHA-256 digest"
            )
        if not isinstance(self.principles, tuple):
            raise TypeError("InteractionContext principles must be a tuple")
        if not all(
            isinstance(item, InteractionPrinciple)
            for item in self.principles
        ):
            raise TypeError(
                "InteractionContext principles must contain "
                "InteractionPrinciple values"
            )
        if self.principles != tuple(InteractionPrinciple):
            raise ValueError(
                "InteractionContext must contain every principle exactly "
                "once in canonical order"
            )
