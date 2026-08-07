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
- Local run artifacts are not encrypted and must contain development-safe,
  non-personal material only.
- A Git status check detects repository changes but cannot identify the process
  that caused them.

**No commit or push automation in v1.**
