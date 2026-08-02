# ADR-0053 – Runtime Observation Governance v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0051 begrenzt die erste reale Read-only-B1-Runtime. ADR-0052 dokumentiert
bereits eingetretene oder ausdrücklich ausgebliebene Runtime-Vorfälle. Für die
verfassungsrechtliche Kontrolle fehlt noch eine explizite Grenze dafür, welche
technischen Systemereignisse grundsätzlich beobachtet werden dürfen.

## Entscheidung

Runtime Observation Governance v1 ist eine ausschließlich beschreibende
Governance-Schicht. Ein versioniertes und begründungspflichtiges Observation
Profile benennt Zweck, zulässige technische Kategorien, verbotene Kategorien,
Verantwortung, Genehmigung, Review und Provenienz. Ein zugehöriger versionierter
Observation Scope partitioniert den geschlossenen Katalog technischer
Runtime-Ereignisse vollständig und überschneidungsfrei in:

- ausdrücklich beobachtbare Systemereignisse und
- ausdrücklich nicht beobachtete Systemereignisse.

Der Vertrag beobachtet selbst nichts. Er stellt weder Collector noch Hook,
Telemetry Client, Event Listener, Analysefunktion oder Runtime-Anbindung bereit.
Keine Runtime-Komponente darf außerhalb des genehmigten Scopes beobachten;
eine technische Durchsetzung dieser Regel ist nicht Teil von v1.

## Trennung von Observation, Evidence und Incident

- **Observation Governance** bestimmt ausschließlich, welche Arten bereits
  typisierter Systemereignisse beobachtet werden dürften.
- **Runtime Evidence** dokumentiert konkrete, bereits erfolgte technische
  Ausführungs- und Prüfereignisse.
- **Runtime Incident Evidence** dokumentiert einen bereits bereitgestellten
  Vorfall oder das ausdrücklich erklärte Ausbleiben eines erkannten Vorfalls.

Observation erzeugt weder Evidence noch Incident. Evidence und Incident
erweitern keinen Observation Scope. Keine dieser Schichten aktiviert eine
andere.

## Absolute Nutzergrenze

Kanonische schichtübergreifende Mindestgrenze ist
`GOV-SYSTEM-BEHAVIOR-ONLY-1` unter
`governance/system-behavior-only-rule.md`. Die nachfolgenden strengeren
Observation-Regeln bleiben unverändert maßgeblich.

Observation beobachtet ausschließlich Systemverhalten. Observation beobachtet
niemals Nutzerverhalten. Verboten sind insbesondere:

- Nutzerverhalten,
- Nutzerprofile,
- Nutzerinhalte,
- Interaktionsmuster,
- Nutzungsstatistiken.

Diese Bereiche müssen in jedem Profile sowohl als verboten als auch als
ausdrücklich nicht beobachtet geführt werden. Es gibt keine Profilbildung,
Verhaltensanalyse, Nutzeranalyse, personenbezogene Auswertung oder Telemetrie.

## Observation Profile

`RuntimeObservationProfile` ist immutable und enthält:

- Profile-ID und positive ganzzahlige Version,
- Name, Zweck und Observation-Scope-Referenz,
- ausdrücklich nicht beobachtete Bereiche,
- zulässige und verbotene Observation-Kategorien,
- Verantwortungsreferenz,
- Genehmigungsstatus und Genehmigungsreferenz,
- Reviewstatus und Reviewreferenz,
- Änderungsakteur und Authority-Referenz,
- optionale Vorgängerreferenz,
- Provenienz.

Profile sind versioniert und begründungspflichtig. Spätere Versionen
referenzieren das unmittelbar vorhergehende Profile und tragen ihre eigene
vollständige Provenienz. Bestehende Profile bleiben unverändert.

Observation Profiles dürfen nicht einseitig durch die Runtime geändert werden.
Als Änderungsakteure sind ausschließlich bereits kanonische menschliche oder
institutionelle Governance-Akteursklassen zulässig. Deterministic Core,
Model Layer und Guardian dürfen kein Profile ändern.

## Observation Scope

`RuntimeObservationScope` enthält Scope-ID, Version, beobachtete technische
Runtime-Ereignisse, ausdrücklich nicht beobachtete technische
Runtime-Ereignisse, eine nicht leere Begründung und Provenienz.

Beide Mengen dürfen sich nicht überschneiden. Ihre Vereinigung muss den
vollständigen geschlossenen Katalog aus `RuntimeObservationEvent` abdecken.
Jedes beobachtete Ereignis benötigt eine im Profile ausdrücklich erlaubte
Systemkategorie. Es erfolgt keine automatische Ergänzung oder Interpretation.

## Validator und Snapshot

Der deterministische `RuntimeObservationGovernanceValidator` prüft:

- eindeutige Identitäten,
- positive, lückenlos referenzierte Versionen,
- konsistente Profile-, Scope- und Vorgängerreferenzen,
- widerspruchsfreie und vollständige Scope-Partitionierung,
- ausschließlich erlaubte Systemkategorien,
- die vollständige Nutzerbeobachtungs- und Profilbildungsgrenze,
- verbotene einseitige Änderungen durch Runtime- oder Modellakteure,
- vollständige Provenienz,
- Review- und Genehmigungsstruktur.

Bei Erfolg wird dasselbe Governance-Objekt unverändert zurückgegeben.
`RuntimeObservationSnapshot` projiziert ausschließlich dasselbe Profile und
denselben Scope mit Version, Status, Review und Provenienz. Er beobachtet,
analysiert, speichert und aktiviert nichts.

## Nicht-Ziele

ADR-0053 implementiert ausdrücklich keine:

- keine Runtime-Erweiterung oder Runtime-Anbindung,
- Incident-Erkennung oder Evidence-Erzeugung,
- automatische Profile- oder Scope-Änderung,
- Audit-Infrastruktur oder Persistenz,
- Metriken, Monitoring oder Benachrichtigungen,
- Profilbildung, Verhaltensanalyse oder Nutzeranalyse,
- Nutzungsstatistik oder Telemetrie,
- Event-Collector, Listener, Hook oder Analysefunktion,
- Workflow-, Werkzeug- oder Capability-Aktivierung,
- Zustandsänderung oder UI.

## Konsequenz

ZONVAA besitzt eine reviewbare Governance-Grenze für zulässige technische
Systembeobachtung, aber weiterhin keine Observation Runtime. Jede spätere
technische Beobachtungsfunktion benötigt eine eigene begrenzte Entscheidung
und muss fail-closed innerhalb eines genehmigten versionierten Profiles und
Scopes bleiben.
