# Handover: Validate Guardian conversations with 100 simulations

- Timestamp: `2026-07-26T15:02:00+00:00`
- Starting commit: `2850492b10ee27d00d2af15aa49fdad07160c2a7`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- knowledge/project/guardian-conversation-lab.md
- knowledge/sources/guardian-conversation-lab.json
- tests/guardian_conversation_lab_data.py
- tests/test_guardian_conversation_lab.py

## Functional changes

- Added 100 anonymized deterministic Guardian conversation simulations.
- Documented Guardian style, rules, anti-patterns, need taxonomy, decision-space handling, help gates, and open questions.
- Validated hidden workflow matching without exposing it to the simulated user.

## Technical changes

- Added a deterministic local matrix generator and machine-readable source artifact.
- Added nine structural regression tests for diversity, SVNP, privacy, routing, and evaluation completeness.
- Kept the lab entirely outside product runtime and domain workflows.

## Decisions

- The Conversation Lab is a test and knowledge artifact, not a new runtime architecture.
- Background classification remains provisional and invisible in the first Guardian turn.
- New decision spaces are marked without inventing workflows.
- No new ADR was necessary because ADR-0023 already defines the governing contract.

## Relevant ADRs

- ADR-0008
- ADR-0023

## Checks

- `python3 -m pytest -q tests/test_guardian_conversation_lab.py`: **passed** — 9 passed
- `python3 -m pytest -q`: **passed** — 334 passed in 11.56s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No errors.

## Open risks

- Curated simulations cannot demonstrate actual sympathy or trust in real users.
- Rule-based tests validate structure but cannot fully judge semantic conversation quality.
- The governance and lifecycle of provisional background classifications remain open.

## Intentionally not implemented

- No UI, speech interface, product runtime, pricing logic, network, cloud, or external dependency.
- No legal, medical, or financial advice and no domain-workflow change.

## Recommended next step

Define a minimal reviewable Guardian conversation contract only after deciding classification transparency, correction, and expiry.

## Git status

- M PLANS.md
- ?? knowledge/project/guardian-conversation-lab.md
- ?? knowledge/sources/guardian-conversation-lab.json
- ?? tests/guardian_conversation_lab_data.py
- ?? tests/test_guardian_conversation_lab.py
