"""Guardian Understanding Core.

This package builds a transient, typed understanding of a user's words. It
does not decide, route, persist, or activate capabilities.
"""

from guardian_understanding.models import (
    Contradiction,
    Fact,
    Goal,
    Hypothesis,
    UnderstandingResult,
    UnderstandingState,
    Unknown,
)
from guardian_understanding.service import GuardianUnderstandingService

__all__ = [
    "Contradiction",
    "Fact",
    "Goal",
    "GuardianUnderstandingService",
    "Hypothesis",
    "UnderstandingResult",
    "UnderstandingState",
    "Unknown",
]
