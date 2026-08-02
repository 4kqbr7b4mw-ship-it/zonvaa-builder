# ADR-0052 – Runtime Incident Evidence v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0046 E6 verlangt, zusätzliche Komplexität an dokumentierte Vorfälle oder
glaubhafte Schadensrisiken zu binden. Die Read-only B1 Provider Runtime aus
ADR-0051 liefert bereits immutable Result-, Evidence- und Receipt-Objekte für
reale, kontrollierte Ausführungen. Bislang fehlte ein eigener, rein
nachweisender Vertrag, der einen bereits eingetretenen Runtime-Vorfall oder das
ausdrücklich erklärte Ausbleiben eines erkannten Vorfalls dokumentiert.

## Entscheidung

Runtime Incident Evidence v1 ergänzt vier immutable Bausteine:

1. `RuntimeIncidentEvidence` dokumentiert einen bereits bereitgestellten
   Vorfall mit Execution-, Provider- und Runtime-Referenz, typisiertem
   Incident-Typ, Severity, Zeitpunkt, Capability, Betriebsart, technischer und
   fachlicher Ursache, Reviewstatus und Provenienz.
2. `RuntimeNoIncidentEvidence` dokumentiert ausdrücklich eine erfolgreiche
   Ausführung und die bereitgestellte Erklärung, dass keine Abweichung erkannt
   wurde. Dieser Nachweis ist weder Qualitätsurteil noch Garantie.
3. `RuntimeIncidentPackage` bindet genau eine der beiden Evidenzformen an den
   originalen Execution Envelope und das originale Runtime Outcome.
4. `RuntimeIncidentSnapshot` projiziert Runtime, Execution, Incident oder
   No-Incident Evidence, Severity, Status, Review und Provenienz read-only.

Der deterministische `RuntimeIncidentValidator` prüft ausschließlich
strukturelle und referenzielle Konsistenz. Er verwendet das bereits erzeugte
Runtime Outcome als Nachweisgrundlage. Incident-Typ, Severity, Ursachen und die
No-Incident-Erklärungen werden vollständig bereitgestellt; der Validator
erkennt, erfindet oder bewertet sie nicht.

## Incident-Typen und Severity

Die v1-Typen entsprechen den bereits vorhandenen Runtime-Endzuständen:

- `PROVIDER_TECHNICAL_ERROR` – `ERROR`
- `PROVIDER_TIMEOUT` – `ERROR`
- `OUTPUT_BOUNDARY_REJECTION` – `ERROR`
- `INVALID_PROVIDER_RESPONSE` – `ERROR`
- `CONTROLLED_DEGRADATION` – `WARNING`
- `PRE_EXECUTION_BLOCK` – `WARNING`

Diese feste Zuordnung ist eine strukturelle v1-Invariante. Sie führt weder eine
Incident-Erkennung noch eine freie Severity-Bewertung ein. Eine abweichende
bereitgestellte Kombination wird fail-closed abgelehnt.

## Validierungsgrenzen

Der Validator prüft:

- kanonische Runtime-, Execution- und Provider-Referenzen,
- identische ursprüngliche Runtime-Objekte und deren interne Referenzen,
- genau eine Incident- oder No-Incident-Evidence je Execution,
- eindeutige Identitäten,
- typisierte Incident-Typen und konsistente Severity,
- Übereinstimmung mit dem bereits vorliegenden Runtime-Endstatus,
- timezone-aware Zeitpunkte innerhalb der dokumentierten Execution,
- vollständige und konsistente Provenienz sowie Reviewstatus.

Bei Erfolg gibt er dasselbe Package unverändert zurück. Der Snapshot behält
dieselben Execution-, Outcome- und Evidence-Objekte.

## Keine neue Macht

Das Paket implementiert ausdrücklich Folgendes nicht:

- keine Runtime-Erweiterung oder Provider-Ausführung,
- automatische Incident- oder Gefahrenerkennung,
- automatische Fehlerbehebung, Retry- oder Fallback-Logik,
- Persistenz, Audit-System oder Audit-Log,
- Metriken, Benachrichtigungen oder Kontaktaufnahme,
- Workflow-, Werkzeug- oder Capability-Aktivierung,
- Zustandsänderung oder UI.

Der Baustein dokumentiert ausschließlich bereits eingetretene oder
ausdrücklich ausgebliebene Ereignisse. Er verändert keine Runtime-Entscheidung
und löst keine Reaktion aus.

## Folgen

E6-Vorfälle der realen B1-Runtime können nun reproduzierbar, referenziell und
reviewbar festgehalten werden. Ein No-Incident-Nachweis bleibt bewusst auf die
deklarierte, geprüfte Ausführung begrenzt und behauptet weder Fehlerfreiheit
noch allgemeine Qualität.
