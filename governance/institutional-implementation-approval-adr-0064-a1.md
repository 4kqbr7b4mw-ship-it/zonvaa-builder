# Institutionelle Implementierungsfreigabe – ADR-0064-A1 Governance Decision and Incident Closed Taxonomies v1

Dokument-ID: `GOV-B2-IMPLEMENTATION-APPROVAL-ADR-0064-A1-V1`

Status: `INSTITUTIONELLE IMPLEMENTIERUNGSFREIGABE – GÜLTIG – NOCH NICHT IMPLEMENTIERT`

## Provenienz und Zeittrennung

- Beschlussdatum: 03.08.2026
- Externe Beschlusszeit: 03.08.2026, 23:04:51 Uhr Europe/Berlin (CEST,
  UTC+02:00)
- Repository-Dokumentationszeit: 03.08.2026, 23:05:39 Uhr Europe/Berlin
  (CEST, UTC+02:00)
- Entscheidungsrolle: Institutionsgründer
- Repository-Ausgangsstand: `c734f6bd30bfff0c979b85ca98ef82107fce13a5`
- Ratifizierung: `GOV-RATIFICATION-ADR-0064-A1-V1`
- Scope-Regel: `GOV-INSTITUTIONAL-DECISION-SCOPE-1`

Der erste Zeitpunkt ist der tatsächliche Zeitpunkt der gegenwärtigen,
außerhalb des Repositories gefassten menschlichen Implementierungsfreigabe.
Der zweite Zeitpunkt bezeichnet ausschließlich die spätere Repository-
Dokumentation. Der Beschluss ist nicht rückwirkend.

## Grundlage und Status

ADR-0064-A1 ist ratifiziert und institutionell implementierungsfreigegeben,
aber weiterhin nicht implementiert. ADR-0064 bleibt ratifiziert und
implementierungsfreigegeben, aber weiterhin nicht vollständig implementiert.
Diese Freigabe erzeugt selbst keinen Decision Record, keine Incident Evidence,
keine Scope-Freigabe, Autorisierung, Observation, Runtime oder technische
Macht.

## Freigegeben

Freigegeben ist ausschließlich eine spätere Implementierung der ratifizierten
ADR-0064-A1-Architektur:

- die vier Decision Classes `ARCHITECTURE_RATIFICATION`,
  `INSTITUTIONAL_IMPLEMENTATION_APPROVAL`, `COMMIT_APPROVAL` und
  `PUSH_APPROVAL`;
- die Rollen `INSTITUTION_FOUNDER`, `CHIEF_ARCHITECT` und `REVIEWER` innerhalb
  ihrer ratifizierten Grenzen;
- `REVIEWER` ohne Decision Class, Ratifizierungs- oder Freigabewirkung;
- `CHIEF_ARCHITECT` ohne neue institutionelle Entscheidungsbefugnis;
- die 18 getrennten Governance-Schritte;
- die Scope-Architektur aus geschlossenem Scope-Typ, kanonischer
  Artefaktreferenz und maschinenlesbarer Abschnittsreferenz;
- die getrennten Mengen `GRANTED_SCOPE` und `EXCLUDED_SCOPE` sowie fehlende
  Nennung als Nichtfreigabe;
- die ratifizierten Abweichungscodes, Evidence-Arten, Missing-Evidence-Arten
  und Missing-Evidence-Status;
- die ratifizierten Auswirkungscodes, Korrekturfolgeschritte,
  Dokumentationsstände und Beobachtungs- und Aussageumfänge;
- die ratifizierten Provenienz-Artefaktklassen und Provenienz-Kontexte;
- die ratifizierten Klassen offener Entscheidungsfragen;
- erforderliche immutable Verträge, zustandslose Validatoren und öffentliche
  Exporte;
- vollständige fokussierte Positiv-, Negativ-, Integrations-, Public-API- und
  Dokumentationstests;
- minimale kanonische Dokumentationsanpassungen innerhalb des späteren
  Implementierungspakets;
- die vollständige Neuprüfung des gesicherten partiellen Arbeitsstands gegen
  ADR-0064 und ADR-0064-A1 in einem späteren separaten Implementierungsauftrag.

## Ausdrücklich nicht freigegeben

Nicht freigegeben sind:

- Anwendung, Pop, Drop, Umbenennung oder Veränderung des Stash in diesem
  Dokumentationsauftrag;
- automatische, ungeprüfte oder teilweise Übernahme des gesicherten
  Arbeitsstands oder einzelner Stash-Dateien;
- Fortsetzung der Implementierung in diesem Auftrag;
- automatische Entscheidungen, Ratifizierungen, Implementierungsfreigaben,
  Scope-Erweiterungen, Record- oder Incident-Erzeugung;
- automatische Incident-Klassifikation historischer Vorgänge oder
  rückwirkende Legitimierung;
- Änderung des ADR-0059-Nachweisstatus oder heutige beziehungsweise
  rückwirkende ADR-0059-Bestätigung;
- weitere Decision Classes, Incident Classes oder institutionelle Rollen;
- freie Scope-Semantik oder freie Governance-Regeln;
- natürliche Personen, personenbezogene Identitäten, Profile,
  Leistungsbewertungen, Sanktionen, Sperr- oder Autorisierungswirkung;
- Observation, Überwachung, Runtime Audit, Operational Memory, Metrics,
  Notifications, Capability Invocation, Runtime oder technische Ausführung;
- personenbezogene Verarbeitung oder Speicherung, ADR-0065, produktive
  Python-Änderungen, Commit und Push.

Fehlende Nennungen sind keine stillschweigende Freigabe.

## Stash-Grenze

Der Stash `ADR-0064 partial implementation blocked before closed taxonomies`
mit der bei Dokumentation geprüften Referenz `stash@{0}` und OID
`f1e6f58aedf31d8617c83b68f9ea899c9aae9e43` bleibt ein nicht kanonischer,
gesicherter Arbeitsstand. Diese Freigabe erlaubt in diesem Auftrag weder seine
Anwendung noch seine technische Übernahme. Eine bloße Stash-Anwendung gilt
niemals als Implementierungsgenehmigung.

Unvereinbare Bestandteile dürfen nicht übernommen werden. Vereinbare
Bestandteile dürfen erst nach ausdrücklicher Einzelprüfung im späteren
Implementierungsauftrag übernommen werden.

## Nächstes Gate und Wiederaufnahme

Ein separater Implementierungsauftrag darf erst nach Commit und nachweisbarem
Push dieser Freigabe erteilt werden. Er muss den vollständigen Stash gegen
ADR-0064 und ADR-0064-A1 neu prüfen. Die Reihenfolge lautet:

1. Dokumentation dieser Implementierungsfreigabe;
2. eigener Commit;
3. nachweisbarer Push;
4. separater Implementierungsauftrag;
5. vollständige Neuprüfung des Stash;
6. ausschließlich ausdrücklich geprüfte Übernahme oder Korrektur.

ADR-0065 bleibt nicht begonnen und gesperrt. Prüffrage Null bleibt
verbindlich.

## Rollenbegrenzung

Der Institutionsgründer handelt in konstituierender Funktion bis zur ersten
ordentlichen Sitzung des Vertrauensrats. Die Rolle ist keine natürliche Person
als fachliches Vertragsobjekt. Diese Freigabe behauptet keine Ratssitzung,
Abstimmung, Ratsmitglieder oder Voten.
