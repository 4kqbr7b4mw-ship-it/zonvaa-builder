# ZONVAA Governance Architecture Mapping

Status: kanonische Architekturübersicht

Normstufe: C2-Orientierung ohne eigene Freigabewirkung

## Zweck

Diese Übersicht ordnet bestehende Verantwortungen vier Ebenen zu. Sie kopiert
keine fachlichen Regeln und bildet keine zweite Wahrheitsquelle. Bei
Abweichungen gelten ausschließlich die jeweils genannten bindenden Dokumente.

## C1-Verfassung

- **Zweck:** dauerhafte Negativ-Garantien und Schutzziele.
- **Zuständigkeit:** bestimmt, was ZONVAA niemals stillschweigend tun oder
  durch nachrangige Regeln umgehen darf.
- **Bindende Dokumente:** `constitution/constitution.md`, konkretisiert durch
  ADR-0027 ohne dessen operative Details in C1 zu erheben.
- **Abhängige ADRs:** sämtliche nachrangigen ADRs, insbesondere ADR-0030,
  ADR-0033 und ADR-0047 bis ADR-0060.
- **Ausgeschlossen:** Organe, Quoren, Runtime, Provider, Produktlogik,
  Implementierungsdetails und konkrete Autorisierungen.

Die Untersuchung der nicht auffindbaren Bezeichnung `I4` führte zu keiner
C1-Änderung. Die gemeinsame Systemverhaltensgrenze liegt als neue
C2-Architekturreferenz unter `governance/system-behavior-only-rule.md` und
behauptet keine historische C1-Identität.

## Institution Layer

- **Zweck:** langfristige Systemgarantien für Governance, Nutzerhoheit,
  Guardian Continuity, Transparenz, Verantwortung, Schutz, Würde und
  Vertrauen.
- **Zuständigkeit:** schützt die dauerhafte Richtung zwischen
  Conversation/Interaction und Runtime.
- **Bindende Dokumente:** `institution/institution.md`, ADR-0025 und für
  Guardian Conversation und Continuity ausschließlich MDR-0001.
- **Abhängige ADRs:** ADR-0026, ADR-0027, ADR-0030, ADR-0032, ADR-0033 und
  ADR-0047 bis ADR-0058.
- **Ausgeschlossen:** operative Policy Engine, Klassifikation, Workflowstart,
  fachliche Entscheidung, Autorisierung und Ausführung.

## Authority Layer

- **Zweck:** beschreibt Befugnisse, Verantwortungsgrenzen, Providerbindungen,
  Autorisierungsnachweise und Invocation-Grenzen.
- **Zuständigkeit:** prüft ausschließlich bereitgestellte abstrakte und
  konkrete Authority-Nachweise innerhalb ihrer jeweiligen Verträge.
- **Bindende Dokumente:** ADR-0030, ADR-0033 sowie ADR-0048, ADR-0049 und
  ADR-0050.
- **Abhängige ADRs:** ADR-0051 bis ADR-0060. ADR-0060 ist ratifiziert, aber
  nicht implementierungsfreigegeben.
- **Ausgeschlossen:** automatische Autorisierung, Providerwahl,
  Vertrauensbewertung, Capability-Aktivierung, Runtime-Ausführung und ein
  B1→B2-Upgrade.

## Runtime Layer

- **Zweck:** hält und verarbeitet ausschließlich den durch konkrete
  Runtime-Entscheidungen freigegebenen technischen Systemzustand.
- **Zuständigkeit:** derzeit genau die read-only B1 Provider Runtime und ihre
  nachgelagerten, inhaltsblinden Betriebsnachweise.
- **Bindende Dokumente:** ADR-0004, ADR-0032 sowie ADR-0051 bis ADR-0057.
- **Abhängige ADRs:** ADR-0052 bis ADR-0057; ADR-0058 begrenzt eine mögliche
  spätere B2-Architektur, autorisiert sie aber nicht.
- **Ausgeschlossen:** C1- oder C2-Änderung, Authority-Erteilung,
  Nutzerbeobachtung, B2-/B3-Runtime, automatische Eskalation und jede nicht
  ausdrücklich freigegebene Macht.

Für Observation, Audit, Operational Memory, Physical Persistence, Metrics,
Notifications und eine mögliche B2-Stufe gilt zusätzlich die kanonische
Mindestgrenze `GOV-SYSTEM-BEHAVIOR-ONLY-1`.

## Ebenengrenze

C1 schützt. Institution garantiert. Authority beschreibt und begrenzt
Befugnisse. Runtime führt ausschließlich ausdrücklich freigegebene technische
Funktionen aus. Keine nachrangige Ebene darf eine höherrangige Regel ändern,
ersetzen oder als Ausführungsvollmacht umdeuten.
