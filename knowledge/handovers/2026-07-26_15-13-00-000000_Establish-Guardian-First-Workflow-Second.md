# Handover: Establish Guardian First, Workflow Second

- Timestamp: `2026-07-26T15:13:00+00:00`
- Starting commit: `c37adbdc1b737da8f0b073217d3c3aa30ffe82d4`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- constitution/constitution.md
- knowledge/adr/ADR-0024-guardian-first-workflow-second.md
- knowledge/project/guardian-conversation-lab.md

## Functional changes

- Established that the user always speaks with the Guardian rather than a workflow.
- Placed provisional decision-space hypotheses before any workflow compatibility check.
- Established user rights to correction, rejection, alternative paths, and recommendation traceability.

## Technical changes

- Added ADR-0024 as an explicit supplement to ADR-0023.
- Updated the binding Constitution to version 1.2.
- Aligned the Conversation Lab with default invisibility and on-request transparency.

## Decisions

- Invisible everyday architecture must not become a black box.
- Workflow existence cannot drive the visible conversation or be inferred from a keyword.
- New decision spaces remain hypotheses until a separate architecture decision establishes a workflow.
- No implementation was required for this architecture-only package.

## Relevant ADRs

- ADR-0008
- ADR-0023
- ADR-0024

## Checks

- `python3 -m pytest -q`: **passed** — 334 passed in 10.79s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No errors.

## Open risks

- The technical form of correction, rejection, explanation, and classification expiry remains undecided.
- Transparency must not turn ordinary conversation into a technical audit flow.

## Intentionally not implemented

- No UI, conversation runtime, classification model, product logic, or workflow change.
- No automatic workflow creation or domain behavior.

## Recommended next step

Define a minimal non-UI transparency contract for provisional decision-space hypotheses before implementing classification.

## Git status

- M PLANS.md
- M constitution/constitution.md
- M knowledge/project/guardian-conversation-lab.md
- ?? knowledge/adr/ADR-0024-guardian-first-workflow-second.md
