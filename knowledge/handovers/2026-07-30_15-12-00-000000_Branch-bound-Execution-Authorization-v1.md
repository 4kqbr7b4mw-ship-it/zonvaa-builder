# Handover: Branch-bound Execution Authorization v1

- Timestamp: `2026-07-30T17:12:00+02:00`
- Starting commit: `d052a222c4108084acb6cc4fec7bfdb708d2e223`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- architecture_integrator/__init__.py
- architecture_integrator/feedback.py
- architecture_integrator/feedback_loop.py
- architecture_integrator/operations.py
- codex_execution/README.md
- codex_execution/orchestration.py
- codex_execution/reconstruction.py
- codex_execution/service.py
- knowledge/adr/ADR-0042-branch-bound-execution-authorization.md
- tests/test_architecture_feedback_loop.py
- tests/test_architecture_operations.py
- tests/test_codex_execution.py
- tests/test_codex_execution_orchestration.py

## Functional changes

- New Execution Authorizations bind the approved repository state to an explicit local branch.
- The orchestrator and direct Bridge block missing, detached or mismatching branch state before a Codex process or attempt starts.
- Status, list and Architecture Operations output expose authorized branch, current branch and branch match.

## Technical changes

- Execution Authorization schema 1.1 adds validated authorized_branch and includes it in deterministic authorization identity.
- Schema 1.0 authorizations remain readable and byte-for-byte unchanged but are non-executable for new automated runs.
- Orchestration failures carry stable machine-readable error codes.
- Branch validation rejects remote refs, ref syntax, wildcards, detached placeholders, malformed separators and control characters.

## Decisions

- ADR-0042 adds the branch-bound authorization contract without rewriting ADR-0041.
- There is no default branch and no conversion from remote refs to local branch names.
- A matching base commit does not compensate for branch mismatch or detached HEAD.

## Relevant ADRs

- ADR-0034
- ADR-0035
- ADR-0041
- ADR-0042

## Checks

- `python3 -m pytest -q tests/test_codex_execution_orchestration.py tests/test_codex_execution.py tests/test_architecture_feedback_loop.py tests/test_architecture_operations.py tests/test_execution_reconstruction.py`: **passed** — 143 passed in 16.22s
- `python3 -m pytest -q`: **passed** — 727 passed in 40.14s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert.
- `git diff --check`: **passed** — No whitespace errors.
- `git diff --exit-code -- knowledge/architecture_workflows/*/feedback/execution-authorization.json`: **passed** — No historical versioned authorization changed.

## Open risks

- Historical schema-1.0 authorizations require a separate explicitly authorized migration or reconstruction before any new automated execution.
- The contract validates local branch syntax but intentionally does not create, switch or resolve branches.
- The handover cannot self-reference the result commit before that commit exists.

## Intentionally not implemented

- No real Codex execution or productive orchestration.
- No branch creation, branch switch, legacy authorization mutation or default to main.
- No push and no change to retry, queue, scheduling or architecture-decision behavior.

## Recommended next step

Review and explicitly migrate or recreate only those legacy authorizations that should become executable on a named branch.

## Git status

- Implementation and handover pending commit.
