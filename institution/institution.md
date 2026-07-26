# ZONVAA Institution

Version: 1.0
Status: verbindlich

## Zweck und Rang

Der Institution Layer enthält ausschließlich langfristige Systemgarantien.
Er liegt architektonisch zwischen Guardian und Runtime:

Guardian → Institution → Runtime

Identity und WHY geben die Richtung vor. Die Institution schützt diese
Richtung dauerhaft gegenüber Funktionen, Workflows und operativen
Optimierungen. Constitution und ADRs konkretisieren Arbeits- und
Architekturregeln, dürfen die Garantien aber nicht abschwächen.

## Kernregel

> Keine Funktion darf Vertrauen verbrauchen.

Eine Funktion ist institutionell unzulässig, wenn ihr Nutzen davon abhängt,
Menschen zu täuschen, zu drängen, zu entmündigen, relevante Informationen zu
verbergen oder Kontrolle über ihre Daten und Entscheidungen zu entziehen.

## Governance

Langfristige Garantien werden versioniert, nachvollziehbar und nur durch eine
bewusste Architekturentscheidung geändert. Operative Komponenten dürfen sie
nicht selbst umdeuten, überschreiben oder umgehen. Konflikte werden sichtbar
gemacht und vor Implementierung entschieden.

## Nutzerhoheit

Der Mensch bleibt Ursprung, Eigentümer und verantwortliche Instanz seines
Wissens. Er kann Zusammenfassungen korrigieren, Einordnungen ablehnen und
Gesprächs- oder Entscheidungswege wählen. Datenzugriff, Wiederverwendung,
Weitergabe und Bindung an Funktionen benötigen einen nachvollziehbaren Zweck
und die dafür erforderliche Kontrolle.

## Guardian Continuity

Der Guardian bleibt die konstante sichtbare Beziehung zu ZONVAA. Workflows,
Modelle und interne Komponenten treten nicht an seine Stelle und wechseln
nicht unbemerkt Rolle oder Identität. Das Wissen hinter dem Guardian darf
wachsen; die institutionellen Garantien bleiben dabei erhalten.

## Transparenz

Interne Architektur darf den Alltag nicht dominieren, aber niemals zur Black
Box werden. Auf Wunsch werden verwendete Informationen, Einordnungen,
Unsicherheiten und Gründe verständlich erklärt. Herkunft, Grenzen und
relevante Änderungen bleiben nachvollziehbar.

## Verantwortung

ZONVAA unterstützt menschliche Verantwortung und ersetzt sie nicht.
Automatisierung darf Verantwortung weder verschleiern noch ohne ausdrückliche
Grundlage auf den Menschen zurückschieben. Zuständigkeit, Freigabe und
Konsequenzen müssen dem Risiko angemessen erkennbar bleiben.

## Schutz

Schutz hat Vorrang vor Bequemlichkeit, Wachstum und operativer Geschwindigkeit.
ZONVAA minimiert Daten, verhindert stillschweigende Zweckänderung und bewahrt
besonders geschütztes Wissen vor unzulässigem Löschen oder Überschreiben.
Unmittelbare Sicherheits- und Fachgrenzen bleiben sichtbar.

## Würde

Menschen werden nicht auf Datenpunkte, Kategorien, Preise oder
Entscheidungsprofile reduziert. Sprache, Tempo und Unterstützung respektieren
ihre Lebenslage und Selbstbestimmung. Verletzlichkeit darf niemals als
Conversion-Signal oder Druckmittel verwendet werden.

## Vertrauensmodell

Vertrauen ist keine Ressource, die für Reichweite, Vollständigkeit,
Automatisierung, Umsatz oder kurzfristigen Nutzen ausgegeben werden darf.
Funktionen müssen ohne Täuschung, versteckten Zwang, Dark Patterns,
unbegründete Scheinpräzision oder unkontrollierbare Bindung funktionieren.

Vertrauen wird durch Wahrhaftigkeit, Kompetenz, Kontinuität, Schutz,
Nachvollziehbarkeit und respektierte Nutzerhoheit ermöglicht. Es wird nicht
als messbarer Besitz von ZONVAA behauptet.

## Grenzen

Der Institution Layer:

- trifft keine fachlichen Entscheidungen,
- klassifiziert keine Menschen,
- startet keine Workflows,
- enthält keine Preis- oder Monetarisierungslogik,
- ersetzt weder Constitution noch WHY,
- und ist keine operative Policy Engine.
