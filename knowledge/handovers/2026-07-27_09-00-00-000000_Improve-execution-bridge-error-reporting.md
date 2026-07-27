# Handover: Improve execution bridge error reporting

- Timestamp: `2026-07-27T11:00:00+02:00`
- Starting commit: `e5bbb6b4de47f18785103c921d8177bece8f4ba5`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- codex_execution/README.md
- codex_execution/__init__.py
- codex_execution/errors.py
- codex_execution/models.py
- codex_execution/runner.py
- codex_execution/service.py
- codex_execution/store.py
- codex_execution/watcher.py
- commands/architecture.py
- knowledge/adr/ADR-0034-automated-codex-execution-bridge.md
- knowledge/handovers/2026-07-27_09-00-00-000000_Improve-execution-bridge-error-reporting.json
- knowledge/handovers/2026-07-27_09-00-00-000000_Improve-execution-bridge-error-reporting.md
- tests/test_codex_execution.py

## Functional changes

- Bridge failures now expose the failed step, structured command, cwd, process result and technical cause.
- Watcher and CLI errors retain structured diagnostics instead of reducing failures to exception class names.
- Successful bridge execution and authorization behavior remain unchanged.

## Technical changes

- Execution Record schema 1.1 embeds immutable ExecutionFailure values and reads legacy schema 1.0 records.
- Subprocess start failures, missing resources, non-zero exits, timeouts and internal errors have stable classifications.
- Known secret patterns and explicit sensitive values are redacted and diagnostic output is bounded before persistence.

## Decisions

- The existing Execution Store remains the only failure persistence mechanism.
- Commands remain separate argv values without shell execution.
- stdin and environment variables are excluded from failure reports.

## Relevant ADRs

- ADR-0034 Automated Codex Execution Bridge

## Checks

- `python3 -m pytest -q tests/test_codex_execution.py`: **passed** — 22 passed
- `python3 -m pytest -q`: **passed** — 574 passed in 24.40s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert
- `git diff --check`: **passed** — No whitespace errors

## Open risks

- Pattern-based redaction cannot guarantee detection of arbitrary unknown sensitive free text.
- Execution reports intentionally retain redacted subprocess diagnostics, which still require access control at the local filesystem boundary.

## Intentionally not implemented

- No automatic retry or queue change.
- No authorization-model change.
- No network, Codex login or launchd dependency in tests.

## Recommended next step

Perform a security review of the local execution-report access boundary before expanding Bridge deployment.

## Git status

- Worktree contains only this work package before commit.
