# ADR-0050: Guardian Capability Invocation Boundary v1

## Status

Angenommen

## Kontext

Die bestehenden Authority-Schichten definieren, welche abstrakten Befugnisse
existieren, welche Provider-Identitäten bereitgestellt wurden und welche
Autorisierungen, Entscheidungen und Lifecycle-Nachweise vorliegen.

Der bestehende Nachweispfad lautet:

```text
Guardian Authority Model
→ Provider Identity
→ Authorization Grant
→ Decision Evidence
→ Lifecycle Evidence
→ Resolution Snapshot
```

Diese Schichten definieren, wer welche Befugnis besitzt. Sie definieren noch
nicht, wie ein möglicher Capability-Aufruf formal angefordert, validiert,
abgelehnt oder als grundsätzlich zulässig nachgewiesen wird.

ADR-0050 schließt diese Lücke, ohne bereits eine Capability auszuführen.

## Entscheidung

ZONVAA führt eine immutable und deterministisch validierbare Guardian
Capability Invocation Boundary ein.

Die Boundary:

- beschreibt einen bereits bereitgestellten Invocation Request,
- prüft dessen Authority-, Provider-, Authorization-, Capability-, Schutz- und
  Kontextbindungen,
- dokumentiert eine bereits bereitgestellte Invocation Decision,
- erzeugt einen immutable Invocation Receipt,
- stellt einen read-only Resolution Snapshot bereit,
- führt keine externe Operation aus,
- aktiviert keine Capability,
- startet keine Runtime.

## Erweiterter Authority Stack

```text
Guardian Authority Model
→ Provider Identity
→ Authorization Grant
→ Decision Evidence
→ Lifecycle Evidence
→ Resolution Snapshot
→ Capability Invocation Boundary
```

Jeder vorgelagerte Nachweis muss für eine zulässige Invocation konsistent und
gültig bereitgestellt sein. Fehlende oder widersprüchliche Nachweise führen zu
einer kontrollierten Ablehnung oder Blockierung. Es erfolgt keine automatische
Reparatur, Hochstufung, Provider-Auswahl oder Ersatzautorisierung.

## Invocation Request

Ein immutable Invocation Request beschreibt ausschließlich einen beantragten
Aufruf. Er führt Invocation-, Requestor-, Provider-, Authorization-, Authority-
und Capability-Referenzen, angeforderte Operation und Operation Mode, maximale
Answer-Betriebsart, Kontext- und optionale Source-Chain-Bindungen,
Eingabevertragsreferenz und Schema-Version, immutable Eingabereferenz,
deklarierte Input-Constraints, erforderliche Kontrollen, Request-Zeitpunkt,
Unsicherheit, Review und Provenienz.

Der Request führt nichts aus, lädt und interpretiert keine Eingaben,
authentifiziert und autorisiert niemanden, wählt keinen Provider und verändert
keinen Zustand.

## Zulässige Grenze v1

Die Boundary v1 ist ausschließlich für `B1_GENERAL_ORIENTATION` vorgesehen.
Zulässig sind nur bereits bereitgestellte Requests mit nicht personenbezogener
oder ausdrücklich entpersonalisierter Bindung, `READ_ONLY`, `SIMULATION` oder
deklarativem `DEGRADED`, gültiger Provider-Identität und Autorisierung,
passender Authority und Capability sowie vollständiger Snapshot-, Kontroll-
und Provenienzbindung.

Nicht zulässig sind B2, B3, `READ_WRITE`, `PRIVILEGED`, Zustandsänderungen,
personenbezogene Recherche sowie Werkzeug-, Workflow- oder Runtime-Aktivierung.

## Operation Modes

Typisierte Operation Modes:

- `READ_ONLY`
- `SIMULATION`
- `DEGRADED`
- `READ_WRITE`
- `PRIVILEGED`

In v1 sind ausschließlich `READ_ONLY`, `SIMULATION` und `DEGRADED` zulässig.
`READ_WRITE` und `PRIVILEGED` werden abgelehnt oder blockiert. `DEGRADED` ist
nur eine bereitgestellte Kennzeichnung; die Boundary erkennt keinen Ausfall
und berechnet keinen Degradationszustand.

## Requestor-Grenze

Der Requestor wird nur durch eine bereitgestellte Referenz dokumentiert. Die
Boundary authentifiziert ihn nicht, erzeugt keine Identity Tokens, validiert
keine Credentials, verwaltet keine Maschinenidentitäten und entscheidet keine
Delegationskette. Sie prüft ausschließlich strukturelle Referenzkonsistenz.

## Authorization-Grenze

Eine Invocation kann nur als grundsätzlich zulässig dokumentiert werden, wenn
Provider Identity und Authorization Package strukturell gültig sind, der Grant
ausdrücklich `AUTHORIZED` ist, keine bereitgestellte Lifecycle-Evidence die
Gültigkeit ausschließt, Authority und Capability passen, die
Verantwortungsgrenze und Kontrollen eingehalten werden, gemeinsame
Akteursklassen vollständig bereitgestellt sind und der Resolution Snapshot den
verwendeten Grant enthält.

Zeitwerte berechnen keinen Status. Ablauf, Widerruf und Aussetzung müssen durch
bestehende Lifecycle-Evidence bereitgestellt sein.

## Eingabegrenze

ADR-0050 definiert keine allgemeine JSON-Schema-, Sanitizing- oder
Injection-Engine. Der Request darf Referenzen auf Eingabevertrag,
Input-Schema-Version und immutable Eingabe sowie deklarierte Constraints
führen. Der Validator prüft nur deren Struktur.

Es gibt keine Inhaltsanalyse, HTML- oder Script-Erkennung, automatische
Sanitization, Binärdatenprüfung, Dateiannahme, Schema-Runtime oder semantische
Validierung.

## Kontext- und Quellenbindungen

Bereits bereitgestellte Bindungen können Jurisdiction, Purpose, Gesprächs- oder
Journey-Kontext und eine entpersonalisierte Datenbereichsreferenz führen.
Source-Chain-Referenzen dürfen geführt werden, wenn die Capability sie
verlangt. Die Boundary beschafft, öffnet oder bewertet keine Quelle, erkennt
keinen Quellenwechsel und führt keine Recherche aus.

## Invocation Decision

Die immutable Invocation Decision dokumentiert eine bereits bereitgestellte
Entscheidung:

- `ACCEPTED`: Vertrags- und Schutzvoraussetzungen sind unter den
  bereitgestellten Nachweisen erfüllt.
- `REJECTED`: fachliche oder strukturelle Voraussetzungen sind nicht erfüllt.
- `BLOCKED`: eine Schutz-, Lifecycle-, Kontroll- oder Governance-Grenze
  verhindert die Zulässigkeit.

`ACCEPTED` bedeutet nur, dass der Request grundsätzlich zulässig wäre. Es führt
nichts aus, öffnet keine Runtime, aktiviert keine Capability, autorisiert
keinen Provider und erzeugt kein fachliches Ergebnis.

## Ablehnungs- und Blockierungsgründe

Typisierte Gründe:

- `PROVIDER_UNKNOWN`
- `AUTHORIZATION_MISSING`
- `AUTHORIZATION_NOT_AUTHORIZED`
- `AUTHORIZATION_SUSPENDED`
- `AUTHORIZATION_REVOKED`
- `AUTHORIZATION_EXPIRED`
- `AUTHORITY_MISMATCH`
- `CAPABILITY_DENIED`
- `RESPONSIBILITY_BOUNDARY_EXCEEDED`
- `CONTROL_LEVEL_INSUFFICIENT`
- `JOINT_CONTROL_INCOMPLETE`
- `OPERATION_MODE_NOT_ALLOWED`
- `CLASSIFICATION_TOO_HIGH`
- `CONTEXT_BINDING_MISSING`
- `SOURCE_BINDING_MISSING`
- `RESOLUTION_SNAPSHOT_MISSING`
- `RESOLUTION_SNAPSHOT_INCONSISTENT`
- `INPUT_CONTRACT_MISSING`
- `PROVENANCE_INCONSISTENT`
- `GOVERNANCE_GAP`

Es gibt keine Retry-, Rate-Limit-, Replay-, Circuit-Breaker- oder
Incident-Logik.

## Invocation Evidence

Immutable Invocation Evidence dokumentiert Evidence-, Invocation-, Request-
und Decision-Referenz, geprüfte Provider Identity, Authorization, Authority,
Provider-Resolution-Snapshot und Lifecycle-Evidence, Schutzstufe, Operation
Mode, Kontrollstufe, Konflikte, Validatorreferenzen, vollständige bestandene
und fehlgeschlagene Prüfschritte, Ergebnis, Review und Provenienz. Sie trifft
keine Entscheidung und führt nichts aus.

## Invocation Receipt

Der immutable Invocation Receipt wird durch eine reine deterministische
Funktion aus der validierten Boundary und ausdrücklich bereitgestellten
Receipt-ID, Zeitpunkt-, Review- und Provenienzangaben erzeugt. Er dokumentiert
Invocation-, Decision- und Evidence-Referenz, Decision-Status,
Authority-Chain-Referenzen, Prüfstatus sowie bestandene und fehlgeschlagene
Prüfungen.

Der Receipt wird nicht persistiert oder signiert, enthält keine Kryptographie
und berechtigt nicht zur Ausführung. Es wird kein Audit Log implementiert.

## Resolution Snapshot

Der immutable read-only Invocation Resolution Snapshot projiziert für einen
validierten `ACCEPTED`-Nachweis dieselben Request-, Decision-, Evidence-,
Receipt-, Provider-, Authority-, Authorization-, Lifecycle- und
Provider-Snapshot-Objekte. Zusätzlich zeigt er Capability, Operation Mode,
Answer-Betriebsart, Kontrollen, Kontext- und Quellenbindungen, Review,
Unsicherheit und Provenienz.

Er erzeugt keinen Request, trifft keine Decision, verändert keinen Status,
wählt keinen Provider, erteilt keine Authorization, aktiviert keine Capability
und startet keine Runtime.

## Deterministischer Validator

Der Validator verwendet unverändert den bestehenden
`GuardianProviderAuthorizationValidator`, der seinerseits das Guardian
Authority Model und sämtliche Provider-, Grant-, Decision-, Lifecycle- und
Provider-Snapshot-Invarianten prüft. Die kanonische
`GuardianAnswerBoundaryValidator`-Prüfung wird für die B1-Grenze
wiederverwendet.

Danach prüft der Invocation Validator globale IDs, Objektidentitäten und
Referenzen, Authority und Capability, Verantwortungsgrenze, Kontrollen,
gemeinsame Akteursklassen, Authorization- und Lifecycle-Status, ausschließlich
B1, zulässigen Operation Mode, Kontext-, Source- und Eingabebindungen,
Decision-Status und -Grund, Evidence-Vollständigkeit, Receipt-Konsistenz und
Provenienz.

Bei Erfolg bleiben sämtliche Eingabeobjekte unverändert. Der Validator führt
keine Capability aus, authentifiziert niemanden, berechnet keinen Status, wählt
keinen Provider, erzeugt keine Authorization und löst keine Konflikte.

## Fail-closed-Grundsatz

Kann ein erforderlicher Nachweis nicht vollständig und widerspruchsfrei
validiert werden, darf kein `ACCEPTED`-Nachweis entstehen. Fail-closed ist eine
deterministische Vertragsregel, keine Runtime-Ausfalllogik.

## Widersprüche und Objections

ADR-0050 führt kein Widerspruchsregister und keine Objection-Runtime ein.
Bestehende typisierte Governance-Sperren dürfen referenziert werden. Fehlt eine
kanonische Objection-Regel, wird keine Regel improvisiert; der Pfad wird als
`GOVERNANCE_GAP` blockiert.

## Nicht-Ziele

- keine Runtime, Provider-Ausführung oder Capability-Aktivierung,
- keine LLM-Aufrufe, Recherche, Quellenbeschaffung oder Antwortgenerierung,
- keine natürliche Sprache, automatische Klassifikation oder Providerwahl,
- keine automatische Authorization, Invocation oder Statusberechnung,
- keine Kryptographie, Hash- oder Signaturalgorithmen,
- keine Credentials, Identity Tokens oder Secrets,
- keine Netzwerkzugriffe, Persistenz oder Audit Logs,
- keine Replay-Erkennung, Rate-Limits, Circuit Breaker oder Retry-Logik,
- kein Scheduling, keine Incident-Runtime oder Kontaktaufnahme,
- keine Workflow-, Werkzeug-, Domänen- oder Routingaktivierung,
- keine UI und keine allgemeine Policy-, IAM- oder RBAC-Engine,
- keine Platzhalter-Hooks für spätere Runtime-Macht.

## Konsequenz

ZONVAA kann formal und deterministisch nachweisen, ob ein bereitgestellter
B1-Invocation-Request unter den bereitgestellten Authority-, Provider-,
Authorization-, Lifecycle-, Kontroll- und Kontextnachweisen grundsätzlich
zulässig wäre. Das System führt weiterhin nichts aus.

Eine reale read-only B1 Provider Runtime benötigt eine eigene
Architekturentscheidung. Sie darf nicht allein durch einen `ACCEPTED`-Receipt
aktiviert werden.
