from datetime import datetime
from pathlib import Path


class RuntimeJournal:
    """Schreibt bestätigte Ereignisse einer Builder-Session."""

    def __init__(self) -> None:
        self.folder = Path("knowledge/protocols")
        self.folder.mkdir(parents=True, exist_ok=True)

        self.file = (
            self.folder /
            f"{datetime.now():%Y-%m-%d_%H-%M-%S}_runtime.md"
        )

    def log(self, message: str) -> None:
        with self.file.open("a", encoding="utf-8") as f:
            f.write(f"- {datetime.now():%H:%M:%S} {message}\n")
