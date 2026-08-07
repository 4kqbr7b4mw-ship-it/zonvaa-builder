from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_eval_matrix_contains_all_required_behavior_cases() -> None:
    cases = [
        json.loads(line)
        for line in (ROOT / "evals" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(cases) == 14
    assert {case["id"] for case in cases} == {
        "normal-research",
        "unclear-scope",
        "missing-evidence",
        "research-expands-scope",
        "review-revision",
        "maximum-iterations",
        "boundary-violation",
        "path-traversal",
        "commit-request",
        "push-request",
        "technical-product-answer",
        "agent-disagreement",
        "budget-limit",
        "missing-api-key",
    }


def test_local_eval_harness_passes() -> None:
    result = subprocess.run(
        [sys.executable, "evals/run_local.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "14 passed, 0 failed" in result.stdout
