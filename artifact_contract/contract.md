# ZONVAA Artefakt- und Autorisierungszustandsvertrag

Version: 1.0
Status: abgeleiteter technischer Vertrag
Normstufe: C2/C3

Normative Entscheidung:
`knowledge/adr/ADR-0030-artifact-authorization-state-contract.md`

## Vertragsgrenze

Der Vertrag konkretisiert die in MDR-0001 und Interaction festgelegte Grenze
zwischen Gespräch, strukturiertem Artefakt und ausdrücklich autorisierter
Handlung. Er ist keine neue Architekturschicht, keine Persistenz und keine
ausführende Workflow- oder Rechte-Engine.

Gesprächsinhalte erzeugen weder ein Artefakt noch Rechte, Freigaben oder
Zustandswechsel. `execution.DocumentArtifact` bleibt davon getrennt und
bezeichnet ausschließlich einen sicheren Plan zur Erzeugung neuer
Wissensdokumente.

## Artefaktzustände

Der stabile Zustandsraum besteht aus:

- `draft`: noch nicht als persönliches Artefakt übernommen,
- `personal`: ausschließlich im persönlichen Verantwortungsraum,
- `ready_for_authorization`: für eine konkrete Freigabe vorbereitet,
- `shared`: aufgrund einer dokumentierten Autorisierung sichtbar,
- `suspended`: vorübergehend ohne aktive gemeinsame Nutzung,
- `archived`: nicht mehr aktiv, aber nach seiner Historienklasse erhalten,
- `expired`: durch eine ausdrücklich dokumentierte Regel nicht mehr aktiv.

Diese Zustände beschreiben ausschließlich Systemzustand. Sie heißen weder
rechtlich wirksam noch fachlich geprüft und erzeugen keine Außenwirkung.

## Hoheit und Beteiligung

Jedes Artefakt besitzt genau einen verantwortlichen `sovereign_id`. Weitere
Personen können ausschließlich als explizit benannte Beteiligte und über eine
eigene Autorisierung handeln. Familienbeziehung, Betreuung, Bevollmächtigung
oder Gesprächsteilnahme leiten keine Rolle und keinen Zugriff ab.

Der Hoheitsträger bleibt von den Beteiligten unterscheidbar. Das Modell
erfindet, überträgt oder ersetzt keine rechtliche Rolle.

## Autorisierung

Eine Autorisierung ist unveränderlich beschrieben durch stabile ID,
Subjekt, erteilenden Hoheitsträger, mindestens einen granularen Umfang,
konkreten Zweck, Status und zeitzonenbewussten Zeitpunkt. Unterstützte
Umfänge sind `read`, `contribute`, `authorize_action` und
`manage_sharing`.

Nur ausdrücklich benannte Beteiligte erhalten Autorisierungen. Ein Widerruf
trägt einen eigenen Zeitpunkt und wirkt im Modell unmittelbar. Dokumentierte
rechtliche oder technische Bindungen werden nur referenziert; der Vertrag
interpretiert oder erfindet sie nicht.

## Zustandsübergänge

Jeder Übergang besitzt eine stabile ID, Artefaktbezug, einen typisierten
Übergang, Ausgangs- und Zielzustand, autorisierenden Akteur,
zeitzonenbewussten Zeitpunkt, Begründung, Normstufe und eine ausdrückliche
Irreversibilitätsangabe.

Übergänge bilden eine einzige chronologische Kette. Ein Zustandswechsel ohne
passenden Audit-Eintrag, ein fallfremder Übergang oder eine parallele
stillschweigende Überschreibung ist ungültig. Außer dem Hoheitsträger darf nur
ein aktiv und ausdrücklich für `authorize_action` autorisierter Beteiligter
einen Übergang tragen.

Irreversibilität wird je Übergang dokumentiert. Sie wird nicht pauschal aus
Zustandsnamen, Dokumentarten oder fachlichen Annahmen abgeleitet.

## Historienklassen

Historien werden ausdrücklich einer Datenklasse zugeordnet:

- `immutable`,
- `retention_required`,
- `deletable`,
- `anonymizable`.

Die Klassifikation behauptet weder pauschale Unlöschbarkeit noch eine konkrete
Aufbewahrungs- oder Löschfrist. Die spätere Ausführung benötigt dokumentierte
Rechts-, Datenschutz-, Memory- und Sicherheitsregeln.

Alle Historienklassen müssen in dokumentierten Formaten exportierbar und ohne
aktive Guardian-Beziehung langfristig interpretierbar bleiben. Der Vertrag
implementiert weder Export noch Aufbewahrung.

## Normhierarchie

C2 bestimmt Prinzipien, Rollen, Vetos und Prüfpflichten. C3 bestimmt
veränderbare Fristen, Gesten, Quoren, Risikoabstufungen und technische
Verfahren. Kein Zustandsübergang erhält durch diesen Vertrag C1-Rang.

Runtime lädt genau einen versionierten Vertragsnachweis und bleibt technische
Single Source of Truth. Preflight weist Version, Hash und die vollständigen
stabilen Typmengen nach. Operative Komponenten erhalten daraus keine
stillschweigende Handlungsvollmacht.

## Ausdrücklich nicht festgelegt

Nicht Bestandteil dieses Vertrags sind:

- feste Zeitfenster, Gesten oder Quorumsgrößen,
- Biometrie-, SMS-, Token- oder andere konkrete Bestätigungsverfahren,
- konkrete Kryptografie, Signatur oder Zero-Knowledge-Verfahren,
- rechtliche Wirksamkeits-, Beweis- oder Haftungsgarantien,
- automatische Notfall-, Amts- oder externe Ereignisübergänge,
- pauschale Unlöschbarkeit aller Historien,
- UI, Netzwerk, Cloud, Datenbank oder Dokumentanalyse.
