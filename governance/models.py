from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple


class NormLevel(str, Enum):
    C1_CONSTITUTION = "c1_constitution"
    C2_GOVERNANCE_CHARTER = "c2_governance_charter"
    C3_OPERATIVE_RULES = "c3_operative_rules"


class ProtectionGoal(str, Enum):
    NO_USER_DATA_SALE = "no_user_data_sale"
    NO_COVERT_THIRD_PARTY_TRAINING = (
        "no_covert_third_party_training"
    )
    NO_HIDDEN_MONETIZATION = "no_hidden_monetization"
    NO_EMOTIONAL_DEPENDENCY_OPTIMIZATION = (
        "no_emotional_dependency_optimization"
    )
    NO_USER_SOVEREIGNTY_BYPASS = "no_user_sovereignty_bypass"
    NO_PORTABILITY_OR_SUNSET_ABANDONMENT = (
        "no_portability_or_sunset_abandonment"
    )
    NO_GUARANTEE_WEAKENING = "no_guarantee_weakening"


class GovernanceBody(str, Enum):
    OPERATIONAL_LEADERSHIP = "operational_leadership"
    TRUST_COUNCIL = "trust_council"
    USER_CONVENTION = "user_convention"
    STEWARDSHIP_STRUCTURE = "stewardship_structure"


class TrustDomain(str, Enum):
    DATA = "data"
    MONETIZATION_AND_CONFLICTS = "monetization_and_conflicts"
    EMERGENCY_AND_SECURITY = "emergency_and_security"
    GUARDIAN_CONTINUITY = "guardian_continuity"
    C1_C2_CHANGES = "c1_c2_changes"


@dataclass(frozen=True)
class GovernanceContext:
    """Versioned C1-C3 governance proof without operational authority."""

    charter_content: str
    charter_source: Path
    charter_version: str
    charter_hash: str
    operative_rules_content: str
    operative_rules_source: Path
    operative_rules_version: str
    operative_rules_hash: str
    constitution_hash: str
    norm_levels: Tuple[NormLevel, ...]
    protection_goals: Tuple[ProtectionGoal, ...]
    bodies: Tuple[GovernanceBody, ...]
    trust_domains: Tuple[TrustDomain, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "charter_content",
            "charter_version",
            "operative_rules_content",
            "operative_rules_version",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(
                    "GovernanceContext {} must be a string".format(
                        field_name
                    )
                )
            if not value.strip():
                raise ValueError(
                    "GovernanceContext {} must not be empty".format(
                        field_name
                    )
                )
        for field_name in (
            "charter_source",
            "operative_rules_source",
        ):
            if not isinstance(getattr(self, field_name), Path):
                raise TypeError(
                    "GovernanceContext {} must be a Path".format(
                        field_name
                    )
                )
        for field_name in (
            "charter_hash",
            "operative_rules_hash",
            "constitution_hash",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(
                    "GovernanceContext {} must be a string".format(
                        field_name
                    )
                )
            if (
                len(value) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in value
                )
            ):
                raise ValueError(
                    "GovernanceContext {} must be a SHA-256 digest".format(
                        field_name
                    )
                )
        for field_name, enum_type in (
            ("norm_levels", NormLevel),
            ("protection_goals", ProtectionGoal),
            ("bodies", GovernanceBody),
            ("trust_domains", TrustDomain),
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                raise TypeError(
                    "GovernanceContext {} must be a tuple".format(
                        field_name
                    )
                )
            if not all(isinstance(item, enum_type) for item in value):
                raise TypeError(
                    "GovernanceContext {} has invalid values".format(
                        field_name
                    )
                )
            if value != tuple(enum_type):
                raise ValueError(
                    "GovernanceContext {} must contain every value exactly "
                    "once in canonical order".format(field_name)
                )
