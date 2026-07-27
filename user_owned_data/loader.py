import hashlib
import re
from pathlib import Path
from typing import Optional

from user_owned_data.models import (
    StorageAvailability,
    StorageOperation,
    StorageProvider,
    StorageScope,
    UserOwnedDataContractContext,
)


class UserOwnedDataContractLoader:
    """Loads the static contract without accessing a User Vault."""

    DEFAULT_SOURCE = Path(__file__).resolve().parent / "contract.md"
    REQUIRED_HEADINGS = (
        "Architekturgrenze",
        "Eigentum und Kontrolle",
        "Referenzmodell",
        "Provider-Neutralität",
        "Autorisierung",
        "Synchronisation und Kopien",
        "Löschung und Retention",
        "Offlinefähigkeit",
        "Runtime- und Knowledge-Grenze",
        "Nicht implementiert",
    )

    def __init__(self, source: Optional[Path] = None) -> None:
        self.source = (source or self.DEFAULT_SOURCE).resolve()

    def load(self) -> UserOwnedDataContractContext:
        if not self.source.is_file():
            raise FileNotFoundError(
                "User-Owned Data contract was not found: {}".format(
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
            raise ValueError("User-Owned Data contract has no version")
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
                "User-Owned Data contract is incomplete: {}".format(
                    ", ".join(missing)
                )
            )
        return UserOwnedDataContractContext(
            content=content,
            source=self.source,
            version=version.group(1),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            storage_providers=tuple(StorageProvider),
            storage_scopes=tuple(StorageScope),
            availability_states=tuple(StorageAvailability),
            storage_operations=tuple(StorageOperation),
        )
