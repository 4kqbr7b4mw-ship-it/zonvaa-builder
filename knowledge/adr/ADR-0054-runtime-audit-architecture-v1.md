# ADR-0054 – Runtime Audit Architecture v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0051 begrenzt die reale Read-only-B1-Runtime, ADR-0052 dokumentiert
Incident- und No-Incident-Nachweise und ADR-0053 legt fest, welche technischen
Systemereignisse beobachtet werden dürfen. Eine getrennte Architektur für die
Prüfung dieser bereits vorhandenen Nachweise fehlte bislang.

## Entscheidung

Runtime Audit Architecture v1 ist eine immutable, deterministische und
ausschließlich nachweisprüfende Governance-Schicht. Audit ist
Nachweisprüfung, keine Runtime-Ausführung. Audit ist von Observation, Runtime
Evidence und Incident Evidence getrennt und verändert keines dieser Objekte.

Der kontrollierte Pfad lautet:

```text
Observation Profile und Scope
→ B1 Runtime Execution und Runtime Evidence
→ Incident oder scope-gebundene No-Incident Evidence
→ Runtime Audit Profile und Scope
→ Runtime Audit Evidence
→ read-only Runtime Audit Resolution Snapshot
```

Audit darf ausschließlich behaupten, was durch die bereitgestellten,
identitätstreuen Nachweise und den ausdrücklich gebundenen Observation Scope
gedeckt ist. Fehlende Evidence ist kein No-Incident-Nachweis. Nicht beobachtete
Bereiche bleiben ausdrücklich nicht beurteilbar.

## Audit Profile

`RuntimeAuditProfile` führt Profile-ID, Version, Name, Zweck, referenziertes
Observation Profile samt Version und Scope, zulässige und ausgeschlossene
Audit-Gegenstände, erforderliche Evidence-Typen und Vollständigkeitsstufe,
Verantwortung, Änderungsakteur, Genehmigung, Review, Begründung, optionale
Vorgängerreferenz und Provenienz.

Audit Profiles sind versioniert und begründungspflichtig. Sie dürfen weder
Nutzerbeobachtung noch Nutzerprofilbildung, Nutzerinhalte, Nutzungsthemen oder
Nutzungsstatistiken zulassen. Runtime-, Modell-, Provider- und Tool-Akteure
dürfen ein Audit Profile nicht allein erstellen oder ändern. Profile werden
an eine konkrete, validierte Observation-Profile-Version gebunden. Eine neue
Version ersetzt oder verändert keine frühere Version.

## Audit Scope

`RuntimeAuditScope` bindet ein Audit Profile an eine konkrete Runtime
Execution, einen Observation Scope und eine bereitgestellte zeitliche Grenze.
Er partitioniert vollständig und widerspruchsfrei:

- beobachtete und ausdrücklich nicht beobachtete Runtime-Ereignisse,
- verfügbare und fehlende Evidence-Typen,
- prüfbare und ausdrücklich nicht prüfbare Aussagen.

Eine prüfbare Aussage darf sich nur auf ein im gebundenen Observation Scope
beobachtetes Systemereignis beziehen. Fehlende Nachweise und nicht prüfbare
Bereiche bleiben sichtbar und werden nicht ergänzt oder umgedeutet.

## No-Incident Observation Binding

`RuntimeNoIncidentEvidence` führt verbindlich das geltende Observation
Profile, dessen Version, den Observation Scope, die beobachteten und
ausdrücklich nicht beobachteten Ereignisse sowie tatsächlich durchgeführte
und nicht durchgeführte Prüfungen.

No-Incident Evidence ohne diese Observation-Scope-Bindung ist ungültig. „Kein
Vorfall erkannt“ gilt ausschließlich innerhalb des gebundenen
Beobachtungsumfangs. Ein nicht beobachtetes Ereignis darf nicht als
vorfallsfrei bezeichnet werden. Fehlende Beobachtung ist keine erfolgreiche
Prüfung und fehlende Evidence ist kein No-Incident-Nachweis.

ADR-0053 schließt Nutzerbeobachtung bereits auf Vertragsebene durch einen
geschlossenen technischen Ereigniskatalog und verpflichtend verbotene
Kategorien für Nutzerverhalten, Nutzerprofile, Nutzerinhalte,
Interaktionsmuster und Nutzungsstatistiken aus. ADR-0054 übernimmt und
verschärft diese Grenze nicht semantisch, sondern bindet Audit ausschließlich
an die validierten ADR-0053-Objekte und schließt zusätzlich Nutzungsthemen als
Audit-Gegenstand typisiert aus.

## Audit Evidence und Ergebnisse

`RuntimeAuditEvidence` dokumentiert Profile-, Scope-, Execution-, Observation-,
Runtime- und Incident- beziehungsweise No-Incident-Referenzen, die geprüfte
Nachweiskette, bestandene, fehlgeschlagene und nicht ausführbare Prüfungen,
erkannte Nachweislücken, Vollständigkeit, Review und Provenienz.

Zulässige Ergebnisse sind:

- `COMPLETE_AND_CONSISTENT`
- `COMPLETE_WITH_INCIDENT`
- `INCOMPLETE_EVIDENCE`
- `OBSERVATION_SCOPE_INSUFFICIENT`
- `INCONSISTENT_EVIDENCE`
- `NOT_AUDITABLE`
- `BLOCKED_BY_GOVERNANCE_GAP`

Ein Audit-Ergebnis ist kein Qualitätsurteil über einen Nutzer, dessen Verhalten
oder fachliche Inhalte.

## Validator und Snapshot

Der `RuntimeAuditValidator` verwendet die bestehenden Observation- und
Incident-Validatoren. Er prüft ausschließlich Strukturen, Versionen,
Vorgängerreferenzen, Objektidentitäten, Runtime-, Provider-, Execution- und
Capability-Bindungen, die Exklusivität von Incident und No-Incident, die
vollständige No-Incident-Scope-Bindung, Evidence-Lücken, zulässige Aussagen,
Review und Provenienz. Bei Erfolg wird dasselbe Package unverändert
zurückgegeben.

Der immutable `RuntimeAuditResolutionSnapshot` projiziert Audit Profile und
Scope, Observation Governance, Runtime Execution und Evidence, Incident oder
No-Incident Evidence, Ergebnis, Lücken, nicht prüfbare Bereiche, Review und
Provenienz. Er erzeugt und ergänzt keine Nachweise, erkennt keine Incidents,
leitet kein No-Incident ab, verändert kein Ergebnis, aktiviert keine Runtime,
persistiert nichts und versendet keine Benachrichtigung.

## B2/B3 Operational Gate

Eine Architekturentscheidung oder Implementierung für eine B2- oder
B3-Runtime ist unzulässig, solange nicht beide Bedingungen erfüllt sind:

1. Runtime Audit Architecture v1 ist ratifiziert, implementiert und validiert.
2. Der spätere Operational-Memory-Block mit Persistenz, Metriken und
   Benachrichtigungen ist ratifiziert, implementiert und validiert.

Diese Gate-Regel erweitert B1 nicht, autorisiert weder B2 noch B3 und führt
keine Runtime-Funktion ein. Sie verhindert ausschließlich eine vorzeitige neue
Machtstufe. Der Operational-Memory-Block ist mit ADR-0054 ausdrücklich nicht
implementiert.

## Nutzer- und Machtgrenze

Audit prüft ausschließlich Systemverhalten, niemals Nutzerverhalten. Es darf
keine Nutzerprofile, Nutzungsmuster, Nutzungsstatistiken, themenbezogene
Nutzeranalysen oder personenbezogenen Auswertungen erzeugen. Audit Profiles
und Scopes aktivieren keine Observation, Runtime, Capability, Werkzeuge oder
Workflows und autorisieren keinen Provider.

Diese Audit-Grenze erbt zusätzlich die kanonische Mindestregel
`GOV-SYSTEM-BEHAVIOR-ONLY-1`. Ihre strengeren Scope-, Evidence- und
Nichtbeurteilbarkeitsregeln bleiben unverändert.

## Nicht-Ziele

- keine Runtime-Erweiterung, B2-Runtime oder B3-Runtime,
- keine automatische Audit-, Incident- oder No-Incident-Erzeugung,
- keine automatische Reparatur, Rekonstruktion oder Interpretation,
- keine Persistenz, Datenbank, Dateispeicherung oder dauerhaftes Audit-Log,
- keine Metriken, Benachrichtigungen, Telemetrie oder Analytics,
- keine Nutzeranalyse, Profilbildung, Nutzungsstatistik oder Themenaggregation,
- keine Provider-Auswahl, Retry-, Fallback- oder Kontaktlogik,
- keine Workflow-, Werkzeug- oder Capability-Aktivierung,
- keine UI, Compliance-, SIEM-, Monitoring- oder Analytics-Plattform,
- keine Platzhalter-Hooks für spätere Betriebsfunktionen.

## Konsequenz

ZONVAA kann die Vollständigkeit und Konsistenz einer bereitgestellten
Read-only-B1-Nachweiskette innerhalb eines konkret genehmigten Observation
Scopes prüfen. Jede Lücke und jeder nicht beobachtete Bereich bleibt sichtbar.
Die Architektur erzeugt keine neue Macht und enthält noch keinen
Operational-Memory-Block.
