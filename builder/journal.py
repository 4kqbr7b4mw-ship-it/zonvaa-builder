from datetime import datetime
from pathlib import Path


class RuntimeJournal:
    """Schreibt bestätigte Ereignisse einer Builder-Session."""

    def __init__(self) -> None:
        self.folder = Path("knowledge/protocols")
        self.folder.mkdir(parents=True, exist_ok=True)

        self.file = self.folder / "runtime.md"

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.file.open("a", encoding="utf-8") as f:
            f.write(f"- {timestamp} {message}\n")