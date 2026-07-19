from constitution.manager import ConstitutionManager
from knowledge.manager import KnowledgeManager


class RuntimeManager:
    """Initialisiert und hält den aktuellen Builder-Zustand."""

    def __init__(self) -> None:
        self.constitution: str | None = None
        self.knowledge: dict = {}
    

    def boot(self) -> "RuntimeManager":
        self.constitution = ConstitutionManager().load()
        self.knowledge = KnowledgeManager().load()
        return self
