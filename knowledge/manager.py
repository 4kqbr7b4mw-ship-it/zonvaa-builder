from pathlib import Path
from typing import Any

from knowledge.memory import MemoryRecord
from knowledge.verified_facts import VerifiedFacts


class KnowledgeManager:
    """Zentrale Schnittstelle für das Builder-Wissen."""

    def __init__(self) -> None:
        self.root = Path("knowledge")

    def load(self) -> dict:
        return {
            "adr": sorted((self.root / "adr").glob("*.md")),
            "protocols": sorted((self.root / "protocols").glob("*.md")),
            "handovers": sorted((self.root / "handovers").glob("*.md")),
            "project": sorted((self.root / "project").glob("*.md")),
            "sessions": sorted((self.root / "sessions").glob("*.md")),
            "sources": sorted((self.root / "sources").glob("*")),
            "verified_facts": VerifiedFacts().load(),
        }

    def classify_memory(self, **metadata: Any) -> MemoryRecord:
        """Validate memory metadata without introducing another knowledge store."""
        return MemoryRecord(**metadata)

    def latest_session(self):
        sessions = sorted(
            (self.root / "sessions").glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        return sessions[0] if sessions else None
