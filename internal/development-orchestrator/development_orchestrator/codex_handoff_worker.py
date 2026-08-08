"""Detached one-shot worker for an already validated Codex handoff."""

from __future__ import annotations

import argparse
from pathlib import Path

from .codex_handoff import CodexHandoffError, CodexHandoffService


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tool-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--authorized-branch", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = _arguments()
    try:
        service = CodexHandoffService(
            Path(arguments.repository),
            Path(arguments.tool_root),
            authorized_branch=arguments.authorized_branch,
        )
        record = service.run_job(arguments.run_id, arguments.job_id)
    except CodexHandoffError:
        return 1
    return 0 if record.status.value == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
