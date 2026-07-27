# Handover: Preserve execution attempt history

- Timestamp: `2026-07-27T11:48:13+02:00`
- Starting commit: `4f66a12b21699044d187569246d7bbc3185e7370`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- codex_execution/README.md
- codex_execution/__init__.py
- codex_execution/models.py
- codex_execution/service.py
- codex_execution/store.py
- knowledge/adr/ADR-0034-automated-codex-execution-bridge.md
- knowledge/handovers/2026-07-27_09-48-13-000000_Preserve-execution-attempt-history.json
- knowledge/handovers/2026-07-27_09-48-13-000000_Preserve-execution-attempt-history.md
- tests/test_codex_execution.py

## Functional changes

- Every Bridge start now creates a separately identifiable attempt beginning deterministically at attempt 1.
- Retries append a new attempt while preserving all terminal output, error and verification data from earlier attempts.
- JSON, Markdown and CLI status output expose the complete ordered attempt history while the parent record retains the latest overall status.

## Technical changes

- Execution Record schema 1.2 embeds immutable typed ExecutionAttempt values with deterministic IDs and explicit lifecycle transitions.
- ExecutionStore permits only the active attempt to advance and rejects replacement of terminal attempts.
- Bridge error and redaction data are copied into the attempt that experienced the failure; successful result verification closes that same attempt.
- Schema 1.0 and 1.1 records load with an empty attempt tuple because no historical attempt details can be proven.

## Decisions

- The existing ExecutionRecord and ExecutionStore remain the single persistence and reporting boundary.
- Attempt IDs are derived from execution ID and ordinal number, and attempt order is validated from 1 without gaps.
- Legacy attempt history is empty rather than synthesized from incomplete aggregate fields.

## Relevant ADRs

- ADR-0034 Automated Codex Execution Bridge

## Checks

- `python3 -m pytest -q tests/test_codex_execution.py`: **passed** — 30 passed in 0.63s
- `python3 -m pytest -q`: **passed** — 582 passed in 14.87s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert
- `git diff --check`: **passed** — No whitespace errors

## Open risks

- An abrupt host termination between atomic record writes can leave the newest attempt in its last persisted nonterminal state.
- Legacy records intentionally expose no attempt history because their aggregate state cannot prove individual historical attempts.
- Redacted diagnostics remain local sensitive operational metadata and still depend on repository filesystem access controls.

## Intentionally not implemented

- No authorization, retry-decision, queue, scheduling, prompt, login-shell, PATH or result-commit-verification changes.
- No network, real Codex login or launchd dependency in tests.
- No separate audit store and no migration that invents historical attempts.

## Recommended next step

Review crash recovery for nonterminal attempts before enabling unattended retry across host restarts.

## Git status

- Worktree contains only this work package before commit.
