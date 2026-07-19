from pathlib import Path

from constitution.manager import ConstitutionManager
from knowledge.manager import KnowledgeManager


class RuntimeManager:
    """Initialisiert und hält den aktuellen Builder-Zustand."""

    def __init__(self) -> None:
        self.constitution: str | None = None
        self.knowledge: dict = {}
        self.latest_session: Path | None = None
        self.latest_session_content: str = ""

    def boot(self) -> "RuntimeManager":
        knowledge_manager = KnowledgeManager()

        self.constitution = ConstitutionManager().load()
        self.knowledge = knowledge_manager.load()
        self.latest_session = knowledge_manager.latest_session()

        if self.latest_session is not None:
            self.latest_session_content = self.latest_session.read_text(
                encoding="utf-8",
                errors="replace",
            )

        return self
