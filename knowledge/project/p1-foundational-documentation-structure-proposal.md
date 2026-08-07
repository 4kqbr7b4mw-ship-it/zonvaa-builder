# P1 – Foundational Vision & Canonical Glossary: Dokumentationsstruktur

Status: **NICHT NORMATIVER STRUKTURVORSCHLAG – KEINE VISION – KEIN GLOSSAR – KEINE ARCHITEKTUR**

## 1. Zweck und Grenze

Dieses Dokument bereitet ausschließlich die Dokumentationsstruktur einer
neuen Produktphase vor. Es formuliert keine Gründervision, definiert keinen
Begriff und ändert weder Architektur noch Governance. ADR-0059 bis ADR-0066
bleiben unverändert und allein für die B2-Verfassungsfamilie maßgeblich.

Der Vorschlag erzeugt keine Freigabe, Aktivierung, Runtime, Observation,
personenbezogene Verarbeitung oder technische Komponente. Ein späteres
Dokument wird durch seine hier genannte Position nicht automatisch zulässig
oder kanonisch.

## 2. Repositorybefund

Die vorhandene Dokumentation trennt ihre Verantwortungen erkennbar:

| Bereich | Vorhandene Verantwortung | Folgerung für P1 |
| --- | --- | --- |
| `constitution/` | oberste Schutz- und Machtgrenzen | kein P1-Verwahrort |
| `knowledge/adr/` | Architekturentscheidungen | Glossar und Vision gehören nicht hierher |
| `governance/` | Governance-Regeln, Beschlüsse, Nachweise und Architekturstatus | kein Verwahrort für Produktsemantik |
| `knowledge/guardian/` | historische und erläuternde Guardian-Grundlagen; MDR-0001 hat für Conversation und Continuity Vorrang | vorhandene Quellen bleiben referenzierbar, werden aber nicht zur neuen Gründervision umgedeutet |
| `knowledge/project/` | kanonischer Produktstatus, fachliche Produktdokumentation, Validierungen und Referenzreisen | geeigneter bestehender P1-Verwahrort |
| `knowledge/mdr/` | bereits konsolidierte materielle Regelentscheidung | kein Glossar-Verwahrort |
| `knowledge/roadmaps/` | vorhandene fachliche Roadmap | nur für tatsächlich freigegebene Roadmaps, nicht für diesen Strukturvorschlag |

Weitere Konventionen sind stabile, sprechende Dateinamen in `kebab-case`,
relative Markdown-Links, eine explizite Status- und Scope-Grenze sowie die
Trennung zwischen aktueller Wahrheit, historischer Quelle und bloßer
Referenz. Die bestehende Human-Journey-Dokumentation liegt als fachliches
Produktartefakt bereits in `knowledge/project/`.

## 3. Vorgeschlagene Zielstruktur

Die kleinste konventionskonforme Struktur bleibt flach in
`knowledge/project/`. Unterverzeichnisse würden erst bei einer nachgewiesenen
Menge gleichartiger Dokumente nötig und werden durch P1 nicht vorweggenommen.

| Zukünftige Dokumentklasse | Vorgeschlagenes Namensmuster | Verantwortung | Nicht-Verantwortung |
| --- | --- | --- | --- |
| Gründervision | `foundational-vision-v1.md` | eine später ausdrücklich beauftragte, versionierte Produktvision | keine Architektur, Governance-Regel oder Aktivierung |
| Glossar-Übersicht | `canonical-glossary-v1.md` | späterer Index kanonisierter Begriffe und ihrer stabilen Identifier | keine Ontologie, kein Validator, kein Codegenerator |
| Glossar-Einträge | zunächst Abschnitte im Glossar; erst bei belegter Größe `glossary-<identifier>.md` | eine kanonische Begriffseinheit | keine freie Dateizerlegung ohne Index |
| Semantische Infrastruktur | `semantic-infrastructure-boundaries-v1.md` | spätere dokumentarische Beschreibung von Zuständigkeiten, Referenzen und Grenzen | keine technische Infrastruktur, kein Datenmodell, keine Runtime |
| Human Journey | `human-journey-<fachlicher-slug>-v1.md` | fachliche, menschenzentrierte Referenzreise | keine Nutzerbeobachtung, kein Workflow- oder Runtime-Auftrag |
| Phase-Status | bestehendes `current-product-status.md` | erst nach tatsächlich abgeschlossenem Produktauftrag aktueller Stand | keine Vorab-Freigabe |

### 3.1 Navigationsprinzip

Ein späteres `canonical-glossary-v1.md` sollte der einzige Einstiegspunkt für
kanonische Produktbegriffe sein. Ein Begriff verweist von dort auf vorhandene
materielle Regelinhaber; er ersetzt sie nicht. ADRs und Governance-Dokumente
verweisen nur dann zurück, wenn ein eigener späterer Auftrag dies ausdrücklich
zulässt. P1 erzeugt keine solchen Rückverweise.

### 3.2 Referenzierungsprinzip

- Dateipfad und Dokument-Identifier erfüllen unterschiedliche Aufgaben.
- Der Identifier bleibt stabil, auch wenn eine Benennung lokalisiert wird.
- Normative und informative Referenzen werden getrennt ausgewiesen.
- Eine Referenz behauptet weder Gleichrangigkeit noch Vorrang.
- Architekturbegriffe verweisen auf ihren ADR als materiellen Regelinhaber.
- Historische Begriffsverwendungen bleiben als Zeitstand sichtbar.
- Nicht auflösbare oder mehrdeutige Referenzen verhindern eine Kanonisierung.

## 4. Begründung der Strukturentscheidungen

1. `knowledge/project/` ist bereits der kanonische fachliche Produktbereich;
   ein neuer Wurzelbereich würde eine zweite Dokumentationsordnung schaffen.
2. Eine zunächst flache Struktur minimiert tote Indizes und vermeidet eine
   Taxonomie, bevor reale Glossareinträge existieren.
3. Vision, Glossar, semantische Grenzen und Human Journeys bleiben getrennte
   Dokumentklassen, weil sie unterschiedliche Aussageumfänge besitzen.
4. Versionierte Dateinamen machen einen veröffentlichten Zeitstand sichtbar,
   ohne die Stabilität der Begriffs-Identifier an Dateinamen zu koppeln.
5. Human Journeys bleiben bei fachlicher Produktdokumentation und dürfen keine
   Beobachtungs- oder Personendatenmodelle einführen.

## 5. Architekturprüfung

| Prüffeld | Ergebnis |
| --- | --- |
| ADR-0059 bis ADR-0066 | unverändert; ausschließlich als bestehende Referenzgrundlage analysiert |
| Governance | keine Regel, Taxonomie oder Decision erzeugt |
| Referenzintegrität | eindeutiger Einstiegspunkt, auflösbare Pfade und Trennung von normativ/informativ vorgesehen |
| Halbordnung | keine neue Ordnung; bestehende B2-Begriffe bleiben an ihre Regelinhaber gebunden |
| Air Gap | keine Transition, Runtime Readiness oder technische Empfangsstelle |
| Runtime-Trennung | vollständig erhalten |
| Observation | nicht eingeführt |
| Personenbezug | nicht eingeführt |
| Ruhende Kandidaten | weder referenziell aufgewertet noch aktiviert |

## 6. Alternativen

- **Neuer Wurzelbereich `product/`:** verworfen, weil `knowledge/project/`
  bereits zuständig ist und eine parallele Ordnung entstünde.
- **Glossar unter `governance/`:** verworfen, weil ein Glossar ausdrücklich
  keine Governance-Regel ist.
- **Glossar als ADR:** verworfen, weil Begriffspflege keine
  Architekturentscheidung ist.
- **Eine Datei pro Begriff ab Tag eins:** zurückgestellt, weil noch keine
  Begriffe kanonisiert sind und unnötige Referenzkomplexität entstünde.
- **Maschinenlesbares Schema:** nicht zulässig; es würde technische Semantik
  und Implementierung vorwegnehmen.

## 7. Risiken und offene Punkte

- Die Grenze zwischen einer Produktdefinition und einer materiellen
  Architekturdefinition muss bei jedem späteren Begriff einzeln geprüft
  werden.
- Eine Übersetzung kann Bedeutungsunterschiede sichtbar machen; sie darf den
  kanonischen Begriff nicht still ändern.
- Ein wachsendes Glossar kann später einen Index oder Unterordner benötigen;
  dafür ist ein eigener dokumentarischer Auftrag erforderlich.
- Die institutionelle Zuständigkeit für Freigabe und Pflege der
  Produktterminologie ist noch nicht entschieden. Dieser Vorschlag vergibt
  keine Rolle.
- Die konkrete Gründervision, Glossarbegriffe, Human Journeys und semantische
  Infrastruktur bleiben bewusst unformuliert.

