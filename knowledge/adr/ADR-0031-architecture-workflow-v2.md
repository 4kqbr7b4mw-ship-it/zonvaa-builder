# ADR-0031 – Architecture Workflow v2

## Status

Beschlossen

## Kontext

ADR-0028 trennt Architecture Integrator, Chief Architect und Codex.
ADR-0029 macht ihre Artefakte reproduzierbar, verlangt im Standardpfad aber
die drei einzelnen CLI-Schritte `analyze`, `decide` und `generate-codex`.
Diese technische Bedienfolge ist keine zusätzliche Schutzgrenze und zwingt
den Nutzer, den internen Workflowzustand selbst zu orchestrieren.

## Entscheidung

ZONVAA führt `architecture run` als einzigen Standard-Einstieg für den
Architecture Workflow v2 ein.

Ein Lauf hat zwei zulässige Eingangsformen:

1. Neue typisierte Proposals und ein optionales Thema starten die
   deterministische Analyse gegen den bestehenden Architekturkontext.
2. Ein bestehender wartender Workflow und ausdrücklich bestätigte
   `ChiefArchitectDecision`-Objekte setzen denselben Prozess fort.

Nach der Analyse erzeugt der Workflow ausschließlich eine gemeinsame,
kompakte Entscheidungsvorlage mit:

- Empfehlung,
- Übernehmen,
- Ändern,
- Ablehnen,
- offenen Entscheidungen.

Der Zustand bleibt `WAITING_FOR_DECISION`. Der Workflow trifft keine
Entscheidung und erzeugt keinen Codex-Prompt.

Erhält ein späterer Aufruf bestätigte Entscheidungen, persistiert derselbe
Einstieg die Decision Records und prüft den berechneten Workflowzustand.
Sobald für jedes Proposal genau eine passende Entscheidung vorliegt, erzeugt
er ohne weiteren CLI-Schritt den gemeinsamen Codex-Prompt. Unvollständige
Entscheidungsmengen bleiben im Wartezustand.

### Versionierung und Reproduzierbarkeit

Neue Manifeste verwenden Schema `2.0`. Sie binden:

- das Thema,
- die kanonisch geordneten Proposal-IDs,
- die Proposal- und Analysepfade,
- sowie genau eine gemeinsame Entscheidungsvorlage.

Thema, Proposal-Inhalte, Analysen und geladene Quellen bestimmen gemeinsam die
deterministische Workflow-ID. Alte Manifeste der Version `1.0` bleiben
lesbar; sie werden nicht migriert oder überschrieben.

### Autoritätsgrenze

Workflow v2 verändert die Rollen aus ADR-0028 und ADR-0029 nicht:

- Der Architecture Integrator analysiert und empfiehlt unverbindlich.
- Der Chief Architect entscheidet ausschließlich `ADOPT`,
  `ADOPT_WITH_CHANGES`, `REJECT` oder `DEFER`.
- Codex erhält erst nach vollständiger bestätigter Entscheidung einen Prompt.

Mehrere Proposals behalten jeweils ein eigenes Decision Record. Der
Orchestrator löst Konflikte nicht auf, publiziert keine Architektur, startet
keine Implementierung und erzeugt weder Tests noch Commits.

Die bisherigen `architecture workflow`-Unterbefehle bleiben zur
Rückwärtskompatibilität verfügbar, sind aber nicht mehr der Standardpfad.
Diese ADR ersetzt ausschließlich den CLI-Standardpfad und das
Entscheidungsvorlagenformat aus ADR-0029; dessen Autoritäts-, Persistenz-,
Gate- und Sicherheitsregeln bleiben verbindlich.

## Folgen

- Nutzer orchestrieren keine internen Workflowstufen mehr.
- Eine fehlende Chief-Architect-Entscheidung bleibt ein sichtbarer,
  reproduzierbarer Wartezustand.
- Nach vollständiger Entscheidung sind Decision Record, Workflowstatus und
  Codex-Prompt Ergebnis desselben `run`-Aufrufs.
- Analyseartefakte bleiben außerhalb normativer MDR- und ADR-Quellen.

## Nicht-Ziele

Nicht eingeführt werden automatische Architekturentscheidung, automatische
Implementierung, autonome Repository-Änderung, Testausführung,
Commiterstellung, Push, externe KI-Aufrufe, Netzwerkzugriff oder UI.
