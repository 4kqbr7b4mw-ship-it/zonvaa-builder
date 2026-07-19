from constitution.manager import ConstitutionManager
from knowledge.manager import KnowledgeManager
from builder.journal import RuntimeJournal


class RuntimeManager:
    """Initialisiert und hält den aktuellen Builder-Zustand."""

    def __init__(self) -> None:
        self.constitution: str | None = None
        self.knowledge: dict = {}
        self.journal = RuntimeJournal()

    def boot(self) -> "RuntimeManager":
        self.constitution = ConstitutionManager().load()
        self.knowledge = KnowledgeManager().load()
        self.journal.log("Runtime gestartet")
        return self
