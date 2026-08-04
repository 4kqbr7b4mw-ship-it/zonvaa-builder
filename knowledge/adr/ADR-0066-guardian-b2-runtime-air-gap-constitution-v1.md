# ADR-0066 – Guardian B2 Runtime Air Gap Constitution v1

Status: **RATIFIZIERT – AUSSCHLIESSLICH DOKUMENTARISCH IMPLEMENTIERUNGSFREIGEGEBEN – DEKLARATORISCH VOLLENDET UND VALIDIERT – OHNE PRODUKTIVE TECHNISCHE KOMPONENTE**

Ratifizierungsnachweis: `GOV-RATIFICATION-ADR-0066-V1`

Implementierungsfreigabe:
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0066-V1`

Die Ratifizierung bestätigt ausschließlich diese deklaratorische Architektur.
Die getrennte institutionelle Implementierungsfreigabe erlaubte ausschließlich
die nun dokumentarisch umgesetzte, deklaratorische Vollendung durch kanonische
Dokumentationspflege, Handover und dokumentarische Regressionstests. Der
Runtime Air Gap ist keine Software. Seine Vollendung ist allein der kanonische
Nachweis, dass keine technische Verbindung vorgesehen oder vorhanden ist. Sie
eröffnet keine Runtime-Diskussion. ADR-0066 sieht dauerhaft keine produktive
technische Komponente vor; Modul, Validator, statische Air-Gap-Analyse und
Runtime Readiness bleiben ausgeschlossen. Diese Vollendung ist noch nicht
committed und noch nicht gepusht.

## 1. Kontext

ADR-0059 bis ADR-0065 bilden die abgeschlossene nicht ausführende B2-
Verfassungskette. ADR-0065 endet jeden positiven und negativen Prüfpfad mit
`NO_EXECUTION_OCCURRED` und `CONTROLLED_STOP`. Eine B2 Runtime existiert nicht.

## 2. Problemstellung

Der kontrollierte Stopp darf weder sprachlich noch durch Planungsartefakte als
Übergabestelle zu einer Runtime umgedeutet werden. Eine positive Invocation
Decision erzeugt keinen Anspruch, keine Vermutung und keine Bereitschaft zur
Ausführung. Deshalb wird nicht ein Übergang geregelt, sondern seine vollständige
Abwesenheit verfassungsrechtlich festgestellt.

## 3. Kanonische Grundlagen

- ADR-0059 bis ADR-0064-A1 bleiben die unveränderte B2-Grundlage.
- ADR-0065 bleibt allein kanonisch für Capability Invocation, Receipt,
  Resolution Snapshot und kontrollierten Stopp.
- `GOV-INSTITUTIONAL-DECISION-SCOPE-1` trennt jeden menschlichen Beschluss und
  jede Freigabe.
- `GOV-SYSTEM-BEHAVIOR-ONLY-1` öffnet keine B2 Runtime.
- Guardian Key Custody / Key Master und Guardian Accountability & Explanation
  bleiben ausschließlich registrierte, ruhende Architekturkandidaten.

## 4. Verhältnis zu ADR-0065

ADR-0065 definiert die nicht ausführende Invocation-Vertragsfamilie. ADR-0066
definiert keine zweite Invocation-Regel und wiederholt deren Verträge nicht.
ADR-0066 ist ausschließlich kanonisch für die Eigenständigkeit einer
hypothetischen Runtime-Verfassung, das Verbot jedes Invocation→Runtime-
Übergangs und die Bedingungen für die Eröffnung einer möglichen späteren
Architekturdiskussion.

## 5. Eigenständiger Zweck

Der zusätzliche verfassungsrechtliche Zweck besteht darin, die in ADR-0065
enthaltene Vertragsgrenze über den Invocation-Scope hinaus institutionell zu
schließen: Nach dem Resolution Snapshot existiert kein nächster technischer
Zustand. Runtime ist weder Folgepaket noch Phase von Invocation. Dieser ADR ist
keine technische Schicht und keine zweite Wahrheit über Invocation.

## 6. Begriffsverfassung

- **Runtime Air Gap:** verfassungsrechtlich festgestellte Abwesenheit jedes
  technischen, strukturellen oder impliziten Übergangs zwischen Invocation und
  Runtime.
- **Controlled Stop:** zwingender nicht ausführender Endpunkt der ADR-0065-
  Vertragsfamilie.
- **Runtime:** hypothetische, derzeit nicht existierende, nicht ratifizierte,
  nicht freigegebene und nicht implementierte eigenständige Verfassungsstufe.
- **Transition:** jeder technische, strukturelle oder implizite Übergang von
  Invocation zu Runtime; innerhalb ADR-0066 ausnahmslos verboten.
- **Runtime Preparation:** jede Architektur oder Implementierung, die Runtime
  technisch, strukturell oder semantisch vorbereitet; ausnahmslos verboten.
- **Runtime Discussion Preconditions:** geschlossene institutionelle
  Bedingungen, die nur eine menschliche Prüfung ermöglichen, ob eine spätere
  Architekturdiskussion eröffnet werden darf. Sie aktivieren, autorisieren oder
  implementieren nichts.

## 7. Verfassungsrechtliche Kernregel

> B2 Capability Invocation endet vollständig mit dem kontrollierten Stopp.

> Kein Objekt, Vertrag, Validator, Evidence-Artefakt, Receipt oder Resolution
> Snapshot aus ADR-0065 besitzt eine technische, strukturelle oder implizite
> Fortsetzungswirkung.

> Invocation endet vollständig. Runtime kann nicht aus Invocation abgeleitet,
> fortgesetzt oder technisch erreicht werden.

Runtime ist keine Unterstufe, Fortsetzung, Ausführungsphase oder Betriebsart
von Invocation. Sie könnte ausschließlich durch eine neue menschliche
Architekturentscheidung entstehen. Request und positive Decision erzeugen
weder Anspruch noch Vermutung auf spätere Ausführung.

Die kanonische Endfolge lautet vollständig:

`B2 Invocation Resolution Snapshot → CONTROLLED_STOP → ENDE`

Danach existiert keine technische Empfangsstelle, Transition, Continuation,
kein Handoff und kein nächster technischer Zustand.

## 8. Keine technische Komponente

ADR-0066 besitzt ausschließlich Dokumentations-, Governance- und Testwirkung.
Er sieht kein Python-Modul, keine Air-Gap-Klasse, keinen Validator, Evaluator,
Service, Adapter, Bridge, Gateway, Interface, Protocol, Abstract Base Class,
API, Endpoint, Client, Server, Queue, Event, Message, Command, Job, Scheduler,
Callback, Hook, Plugin, Tool, Agent, MCP- oder Provider-Verbindung, Datenbank,
Speichervertrag, Runtime-Konfiguration, Sandbox, Simulation, Mock Runtime,
Test Runtime, Dummy Runtime, Dry-Run Runtime oder Execution Stub vor.

## 9. Keine Bridge

Zwischen ADR-0065 und Runtime existieren kein Output- oder Input-Port, kein
Übergabe- oder Transportvertrag, Runtime Envelope, Runtime Request, Runtime
Command, Execution Request, Execution Grant, Execution Token, Dispatch Record,
Queue Record, Runtime Receipt, Runtime Handle, Continuation Reference,
Next-Step Reference, Adapter Reference, Provider Endpoint Reference, Tool
Reference, Agent Reference, API Reference oder MCP Reference.

Der Resolution Snapshot endet und besitzt keinen nachgelagerten Empfänger.

## 10. Keine implizite Fortsetzung

Verboten sind `ready`, `ready_for_runtime`, `execution_ready`, `dispatchable`,
`runnable`, `approved_for_execution`, `eligible_for_runtime`,
`pending_execution`, `awaiting_runtime`, `next_stage`, `continuation`,
`handoff`, `runtime_candidate`, `execution_candidate` und funktional
gleichwertige Aussagen. Eine positive Invocation Decision bedeutet nur:

- konsistent für nicht ausführende Auflösung;
- keine Ausführung erfolgt;
- kontrollierter Stopp.

Sie bedeutet niemals technisch ausführbar, später auszuführen, auf Runtime
wartend oder für Runtime vorgemerkt.

## 11. Trennung von Authorization, Invocation und Runtime

Authorization, Invocation und Runtime sind drei getrennte Verfassungsstufen.
Authorization ist nicht Invocation. Invocation ist nicht Runtime. Runtime ist
keine Fortsetzung von Invocation. Keine Stufe impliziert oder autorisiert die
nächste. Evidence, Receipt, Statusdokument, technischer Bedarf oder
Produktstrategie einer Stufe öffnet keine andere Stufe.

## 12. Runtime-Diskussionsvoraussetzungen

Die kleinste ausreichende geschlossene Menge lautet:

1. ADR-0059 bis ADR-0066 sind jeweils in ihrem eigenen zulässigen Scope
   abgeschlossen; für ADR-0066 schließt dies gesonderte Ratifizierung und
   institutionelle Behandlung ein.
2. Es bestehen keine offenen Architekturblocker in der aktuellen B2-
   Verfassung, und diese wurde vollständig neu reviewed.
3. Eine eigenständige Runtime-Risikobewertung sowie getrennte Prüfungen der
   Datenschutz-/Personenbezogenheits-, Key-Custody- und Inhaltszugriffsgrenzen
   sind dokumentiert.
4. Observation, Runtime Audit, Incident/Accountability und externe Provider-
   und Integrationsgrenzen wurden jeweils als getrennte offene Gates geklärt,
   ohne sie zu implementieren oder zusammenzulegen.
5. Ein ausdrücklicher gegenwärtiger menschlicher institutioneller Beschluss
   erlaubt ausschließlich, eine Runtime-Architekturdiskussion zu eröffnen.
6. Jede daraus möglicherweise entstehende Runtime-Architektur benötigt einen
   eigenen neuen ADR, eigene menschliche Ratifizierung und eigene
   institutionelle Implementierungsfreigabe.

Diese Bedingungen sind Aktivierungsbedingungen für eine Diskussion, keine
Runtime-Readiness, keine Runtime-Planung und keine technische Vorbereitung.

## 13. Keine automatische Aktivierung

Keine Bedingung löst automatisch Diskussion, ADR, Planung, Ratifizierung,
Freigabe, Providerauswahl, Toolauswahl oder Implementierung aus. Selbst wenn
alle Bedingungen dokumentiert erfüllt wären, bliebe ein ausdrücklicher
menschlicher institutioneller Beschluss erforderlich.

## 14. Keine vorweggenommene Runtime-Semantik

ADR-0066 definiert nicht, wie Runtime funktioniert, welche Komponenten,
Provider oder Tools existieren, wie Queues, Fehler, Retries, Sessions, Tokens,
Secrets, Schlüssel, APIs, Agents oder MCP funktionieren oder wie Inhalte,
Observation, Audit, Operational Memory, Metrics oder Notifications behandelt
werden. Alle diese Fragen liegen vollständig außerhalb des Scopes.

## 15. Personenbezogene Grenze

Der Air Gap ist vollständig datenblind. Er enthält keinen Nutzer-, Akteurs-
oder Provider-Personenbezug, keine Identitätsbindung, Inhalte, Prompts,
Dokumente, medizinischen oder rechtlichen Inhalte, Adressen, Kontakte, Geräte,
Sessions, Nutzerkonten oder Rollen natürlicher Personen. Er verarbeitet und
speichert keine personenbezogenen Daten.

## 16. Key-Custody- und Inhaltszugriffsgrenze

ADR-0066 öffnet keinen Key-Custody-, Entschlüsselungs- oder Inhaltszugriffspfad,
erzeugt keinen Key Master, keine Schlüsselanteile oder Endgerätefreigabe und
bindet keine kryptografische Komponente. Guardian Key Custody / Key Master
bleibt ausschließlich registrierter Architekturkandidat: keine Aktivierung,
Planung oder Implementierung.

## 17. Governance- und Evidenzgrenze

Governance Decision Records dokumentieren nur tatsächlich gefasste
Entscheidungen. Ein Diskussionsbeschluss ist keine Runtime-Freigabe, ein
Architekturauftrag keine Ratifizierung, eine Ratifizierung keine
Implementierungsfreigabe und eine Implementierungsfreigabe keine technische
Ausführung. Keine Stufe wird zusammengelegt. Governance Incident Evidence
dokumentiert nur Abweichungen und erzeugt weder Runtime-Sperre noch
Runtime-Freigabe.

## 18. Accountability- und Explanation-Abgrenzung

Der registrierte Guardian Accountability & Explanation Layer wird weder
aktiviert noch implementiert. Er darf nur als mögliche spätere
Diskussionsvoraussetzung referenziert werden, soweit sein bestehender
Kandidatenstatus reicht. ADR-0066 erfindet keine Accountability-Semantik,
keine Erklärungsklasse und keine automatische Rechenschaft.

## 19. Architekturvarianten

### Variante A – kein ADR-0066

ADR-0065 schützt seine eigene Vertragsfamilie, schließt aber institutionelle
Planung außerhalb dieses Scopes nicht als eigene Regel. Der zusätzliche Zweck
bliebe nur implizit. Verworfen.

### Variante B – deklaratorischer ADR ohne technische Komponenten

Trennt Invocation und jede hypothetische Runtime verfassungsrechtlich, entfernt
Übergangsvorwegnahmen und formuliert nur Diskussionsvoraussetzungen. Gewählt.

### Variante C – technischer Runtime Boundary Validator

Wäre selbst eine technische Übergangskomponente und Runtime-Vorbereitung.
Verworfen.

### Variante D – Runtime Readiness Contract

Würde Status, maschinelle Aktivierung und vorweggenommene Runtime-Semantik
erzeugen. Verworfen.

## 20. Gewählte Variante

Variante B besitzt den kleinsten eigenständigen Zweck, die stärkste
Nichtausführungsgrenze und die geringste versteckte Runtime-Gefahr. Sie
ergänzt ADR-0065, ohne dessen Invocation-Wahrheit zu duplizieren.

## 21. Verworfene Varianten

Variante A lässt die institutionelle Planungsgrenze ungesichert. Varianten C
und D verletzen Prüffrage Null, weil sie technische Erreichbarkeit oder
automatische Readiness modellieren würden.

## 22. Strukturelle Invarianten

- Die Kette endet nach dem Resolution Snapshot mit `CONTROLLED_STOP` und ENDE.
- Kein ADR-0065-Artefakt besitzt Fortsetzungswirkung.
- Runtime ist eigenständig, hypothetisch, nicht existent und gesperrt.
- ADR-0066 besitzt keine produktive technische Komponente.
- Diskussionsvoraussetzungen sind keine Readiness oder Freigabe.
- Jede spätere institutionelle Stufe benötigt einen eigenen menschlichen Akt.
- Der Air Gap bleibt datenblind und nicht personenbezogen.
- Keine Evidence oder Provenienz ersetzt ein nachgelagertes Gate.

## 23. Negative Runtime-Air-Gap-Rules

Unzulässig sind jede Transition oder Runtime Preparation, Bridge, Adapter,
Gateway, Interface, Validator, Pipeline, Queue, Event, Runtime Request,
Execution Contract, Fortsetzungsreferenz, automatische Readiness, Aktivierung,
Eskalation, ADR-Erzeugung, Planung, Provider- oder Toolauswahl, Key Custody,
Inhaltszugriff, Observation, Audit, Operational Memory, Metrics,
Notifications, natürliche Person, personenbezogene Verarbeitung und jede
technische Macht.

## 24. Prüffrage Null

Kann ADR-0066 Invocation technisch fortsetzen, einen Runtime-Übergang oder
Runtime Preparation modellieren, Runtime als nächsten Zustand darstellen,
positive Invocation als Runtime-Reife umdeuten, Adapter, Gateway, Interface
oder Validator bereitstellen, automatische Readiness oder Aktivierung
erzeugen, Tool, Agent, MCP, Provider oder API aufrufen, Session, Token, Cache,
Key oder Runtime Handle erzeugen, Key Custody oder Inhaltszugriff öffnen,
natürliche Personen oder personenbezogene Inhalte binden, Observation oder
Profilbildung erzeugen oder technische Macht schaffen?

Antwort: **Nein.** Der ADR ist ausschließlich deklaratorisch, enthält keine
technische Komponente und beendet jede Kette nach dem kontrollierten Stopp.

## 25. Auswirkungen auf ADR-0059 bis ADR-0065

ADR-0059 bis ADR-0065 bleiben semantisch unverändert. ADR-0065 bleibt allein
kanonisch für Invocation. Die zuvor in der Future B2 Package Map enthaltene
planende Zeile „B2 Provider Runtime“ wird nicht fortgeführt, weil sie eine
Invocation-Abhängigkeit und einen Ausführungszweck vorwegnahm. Dies ändert
keine ratifizierte Architektur; es entfernt eine nicht kanonische
Planungsvorwegnahme.

## 26. Ausdrücklich nicht freigegebene Bereiche

Nicht freigegeben sind Ratifizierung, institutionelle Implementierungsfreigabe,
Implementierung, produktive Python-Dateien, technische Air-Gap-Komponenten,
Runtime Boundary Validator, Readiness Contract, Adapter, Bridge, API, Request,
Command, Token, technische Ausführung, Provider-, Tool-, API-, MCP- oder
Agent-Aufruf, externe Integration, Sessions, Caches, Tokens, Schlüsselmaterial,
Key Custody, Inhaltszugriff, Observation, Runtime Audit, Operational Memory,
Metrics, Notifications, natürliche Personen, personenbezogene Verarbeitung
oder Speicherung, ein neuer Runtime-ADR, ADR-0067 und Änderungen an ADR-0059
bis ADR-0065.

## 27. Ratifikationsanforderungen

Eine Ratifizierung müsste den eigenständigen Zweck, die vollständige
Übergangsabwesenheit, Diskussionsvoraussetzungen, alle Invarianten,
Negativregeln und Prüffrage Null ausdrücklich menschlich bestätigen. Sie wäre
keine Implementierungsfreigabe und keine Runtime-Diskussionsfreigabe.

## 28. Implementierungsfreigabeanforderungen

ADR-0066 sieht keine produktive Implementierung vor. Eine spätere
institutionelle Behandlung dürfte höchstens kanonische Dokumentations- und
Testpflege freigeben und müsste technische Komponenten, Runtime Preparation
und Runtime weiterhin ausdrücklich ausschließen. Fehlende Nennung wäre
Nichtfreigabe.

## 29. Testanforderungen

Tests müssen ausschließlich Dokumentation, Governance, Handover, Status,
fehlende technische Module, fehlende Übergangsartefakte, fehlende Readiness-
Automatik, ADR-0065-Kanonizität, Datenblindheit, Key-Custody-Grenze,
Accountability-Nichtaktivierung und Prüffrage Null nachweisen.

## 30. Offene institutionelle Entscheidungen

Der separate deklaratorische Vollendungsauftrag ist dokumentarisch umgesetzt.
Weiterhin nicht eröffnet ist eine Runtime-Architekturdiskussion. Auch die
vollständige Erfüllung aller menschlichen Diskussionsgates löst nichts aus;
hierfür wäre ein neuer ausdrücklicher institutioneller Beschluss erforderlich.
Es gibt keinen Runtime-ADR und keinen ADR-0067.

## 31. Konsequenzen

Der kontrollierte Stopp ist nicht nur Endpunkt einer Vertragsfamilie, sondern
institutionelle Endgrenze. Planung kann ihn nicht als stillschweigende
Übergabestelle behandeln.

## 32. Risiken

Die deklaratorische Regel könnte irrtümlich als technische Air-Gap-Komponente
verstanden werden. Deshalb verbietet der ADR ausdrücklich jedes Modul und
jeden Validator. Diskussionsvoraussetzungen könnten als Readiness-Score
missverstanden werden; deshalb besitzen sie keine automatische Wirkung und
erfordern stets einen neuen menschlichen Beschluss.
