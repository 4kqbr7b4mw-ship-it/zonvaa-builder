# Architektur-Review B2-Verfassung – ADR-0059 bis ADR-0062

Dokument-ID: `GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1`

Status: Maintenance-Review abgeschlossen; zwei Architekturblocker durch
ratifizierte ADR-0063 architektonisch entschieden, implementiert und validiert

Governance-Evidenzstatus: durch ADR-0064 und ADR-0064-A1 implementiert und validiert

Stand: 03.08.2026

## Scope und Grenze

Geprüft wurde die nicht ausführende Referenzkette:

`Data Corridor → Authority → Grant → Provider Identity → Provider Authorization`

Grundlagen waren ADR-0059 bis ADR-0062, ihre Ratifikations- und
Implementierungsfreigaben, Architekturkarte, Readiness, Package Map,
Projektstatus, `PLANS.md`, die vier Implementierungsmodule, ihre Validatoren,
öffentlichen Exporte sowie Architektur-, Dokumentations-, Public-API- und
Handover-Tests. Dieses Review ist weder ADR noch Ratifizierung oder Freigabe.
Es definiert keine neue Semantik und bereitet weder Capability Invocation noch
Runtime vor.

## Befunde 1 bis 15

### 1. Begriffskonsistenz

`Authority`, `Grant`, `Provider Identity` und `Provider Authorization` sind
getrennt. Provider bezeichnet ab ADR-0061 ausschließlich institutionelle oder
fachliche Leistungseinheiten, niemals natürliche Personen. `Evaluation`
bezeichnet eine punktuelle Ableitung; `Evidence` ausschließlich deren
Rekonstruktionsnachweis. Zwei offene Übersetzungen zwischen `purpose` und
`Purpose Scope` sowie zwischen `REFERENCE` und `REFERENCE_ONLY` sind unter
Architekturblocker dokumentiert und wurden nicht umgedeutet.

### 2. Redundante Invarianten

Kanonische Quellen bleiben: ADR-0059 für Corridor- und Negativgrenzen,
ADR-0060 für Authority, Grant, Purpose Scope und Authorization Evaluation,
ADR-0061 für Provider Identity und ADR-0062 für deren punktuelle Anwendung.
Lokale Kurzfassungen in Statusdokumenten sind nur Verweise; sie ersetzen keine
dieser Quellen. Historische Beschlussdokumente wurden nicht umgeschrieben.

### 3. Doppelte Negativregeln

`PROHIBITED_B2_DATA_CLASSES` und die übrigen Corridor-Verbotsmengen werden
ausschließlich in `governance/b2_data_corridor.py` definiert.
`B2PurposeScope` importiert `ALLOWED_B2_DATA_CLASSES`; Provider Authorization
verwendet Corridor- und ADR-0060-Validatoren. Es existiert keine zweite
Datenklassen- oder Verbotsliste. ADR-spezifische Feldverbote bleiben wegen
ihrer unterschiedlichen Objekte getrennt.

### 4. Wiederverwendbare Validatoren

`B2ProviderAuthorizationEvaluator` und
`B2AuthorizationFoundationValidator` verwenden unverändert
`B2DataCorridorValidator`, `B2AuthorizationEvaluator` und
`B2ProviderAuthorizationValidator`. Die kleinen lokalen Typ-, Referenz- und
Zeitprüfungen bleiben modulnah; ein gemeinsamer Universalvalidator würde eine
neue technische Wahrheitsquelle schaffen und wurde deshalb nicht eingeführt.

### 5. Evidence-Strukturen

Positive Evaluation Evidence und Negative Governance Evidence sind immutable,
typisiert und punktuell. Beide tragen expliziten Auswertungszeitpunkt,
Referenzen, geschlossene Gründe und Vertragsversion. Positive Evidence besitzt
keine fortwirkende Berechtigungswirkung; negative Evidence keine Sperr-,
Sanktions-, Profil- oder Entscheidungswirkung. Eine gemeinsame Basisklasse
wurde wegen der unterschiedlichen fachlichen Aussage nicht eingeführt.

### 6. Provenienzmodelle

ADR-0061-Provenienz beschreibt die Provider Identity. ADR-0062 referenziert
deren typisierte nicht personenbezogene IDs und ergänzt ausschließlich die
eigene Evaluations-, Grant- und Zeitpunktbindung. Provenienz ersetzt keinen
D3-, T4-, AAV-, UODL-, Grant- oder Evidence-Nachweis und bestätigt sich nicht
selbst. Freie Identitäts- oder Provenienztexte sind nicht modellierbar.

### 7. UODL-Konsistenz

ADR-0062 und seine Implementierung verwenden ausschließlich die sechs
ratifizierten Hooks: UODL Reference Identity, Grant Binding, AAV Binding,
`REFERENCE_ONLY`, Temporal Effectiveness und User Ownership / Reference before
Copy. Inhalts-, Speicher-, Provider-, Invocation- oder Runtime-Hooks sind
nicht vorhanden. Die nicht entschiedene Namensabbildung zur ADR-0059-Operation
`StorageOperation.REFERENCE` bleibt fail closed und ist als Blocker sichtbar.

### 8. Public API

Alle vier Typfamilien besitzen stabile Exporte über `governance`. Die
Provider-Authorization-Exporte werden wegen der existierenden Importkette
lazy geladen; dadurch bleibt der öffentliche Importpfad stabil und ein Zyklus
zwischen Corridor-, Authorization- und Provider-Modulen wird vermieden.
Runtime-, Invocation- oder Adaptertypen werden nicht exportiert. Es wurde kein
Breaking Change vorgenommen.

### 9. Lesbarkeit und Wartbarkeit

Die Module bleiben nach Verfassungsgegenstand getrennt. Wiederholte
Test-Fixtures wurden nicht in eine produktive Hilfsschicht verschoben, weil
dies Abhängigkeiten zwischen getrennten Verträgen erzeugen würde. Konstruktoren
haben keine versteckten Defaults für Zeit oder Wirksamkeit. Das Review ergänzt
nur fehlende Beweise für Identitätsunveränderlichkeit und Provenienzbindung.

### 10. Grenze zu Capability Invocation

Provider Authorization endet bei der Aussage, ob ein vollständig
bereitgestellter Grant für eine unveränderte Provider Identity zu einem
expliziten Zeitpunkt wirksam ausgewertet wurde. Selbst positive Evidence ist
kein Aufruf, Token, Handle, Session, Runtime-Recht oder Ausführungsauftrag.
Capability Invocation bleibt gesperrt; es wurde kein Request-, Decision- oder
Invocation-Vertrag angelegt.

### 11. Governance-Sequenz

Die Sollfolge lautet Architektur, ADR-Dokumentation, Validierung,
Ratifizierung, deren Dokumentation/Commit/Push, getrennte institutionelle
Freigabe mit Dokumentation/Commit/Push, separater Implementierungsauftrag,
Implementierung, Tests/Review sowie getrennte Commit- und Push-Freigaben.

- ADR-0060 und ADR-0062 sind durch getrennte Architektur-, Ratifikations-,
  Freigabe- und Implementierungscommits nachvollziehbar.
- Für ADR-0061 ist der Prozessvorfall „Implementierungsbeginn vor kanonischem
  Freigabe-Push“ in der ADR-0062-Freigabe und im institutionellen Ablauf
  referenziert. Der Freigabe-Commit wurde nachträglich gepusht; der Arbeitsstand
  wurde erst nach einem neuen Auftrag geprüft und anschließend separat
  committed. Der ursprüngliche Beginn wird nicht rückwirkend umgedeutet.
- Für ADR-0059 ist kein eigenständiger Ratifikationsnachweis im Repository
  auffindbar. Die vorhandene institutionelle Freigabe und der kombinierte
  Implementierungscommit belegen nicht alle 18 Sollschritte. Diese historische
  Dokumentationslücke wird nicht rekonstruiert.
- Ein eigenes kanonisches Governance-Incident-Ledger existiert weiterhin nicht;
  ADR-0052 ist ausschließlich Runtime Incidents vorbehalten.

ADR-0064 hat den Zielort später ratifiziert, ließ aber die für vollständige
Verträge erforderlichen geschlossenen Typmengen offen. Der deshalb blockierte
partielle Arbeitsstand ist ausschließlich in einem benannten Stash gesichert.
ADR-0064-A1 ratifiziert die fehlenden Taxonomien ausschließlich als
Architektur. Seine getrennte Implementierungsfreigabe ist gültig, erzeugt aber
keine Implementierung oder Stash-Anwendung und verändert die historischen
Review-Befunde nicht.

### 12. Gesperrte Bereiche

Der gemeinsame Kern bleibt: keine natürliche Person, keine personenbezogene
Verarbeitung oder Speicherung, keine Invocation, Runtime, technische
Ausführung, Tools, Sessions, Caches, Tokens, Schlüssel, Inhaltszugriffe oder
Betriebsintegration. Stärkere lokale Sperren bleiben erhalten. Fehlende
Nennungen sind nach `GOV-INSTITUTIONAL-DECISION-SCOPE-1` keine Freigabe.

### 13. Trennung ADR-0061 und ADR-0062

Provider Identity enthält weder Authority, Grant, Permission,
Autorisierungs- noch Wirksamkeitszustand. Provider Authorization speichert nur
die unveränderte Identity-ID, erzeugt keine Identity und verändert weder
Provider Class, Responsibility Areas noch Capability Descriptoren. Beide sind
getrennte immutable Objekte; natürliche Personen sind strukturell abgelehnt.

### 14. Testabdeckung

| Kanonische Invariante | ADR | Implementierung | Positiver Test | Negativer Test / Lücke |
|---|---|---|---|---|
| vollständiger Corridor und Negativregeln | 0059 | `b2_data_corridor.py` | `test_valid_corridor_consent_depersonalization_and_snapshot_are_immutable` | `test_each_negative_rule_family_is_mandatory` |
| D3 notwendig, nie hinreichend; T4 getrennt | 0060/0062 | `b2_authorization.py`, `b2_provider_authorization.py` | `test_positive_evaluation_requires_every_current_binding` | `test_d3_and_t4_never_replace_each_other` |
| Purpose gleich oder enger | 0060 | `B2PurposeScope`, `B2Grant` | `test_equal_and_narrower_grant_scopes_are_allowed` | `test_grant_scope_expansion_is_structurally_rejected`; Corridor-Purpose-Mapping offen |
| explizite timezone-aware Zeit, kein Zustand | 0060/0062 | beide Evaluatoren | deterministische Positivtests | naive Zeit und Quelltextprüfung ohne Uhr/Repository/Service |
| Provider Identity beschreibt nur | 0061 | `b2_provider_identity.py` | immutable Identity | Personen-, Status-, Permission-, Invocation-, Runtime- und B1-Negativtests |
| Identity bleibt bei Authorization unverändert | 0061/0062 | `b2_provider_authorization.py` | vollständige Referenzkette | `test_provider_authorization_preserves_identity_semantics_and_identity` |
| Provenienz ersetzt keinen Nachweis | 0062 | Provider-Validator/Evaluator | gültige Provenienzbindung | `test_provenance_cannot_replace_evaluation_evidence` |
| ausschließlich ratifizierte UODL-Hooks | 0062 | `B2UODLOperation` | `REFERENCE_ONLY`-Positivpfad | `test_only_the_ratified_uodl_hook_is_modelable`; Namensmapping zu ADR-0059 offen |
| Evidence ohne Macht | 0060/0062 | positive/negative Evidence | rekonstruierbare Evidence | Token-, Cache-, Permission-, Sperr-, Sanktions- und Profiltests |
| keine technische Ausführung | 0062 | Foundation | vollständige immutable Kette | Runtime-, Invocation-, Tool-, Session-, Cache-, Token-, Schlüssel- und Inhaltszugriffstests |

### 15. Eintopf-Prüfung

Corridor, Authority, Grant, Provider Identity, Provider Authorization,
Evaluation und Evidence sind mechanisch verbunden, aber fachlich getrennt.
UODL-Referenz ist kein Inhaltszugriff; Provenienz ist keine Autorisierung;
Negative Governance Evidence ist keine Sperre. Es wurde keine Trennung
vorgenommen, die eine neue fachliche Entscheidung verlangt hätte.

## Zulässige Korrekturen

- Readiness-Freigabegrenze auf die tatsächlich getrennt freigegebenen und
  implementierten ADR-0059- bis ADR-0062-Pakete präzisiert.
- Institutionellen Ablauf um aktuellen Abschlussstatus und bekannte
  Prozessabweichungen ergänzt, ohne Historie umzuschreiben.
- Zwei fehlende Negativ-/Identitätsbeweise ergänzt.
- Architekturkarte, Plan, Produktstatus und Handover referenzieren dieses
  Review als Maintenance-Nachweis ohne Freigabewirkung.

Produktive Verträge, Enums, Validatorlogik und Public API wurden nicht
verändert. Redundante Verbotslisten wurden nicht gefunden; daher wurde keine
Liste entfernt und keine neue Meta-Verfassung geschaffen.

## Nicht durchgeführte Änderungen und Architekturblocker

### A. Corridor-Purpose und typisierter Purpose Scope

- Fundstellen: `B2DataCorridor.purpose` und
  `B2ConsentBoundary.purpose_binding` in ADR-0059 gegenüber
  `B2PurposeScope` in ADR-0060.
- Wirkung: Die Integration prüft Datenklassen und Nutzungen, kann aber keine
  ratifizierte semantische Gleichheit zwischen dem freien Corridor-Zweck und
  dem typisierten Grant-Scope beweisen.
- Entscheidungsfrage: Soll ADR-0059 einen kanonischen typisierten Purpose
  referenzieren oder soll eine ausdrücklich ratifizierte, geschlossene
  Mapping-Regel eingeführt werden?

### B. UODL-Operationsnamen

- Fundstellen: `StorageOperation.REFERENCE` in ADR-0059 und
  `B2UODLOperation.REFERENCE_ONLY` in ADR-0060/0062.
- Wirkung: Referenzidentität und AAV-Bindung sind prüfbar, eine semantische
  Äquivalenz der beiden Operationscodes ist jedoch nicht ratifiziert.
- Entscheidungsfrage: Sind beide Codes ausdrücklich äquivalent, oder benötigt
  die B2-Verfassung einen einzigen kanonischen Operationscode?

### C. Historische Governance-Evidenz

- Für ADR-0059 fehlt ein eigenständiger Ratifikationsnachweis.
- Für den ADR-0061-Prozessvorfall fehlt ein eigenständiger kanonischer
  Governance-Incident-Zielort; er ist nur in bestehenden Governance-Dokumenten
  referenziert.
- Entscheidungsfrage: Soll ein begrenzter historischer Nachweis beziehungsweise
  ein eigener Governance-Prozessvorfall-Ort durch gesonderten Architekturakt
  geschaffen werden? Dieses Review erfindet beides nicht.

## Prüffrage Null und Stabilitätsaussage

> Kann durch irgendeine Änderung dieses Review-Pakets ein unerlaubter
> personenbezogener Zustand modelliert, eine neue Autorisierung erzeugt, eine
> gesperrte Macht geöffnet, eine Invocation vorbereitet oder eine
> Runtime-Ausführung ermöglicht werden?

Antwort: **Nein.** Das Paket verändert keine produktiven Verträge oder
Validatorsemantik. Die B2-Verfassungsgrundlage ist innerhalb ihrer
nicht ausführenden Grenzen stabil; ihre vollständige semantische
End-to-End-Geschlossenheit bleibt bis zur Entscheidung der zwei fachlichen
Mapping-Blocker eingeschränkt. Der Governance-Evidenzblocker zu ADR-0059 und
zum fehlenden kanonischen Governance-Incident-Zielort bleibt ebenfalls offen.

ADR-0063, ADR-0064 und die Ergänzung ADR-0064-A1 sind getrennt ratifiziert,
implementierungsfreigegeben, implementiert und validiert. ADR-0064/A1 schließt
den Governance-Evidenzblocker ausschließlich mit nicht ausführenden,
evidenzgebundenen Verträgen. Keine Freigabe oder Implementierung erzeugt eine
fachliche Unterordnung, automatische Entscheidung oder Ausführungswirkung.
Die damals nicht begonnene Capability Invocation ist nun ausschließlich als
ADR-0065-Architektur dokumentiert und getrennt durch
`GOV-RATIFICATION-ADR-0065-V1` ratifiziert. Es wurde kein produktiver Vertrag,
Validator oder ausführendes Modul außerhalb des begrenzt freigegebenen
ADR-0065-Moduls angelegt. ADR-0065 ist durch
`GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0065-V1` begrenzt
implementierungsfreigegeben, implementiert und validiert; Runtime bleibt
gesperrt.

## ADR-0066 Runtime-Air-Gap-Ergänzung

ADR-0066 ist als eigenständige rein deklaratorische Ergänzung vorgeschlagen,
nicht ratifiziert, nicht implementierungsfreigegeben und nicht implementiert.
ADR-0065 bleibt die einzige kanonische Invocation-Verfassung. Der neue
Vorschlag dokumentiert ausschließlich, dass nach dem kontrollierten Stopp kein
technischer oder impliziter Übergang existiert und eine hypothetische Runtime
nur durch einen neuen menschlichen Verfassungsakt überhaupt diskutiert werden
dürfte. Die Future B2 Package Map nahm bislang mit „B2 Provider Runtime“ und
einer Invocation-Abhängigkeit einen nicht ratifizierten Folgeschritt vorweg;
diese Planungssemantik wird entfernt. Es entsteht keine technische Komponente,
Runtime Readiness, Ratifizierung, Freigabe oder Implementierung.
