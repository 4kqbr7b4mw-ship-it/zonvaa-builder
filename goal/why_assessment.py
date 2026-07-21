from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from goal.models import Goal


class WhyAssessmentStatus(str, Enum):
    ALIGNED = "aligned"
    CONFLICTING = "conflicting"
    NOT_EVALUABLE = "not_evaluable"


class WhyAssessmentReason(str, Enum):
    EXPLICIT_ALIGNMENT_CONFIRMED = "explicit_alignment_confirmed"
    EXPLICIT_CONFLICT_CONFIRMED = "explicit_conflict_confirmed"
    INSUFFICIENT_ASSESSMENT_BASIS = "insufficient_assessment_basis"


_VALID_REASONS = {
    WhyAssessmentStatus.ALIGNED:
        WhyAssessmentReason.EXPLICIT_ALIGNMENT_CONFIRMED,
    WhyAssessmentStatus.CONFLICTING:
        WhyAssessmentReason.EXPLICIT_CONFLICT_CONFIRMED,
    WhyAssessmentStatus.NOT_EVALUABLE:
        WhyAssessmentReason.INSUFFICIENT_ASSESSMENT_BASIS,
}


@dataclass(frozen=True)
class WhyAssessment:
    goal: Goal
    identity_version: str
    status: WhyAssessmentStatus
    reason: WhyAssessmentReason
    evidence: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.goal, Goal):
            raise TypeError("WhyAssessment goal must be a Goal instance")
        if not isinstance(self.identity_version, str):
            raise TypeError("WhyAssessment identity_version must be a string")
        if self.identity_version == "":
            raise ValueError("WhyAssessment identity_version must not be empty")
        if not isinstance(self.status, WhyAssessmentStatus):
            raise TypeError("WhyAssessment status must be WhyAssessmentStatus")
        if not isinstance(self.reason, WhyAssessmentReason):
            raise TypeError("WhyAssessment reason must be WhyAssessmentReason")
        if not isinstance(self.evidence, tuple):
            raise TypeError("WhyAssessment evidence must be a tuple")
        if not all(isinstance(item, str) for item in self.evidence):
            raise TypeError("WhyAssessment evidence items must be strings")
        if self.reason is not _VALID_REASONS[self.status]:
            raise ValueError(
                "Invalid WhyAssessment status/reason combination: {}/{}".format(
                    self.status.value,
                    self.reason.value,
                )
            )
