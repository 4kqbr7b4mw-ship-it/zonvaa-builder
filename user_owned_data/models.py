import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Type

from artifact_contract import (
    ArtifactAuthorization,
    AuthorizationScope,
    AuthorizationStatus,
)
from guardian_runtime import RetentionClass


def _text(value: object, field_name: str, maximum: int = 1000) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if (
        not value
        or value != value.strip()
        or "\n" in value
        or "\r" in value
    ):
        raise ValueError(
            "{} must be a trimmed single line".format(field_name)
        )
    if len(value) > maximum or any(ord(char) < 32 for char in value):
        raise ValueError("{} contains invalid content".format(field_name))
    return value


def _aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


def _enum(value: object, expected: Type[Enum], field_name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(
            "{} must be {}".format(field_name, expected.__name__)
        )


def _identifiers(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    for item in value:
        _text(item, "{} item".format(field_name), maximum=255)
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(field_name))
    return value


def _locator(value: object) -> str:
    locator = _text(value, "StorageReference locator")
    lowered = locator.lower()
    if lowered.startswith("data:") or lowered.startswith("base64:"):
        raise ValueError("StorageReference locator cannot embed content")
    if re.match(
        r"^(?:%pdf-|pk\x03\x04|-----begin |<\?xml|<!doctype|"
        r"\{\\rtf|i?vbora|ue[s9])",
        lowered,
    ):
        raise ValueError("StorageReference locator cannot embed content")
    if (
        len(locator) >= 128
        and re.fullmatch(r"[A-Za-z0-9+/=_-]+", locator) is not None
    ):
        raise ValueError("StorageReference locator cannot embed content")
    if ":" not in locator:
        raise ValueError(
            "StorageReference locator must be a logical reference"
        )
    return locator


class StorageProvider(str, Enum):
    LOCAL_FOLDER = "LOCAL_FOLDER"
    NAS = "NAS"
    PRIVATE_CLOUD = "PRIVATE_CLOUD"
    SELF_HOSTED_SERVER = "SELF_HOSTED_SERVER"
    EXTERNAL_CONNECTOR = "EXTERNAL_CONNECTOR"
    UNKNOWN = "UNKNOWN"


class StorageScope(str, Enum):
    OWNER_PRIVATE = "OWNER_PRIVATE"
    AUTHORIZED_SHARED = "AUTHORIZED_SHARED"
    SHARED_SAFE = "SHARED_SAFE"
    EXTERNAL_CONTROLLED = "EXTERNAL_CONTROLLED"
    UNKNOWN = "UNKNOWN"


class StorageAvailability(str, Enum):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    VERIFICATION_REQUIRED = "VERIFICATION_REQUIRED"


class StorageOperation(str, Enum):
    REFERENCE = "REFERENCE"
    READ = "READ"
    COPY = "COPY"
    SYNCHRONIZE = "SYNCHRONIZE"
    EXPORT = "EXPORT"
    DELETE_METADATA = "DELETE_METADATA"
    DELETE_ORIGINAL = "DELETE_ORIGINAL"


class ChecksumAlgorithm(str, Enum):
    SHA256 = "SHA256"
    SHA512 = "SHA512"


@dataclass(frozen=True)
class ChecksumMetadata:
    algorithm: ChecksumAlgorithm
    value: str

    def __post_init__(self) -> None:
        _enum(self.algorithm, ChecksumAlgorithm, "Checksum algorithm")
        _text(self.value, "Checksum value", maximum=128)
        expected = {
            ChecksumAlgorithm.SHA256: 64,
            ChecksumAlgorithm.SHA512: 128,
        }[self.algorithm]
        if (
            len(self.value) != expected
            or re.fullmatch(r"[0-9a-f]+", self.value) is None
        ):
            raise ValueError(
                "Checksum value must be a lowercase hexadecimal digest"
            )

    def to_dict(self) -> Dict[str, str]:
        return {
            "algorithm": self.algorithm.value,
            "value": self.value,
        }


@dataclass(frozen=True)
class ReferenceRetention:
    retention_class: RetentionClass
    retain_until: Optional[datetime] = None
    binding_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _enum(
            self.retention_class,
            RetentionClass,
            "ReferenceRetention retention_class",
        )
        if self.retain_until is not None:
            _aware(
                self.retain_until,
                "ReferenceRetention retain_until",
            )
        _identifiers(
            self.binding_references,
            "ReferenceRetention binding_references",
        )
        if (
            self.retention_class is RetentionClass.KEEP_UNTIL_DATE
            and self.retain_until is None
        ):
            raise ValueError(
                "KEEP_UNTIL_DATE requires retain_until"
            )
        if (
            self.retention_class is not RetentionClass.KEEP_UNTIL_DATE
            and self.retain_until is not None
        ):
            raise ValueError(
                "retain_until is only valid for KEEP_UNTIL_DATE"
            )
        if (
            self.retention_class is RetentionClass.LEGAL_HOLD
            and not self.binding_references
        ):
            raise ValueError("LEGAL_HOLD requires binding references")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "retention_class": self.retention_class.value,
            "retain_until": (
                self.retain_until.isoformat()
                if self.retain_until is not None
                else None
            ),
            "binding_references": list(self.binding_references),
        }


@dataclass(frozen=True)
class ReferenceAuthorization:
    reference_id: str
    authorization: ArtifactAuthorization
    operations: Tuple[StorageOperation, ...]

    def __post_init__(self) -> None:
        _text(
            self.reference_id,
            "ReferenceAuthorization reference_id",
            maximum=255,
        )
        if not isinstance(self.authorization, ArtifactAuthorization):
            raise TypeError(
                "ReferenceAuthorization authorization must be "
                "ArtifactAuthorization"
            )
        if self.authorization.status is not AuthorizationStatus.ACTIVE:
            raise ValueError("ReferenceAuthorization must be active")
        if self.reference_id not in (
            self.authorization.binding_references
        ):
            raise ValueError(
                "ReferenceAuthorization must be bound to its reference"
            )
        if not isinstance(self.operations, tuple) or not self.operations:
            raise ValueError(
                "ReferenceAuthorization operations must be a non-empty tuple"
            )
        if not all(
            isinstance(operation, StorageOperation)
            for operation in self.operations
        ):
            raise TypeError(
                "ReferenceAuthorization operations must contain "
                "StorageOperation values"
            )
        if len(self.operations) != len(set(self.operations)):
            raise ValueError(
                "ReferenceAuthorization operations must be unique"
            )
        if (
            StorageOperation.READ in self.operations
            and AuthorizationScope.READ
            not in self.authorization.scopes
        ):
            raise ValueError("READ operation requires read scope")
        controlled = {
            StorageOperation.COPY,
            StorageOperation.SYNCHRONIZE,
            StorageOperation.EXPORT,
            StorageOperation.DELETE_METADATA,
            StorageOperation.DELETE_ORIGINAL,
        }
        if (
            set(self.operations) & controlled
            and AuthorizationScope.AUTHORIZE_ACTION
            not in self.authorization.scopes
        ):
            raise ValueError(
                "Controlled storage operations require authorize_action scope"
            )

    @property
    def authorization_id(self) -> str:
        return self.authorization.authorization_id

    def allows(
        self,
        operation: StorageOperation,
        owner: str,
        at: datetime,
    ) -> bool:
        _enum(operation, StorageOperation, "operation")
        _text(owner, "owner", maximum=255)
        _aware(at, "authorization time")
        return (
            operation in self.operations
            and self.authorization.status is AuthorizationStatus.ACTIVE
            and self.authorization.subject_id == owner
            and self.authorization.granted_by == owner
            and self.authorization.granted_at <= at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "authorization_id": self.authorization.authorization_id,
            "subject_id": self.authorization.subject_id,
            "granted_by": self.authorization.granted_by,
            "purpose": self.authorization.purpose,
            "operations": [
                operation.value for operation in self.operations
            ],
        }


@dataclass(frozen=True)
class StorageCapability:
    operations: Tuple[StorageOperation, ...]
    verified_at: datetime
    evidence_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.operations, tuple) or not self.operations:
            raise ValueError(
                "StorageCapability operations must be a non-empty tuple"
            )
        if not all(
            isinstance(operation, StorageOperation)
            for operation in self.operations
        ):
            raise TypeError(
                "StorageCapability operations must contain "
                "StorageOperation values"
            )
        if len(self.operations) != len(set(self.operations)):
            raise ValueError("StorageCapability operations must be unique")
        _aware(self.verified_at, "StorageCapability verified_at")
        _text(
            self.evidence_reference,
            "StorageCapability evidence_reference",
            maximum=255,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operations": [
                operation.value for operation in self.operations
            ],
            "verified_at": self.verified_at.isoformat(),
            "evidence_reference": self.evidence_reference,
        }


@dataclass(frozen=True)
class StorageReference:
    reference_id: str
    owner: str
    storage_provider: StorageProvider
    storage_scope: StorageScope
    locator: str
    checksum: Optional[ChecksumMetadata]
    version: int
    created_at: datetime
    last_verified: Optional[datetime]
    authorization: ReferenceAuthorization
    capability: Optional[StorageCapability]
    retention: ReferenceRetention
    availability: StorageAvailability

    def __post_init__(self) -> None:
        _text(self.reference_id, "StorageReference reference_id", maximum=255)
        _text(self.owner, "StorageReference owner", maximum=255)
        _enum(
            self.storage_provider,
            StorageProvider,
            "StorageReference storage_provider",
        )
        _enum(
            self.storage_scope,
            StorageScope,
            "StorageReference storage_scope",
        )
        _locator(self.locator)
        if self.checksum is not None and not isinstance(
            self.checksum,
            ChecksumMetadata,
        ):
            raise TypeError(
                "StorageReference checksum must be ChecksumMetadata or None"
            )
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise TypeError("StorageReference version must be an integer")
        if self.version < 1:
            raise ValueError("StorageReference version must be positive")
        _aware(self.created_at, "StorageReference created_at")
        if self.last_verified is not None:
            _aware(
                self.last_verified,
                "StorageReference last_verified",
            )
            if self.last_verified < self.created_at:
                raise ValueError(
                    "StorageReference last_verified precedes created_at"
                )
        if not isinstance(
            self.authorization,
            ReferenceAuthorization,
        ):
            raise TypeError(
                "StorageReference authorization must be "
                "ReferenceAuthorization"
            )
        if not isinstance(self.retention, ReferenceRetention):
            raise TypeError(
                "StorageReference retention must be ReferenceRetention"
            )
        _enum(
            self.availability,
            StorageAvailability,
            "StorageReference availability",
        )
        if (
            self.availability is StorageAvailability.AVAILABLE
            and self.last_verified is None
        ):
            raise ValueError(
                "AVAILABLE reference requires last_verified"
            )
        if self.authorization.reference_id != self.reference_id:
            raise ValueError(
                "Storage authorization belongs to another reference"
            )
        if StorageOperation.REFERENCE not in self.authorization.operations:
            raise ValueError(
                "Storage reference requires explicit REFERENCE authorization"
            )
        authorization = self.authorization.authorization
        if (
            authorization.subject_id != self.owner
            or authorization.granted_by != self.owner
        ):
            raise ValueError(
                "Storage authorization must belong to the owner"
            )
        if self.capability is not None and not isinstance(
            self.capability,
            StorageCapability,
        ):
            raise TypeError(
                "StorageReference capability must be StorageCapability or None"
            )

    def require_authorization(
        self,
        operation: StorageOperation,
        at: datetime,
    ) -> str:
        _enum(operation, StorageOperation, "operation")
        _aware(at, "operation time")
        if not self.authorization.allows(
            operation,
            self.owner,
            at,
        ):
            raise ValueError(
                "{} is not explicitly authorized".format(operation.value)
            )
        if (
            operation is StorageOperation.DELETE_ORIGINAL
            and (
                self.storage_provider is StorageProvider.UNKNOWN
                or self.availability is not StorageAvailability.AVAILABLE
                or self.capability is None
                or StorageOperation.DELETE_ORIGINAL
                not in self.capability.operations
            )
        ):
            raise ValueError(
                "Original deletion requires verified provider capability"
            )
        return self.authorization.authorization_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "owner": self.owner,
            "storage_provider": self.storage_provider.value,
            "storage_scope": self.storage_scope.value,
            "locator": self.locator,
            "checksum": (
                self.checksum.to_dict()
                if self.checksum is not None
                else None
            ),
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_verified": (
                self.last_verified.isoformat()
                if self.last_verified is not None
                else None
            ),
            "authorization": self.authorization.to_dict(),
            "capability": (
                self.capability.to_dict()
                if self.capability is not None
                else None
            ),
            "retention": self.retention.to_dict(),
            "availability": self.availability.value,
        }


@dataclass(frozen=True)
class UserOwnedDataContractContext:
    content: str
    source: Path
    version: str
    content_hash: str
    storage_providers: Tuple[StorageProvider, ...]
    storage_scopes: Tuple[StorageScope, ...]
    availability_states: Tuple[StorageAvailability, ...]
    storage_operations: Tuple[StorageOperation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError(
                "UserOwnedData contract content must be a string"
            )
        if not self.content.strip() or len(self.content) > 50000:
            raise ValueError(
                "UserOwnedData contract content must not be empty"
            )
        if not isinstance(self.source, Path):
            raise TypeError("UserOwnedData contract source must be a Path")
        _text(self.version, "UserOwnedData contract version", maximum=32)
        if re.fullmatch(r"[0-9a-f]{64}", self.content_hash) is None:
            raise ValueError(
                "UserOwnedData contract content_hash must be SHA-256"
            )
        expected = (
            (self.storage_providers, StorageProvider, "storage_providers"),
            (self.storage_scopes, StorageScope, "storage_scopes"),
            (
                self.availability_states,
                StorageAvailability,
                "availability_states",
            ),
            (
                self.storage_operations,
                StorageOperation,
                "storage_operations",
            ),
        )
        for values, enum_type, field_name in expected:
            if not isinstance(values, tuple) or tuple(enum_type) != values:
                raise ValueError(
                    "{} must contain every stable enum value".format(
                        field_name
                    )
                )
