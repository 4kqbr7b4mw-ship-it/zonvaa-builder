# Handover: Version review decisions and supersede workflows

- Timestamp: `2026-07-30T13:10:00+00:00`
- Starting commit: `d8b4c3d40f8cb9dc2f8c3b59e4935cf469c0dbe7`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- architecture_integrator/__init__.py
- architecture_integrator/operations.py
- architecture_integrator/review_decision.py
- architecture_integrator/supersession.py
- builder/main.py
- commands/architecture.py
- knowledge/adr/ADR-0040-versioned-review-decisions-and-workflow-supersession.md
- knowledge/architecture_review_decisions/review-7c594772df053366.json
- knowledge/architecture_review_decisions/review-223f811d69329e77.json
- knowledge/architecture_workflow_supersessions/workflow-cc69d796a87b2cad.json
- knowledge/handovers/2026-07-30_13-10-00-000000_Version-review-decisions-and-supersede-workflows.json
- knowledge/handovers/2026-07-30_13-10-00-000000_Version-review-decisions-and-supersede-workflows.md
- tests/test_architecture_operations.py

## Functional changes

- Chief Architect implementation-review decisions are now persisted in a normal versioned review-centered knowledge area.
- Explicit workflow supersession resolves duplicate topics without time, commit, status, or file-age heuristics.
- Operations status exposes superseded state, canonical workflow, supersession ID, and versioned decision paths.

## Technical changes

- Added immutable schema-versioned workflow supersession model and atomic store.
- Added explicit legacy review-decision migration while preserving decision IDs, timestamps, reasons, and references.
- Added exact-before-partial topic resolution, structured ambiguity candidates, and decision-only checkout reconstruction.

## Decisions

- ADR-0039 remains valid while ADR-0040 corrects its physical canonical decision path.
- workflow-cc69d796a87b2cad is explicitly superseded by workflow-43af40b39b5593f6 for their shared topic.
- Runtime execution and attempt trees remain ignored and are not opened through a broad Git exception.

## Relevant ADRs

- ADR-0038
- ADR-0039
- ADR-0040

## Checks

- `python3 -m pytest -q tests/test_architecture_operations.py tests/test_architecture_workflow.py tests/test_architecture_feedback_loop.py tests/test_execution_reconstruction.py`: **passed** — 80 passed in 16.56s
- `python3 -m pytest -q`: **passed** — 685 passed in 38.46s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No whitespace errors.

## Open risks

- Version 1 does not define reversal or revision of a recorded workflow supersession.
- Decision-only checkout reconstruction intentionally does not invent unavailable execution attempts or runtime artifacts.
- The ending commit is unavailable until the atomic implementation commit is created.

## Intentionally not implemented

- No automatic workflow supersession.
- No migration from read-only status, next, reviews, or artifacts commands.
- No execution, attempt, retry, push, or historical workflow modification.

## Recommended next step

Review and later push the committed six-commit main branch through the separately authorized release step.

## Git status

- Implementation, ADR, migrated decisions, supersession, tests, plan, and handover pending commit.
