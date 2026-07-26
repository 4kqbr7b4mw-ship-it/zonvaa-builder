import hashlib
from pathlib import Path
import re
from typing import Optional

from interaction.models import InteractionContext, InteractionPrinciple


class InteractionLoader:
    """Loads and structurally validates the interaction contract."""

    DEFAULT_SOURCE = Path(__file__).resolve().parent / "interaction.md"
    REQUIRED_HEADINGS = {
        InteractionPrinciple.CONVERSATION_ENGINE: "Conversation Engine",
        InteractionPrinciple.INSTITUTION_BOARD: "Institution Board",
        InteractionPrinciple.DUAL_SPACE: "Dual-Space-Interaktion",
        InteractionPrinciple.CONVERSATION_INSTITUTION_TRANSITION: (
            "Conversation → Institution Übergang"
        ),
        InteractionPrinciple.ARTIFACT_ARCHITECTURE: (
            "Artefakt-Architektur"
        ),
        InteractionPrinciple.ARTIFACT_ISLAND: "Artefakt-Insel",
        InteractionPrinciple.AUTHORIZATION_BOUNDARY: (
            "Autorisierungs-Graben"
        ),
        InteractionPrinciple.GUARDIAN_INSTANCE_ISOLATION: (
            "Personengebundene Guardian-Instanzen"
        ),
        InteractionPrinciple.MULTI_PARTY_GRAPH: (
            "Multi-Party Graph Engine"
        ),
        InteractionPrinciple.SHARED_SAFE: "Shared Safe",
        InteractionPrinciple.NEUTRALITY_GUARANTEE: (
            "Neutralitäts-Garantie"
        ),
        InteractionPrinciple.INACTIVITY_IS_SUCCESS: (
            "Inaktivität = Erfolg"
        ),
        InteractionPrinciple.OFFBOARDING_NO_LOCK_IN: (
            "Offboarding ohne Lock-in"
        ),
        InteractionPrinciple.UNAVAILABILITY_CLAUSE: (
            "Unverfügbarkeits-Klausel"
        ),
        InteractionPrinciple.SYSTEM_LIMIT_HANDOVER: (
            "Systemgrenzen und Übergabe"
        ),
    }

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> InteractionContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Der verbindliche Interaction-Vertrag wurde nicht "
                "gefunden: {}".format(self.source)
            )
        try:
            content_bytes = self.source.read_bytes()
        except OSError as exc:
            raise OSError(
                "Der verbindliche Interaction-Vertrag konnte nicht gelesen "
                "werden: {}".format(self.source)
            ) from exc
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeError(
                "Der verbindliche Interaction-Vertrag ist nicht als UTF-8 "
                "lesbar: {}".format(self.source)
            ) from exc

        match = re.search(
            r"^Version:\s*(\S+)\s*$",
            content,
            re.MULTILINE,
        )
        if match is None:
            raise ValueError(
                "Der Interaction-Vertrag enthält keine Version."
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
                "Der Interaction-Vertrag enthält nicht alle Prinzipien: "
                "{}".format(", ".join(missing))
            )

        return InteractionContext(
            content=content,
            source=self.source,
            version=match.group(1),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            principles=tuple(InteractionPrinciple),
        )
