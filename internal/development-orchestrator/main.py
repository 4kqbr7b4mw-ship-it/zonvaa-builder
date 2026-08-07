"""Local CLI for the internal development orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from development_orchestrator.backends import (
    BackendConfigurationError,
    OfflineContractBackend,
    OpenAIAgentsBackend,
)
from development_orchestrator.orchestrator import DevelopmentOrchestrator
from development_orchestrator.model_configuration import V1_LIVE_MODEL_CONFIGURATION
from development_orchestrator.schemas import WorkRequest


TOOL_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = TOOL_ROOT.parents[1]


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="ZONVAA internal development orchestrator")
    commands = root.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run a structured research request")
    run.add_argument("--request", required=True, type=Path)
    run.add_argument("--offline", action="store_true", help="explicit contract-only run")
    smoke = commands.add_parser("smoke", help="run the synthetic smoke request")
    smoke.add_argument("--offline", action="store_true", help="explicit contract-only run")
    return root


def load_request(path: Path) -> WorkRequest:
    return WorkRequest.model_validate_json(path.read_text(encoding="utf-8"))


def smoke_request() -> WorkRequest:
    return WorkRequest(
        goal=(
            "Review an existing ZONVAA research state and produce a compact analysis "
            "whose scope, evidence, customer benefit, and simplicity are reviewed."
        ),
        scope=["research and review only", "no repository product changes"],
        requested_output="compact reviewed decision brief",
        allowed_context=["README.md", "knowledge/project/current-product-status.md"],
        approval_constraints=["no commit", "no push"],
        max_iterations=2,
    )


def execute(request: WorkRequest, offline: bool) -> int:
    backend = (
        OfflineContractBackend()
        if offline
        else OpenAIAgentsBackend(V1_LIVE_MODEL_CONFIGURATION)
    )
    result = DevelopmentOrchestrator(REPOSITORY_ROOT, TOOL_ROOT, backend).run(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
    return 0 if result.status.value == "COMPLETED" else 1


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        request = load_request(arguments.request) if arguments.command == "run" else smoke_request()
        return execute(request, arguments.offline)
    except (BackendConfigurationError, FileNotFoundError, OSError, ValidationError) as error:
        print("Configuration error: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
