# Single Front Door Integration Assessment v1

## Scope and outcome

This assessment selects the smallest currently usable integration for the
existing Development Orchestrator. It introduces no ZONVAA product runtime,
architecture decision, governance authority, dormant candidate activation, or
second orchestration path.

**Selected:** a local, tool-only STDIO MCP adapter in front of the existing
`DevelopmentOrchestrator`.

The adapter is usable today by a locally installed MCP-capable client after a
separate client registration. It does not by itself connect a browser ChatGPT
conversation to the Mac. That web path remains absent.

## Options assessed

| Option | Current utility | Decision |
| --- | --- | --- |
| Direct Python/CLI | Proven backend path, but still requires a technical operator | Retained underneath the adapter |
| Local HTTP API | Adds listener, authentication questions, and another transport without solving browser reachability | Not implemented |
| Local STDIO MCP | Thin, no network listener, closed tool set, supported by local ChatGPT Desktop/Codex clients | Implemented |
| Remote Streamable HTTP MCP | Can serve remote chat clients, but requires hosting, HTTPS, authentication, authorization, and operations | Deferred; no preparation beyond the transport-neutral service boundary |
| ChatGPT App | Relevant if a browser ChatGPT experience and optional UI are later authorized | Not implemented |
| Local web UI | A second surface would preserve manual switching and duplicate the desired conversation front door | Rejected for this step |

## Current tool boundary

The front door offers five bounded operations:

1. `submit_work` records one structured request. With proposed repository
   context it stops before external transfer and returns a minimized preview.
2. `approve_context` records rejection or starts the existing orchestrator with
   only an expressly approved subset.
3. `get_run_status` reads persisted front-door status.
4. `get_decision_brief` returns the existing compact reviewed result.
5. `list_pending_decisions` returns only runs with an open human decision.

There is no shell, generic file write, arbitrary agent creation, commit, push,
or repository mutation tool. Research and Review remain the two existing agent
roles. The Agents SDK remains the internal model-execution layer.

## Context minimization

Context candidates are repository-relative paths plus a neutral necessity
reason. Before any model call, the existing bounded context loader resolves and
limits them. The front door returns the selected paths, reasons, exact loaded
character counts, and truncation state. Explicit approval is scoped to one run;
unproposed paths fail closed and no standing approval is created.

## Local and remote responsibilities

The orchestrator, run files, repository reads, write guard, and STDIO server can
remain local. Local STDIO does not expose a port and relies on the local client
and operating-system account boundary.

A browser ChatGPT connection would require a reachable remote MCP endpoint (or
a development tunnel), HTTPS, client authentication, per-tool authorization,
deployment operations, and narrowly scoped secret handling. A public anonymous
service and a general shell capability are prohibited. Hosting and remote auth
are not implemented or authorized by this package.

## Official sources checked

- [ChatGPT and Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
  documents local STDIO and Streamable HTTP registration for supported local
  clients.
- [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server)
  documents tool-only MCP servers, the official Python MCP SDK, and the need for
  authentication and authorization for private remote servers.
- [ChatGPT app quickstart](https://developers.openai.com/plugins/build/app-quickstart)
  documents the public HTTPS `/mcp` requirement for browser/developer-mode
  testing and the use of a tunnel only for development.
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
  remains the agent runtime behind the adapter; its orchestration logic is not
  reimplemented here.

## Working judgment

The local MCP adapter removes manual terminal commands and copy/paste for a
user working through a registered local ChatGPT Desktop or Codex conversation.
It does not yet deliver a universal single front door in browser ChatGPT.

**Answer: NO.** The smallest missing technical step is client registration for
the local Desktop/Codex path. For browser ChatGPT specifically, the missing
step is a separately authorized, authenticated HTTPS Streamable HTTP deployment
and ChatGPT app/connector registration. No local UI is required.
