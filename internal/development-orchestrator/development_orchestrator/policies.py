"""Closed v1 policy set for routing and stop conditions."""

from __future__ import annotations

import re
from typing import Iterable, List


AGENT_SEQUENCE = ["research_agent", "review_agent"]
EXPECTED_ARTIFACTS = [
    "request.json",
    "plan.json",
    "research.md",
    "review.md",
    "handover.md",
    "result.json",
    "usage.json",
]
FORBIDDEN_GIT_ACTIONS = re.compile(r"\b(commit|push|merge|rebase|stash)\b", re.I)
NEGATED_GIT_ACTIONS = re.compile(
    r"\b(no|kein(?:e[nsrm]?)?|without)\s+(commit|push|merge|rebase|stash)\b",
    re.I,
)


def requested_forbidden_git_action(values: Iterable[str]) -> bool:
    return any(
        FORBIDDEN_GIT_ACTIONS.search(NEGATED_GIT_ACTIONS.sub("", value))
        for value in values
    )


def stop_conditions() -> List[str]:
    return [
        "boundary violation",
        "cost or step budget exceeded",
        "maximum review iterations reached",
        "commit, push, merge, rebase, or stash requested",
        "review escalation requires founder decision",
    ]
