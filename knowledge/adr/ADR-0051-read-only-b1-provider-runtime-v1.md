# ADR-0051 – Read-only B1 Provider Runtime v1

## Status

Angenommen für den begrenzten Implementierungsauftrag vom 02.08.2026.

## Kontext und Zweck

ADR-0047 definiert allgemeine Orientierung und entpersonalisierte Recherche,
ADR-0048 abstrakte Befugnisse, ADR-0049 konkrete Provider-Autorisierungen und
ADR-0050 die nicht ausführende Capability Invocation Boundary. ADR-0051 zieht
die erste reale Machtgrenze: Ein bereits vollständig validierter und
`ACCEPTED` dokumentierter Invocation-Pfad darf genau einen ausdrücklich
bereitgestellten Provider-Adapter genau einmal aufrufen.

Diese Freigabe gilt ausschließlich für `B1_GENERAL_ORIENTATION` und
`READ_ONLY`. Sie ist keine allgemeine Provider-, Werkzeug-, Workflow- oder
Research-Runtime.

## Entscheidung

ZONVAA führt eine enge, fail-closed Read-only-B1-Runtime ein. Ihr Pfad lautet:

```text
Authority Model
→ Provider Authorization
→ Capability Invocation Boundary
→ ACCEPTED Receipt und Resolution Snapshot
→ B1 Runtime Execution Request
→ benannter B1 Read-only Provider Adapter
→ Runtime Result
→ Output Boundary
→ Execution Evidence und Receipt
```

Die Runtime wählt weder Provider noch Capability. Sie übernimmt ausschließlich
die Identität, Authority, Authorization, Capability, Betriebsart, Datenbindung,
Kontrollen, Quellen und Input-Verträge des unveränderten ADR-0050-Pfads.

## Zulässige Machtgrenze

Zulässig sind ausschließlich:

- `B1_GENERAL_ORIENTATION`,
- `READ_ONLY`,
- `NON_PERSONAL` oder ausdrücklich `DEPERSONALIZED`,
- ein bereits benannter Provider,
- eine bereits autorisierte Capability,
- ein vollständiger `ACCEPTED`-Invocation-Pfad,
- explizite Kontext-, Source-Chain-, Input- und Output-Bindungen,
- immutable Ergebnis- und Ausführungsnachweise.

`SIMULATION` und `DEGRADED` bleiben in ADR-0050 deklarativ zulässige
Invocation-Modi, sind aber keine reale Ausführungsfreigabe nach ADR-0051.
ADR-0051 führt nur `READ_ONLY` aus.

## Entpersonalisierungsgrenze

Personenbezogene Daten sind ausgeschlossen. Vor dem Provider-Aufruf muss der
bereits validierte Invocation Request `NON_PERSONAL` oder `DEPERSONALIZED`
führen. Die Runtime übernimmt die vollständigen typisierten Kontextbindungen
unverändert. Sie interpretiert, anonymisiert oder bereinigt keine Inhalte.

Fehlt die sichere Datenbereichs- oder Kontextbindung, bleibt der Aufruf
blockiert. Eine D3-Einwilligung, personenbezogene Recherche oder automatische
Entpersonalisierung ist nicht Teil dieser Runtime.

## Input-Vertrag

Der immutable `B1RuntimeExecutionRequest` bindet Execution, Invocation Request,
`ACCEPTED` Decision, Invocation Evidence, Receipt und Resolution Snapshot sowie
Provider, Authorization, Capability, `READ_ONLY`, B1, Eingabevertrag,
Schema-Version, immutable Eingabefelder, Kontext, Source Chains, Startzeit,
Timeout, Review, Unsicherheit, Provenienz und Output-Vertrag.

Eingaben werden nicht semantisch interpretiert. Die Runtime prüft ausschließlich
Typen, Referenzen, Vollständigkeit und Gleichheit zu den bereitgestellten
Nachweisen.

## Provider-Adapter

`B1ReadOnlyProviderAdapter` ist ein enger Port für genau eine benannte
Provider-Identität und genau eine autorisierte Capability. Er erhält einen
immutable `ProviderAdapterRequest` und liefert ein typisiertes Ergebnis oder
einen typisierten technischen Status.

Der Adapter darf keinen Provider suchen, vergleichen, priorisieren oder
ersetzen. Er darf keine Authorization ändern, keine Capability erweitern,
keinen Prompt improvisieren und keine B2-/B3-Inhalte verarbeiten. Die
Timeout-Grenze wird dem Adapter ausdrücklich übergeben; v1 startet keinen
zweiten Prozess und keine allgemeine Scheduling- oder Retry-Runtime.

Im Repository ist zum Entscheidungszeitpunkt kein kanonisch autorisierter und
sicher konfigurierter externer Provider für diese Grenze vorhanden. Daher wird
keine externe Anbindung improvisiert. Die Runtime wird gegen einen
kontrollierten Testadapter validiert. Secrets, Credentials und produktive
Netzwerkaufrufe sind nicht Bestandteil von ADR-0051.

## Ausführungsfreigabe und Executor

Vor jedem Aufruf validiert der Executor erneut den vollständigen ADR-0050-Pfad
mit den bestehenden Validatoren. Zusätzlich prüft er:

- Decision exakt `ACCEPTED`,
- Receipt und Resolution Snapshot mit unveränderter Objektidentität,
- unveränderte Provider- und Authorization-Referenzen,
- Grant ausdrücklich `AUTHORIZED`,
- keine bereitgestellte Suspension, Revocation oder Expiration,
- Capability und Verantwortungsgrenze,
- Kontrollen,
- exakt B1 und `READ_ONLY`,
- nicht personenbezogene oder entpersonalisierte Datenbindung,
- vollständige Source Chains,
- passenden Input-Vertrag,
- konsistente Provenienz,
- exakte Adapteridentität.

Ein fehlender oder widersprüchlicher Nachweis blockiert vor dem Provider-Aufruf.
Es gibt keine Reparatur, Ersatzautorisierung, Providerwahl oder Wiederholung.

## Runtime Result und Output Boundary

`B1RuntimeResult` unterscheidet Erfolg, kontrollierte Ablehnung oder
Blockierung, technischen Provider-Fehler, Timeout, ungültige Provider-Antwort
und deklarative Degradation. Ein Erfolg enthält Result- und Execution-ID,
Provider, Capability, B1, immutable Ausgabefelder, Source Chains, Zeiten,
technischen Status, Bereitstellungsstatus, Review, Unsicherheit und Provenienz.

Ein Ergebnis ist ausschließlich ein Provider-Runtime-Ergebnis. Der Status
`PROVIDED_NOT_ACTIVATED` bestätigt ausdrücklich, dass daraus keine automatische
Guardian-Antwort entsteht.

Die Output Boundary prüft strukturell Provider, Capability, B1-Ausgabeart,
erlaubte und erforderliche Felder, Feldzahl und Wertlängen. Typisierte B2-,
B3-, Zustandsänderungs- und Tool-Ausgabearten werden abgelehnt. Es gibt keine
semantische Fachprüfung, allgemeine Inhaltsmoderation, Prompt-Injection-
Erkennung oder NLP-Pipeline.

## Fehler, Timeout, Abbruch und kontrollierte Degradation

Zulässige fail-closed Ergebnisse sind:

- kein Aufruf bei gescheiterter Vorprüfung,
- `PROVIDER_ERROR` bei technischem Adapterfehler,
- `TIMED_OUT` bei typisiertem Provider-Timeout,
- `INVALID_PROVIDER_RESPONSE` bei ungültiger Antwort oder Output Boundary,
- `DEGRADED` nur bei ausdrücklich so geliefertem typisiertem Ergebnis.

Ein optionaler allgemeiner Degradationshinweis muss bereits im Execution
Request bereitgestellt sein. Die Runtime erzeugt keinen Hinweis, wechselt
keinen Provider, wiederholt keinen Aufruf und deutet das Ergebnis nicht als B2
oder B3 um. Ein neuer Versuch benötigt einen ausdrücklich neuen Execution
Request.

## Execution Evidence und Receipt

Jeder Ausführungsversuch erzeugt immutable `RuntimeExecutionEvidence` und ein
immutable `RuntimeExecutionReceipt`. Sie dokumentieren Execution, Invocation-
Boundary, Provider, Authorization, tatsächlich durchgeführte Prüfungen,
Provider-Aufruf ja/nein, technischen und fachlichen Abschluss, Fehler- oder
Blockierungsgrund, Adapter, Source Chains, Zeiten, Review und Provenienz.

IDs und Zeitpunkte werden ausdrücklich bereitgestellt. Es gibt keine Uhr- oder
Zufallsabhängigkeit für Nachweisidentitäten, keine Persistenz, kein Audit Log,
keine Signatur und keine automatische Registrierung.

## Fail-closed-Verhalten

Die Runtime ruft den Provider nur nach vollständig erfolgreicher Vorprüfung.
Jede Abweichung stoppt den Pfad. Fehler führen nie zu Fallback, Retry,
Reautorisierung, Capability-Erweiterung oder automatischer Antwortaktivierung.

## Verhältnis zu ADR-0047 bis ADR-0050

- ADR-0047 bleibt für B1, Quellen, Wahrhaftigkeit und Entpersonalisierung
  verbindlich.
- ADR-0048 bleibt einzige Quelle für Authority, Capability, Verantwortung und
  Kontrollstufen.
- ADR-0049 bleibt einzige Quelle für Provider Identity, Authorization und
  Lifecycle Evidence.
- ADR-0050 bleibt einzige Invocation-Entscheidungs- und Nachweisgrenze.
- ADR-0051 führt nur den von diesen Nachweisen bereits erlaubten engen Aufruf
  aus und verändert keinen vorgelagerten Vertrag.

## Nicht-Ziele

- keine B2- oder B3-Runtime,
- keine Schreib-, privilegierte, Werkzeug- oder Workflowoperation,
- keine Provider-Auswahl, kein Fallback und keine Retry-Logik,
- kein Scheduling oder allgemeiner Execution Owner,
- keine automatische Authorization, Reautorisierung oder Capability-Erweiterung,
- keine Antwort-, Journey-, Resolution-, Rechte- oder Nutzerzustandsänderung,
- keine allgemeine Agenten-, Tool-, Provider- oder Research-Runtime,
- keine freie oder personenbezogene Webrecherche,
- keine Entpersonalisierungs- oder Einwilligungs-Runtime,
- keine Credential-, Token- oder Secret-Verwaltung,
- keine Persistenz, kein Audit Log, keine UI,
- keine allgemeine Policy-, IAM- oder RBAC-Engine,
- keine Zukunftshooks für B2, B3, Schreiben, Tools oder Workflows.

## Konsequenz

ZONVAA besitzt erstmals einen real ausführenden, aber eng begrenzten Port. Die
Ausführungsmacht endet an einem bereits validierten B1-`READ_ONLY`-Aufruf. Ohne
kanonisch autorisierten externen Provider bleibt die tatsächliche externe
Anbindung blockiert; die Verträge, Vorprüfungen, der Executor und die
kontrollierte Adapterintegration sind vollständig testbar.
