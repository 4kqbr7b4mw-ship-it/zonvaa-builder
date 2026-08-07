"""Stable behavioral graders for local contract evals."""

from __future__ import annotations

from typing import Any, Dict


def grade(case: Dict[str, Any], observed: Dict[str, Any]) -> list[str]:
    failures = []
    for expected, key in (
        (case.get("expected_status"), "status"),
        (case.get("expected_review"), "review_outcome"),
        (case.get("expected_error"), "error"),
    ):
        if expected is not None and observed.get(key) != expected:
            failures.append("{} expected {!r}, got {!r}".format(key, expected, observed.get(key)))
    if case["kind"] in {"orchestrator", "git_request"}:
        required = {
            "request.json",
            "plan.json",
            "research.md",
            "review.md",
            "handover.md",
            "result.json",
            "usage.json",
        }
        if set(observed.get("artifacts", [])) != required:
            failures.append("run artifacts are incomplete")
    return failures
