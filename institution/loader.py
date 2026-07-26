import hashlib
from pathlib import Path
import re
from typing import Optional

from institution.models import (
    InstitutionContext,
    InstitutionGuarantee,
)


class InstitutionLoader:
    """Loads and structurally validates the canonical guarantee contract."""

    DEFAULT_SOURCE = (
        Path(__file__).resolve().parent / "institution.md"
    )
    REQUIRED_HEADINGS = {
        InstitutionGuarantee.GOVERNANCE: "Governance",
        InstitutionGuarantee.USER_SOVEREIGNTY: "Nutzerhoheit",
        InstitutionGuarantee.GUARDIAN_CONTINUITY: "Guardian Continuity",
        InstitutionGuarantee.TRANSPARENCY: "Transparenz",
        InstitutionGuarantee.RESPONSIBILITY: "Verantwortung",
        InstitutionGuarantee.PROTECTION: "Schutz",
        InstitutionGuarantee.DIGNITY: "Würde",
        InstitutionGuarantee.TRUST_MODEL: "Vertrauensmodell",
    }

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> InstitutionContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Der verbindliche Institution-Vertrag wurde nicht gefunden: "
                "{}".format(self.source)
            )
        try:
            content_bytes = self.source.read_bytes()
        except OSError as exc:
            raise OSError(
                "Der verbindliche Institution-Vertrag konnte nicht gelesen "
                "werden: {}".format(self.source)
            ) from exc
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeError(
                "Der verbindliche Institution-Vertrag ist nicht als UTF-8 "
                "lesbar: {}".format(self.source)
            ) from exc

        match = re.search(
            r"^Version:\s*(\S+)\s*$",
            content,
            re.MULTILINE,
        )
        if match is None:
            raise ValueError(
                "Der Institution-Vertrag enthält keine Version."
            )
        missing = [
            heading
            for heading in self.REQUIRED_HEADINGS.values()
            if re.search(
                r"^##\s+{}\s*$".format(re.escape(heading)),
                content,
                re.MULTILINE,
            )
            is None
        ]
        if missing:
            raise ValueError(
                "Der Institution-Vertrag enthält nicht alle Garantien: "
                "{}".format(", ".join(missing))
            )

        return InstitutionContext(
            content=content,
            source=self.source,
            version=match.group(1),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            guarantees=tuple(InstitutionGuarantee),
        )
