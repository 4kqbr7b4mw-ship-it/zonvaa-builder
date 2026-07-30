# ADR-0040 – Versioned Review Decisions and Workflow Supersession

## Status

Accepted

## Kontext

ADR-0039 definiert einen unveränderlichen, versionierten Vertrag für genau
eine Chief-Architect-Entscheidung zu einem Implementierungsreview. Der dort
festgelegte physische Pfad lag jedoch unter
`knowledge/architecture_workflows/*/executions/`. Dieser gesamte lokale
Runtime-Baum wird absichtlich von Git ignoriert. Die Entscheidung war dadurch
lokal lesbar, aber nicht normal versionierbar und nach einem Checkout nicht
rekonstruierbar.

Der Architecture Operations Agent sucht Topics bisher als
case-insensitive Teilzeichenfolge. Mehrere eigenständige Workflows können
dasselbe Topic besitzen. Ohne einen ausdrücklichen Lifecycle-Vertrag darf
ZONVAA nicht anhand von Zeit, Commit, Status oder Dateialter bestimmen,
welcher Workflow kanonisch ist.

## Entscheidung 1: Versionierte Review-Entscheidungen

ADR-0039 bleibt fachlich gültig. Diese ADR korrigiert ausschließlich den
physischen kanonischen Ablageort. Das reviewzentrierte Artefakt liegt unter:

```text
knowledge/architecture_review_decisions/<review-id>.json
```

Der Dateiname ist an die validierte `review_id` gebunden. Der Bereich ist
nicht ignoriert und gehört zum versionierten Knowledge-System. Execution-,
Attempt- und sonstige Runtime-Artefakte unter `executions/` bleiben
vollständig ignoriert.

Der Store liest und schreibt neue Entscheidungen ausschließlich am neuen
kanonischen Pfad. Für lokale Version-1-Legacy-Dateien gilt:

- nur kanonisch vorhanden: kanonisches Artefakt verwenden,
- nur Legacy vorhanden: read-only lesbar, aber keine stille Migration,
- beide identisch: kanonisches Artefakt verwenden,
- beide unterschiedlich: strukturierter Konflikt,
- beschädigtes Artefakt: strukturierter Fehler.

Eine Migration ist eine explizite Schreiboperation. Sie erhält sämtliche
Felder einschließlich Decision-ID, Entscheidungszeitpunkt, Begründung,
Workflow-, Run-, Execution-, Commit- und Integrator-Referenzen. Read-only
Operations-Befehle erzeugen oder migrieren keine Datei.

## Entscheidung 2: Explizite Workflow-Supersession

ZONVAA führt einen unveränderlichen und versionierten
`ArchitectureWorkflowSupersession`-Vertrag ein. Das kanonische Artefakt liegt
unter:

```text
knowledge/architecture_workflow_supersessions/
<superseded-workflow-id>.json
```

Der Vertrag enthält Schema-Version, Supersession-ID, normalisierbares Topic,
supersedierten und kanonischen Workflow, Begründung, Zeitpunkt und
entscheidende Rolle. Beide Workflow-IDs und ihre Topics werden gegen den
bestehenden Workflow Store validiert.

Verbindliche Regeln:

- keine Selbst-Supersession,
- keine unbekannten Workflow-IDs,
- Topics müssen nach whitespace-stabiler, case-insensitiver Normalisierung
  übereinstimmen,
- ein supersedierter Workflow darf nicht zugleich kanonisch sein,
- Zyklen sind verboten,
- identische Wiederholung ist idempotent,
- widersprüchliche Zuordnung blockiert,
- historische Workflow-Artefakte bleiben unverändert.

Eine Supersession entsteht ausschließlich durch
`architecture workflow supersede`. Sie wird niemals aus Zeitstempeln,
Commit-Reihenfolge, Workflow-Status oder vorhandenen Reviews abgeleitet.

## Query-Vertrag

Topic-Abfragen werden in folgender Reihenfolge aufgelöst:

1. normalisierte exakte Treffer,
2. explizite Supersession innerhalb dieser Treffer,
3. sichere Mehrdeutigkeit, falls mehrere kanonische Treffer verbleiben,
4. Teiltreffer nur, wenn kein exakter Treffer existiert; auch dort gilt die
   explizite Supersession.

Direkte Abfragen über Workflow-, Run-, Execution- oder Review-ID bleiben
unverändert. Ein supersedierter Workflow bleibt über seine Workflow-ID
vollständig auffindbar und wird als supersediert mit kanonischem Workflow und
Supersession-ID angezeigt.

Mehrdeutigkeitsfehler enthalten neben den Workflow-IDs strukturierte
Kandidatendaten. `status` und `next` verwenden denselben Resolver.

## Reale Supersession

Für das Topic `Controlled Architecture Feedback Loop E2E Validation` gilt:

- superseded: `workflow-cc69d796a87b2cad`
- canonical: `workflow-43af40b39b5593f6`

Der kanonische Workflow ist der kontrollierte, vollständig validierte
End-to-End-Nachfolger mit Execution-Bridge-Herkunft, Implementation Review
und aufgezeichneter Chief-Architect-Entscheidung. Der supersedierte Workflow
bleibt als historischer Vorgang vollständig erhalten.

## Sicherheitsgrenzen

Diese Architektur:

- erzeugt keine neue Chief-Architect-Entscheidung,
- verändert keine Decision-ID und keinen Entscheidungszeitpunkt,
- startet keine Execution und erzeugt keinen Attempt,
- verändert keine Integrator-Reviews, Handovers oder historischen Workflows,
- öffnet den ignorierten Runtime-Baum nicht pauschal für Git,
- trifft keine automatische Supersession,
- verwendet keine semantische Ähnlichkeit.

## Konsequenzen

Chief-Architect-Review-Entscheidungen sind nach normalem Commit und Checkout
vollständig rekonstruierbar. Lokale Runtime-Daten bleiben vom versionierten
Knowledge-System getrennt. Identische Topics werden nur aufgrund eines
expliziten, auditierbaren Lifecycle-Vertrags eindeutig aufgelöst.

Der Supersession-Vertrag Version 1 erlaubt keine Änderung bestehender
Zuordnungen. Aufhebung, Kettenmigration oder Revision benötigt eine spätere
Architekturentscheidung.

## Teststrategie

Tests prüfen:

- Git-Sichtbarkeit ohne `git add -f`,
- weiterhin ignorierte Execution-/Attempt-Dateien,
- Statusrekonstruktion aus dem versionierten Decision-Artefakt,
- Legacy-Lesen, explizite Migration und Konflikte,
- exakte vor partieller Topic-Auflösung,
- case-insensitive Normalisierung,
- sichere Mehrdeutigkeit ohne Supersession,
- direkte Auffindbarkeit historischer Workflows,
- Selbstreferenz, unbekannte IDs, unterschiedliche Topics, Zyklen,
  Idempotenz und Konflikte,
- CLI-Hilfe und ausbleibende Execution-/Attempt-Seiteneffekte.
