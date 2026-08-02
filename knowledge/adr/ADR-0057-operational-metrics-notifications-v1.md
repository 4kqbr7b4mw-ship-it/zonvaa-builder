# ADR-0057 – Operational Metrics and Notifications v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0053 bis ADR-0056 begrenzen technische Observation, Audit,
Operational Memory und physische Persistenz. Der in ADR-0054 und ADR-0055
verlangte Betriebsblock benötigt zusätzlich eng begrenzte Metrik- und
Benachrichtigungsnachweise, ohne daraus Monitoring-, Analyse- oder
Zustellungsmacht abzuleiten.

## Entscheidung

Operational Metrics folgen physischer Persistenz, niemals umgekehrt. Eine
Metrik darf ausschließlich einen bereits bereitgestellten Wert dokumentieren,
der an validierte Observation-, Audit-, Operational-Memory- und Physical-
Persistence-Nachweise gebunden ist.

Operational Notifications folgen einer validierten Metrik oder einem
ausdrücklich bereitgestellten, beobachteten und physisch referenzierten
Systemereignis. Eine Notification Evidence dokumentiert ausschließlich eine
bereits bereitgestellte Benachrichtigungsentscheidung. Sie erzeugt keine
Nachricht und stellt nichts zu.

Beide Schichten werten ausschließlich Systemverhalten aus. Nutzerverhalten,
Nutzeridentitäten, Nutzersegmente, Gesprächsinhalte, Themen, Lebensbereiche,
Häufigkeiten pro Nutzer, Nutzungsmuster und Nutzerprofile sind strukturell
ausgeschlossen.

## Operational Metric Definition

`OperationalMetricDefinition` ist immutable, versioniert und begründet. Sie
führt technische Systemereignisse als vollständige Partition aus erlaubten und
ausdrücklich ausgeschlossenen `RuntimeObservationEvent`-Werten, kanonische
Operational-Memory-Artefakttypen, eine geschlossene Aggregationsregel, eine
geschlossene Maßeinheit, eine bereitgestellte Zeitgrenze sowie konkrete
Observation- und Audit-Profile, Verantwortung, Genehmigung, Review und
Provenienz.

Die Aggregationsregeln sind keine Formeln und keine Berechnungsbefehle. Sie
beschreiben ausschließlich die Art eines bereits bereitgestellten Wertes. Freie
Formeln, Skripte, Ausdrücke, Code oder Abfragen sind nicht darstellbar.

Metrikdefinitionen dürfen nicht einseitig durch Runtime-, Modell-, Provider-
oder Tool-Akteure erstellt oder geändert werden. Versionen ab v2 benötigen eine
deklarative Vorgängerreferenz; bestehende Definitionen bleiben unverändert.

## Operational Metric Observation

`OperationalMetricObservation` dokumentiert Metrikdefinition und -version,
vollständig referenzierte Physical-Persistence-Records und Operational-Memory-
Artefakte, Zeitgrenze, bereitgestellten Wert, Maßeinheit, Vollständigkeit,
fehlende Eingangsartefakte, Unsicherheit, Review und Provenienz.

Der Wert wird nicht berechnet, normalisiert, verglichen oder interpretiert.
Fehlende Eingangsartefakte bleiben typisiert sichtbar. Eine Observation darf
nicht `COMPLETE` behaupten, solange ein von der Definition verlangter
Artefakttyp fehlt.

## Metric Validator und Snapshot

Der `OperationalMetricValidator` verwendet zuerst den bestehenden
`PhysicalOperationalPersistenceValidator`, der wiederum Operational Memory,
Audit und Observation validiert. Danach prüft er ausschließlich:

- Definition, Version und vollständige technische Ereignispartition,
- Bindung an genau ein vorhandenes Observation- und Audit-Profil,
- Ereignisse innerhalb des validierten Observation Scopes,
- Zeitgrenzen innerhalb des Audit- und Definitionsumfangs,
- vollständige Physical-Persistence- und Memory-Referenzen,
- kanonische Artefakttypen und sichtbare fehlende Eingänge,
- passende Maßeinheit, Vollständigkeit, Review und Provenienz,
- verbotene Änderungsakteure.

Bei Erfolg bleibt dasselbe Package unverändert. Der immutable
`OperationalMetricSnapshot` projiziert dieselben Definitionen, Observations,
Persistenzrecords, Werte, Einheiten, Zeitgrenzen, Lücken, Unsicherheit, Review
und Provenienz. Er berechnet, persistiert oder verändert nichts.

## Notification Policy

`OperationalNotificationPolicy` ist immutable, versioniert und begründet. Ihre
Quelle ist entweder genau eine Metrikdefinition oder genau ein typisiertes
`RuntimeObservationEvent`. Geschlossene Auslösebedingungen beschreiben nur den
bereitgestellten Entscheidungsgrund; sie sind keine ausführbare Regel- oder
Eskalationsmaschine.

Empfängerkategorien sind geschlossen auf betriebliche Leitung, Governance-
Review und Vertrauensrat. Endnutzer sind keine Empfängerkategorie. Zulässige
Nachrichtentypen sind rein betrieblich. Jede Policy muss Nutzeridentität,
personenbezogene Daten, Gesprächsinhalte, Nutzerprofile, Nutzungsthemen,
Lebensbereiche und generierten freien Text ausdrücklich ausschließen.

Policies dürfen nicht einseitig durch Runtime-, Modell-, Provider- oder
Tool-Akteure erstellt oder geändert werden.

## Operational Notification Evidence

`OperationalNotificationEvidence` dokumentiert eine bereits bereitgestellte
Entscheidung mit einem der Statuswerte:

- `NOT_REQUIRED`,
- `PREPARED`,
- `BLOCKED`,
- `SUPPRESSED`,
- `DELIVERED_EXTERNALLY_DECLARED`.

`PREPARED` führt ausschließlich eine bereits bereitgestellte Nachrichtreferenz
und einen erlaubten Nachrichtentyp. Freier Nachrichtentext ist nicht Teil des
Vertrags. `DELIVERED_EXTERNALLY_DECLARED` ist ausschließlich ein bereitgestellter
externer Nachweis und muss zum deklarativen Deliverystatus passen. Das Paket
sendet weder E-Mail, SMS, Push, Slack, Webhook noch eine andere Nachricht.

## Notification Validator und Snapshot

Der `OperationalNotificationValidator` validiert Physical Persistence und bei
Metrikbezug das identische `OperationalMetricPackage`. Er prüft Policy-Version,
Quellart, Metrik- oder Ereignisreferenz, Observation Scope, Auslösebedingung,
Entscheidungsstatus, Schweregrad, betriebliche Empfängerkategorie,
Nachrichtreferenz, externen Zustellnachweis, Review und Provenienz.

Er berechnet keinen Trigger, erkennt keinen Incident, eskaliert nicht, erzeugt
keine Nachricht und stellt nichts zu. Bei Erfolg bleibt dasselbe Package
unverändert. Der immutable Notification Snapshot projiziert lediglich Policy,
Quelle, Evidence, Status, Schweregrad, Empfängerkategorie, Nachrichtreferenz,
Deliverystatus, Review und Provenienz.

## Absolute Nutzergrenze

Kanonische schichtübergreifende Mindestgrenze ist
`GOV-SYSTEM-BEHAVIOR-ONLY-1`. Die nachfolgenden strengeren Metrics- und
Notifications-Verbote bleiben unverändert.

Die Nicht-Nutzerdaten-Grenzen aus ADR-0053 bis ADR-0056 werden unverändert
geerbt. Der geschlossene technische Ereigniskatalog und die geschlossenen
Artefakttypen verhindern Nutzerbeobachtung auf Vertragsebene. Es gibt keine
Nutzeranalyse, Nutzungsstatistik, Nutzersegmentierung, Profilbildung,
Gesprächs- oder Themenanalyse und keine Lebensbereichsauswertung.

## Operational-Memory-Block und B2/B3-Gate

Der Operational-Memory-Block gilt erst als vollständig geschlossen, wenn alle
vier Bausteine ratifiziert, implementiert und validiert sind:

1. Operational Memory v1,
2. Physical Operational Persistence v1,
3. Operational Metrics v1,
4. Operational Notifications v1.

Mit ADR-0055, ADR-0056 und diesem ADR sind diese vier begrenzten Bausteine im
Repository vorhanden, implementiert und validiert. Damit ist der Block
`Operational-Memory-Block` auf Vertragsebene vollständig geschlossen.

Diese Feststellung gibt weder B2 noch B3 frei. Sie erlaubt keine B2- oder
B3-Runtime, keine Schreiboperation und keine neue Capability. Nach Abschluss
dieses Pakets darf lediglich eine gesonderte Architekturentscheidung über eine
mögliche B2-Stufe wieder aufgenommen werden. Jede Implementierung benötigt
weiterhin einen eigenen begrenzten Auftrag.

## Nicht-Ziele

- keine Nutzeranalyse, Nutzungsstatistik, Profilbildung oder Nutzersegmente,
- keine Gesprächs-, Themen-, Lebensbereichs- oder Häufigkeitsanalyse pro Nutzer,
- keine freie Metrikberechnung, Formel-Engine, Skript- oder Codeausführung,
- keine Telemetrie-Erfassung oder automatische Evidenzerzeugung,
- keine automatische Incident- oder No-Incident-Erkennung,
- keine automatische Eskalation oder Zustandsänderung,
- keine externe Zustellung, E-Mail-, SMS-, Push-, Slack- oder Webhook-Anbindung,
- keine freie Text- oder Nachrichtengenerierung und keine Endnutzeransprache,
- keine neue Persistenztechnologie oder Veränderung physischer Records,
- keine Löschung, Archivierung, Replikation, Retry- oder Fallback-Logik,
- keine B2-/B3-Runtime, Schreiboperation oder Provider-Auswahl,
- keine Workflow-, Werkzeug- oder Capability-Aktivierung,
- keine UI oder allgemeine Monitoring-, Analytics-, Alerting- oder
  Observability-Plattform,
- keine Platzhalter-Hooks für spätere Machtfunktionen.

## Konsequenz

ZONVAA kann bereits bereitgestellte technische Metrikwerte und betriebliche
Benachrichtigungsentscheidungen vollständig an validierte, physisch referenzierte
Systemnachweise binden. Das System berechnet, eskaliert, sendet und aktiviert
weiterhin nichts.
