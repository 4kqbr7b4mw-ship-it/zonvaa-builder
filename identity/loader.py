import hashlib
from pathlib import Path
from typing import Optional

from identity.models import IdentityContext


class IdentityLoader:
    """Loads WHY.md without interpreting or transforming its content."""

    DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "WHY.md"

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> IdentityContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Die verbindliche ZONVAA-Identitätsquelle wurde nicht gefunden: "
                "{}".format(self.source)
            )

        try:
            content_bytes = self.source.read_bytes()
        except OSError as exc:
            raise OSError(
                "Die verbindliche ZONVAA-Identitätsquelle konnte nicht gelesen "
                "werden: {}".format(self.source)
            ) from exc

        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeError(
                "Die verbindliche ZONVAA-Identitätsquelle ist nicht als UTF-8 "
                "lesbar: {}".format(self.source)
            ) from exc

        version = hashlib.sha256(content_bytes).hexdigest()

        return IdentityContext(
            content=content,
            source=self.source,
            version=version,
        )
