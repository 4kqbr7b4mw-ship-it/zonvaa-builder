# ADR-0055 – Operational Memory v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0051 bis ADR-0054 erzeugen beziehungsweise prüfen immutable technische
Runtime-, Observation-, Incident- und Audit-Nachweise. Bislang fehlt eine
verfassungsrechtlich begrenzte Beschreibung, welche dieser bereits validierten
Betriebsartefakte als Speicherobjekte abgebildet werden dürfen.

## Entscheidung

Operational Memory v1 ist ausschließlich die persistenzneutrale,
deterministisch validierbare Abbildung bereits validierter,
maschinengenerierter Betriebsartefakte. Persistenz folgt Audit, niemals
umgekehrt. Operational Memory erzeugt, ergänzt, interpretiert oder verändert
keinen Nachweis.

Alle Speicherverträge sind immutable. Laufzeitobjekte und Speicherobjekte
bleiben vollständig getrennt: Ein `OperationalMemoryRecord` referenziert einen
unveränderten Artefaktstand, während eine `OperationalMemoryArtifactBinding`
die identische bereits validierte Objektinstanz für die Strukturprüfung führt.
Der Record ist weder Kopie noch neue Version des Artefakts.

## Zulässige Betriebsartefakte

Der geschlossene Katalog umfasst ausschließlich:

- Observation Governance,
- Runtime Execution,
- Runtime Result,
- Runtime Execution Evidence,
- Runtime Execution Receipt,
- Incident Evidence,
- scope-gebundene No-Incident Evidence,
- Audit Profile,
- Audit Scope,
- Audit Evidence,
- Runtime Audit Resolution Snapshot.

Diese Artefakte müssen über ihre bestehenden kanonischen Validation Envelopes
und Validatoren vollständig validiert sein. Eine Speicherabbildung ersetzt
keine Validation und kann fehlende Evidence nicht ergänzen.

## Absolute Nicht-Nutzerdaten-Grenze

Operational Memory speichert ausschließlich maschinengenerierte
Betriebsevidenzen. Nutzerdaten, Gesprächsinhalte, Nutzerprofile,
Nutzungsmuster, themenbezogene Nutzungsinformationen, personenbezogene
Artefakte und nutzeridentifizierende Metadaten sind keine zulässigen
Artefakttypen.

Die Nicht-Nutzerdaten-Grenze aus ADR-0053 wird vollständig geerbt. Sie darf
weder durch freie Typbezeichnungen, generische Payloads, Locator-Felder noch
eine allgemeine Storage-Abstraktion umgangen werden. Der Artefaktkatalog ist
geschlossen und enthält keine User-Data-, Conversation-, Profile- oder
Content-Variante.

## Abgrenzung zu AAV und UODL

AAV bleibt für zustandsbehaftete Autorisierungen und deren unveränderbare
Nachweise zuständig. Operational Memory erteilt, ändert oder widerruft keine
Autorisierung.

UODL bleibt die providerneutrale Hoheitsgrenze für nutzerkontrollierte Daten.
Seine `StorageReference` ist kein Operational-Memory-Artefakt und seine
Operationen werden hier weder übernommen noch ausgeführt. Die vollständige
Hoheitsarchitektur für Nutzerdaten, insbesondere AAV/UODL, bleibt ein
separater späterer Architekturbaustein.

## Operational Memory Record und Package

`OperationalMemoryRecord` führt Memory-ID, kanonischen Artefakttyp,
Artefaktreferenz und -version, bereitgestellten Persistierungszeitpunkt,
maschinelle Herkunft, Reviewstatus und Provenienz.

`OperationalMemoryPackage` führt immutable Records und direkte Bindungen an
die unveränderten Artefaktobjekte. Observation-, Incident- und Audit-Packages
dienen ausschließlich als bereits vorhandene Validation Contexts. Sie werden
nicht umgeformt und begründen keine automatische physische Speicherung.

## Duplikatidentität

Zwei Records sind Duplikate, wenn ihre Kombination aus Artefaktreferenz und
Artefaktversion identisch ist. Eine andere Memory-ID, Provenienz oder ein
anderer Persistierungszeitpunkt erzeugt keinen neuen zulässigen Record.
Duplikate werden deterministisch abgelehnt.

## Validator und Snapshot

Der `OperationalMemoryValidator` verwendet die bestehenden Observation-,
Incident- und Audit-Validatoren. Er prüft den geschlossenen Artefaktkatalog,
identische validierte Objektinstanzen, Referenzen, Versionen, Herkunft, Review,
Provenienz, globale Memory-Identitäten und die Duplikatregel. Bei Erfolg wird
dasselbe Package unverändert zurückgegeben.

Der read-only `OperationalMemorySnapshot` projiziert dieselben Records,
Artefaktbindungen, Typen, Versionen, Reviewstatus, Provenienzen und bereits
bereitgestellte Validierungslücken. Er lädt, interpretiert, ergänzt, verändert,
löscht, archiviert oder repliziert kein Artefakt und berechnet keine Metrik.

## Persistenzgrenze

Im Repository existiert keine kanonische, begrenzte physische
Persistenzschnittstelle für Betriebsevidenz. `KnowledgeManager` validiert
Wissens- und UODL-Referenzen ohne sie zu persistieren. Die bestehende
Memory-Klassifikation begründet ausdrücklich keinen eigenen Speicher. UODL ist
ein Referenzvertrag und kein Speicherprodukt.

Operational Memory v1 implementiert deshalb ausschließlich Speicherverträge,
Package, Validator und Snapshot. Es führt keine Datenbank, Dateiablage,
Storage Engine, Repository-Schnittstelle oder physische Schreiboperation ein.
Reale physische Speicherung bleibt bis zu einer gesonderten ratifizierten
Architekturentscheidung blockiert.

## Offene Entscheidungen und verbindlicher Auslöser

Noch nicht entschieden sind:

- Lösch- und Verfallsstrategie,
- Archivierungsstrategie,
- gesetzliche oder vertragliche Aufbewahrungsfristen,
- technische Replikations- und Wiederherstellungsstrategie.

Diese Punkte müssen spätestens entschieden werden:

1. bevor der erste Artefakttyp mit gesetzlicher, regulatorischer oder
   vertraglicher Aufbewahrungs- oder Löschpflicht persistiert wird, oder
2. vor dem ersten produktiven Betrieb mit realen Runtime-, Incident- oder
   Audit-Evidenzen,

je nachdem, welches Ereignis zuerst eintritt.

Die offenen Punkte dürfen nicht stillschweigend als dauerhafte
Append-only-Strategie behandelt werden.

## B2/B3 Operational Gate

Die Sperre aus ADR-0054 bleibt vollständig bestehen. Operational Memory v1
hebt sie nicht auf. Eine B2- oder B3-Runtime darf weder architektonisch
freigegeben noch implementiert werden, solange der vollständige
Operational-Memory-Block einschließlich Persistenz, Metriken und
Benachrichtigungen nicht ratifiziert, implementiert und validiert ist.

Dieses v1-Paket implementiert keine physische Persistenz, keine Metriken und
keine Benachrichtigungen. Das Gate ist daher ausdrücklich nicht erfüllt.

## Nicht-Ziele

- keine Nutzerdatenpersistenz, Gesprächsinhalte oder personenbezogenen Artefakte,
- keine Nutzerprofile, Nutzungsmuster oder themenbezogene Nutzeranalyse,
- keine konkrete Datenbank, Dateiablage oder allgemeine Storage Engine,
- keine physische Persistierung und kein dauerhaftes Audit-Log,
- keine Metriken, Benachrichtigungen, Telemetrie oder Analytics,
- keine Archivierung, Löschung, Verfallslogik oder Retention Engine,
- keine Replikation, Backups oder Wiederherstellung,
- keine Runtime-, Audit- oder Evidence-Erweiterung,
- keine Incident-Erkennung oder No-Incident-Ableitung,
- keine Workflow-, Werkzeug- oder Capability-Aktivierung,
- keine UI, Compliance-, Records-Management- oder Data-Governance-Plattform,
- keine Platzhalter-Hooks für spätere Speicherfunktionen.

## Konsequenz

ZONVAA besitzt einen geschlossenen, reviewbaren Vertrag dafür, welche bereits
validierten technischen Betriebsartefakte künftig gespeichert werden dürften.
Physische Persistenz und ihr vollständiger Lebenszyklus bleiben blockiert, bis
die offenen Entscheidungen rechtzeitig gesondert ratifiziert sind.
