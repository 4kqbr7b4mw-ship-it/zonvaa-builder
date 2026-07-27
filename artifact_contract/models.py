from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from governance import NormLevel


def _require_identifier(value: object, field_name: str) -> str:
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
    return value


def _require_aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must be timezone-aware".format(field_name))
    return value


def _require_identifiers(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    for item in value:
        _require_identifier(item, "{} item".format(field_name))
    if len(value) != len(set(value)):
        raise ValueError("{} must be unique".format(field_name))
    return value


class ArtifactState(str, Enum):
    DRAFT = "draft"
    PERSONAL = "personal"
    READY_FOR_AUTHORIZATION = "ready_for_authorization"
    SHARED = "shared"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class AuthorizationScope(str, Enum):
    READ = "read"
    CONTRIBUTE = "contribute"
    AUTHORIZE_ACTION = "authorize_action"
    MANAGE_SHARING = "manage_sharing"


class AuthorizationStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class HistoryDataClass(str, Enum):
    IMMUTABLE = "immutable"
    RETENTION_REQUIRED = "retention_required"
    DELETABLE = "deletable"
    ANONYMIZABLE = "anonymizable"


class ArtifactTransitionType(str, Enum):
    MAKE_PERSONAL = "make_personal"
    PREPARE_AUTHORIZATION = "prepare_authorization"
    SHARE = "share"
    SUSPEND = "suspend"
    RESTORE = "restore"
    ARCHIVE = "archive"
    EXPIRE = "expire"


@dataclass(frozen=True)
class ArtifactAuthorization:
    authorization_id: str
    subject_id: str
    granted_by: str
    scopes: Tuple[AuthorizationScope, ...]
    purpose: str
    status: AuthorizationStatus
    granted_at: datetime
    revoked_at: Optional[datetime] = None
    binding_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(
            self.authorization_id,
            "ArtifactAuthorization authorization_id",
        )
        _require_identifier(
            self.subject_id,
            "ArtifactAuthorization subject_id",
        )
        _require_identifier(
            self.granted_by,
            "ArtifactAuthorization granted_by",
        )
        _require_identifier(
            self.purpose,
            "ArtifactAuthorization purpose",
        )
        if not isinstance(self.scopes, tuple):
            raise TypeError("ArtifactAuthorization scopes must be a tuple")
        if not self.scopes:
            raise ValueError("ArtifactAuthorization scopes must not be empty")
        if not all(
            isinstance(scope, AuthorizationScope)
            for scope in self.scopes
        ):
            raise TypeError(
                "ArtifactAuthorization scopes must contain "
                "AuthorizationScope values"
            )
        if len(self.scopes) != len(set(self.scopes)):
            raise ValueError(
                "ArtifactAuthorization scopes must be unique"
            )
        if not isinstance(self.status, AuthorizationStatus):
            raise TypeError(
                "ArtifactAuthorization status must be an "
                "AuthorizationStatus"
            )
        _require_aware(
            self.granted_at,
            "ArtifactAuthorization granted_at",
        )
        if self.revoked_at is not None:
            _require_aware(
                self.revoked_at,
                "ArtifactAuthorization revoked_at",
            )
            if self.revoked_at < self.granted_at:
                raise ValueError(
                    "ArtifactAuthorization revoked_at precedes granted_at"
                )
        if (
            self.status is AuthorizationStatus.REVOKED
            and self.revoked_at is None
        ):
            raise ValueError(
                "Revoked authorization requires revoked_at"
            )
        if (
            self.status is not AuthorizationStatus.REVOKED
            and self.revoked_at is not None
        ):
            raise ValueError(
                "Only revoked authorization may contain revoked_at"
            )
        _require_identifiers(
            self.binding_references,
            "ArtifactAuthorization binding_references",
        )


@dataclass(frozen=True)
class ArtifactTransition:
    transition_id: str
    artifact_id: str
    transition_type: ArtifactTransitionType
    from_state: ArtifactState
    to_state: ArtifactState
    authorized_by: str
    occurred_at: datetime
    irreversible: bool
    rule_level: NormLevel
    reason: str

    def __post_init__(self) -> None:
        _require_identifier(
            self.transition_id,
            "ArtifactTransition transition_id",
        )
        _require_identifier(
            self.artifact_id,
            "ArtifactTransition artifact_id",
        )
        _require_identifier(
            self.authorized_by,
            "ArtifactTransition authorized_by",
        )
        _require_identifier(self.reason, "ArtifactTransition reason")
        if not isinstance(
            self.transition_type,
            ArtifactTransitionType,
        ):
            raise TypeError(
                "ArtifactTransition transition_type must be an "
                "ArtifactTransitionType"
            )
        if not isinstance(self.from_state, ArtifactState):
            raise TypeError(
                "ArtifactTransition from_state must be an ArtifactState"
            )
        if not isinstance(self.to_state, ArtifactState):
            raise TypeError(
                "ArtifactTransition to_state must be an ArtifactState"
            )
        if self.from_state is self.to_state:
            raise ValueError(
                "ArtifactTransition must change the artifact state"
            )
        _require_aware(
            self.occurred_at,
            "ArtifactTransition occurred_at",
        )
        if not isinstance(self.irreversible, bool):
            raise TypeError(
                "ArtifactTransition irreversible must be a bool"
            )
        if not isinstance(self.rule_level, NormLevel):
            raise TypeError(
                "ArtifactTransition rule_level must be a NormLevel"
            )
        if self.rule_level is NormLevel.C1_CONSTITUTION:
            raise ValueError(
                "Artifact transitions must be governed by C2 or C3"
            )


@dataclass(frozen=True)
class ArtifactStateContract:
    contract_version: str
    artifact_id: str
    sovereign_id: str
    participant_ids: Tuple[str, ...]
    state: ArtifactState
    history_data_class: HistoryDataClass
    authorizations: Tuple[ArtifactAuthorization, ...] = ()
    transitions: Tuple[ArtifactTransition, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(
            self.contract_version,
            "ArtifactStateContract contract_version",
        )
        _require_identifier(
            self.artifact_id,
            "ArtifactStateContract artifact_id",
        )
        _require_identifier(
            self.sovereign_id,
            "ArtifactStateContract sovereign_id",
        )
        _require_identifiers(
            self.participant_ids,
            "ArtifactStateContract participant_ids",
        )
        if self.sovereign_id in self.participant_ids:
            raise ValueError(
                "ArtifactStateContract sovereign must not be duplicated "
                "as a participant"
            )
        if not isinstance(self.state, ArtifactState):
            raise TypeError(
                "ArtifactStateContract state must be an ArtifactState"
            )
        if not isinstance(
            self.history_data_class,
            HistoryDataClass,
        ):
            raise TypeError(
                "ArtifactStateContract history_data_class must be a "
                "HistoryDataClass"
            )
        if not isinstance(self.authorizations, tuple):
            raise TypeError(
                "ArtifactStateContract authorizations must be a tuple"
            )
        if not all(
            isinstance(item, ArtifactAuthorization)
            for item in self.authorizations
        ):
            raise TypeError(
                "ArtifactStateContract authorizations must contain "
                "ArtifactAuthorization values"
            )
        if not isinstance(self.transitions, tuple):
            raise TypeError(
                "ArtifactStateContract transitions must be a tuple"
            )
        if not all(
            isinstance(item, ArtifactTransition)
            for item in self.transitions
        ):
            raise TypeError(
                "ArtifactStateContract transitions must contain "
                "ArtifactTransition values"
            )
        self._validate_authorizations()
        self._validate_transitions()

    def _validate_authorizations(self) -> None:
        authorization_ids = [
            authorization.authorization_id
            for authorization in self.authorizations
        ]
        if len(authorization_ids) != len(set(authorization_ids)):
            raise ValueError(
                "ArtifactStateContract authorization IDs must be unique"
            )
        participants = set(self.participant_ids)
        for authorization in self.authorizations:
            if authorization.granted_by != self.sovereign_id:
                raise ValueError(
                    "Artifact authorization must be granted by the "
                    "sovereign"
                )
            if authorization.subject_id not in participants:
                raise ValueError(
                    "Artifact authorization subject must be an explicit "
                    "participant"
                )

    def _validate_transitions(self) -> None:
        transition_ids = [
            transition.transition_id
            for transition in self.transitions
        ]
        if len(transition_ids) != len(set(transition_ids)):
            raise ValueError(
                "ArtifactStateContract transition IDs must be unique"
            )
        expected_state = ArtifactState.DRAFT
        previous_time: Optional[datetime] = None
        for transition in self.transitions:
            if transition.artifact_id != self.artifact_id:
                raise ValueError(
                    "Artifact transition belongs to another artifact"
                )
            if transition.from_state is not expected_state:
                raise ValueError(
                    "Artifact transitions must form one ordered chain"
                )
            if (
                previous_time is not None
                and transition.occurred_at < previous_time
            ):
                raise ValueError(
                    "Artifact transitions must be chronological"
                )
            if not self._may_authorize_transition(
                transition.authorized_by,
                transition.occurred_at,
            ):
                raise ValueError(
                    "Artifact transition lacks explicit authorization"
                )
            expected_state = transition.to_state
            previous_time = transition.occurred_at
        if self.state is not expected_state:
            raise ValueError(
                "Artifact state must equal the last audited transition"
            )

    def _may_authorize_transition(
        self,
        actor_id: str,
        occurred_at: datetime,
    ) -> bool:
        if actor_id == self.sovereign_id:
            return True
        return any(
            authorization.subject_id == actor_id
            and AuthorizationScope.AUTHORIZE_ACTION
            in authorization.scopes
            and authorization.granted_at <= occurred_at
            and (
                authorization.status is AuthorizationStatus.ACTIVE
                or (
                    authorization.status
                    is AuthorizationStatus.REVOKED
                    and authorization.revoked_at is not None
                    and occurred_at < authorization.revoked_at
                )
            )
            for authorization in self.authorizations
        )


@dataclass(frozen=True)
class ArtifactContractContext:
    content: str
    source: Path
    version: str
    content_hash: str
    states: Tuple[ArtifactState, ...]
    authorization_scopes: Tuple[AuthorizationScope, ...]
    history_data_classes: Tuple[HistoryDataClass, ...]
    transition_types: Tuple[ArtifactTransitionType, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise TypeError("ArtifactContractContext content must be a string")
        if not self.content.strip():
            raise ValueError(
                "ArtifactContractContext content must not be empty"
            )
        if not isinstance(self.source, Path):
            raise TypeError("ArtifactContractContext source must be a Path")
        _require_identifier(
            self.version,
            "ArtifactContractContext version",
        )
        if (
            not isinstance(self.content_hash, str)
            or len(self.content_hash) != 64
            or any(
                character not in "0123456789abcdef"
                for character in self.content_hash
            )
        ):
            raise ValueError(
                "ArtifactContractContext content_hash must be a SHA-256 "
                "digest"
            )
        for field_name, value, enum_type in (
            ("states", self.states, ArtifactState),
            (
                "authorization_scopes",
                self.authorization_scopes,
                AuthorizationScope,
            ),
            (
                "history_data_classes",
                self.history_data_classes,
                HistoryDataClass,
            ),
            (
                "transition_types",
                self.transition_types,
                ArtifactTransitionType,
            ),
        ):
            if not isinstance(value, tuple):
                raise TypeError(
                    "ArtifactContractContext {} must be a tuple".format(
                        field_name
                    )
                )
            if value != tuple(enum_type):
                raise ValueError(
                    "ArtifactContractContext {} must contain every value "
                    "once in canonical order".format(field_name)
                )
