# ADR-0044 – Authorization-Aware Codex Prompts

## Status

Beschlossen

## Kontext

ADR-0043 trennt die Commit-Berechtigung als `create_commit` von allgemeinen
Execution-Aktionen. Der bestehende Architecture Workflow erzeugte jedoch
weiterhin für jeden Auftrag die Anweisung, nach den Prüfungen einen Commit
anzulegen. Damit konnte ein Prompt mehr Befugnis behaupten als die zugehörige
Execution Authorization.

Prompttext, Prompt Proof und Authorization müssen dieselbe Aktionsgrenze
beweisen, bevor ein lokaler Codex-Prozess gestartet wird.

## Entscheidung

Der typisierte Wert `create_commit` wird durch den offiziellen Workflow an
Prompt-Generator, Prompt Proof und Execution Authorization übergeben.

Der Prompt darf keine Berechtigung erteilen, die nicht in der Authorization
enthalten ist. Commit-Anweisungen werden ausschließlich aus `create_commit`
abgeleitet, nicht aus `ALLOWED_ACTIONS`, Promptinhalt oder globalem Zustand.

Push bleibt in beiden Varianten ausdrücklich verboten.

## Commitloser Prompt

Bei `create_commit: false` enthält der normative Abschluss genau:

```text
Do not create a commit.
Do not stage files.
Leave validated changes in the working tree.
Do not push.
```

Der Prompt enthält keine Commit-, Staging- oder Push-Erlaubnis. Eine
erfolgreiche Orchestration endet bei `COMMIT_READY`; der nächste Schritt ist
`MANUAL_COMMIT_APPROVAL`.

## Commitfähiger Prompt

Bei `create_commit: true` enthält der normative Abschluss:

```text
Create exactly one commit only after all required validations pass.
Do not amend or create multiple commits.
Do not push.
```

Die Berechtigung gilt ausschließlich für genau einen nachgelagerten Commit
nach erfolgreicher Orchestrator-Validierung. Sie erlaubt keinen frühen Commit,
kein Amend, keine Commit-Serie und keinen Push.

## Prompt Proof

Prompt Proof Schema 1.1 ergänzt:

- `create_commit_authorized`,
- `commit_instruction`,
- `push_forbidden`.

Zulässige Commit-Anweisungen sind typisiert:

- `DO_NOT_COMMIT`,
- `CREATE_EXACTLY_ONE_AFTER_VALIDATION`.

Der Proof bindet diese Felder zusammen mit Prompt-Hash, Workflow und
Chief-Architect-Entscheidungen. Ein widersprüchlicher Prompt erhält keinen
gültigen neuen Proof.

## Orchestrator-Preflight

Vor PID-, Attempt- oder Prozessstart analysiert der Orchestrator ausschließlich
die definierten normativen Prompt-Sätze und vergleicht:

```text
Prompt Commit Instruction
==
Prompt Proof
==
Execution Authorization create_commit
```

Zusätzlich muss `push_forbidden` wahr sein. Fehlende, widersprüchliche oder
abweichende Semantik führt zu:

```text
BLOCKED
PROMPT_AUTHORIZATION_MISMATCH
```

Es wird kein Codex-Prozess gestartet und keine Berechtigung ergänzt.

## Historische Prompts

Historische Prompts und Proofs werden nicht verändert. Prompt Proof Schema 1.0
bleibt read-only lesbar. Vor einer neuen Ausführung wird der tatsächliche
historische Prompt dennoch gegen die aktuelle Authorization geprüft.

Ein historischer Prompt mit pauschaler Commit-Anweisung und
`create_commit: false`, ein Push erlaubender Prompt oder eine widersprüchliche
Anweisung wird blockiert. Es gibt keine automatische Umschreibung oder
Migration.

## Diagnose

Orchestration- und Architecture-Operations-Ausgaben zeigen:

- `prompt_commit_instruction`,
- `create_commit_authorized`,
- `prompt_authorization_match`,
- `push_forbidden`.

Read-only Status- und Listenbefehle verändern keine Prompt-, Proof-,
Authorization- oder Runtime-Artefakte.

## Sicherheitsgrenzen

- keine globale Commit-Vorgabe,
- keine Ableitung aus allgemeinen Aktionen,
- keine nachträgliche Promptmanipulation,
- kein Prozess bei semantischem Widerspruch,
- keine Mutation historischer Prompts oder Proofs,
- kein Push,
- keine reale Codex-Ausführung durch diesen Auftrag.

## Konsequenzen

Der erste produktive Diagnostiklauf kann erst nach dieser Änderung einen
widerspruchsfreien Prompt und eine Authorization mit `create_commit: false`
erhalten. Prompt Proof und Orchestration dokumentieren die Grenze
maschinenlesbar.

## Teststrategie

Tests prüfen beide Promptvarianten, exakt eine Commit-Anweisung bei Freigabe,
Commit- und Staging-Verbot ohne Freigabe, Push-Verbot, Proof Schema 1.1,
widersprüchliche Proofs, alle Mismatch-Richtungen, ausbleibenden Prozess/PID/
Attempt, unveränderte historische Artefakte, Operations-Ausgabe sowie
erfolgreiche Fake-Codex-Läufe für `false` und `true`.
