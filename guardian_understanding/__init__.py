"""Guardian Understanding Core.

This package builds a transient, typed understanding of a user's words. It
does not decide, route, persist, or activate capabilities.
"""

from guardian_understanding.models import (
    Contradiction,
    Fact,
    FactStatus,
    Goal,
    GoalStatus,
    Hypothesis,
    HypothesisStatus,
    UnderstandingChange,
    UnderstandingOperation,
    UnderstandingOperationType,
    UnderstandingRevision,
    UnderstandingResult,
    UnderstandingState,
    UnderstandingUpdate,
    Unknown,
    UnknownStatus,
)
from guardian_understanding.service import GuardianUnderstandingService
from guardian_understanding.proposal import (
    GuardianUnderstandingProposalService,
    UnderstandingProposal,
    UnderstandingProposalApplication,
    UnderstandingProposalCandidate,
    UnderstandingProposalSelection,
    UnderstandingProposalSet,
)
from guardian_understanding.clarification import (
    ClarificationResolution,
    ClarificationResolutionRequest,
    ClarificationResolutionResult,
    ClarificationResolutionType,
    GuardianClarificationResolutionService,
    ProposalDisposition,
    ProposalDispositionType,
)
from guardian_understanding.answer_boundary import (
    ALWAYS_FORBIDDEN_CAPABILITIES,
    AnswerBoundaryContract,
    AnswerBoundaryValidationError,
    AnswerCapability,
    AnswerOperatingMode,
    GuardianAnswerBoundaryValidator,
)

__all__ = [
    "Contradiction",
    "ClarificationResolution",
    "ClarificationResolutionRequest",
    "ClarificationResolutionResult",
    "ClarificationResolutionType",
    "Fact",
    "FactStatus",
    "Goal",
    "GoalStatus",
    "GuardianUnderstandingService",
    "GuardianUnderstandingProposalService",
    "GuardianClarificationResolutionService",
    "Hypothesis",
    "HypothesisStatus",
    "UnderstandingChange",
    "UnderstandingOperation",
    "UnderstandingOperationType",
    "UnderstandingProposal",
    "UnderstandingProposalApplication",
    "UnderstandingProposalCandidate",
    "UnderstandingProposalSelection",
    "UnderstandingProposalSet",
    "ProposalDisposition",
    "ProposalDispositionType",
    "UnderstandingRevision",
    "UnderstandingResult",
    "UnderstandingState",
    "UnderstandingUpdate",
    "Unknown",
    "UnknownStatus",
    "ALWAYS_FORBIDDEN_CAPABILITIES",
    "AnswerBoundaryContract",
    "AnswerBoundaryValidationError",
    "AnswerCapability",
    "AnswerOperatingMode",
    "GuardianAnswerBoundaryValidator",
]
