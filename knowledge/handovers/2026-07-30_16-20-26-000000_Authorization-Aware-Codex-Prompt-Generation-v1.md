# Handover: Authorization-Aware Codex Prompt Generation v1

- Timestamp: `2026-07-30T18:20:26+02:00`
- Starting commit: `a8e917c17fb6ac3bc5d8ef3c05173fa44c84da21`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- architecture_integrator/README.md
- architecture_integrator/__init__.py
- architecture_integrator/feedback_loop.py
- architecture_integrator/operations.py
- architecture_integrator/workflow.py
- codex_execution/README.md
- codex_execution/orchestration.py
- commands/architecture.py
- knowledge/adr/ADR-0044-authorization-aware-codex-prompts.md
- tests/test_architecture_feedback_loop.py
- tests/test_architecture_workflow.py
- tests/test_codex_execution_orchestration.py

## Functional changes

- Commitless prompts explicitly prohibit commit, staging and push while retaining validated worktree changes.
- Commit-authorized prompts permit exactly one commit only after required validation and still prohibit push.
- Prompt Proof schema 1.1 records commit authorization, typed instruction and push prohibition.
- Orchestration blocks semantic mismatch before PID, Attempt or Codex process creation.
- Status and Operations expose prompt instruction, authorization match and push policy.

## Technical changes

- Added immutable PromptCommitInstruction and CodexPromptSemantics contracts.
- Passed create_commit through the official workflow into prompt generation and authorization.
- Bound semantic proof fields to the prompt hash and Chief Architect decisions.
- Added PROMPT_AUTHORIZATION_MISMATCH preflight validation for new and historical prompts.

## Decisions

- ADR-0044 makes prompts incapable of granting authority absent from Execution Authorization.
- Historical schema-1.0 proofs remain unchanged but their real prompt semantics are checked before execution.
- Push remains forbidden for both commit modes.

## Relevant ADRs

- ADR-0041
- ADR-0042
- ADR-0043
- ADR-0044

## Checks

- `python3 -m pytest -q tests/test_architecture_workflow.py tests/test_architecture_feedback_loop.py tests/test_codex_execution_orchestration.py tests/test_architecture_operations.py tests/test_execution_reconstruction.py`: **passed** — 132 passed in 18.45s
- `python3 -m pytest -q`: **passed** — 737 passed in 40.34s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No whitespace errors.
- `git diff --exit-code -- knowledge/architecture_workflows/*/prompts/* knowledge/architecture_workflows/*/feedback/execution-authorization.json`: **passed** — No historical prompt, proof or authorization changed.

## Open risks

- Historical free-form prompts without one defined normative instruction remain non-executable until explicitly reviewed and re-authorized.
- The semantic parser intentionally recognizes only the versioned normative action sentences, not arbitrary natural-language permissions.
- The handover cannot self-reference the result commit before that commit exists.

## Intentionally not implemented

- No real Architecture Workflow, Authorization, Codex execution or productive orchestration.
- No historical prompt, proof or authorization migration.
- No push and no change to state, retry, queue or scheduling contracts.

## Recommended next step

Run the separately authorized diagnostics workflow with create_commit false and verify terminal COMMIT_READY.

## Git status

- Implementation and handover pending commit.
