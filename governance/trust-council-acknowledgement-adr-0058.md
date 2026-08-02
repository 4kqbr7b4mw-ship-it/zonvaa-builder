# Vertrauensrats-Kenntnisnahme zu ADR-0058

Dokument-ID: `TRUST-ACK-ADR-0058-V1`

Status: Kenntnisnahme dokumentiert – ordentliche Vertrauensratsbestätigung ausstehend

Normstufe: C2-Verfahrensnachweis

Dokumentversion: 1.0

Kenntnisnahmedatum: 02.08.2026

## Bezug und Zweck

Dieses Dokument weist ausschließlich die institutionelle Kenntnisnahme
des Vertrauensrats zu
`knowledge/adr/ADR-0058-guardian-b2-architecture-v1.md`.

Sie betrifft Vetodomäne 2: Datenverwendung und externe Recherche. Die Kenntnisnahme
erteilt keine Zustimmung, Autorisierung oder Freigabe und ersetzt weder das
Prüf- und Vetoverfahren der Governance Charter noch eine gesonderte spätere
Architektur- oder Implementierungsentscheidung.

## Beratungsgegenstand

Gegenstand ist ausschließlich die Kenntnisnahme der mit ADR-0058 ratifizierten
B2-Verfassungsarchitektur: Datenhoheit, Depersonalisierung, eigenständige
B2-Authority und Grants, Verbot eines B1→B2-Upgrades, Inhaltsblindheit des
Betriebsblocks sowie Widerrufs- und AAV-/UODL-Grenzen.

## Bestehendes bindendes Recht

- C1 Constitution: Nutzerhoheit, bewusste Autorisierung, persönliche
  Kontextisolation und Schutz vor stiller Garantieabschwächung.
- C2 Governance Charter: unabhängige Prüfung erheblicher Änderungen an
  Erhebung, Zweck, Zugriff, Weitergabe, Aufbewahrung und Löschung von
  Nutzerdaten.
- ADR-0030 und AAV: konkrete, zweck- und umfangsgebundene Autorisierung sowie
  getrennte unveränderliche Nachweise von Erteilung, Nutzung und Widerruf.
- ADR-0033 und UODL: User Ownership, Reference before Copy, Minimal Metadata,
  Explicit Consent, Privacy by Design und Provider Independence.
- ADR-0047: D1–D6, D3 und D3-UX sowie die Trennung von Modellschicht und
  deterministischem Kern.
- ADR-0048 bis ADR-0057: Authority-, Provider-, Invocation-, Runtime- und
  inhaltsblinde Betriebsgrenzen.

## Neue Architekturentscheidung

ADR-0058 definiert B2 als eigene Verfassungsstufe. B2 ist keine Erweiterung
der B1-Runtime. Vorgesehen sind eine eigene B2-Authority-Klasse, eigene Grants,
ein minimaler zweck-, zeit- und datenklassengebundener Datenkorridor,
vorgeschaltete Depersonalisierung sowie die vollständige Inhaltsblindheit des
Betriebsblocks.

D3 bleibt notwendig, ist aber nicht hinreichend. Eine B1-Autorisierung
autorisiert niemals B2.

### Datenhoheit und Depersonalisierungsgrenze

B2 darf nur einen ausdrücklich autorisierten, minimalen, zweck-, zeit- und
datenklassengebundenen Korridor erhalten. Direkte und nicht erforderliche
indirekte Identifikatoren werden vor B2 entfernt. Rohgespräche, vollständige
Understanding States, Hypothesen, T2-Beziehungsartefakte, Zugangsdaten und
nicht autorisierte Drittpersonendaten bleiben ausgeschlossen.

### Eigenständige Authority- und Grant-Grenze

B2 benötigt eine eigene Authority-Klasse und eigene Grants. D3 ersetzt weder
Authority noch Grant, Provider-, Capability- oder Kontrollbindung. Ein
B1-Grant darf niemals erweitert, migriert oder als B2-Grant interpretiert
werden.

### Betriebsblock

Observation und Audit bleiben gegenüber B2-Inhalten blind. Operational Memory
und Physical Persistence speichern keine B2-Inhalte. Metrics und Notifications
verarbeiten keine B2-Inhalte. Die gemeinsame Mindestgrenze ist unter
`GOV-SYSTEM-BEHAVIOR-ONLY-1` dokumentiert.

### Widerruf und AAV/UODL

Widerruf beendet die aktuelle Zugänglichkeit personenbezogener Inhalte.
Governance-Nachweise bleiben nach den bestehenden AAV-Regeln erhalten. UODL
bleibt für Eigentum, Referenzen, Speicherwahl und Operationen maßgeblich. Diese
Unterlage erfindet keine Lösch-, Speicher- oder Widerrufslogik.

## Ausdrücklich nicht autorisierte Bereiche

- B2 Runtime, Verträge, Provider, Invocation oder Capability,
- B2 Persistenz, Operational Memory, Metrics oder Notifications,
- B2 UI, Workflows oder Produktfunktion,
- ein Upgrade bestehender B1-Grants,
- personenbezogene Inhalte im Betriebsblock,
- Implementierungs-, Runtime- oder Produktfreigabe.

## Offene Risiken

- Eine historische, als `I4` bezeichnete Quellregel ist nicht belegbar. Die
  neue C2-Referenz `GOV-SYSTEM-BEHAVIOR-ONLY-1` darf nicht rückwirkend als I4
  bezeichnet werden.
- Datenklassen, Depersonalisierungsnachweis und technische Widerrufsfolgen sind
  noch nicht als B2-Verträge entschieden.
- Provider-, Credential-, Ausführungs- und Missbrauchsgrenzen für B2 sind noch
  nicht entschieden.
- Die erstmalige Bestätigung, Änderung oder Ersetzung durch den ordentlichen
  Vertrauensrat ist noch nicht erfolgt.

## Offene Folgeentscheidungen

- jeweils gesonderte Architekturentscheidungen für B2 Authority und Grants,
  Datenkorridor und Depersonalisierung, Invocation, Provider und Runtime,
- jeweils gesonderte begrenzte Implementierungsaufträge; ausschließlich
  ADR-0059 besitzt derzeit eine eigene dokumentierte Freigabe.

## Ergebnisfeld der Kenntnisnahme

- Ergebnis: `ZUR KENNTNIS GENOMMEN`
- Kenntnis genommen durch: Michael Giese
- Rolle oder Mandatsreferenz: Institutionsgründer in konstituierender Funktion
  vor erstmaliger Konstituierung des ordentlichen Vertrauensrats
- Datum: 02.08.2026
- Feststellung: Prüfung und Anerkennung der in ADR-0058 festgelegten
  verfassungsrechtlichen Grenzen
- Anmerkungen oder Auflagen: _nicht dokumentiert_
- Veto oder Eskalationsreferenz: _nicht dokumentiert_

## Teilnehmende oder verantwortliche Rollen

- Kenntnisnehmender in konstituierender Funktion: Michael Giese
- Ordentliche Vertrauensratsvertretung: _noch nicht konstituiert_
- Protokollverantwortung: _nicht eingetragen_
- Chief-Architect-Referenz: _nicht eingetragen_
- Weitere beratende Rollen: _nicht eingetragen_

## Vorbehalte, Auflagen und Sondervoten

- Vorbehalte oder Auflagen: _nicht dokumentiert_
- Minderheits- oder Sondervotum: _nicht dokumentiert; keine ordentliche
  Vertrauensratssitzung hat stattgefunden_

## Rollenbegrenzung und Bestätigungspflicht

Diese Gründer-Kenntnisnahme gilt ausschließlich bis zur erstmaligen
Konstituierung des ordentlichen Vertrauensrats. Sie muss bei dessen erster
ordentlicher Sitzung ausdrücklich bestätigt, geändert oder ersetzt werden.
Bis dahin wird weder eine ordentliche Ratsentscheidung noch ein dauerhaftes
Vertretungsmandat behauptet.

## Provenienz

- Bezug: ADR-0058 am Repository-Stand
  `de60ea7ddb49be43f4b6999d537e87339a669315`
- I4-Analyse: `GOV-ANALYSIS-I4-2026-08-02`
- Kanonische Mindestgrenze: `GOV-SYSTEM-BEHAVIOR-ONLY-1`
- Dokumentationsgrundlage: ausdrückliche institutionelle Erklärung von
  Michael Giese im Chat am 02.08.2026
- Beschluss- oder Kenntnisnahmeprovenienz: Gründer-Kenntnisnahme in
  konstituierender Funktion; ordentliche Vertrauensratsbestätigung ausstehend

Die Kenntnisnahme dokumentiert ausschließlich den institutionellen Vorgang.
Sie autorisiert keine B2-Runtime, keine personenbezogenen Provider-Aufrufe,
keine B2-Produktfreigabe, keine allgemeine B2-Implementierung, keine
B2-Persistenz, keine B2-Metriken oder Benachrichtigungen und keine Aufhebung
bestehender Schutzgrenzen.

Eine anschließende institutionelle Implementierungsfreigabe ist ein eigener,
getrennter Schritt und darf nicht aus diesem Dokument abgeleitet werden.
