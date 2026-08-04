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
  ADR-0033 und ADR-0047 bis ADR-0062.
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
- **Abhängige ADRs:** ADR-0051 bis ADR-0062. ADR-0060 ist ratifiziert und im
  begrenzten nicht ausführenden Scope implementiert. ADR-0061 ist ratifiziert
  und ausschließlich für den begrenzten nicht ausführenden Provider-Identity-
  Scope implementiert. ADR-0062 ist ratifiziert und ausschließlich im
  geschlossenen nicht ausführenden Provider-Authorization-Scope
  implementierungsfreigegeben und im nicht ausführenden Scope implementiert.
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

Institutionelle Beschlüsse werden zusätzlich durch
`GOV-INSTITUTIONAL-DECISION-SCOPE-1` begrenzt und müssen `Freigegeben` sowie
`Ausdrücklich nicht freigegeben` getrennt dokumentieren.

Das Maintenance-Dokument
`GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1` prüft die bestehende Kette von
Data Corridor bis Provider Authorization. Es ist nur Review-Nachweis, keine
kanonische Fachregel, ADR, Ratifizierung oder Implementierungsfreigabe.

### ADR-0063 – B2 Purpose and UODL Binding Constitution

ADR-0063 ist durch `GOV-RATIFICATION-ADR-0063-V1` ausschließlich als Purpose-
und UODL-Bindungsverfassung ratifiziert. Die getrennte Freigabe
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0063-V1` erlaubt ausschließlich den
ratifizierten nicht ausführenden Scope. Dieser ist durch immutable Purpose-
Bindung, UODL-Mapping, getrennte Evidence und zustandslose Validatoren in
`governance/b2_purpose_uodl_binding.py` implementiert und validiert. Migration,
Capability Invocation und Runtime bleiben ausgeschlossen.

### ADR-0064 – Governance Decision and Incident Evidence Constitution

ADR-0064 ist durch `GOV-RATIFICATION-ADR-0064-V1` ausschließlich als
Governance-Decision- und Incident-Evidence-Verfassung ratifiziert. Sie bewahrt
den ADR-0059-Nachweisstatus. Die getrennte Freigabe
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-V1` erlaubt ausschließlich die
ratifizierte nicht ausführende Implementierung. ADR-0064-A1 ergänzt die
geschlossenen Taxonomien und ist getrennt ratifiziert sowie
implementierungsfreigegeben. Beide Architekturen sind mit immutable Decision-
und Incident-Verträgen, zustandslosen Validatoren, Public API und den leeren
kanonischen Dokumentationsorten implementiert und validiert. Der Recovery-
Stash wurde kontrolliert angewendet und vollständig neu geprüft, bleibt aber
unverändert erhalten. ADR-0065, Capability Invocation und Runtime bleiben
bis zu einem eigenen Architekturakt gesperrt.

### ADR-0065 – Guardian B2 Capability Invocation Constitution

ADR-0065 ist durch `GOV-RATIFICATION-ADR-0065-V1` ausschließlich als
nicht ausführende Capability-Invocation-Architektur ratifiziert und durch
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1` begrenzt
implementierungsfreigegeben. Die eigenständige immutable Vertragsfamilie,
zustandslose Evaluation, Evidence, Receipt, Resolution Snapshot und Foundation
sind implementiert und validiert. Sie
referenziert die unveränderten ADR-0059-bis-ADR-0063-Verträge in einer
eigenständigen B2-Request–Decision–Evidence–Receipt–Snapshot-Familie. Jeder
Prüfpfad endet mit `CONTROLLED_STOP` und `NO_EXECUTION_OCCURRED`. Die
Architektur enthält keine neue Autorisierung, keine B1→B2-Konvertierung, keine
Providerwahl und keinerlei Runtime-, Tool-, Agent-, MCP-, API- oder
Ausführungswirkung. B2 Runtime bleibt ein getrenntes gesperrtes Gate.

## Ebenengrenze

### ADR-0066 – Guardian B2 Runtime Air Gap Constitution

ADR-0066 ist ausschließlich als deklaratorische Architektur ratifiziert,
ausschließlich dokumentarisch implementierungsfreigegeben und nicht
implementiert. Ratifizierung und Freigabe sind durch
`GOV-RATIFICATION-ADR-0066-V1` und
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0066-V1` getrennt dokumentiert.
ADR-0065 bleibt kanonisch für Invocation. ADR-0066 ergänzt nur die
Eigenständigkeit jeder hypothetischen Runtime-Verfassung, das Verbot jedes
Invocation→Runtime-Übergangs und die menschlichen Voraussetzungen vor einer
möglichen späteren Architekturdiskussion. Es gibt kein Modul, keinen Validator,
Adapter, Bridge, Gateway, Runtime Request oder Readiness Contract. Runtime ist
kein nächster Zustand und bleibt nicht existent und gesperrt.
ADR-0066 sieht dauerhaft keine produktive technische Komponente vor. Die
Freigabe erlaubt nur eine spätere deklaratorische Vollendung durch
Dokumentationspflege und dokumentarische Regressionstests.

C1 schützt. Institution garantiert. Authority beschreibt und begrenzt
Befugnisse. Runtime führt ausschließlich ausdrücklich freigegebene technische
Funktionen aus. Keine nachrangige Ebene darf eine höherrangige Regel ändern,
ersetzen oder als Ausführungsvollmacht umdeuten.
