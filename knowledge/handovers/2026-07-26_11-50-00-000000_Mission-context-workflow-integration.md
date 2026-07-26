# Handover: Mission context workflow integration

- Timestamp: `2026-07-26T13:50:00+02:00`
- Starting commit: `36c43b53cfde0ce3d5e60bfb381ef022139eec69`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- builder/goal_application_service.py
- builder/orchestrator.py
- builder/preflight.py
- builder/runtime.py
- commands/goal.py
- knowledge/adr/ADR-0021-mission-context-workflow-integration.md
- knowledge/handovers/2026-07-26_11-50-00-000000_Mission-context-workflow-integration.json
- knowledge/handovers/2026-07-26_11-50-00-000000_Mission-context-workflow-integration.md
- tests/integration/test_goal_application_service_flow.py
- tests/test_goal_application_service.py
- tests/test_goal_aware_orchestrator.py
- tests/test_goal_cli.py
- tests/test_preflight.py

## Functional changes

- Goal runs now require a validated and fresh Mission Context.
- Missing, invalid, changed, or stale project context blocks the workflow.
- The existing Goal workflow remains the single application path.

## Technical changes

- MissionContext is deeply immutable and revalidated against RuntimeManager.
- A minimal immutable WorkflowContext is derived for the Orchestrator.
- Decision Engine, Planner, and Execution Engine keep their narrow existing inputs.
- The goal CLI builds Mission Context from the same booted RuntimeManager.

## Decisions

- GoalApplicationService is the approved integration boundary.
- Mission Context validity expires five minutes after creation for run startup.
- Goal-aware Orchestrator calls require a derived WorkflowContext.
- Legacy Orchestrator calls remain backward compatible.
- No second context store or hidden global handoff is introduced.

## Relevant ADRs

- ADR-0004
- ADR-0014
- ADR-0015
- ADR-0020
- ADR-0021

## Checks

- `python3 -m pytest -q`: **passed** — 292 passed in 13.08s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI works
- `git diff --check`: **passed** — No whitespace errors
- `python3 -m builder.main preflight`: **passed** — Mission Context status ready

## Open risks

- A workflow paused longer than five minutes before run startup requires a new Mission Context.
- The ending commit is unavailable until this handover is committed.

## Intentionally not implemented

- No Life Decisions business rules.
- No network, cloud, database, UI, or external filesystem integration.
- No new demonstration workflow.
- No automatic commit or push.

## Recommended next step

Define an explicit refresh policy only if future workflows need a longer pre-run preparation phase.

## Git status

- Work package files modified or untracked before final commit
