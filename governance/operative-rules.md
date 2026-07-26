# ZONVAA Operative Rules Register

Version: 1.1
Status: verbindlich
Normstufe: C3

## C3-Grenze

C3 enthält veränderbare Produkt-, Technik-, Preis-, Workflow-, Betriebs- und
Arbeitsentscheidungen. C3 darf C1 oder C2 nicht verändern, abschwächen oder
umgehen. Bei Konflikt hat die nachrangige operative Regel keine Wirkung.

## Aktive Regelquellen

Operative Regeln bleiben in ihren bestehenden fachlichen Quellen:

- `AGENTS.md` für die verbindliche lokale Codex-Arbeitsweise,
- `PLANS.md` für fortgeschriebene Langlaufpläne,
- Master Decision Records für konsolidierte, ausdrücklich als alleinige
  Quelle beschlossene Architekturentscheidungen,
- ADRs für konkrete Architekturentscheidungen,
- Goal-, Decision-, Execution- und Workflow-Verträge für Produktverhalten,
- Knowledge-Protokolle, Sessions und Handovers für nachweisbaren Zustand,
- Tests für ausführbare technische Verträge.

Dieses Register ist ein Normstufen-Index. Es kopiert diese Regeln nicht und
führt keine zweite Produkt-, Workflow- oder Wissensstruktur ein.

## Arbeits- und Qualitätsregeln

Bestehende Architektur, Wissen, Git-Stand und Tests werden vor Änderungen
geprüft. Architekturentscheidungen werden dokumentiert, Änderungen
nachvollziehbar getestet und wichtige Meilensteine mit einem Handover
abgeschlossen.

Der Produktarchitekt verantwortet Ziele, Prioritäten, fachliche
Architekturfreigaben und Abnahmen. Ausführende Agenten verantworten Analyse,
Implementierung, Tests, Dokumentation und Qualität innerhalb der freigegebenen
Architektur.

Die konkrete ausführbare Regelmenge steht in `AGENTS.md`; Änderungen an ihr
sind C3-Änderungen und benötigen keinen C1-Verfassungsprozess, solange sie C1
und C2 entsprechen.

## Runtime und Preflight

RuntimeManager bleibt technische Single Source of Truth. KnowledgeManager
bleibt einzige Knowledge-Schnittstelle. Vor fachlichen Workflows lädt Runtime
die verbindlichen Identity-, Institution-, Interaction-, Constitution- und
Governance-Verträge sowie Knowledge und Project State.

Preflight weist Versionen und Integrität nach. Operative Komponenten erhalten
nur den für ihre Aufgabe notwendigen validierten Kontext und keine
stillschweigende Governance-Vollmacht.

## Änderung und Nachweis

C3-Regeln werden versioniert oder über Git-Historie, ADR, Test,
Decision Record, Session oder Handover nachvollziehbar geändert. Produkt- und
Betriebsdetails dürfen angepasst werden, ohne C1 zu versteinern.

Eine C3-Änderung mit erheblicher Wirkung in einer Schutzdomäne löst das
C2-Prüfverfahren aus. Stille faktische C1- oder C2-Änderungen sind unzulässig.
