import hashlib
from pathlib import Path
import re
from typing import Optional, Tuple

from governance.models import (
    GovernanceBody,
    GovernanceContext,
    NormLevel,
    ProtectionGoal,
    TrustDomain,
)


class GovernanceLoader:
    """Loads and validates the C1-C3 governance contract."""

    DEFAULT_CHARTER = Path(__file__).resolve().parent / "charter.md"
    DEFAULT_OPERATIVE_RULES = (
        Path(__file__).resolve().parent / "operative-rules.md"
    )
    C1_HEADINGS = {
        ProtectionGoal.NO_USER_DATA_SALE: "Kein Verkauf von Nutzerdaten",
        ProtectionGoal.NO_COVERT_THIRD_PARTY_TRAINING: (
            "Kein verdecktes Training Dritter"
        ),
        ProtectionGoal.NO_HIDDEN_MONETIZATION: (
            "Keine verdeckte Monetarisierung"
        ),
        ProtectionGoal.NO_EMOTIONAL_DEPENDENCY_OPTIMIZATION: (
            "Keine emotionale Abhängigkeit"
        ),
        ProtectionGoal.NO_USER_SOVEREIGNTY_BYPASS: (
            "Keine Umgehung der Nutzerhoheit"
        ),
        ProtectionGoal.NO_PORTABILITY_OR_SUNSET_ABANDONMENT: (
            "Keine Aufgabe von Portabilität und Sunset-Fähigkeit"
        ),
        ProtectionGoal.NO_GUARANTEE_WEAKENING: (
            "Keine Aufweichung von Guardian- oder Institution-Garantien"
        ),
    }
    C2_BODY_HEADINGS = {
        GovernanceBody.OPERATIONAL_LEADERSHIP: "Operative Leitung",
        GovernanceBody.TRUST_COUNCIL: "Vertrauensrat",
        GovernanceBody.USER_CONVENTION: "Nutzer-Konvent",
        GovernanceBody.STEWARDSHIP_STRUCTURE: (
            "Eigentums- und Trägerstruktur"
        ),
    }
    C2_DOMAIN_HEADINGS = {
        TrustDomain.DATA: "Daten",
        TrustDomain.MONETIZATION_AND_CONFLICTS: (
            "Monetarisierung und Interessenkonflikte"
        ),
        TrustDomain.EMERGENCY_AND_SECURITY: (
            "Notfall- und Sicherheitslogik"
        ),
        TrustDomain.GUARDIAN_CONTINUITY: "Guardian Continuity",
        TrustDomain.C1_C2_CHANGES: "Änderungen an C1 oder C2",
    }
    C2_REQUIRED_HEADINGS = (
        "Normhierarchie",
        "Prüf- und Vetoverfahren",
        "Transparenz und Audit",
        "Verfassungsänderungen",
        "Whistleblower-Schutz",
    )
    C3_REQUIRED_HEADINGS = (
        "C3-Grenze",
        "Aktive Regelquellen",
        "Arbeits- und Qualitätsregeln",
        "Runtime und Preflight",
        "Änderung und Nachweis",
    )

    def __init__(
        self,
        charter_source: Optional[Path] = None,
        operative_rules_source: Optional[Path] = None,
    ) -> None:
        self.charter_source = (
            charter_source or self.DEFAULT_CHARTER
        ).resolve()
        self.operative_rules_source = (
            operative_rules_source or self.DEFAULT_OPERATIVE_RULES
        ).resolve()

    def load(self, constitution: str) -> GovernanceContext:
        if not isinstance(constitution, str):
            raise TypeError("Constitution must be a string")
        if not constitution.strip():
            raise ValueError("Constitution must not be empty")
        self._version(constitution, "C1")
        self._require_norm_level(constitution, "C1")
        self._require_headings(
            constitution,
            tuple(self.C1_HEADINGS.values()),
            "C1 protection goals",
        )

        charter_bytes, charter = self._read(self.charter_source, "C2")
        operative_bytes, operative = self._read(
            self.operative_rules_source,
            "C3",
        )
        self._require_norm_level(charter, "C2")
        self._require_norm_level(operative, "C3")
        self._require_headings(
            charter,
            tuple(self.C2_BODY_HEADINGS.values())
            + tuple(self.C2_DOMAIN_HEADINGS.values())
            + self.C2_REQUIRED_HEADINGS,
            "C2 governance",
        )
        self._require_headings(
            operative,
            self.C3_REQUIRED_HEADINGS,
            "C3 operative rules",
        )

        return GovernanceContext(
            charter_content=charter,
            charter_source=self.charter_source,
            charter_version=self._version(charter, "C2"),
            charter_hash=hashlib.sha256(charter_bytes).hexdigest(),
            operative_rules_content=operative,
            operative_rules_source=self.operative_rules_source,
            operative_rules_version=self._version(operative, "C3"),
            operative_rules_hash=hashlib.sha256(
                operative_bytes
            ).hexdigest(),
            constitution_hash=hashlib.sha256(
                constitution.encode("utf-8")
            ).hexdigest(),
            norm_levels=tuple(NormLevel),
            protection_goals=tuple(ProtectionGoal),
            bodies=tuple(GovernanceBody),
            trust_domains=tuple(TrustDomain),
        )

    def _read(self, source: Path, level: str) -> Tuple[bytes, str]:
        if not source.is_file():
            raise FileNotFoundError(
                "{} governance contract was not found: {}".format(
                    level,
                    source,
                )
            )
        content_bytes = source.read_bytes()
        try:
            return content_bytes, content_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeError(
                "{} governance contract is not valid UTF-8: {}".format(
                    level,
                    source,
                )
            ) from exc

    def _version(self, content: str, level: str) -> str:
        match = re.search(
            r"^Version:\s*(\S+)\s*$",
            content,
            re.MULTILINE,
        )
        if match is None:
            raise ValueError("{} contract has no version".format(level))
        return match.group(1)

    def _require_norm_level(self, content: str, level: str) -> None:
        pattern = r"^Normstufe:\s*{}\s*$".format(re.escape(level))
        if re.search(pattern, content, re.MULTILINE) is None:
            raise ValueError(
                "{} contract has the wrong norm level".format(level)
            )

    def _require_headings(
        self,
        content: str,
        headings: Tuple[str, ...],
        label: str,
    ) -> None:
        missing = [
            heading
            for heading in headings
            if re.search(
                r"^##\s+{}\s*$".format(re.escape(heading)),
                content,
                re.MULTILINE,
            )
            is None
        ]
        if missing:
            raise ValueError(
                "{} sections are missing: {}".format(
                    label,
                    ", ".join(missing),
                )
            )
