# Institutionelle Implementierungsfreigabe – ADR-0063 B2 Purpose and UODL Binding Constitution v1

Dokument-ID: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0063-V1`

Status: `INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG`

## Provenienz und Zeittrennung

- Beschlussdatum: 03.08.2026
- Externe Beschlusszeit: 03.08.2026, 20:00:35 Uhr Europe/Berlin (CEST,
  UTC+02:00)
- Repository-Dokumentationszeit: 03.08.2026, 20:00:39 Uhr Europe/Berlin
  (CEST, UTC+02:00)
- Entscheidungsrolle: Institutionsgründer
- Repository-Ausgangsstand: `e61414d149e4f7284ac782326b58d0c6eaa71560`
- Ratifizierung: `GOV-RATIFICATION-ADR-0063-V1`
- Scope-Regel: `GOV-INSTITUTIONAL-DECISION-SCOPE-1`

Der erste Zeitpunkt ist der tatsächliche Zeitpunkt der gegenwärtigen,
außerhalb des Repositories gefassten menschlichen Implementierungsfreigabe.
Der zweite Zeitpunkt bezeichnet ausschließlich ihre spätere Repository-
Dokumentation. Keine frühere Gutachterbewertung wird als Beschlusszeitpunkt
verwendet. Die Freigabe ist nicht rückwirkend.

## Grundlage

ADR-0063 ist ratifiziert. Ratifizierung und institutionelle
Implementierungsfreigabe sind zwei getrennte menschliche Beschlüsse. Diese
Freigabe betrifft ausschließlich die ratifizierte Architektur von ADR-0063.
ADR-0064 bleibt fachlich unabhängig, ratifiziert, aber nicht
implementierungsfreigegeben oder implementiert.

## Freigegeben

Die spätere Implementierung ist ausschließlich freigegeben für:

- die ratifizierte Architektur von ADR-0063;
- `B2PurposeScope` als einzige fachlich autoritative B2-Purpose-Verfassung;
- einen immutable typisierten Purpose-Bindungsnachweis;
- die Bindung zwischen Corridor-Referenz und kanonischem `B2PurposeScope`;
- ausschließlich identische oder nachweisbar engere Purpose Scopes;
- fail closed bei fehlender, inkonsistenter oder nicht vergleichbarer
  Purpose-Bindung;
- eine explizite typisierte Vergleichsrelation;
- ausschließlich nicht personenbezogene Provenienz;
- explizit übergebene timezone-aware Erstellungs- oder Auswertungszeitpunkte,
  soweit ADR-0063 sie vorsieht;
- den Ausschluss interner Zeit- und Zustandsquellen;
- ein immutable typisiertes UODL-Mapping;
- die Ebenentrennung von `StorageOperation.REFERENCE` und
  `B2UODLOperation.REFERENCE_ONLY`;
- ausschließlich das geschlossene Paar
  `StorageOperation.REFERENCE` → `B2UODLOperation.REFERENCE_ONLY`;
- fail closed bei fehlendem oder abweichendem UODL-Mapping;
- sämtliche ratifizierten Invarianten und Negative Rules;
- erforderliche Validatoren und öffentliche Exporte;
- vollständige fokussierte Positiv- und Negativtests;
- minimale kanonische Dokumentationsanpassungen im Implementierungspaket.

## Ausdrücklich nicht freigegeben

Nicht freigegeben sind:

- automatische Migration oder manuelle beziehungsweise automatische
  Umdeutung bestehender ADR-0059-Purpose-Werte;
- Interpretation freier Purpose-Texte, semantische Textanalyse,
  Ähnlichkeitszuordnung oder Default-Mapping;
- implizite Purpose-Konvertierung, Purpose-Erweiterung, Bewegung zu breiteren
  Scopes oder Akzeptanz nicht vergleichbarer Scopes;
- zweite Purpose-Verfassung oder Purpose-Liste sowie Änderung oder Erweiterung
  bestehender `B2PurposeScope`-Werte ohne gesonderte Architekturentscheidung;
- String-, Alias- oder namensbasiertes Mapping und implizite UODL-Konvertierung;
- zusätzliche UODL-Operationen oder UODL-Hooks;
- Lesen, Schreiben, Kopieren, Inhaltszugriff oder Speicherung
  personenbezogener Inhalte;
- Provider-Ausführung, Capability Invocation, Runtime oder technische
  Ausführung;
- personenbezogene Verarbeitung oder Speicherung und natürliche Personen;
- Sessions, Caches, Tokens, Permissions, Schlüsselmaterial, Key Custody,
  Tools, Callbacks oder Runtime-Handles;
- Observation, Runtime Audit, Operational Memory, Metrics oder Notifications;
- externe Integrationen oder produktive Provider-Anbindungen;
- Änderung der ratifizierten Semantik von ADR-0059 bis ADR-0063;
- Implementierung oder Implementierungsfreigabe von ADR-0064;
- heutige oder rückwirkende ADR-0059-Bestätigung;
- Commit oder Push.

Fehlende Nennungen gelten niemals als stillschweigende Freigabe.

## Verfassungsinvarianten

- Es existiert genau eine fachlich autoritative B2-Purpose-Verfassung.
- Purpose darf nur identisch bleiben oder nachweisbar enger werden.
- Fehlende, inkonsistente oder nicht vergleichbare Bindungen bleiben fail
  closed.
- Die beiden UODL-Operationen bleiben typisiert getrennt; nur das ratifizierte
  Paar ist explizit abbildbar.
- Evidence und Provenienz ersetzen weder Purpose-Bindung noch Mapping.
- Prüffrage Null aus ADR-0063 bleibt verbindlich und muss mit **Nein**
  beantwortet bleiben.

## Wirkung und nächstes Gate

ADR-0063 ist ratifiziert und institutionell implementierungsfreigegeben, aber
weiterhin nicht implementiert. Dieses Dokument erzeugt selbst keine Purpose-
Bindung, kein UODL-Mapping, keine Autorisierung, Invocation, Runtime oder
technische Macht und ist kein Implementierungsauftrag.

Ein separater Implementierungsauftrag darf erst nach nachweisbarem Push des
Freigabe-Commits auf `origin/builder-reset-v2` erteilt werden. Die gewählte
Repository-Reihenfolge erzeugt keine fachliche Unterordnung zwischen ADR-0063
und ADR-0064.
