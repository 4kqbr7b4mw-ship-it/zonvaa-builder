# Development Orchestrator – Runnable Prototype v1

## Purpose

This directory contains an internal development tool that turns one structured
founder request into a bounded research run, an independent review, at most two
research/review cycles, and a compact decision brief.

It is not part of the ZONVAA product runtime, B2 runtime, Runtime Readiness, or
the Invocation-to-Runtime constitution. It does not create architecture,
governance, institutional decisions, customer-facing agents, or dormant
architecture candidates.

## V1 workflow

```text
structured request
-> deterministic plan
-> bounded context selection
-> Research Agent
-> Review Agent (ACCEPT | REVISE | ESCALATE)
-> at most one repeated cycle when max_iterations=2
-> compact decision brief
```

The manager controls sequencing in code. It never invents agent types. The
Research Agent separates evidence, findings, uncertainty, and open questions.
The Review Agent checks the original goal, evidence, scope, useful simplicity,
and the product principle "Innen maximal präzise. Außen maximal verständlich."

## Context loader

`allowed_context` contains explicit repository-relative file paths. The loader
ranks that closed list against the goal, resolves every path inside the
repository, reads text only, records selected paths, and enforces file-count and
character limits. It does not scan or load the complete repository into every
prompt and does not use implicit chat memory.

## Write boundary

The only writable tree is this directory:

```text
internal/development-orchestrator/**
```

Every application write passes through `BoundaryGuard` and `WorkspaceWriter`.
They resolve paths before writing and reject traversal, absolute external
paths, and symlink components. After every run, porcelain Git status is parsed
and any changed path outside this directory fails closed. The orchestrator does
not repair or revert foreign changes.

Repository context is read-only. There are no shell, commit, push, merge,
rebase, or stash tools available to either agent.

## Run artifacts

Each run gets `runs/<run-id>/` containing:

- `request.json`
- `plan.json`
- `research.md`
- `review.md`
- `handover.md`
- `result.json`
- `usage.json`

The console prints only `result.json`'s compact decision brief, not the full
research document. Run data is ignored by Git but remains locally inspectable.
Only synthetic, non-personal fixtures are used by tests and evals.

## Cost and usage guard

The guard bounds review iterations and run steps. It records SDK request and
token usage when reported. It accepts provider-reported cost but does not infer
prices. Without reliable cost data the status is exactly
`not reliably determined`. A reliably reported cost above `max_cost` stops the
run.

## Install and run

Use a dedicated environment from this directory so the repository's historical
top-level `agents/` package does not shadow the OpenAI Agents SDK package:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/python main.py run --request path/to/request.json
```

A live run requires `OPENAI_API_KEY`. The value is read only by the SDK from the
environment and is never written or logged. Expected missing-key errors are
reported without a traceback.

V1 explicitly selects `gpt-4.1` for both Research and Review in the central
`development_orchestrator/model_configuration.py` module. The selected models
are persisted in `plan.json`. Missing or unsupported live model configuration
fails closed; the SDK default model and automatic fallback chains are not used.

Explicit offline contract execution:

```bash
python main.py run --request fixtures/smoke-request.json --offline
python main.py smoke --offline
```

Live smoke execution:

```bash
python main.py smoke
```

The offline command proves contracts, routing, persistence, review looping, and
boundaries. It is not represented as an OpenAI model run.

## Single working front door

The optional integration extra adds a thin local MCP front door around the
existing orchestrator. It does not duplicate Research, Review, routing, or run
persistence. The adapter exposes the five research/front-door tools:

- `submit_work`
- `get_run_status`
- `get_decision_brief`
- `approve_context`
- `list_pending_decisions`

It additionally exposes one narrowly bounded execution handoff:

- `handoff_reviewed_run`

That operation accepts only a known run ID, explicit human approval and a
closed list of repository-relative write paths. It requires a completed run,
an accepted review and an available decision brief. An open founder decision
blocks handoff unless the same human approval explicitly covers it. The
handoff is one-shot and persists `codex-handoff.md` plus
`codex-handoff.json` in that run directory before invoking Codex.

The bridge uses the locally installed stable non-interactive `codex exec`
command with fixed arguments, an ephemeral session, ignored user configuration
and the `workspace-write` sandbox. The caller cannot supply a command or free
prompt. Codex receives only the persisted reviewed package, its run ID, the
closed path scope and the permanent prohibition on commit and push. Branch,
HEAD and changed paths are verified after execution; any mismatch is recorded
as `FAILED`. No retry or second task follows automatically.

When repository context is proposed, `submit_work` persists the request and
returns paths, one-sentence reasons, character counts, and truncation flags. It
does not start the Agents SDK. `approve_context` accepts only an explicitly
approved subset of that proposal and only then starts the existing orchestrator.
Commit, push, shell, general filesystem and generic execution tools are not
exposed.

The current official MCP package requires Python 3.10 or newer. A separate,
ignored integration environment keeps this constraint out of the existing
Python 3.9 core environment:

```bash
python3.10 -m venv .mcp-venv
.mcp-venv/bin/pip install -e '.[test,integration]'
.mcp-venv/bin/python mcp_server.py
```

This server uses local STDIO only. ChatGPT Desktop and Codex can register that
command as a local MCP server; registration is a separate user-level client
configuration step and is intentionally not written into this repository. A
browser-based ChatGPT integration cannot call this localhost process directly.
That later step would require a securely reachable Streamable HTTP MCP endpoint
or ChatGPT app connection, HTTPS, authentication and authorization, and an
explicit hosting decision. None of those remote components exists in v1.

No local web UI is needed for the working local MCP path. STDIO inherits the
permissions of the local client process and does not open a network listener.
The adapter remains subject to the existing repository read policy, hard write
boundary, run evidence, iteration guard, and cost/usage guard.

## Tests and evals

```bash
python -m pytest tests
python evals/run_local.py
```

The local eval harness exercises the actual `DevelopmentOrchestrator` manager
with an explicit deterministic backend. It grades behavior and artifacts, not
exact prose. Results are written to `evals/results/latest.json`.

## Security model and known limits

- V1 exposes no model-controlled filesystem, shell, SDK tool, or SandboxAgent.
- Live context is assembled before the model call by deterministic read-only
  code; writes occur after the call through the guarded writer.
- Cost enforcement can only use costs actually reported to the application.
- Live SDK behavior and model quality require a separate credentialed smoke
  test.
- V1 is single-process and has no concurrent-run lock.
- The controlled Codex handoff is also single-process and one-shot. It records
  failures but never repairs or reverts an out-of-scope change automatically.
- MCP tool calls are synchronous in v1; status polling is useful between calls,
  but a running agent call does not provide background-job progress.
- Local run artifacts are not encrypted and must contain development-safe,
  non-personal material only.
- A Git status check detects repository changes but cannot identify the process
  that caused them.

**No commit or push automation in v1.**
