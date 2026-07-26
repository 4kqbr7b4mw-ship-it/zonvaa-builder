# Handover: Establish SVNP guardian conversation principles

- Timestamp: `2026-07-26T14:40:00+00:00`
- Starting commit: `7886bbb260520bede93bdd87d936fc9777cc0741`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- constitution/constitution.md
- foundation/values.md
- knowledge/adr/ADR-0023-guardian-conversation-principles.md

## Functional changes

- Established Sympathy, Trust, Utility, Price as the mandatory visible interaction order.
- Required the Guardian to follow and understand the person before exposing architecture or utility.
- Placed price and payment logic after experienced or clearly recognizable utility.

## Technical changes

- Updated the binding Constitution to version 1.1.
- Added ADR-0023 within the existing Identity-First architecture.
- Aligned existing Values interaction guidance without adding runtime behavior.

## Decisions

- SVNP is an interaction and UX rule, not a marketing funnel.
- Internal Goal and Decision architecture remains valid but cannot dominate conversation entry.
- Immediate safety and professional boundaries are not delayed by the interaction order.

## Relevant ADRs

- ADR-0008
- ADR-0010
- ADR-0013
- ADR-0018
- ADR-0023

## Checks

- `python3 -m pytest -q`: **passed** — 325 passed in 10.78s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No errors.

## Open risks

- Sufficient trust is context-dependent and must not become a mechanical dialogue gate.
- Future implementations must preserve immediate safety warnings and professional boundaries.

## Intentionally not implemented

- No UI, workflow, dialogue state machine, pricing logic, or monetization behavior.
- No changes to Life Decisions or the power-of-attorney workflow.

## Recommended next step

Define a small testable Guardian conversation contract before implementing any conversational runtime.

## Git status

- M PLANS.md
- M constitution/constitution.md
- M foundation/values.md
- ?? knowledge/adr/ADR-0023-guardian-conversation-principles.md
