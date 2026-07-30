# ADR-0046 – ZONVAA Builder Reset v2

## Status

Accepted

## Context

The previous Builder architecture accumulated competing execution owners,
watchers, feedback-triggered execution, orchestration state machines, and
intermediate artifacts. A real interrupted Codex run demonstrated that this
complexity obstructed controlled development and left ambiguous ownership.

## Decision

The active Builder uses one local development path:

`IMMUTABLE TASK → GUARD → VETO GATE → REPOSITORY LOCK → SINGLE EXECUTION
OWNER → RUN RECEIPT → STRONG GIT GATE → HUMAN COMMIT APPROVAL → SEPARATE
HUMAN PUSH APPROVAL`

The immutable task binds task ID, repository, branch, start HEAD, goal, allowed
paths, non-goals, veto classification, and whether commit or push can later be
approved. Unclear veto classification blocks. A veto-domain task requires a
human plan approval.

An atomic repository lock contains only task ID, PID, start time, and
repository. Existing locks block; suspected stale locks are reported and never
removed automatically.

Only the Builder task runner may start Codex. It starts at most once, never
retries, and never stages, commits, or pushes. One immutable run receipt records
the technical outcome as `COMPLETED`, `FAILED`, or `INTERRUPTED`; it triggers
nothing.

The Git gate verifies branch, start HEAD, staging, changed-path scope, absence
of push, the full test suite, Doctor, `git diff --check`, and receipt
consistency. Commit approval is a separate human artifact bound to task,
branch, HEAD, diff hash, action, time, and approver. A changed diff invalidates
it. Push approval is later and separately bound to the exact commit, remote,
and remote branch. Force-push, rebase, merge, and amend are outside this path.

## Veto domains

The gate has exactly three results: `NO_VETO`, `VETO_REQUIRED`, and
`HUMAN_CLASSIFICATION_REQUIRED`. The latter blocks pending a human
classification. Veto domains include authorization, governance, data
sovereignty, and security-critical execution. A second AI is not mandatory.

Additional complexity requires either a documented incident or an immediately
credible, highly probable material harm. An incident need not already have
caused damage.

## Supersession

This ADR replaces the active execution behavior of ADR-0034, ADR-0035,
ADR-0041, ADR-0042, ADR-0043, ADR-0044, and ADR-0045. Their artifacts remain
historical and read-only. Feedback loops, watchers, the Architecture Operations
Agent, the legacy execution bridge, and the former orchestrator may inspect
history but may not start processes or attempts.

Still binding are the three minimum Builder protections: correct branch and
defined starting state, successful tests before commit, and no commit or push
without explicit human approval. ZONVAA product, Constitution, Guardian,
Institution, Governance, data-ownership, and domain decisions are untouched.

## Consequences

There is one process owner and one receipt rather than a distributed lifecycle.
Humans retain commit and push authority. The design intentionally accepts less
automation and requires explicit handling of stale locks and interrupted runs.
