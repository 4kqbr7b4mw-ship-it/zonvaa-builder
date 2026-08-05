# Guardian Accountability & Explanation Layer

Dokument-ID: `GOV-ARCH-CANDIDATE-GUARDIAN-ACCOUNTABILITY-1`

Status:

- Registriert
- Nicht geplant
- Nicht implementiert
- Kein Implementierungsauftrag
- Keine Implementierungsfreigabe

Auslöser: Architekturdiskussion „Verifizierbarkeit statt Vertrauen“

## Gegenstand

Der offene Architekturkandidat beschreibt eine mögliche spätere lesbare
Projektion bereits vorhandener Evidenz. Er ist keine Architekturentscheidung,
keine Governance-Regel, keine ADR, kein Vertrag und keine Produkt-Roadmap-
Zusage.

## Dokumentierte Ausnahme zu E6

Die Registrierung ist eine dokumentierte Ausnahme zu ADR-0046 E6. Der
Kandidat schützt eine Verfassungsregel, die bereits heute
Architekturentscheidungen beeinflusst, obwohl die produktive Runtime noch
nicht existiert.

Die Ausnahme gilt ausschließlich für die Registrierung dieses Kandidaten. Sie
autorisiert weder Planung noch Aktivierung, Architekturentscheidung oder
Implementierung. E6 bleibt unverändert in Kraft.

## Verfassungskern des Kandidaten

### 1. Evidenzableitung

Jede Erklärung muss vollständig aus vorhandenen Evidenzartefakten ableitbar
sein. Aussagen, die nicht auf Evidenz beruhen oder den dokumentierten
Beobachtungsumfang überschreiten, sind unzulässig.

### 2. Typisierte Aussagen

Erklärungen sind typisiert. Jede Aussage trägt ihre Artefaktreferenz und ihre
Beobachtungsumfang-Deklaration. Eine Erklärung ohne Referenz kompiliert nicht.

### 3. Keine zweite Wahrheit

Die Erklärung entscheidet nichts. Die Erklärung weiß nichts. Die Erklärung liest.
Sie ist kein zweites Modell der Wahrheit. Sie ist ausschließlich eine
lesbare Darstellung bereits vorhandener Evidenz.

## Offener Governance-Konsolidierungspunkt

Arbeitstitel: `GOV-NO-FABRICATION-1`

Status: offener Konsolidierungskandidat; keine Governance-Regel

Ziel ist die mögliche spätere Zusammenführung bereits bestehender
Fabrikationsverbote zu einer kanonischen C2-Regel. Zu untersuchende
Anwendungsfälle:

- keine erfundenen Quellen,
- keine erfundenen Gefühle,
- keine erfundenen Nachweise,
- keine erfundene Rechenschaft.

Arbeitshypothese:

> Das System erzeugt keine Aussage, die nicht auf einem benennbaren Artefakt
> beruht.

Diese Registrierung ratifiziert, konsolidiert oder aktiviert keine neue
Governance-Regel. `GOV-NO-FABRICATION-1` ist weder bindend noch freigegeben.

### Historische Bezeichnungs- und Referenztrennung

`GOV-NO-FABRICATION-1` bleibt unverändert der historische Arbeitstitel dieses
offenen Konsolidierungskandidaten. Er ist keine Dokument-ID und bezeichnet
nicht das später abgeschlossene Referenzartefakt.

Das davon getrennte, rein dokumentarische Referenzartefakt besitzt
ausschließlich die Dokument-ID
`GOV-NO-FABRICATION-REFERENCE-CONSOLIDATION-V1` und liegt unter
`governance/no-fabrication-reference-consolidation.md`. Seine Fertigstellung
aktiviert den historischen Kandidaten nicht. Diese Klarstellung erhält die
frühere Kandidatenbezeichnung und führt weder eine Umbenennung noch eine neue
Regel, Taxonomie, Priorität oder materielle Wirkung ein.

## Aktivierungsbedingungen

Der Architekturkandidat darf erst aktiviert werden, wenn alle folgenden
Voraussetzungen erfüllt sind:

- produktive B2-Runtime,
- erste reale Rechenschaftspflichten,
- dokumentierter Aktivierungsbeschluss.

Vorher bleibt der Kandidat ausdrücklich ruhend.

## Macht- und Freigabegrenze

Dieser Kandidat erzeugt keinerlei Freigabe für spätere Implementierungen.
Keine Runtime, API oder Erklärungsschicht darf daraus abgeleitet oder
implementiert werden. Er erzeugt keine Verträge, Provider, Werkzeuge,
Workflows, Persistenz, Observation, Audit-Auswertung oder Produktfunktion.
