from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from guardian_runtime import (
    GuardianRuntimeSnapshot,
    KnowledgeItem,
)
from knowledge.memory import MemoryRecord
from knowledge.verified_facts import VerifiedFacts


class KnowledgeManager:
    """Zentrale Schnittstelle für das Builder-Wissen."""

    REQUIRED_FOLDERS = (
        "adr",
        "architecture_workflows",
        "handovers",
        "mdr",
        "project",
        "protocols",
        "sessions",
        "sources",
    )

    def __init__(self) -> None:
        self.root = Path("knowledge")

    def load(self) -> dict:
        missing = [
            name
            for name in self.REQUIRED_FOLDERS
            if not (self.root / name).is_dir()
        ]
        if missing:
            raise FileNotFoundError(
                "Missing knowledge folders: {}".format(
                    ", ".join(missing)
                )
            )
        return {
            "adr": sorted((self.root / "adr").glob("*.md")),
            "architecture_workflows": sorted(
                (self.root / "architecture_workflows").glob("*")
            ),
            "mdr": sorted((self.root / "mdr").glob("*.md")),
            "protocols": sorted((self.root / "protocols").glob("*.md")),
            "handovers": sorted(
                list((self.root / "handovers").glob("*.md"))
                + list((self.root / "handovers").glob("*.json"))
            ),
            "project": sorted((self.root / "project").glob("*.md")),
            "sessions": sorted((self.root / "sessions").glob("*.md")),
            "sources": sorted((self.root / "sources").glob("*")),
            "verified_facts": VerifiedFacts().load(),
        }

    def classify_memory(self, **metadata: Any) -> MemoryRecord:
        """Validate memory metadata without introducing another knowledge store."""
        return MemoryRecord(**metadata)

    def validate_guardian_knowledge(
        self,
        knowledge_item: KnowledgeItem,
    ) -> KnowledgeItem:
        """Validate typed Guardian knowledge without persisting it."""
        if not isinstance(knowledge_item, KnowledgeItem):
            raise TypeError("knowledge_item must be KnowledgeItem")
        return knowledge_item

    def unbound_guardian_runtime(
        self,
        captured_at: datetime,
    ) -> GuardianRuntimeSnapshot:
        """Provide the explicit empty runtime state for no active person."""
        return GuardianRuntimeSnapshot.unbound(captured_at)

    def latest_session(self):
        return self._latest_file(self.root / "sessions", ("*.md",))

    def latest_handover(self) -> Optional[Path]:
        return self._latest_file(
            self.root / "handovers",
            ("*.json", "*.md"),
        )

    def latest_context(self) -> Optional[Path]:
        candidates = [
            path
            for path in (self.latest_session(), self.latest_handover())
            if path is not None
        ]
        return max(candidates, key=lambda path: path.stat().st_mtime, default=None)

    def _latest_file(
        self,
        folder: Path,
        patterns: tuple,
    ) -> Optional[Path]:
        candidates = []
        for pattern in patterns:
            candidates.extend(folder.glob(pattern))
        return max(
            candidates,
            key=lambda path: path.stat().st_mtime,
            default=None,
        )
