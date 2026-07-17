from pathlib import Path


class ConstitutionManager:
    """Lädt und verwaltet die ZONVAA Constitution."""

    def __init__(self) -> None:
        self.path = Path("constitution/constitution.md")
        self.content: str | None = None

    def load(self) -> str:
        if not self.path.exists():
            raise FileNotFoundError(
                "Die ZONVAA Constitution wurde nicht gefunden."
            )

        self.content = self.path.read_text(encoding="utf-8")
        return self.content
