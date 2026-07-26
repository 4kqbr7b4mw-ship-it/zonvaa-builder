# ADR-0025 – Institution Layer

## Status

Beschlossen

## Kontext

WHY, Constitution und Values enthalten bereits langfristige Aussagen über
Menschen, Wissen, Verantwortung und Vertrauen. ADR-0008 priorisiert Identity
vor operativen Komponenten. ADR-0023 und ADR-0024 definieren den Guardian als
konstante sichtbare Beziehung und Workflows als interne Werkzeuge.

Die Runtime besitzt jedoch keinen eigenständigen, typisierten Vertrag, der
langfristige Systemgarantien vor jeder operativen Funktion verfügbar und
prüfbar macht. Einzelne Regeln ausschließlich über mehrere Dokumente verteilt
zu lassen, würde ihre technische Verbindlichkeit schwächen. Eine zweite
Constitution oder operative Policy Engine würde dagegen Redundanz und
konkurrierende Zuständigkeiten erzeugen.

## Entscheidung

ZONVAA führt den Institution Layer als eigenständige Architekturebene ein:

Guardian → Institution → Runtime

Die Institution definiert ausschließlich langfristige Systemgarantien:

- Governance
- Nutzerhoheit
- Guardian Continuity
- Transparenz
- Verantwortung
- Schutz
- Würde
- Vertrauensmodell

Ihre Kernregel lautet:

> Keine Funktion darf Vertrauen verbrauchen.

Der kanonische Vertrag liegt versioniert unter
`institution/institution.md`. Ein kleiner, unveränderlicher
`InstitutionContext` enthält Quelle, Version, SHA-256-Hash und exakt die acht
stabilen Garantietypen. Der Loader prüft UTF-8, Version und Vollständigkeit,
interpretiert aber keine operative Fachregel.

## Verhältnis zu bestehenden Ebenen

- WHY und Identity bleiben Richtung und höchste fachliche Instanz.
- Die Institution formuliert daraus dauerhafte, funktionsübergreifende
  Garantien.
- Die Constitution bleibt verbindlicher Arbeits- und Systemregelvertrag.
- ADRs dokumentieren konkrete Architekturentscheidungen.
- Runtime bleibt gemäß ADR-0004 Single Source of Truth und lädt genau einen
  `InstitutionContext`.
- Guardian und spätere Interaktionskomponenten beziehen Runtime-Fähigkeiten
  nur innerhalb der Institution-Garantien.

ADR-0025 ergänzt ADR-0004 und ADR-0008. Die Identity wird weiterhin zuerst
geladen. Danach wird die Institution geladen, bevor Constitution, Knowledge,
Project State und operative Engines verfügbar werden.

## Preflight

Der Mission Context wird auf Schema-Version 1.1 erweitert. Er weist Status,
Quelle, Version, Content-Hash und Garantietypen der geladenen Institution nach.
Fehlende, unvollständige oder während des Laufs veränderte Institution bricht
den Preflight ab. Freigegebene Goal-Workflows können dadurch nicht ohne den
Institution-Vertrag starten.

Der abgeleitete kleine `WorkflowContext` erhält weiterhin keine
Institution-Inhalte. Operative Komponenten sollen keine eigenen
Interpretationen des Garantievertrags entwickeln.

## Vertrauensmodell

„Vertrauen verbrauchen“ bezeichnet keine berechenbare Kennzahl. Die Regel
verbietet Architektur, deren Nutzen von Täuschung, verstecktem Zwang,
Entmündigung, Dark Patterns, unklarer Zweckänderung, nicht erklärbaren
Entscheidungen oder dem Verlust von Nutzerkontrolle abhängt.

Vertrauen darf nicht gegen Geschwindigkeit, Wachstum, Vollständigkeit,
Automatisierung oder Umsatz eingetauscht werden. Es wird durch Wahrhaftigkeit,
Kompetenz, Kontinuität, Schutz, Transparenz und Nutzerhoheit ermöglicht, aber
nicht als Besitz des Systems behauptet.

## Grenzen

Der Institution Layer:

- trifft keine fachlichen Entscheidungen,
- klassifiziert keine Menschen oder Anliegen,
- startet und erzeugt keine Workflows,
- implementiert keine UI oder Monetarisierung,
- ist keine allgemeine Rule Engine,
- dupliziert keine Knowledge- oder Memory-Persistenz.

## Konsequenzen

- Jede Runtime besitzt einen nachweisbaren Institution-Vertrag.
- Langfristige Garantien sind typisiert, versioniert und unveränderlich.
- Änderungen am Vertrag benötigen eine bewusste Architekturentscheidung.
- Funktionen, die Garantien nur durch Vertrauensverlust erfüllen könnten,
  sind architektonisch unzulässig.
- Spätere technische Durchsetzungsmechanismen benötigen eigene, begrenzte
  Entscheidungen; sie dürfen nicht stillschweigend in den Loader wandern.
