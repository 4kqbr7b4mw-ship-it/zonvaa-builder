# ADR-0009 – Memory Architecture

## Status

Beschlossen

## Kontext

ZONVAA ist eine vertrauenswürdige Infrastruktur für menschliches Wissen. Dabei gilt:

> Kein wertvolles Wissen sollte verloren gehen, nur weil niemand danach gefragt hat.

Das bestehende Wissenssystem unterscheidet Quellen und Wissensbereiche, besitzt aber noch keine verbindliche Klassifikation für Lebensdauer, Schutz und Verlässlichkeit von Erinnerungen. Die zentrale Runtime bleibt gemäß ADR-0004 die Single Source of Truth. Es wird keine zweite Wissensstruktur und keine zusätzliche Persistenz eingeführt.

## Entscheidung

Jeder künftig als Memory geführte Inhalt wird durch Metadaten klassifiziert. Das typisierte Modell umfasst mindestens:

- `memory_type`
- `source`
- `created_at`
- `confidence`
- `retention_policy`
- `protected`
- `verified`

`source` dokumentiert die Herkunft, `created_at` wird mit Zeitzone geführt, `confidence` unterscheidet unsichere, wahrscheinliche und bestätigte Inhalte. Nur Inhalte mit `confidence = confirmed` dürfen `verified = true` tragen. Die Klassifikation wird vom bestehenden `KnowledgeManager` validiert und über die bestehende Runtime genutzt; sie begründet keinen eigenen Speicher.

## Gedächtnisklassen

- `working_memory`: kurzfristiger Arbeitskontext; darf gemäß dokumentierter Retention Policy kontrolliert verfallen.
- `project_memory`: dauerhaftes Wissen eines konkreten Projekts.
- `personal_memory`: bestätigte Rollen, Präferenzen und langfristig relevante personenbezogene Zusammenhänge.
- `knowledge_memory`: Quellen, Dokumente, Fakten, Beziehungen, Vertrauensgrad und Versionen.
- `heritage_memory`: besonders schützenswertes Wissen; ist immer geschützt und darf niemals automatisiert gelöscht oder überschrieben werden.
- `archive_memory`: historisches, nicht mehr aktives Wissen, das weiterhin nachvollziehbar bleibt.

Unbekannte Klassen werden abgelehnt.

## Schutz- und Vertrauensregeln

1. `heritage_memory` erzwingt `protected = true`.
2. Für `heritage_memory` sind automatische Löschung und automatisches Überschreiben verboten. Änderungen erfordern eine bewusste, nachvollziehbare menschliche Entscheidung.
3. Herkunft, Klassifikation, Erstellungszeitpunkt und Retention Policy müssen nachvollziehbar bleiben.
4. Unsichere oder nur wahrscheinliche Inhalte dürfen nicht als verifiziert behandelt oder als bestätigte Fakten gespeichert werden.
5. Archivierung ist keine Löschung: Historie und Herkunft bleiben erhalten.
6. Die vorhandene Runtime bleibt die einzige Quelle des aktiven Zustands. Persistenz und Laden verbleiben in der bestehenden Knowledge-Struktur.

## Konsequenzen

- Memory besitzt eine kleine, überprüfbare und Python-3.9-kompatible Grundlage ohne neue Abhängigkeiten.
- Bestehende Wissensbereiche und Runtime-Abläufe bleiben unverändert.
- Spätere Persistenzfunktionen müssen Schutz, Herkunft und Verifikation vor jedem Schreiben, Überschreiben, Archivieren oder Löschen prüfen.
- Konkrete Retention-Zeiträume und Freigabeprozesse werden erst bei Bedarf separat entschieden.
