# Handover: Validate automated Codex execution bridge

- Timestamp: `2026-07-27T11:30:00+02:00`
- Starting commit: `0245f7775195d6e7a0a18149f61587c00ad03479`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- codex_execution/errors.py
- codex_execution/service.py
- knowledge/adr/ADR-0034-automated-codex-execution-bridge.md
- knowledge/handovers/2026-07-27_09-30-00-000000_Validate-automated-Codex-execution-bridge.json
- knowledge/handovers/2026-07-27_09-30-00-000000_Validate-automated-Codex-execution-bridge.md
- tests/test_codex_execution.py

## Functional changes

- The Bridge now starts Codex CLI 0.145.0 with the approval option in the supported position before the exec subcommand.
- Missing workflow input artifacts without a program context are reported as INPUT_NOT_FOUND instead of EXECUTABLE_NOT_FOUND.
- Post-execution verification failures retain bounded and redacted stdout and stderr from the successful Codex process.

## Technical changes

- A real Watcher run created execution-c8204d2cc7035fce from decision-execution-bridge-read-only-e2e and prompt hash 64d4d8b575c093274198bf7c2c149be1f06e917a282733d88a13ebb033c6cdef.
- The first process start returned exit code 2 with the unsupported exec-level approval argument; the corrected retries returned Codex exit code 0.
- The final record persisted full redacted Codex diagnostics and the expected RESULT_VERIFICATION failure because the read-only order prohibited a result commit.

## Decisions

- Only reproduced Bridge defects were changed; retry, queue and authorization semantics remain unchanged.
- The approval policy remains never and was only moved to the CLI-supported global option position.
- The isolated validation workflow and Execution Report remain local runtime artifacts and are not committed.

## Relevant ADRs

- ADR-0034 Automated Codex Execution Bridge

## Checks

- `python3 -m pytest -q tests/test_codex_execution.py`: **passed** — 24 passed
- `python3 -m pytest -q`: **passed** — 576 passed in 23.57s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert
- `git diff --check`: **passed** — No whitespace errors
- `real Codex execution bridge retry`: **passed** — Codex exit 0; read-only agent status unchanged; expected missing-result-commit failure persisted

## Open risks

- The Codex agent login shell did not inherit the venv-first PATH, so its own Doctor command used system Python; the independent Bridge Doctor check passed with the validated environment.
- The historical workflow workflow-81d7ba505f25f885 has no prompt-proof file and is now correctly reported as missing input during Watcher scans.
- Execution Records retain the latest retry state rather than a separate immutable record for every retry attempt.

## Intentionally not implemented

- No retry or queue change.
- No environment-inheritance contract without a separate security specification.
- No product, architecture workflow, authorization or scheduling change.

## Recommended next step

Define a minimal secret-safe Codex subprocess environment contract before unattended production scheduling is expanded.

## Git status

- Only validated defect fixes, tests, ADR clarification, plan and handover are pending before commit.
