from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
from typing import Optional, Tuple


class LifeDecisionTopic(str, Enum):
    ESTATE = "estate"
    POWER_OF_ATTORNEY = "power_of_attorney"
    ADVANCE_DIRECTIVE = "advance_directive"
    GUARDIANSHIP = "guardianship"
    EMERGENCY_RESPONSIBILITIES = "emergency_responsibilities"
    FAMILY_ASSETS = "family_assets"
    SUCCESSION = "succession"
    DIGITAL_LEGACY = "digital_legacy"
    PERSONAL_WISHES = "personal_wishes"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ParticipantRole(str, Enum):
    CASE_OWNER = "case_owner"
    FAMILY_MEMBER = "family_member"
    TRUSTED_CONTACT = "trusted_contact"
    PROFESSIONAL_CONTACT = "professional_contact"
    OTHER = "other"


class DocumentType(str, Enum):
    TESTAMENT = "testament"
    POWER_OF_ATTORNEY = "power_of_attorney"
    ADVANCE_DIRECTIVE = "advance_directive"
    GUARDIANSHIP_DIRECTIVE = "guardianship_directive"
    EMERGENCY_INFORMATION = "emergency_information"
    ASSET_OVERVIEW = "asset_overview"
    SUCCESSION_DOCUMENT = "succession_document"
    DIGITAL_LEGACY = "digital_legacy"
    PERSONAL_WISHES = "personal_wishes"
    OTHER = "other"


class ChecksumAlgorithm(str, Enum):
    SHA256 = "sha256"
    SHA512 = "sha512"


class FactConfirmationStatus(str, Enum):
    USER_CONFIRMED = "user_confirmed"
    SOURCE_CONFIRMED = "source_confirmed"
    PROFESSIONALLY_CONFIRMED = "professionally_confirmed"


class OpenQuestionStatus(str, Enum):
    OPEN = "open"
    IN_CLARIFICATION = "in_clarification"
    RESOLVED = "resolved"


class UncertaintySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProfessionalField(str, Enum):
    LEGAL = "legal"
    NOTARIAL = "notarial"
    TAX = "tax"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    OTHER = "other"


class ProfessionalReviewStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DecisionReviewStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    REVIEW_REQUIRED = "review_required"
    PROFESSIONAL_REVIEWS_COMPLETED = "professional_reviews_completed"


class ReviewScheduleStatus(str, Enum):
    SCHEDULED = "scheduled"
    DUE = "due"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def _require_text(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value.strip():
        raise ValueError("{} must not be empty".format(field_name))


def _require_datetime(value: object, field_name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError("{} must be a datetime".format(field_name))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("{} must include timezone information".format(field_name))


def _require_enum(value: object, enum_type: type, field_name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError(
            "{} must be {}".format(field_name, enum_type.__name__)
        )


def _require_tuple_items(
    value: object,
    item_type: type,
    field_name: str,
) -> None:
    if not isinstance(value, tuple):
        raise TypeError("{} must be a tuple".format(field_name))
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError(
            "{} items must be {}".format(field_name, item_type.__name__)
        )


def _require_unique_ids(value: tuple, field_name: str) -> None:
    identifiers = tuple(item.id for item in value)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("{} must contain unique ids".format(field_name))


def _require_storage_reference(value: object) -> None:
    _require_text(value, "DocumentReference storage_reference")
    assert isinstance(value, str)
    if value != value.strip():
        raise ValueError(
            "DocumentReference storage_reference must not have surrounding "
            "whitespace"
        )
    if len(value) > 2048:
        raise ValueError(
            "DocumentReference storage_reference must not contain embedded "
            "content"
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(
            "DocumentReference storage_reference must be a single-line "
            "reference without control characters"
        )
    lowered = value.lower()
    if lowered.startswith("data:"):
        raise ValueError(
            "DocumentReference storage_reference must not be a data URI"
        )
    content_markers = (
        "-----begin ",
        "<?xml",
        "<!doctype ",
        "<html",
        "{\\rtf",
    )
    if lowered.startswith(content_markers):
        raise ValueError(
            "DocumentReference storage_reference must not contain embedded "
            "document content"
        )
    if re.fullmatch(r"[A-Za-z0-9+/]{128,}={0,2}", value):
        raise ValueError(
            "DocumentReference storage_reference must not contain embedded "
            "base64 content"
        )


@dataclass(frozen=True)
class Participant:
    id: str
    label: str
    role: ParticipantRole

    def __post_init__(self) -> None:
        _require_text(self.id, "Participant id")
        _require_text(self.label, "Participant label")
        _require_enum(self.role, ParticipantRole, "Participant role")


@dataclass(frozen=True)
class DocumentReference:
    id: str
    document_type: DocumentType
    storage_reference: str
    analysis_authorized: bool
    checksum: Optional[str] = None
    checksum_algorithm: Optional[ChecksumAlgorithm] = None

    def __post_init__(self) -> None:
        _require_text(self.id, "DocumentReference id")
        _require_enum(
            self.document_type,
            DocumentType,
            "DocumentReference document_type",
        )
        _require_storage_reference(self.storage_reference)
        if not isinstance(self.analysis_authorized, bool):
            raise TypeError(
                "DocumentReference analysis_authorized must be a bool"
            )
        if (self.checksum is None) != (self.checksum_algorithm is None):
            raise ValueError(
                "DocumentReference checksum and checksum_algorithm "
                "must be provided together"
            )
        if self.checksum is not None:
            _require_text(self.checksum, "DocumentReference checksum")
            _require_enum(
                self.checksum_algorithm,
                ChecksumAlgorithm,
                "DocumentReference checksum_algorithm",
            )
            expected_length = {
                ChecksumAlgorithm.SHA256: 64,
                ChecksumAlgorithm.SHA512: 128,
            }[self.checksum_algorithm]
            if (
                len(self.checksum) != expected_length
                or not re.fullmatch(r"[0-9a-fA-F]+", self.checksum)
            ):
                raise ValueError(
                    "DocumentReference checksum must be a hexadecimal "
                    "digest matching checksum_algorithm"
                )


@dataclass(frozen=True)
class VerifiedFact:
    id: str
    statement: str
    source: str
    confirmation_status: FactConfirmationStatus
    confirmed_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.id, "VerifiedFact id")
        _require_text(self.statement, "VerifiedFact statement")
        _require_text(self.source, "VerifiedFact source")
        _require_enum(
            self.confirmation_status,
            FactConfirmationStatus,
            "VerifiedFact confirmation_status",
        )
        _require_datetime(self.confirmed_at, "VerifiedFact confirmed_at")


@dataclass(frozen=True)
class OpenQuestion:
    id: str
    question: str
    responsible: str
    status: OpenQuestionStatus
    required_clarification: str

    def __post_init__(self) -> None:
        _require_text(self.id, "OpenQuestion id")
        _require_text(self.question, "OpenQuestion question")
        _require_text(self.responsible, "OpenQuestion responsible")
        _require_enum(self.status, OpenQuestionStatus, "OpenQuestion status")
        _require_text(
            self.required_clarification,
            "OpenQuestion required_clarification",
        )


@dataclass(frozen=True)
class Uncertainty:
    id: str
    description: str
    severity: UncertaintySeverity
    cause: str
    possible_impact: str

    def __post_init__(self) -> None:
        _require_text(self.id, "Uncertainty id")
        _require_text(self.description, "Uncertainty description")
        _require_enum(
            self.severity,
            UncertaintySeverity,
            "Uncertainty severity",
        )
        _require_text(self.cause, "Uncertainty cause")
        _require_text(self.possible_impact, "Uncertainty possible_impact")


@dataclass(frozen=True)
class ProfessionalReviewRequirement:
    id: str
    field: ProfessionalField
    reason: str
    status: ProfessionalReviewStatus
    zonvaa_does_not_replace_review: bool = True

    def __post_init__(self) -> None:
        _require_text(self.id, "ProfessionalReviewRequirement id")
        _require_enum(
            self.field,
            ProfessionalField,
            "ProfessionalReviewRequirement field",
        )
        _require_text(self.reason, "ProfessionalReviewRequirement reason")
        _require_enum(
            self.status,
            ProfessionalReviewStatus,
            "ProfessionalReviewRequirement status",
        )
        if self.zonvaa_does_not_replace_review is not True:
            raise ValueError(
                "ZONVAA must not be represented as replacing "
                "professional review"
            )


@dataclass(frozen=True)
class DecisionRecord:
    id: str
    decision: str
    rationale: str
    used_fact_ids: Tuple[str, ...]
    open_uncertainty_ids: Tuple[str, ...]
    professional_review_ids: Tuple[str, ...]
    review_status: DecisionReviewStatus
    decided_at: datetime
    version: str

    def __post_init__(self) -> None:
        _require_text(self.id, "DecisionRecord id")
        _require_text(self.decision, "DecisionRecord decision")
        _require_text(self.rationale, "DecisionRecord rationale")
        _require_tuple_items(
            self.used_fact_ids,
            str,
            "DecisionRecord used_fact_ids",
        )
        _require_tuple_items(
            self.open_uncertainty_ids,
            str,
            "DecisionRecord open_uncertainty_ids",
        )
        _require_tuple_items(
            self.professional_review_ids,
            str,
            "DecisionRecord professional_review_ids",
        )
        for field_name, identifiers in (
            ("DecisionRecord used_fact_ids", self.used_fact_ids),
            (
                "DecisionRecord open_uncertainty_ids",
                self.open_uncertainty_ids,
            ),
            (
                "DecisionRecord professional_review_ids",
                self.professional_review_ids,
            ),
        ):
            for identifier in identifiers:
                _require_text(identifier, field_name)
            if len(identifiers) != len(set(identifiers)):
                raise ValueError("{} must be unique".format(field_name))
        _require_enum(
            self.review_status,
            DecisionReviewStatus,
            "DecisionRecord review_status",
        )
        _require_datetime(self.decided_at, "DecisionRecord decided_at")
        _require_text(self.version, "DecisionRecord version")

        if (
            self.review_status
            is DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
            and not self.professional_review_ids
        ):
            raise ValueError(
                "DecisionRecord must reference professional reviews "
                "when their completion is recorded"
            )


@dataclass(frozen=True)
class ReviewSchedule:
    id: str
    next_review_at: datetime
    trigger: str
    status: ReviewScheduleStatus

    def __post_init__(self) -> None:
        _require_text(self.id, "ReviewSchedule id")
        _require_datetime(self.next_review_at, "ReviewSchedule next_review_at")
        _require_text(self.trigger, "ReviewSchedule trigger")
        _require_enum(
            self.status,
            ReviewScheduleStatus,
            "ReviewSchedule status",
        )


@dataclass(frozen=True)
class LifeDecisionCase:
    id: str
    title: str
    topic: LifeDecisionTopic
    status: CaseStatus
    owner: str
    created_at: datetime
    updated_at: datetime
    participants: Tuple[Participant, ...] = ()
    document_references: Tuple[DocumentReference, ...] = ()
    verified_facts: Tuple[VerifiedFact, ...] = ()
    open_questions: Tuple[OpenQuestion, ...] = ()
    uncertainties: Tuple[Uncertainty, ...] = ()
    professional_reviews: Tuple[ProfessionalReviewRequirement, ...] = ()
    decisions: Tuple[DecisionRecord, ...] = ()
    review_schedules: Tuple[ReviewSchedule, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.id, "LifeDecisionCase id")
        _require_text(self.title, "LifeDecisionCase title")
        _require_enum(self.topic, LifeDecisionTopic, "LifeDecisionCase topic")
        _require_enum(self.status, CaseStatus, "LifeDecisionCase status")
        _require_text(self.owner, "LifeDecisionCase owner")
        _require_datetime(self.created_at, "LifeDecisionCase created_at")
        _require_datetime(self.updated_at, "LifeDecisionCase updated_at")
        if self.updated_at < self.created_at:
            raise ValueError(
                "LifeDecisionCase updated_at must not precede created_at"
            )

        for value, item_type, field_name in (
            (self.participants, Participant, "LifeDecisionCase participants"),
            (
                self.document_references,
                DocumentReference,
                "LifeDecisionCase document_references",
            ),
            (
                self.verified_facts,
                VerifiedFact,
                "LifeDecisionCase verified_facts",
            ),
            (
                self.open_questions,
                OpenQuestion,
                "LifeDecisionCase open_questions",
            ),
            (
                self.uncertainties,
                Uncertainty,
                "LifeDecisionCase uncertainties",
            ),
            (
                self.professional_reviews,
                ProfessionalReviewRequirement,
                "LifeDecisionCase professional_reviews",
            ),
            (self.decisions, DecisionRecord, "LifeDecisionCase decisions"),
            (
                self.review_schedules,
                ReviewSchedule,
                "LifeDecisionCase review_schedules",
            ),
        ):
            _require_tuple_items(value, item_type, field_name)
            _require_unique_ids(value, field_name)

        fact_ids = {fact.id for fact in self.verified_facts}
        uncertainty_ids = {
            uncertainty.id for uncertainty in self.uncertainties
        }
        review_by_id = {
            review.id: review for review in self.professional_reviews
        }
        for decision in self.decisions:
            missing_fact_ids = set(decision.used_fact_ids) - fact_ids
            missing_uncertainty_ids = (
                set(decision.open_uncertainty_ids) - uncertainty_ids
            )
            missing_review_ids = (
                set(decision.professional_review_ids) - set(review_by_id)
            )
            if missing_fact_ids:
                raise ValueError(
                    "DecisionRecord references facts outside "
                    "LifeDecisionCase"
                )
            if missing_uncertainty_ids:
                raise ValueError(
                    "DecisionRecord references uncertainties outside "
                    "LifeDecisionCase"
                )
            if missing_review_ids:
                raise ValueError(
                    "DecisionRecord references professional reviews outside "
                    "LifeDecisionCase"
                )
            if (
                decision.review_status
                is DecisionReviewStatus.PROFESSIONAL_REVIEWS_COMPLETED
                and any(
                    review_by_id[review_id].status
                    is not ProfessionalReviewStatus.COMPLETED
                    for review_id in decision.professional_review_ids
                )
            ):
                raise ValueError(
                    "DecisionRecord cannot record completed professional "
                    "reviews while referenced reviews are open"
                )
