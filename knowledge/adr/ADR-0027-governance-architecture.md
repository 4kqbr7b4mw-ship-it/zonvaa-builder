# ADR-0027 – Governance Architecture

## Status

Beschlossen

## Kontext

Die Constitution 1.4 enthielt dauerhafte Schutzprinzipien gemeinsam mit
veränderbaren Rollen-, Arbeits-, Runtime-, Kommunikations- und
Produktregeln. Der Institution Layer 1.1 definierte Governance als
langfristige Garantie, aber noch keine Organe, Prüfmechanismen oder
Eskalationen.

Diese Vermischung erschwert sowohl dauerhaften Schutz als auch legitime
operative Veränderung. C1 darf nicht durch Detailregeln versteinern.
Gleichzeitig dürfen C2- oder C3-Entscheidungen Guardian-, Interaction- oder
Institution-Garantien nicht stillschweigend abschwächen.

## Entscheidung

ZONVAA führt eine dreistufige Normhierarchie ein:

1. **C1 – Constitution** enthält ausschließlich dauerhafte
   Negativ-Garantien und Schutzziele.
2. **C2 – Governance Charter** definiert Organe, Prüfmechanismen,
   Vetorechte, Audits, Eskalationen und Verantwortlichkeiten.
3. **C3 – Operative Regeln** enthält veränderbare Produkt-, Technik-, Preis-,
   Workflow-, Betriebs- und Arbeitsentscheidungen.

Die Hierarchie ist strikt: C3 muss C2 und C1 entsprechen; C2 muss C1
entsprechen. Nachrangige Regeln dürfen einen Konflikt nicht durch operative
Praxis faktisch entscheiden.

## C1

Die Constitution wird auf Version 2.0 angehoben und auf folgende
Negativ-Garantien konzentriert:

- kein Verkauf von Nutzerdaten,
- kein verdecktes Training Dritter mit Nutzerdaten,
- keine verdeckte Monetarisierung oder Kickbacks,
- keine Optimierung auf emotionale Abhängigkeit oder Verweildauer,
- keine Umgehung von Nutzerhoheit und Autorisierung,
- keine Aufgabe von Portabilität und Sunset-Fähigkeit,
- keine stille Aufweichung von Guardian-, Interaction- oder
  Institution-Garantien.

C1 legt keine Organe, Quoren, Fristen, Gesellschaftsformen, Rechtsfolgen oder
technischen Verfahren fest.

Die bisher in der Constitution enthaltenen operativen Arbeits-, Rollen-,
Runtime- und Qualitätsregeln werden nicht gelöscht. Sie bleiben über
`AGENTS.md`, ADRs, ausführbare Verträge und das neue C3-Register
`governance/operative-rules.md` aktiv und veränderbar.

## C2 Governance Charter

Die kanonische Charter liegt unter `governance/charter.md` und definiert vier
funktionale Organe:

- operative Leitung,
- unabhängiger Vertrauensrat,
- Nutzer-Konvent,
- Eigentums- oder Trägerstruktur mit Schutzfunktion.

Anzahl, Beruf, Quote, Amtszeit, Vergütung und konkrete Besetzung werden nicht
als unveränderliche Architektur festgelegt.

### Vertrauensrat und Veto

Der Vertrauensrat besitzt ein begrenztes aufschiebendes Prüf- und Vetorecht
für:

- Daten,
- Monetarisierung und Interessenkonflikte,
- Notfall- und Sicherheitslogik,
- Guardian Continuity,
- Änderungen an C1 oder C2.

Das Verfahren besteht aus Prüfung, begründetem Veto, Vermittlung, erneuter
Prüfung und dokumentierter Eskalation an eine unabhängige Träger- oder
Verfassungsinstanz. Überstimmungen bleiben begründet, dokumentiert und
auditierbar. Es gibt kein absolutes, unbegrenzt unüberstimmbares Veto.

### Nutzerbeteiligung

Der Nutzer-Konvent muss repräsentative, gegen einfache Manipulation
geschützte Beteiligung ermöglichen. Losverfahren, rotierende Nutzerpanels,
verifizierte Langzeitnutzer oder ausgewogene Stichproben sind mögliche
C2-Methoden. Direkte offene Onlinewahlen sind kein verbindliches
Standardmodell.

### Transparenz, Audit und Vorfälle

Governance-Entscheidungen werden grundsätzlich öffentlich dokumentiert.
Ausnahmen bleiben auf Datenschutz, Sicherheit und laufende Verfahren
begrenzt.

Unabhängige externe Audits, rotierende Prüfinstanzen, ein Register
erheblicher C1-Verletzungen und ein geschützter Whistleblower-Kanal sind
verbindliche C2-Ziele. Bagatellfälle gehören nicht in das
Vertrauensverletzungsregister. Einträge werden durch Nachträge korrigiert,
nicht still gelöscht.

Konkrete Anbieter, Intervalle, Plattformen, Anonymitäts- oder
Sicherheitswirkungen benötigen eigene Entscheidungen.

## Verfassungsänderungen

C1-Änderungen benötigen als Mehrschlüssel-Verfahren mindestens die Zustimmung
von operativer Leitung, Vertrauensrat und Nutzer-Konvent als unabhängigen
Machtzentren. Kein Zentrum ändert C1 allein.

Konkrete Mehrheiten, Quoren, Fristen und Kühlphasen sind begründete
C2-Ausführungsregeln und keine ewigen C1-Zahlen.

## Eigentums- und Trägerschutz

Verantwortungseigentum, Stiftung, Sperrrechte und vergleichbare Modelle sind
zu prüfende Zielstrukturen. ADR-0027 legt keine Rechtsform fest und behauptet
keine Haftungs- oder Insolvenzfestigkeit.

Die spätere Struktur muss Datenhoheit, Guardian- und Institution-Garantien,
Sunset-Fähigkeit und Vertrauensschutz gegen stille Aufhebung durch Verkauf,
Kontrollwechsel oder Investorendruck absichern.

## C3 Operative Regeln

`governance/operative-rules.md` ist der versionierte Normstufen-Index.
Operative Regeln bleiben in ihren bestehenden Quellen wie `AGENTS.md`,
`PLANS.md`, ADRs, Workflow-Verträgen, Tests und Handovers. Das Register
dupliziert sie nicht.

C3-Änderungen benötigen keinen C1-Prozess, solange sie C1 und C2 entsprechen.
Erhebliche Auswirkungen in einer Schutzdomäne lösen die C2-Prüfung aus.

## Verhältnis zur bestehenden Architektur

- WHY und Identity bleiben höchste fachliche Richtung.
- Guardian Foundation, ADR-0023 und ADR-0024 bleiben unverändert gültig.
- Interaction 1.0 bleibt Grenze zwischen Gespräch und autorisierter Handlung.
- Institution wird auf 1.2 aktualisiert; C2 operationalisiert ausschließlich
  deren Governance-Garantie und bildet keine parallele Institution.
- RuntimeManager bleibt technische Single Source of Truth.
- KnowledgeManager bleibt einzige Knowledge-Schnittstelle.
- Goal-, Decision-, Execution- und Life-Decisions-Workflows erhalten keine
  Governance-Vollmacht.

ADR-0027 ersetzt die bisherige Annahme, dass die Constitution zugleich
operativer Arbeits- und Systemregelvertrag ist. Historische ADRs bleiben als
Entscheidungsnachweis erhalten; ab ADR-0027 gilt die C1-C3-Trennung.

## Runtime und Preflight

Ein unveränderlicher `GovernanceContext` weist C1-Hash, C2- und C3-Versionen
und -Hashes sowie stabile Schutzziele, Organe und Vetodomänen nach.
GovernanceLoader prüft Normstufen und strukturelle Vollständigkeit, führt aber
keine Governance-Aktion aus.

Runtime lädt Constitution und anschließend Governance vor Knowledge, Project
State und operativen Engines. Mission Context Schema 1.3 enthält den
Governance-Nachweis. Fehlender oder veränderter Governance-Kontext bricht den
Preflight ab. WorkflowContext erhält keine Governance-Inhalte.

## Bewusst nicht festgelegt

- feste Organ- oder Personenzahlen,
- Berufsquoten, Amtszeiten oder feste Budgets,
- Mehrheiten, Quoren, Fristen oder Kühlphasen,
- bestimmte Verbände oder Akademien als Ernennungsstellen,
- pauschale Open-Source-Pflicht bei Insolvenz,
- absolute Ewigkeitsklauseln,
- konkrete Rechtsform oder ungeprüfte gesellschaftsrechtliche Konstruktion,
- pauschale Haftungs- oder Insolvenzbehauptungen,
- technische Audit-, Incident- oder Whistleblower-Systeme.

## Konsequenzen

- Dauerhafte Schutzgrenzen sind von veränderbaren Verfahren und
  Betriebsregeln getrennt.
- Governance wird strukturell nachgewiesen, aber nicht als funktionsfähiges
  Organ oder Rechtskonstrukt vorgetäuscht.
- Bestehende Garantien bleiben vorrangig und dürfen nicht still operativ
  überschrieben werden.
