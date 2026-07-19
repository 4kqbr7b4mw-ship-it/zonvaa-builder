from pathlib import Path


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
        }
