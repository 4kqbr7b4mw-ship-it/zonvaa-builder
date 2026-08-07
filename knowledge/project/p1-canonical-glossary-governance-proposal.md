# P1 – Vorschlag zur Governance eines kanonischen Glossars

Status: **NICHT NORMATIVER VORSCHLAG – KEINE GOVERNANCE-REGEL – KEIN GLOSSAR – NICHT IMPLEMENTIERT**

## 1. Aussageumfang

Dieses Dokument beschreibt einen möglichen dokumentarischen Pflegeprozess.
Es erteilt keine Rolle, Entscheidungsmacht oder Freigabe und kanonisiert
keinen Begriff. Das Glossar wäre kein ADR, keine Governance-Regel, keine
Architektur, keine Ontologie, keine Runtime-Komponente und keine technische
Implementierung.

## 2. Zweck eines späteren Glossars

Ein späteres Glossar soll unterschiedliche Verwendungen desselben Wortes
sichtbar trennen, stabile Referenzen für Produktdokumente bereitstellen und
den materiellen Regelinhaber eines Begriffs auffindbar machen. Es soll keine
materielle Regel verdoppeln, auslegen, priorisieren oder erweitern.

## 3. Vorgeschlagener dokumentarischer Lebenszyklus

Die Bezeichnungen sind Arbeitsphasen, keine neue Governance-Taxonomie:

1. **Kandidat erfassen:** Fundstelle, Verwendungsbereich und Mehrdeutigkeit
   dokumentieren; noch keine Definition.
2. **Quellen prüfen:** alle bekannten Regelinhaber, historischen Verwendungen,
   Übersetzungen und Abgrenzungen erfassen.
3. **Entwurf dokumentieren:** Definition und Grenzen als ausdrücklich nicht
   kanonischen Entwurf vorlegen.
4. **Kanonisierung gesondert beschließen:** nur durch einen später bestimmten,
   ausdrücklich dokumentierten menschlichen Prozess.
5. **Veröffentlichen:** stabilen Identifier, Version, Status, Quellen und
   Sprachfassungen gemeinsam ausweisen.
6. **Pflegen:** Änderungen nach Bedeutungswirkung klassifizieren, referenzierte
   Dokumente prüfen und Historie fortschreiben.
7. **Deprecated kennzeichnen:** Begriff nicht löschen oder Identifier neu
   verwenden; Nachfolger und Grund referenzieren.

Keine Phase löst die nächste automatisch aus. Insbesondere erzeugt ein
Kandidat weder Kanonisierung noch technische Bindung.

## 4. Kanonisierung

Vor einer späteren Kanonisierung wären mindestens dokumentarisch zu prüfen:

- eindeutiger, stabiler Identifier,
- genau eine kanonische Definition je veröffentlichter Version,
- bekannte positive und negative Abgrenzungen,
- auflösbare normative und informative Quellen,
- keine Kollision mit bestehenden ADR- oder Governance-Begriffen,
- konsistente Lokalisierungen oder sichtbar offene Übersetzungen,
- keine neue materielle Regel durch die Definition,
- expliziter menschlicher Freigabenachweis.

Scheitert eine Prüfung, bleibt der Eintrag Kandidat. Freier Text, Modelloutput
oder Häufigkeit der Verwendung kanonisieren nichts.

## 5. Erweiterungen und Änderungen

Eine Ergänzung darf einen bestehenden Begriff nicht still verbreitern.
Redaktionelle Änderungen erhalten Identifier und Version nur, wenn die
Bedeutung unverändert bleibt. Eine Bedeutungsänderung benötigt mindestens
eine neue Eintragsversion; bei begrifflicher Identitätsänderung einen neuen
Identifier und eine dokumentierte Beziehung zum Vorgänger.

Ein Architektur- oder Governance-Begriff darf im Glossar nur die vorhandene
materielle Quelle zusammenfassen. Konflikte werden sichtbar dokumentiert und
nicht im Glossar entschieden.

## 6. Versionierung

Vorgeschlagen ist eine zweistufige dokumentarische Versionierung:

- **Glossar-Release:** eingefrorener Veröffentlichungsstand des Gesamtindex.
- **Eintragsversion:** Bedeutungsstand eines einzelnen stabilen Identifiers.

Jeder Release dokumentiert Datum, enthaltene Eintragsversionen und
Änderungsübersicht. „Latest“ darf nur Navigationshilfe sein; präzise
Evidenzreferenzen nennen einen veröffentlichten Stand. Identifier werden nie
recycelt.

## 7. Lokalisierungen

- Jede Benennung und Definition trägt einen expliziten BCP-47-Sprachtag.
- Eine später bestimmte Basissprache liefert keinen semantischen Vorrang kraft
  dieses Vorschlags.
- Pro Sprache gibt es höchstens eine bevorzugte Benennung je Eintragsversion;
  Synonyme und Suchformen bleiben getrennt.
- Übersetzungen referenzieren denselben Identifier, aber ihren eigenen
  Prüfstatus und ihre Quelle.
- Fehlende Übersetzung bleibt sichtbar; maschinelle Übersetzung wird nicht
  still kanonisch.
- Bedeutungsinkongruenz führt zu einem offenen Prüfpunkt, nicht zu einer
  automatischen Angleichung.

## 8. Referenzierung

Ein Glossareintrag trennt:

- **materielle Regelinhaber:** Quellen, die den Begriff tatsächlich regeln,
- **unterstützende Referenzen:** Quellen, die Kontext liefern,
- **historische Verwendungen:** frühere Zeitstände ohne aktuelle Regelwirkung,
- **nicht zuständige Quellen:** zur Vermeidung falscher Zuständigkeit.

Referenzen müssen auflösbar sein. Ein Glossareintrag darf keinen Vorrang
zwischen mehreren Regelinhabern erfinden.

## 9. Deprecation

Deprecation bedeutet „nicht für neue Verwendung empfohlen“, nicht Löschung,
Unwahrheit oder rückwirkende Ungültigkeit. Erforderlich sind Grund,
Wirksamkeitsdatum, letzter kanonischer Stand, optionaler Nachfolger und
bekannte betroffene Referenzen. Historische Dokumente werden nicht
rückwirkend umgeschrieben.

## 10. Semantische Stabilität

Stabilität entsteht durch unveränderliche Identifier, explizite Versionen,
sichtbare Bedeutungsänderungen, eindeutige Quellen und getrennte
Lokalisierungen. Sie entsteht nicht durch technische Sperren, automatische
Validierung oder ein Universalmodell. Das Glossar bleibt dokumentarisch.

## 11. Vorgeschlagene Verantwortungsgrenzen

P1 bestimmt noch keine institutionellen Rollen. Für einen späteren Prozess
müssen mindestens Autorenschaft, fachliche Prüfung, Sprachprüfung,
Kanonisierungsentscheidung und Verwahrung getrennt benannt werden. Eine Person
kann mehrere Aufgaben übernehmen, aber die Aufgaben und Nachweise müssen
sichtbar bleiben. Architekturbegriffe benötigen zusätzlich eine Prüfung gegen
ihren kanonischen ADR; dies ändert den ADR nicht.

## 12. Nicht eingeführt

Kein Registry-Service, Schema, Parser, Validator, Generator, API, Identifier-
Dienst, Übersetzungsdienst, Ontologiemodell, Suchindex oder Runtime-Vertrag
wird vorgeschlagen oder implementiert. Ebenso entstehen keine Observation,
Personenbindung, Nutzerprofile, ruhenden Kandidatenaktivierung oder neue
Governance-Macht.

