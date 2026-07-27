# Handover: Legacy workflow watcher compatibility

- Timestamp: `2026-07-27T16:28:10+00:00`
- Starting commit: `6772c54af823b34bea3ac234a85adefbcd5f2b2b`
- Ending commit: `missing`
- Push status: `not_pushed`

## Changed files

- PLANS.md
- codex_execution/watcher.py
- tests/test_codex_execution.py
- knowledge/handovers/2026-07-27_16-28-10-000000_Legacy-workflow-watcher-compatibility.json
- knowledge/handovers/2026-07-27_16-28-10-000000_Legacy-workflow-watcher-compatibility.md

## Functional changes

- The watcher now skips legacy workflows whose Markdown Codex prompt exists but whose prompt-proof artifact is completely absent.
- Valid current workflows remain executable and present but invalid proofs remain structured errors.
- A skipped legacy workflow no longer blocks valid workflows in the same scan.

## Technical changes

- Added a pre-service selection guard in codex_execution/watcher.py using ArchitectureWorkflowStore.prompt_proof_path().
- The guard distinguishes a truly absent path from a present or broken symlink so malformed proof artifacts are still validated and reported.
- Added regression coverage for no runner call, no execution record, unchanged historical bytes, mixed scans and manipulated proofs.

## Decisions

- Workflow status semantics remain unchanged.
- No legacy workflow is migrated, modified, deleted or supplied with a generated proof.
- Execution authorization and prompt-proof schema remain unchanged.

## Relevant ADRs

- ADR-0028
- ADR-0029
- ADR-0031
- ADR-0034
- ADR-0035

## Checks

- `python3 -m pytest -q tests/test_codex_execution.py`: **passed** — 37 passed in 1.32s
- `python3 -m pytest -q tests/test_architecture_workflow.py`: **passed** — 15 passed in 2.96s
- `python3 -m pytest -q tests/test_architecture_feedback_loop.py`: **passed** — 10 passed in 2.62s
- `python3 -m pytest -q`: **passed** — 630 passed in 26.38s
- `python3 -m builder.main doctor`: **passed** — ZONVAA Builder CLI funktioniert
- `git diff --check`: **passed** — No whitespace errors
- `python3 -m builder.main architecture execution watch-once`: **passed** — results was empty; the legacy workflow produced no ERROR entry

## Open risks

- Historical status displays may still classify prompt-only workflows as CODEX_PROMPT_GENERATED; only execution selection is hardened.
- Handover schema 1.0 cannot contain the hash of its own containing result commit before commit creation.

## Intentionally not implemented

- Legacy workflow migration or prompt-proof generation.
- Historical artifact modification, deletion or relocation.
- Prompt-proof schema, authorization or feedback-loop changes.
- Guardian Succession changes, new persistence or new dependencies.

## Recommended next step

Keep legacy workflows immutable and use only proof-backed workflows for future automated Codex execution.

## Git status

- Before commit, only the watcher, its regression tests, PLANS.md and this handover pair are changed or new.
