# ADR-0056 – Physical Operational Persistence v1

## Status

RATIFIZIERT – 02.08.2026

## Kontext

ADR-0055 definiert einen geschlossenen, immutable Operational-Memory-Vertrag
für bereits validierte maschinengenerierte Betriebsartefakte. Eine physische
Speichergrenze fehlte bislang. ADR-0056 ergänzt diese Grenze, ohne ein
Speichermedium auszuwählen oder Operational Memory mit Infrastruktur zu
vermischen.

## Entscheidung

Physical Operational Persistence folgt Operational Memory, niemals umgekehrt.
Persistierbar sind ausschließlich bereits durch den kanonischen
`OperationalMemoryValidator` validierte Operational-Memory-Objekte. Die
Persistenzschicht erzeugt, kopiert, interpretiert, ergänzt oder verändert kein
fachliches oder technisches Artefakt.

Logisches Gedächtnis und physisches Speichermedium bleiben strikt getrennt.
Operational Memory bestimmt die zulässigen Artefakte und ihre unveränderliche
Identität. Physical Persistence dokumentiert ausschließlich den bereitgestellten
Speichervorgang und dessen opaque physische Referenz.

## Kanonischer Persistence Port

`PhysicalOperationalPersistencePort` ist die einzige medienneutrale
Port-Schnittstelle. Sie erhält einen immutable `PersistencePortRequest` und
liefert ein typisiertes `PersistencePortResult`. Die Operationen sind
geschlossen auf:

- `STORE`,
- `READ`,
- `EXISTS`.

Request und Result führen die referenzierte Artefaktidentität, Version und eine
opaque physische Speicherreferenz. Das Result dokumentiert ausschließlich den
bereitgestellten Ergebnisstatus. Der Port enthält keine Datenbank-, Datei-,
Cloud-, Netzwerk-, Serialisierungs- oder Credential-Regel.

ADR-0056 implementiert keine konkrete Port-Implementierung. Ein späterer
Speicheradapter muss austauschbar bleiben und darf ausschließlich diesen Port
implementieren. Das Speichermedium darf weder Governance- noch Runtime-Regeln
definieren.

## Physical Persistence Record

`PhysicalPersistenceRecord` bindet genau einen validierten
`OperationalMemoryRecord` an Artefaktreferenz und -version, bereitgestellten
Persistierungsstatus, opaque physische Speicherreferenz, Port-Resultat,
Persistierungszeitpunkt, Review und Provenienz.

Ein als `PERSISTED` deklarierter Record benötigt ein konsistentes `STORE`-Resultat
mit `STORED`. Operational-Memory-Objektidentität, Referenz, Version, Review und
Provenienz bleiben unverändert. Zwei physische Records mit derselben Kombination
aus Artefaktreferenz und Version sind Duplikate und werden abgelehnt.

## Backup und Recovery

Backup und Recovery gehören ab dieser Stufe zur Betriebsarchitektur. v1
implementiert ausschließlich immutable Nachweisverträge:

- `PhysicalBackupContract` bindet einen Persistenzsatz an Status, Zeitpunkt,
  Vollständigkeitsstatus, Review und Provenienz.
- `PhysicalRecoveryContract` bindet optional einen vorhandenen Backupvertrag an
  Status, Zeitpunkt, Vollständigkeitsnachweis, Review und Provenienz.

Jeder physische Persistenzsatz benötigt genau einen Backupvertrag. Ein als
abgeschlossen deklarierter Backupvertrag muss als vollständig deklariert sein.
Eine abgeschlossene Recovery benötigt einen vollständigen abgeschlossenen
Backupvertrag und einen nicht leeren Vollständigkeitsnachweis.

Die Verträge planen, starten oder überwachen weder Backup noch Recovery. Sie
wählen kein Medium, kopieren keine Daten und verändern keine Speicherreferenz.

## Validator

Der deterministische `PhysicalOperationalPersistenceValidator` verwendet
zuerst den bestehenden `OperationalMemoryValidator`. Danach prüft er:

- globale eindeutige Identitäten,
- identische validierte Operational-Memory-Objekte,
- bekannte Operational-Memory-Referenzen,
- konsistente Artefaktreferenzen und Versionen,
- konsistente Port-Requests und Port-Results,
- opaque und eindeutige physische Speicherreferenzen,
- keine doppelte Persistierung derselben Artefaktversion,
- vollständige Review- und Provenienzbindung,
- genau einen Backupvertrag je Persistenzsatz,
- bekannte und strukturell konsistente Recovery-Referenzen.

Bei Erfolg gibt der Validator dasselbe Package unverändert zurück. Er ruft den
Port nicht auf, persistiert nichts und führt weder Backup noch Recovery aus.

## Read-only Snapshot

Der immutable `PhysicalOperationalPersistenceSnapshot` projiziert dieselben
Packages, Operational-Memory-Records, Artefaktbindungen, Persistenz-, Backup-
und Recoverystatus, Versionen, Review und Provenienz. Er liest kein Medium,
verändert keinen Record und löst keine Operation aus.

## Nutzer- und Machtgrenze

Die geschlossene Nicht-Nutzerdaten-Grenze aus ADR-0053 und ADR-0055 bleibt
vollständig erhalten. Physical Persistence kann ausschließlich Objekte aus
einem validierten Operational-Memory-Package binden. Nutzerdaten,
Gesprächsinhalte, Nutzerprofile, Nutzungsmuster und personenbezogene Artefakte
sind auf dieser Ebene nicht darstellbar.

Persistenz besitzt keine Runtime- oder Governance-Macht. Ein erfolgreicher
Speichernachweis aktiviert keine Capability, keinen Provider, keine Runtime,
keinen Workflow und keine fachliche Entscheidung.

## Verhältnis zu offenen Lebenszyklusentscheidungen

ADR-0056 führt keine Archivierungs-, Lösch-, Verfalls-, Retention-,
Replikations- oder Wiederherstellungsstrategie ein. Die in ADR-0055 definierten
Entscheidungsauslöser bleiben verbindlich. Der Port darf nicht als
stillschweigende dauerhafte Append-only-Strategie interpretiert werden.

## B2/B3 Operational Gate

ADR-0056 implementiert weder Metriken noch Benachrichtigungen und keine konkrete
produktive Speicheranbindung. Das Gate aus ADR-0054 und ADR-0055 bleibt daher
ausdrücklich geschlossen. Physical Persistence v1 autorisiert keine B2- oder
B3-Runtime.

## Nicht-Ziele

- keine konkrete Datenbank, Tabelle, Abfragesprache oder Migration,
- keine konkrete Datei-, Verzeichnis- oder Serialisierungsstruktur,
- keine Cloud-, Netzwerk-, Provider- oder Credential-Anbindung,
- keine konkrete Port-Implementierung oder Storage Engine,
- keine physische Backup- oder Recovery-Ausführung,
- keine Archivierung, Löschung, Retention, Replikation oder Wiederherstellung,
- keine Metriken, Benachrichtigungen, Telemetrie oder Analytics,
- keine Runtime-, Audit-, Evidence- oder Incident-Erweiterung,
- keine Nutzerdaten, Gesprächsinhalte oder personenbezogenen Artefakte,
- keine Workflow-, Werkzeug-, Provider- oder Capability-Aktivierung,
- keine UI und keine allgemeine Data-, Records- oder Storage-Plattform,
- keine Platzhalter-Hooks für spätere Betriebsfunktionen.

## Konsequenz

ZONVAA besitzt einen kanonischen, technologieneutralen Port und vollständig
immutable Verträge für bereits eingetretene physische Operational-Memory-
Speichervorgänge sowie Backup- und Recovery-Nachweise. Ein reales Medium kann
später nur hinter diesem Port angeschlossen werden; v1 wählt oder betreibt
keines.
