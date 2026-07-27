# ENTSCHEIDUNGSVORLAGE

## Empfehlung
ADOPT

## Kernaussage
Proposal artifact-authorization-gemini-ux was compared with the loaded architecture. 0 aligned, 81 additive, 0 conflicting, and 1 duplicate elements were identified. The recommendation is advisory. Only the Chief Architect may decide.

## Übernehmen
- ZONVAA UX- & Conversation-Architektur: Artefakte & Berechtigungen
- Diese Architektur beschreibt die psychologische und visuelle Interaktionsschicht für den Umgang mit sensiblen Dokumenten, Freigaben und Familienkonflikten in ZONVAA. Sie baut auf der strikten Trennung zwischen dem Sanctuary (Gesprächsraum / Conversation Engine) und der Workbench (Institution Board / Rechte-Artefakte) auf.
- 1. Das Konzept der „Menschlichen Transaktion“
- Rechtliche Freigaben und Datenzugriffe basieren in herkömmlichen Systemen auf technischer Sprache. ZONVAA übersetzt dieses Paradigma in menschliche Schutzräume.
- Prinzipien der Berechtigungs-Psychologie
- Kein Berechtigungs-Jargon: Weder im Chat noch auf dem Board existieren Begriffe wie Admin, User, Access, Grant, Revoke, Sync, Read/Write, Permission.
- Beziehungs-Metaphern statt Rollen-Matrizen:
- Zugriff erteilen → „In den Raum holen“
- Eingeschränkte Leserechte → „Nur zum Durchlesen hinlegen“
- Vollmacht erteilen → „Schlüssel übergeben“
- Berechtigung entziehen → „Wieder zu sich nehmen“
- Getrennte Wahrnehmungsebenen: Das Verfassen/Besprechen eines Dokuments ist eine Gedankenebene (Sanctuary). Das Freigeben ist eine Handlungsebene (Workbench). Beide Räume dürfen visuell und kognitiv niemals verschmelzen.
- 2. Artefakt-Zustände (Sichtbar vs. Unsichtbar)
- Ein Artefakt durchläuft einen Lebenszyklus, der dem Nutzer maximale emotionale und rechtliche Sicherheit garantiert:
- GEDANKE / CHAT → ENTWURF → UNSICHTBARES ARTEFAKT (nur Eigentümer) → SICHTBARES ARTEFAKT (persönliches Board) → GEMEINSAMES ARTEFAKT (Shared Safe / Familie)
- Die vier Artefakt-Zustände
- Entwurf (Latenz)
- Nur im Fließtext des Chats verankert.
- Lokale Engine-Instanz.
- Der Nutzer spricht über ein Thema. Die KI strukturiert im Hintergrund, erzeugt aber noch kein sichtbares Objekt.
- Persönlich (Lokal)
- Nur für den Ersteller auf seinem persönlichen Institution Board sichtbar.
- Verschlüsselter Tresor des Nutzers.
- Für niemanden sonst einsehbar.
- Bereitgestellt (Ruhend)
- Auf dem Board als „Bereit zur Freigabe“ markiert.
- Schnittstelle zum Shared Safe.
- Ein Schlüssel wurde vorbereitet, aber noch nicht übergeben.
- Geteilt (Aktiv)
- Für ausgewählte Personen im gemeinsamen Familien-Board sichtbar.
- Kryptografischer Consensus-Graph (Zero-Knowledge).
- Änderungen erfordern Transparenz.
- 3. Schutz vor versehentlichen Freigaben und sensible Dokumente
- Je sensibler ein Dokument, desto höher muss die kognitive Reibung vor der Freigabe sein. ZONVAA nutzt einen „Autorisierungs-Graben“.
- Drei-Ebenen-Schutzbarriere
- Gesprächs-Reflexion: „Möchtest du das wirklich teilen?“
- Physische Haptik: 3-Sekunden-Press-and-Hold auf der Workbench.
- Einmal-Schlüssel: Biometrie, SMS oder physisches Token.
- Kein Ein-Klick-Share.
- Sensible Artefakte erfordern eine bewusste Halte-Geste.
- Vor der Übergabe zeigt das Board exakt, was die Zielperson sehen wird und was nicht.
- 4. Gemeinsames Arbeiten und Konflikte in Familien
- Der Guardian wird niemals Schiedsrichter oder Partei.
- Zero-Knowledge-Familienraum
- Es gibt keine globale Wahrheit im Chat.
- Vertrauliche Informationen einer personengebundenen Guardian-Instanz sind für andere Instanzen unsichtbar und nicht verarbeitbar.
- Widersprüchliche Wünsche auf dem Shared Board
- Kein Überschreiben von Inhalten.
- Gegensätzliche Perspektiven stehen sichtbar nebeneinander.
- Die Engine validiert keine Seite.
- Das Artefakt bleibt eingefroren, bis eine gemeinsam tragfähige Form gefunden wurde.
- 5. Warnungen, Rückfragen und Schweigen
- Schweigen
- Bei hochemotionalen Freigabe- oder Widerrufsimpulsen:
- keine sofortige Workbench-Aktion,
- keine alarmistische Warnmeldung,
- keine technische Eskalation,
- stattdessen Entlastung und Zeitgewinn.
- Sanfte Rückfrage
- Nur bei rechtlich oder organisatorisch schwer umkehrbaren Handlungen:
- Konsequenzen konkret und ruhig benennen,
- eine reversible Alternative anbieten,
- keine technische oder drohende Sprache.
- 6. Widerruf und Kontrollrückgabe
- Souveräner Widerruf
- Keine Rechtfertigungspflicht.
- Das Artefakt zieht sich aus dem gemeinsamen Raum auf das persönliche Board zurück.
- Die Gegenseite sieht nur „Nicht verfügbar“ oder „In Überarbeitung“.
- Keine Offenlegung des Grundes.
- Emergency Lock
- Unauffällige Geste auf dem Institution Board.
- Alle externen Freigaben werden sofort eingefroren.
- Artefakte werden lokal isoliert.
- Externe Parteien werden nicht informiert.
- Der Guardian unterstützt neutral bei der Wiederherstellung persönlicher Sicherheit.
- 7. Guardian-Artefakt-Manifest
- Kein Chat-Text verändert automatisch ein Recht auf dem Board.
- Keine Freigabe geschieht ohne bewusste, gesonderte Handlung.
- Berechtigungen werden nicht in technischem Jargon erklärt.
- Familienkonflikte werden nicht durch die KI entschieden.
- Jeder Widerruf geschieht sofort, still und ohne Rechtfertigungszwang.

## Ändern
- None

## Ablehnen
- None

## Konflikte
- None

## Betroffene Architektur
- CONVERSATION
- INTERACTION
- INSTITUTION
- CROSS_LAYER
- constitution/constitution.md
- governance/charter.md
- institution/institution.md
- interaction/interaction.md
- knowledge/adr/ADR-0002-knowledge-system.md
- knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md

## Entscheidung erforderlich
- Confirm the non-binding ADOPT recommendation for proposal artifact-authorization-gemini-ux.
