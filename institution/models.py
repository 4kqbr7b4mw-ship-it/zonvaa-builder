from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple


class InstitutionGuarantee(str, Enum):
    GOVERNANCE = "governance"
    USER_SOVEREIGNTY = "user_sovereignty"
    GUARDIAN_CONTINUITY = "guardian_continuity"
    TRANSPARENCY = "transparency"
    RESPONSIBILITY = "responsibility"
    PROTECTION = "protection"
    DIGNITY = "dignity"
    TRUST_MODEL = "trust_model"


@dataclass(frozen=True)
class InstitutionContext:
    """Versioned long-term guarantees without operational policy logic."""

    content: str
    source: Path
    version: str
    content_hash: str
    guarantees: Tuple[InstitutionGuarantee, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("InstitutionContext content must be a string")
        if not self.content.strip():
            raise ValueError("InstitutionContext content must not be empty")
        if not isinstance(self.source, Path):
            raise TypeError("InstitutionContext source must be a Path")
        if not isinstance(self.version, str):
            raise TypeError("InstitutionContext version must be a string")
        if not self.version.strip():
            raise ValueError("InstitutionContext version must not be empty")
        if not isinstance(self.content_hash, str):
            raise TypeError(
                "InstitutionContext content_hash must be a string"
            )
        if (
            len(self.content_hash) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.content_hash
            )
        ):
            raise ValueError(
                "InstitutionContext content_hash must be a SHA-256 digest"
            )
        if not isinstance(self.guarantees, tuple):
            raise TypeError("InstitutionContext guarantees must be a tuple")
        if not all(
            isinstance(item, InstitutionGuarantee)
            for item in self.guarantees
        ):
            raise TypeError(
                "InstitutionContext guarantees must contain "
                "InstitutionGuarantee values"
            )
        if self.guarantees != tuple(InstitutionGuarantee):
            raise ValueError(
                "InstitutionContext must contain every guarantee exactly once "
                "in canonical order"
            )
