import hashlib
from pathlib import Path
import re
from typing import Optional

from artifact_contract.models import (
    ArtifactContractContext,
    ArtifactState,
    ArtifactTransitionType,
    AuthorizationScope,
    HistoryDataClass,
)


class ArtifactContractLoader:
    """Loads the typed artifact contract without executing transitions."""

    DEFAULT_SOURCE = Path(__file__).resolve().parent / "contract.md"
    REQUIRED_HEADINGS = (
        "Vertragsgrenze",
        "Artefaktzustände",
        "Hoheit und Beteiligung",
        "Autorisierung",
        "Zustandsübergänge",
        "Historienklassen",
        "Normhierarchie",
        "Ausdrücklich nicht festgelegt",
    )

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> ArtifactContractContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Der Artefaktvertrag wurde nicht gefunden: {}".format(
                    self.source
                )
            )
        try:
            content_bytes = self.source.read_bytes()
        except OSError as exc:
            raise OSError(
                "Der Artefaktvertrag konnte nicht gelesen werden: {}".format(
                    self.source
                )
            ) from exc
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeError(
                "Der Artefaktvertrag ist nicht als UTF-8 lesbar: {}".format(
                    self.source
                )
            ) from exc
        version_match = re.search(
            r"^Version:\s*(\S+)\s*$",
            content,
            re.MULTILINE,
        )
        if version_match is None:
            raise ValueError("Der Artefaktvertrag enthält keine Version.")
        missing = [
            heading
            for heading in self.REQUIRED_HEADINGS
            if re.search(
                r"^##\s+{}\s*$".format(re.escape(heading)),
                content,
                re.MULTILINE,
            )
            is None
        ]
        if missing:
            raise ValueError(
                "Der Artefaktvertrag ist unvollständig: {}".format(
                    ", ".join(missing)
                )
            )
        return ArtifactContractContext(
            content=content,
            source=self.source,
            version=version_match.group(1),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            states=tuple(ArtifactState),
            authorization_scopes=tuple(AuthorizationScope),
            history_data_classes=tuple(HistoryDataClass),
            transition_types=tuple(ArtifactTransitionType),
        )
