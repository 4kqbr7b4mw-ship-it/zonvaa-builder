"""Immutable, non-personal B2 provider identity descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple


class B2ProviderClass(str, Enum):
    INSTITUTIONAL_SERVICE_UNIT = "INSTITUTIONAL_SERVICE_UNIT"
    PROFESSIONAL_ROLE_UNIT = "PROFESSIONAL_ROLE_UNIT"
    MODEL_SERVICE_UNIT = "MODEL_SERVICE_UNIT"
    RESEARCH_SERVICE_UNIT = "RESEARCH_SERVICE_UNIT"
    TECHNICAL_TOOL_SERVICE_UNIT = "TECHNICAL_TOOL_SERVICE_UNIT"


class B2ResponsibilityArea(str, Enum):
    GENERAL_ORIENTATION_SUPPORT = "GENERAL_ORIENTATION_SUPPORT"
    PERSONAL_PREPARATION_SUPPORT = "PERSONAL_PREPARATION_SUPPORT"
    PROFESSIONAL_REVIEW_PREPARATION_SUPPORT = (
        "PROFESSIONAL_REVIEW_PREPARATION_SUPPORT"
    )
    SOURCE_REFERENCE_SUPPORT = "SOURCE_REFERENCE_SUPPORT"


class B2CapabilityDescriptor(str, Enum):
    GENERAL_ORIENTATION_SERVICE_DESCRIPTOR = (
        "GENERAL_ORIENTATION_SERVICE_DESCRIPTOR"
    )
    PERSONAL_PREPARATION_SERVICE_DESCRIPTOR = (
        "PERSONAL_PREPARATION_SERVICE_DESCRIPTOR"
    )
    PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR = (
        "PROFESSIONAL_REVIEW_PREPARATION_DESCRIPTOR"
    )
    SOURCE_REFERENCE_SERVICE_DESCRIPTOR = "SOURCE_REFERENCE_SERVICE_DESCRIPTOR"


@dataclass(frozen=True)
class B2ProviderIdentityId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "identity_id", "b2-provider-identity:")


@dataclass(frozen=True)
class B2InstitutionalSourceId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "institutional_source_id", "institutional-source:")


@dataclass(frozen=True)
class B2GovernanceDecisionId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "governance_decision_id", "governance-decision:")


@dataclass(frozen=True)
class B2RegistrationBasisReference:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "registration_basis", "registration-basis:")


@dataclass(frozen=True)
class B2NonPersonalReferenceId:
    value: str

    def __post_init__(self) -> None:
        _reference(self.value, "reference_id", "non-personal-reference:")


@dataclass(frozen=True)
class B2ProviderProvenance:
    institutional_source_id: B2InstitutionalSourceId
    governance_decision_id: B2GovernanceDecisionId
    registration_basis: B2RegistrationBasisReference
    reference_id: B2NonPersonalReferenceId
    created_at: datetime

    def __post_init__(self) -> None:
        _instance(
            self.institutional_source_id,
            B2InstitutionalSourceId,
            "institutional_source_id",
        )
        _instance(
            self.governance_decision_id,
            B2GovernanceDecisionId,
            "governance_decision_id",
        )
        _instance(
            self.registration_basis,
            B2RegistrationBasisReference,
            "registration_basis",
        )
        _instance(self.reference_id, B2NonPersonalReferenceId, "reference_id")
        _aware(self.created_at, "created_at")


@dataclass(frozen=True)
class B2ProviderIdentity:
    identity_id: B2ProviderIdentityId
    provider_class: B2ProviderClass
    responsibility_areas: Tuple[B2ResponsibilityArea, ...]
    capability_descriptors: Tuple[B2CapabilityDescriptor, ...]
    provenance: B2ProviderProvenance
    previous_identity_reference: Optional[B2ProviderIdentityId] = None

    def __post_init__(self) -> None:
        _instance(self.identity_id, B2ProviderIdentityId, "identity_id")
        _enum(self.provider_class, B2ProviderClass, "provider_class")
        _typed_unique_nonempty(
            self.responsibility_areas,
            B2ResponsibilityArea,
            "responsibility_areas",
        )
        _typed_unique_nonempty(
            self.capability_descriptors,
            B2CapabilityDescriptor,
            "capability_descriptors",
        )
        _instance(self.provenance, B2ProviderProvenance, "provenance")
        if self.previous_identity_reference is not None:
            _instance(
                self.previous_identity_reference,
                B2ProviderIdentityId,
                "previous_identity_reference",
            )
            if self.previous_identity_reference == self.identity_id:
                raise ValueError(
                    "previous_identity_reference must differ from identity_id"
                )


def _reference(value: object, name: str, prefix: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("{} must be a non-empty machine reference".format(name))
    if not value.startswith(prefix) or len(value) == len(prefix):
        raise ValueError("{} has an invalid reference family".format(name))
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-._:")
    if any(character not in allowed for character in value):
        raise ValueError("{} must be a non-personal machine reference".format(name))
    payload = value[len(prefix) :]
    segments = set(payload.replace("_", "-").replace(":", "-").split("-"))
    if segments.intersection(
        {"person", "personal", "human", "name", "email", "contact", "account"}
    ):
        raise ValueError("{} must not identify a natural person".format(name))


def _aware(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(name))


def _enum(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _instance(value: object, expected: type, name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError("{} must be a {}".format(name, expected.__name__))


def _typed_unique_nonempty(values: object, expected: type, name: str) -> None:
    if not isinstance(values, tuple):
        raise TypeError("{} must be a tuple".format(name))
    if not values:
        raise ValueError("{} must not be empty".format(name))
    if any(not isinstance(value, expected) for value in values):
        raise TypeError("{} contains an invalid value".format(name))
    if len(values) != len(set(values)):
        raise ValueError("{} must not contain duplicates".format(name))
