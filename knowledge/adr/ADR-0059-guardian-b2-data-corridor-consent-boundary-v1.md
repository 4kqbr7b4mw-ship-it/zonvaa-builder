# ADR-0059 – Guardian B2 Data Corridor and Consent Boundary v1

Status: RATIFIZIERT UND IMPLEMENTIERT

Datum: 02.08.2026

## Kontext

B2 beginnt mit dem Datenkorridor, nicht mit Authority. Datenfluss ist die erste B2-Machtgrenze;
der Korridor existiert vor jeder Authority. Er beschreibt nur,
welche bereits typisierten Datenklassen, Quellen und Flussrichtungen eine
spätere B2-Verarbeitung erreichen dürften. Er bewegt und verarbeitet keine
Daten.

Die begrenzte institutionelle Freigabe
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0059-V1` trägt ausschließlich diesen
Vertrags-, Validierungs- und Dokumentationsbaustein. Weitere B2-Pakete und jede
B2-Runtime bleiben gesperrt.

## Entscheidung

ADR-0047 D1–D6 werden vollständig und unverändert übernommen. D3 ist eine
notwendige, aber niemals hinreichende Voraussetzung. Jeder gültige Korridor
bindet zusätzlich eine aktive, zweckgleiche AAV-Autorisierung und dieselbe
Autorisation über eine kanonische UODL-Referenz. AAV und UODL werden nicht
dupliziert und ihre Objekte nicht verändert.

`GOV-SYSTEM-BEHAVIOR-ONLY-1` bleibt unverändert bindend. Der Betriebsblock
bleibt vollständig blind gegenüber B2-Inhalten: Eine Weitergabe an Runtime,
Observation, Audit, Operational Memory, Physical Persistence, Metrics oder
Notifications ist typisiert verboten.

### Zulässiger Korridor

Zulässig sind ausschließlich bestätigte persönliche Tatsachen, ausdrücklich
autorisierte Dokumentfragmente, zweckgebundene Kontextattribute,
depersonalisierter Kontext und allgemeine nicht personenbezogene Information.
Zulässige Quellen und Flussrichtungen sind geschlossen typisiert. Der Vertrag
bewegt, lädt, interpretiert oder speichert nichts.

### Consent Boundary

Die Consent Boundary bindet genau einen Korridor, dessen Zweck, dessen
Datenklassenscope, alle D3-Voraussetzungen, eine Widerrufsreferenz, erlaubte
Nutzungen und den vollständigen Katalog verbotener Nutzungen. D3 allein
autorisiert weder Verarbeitung noch Authority, Provider, Invocation oder
Runtime.

### Data Classification und Depersonalisierung

Jede Datenklasse wird unveränderlich als Sensitivitätsklasse,
personenbezogen/nicht personenbezogen, depersonalisierbar und niemals zulässig
klassifiziert. Die Depersonalization Boundary bindet D1–D6, die bereits
festgelegten zu entfernenden Identifikatoren, zulässige Restdaten und verbotene
Restidentifikatoren. Sie implementiert keinen Algorithmus und erfindet keine
neue Depersonalisierungslogik.

### Negative Corridor Rules

Ein eigener immutable Vertragsbestandteil führt vollständig:

- nicht zulässige Datenklassen,
- nicht zulässige Datenquellen,
- nicht zulässige Flussrichtungen,
- nicht zulässige Kombinationen,
- verbotene Restidentifikatoren,
- verbotene Zweckänderungen,
- verbotene Ziele Runtime, Observation, Audit, Operational Memory, Physical
  Persistence, Metrics und Notifications.

Fehlt eine dieser Regelgruppen oder ein kanonischer Eintrag, ist der Vertrag
ungültig.

## Validierung und Snapshot

Der deterministische Validator prüft ausschließlich Struktur, Typen,
Vollständigkeit, Referenz- und Objektidentität, Review und Provenienz. Er gibt
bei Erfolg dasselbe Package-Objekt zurück. Er verarbeitet keine Inhalte und
trifft keine fachliche Entscheidung. Der read-only Snapshot projiziert nur die
identischen bereitgestellten Verträge.

## Nicht-Ziele

Keine Runtime. Keine Authority. Keine Authorization Grants. Keine Invocation.
Keine Provider. Keine personenbezogene Verarbeitung oder Speicherung. Keine
Observation oder Audit-Auswertung personenbezogener Inhalte. Keine Integration
in Operational Memory oder Physical Persistence. Keine Metrics, Notifications,
Workflows, Werkzeuge oder UI. Keine automatische Einwilligung,
Depersonalisierung, Datenbewegung oder Zweckänderung.
