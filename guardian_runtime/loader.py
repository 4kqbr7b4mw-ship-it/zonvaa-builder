import hashlib
import re
from pathlib import Path
from typing import Optional

from guardian_runtime.models import (
    Confidence,
    GuardianRuntimeContractContext,
    KnowledgeType,
    MemoryScope,
    RetentionClass,
    TransitionType,
    Validity,
    VerificationStatus,
)


class GuardianRuntimeContractLoader:
    """Loads the static contract without loading personal knowledge."""

    DEFAULT_SOURCE = Path(__file__).resolve().parent / "contract.md"
    REQUIRED_HEADINGS = (
        "Vertragsgrenze",
        "Wissen und Provenienz",
        "Zeit und Widerspruch",
        "Guardian Memory",
        "Retention und Forgetting",
        "Personen- und Autorisierungsgrenze",
        "Zustandsübergänge",
        "Snapshot und Integrität",
        "Nicht implementiert",
    )

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> GuardianRuntimeContractContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Guardian Runtime contract was not found: {}".format(
                    self.source
                )
            )
        content_bytes = self.source.read_bytes()
        content = content_bytes.decode("utf-8")
        version = re.search(
            r"^Version:\s*(\S+)\s*$",
            content,
            re.MULTILINE,
        )
        if version is None:
            raise ValueError("Guardian Runtime contract has no version")
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
                "Guardian Runtime contract is incomplete: {}".format(
                    ", ".join(missing)
                )
            )
        return GuardianRuntimeContractContext(
            content=content,
            source=self.source,
            version=version.group(1),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            knowledge_types=tuple(KnowledgeType),
            verification_statuses=tuple(VerificationStatus),
            confidence_levels=tuple(Confidence),
            validity_states=tuple(Validity),
            retention_classes=tuple(RetentionClass),
            memory_scopes=tuple(MemoryScope),
            transition_types=tuple(TransitionType),
        )
