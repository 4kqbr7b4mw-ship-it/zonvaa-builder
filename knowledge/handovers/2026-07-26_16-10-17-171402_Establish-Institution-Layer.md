# Handover: Establish Institution Layer

- Timestamp: `2026-07-26T16:10:17.171402+00:00`
- Starting commit: `9221193bc7f8906f2950cb95821ea332ef35a2c6`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- builder/preflight.py
- builder/runtime.py
- constitution/constitution.md
- institution/__init__.py
- institution/institution.md
- institution/loader.py
- institution/models.py
- knowledge/adr/ADR-0025-institution-layer.md
- knowledge/handovers/2026-07-26_16-10-17-171402_Establish-Institution-Layer.json
- knowledge/handovers/2026-07-26_16-10-17-171402_Establish-Institution-Layer.md
- tests/test_goal_application_service.py
- tests/test_goal_aware_orchestrator.py
- tests/test_goal_cli.py
- tests/test_institution.py
- tests/test_power_of_attorney_workflow.py
- tests/test_preflight.py

## Functional changes

- ZONVAA now exposes eight binding long-term guarantees through one canonical Institution charter.
- Preflight now fails when the Institution contract is missing or invalid and reports its version, hash, and guarantee identifiers.

## Technical changes

- Added an immutable typed InstitutionContext and strict UTF-8 InstitutionLoader.
- Runtime loads Identity, Institution, Constitution, Knowledge, Project State, and Goal Engine in that order.
- Mission Context schema 1.1 binds the loaded Institution version, content hash, and guarantee set without exposing its full text to workflows.

## Decisions

- The Institution Layer is a non-operational guarantee boundary between Guardian and Runtime.
- RuntimeManager remains the single source of truth and owns exactly one InstitutionContext.
- No function may consume trust; trust is not modeled as a numeric system asset.
- Operational components receive no Institution content and cannot create competing interpretations.

## Relevant ADRs

- ADR-0004
- ADR-0008
- ADR-0023
- ADR-0024
- ADR-0025

## Checks

- `python3 -m pytest -q`: **passed** — 352 passed in 11.45s under Python 3.9.6
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI works
- `python3 -m builder.main preflight`: **passed** — Mission Context schema 1.1 ready with Institution 1.0
- `git diff --check`: **passed** — No whitespace errors

## Open risks

- The guarantee contract is structurally enforced at boot and preflight; later feature-specific enforcement still requires narrow architecture decisions.

## Intentionally not implemented

- No policy engine, workflow behavior, UI, pricing logic, network access, or new dependency was added.
- No Institution content was passed into Decision Engine or Execution Engine.

## Recommended next step

Define a narrow architecture review gate for future feature proposals against Institution guarantees before adding operational enforcement.

## Git status

- Work package changes present before commit; no unrelated paths detected.
