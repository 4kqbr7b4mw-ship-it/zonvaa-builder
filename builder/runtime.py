from pathlib import Path
from typing import Optional

from constitution.manager import ConstitutionManager
from knowledge.manager import KnowledgeManager


class RuntimeManager:
    """Initialisiert und hält den aktuellen Builder-Zustand."""

    def __init__(self) -> None:
        self.constitution: Optional[str] = None
        self.knowledge: dict = {}
        self.latest_session: Optional[Path] = None
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


_runtime: Optional[RuntimeManager] = None


def get_runtime() -> RuntimeManager:
    """Liefert die einmalig initialisierte Builder-Runtime."""
    global _runtime

    if _runtime is None:
        _runtime = RuntimeManager().boot()

    return _runtime
