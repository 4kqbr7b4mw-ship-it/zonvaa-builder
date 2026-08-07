"""Run the offline cases through the real v1 manager and guards."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from development_orchestrator.backends import (  # noqa: E402
    BackendConfigurationError,
    OfflineContractBackend,
    OpenAIAgentsBackend,
)
from development_orchestrator.boundary import (  # noqa: E402
    BoundaryGuard,
    BoundaryViolation,
    WorkspaceWriter,
)
from development_orchestrator.orchestrator import DevelopmentOrchestrator  # noqa: E402
from development_orchestrator.schemas import ReviewOutcome, WorkRequest  # noqa: E402
from graders import grade  # noqa: E402


def request(goal: str = "Review a synthetic research state", **changes: object) -> WorkRequest:
    values = {
        "goal": goal,
        "scope": ["synthetic research only"],
        "requested_output": "compact decision brief",
        "allowed_context": ["README.md"],
        "approval_constraints": ["no commit", "no push"],
        "max_iterations": 2,
    }
    values.update(changes)
    return WorkRequest.model_validate(values)


def observe(case: dict) -> dict:
    kind = case["kind"]
    if kind == "invalid_request":
        try:
            request(scope=[])
        except Exception:
            return {"error": "validation"}
        return {"error": None}
    if kind == "boundary":
        try:
            BoundaryGuard(REPOSITORY, ROOT).resolve_write_path(case["target"])
        except BoundaryViolation:
            return {"error": "boundary"}
        return {"error": None}
    if kind == "missing_key":
        previous = os.environ.pop("OPENAI_API_KEY", None)
        try:
            OpenAIAgentsBackend()
        except BackendConfigurationError:
            return {"error": "configuration"}
        finally:
            if previous is not None:
                os.environ["OPENAI_API_KEY"] = previous
        return {"error": None}

    outcomes = [ReviewOutcome(value) for value in case.get("outcomes", ["ACCEPT"])]
    backend = OfflineContractBackend(
        review_outcomes=outcomes,
        force_scope_violation=case.get("scope_violation", False),
        force_missing_evidence=case.get("missing_evidence", False),
        reported_cost_per_call=case.get("reported_cost"),
    )
    item = request(
        goal=case.get("goal", "Review a synthetic research state"),
        max_cost=case.get("max_cost"),
    )
    result = DevelopmentOrchestrator(REPOSITORY, ROOT, backend).run(item)
    run_dir = ROOT / "runs" / result.run_id
    return {
        "status": result.status.value,
        "review_outcome": result.review_outcome.value,
        "artifacts": sorted(path.name for path in run_dir.iterdir() if path.is_file()),
    }


def main() -> int:
    cases = [
        json.loads(line)
        for line in (ROOT / "evals" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results = []
    for case in cases:
        observed = observe(case)
        failures = grade(case, observed)
        results.append(
            {"id": case["id"], "passed": not failures, "failures": failures, "observed": observed}
        )
    writer = WorkspaceWriter(BoundaryGuard(REPOSITORY, ROOT))
    writer.write_json("evals/results/latest.json", {"results": results})
    failed = [result for result in results if not result["passed"]]
    print("{} passed, {} failed".format(len(results) - len(failed), len(failed)))
    for result in failed:
        print("{}: {}".format(result["id"], "; ".join(result["failures"])))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
