# Handover: Authorized workflow preparation baseline v1

- Timestamp: `2026-07-30T19:02:31+02:00`
- Starting commit: `d2a63bdce3dc6ed228d2b2a7506cbd352d737033`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- codex_execution/README.md
- codex_execution/__init__.py
- codex_execution/orchestration.py
- codex_execution/preparation.py
- commands/architecture.py
- knowledge/adr/ADR-0045-authorized-workflow-preparation-baseline.md
- tests/test_codex_execution_orchestration.py
- tests/test_codex_execution_preparation.py
- knowledge/handovers/2026-07-30_17-02-31-000000_Authorized-workflow-preparation-baseline-v1.json
- knowledge/handovers/2026-07-30_17-02-31-000000_Authorized-workflow-preparation-baseline-v1.md

## Functional changes

- Added an official command to capture an authorized workflow preparation baseline.
- Allowed orchestration from a dirty working tree only when every existing change exactly matches the immutable baseline.
- Separated protected workflow preparation files from Codex result changes.

## Technical changes

- Added frozen typed baseline, file, assessment, state and error contracts.
- Bound baseline identity and SHA-256 hashes to workflow, architecture run, authorization, repository, branch and base commit.
- Blocked staged, foreign, missing and modified preparation artifacts before process start and during result validation.

## Decisions

- Preparation baselines are technical runtime evidence under the ignored executions area.
- Only new untracked files derived from the concrete workflow manifest are accepted in v1.
- Read-only preparation status never creates or mutates a baseline.

## Relevant ADRs

- ADR-0041
- ADR-0042
- ADR-0043
- ADR-0044
- ADR-0045

## Checks

- `python3 -m pytest -q tests/test_codex_execution_preparation.py tests/test_codex_execution_orchestration.py`: **passed** — 59 passed in 5.50s
- `python3 -m pytest -q`: **passed** — 747 passed in 44.30s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI works
- `git diff --check`: **passed** — No whitespace errors

## Open risks

- Preparation v1 intentionally rejects renamed or quoted Git porcelain paths instead of interpreting them.
- Preparation v1 accepts only new workflow artifacts and does not authorize modifications to existing handovers or governance files.
- No productive orchestration has yet exercised the baseline contract.

## Intentionally not implemented

- No real Codex execution or productive orchestration.
- No productive preparation baseline.
- No automatic baseline update, commit, push or historical migration.

## Recommended next step

Run a separately authorized read-only productive orchestration using create_commit false and a freshly prepared workflow baseline.

## Git status

- Work-package changes and handover files pending the authorized commit.
