from pathlib import Path
from typing import Optional

from constitution.manager import ConstitutionManager
from goal.engine import GoalEngine
from identity import IdentityContext, IdentityLoader
from institution import InstitutionContext, InstitutionLoader
from knowledge.manager import KnowledgeManager
from builder.project_state import ProjectState


class RuntimeManager:
    """Initialisiert und hält den aktuellen Builder-Zustand."""

    def __init__(self) -> None:
        self.project_root = Path.cwd().resolve()
        self.identity_context: Optional[IdentityContext] = None
        self.institution_context: Optional[InstitutionContext] = None
        self.constitution: Optional[str] = None
        self.knowledge: dict = {}
        self.latest_session: Optional[Path] = None
        self.latest_session_content: str = ""
        self.latest_handover: Optional[Path] = None
        self.latest_context: Optional[Path] = None
        self.latest_context_content: str = ""
        self.project_state: dict = {}
        self.verified_facts: dict = {}
        self.goal_engine: Optional[GoalEngine] = None

    def boot(self) -> "RuntimeManager":
        knowledge_manager = KnowledgeManager()

        self.identity_context = IdentityLoader().load()
        self.institution_context = InstitutionLoader().load()
        self.constitution = ConstitutionManager().load()
        self.knowledge = knowledge_manager.load()
        self.latest_session = knowledge_manager.latest_session()
        self.latest_handover = knowledge_manager.latest_handover()
        context_candidates = [
            path
            for path in (self.latest_session, self.latest_handover)
            if path is not None
        ]
        self.latest_context = max(
            context_candidates,
            key=lambda path: path.stat().st_mtime,
            default=None,
        )

        if self.latest_session is not None:
            self.latest_session_content = self.latest_session.read_text(
                encoding="utf-8",
                errors="replace",
            )
        if self.latest_context is not None:
            self.latest_context_content = self.latest_context.read_text(
                encoding="utf-8",
                errors="replace",
            )

        self.project_state = ProjectState().collect()
        self.verified_facts = self.project_state.get("verified_facts", {})
        self.goal_engine = GoalEngine()

        return self



_runtime: Optional[RuntimeManager] = None


def get_runtime() -> RuntimeManager:
    """Liefert die einmalig initialisierte Builder-Runtime."""
    global _runtime

    if _runtime is None:
        _runtime = RuntimeManager().boot()

    return _runtime
