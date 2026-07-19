# ADR-0002: Wissenssystem des ZONVAA Builders

Status: beschlossen
Datum: 2026-07-17

## Entscheidung

Der ZONVAA Builder arbeitet wissensbasiert.

Dokumente, PDFs, Chatübergaben und Session-Dateien gelten zunächst als Quellen. Sie werden nicht automatisch als verbindliches Wissen behandelt.

Der Builder unterscheidet:

- Quellen
- dauerhaftes Projektwissen
- Architekturentscheidungen
- Protokolle
- Übergaben
- kurzfristige Sessions

## Zielstruktur

knowledge/
├── adr/
├── handovers/
├── protocols/
├── project/
├── sessions/
└── sources/

## Regeln

1. Externe Dokumente werden unter `knowledge/sources/` importiert.
2. Dauerhaft relevante Übergaben werden unter `knowledge/handovers/` gespeichert.
3. Verbindliche Architekturentscheidungen werden unter `knowledge/adr/` dokumentiert.
4. Kurzfristige Arbeitsverläufe bleiben unter `knowledge/sessions/`.
5. Der Builder lädt vor wissensabhängigen Aufgaben Constitution, ADRs, Protokolle, Übergaben und Projektwissen.
6. Quellen werden nicht ungeprüft als verbindliche Wahrheit übernommen.
7. Doppelte oder widersprüchliche Informationen müssen erkannt und gekennzeichnet werden.

## Nächster technischer Baustein

Ein `KnowledgeManager` lädt und strukturiert die vorhandenen Wissensbereiche und stellt sie dem Builder als gemeinsamen Kontext bereit.
