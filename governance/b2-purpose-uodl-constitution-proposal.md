# B2 Purpose- und UODL-Bindungsverfassung – Entscheidungsvorlage v1

Dokument-ID: `GOV-B2-PURPOSE-UODL-BINDING-PROPOSAL-V1`

Status: `VORGESCHLAGEN – NICHT RATIFIZIERT – NICHT IMPLEMENTIERUNGSFREIGEGEBEN – NICHT IMPLEMENTIERT`

Stand: 03.08.2026

## Gegenstand und Grenze

Diese Entscheidungsvorlage schließt keinen der im Review
`GOV-B2-CONSTITUTIONAL-REVIEW-0059-0062-V1` festgestellten Blocker. Sie macht
die zwei fachlich zusammengehörigen Übersetzungsgrenzen entscheidungsreif:

1. Corridor-`purpose` und `purpose_binding` aus ADR-0059 gegenüber dem
   typisierten `B2PurposeScope` aus ADR-0060;
2. `StorageOperation.REFERENCE` aus ADR-0059 gegenüber
   `B2UODLOperation.REFERENCE_ONLY` aus ADR-0060 und ADR-0062.

Beide Fragen betreffen dieselbe nicht ausführende Bindungsgrenze zwischen
Datenkorridor und Autorisierung. Deshalb werden sie gemeinsam analysiert,
aber als getrennte Entscheidungen bewertet. Dieses Dokument ist keine ADR,
keine Ratifizierung, keine Implementierungsfreigabe und keine Migration. Der
ratifizierungsreife Inhalt wurde ohne Freigabewirkung in den formalen
Vorschlag ADR-0063 überführt. Capability Invocation und Runtime bleiben
weiterhin nicht begonnen.

## Teil A – Purpose Binding Constitution

### Bestehender Stand

- ADR-0059 führt `B2DataCorridor.purpose` und
  `B2ConsentBoundary.purpose_binding` als nicht leere Strings. Der Validator
  beweist deren Gleichheit, aber keine fachliche Semantik.
- ADR-0060 führt `B2PurposeScope` als geschlossene Kombination aus
  `B2ConsentUse` und den kanonischen erlaubten Datenklassen aus ADR-0059. Die
  Halbordnung erlaubt Gleichheit oder Verengung und verbietet Erweiterung.
- `B2Grant`, die Authorization Evaluation und ADR-0062 verwenden ausschließlich
  den typisierten `B2PurposeScope`.
- Die End-to-End-Integration prüft Datenklassen, Nutzungen und Referenz-IDs,
  besitzt jedoch keine ratifizierte Abbildung des freien Corridor-Zwecks auf
  den typisierten Scope.

Damit bestehen derzeit zwei syntaktische Purpose-Darstellungen, aber nur
`B2PurposeScope` trägt eine geschlossene, beweisbare fachliche Halbordnung.
Freie Purpose-Texte dürfen weder interpretiert noch implizit konvertiert
werden. Evidence, Provenienz und Validatorannahmen ersetzen keine Bindung.

### Varianten

| Variante | Eine Wahrheit / Halbordnung | Rückwärtskompatibilität / Migration | Beweisbarkeit und Wartbarkeit | Risiko |
|---|---|---|---|---|
| 1. ADR-0059 referenziert unmittelbar `B2PurposeScope` | eine fachliche Wahrheit; Halbordnung vollständig | öffentlicher Vertragswechsel und Migrationsbedarf; Abhängigkeit von ADR-0059 auf die spätere ADR-0060 | sehr gut nach Migration | Schichtenumkehr und Breaking Change |
| 2. geschlossenes Mapping-Objekt zwischen Corridor Purpose und `B2PurposeScope` | Mapping kann exakt sein; freie Ausgangswerte bleiben jedoch zweite Semantik | bestehende Objekte bleiben darstellbar | nur beweisbar, wenn jedes Paar institutionell geschlossen ist | Mapping-Liste kann Parallelverfassung werden |
| 3. ADR-0059-Purpose bleibt syntaktischer Vorläufer mit Mapping-Evidence | typisierter Scope bleibt fachlich maßgeblich | hohe Kompatibilität, aber dauerhafte Legacy-Last | rekonstruierbar, solange Text niemals interpretiert wird | zwei Darstellungen und Drift bleiben sichtbar |
| 4. kanonischer typisierter Purpose-Bindungsnachweis | `B2PurposeScope` ist einzige fachliche Purpose-Verfassung; ein immutable Nachweis bindet Corridor-ID und exakten Scope ohne Textinterpretation | explizite Migration der Bindung, vorhandener Text bleibt nur nicht autoritative historische Darstellung | vollständig typisiert; Gleichheit und Verengung folgen der bestehenden Halbordnung | geringstes Parallelverfassungsrisiko, aber ratifizierungs- und migrationspflichtig |

### Bevorzugte Variante

**Vorgeschlagen ist Variante 4.** `B2PurposeScope` aus ADR-0060 bleibt die
einzige kanonische fachliche Purpose-Verfassung. Ein späterer, ausdrücklich
ratifizierter immutable Purpose-Bindungsnachweis dürfte ausschließlich eine
Corridor-Referenz und einen konkreten `B2PurposeScope` binden. Er enthält keine
zweite Purpose-Liste, keinen freien fachlichen Text und keine
Konvertierungslogik. Der bestehende ADR-0059-String wäre nur eine historische,
nicht autoritative Darstellung und dürfte keine Authorization beeinflussen.

Bewegung ist ausschließlich zum gleichen oder engeren Scope gemäß der bereits
kanonischen `contains`-Halbordnung zulässig. Nicht vergleichbare Scopes,
fehlende Bindung oder ein breiterer Ziel-Scope schließen eine positive
Bewertung aus. Keine impliziten Defaults, keine automatische Heilung und keine
Purpose-Eskalation sind zulässig.

Diese Präferenz ist **nicht ratifiziert, nicht implementierungsfreigegeben und
nicht implementiert**. Ihre spätere Annahme verlangt einen eigenständigen
Architekturakt sowie getrennte Migrations- und Implementierungsentscheidungen.

## Teil B – UODL Reference Constitution

### Bestehender Stand

- ADR-0059 prüft für die Corridor-UODL-Referenz die Operation
  `StorageOperation.REFERENCE`.
- ADR-0060 schließt die Authorization-UODL-Operation auf
  `B2UODLOperation.REFERENCE_ONLY`.
- ADR-0062 verwendet `REFERENCE_ONLY` als einen von genau sechs ratifizierten
  Hooks: Reference Identity, Grant Binding, AAV Binding, `REFERENCE_ONLY`,
  Temporal Effectiveness sowie User Ownership / Reference before Copy.
- Namensähnlichkeit beweist weder Identität noch Halbordnung. Es existiert
  keine ratifizierte Abbildung zwischen beiden Enum-Werten.

Beide Ebenen erlauben weder Lesen, Kopieren, Schreiben noch Speichern
personenbezogener Inhalte. Es gibt keine Inhalts-, Provider-, Invocation- oder
Runtime-Operation.

### Varianten

| Variante | Schutzwirkung und Beweisbarkeit | Kompatibilität / Migration | Parallelverfassungsrisiko |
|---|---|---|---|
| 1. kanonische Identität beider Typen | einfach, setzt aber bisher unbelegte semantische Identität voraus | Typmigration oder Alias nötig | Alias kann Ebenen verwischen |
| 2. `REFERENCE_ONLY` ist strenger als `REFERENCE` | erhält eine Halbordnung | zusätzliche Ordnungsregel erforderlich | neue, bislang nicht belegte Operationssemantik |
| 3. Ebenentrennung ohne Mapping | Corridor und Authorization bleiben sauber getrennt | vollständig kompatibel | End-to-End-Bindung bleibt unbeweisbar |
| 4. explizites immutable Mapping mit typisierten zulässigen Paaren | keine String-Konvertierung; nur ausdrücklich ratifizierte Paarung ist gültig | vorhandene Typen bleiben erhalten; Mapping-Nachweis wird zusätzlich benötigt | gering, wenn die Paarmenge geschlossen und allein kanonisch ist |
| 5. ein neuer gemeinsamer Operationscode | eine technische Darstellung | Breaking Change und Migration beider Schichten | neue Meta-Verfassung mit unnötiger Reichweite |

### Bevorzugte Variante

**Vorgeschlagen ist Variante 4.** Die Ebenentrennung bleibt erhalten. Ein
späterer immutable Mapping-Nachweis dürfte als einzige geschlossene Paarung
`StorageOperation.REFERENCE` zu `B2UODLOperation.REFERENCE_ONLY` ausweisen.
Er begründet keine allgemeine Enum-Konvertierung und keine Identitätsbehauptung.
Alle anderen Paare und alle nicht ratifizierten Operationen bleiben
unzulässig. Die Abbildung erlaubt ausschließlich Referenzbindung; sie erzeugt
weder Inhaltszugriff noch Kopie, Schreiben, Speicherung, Provider-Ausführung,
Invocation oder Runtime.

Diese Präferenz ist **nicht ratifiziert, nicht implementierungsfreigegeben und
nicht implementiert**. Bis zu einer gesonderten Entscheidung bleibt die
End-to-End-Operationsabbildung unbeweisbar und muss fail closed bleiben.

## Verworfene Varianten

- Purpose-Variante 1 ist fachlich sauber, würde aber ohne getrennte
  Migrationsentscheidung bestehende öffentliche Verträge brechen.
- Purpose-Varianten 2 und 3 lassen freie Purpose-Semantik als potenzielle
  zweite Wahrheit bestehen.
- UODL-Varianten 1 und 2 behaupten nicht ratifizierte Identität oder Ordnung.
- UODL-Variante 3 löst den Nachweisblocker nicht; Variante 5 schafft eine neue
  übergeordnete Operationsverfassung.

## Offene Entscheidungsfragen

1. Soll `B2PurposeScope` institutionell als einzige fachliche
   Purpose-Verfassung auch für den Corridor bestätigt werden?
2. Wie werden bestehende Corridor-Objekte ohne rückwirkende Textinterpretation
   auf einen expliziten Purpose-Bindungsnachweis migriert?
3. Soll genau das Paar `REFERENCE`/`REFERENCE_ONLY` als zulässige
   Ebenenabbildung ratifiziert werden?
4. Benötigen Architekturentscheidung, Migration und Implementierung getrennte
   institutionelle Freigaben?

## Vorgeschlagener späterer Paketschnitt

Purpose Binding und UODL Reference Mapping sollen aufgrund ihrer gemeinsamen
Corridor-zu-Authorization-Grenze in genau einer zukünftigen fachlichen
Architektur-ADR entschieden werden. Ihre Nummer darf erst im gesonderten
Architekturauftrag aus dem dann aktuellen ADR-Stand bestimmt werden. Der
historische Governance-Nachweis und die allgemeine Governance-Incident-
Architektur gehören ausdrücklich nicht in diese fachliche ADR.

Ratifizierung, Migration bestehender Verträge, Implementierungsfreigabe und
Implementierung bleiben vier getrennte spätere Vorgänge. Diese Vorlage nimmt
keinen davon vorweg.

## Prüffrage Null

> Kann durch die vorgeschlagene Architektur ein breiterer Purpose, eine nicht
> kanonisch abgebildete UODL-Operation, Autorisierung, Invocation, Runtime-Macht
> oder ein unerlaubter personenbezogener Zustand entstehen?

Antwort: **Nein.** Die bevorzugten Varianten sind geschlossen, referenzieren
die bestehenden kanonischen Typen, interpretieren keine Strings und bleiben
ohne Ratifizierung sowie getrennte Implementierungsfreigabe wirkungslos.
