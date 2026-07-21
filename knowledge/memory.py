from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Union


class MemoryType(str, Enum):
    WORKING = "working_memory"
    PROJECT = "project_memory"
    PERSONAL = "personal_memory"
    KNOWLEDGE = "knowledge_memory"
    HERITAGE = "heritage_memory"
    ARCHIVE = "archive_memory"


class Confidence(str, Enum):
    UNCERTAIN = "uncertain"
    PROBABLE = "probable"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class MemoryRecord:
    """Classification metadata for knowledge managed by the central runtime."""

    memory_type: Union[MemoryType, str]
    source: str
    created_at: datetime
    confidence: Union[Confidence, str]
    retention_policy: str
    protected: bool = False
    verified: bool = False

    def __post_init__(self) -> None:
        try:
            memory_type = MemoryType(self.memory_type)
        except ValueError as exc:
            raise ValueError("Unknown memory type: {}".format(self.memory_type)) from exc

        try:
            confidence = Confidence(self.confidence)
        except ValueError as exc:
            raise ValueError("Unknown confidence: {}".format(self.confidence)) from exc

        if not self.source.strip():
            raise ValueError("Memory source must not be empty")
        if not self.retention_policy.strip():
            raise ValueError("Retention policy must not be empty")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include timezone information")
        if self.verified and confidence is not Confidence.CONFIRMED:
            raise ValueError("Only confirmed memory may be marked as verified")

        object.__setattr__(self, "memory_type", memory_type)
        object.__setattr__(self, "confidence", confidence)

        if memory_type is MemoryType.HERITAGE:
            object.__setattr__(self, "protected", True)
