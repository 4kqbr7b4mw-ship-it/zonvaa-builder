# Automated Codex Execution Bridge

The Bridge transports one confirmed Architecture Workflow prompt to the
official local Codex CLI. It does not analyze, approve or modify architecture.

## Authority chain

1. The Chief Architect decides.
2. Architecture Workflow writes Decision Records and the canonical prompt.
3. A prompt proof binds workflow, decisions, path and SHA-256.
4. The Bridge validates repository, prompt, proof, lock, Git state, Codex
   installation and local authentication.
5. Codex implements through `codex exec`.
6. The Bridge verifies tests, Doctor, `git diff --check`, result commit,
   handover and a clean worktree.
7. No push is performed.

Execution JSON and Markdown reports are local runtime state below
`knowledge/architecture_workflows/<workflow-id>/executions/`. They are ignored
by Git so final status cannot contaminate the Codex result commit.

Execution-Record-Schema 1.1 speichert Fehler maschinenlesbar. `failure`
unterscheidet fehlende Ressourcen, Prozessstart, Non-Zero-Exit, Timeout und
interne Bridge-Fehler. Es enthält den konkreten Schritt, getrennte Programm-
und Argumentdaten, Exit-Code, redigiertes stdout/stderr und eine technische
Ursache. stdin und Umgebungsvariablen werden nicht protokolliert; bekannte
Token-, API-Key-, Passwort-, Credential-, Secret- und Authorization-Muster
werden durch `[REDACTED]` ersetzt.

Schema 1.2 ergänzt eine geordnete `attempts`-History im selben Execution
Record. Jeder Start besitzt eine deterministische Attempt-ID und Nummer; ein
Retry hängt einen neuen Attempt an. Nur der aktive Attempt darf von `PENDING`
über `RUNNING` in einen terminalen Status wechseln. Der Store lehnt Änderungen
bereits terminaler Attempts ab. JSON enthält die vollständige History;
Markdown zeigt Anzahl, Status, Zeiten und Ergebnis jedes Attempts. Historische
Schema-1.0/1.1-Records bleiben lesbar und erhalten eine leere History, weil
Einzelversuchsdaten nicht nachträglich erfunden werden.

Schema 1.3 ergänzt die Herkunft `EXECUTION_BRIDGE` oder `RECONSTRUCTED`.
Rekonstruktion führt einen ausdrücklich autorisierten Direktauftrag nicht
erneut aus. Sie verifiziert Basis- und Result-Commit, explizite Handover-Pfade
und maschinenlesbare Checks, speichert keine erfundenen Attempts oder
Ausführungszeiten und führt den Record anschließend durch dieselbe
Handover-Validierung und Integrator-Review wie die Bridge. Ein Handover allein
ist niemals Autorisierung. Schema-1.0 bis 1.2 bleiben als Bridge-Records
lesbar.

## Manual commands

```text
python3 -m builder.main architecture execute --workflow-id workflow-0123456789abcdef
python3 -m builder.main architecture execution status --workflow-id workflow-0123456789abcdef
python3 -m builder.main architecture execution retry --workflow-id workflow-0123456789abcdef
python3 -m builder.main architecture execution cancel --workflow-id workflow-0123456789abcdef
python3 -m builder.main architecture execution watch-once
python3 -m builder.main architecture execution reconstruct \
  --authorization knowledge/execution_reconstruction/authorization.json \
  --reconstructed-at 2026-07-27T17:00:00+00:00
```

`execute` only accepts `CODEX_PROMPT_GENERATED`. Failed or blocked records need
an explicit retry. Capacity retries follow `policy.md`.

## macOS launchd watcher

The repository contains `automation/com.zonvaa.codex-execution.plist`. It
starts one finite, idempotent scan periodically; there is no busy-wait process.

One-time installation by the Mac user:

```text
cp automation/com.zonvaa.codex-execution.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.zonvaa.codex-execution.plist
```

Status:

```text
launchctl print gui/$UID/com.zonvaa.codex-execution
```

Stop and remove:

```text
launchctl bootout gui/$UID/com.zonvaa.codex-execution
rm ~/Library/LaunchAgents/com.zonvaa.codex-execution.plist
```

Installation is deliberately not automatic. The user remains able to stop the
watcher at any time.

## Failure boundaries

- Prompt or decision mismatch blocks before Codex.
- Capacity creates `WAITING_FOR_CAPACITY`.
- Codex, test, Doctor, diff, commit, handover or clean-tree failure creates
  `FAILED`.
- Existing worktree changes are retained on failure.
- The Bridge never resets, commits, pushes, creates a PR or changes a Chief
  Architect decision.
- A retry reuses the exact approved prompt and current intermediate worktree.
- A retry requires the recorded branch and start commit; uncommitted
  intermediate changes remain untouched.

The Bridge cannot prevent a Codex process from having created a commit before a
later independent verification fails. Such a commit is not approved as the
result, is not changed automatically and is reported as a risk.

## Feedback-loop authorization

Architecture Workflow v2 may persist
`feedback/execution-authorization.json`. When present, the Bridge additionally
requires its confirmed approval status, workflow and deterministic
Execution-ID, prompt hash, repository and expected base commit to match before
Codex starts. Historical confirmed workflows without this additive artifact
remain readable and executable under their existing prompt proof.

After success, the watcher can hand the owning workflow directly to the
Architecture feedback coordinator. The coordinator consumes the existing
Execution Record and its immutable Attempt History; it does not copy or replace
Bridge state.

The confirmed order explicitly authorizes a result commit. The Codex CLI
therefore receives the repository's own `.git` directory as an additional
writable directory while retaining `workspace-write` for the repository. No
parent directory, home directory or external path is added.
