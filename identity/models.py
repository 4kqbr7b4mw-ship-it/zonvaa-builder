from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IdentityContext:
    """Uninterpreted, versioned identity loaded from the canonical WHY source."""

    content: str
    source: Path
    version: str
