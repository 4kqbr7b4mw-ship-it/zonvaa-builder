# CODEX ARCHITECTURE WORKFLOW ORDER

Workflow: `workflow-81d7ba505f25f885`

Every section below is based on a separate confirmed Chief Architect decision. The workflow made no decision.

---

# CODEX ARCHITECTURE IMPLEMENTATION ORDER

## Authority
Chief Architect decision `decision-artifact-authorization-gemini-ux` by `Chief Architect`: `ADOPT_WITH_CHANGES`.
Architecture Integrator advised; the Chief Architect decided; Codex implements only this confirmed scope.

## Proposal
- ID: `artifact-authorization-gemini-ux`
- Title: UX- und Conversation-Architektur für Artefakte und Berechtigungen
- Source: ZONVAA_Gemini_Artefakte_Berechtigungen.md (GEMINI)
- Requested scope: Typisierter Artefakt- und Autorisierungszustandsvertrag
- Affected layers: CONVERSATION, INTERACTION, INSTITUTION, CROSS_LAYER

## Complete submitted architecture content
# ZONVAA UX- & Conversation-Architektur: Artefakte & Berechtigungen

Diese Architektur beschreibt die psychologische und visuelle Interaktionsschicht für den Umgang mit sensiblen Dokumenten, Freigaben und Familienkonflikten in ZONVAA. Sie baut auf der strikten Trennung zwischen dem Sanctuary (Gesprächsraum / Conversation Engine) und der Workbench (Institution Board / Rechte-Artefakte) auf.

## 1. Das Konzept der „Menschlichen Transaktion“

Rechtliche Freigaben und Datenzugriffe basieren in herkömmlichen Systemen auf technischer Sprache. ZONVAA übersetzt dieses Paradigma in menschliche Schutzräume.

### Prinzipien der Berechtigungs-Psychologie

- Kein Berechtigungs-Jargon: Weder im Chat noch auf dem Board existieren Begriffe wie Admin, User, Access, Grant, Revoke, Sync, Read/Write, Permission.
- Beziehungs-Metaphern statt Rollen-Matrizen:
  - Zugriff erteilen → „In den Raum holen“
  - Eingeschränkte Leserechte → „Nur zum Durchlesen hinlegen“
  - Vollmacht erteilen → „Schlüssel übergeben“
  - Berechtigung entziehen → „Wieder zu sich nehmen“
- Getrennte Wahrnehmungsebenen: Das Verfassen/Besprechen eines Dokuments ist eine Gedankenebene (Sanctuary). Das Freigeben ist eine Handlungsebene (Workbench). Beide Räume dürfen visuell und kognitiv niemals verschmelzen.

## 2. Artefakt-Zustände (Sichtbar vs. Unsichtbar)

Ein Artefakt durchläuft einen Lebenszyklus, der dem Nutzer maximale emotionale und rechtliche Sicherheit garantiert:

GEDANKE / CHAT → ENTWURF → UNSICHTBARES ARTEFAKT (nur Eigentümer) → SICHTBARES ARTEFAKT (persönliches Board) → GEMEINSAMES ARTEFAKT (Shared Safe / Familie)

### Die vier Artefakt-Zustände

1. Entwurf (Latenz)
   - Nur im Fließtext des Chats verankert.
   - Lokale Engine-Instanz.
   - Der Nutzer spricht über ein Thema. Die KI strukturiert im Hintergrund, erzeugt aber noch kein sichtbares Objekt.

2. Persönlich (Lokal)
   - Nur für den Ersteller auf seinem persönlichen Institution Board sichtbar.
   - Verschlüsselter Tresor des Nutzers.
   - Für niemanden sonst einsehbar.

3. Bereitgestellt (Ruhend)
   - Auf dem Board als „Bereit zur Freigabe“ markiert.
   - Schnittstelle zum Shared Safe.
   - Ein Schlüssel wurde vorbereitet, aber noch nicht übergeben.

4. Geteilt (Aktiv)
   - Für ausgewählte Personen im gemeinsamen Familien-Board sichtbar.
   - Kryptografischer Consensus-Graph (Zero-Knowledge).
   - Änderungen erfordern Transparenz.

## 3. Schutz vor versehentlichen Freigaben und sensible Dokumente

Je sensibler ein Dokument, desto höher muss die kognitive Reibung vor der Freigabe sein. ZONVAA nutzt einen „Autorisierungs-Graben“.

### Drei-Ebenen-Schutzbarriere

1. Gesprächs-Reflexion: „Möchtest du das wirklich teilen?“
2. Physische Haptik: 3-Sekunden-Press-and-Hold auf der Workbench.
3. Einmal-Schlüssel: Biometrie, SMS oder physisches Token.

Regeln:

- Kein Ein-Klick-Share.
- Sensible Artefakte erfordern eine bewusste Halte-Geste.
- Vor der Übergabe zeigt das Board exakt, was die Zielperson sehen wird und was nicht.

## 4. Gemeinsames Arbeiten und Konflikte in Familien

Der Guardian wird niemals Schiedsrichter oder Partei.

### Zero-Knowledge-Familienraum

- Es gibt keine globale Wahrheit im Chat.
- Vertrauliche Informationen einer personengebundenen Guardian-Instanz sind für andere Instanzen unsichtbar und nicht verarbeitbar.

### Widersprüchliche Wünsche auf dem Shared Board

- Kein Überschreiben von Inhalten.
- Gegensätzliche Perspektiven stehen sichtbar nebeneinander.
- Die Engine validiert keine Seite.
- Das Artefakt bleibt eingefroren, bis eine gemeinsam tragfähige Form gefunden wurde.

## 5. Warnungen, Rückfragen und Schweigen

### Schweigen

Bei hochemotionalen Freigabe- oder Widerrufsimpulsen:

- keine sofortige Workbench-Aktion,
- keine alarmistische Warnmeldung,
- keine technische Eskalation,
- stattdessen Entlastung und Zeitgewinn.

### Sanfte Rückfrage

Nur bei rechtlich oder organisatorisch schwer umkehrbaren Handlungen:

- Konsequenzen konkret und ruhig benennen,
- eine reversible Alternative anbieten,
- keine technische oder drohende Sprache.

## 6. Widerruf und Kontrollrückgabe

### Souveräner Widerruf

- Keine Rechtfertigungspflicht.
- Das Artefakt zieht sich aus dem gemeinsamen Raum auf das persönliche Board zurück.
- Die Gegenseite sieht nur „Nicht verfügbar“ oder „In Überarbeitung“.
- Keine Offenlegung des Grundes.

### Emergency Lock

- Unauffällige Geste auf dem Institution Board.
- Alle externen Freigaben werden sofort eingefroren.
- Artefakte werden lokal isoliert.
- Externe Parteien werden nicht informiert.
- Der Guardian unterstützt neutral bei der Wiederherstellung persönlicher Sicherheit.

## 7. Guardian-Artefakt-Manifest

1. Kein Chat-Text verändert automatisch ein Recht auf dem Board.
2. Keine Freigabe geschieht ohne bewusste, gesonderte Handlung.
3. Berechtigungen werden nicht in technischem Jargon erklärt.
4. Familienkonflikte werden nicht durch die KI entschieden.
5. Jeder Widerruf geschieht sofort, still und ohne Rechtfertigungszwang.

## Binding accepted content
- Typisierte, versionierte Artefaktzustände
- Explizite, granulare, zweckgebundene, nachvollziehbare und widerrufbare Autorisierung
- Strikte Trennung zwischen Gespräch und autorisierter Handlung
- Keine impliziten Familien-, Rollen- oder Zugriffsrechte
- Isolierte personengebundene Kontexte
- Sichtbare Konflikte ohne automatische Parteinahme
- Keine stille Überschreibung paralleler Zustandsänderungen
- Auditierbare Zustandsübergänge
- Exportierbare und langfristig interpretierbare Historien

## Binding modifications
- Genau ein verantwortlicher Hoheitsträger pro Artefakt; mehrere autorisierte Beteiligte bleiben möglich.
- Irreversibilität wird je Übergangstyp definiert.
- C2 regelt Prinzipien, Rollen, Vetos und Prüfpflichten.
- C3 regelt konkrete Fristen, Gesten, Quoren und technische Verfahren.
- Historien werden nach Datenklasse unterschieden: unveränderbar, aufbewahrungspflichtig, löschbar oder anonymisierbar.
- Widerrufe wirken sofort, soweit keine dokumentierte rechtliche oder technische Bindung entgegensteht.
- Notfall- und automatische Ereignisübergänge werden separat behandelt.
- Unbestätigte Rechtswirkungs- und Kryptografiebegriffe werden entfernt oder neutral formuliert.
- Nicht vorhandene Referenzen werden ersetzt oder entfernt.

## Explicitly rejected content
- Zwingende Drei-Sekunden-Geste
- Verpflichtende Biometrie-, SMS- oder Token-Vorgaben
- Unbestätigte Zero-Knowledge-, Signatur- oder Verschlüsselungsbehauptungen
- Pauschale rechtliche Wirksamkeits- oder Beweisgarantien
- Automatische externe Notfall- oder Amtsmaßnahmen
- Absolute Unlöschbarkeit sämtlicher Historien

## Deferred content
- None

## Rationale
Der gemeinsame Kern stärkt Nutzerhoheit, Nachvollziehbarkeit und die Trennung zwischen Gespräch und Handlung. Technische, rechtliche und operative Details benötigen gesonderte Prüfung.

## Existing binding sources
- C1-CONSTITUTION
- MDR-0001-guardian-conversation-and-continuity
- C2-GOVERNANCE-CHARTER
- SPEC-INSTITUTION
- SPEC-INTERACTION
- ADR-0002-knowledge-system
- ADR-0003-runtime-journal
- ADR-0004-runtime-architecture
- ADR-0005-decision-engine
- ADR-0006-execution-engine
- ADR-0007-knowledge-priority
- ADR-0008-identity-first
- ADR-0009-memory-architecture
- ADR-0010-goal-engine
- ADR-0011-goal-evaluation-contract
- ADR-0012-why-assessment-model
- ADR-0013-decision-why-integration
- ADR-0014-goal-aware-orchestration
- ADR-0015-goal-application-service
- ADR-0016-decision-journal
- ADR-0017-knowledge-proposal-execution
- ADR-0018-life-decisions
- ADR-0019-life-decisions-domain-model
- ADR-0020-codex-context-and-handover
- ADR-0021-mission-context-workflow-integration
- ADR-0022-power-of-attorney-workflow
- ADR-0025-institution-layer
- ADR-0027-governance-architecture
- ADR-0028-architecture-integrator-agent
- ADR-0029-architecture-workflow-orchestrator
- C3-OPERATIVE-RULES

## Existing affected documents
- constitution/constitution.md
- governance/charter.md
- institution/institution.md
- interaction/interaction.md
- knowledge/adr/ADR-0002-knowledge-system.md
- knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md

## Protection goals and constraints
- Gespräch und institutionelle Handlung bleiben getrennt.
- Gesprächsinhalte erzeugen keine Autorisierung.
- Konkrete Gesten, Zeitwerte, Biometrie und Kryptografie sind keine bereits bestätigten Architekturvorgaben.

## Non-goals
- Do not implement rejected or deferred elements.
- Do not call external AI services or use network access.
- Do not create UI unless explicitly accepted above.
- Do not weaken C1, MDR-0001, C2, Institution, or Interaction guarantees.
- Do not treat Integrator recommendations as authority.

## Required verification
- Add focused tests for every accepted invariant and modified boundary.
- Preserve and run the complete existing test suite.
- Run `python3 -m builder.main doctor`.
- Run `git diff --check` and inspect `git status --short`.
- Review the full architecture diff for conflicts and unintended changes.
- Create JSON and Markdown handover files.


---

# CODEX ARCHITECTURE IMPLEMENTATION ORDER

## Authority
Chief Architect decision `decision-artifact-authorization-kimi-contract` by `Chief Architect`: `ADOPT_WITH_CHANGES`.
Architecture Integrator advised; the Chief Architect decided; Codex implements only this confirmed scope.

## Proposal
- ID: `artifact-authorization-kimi-contract`
- Title: Artefakt- und Autorisierungszustandsvertrag
- Source: ZONVAA_Artefakt_Autorisierungsvertrag_ADR.md (KIMI)
- Requested scope: Typisierter Artefakt- und Autorisierungszustandsvertrag
- Affected layers: INTERACTION, INSTITUTION, GOVERNANCE, RUNTIME, CROSS_LAYER

## Complete submitted architecture content
# ZONVAA Artefakt- & Autorisierungszustandsvertrag – Architekturentscheidung

**Status:** ENTSCHIEDEN (zur Ratifizierung)
**Rang:** C2-Vertrauensordnung, technisch-institutionelles ADR
**Einordnung:** Dieses Dokument definiert den institutionellen Vertrag, nach dem ZONVAA mit *Dingen von dauerhaftem Wert* umgeht: Vorsorgevollmachten, Nachlassmappen, Freigaben, Gesprächsprotokolle, Verfügungen. Es übersetzt die Verfassung (C1) und den Institution Layer in ein Zustandsmodell – ohne Implementierung festzulegen.
**Leitprinzip:** Ein Artefakt in ZONVAA ist kein Datensatz. Es ist ein **Rechtsobjekt mit Lebenszyklus, Eigentümern, Zeugen und Geschichte**. Die Architektur muss jedes Artefakt so behandeln, als könnte es eines Tages vor einem Gericht, einem Notar oder einer trauernden Familie liegen – denn genau das wird passieren.

---

## AAV-00: Grundsatzentscheidung – Zustandsvertrag statt Dateiverwaltung

**Kontext:** Klassische Systeme behandeln Dokumente als Dateien mit Zugriffsrechten: erstellen, bearbeiten, löschen, teilen. Für ZONVAA ist das unzureichend und gefährlich, weil seine Artefakte rechtliche und existenzielle Bedeutung tragen (Vollmachten, Verfügungen, Nachlassdokumente). „Bearbeiten" und „Löschen" sind hier keine technischen, sondern rechtliche Ereignisse – mit Beteiligten, Fristen, Widerrufen und Beweiswert.

**Entscheidung:**
Jedes Artefakt in ZONVAA unterliegt einem **typisierten Zustandsvertrag**: Eine deklarative, revisionssichere Spezifikation, die festlegt
- welcher **Typ** das Artefakt hat (und damit welche Regeln gelten),
- in welchem **Zustand** es sich befindet,
- welche **Zustandswechsel** zulässig sind, durch wen, unter welchen Bedingungen,
- wer welche **Autorisierung** hält, und wie sie entsteht, delegiert, ruht oder erlischt.

Der Zustandsvertrag ist **Teil des Artefakts selbst**, nicht eine externe Konfiguration. Ein Artefakt ohne seinen Vertrag ist ungültig; ein Vertrag ohne Artefakt ist wirkungslos.

**Verworfene Alternativen:**
- *Generisches ACL-/Rollensystem:* Kann nicht ausdrücken, dass eine Patientenverfügung nach Tod „erstarrbar" sein muss oder eine Vollmacht ruhen kann. Verworfen.
- *Freie Workflow-Engine pro Artefakt:* Beliebigkeit zerstört Prüfbarkeit und Langzeitstabilität. Verworfen; die Typologie ist absichtlich geschlossen (AAV-01).

---

## 1. DEFINITION UND EIGENTUM EINES ARTEFAKTS

### AAV-01: Definition und Typologie

**Entscheidung:**

**Definition:** Ein Artefakt ist eine versionierte, identifizierbare, einem oder mehreren Hoheitsträgern zugeordnete Einheit aus (a) Inhalt, (b) Zustandsvertrag, (c) Historie. Artefakte sind unveränderbar in ihrer Vergangenheit und veränderbar nur durch definierte Zustandswechsel in ihrer Gegenwart.

**Geschlossene Typologie (Typklassen):**

| Typklasse | Beispiele | Kernmerkmal |
|---|---|---|
| **T1 – Lebensdokument** | Vorsorgevollmacht, Patientenverfügung, Testament-Entwurf, Betreuungsverfügung | Rechtliche Wirkung außerhalb von ZONVAA; Erstarrungspflicht bei Wirksamkeit; Übergabe an Berufsträger üblich |
| **T2 – Beziehungsartefakt** | Vertrauensregister, Gesprächszusammenfassungen, Widerspruchsarchiv | Gehört der Beziehung; niemals an Dritte übertragbar; stirbt mit der Beziehung (IL-60) |
| **T3 – Verfügung** | Digitales Vermächtnis, Freigabe-Anordnungen für den Todesfall, Hoheitsstufen-Anordnungen | Bedingte Wirksamkeit (Eintrittsereignis); verschlossen bis zum Ereignis |
| **T4 – Nachweisartefakt** | Exporte, Übergabeprotokolle, Audit-Befunde, Notfall-Dokumentationen | Von Anfang an unveränderbar; dient ausschließlich der Rechenschaft |
| **T5 – Arbeitsartefakt** | Entwürfe, Checklisten, Planungsstände | Flüchtig; kann in T1/T3 überführt werden („Erhebung"), nie umgekehrt |

**Regeln:**
- Die Typklasse bestimmt den zulässigen Zustandsraum. Kein Artefakt kann seine Typklasse wechseln, außer durch die ausdrücklich definierte **Erhebung** (T5 → T1/T3), die unwiderruflich ist.
- Neue Typklassen entstehen nur durch C2-Verfahren (GOV-40). Das verhindert Typeninflation als Hintertür um Regeln.

### AAV-02: Eigentum und Hoheit

**Entscheidung:**
ZONVAA unterscheidet drei Ebenen, die in klassischen Systemen vermischt werden:

1. **Hoheit (Souveränität):** liegt grundsätzlich bei genau **einer Person** – dem Hoheitsträger. Sie umfasst: Zustandswechsel autorisieren, Freigaben erteilen und widerrufen, Löschung/Übergabe anordnen, den Vertrag lesen. Hoheit ist **nicht teilbar**. Mehrpersonenkonstellationen werden über Beteiligtenrollen gelöst (AAV-04), nicht über geteilte Hoheit. Begründung: Geteilte Hoheit erzeugt unlösbare Patt-Zustände und juristische Unklarheit im Ernstfall; ZONVAA folgt dem Prinzip „eine Verantwortung, ein Träger" (Kohärenz mit IL-61: Der Guardian gehört immer einer Person).
2. **Verfügung (Operative Befugnis):** kann an Bevollmächtigte delegiert werden (AAV-03), bleibt aber jederzeit widerrufbar und erlischt spätestens mit der Hoheit.
3. **Verwahrung (Custody):** ZONVAA ist Treuhänder (IL-30), niemals Hoheitsträger – mit einer einzigen, verfassungsverankerten Ausnahme: der **Amtsverwahrung** im Notfall (AAV-06).

**Sonderregeln:**
- **Geschäftsunfähigkeit des Hoheitsträgers:** Hoheit ruht (geht nicht über). Vorher ernannte Verfügungsberechtigte treten ein, sofern das Artefakt dies vorsieht. ZONVAA entscheidet niemals selbst über Geschäftsfähigkeit – Auslöser sind ausschließlich externe, prüfbare Ereignisse (ärztliches Zeugnis, Betreuungsanordnung), deren Erkennungsregeln im Zustandsvertrag stehen.
- **Tod des Hoheitsträgers:** Hoheit erlischt. Artefakte gehen in den Erstarrungszustand; was dann geschieht, bestimmt ausschließlich die zu Lebzeiten hinterlegte Verfügung (T3) oder, in deren Abwesenheit, der Default (Löschung nach Fristen, IL-60).
- **Minderjährige:** Hoheit bei den gesetzlichen Vertretern, aber mit **Reiferegelung**: Bei Erreichen der Volljährigkeit geht die Hoheit automatisch und vollständig auf die Person über; die bisherigen Träger verlieren jeden Zugriff, der nicht neu erteilt wird.

---

## 2. ZUSTÄNDE UND ZULÄSSIGE ZUSTANDSWECHSEL

### AAV-03: Der Kern-Zustandsautomat

**Entscheidung:**
Alle Artefakte aller Typklassen durchlaufen Teilmengen eines einheitlichen Zustandsraums. Einheitlichkeit ist Pflicht: Nur ein gemeinsamer Zustandsraum erlaubt 50 Jahre lang prüfbare, vorhersagbare Systematik statt wachsender Sonderlogik.

**Kernzustände:**

| Zustand | Bedeutung | Wer darf was |
|---|---|---|
| **ENTWURF** | In Arbeit, keine Außenwirkung | Hoheitsträger + Verfügungsberechtigte: lesen, ändern, verwerfen |
| **WIRKSAM** | Festgestellt, gegengezeichnet, außenwirksam | Änderung nur per **Neufassung** (neue Version, alte bleibt als Historie); keine stille Editierung |
| **VERSIEGELT** | Gegen inhaltliche Änderung gesperrt (z. B. T3 vor Ereignis, T4 immer) | Niemand ändert. Lesen nur nach Freigaberegeln. Entsiegelung nur durch definierte Ereignisse oder den Verfassungsnotweg (AAV-06) |
| **RUHEND** | Vorübergehend außer Kraft (z. B. Geschäftsunfähigkeit, aktiver Widerruf auf Zeit) | Keine Nutzung, keine Delegation; Reaktivierung nur durch den, der die Ruhe veranlasst hat, oder durch Ereignisregel |
| **ERSTARRT** | Endgültig geschlossen (Tod, Fristablauf, vollzogene Übergabe) | Unveränderbar für immer; Zugriff nur gemäß Verfügung/Default; dient nur noch als Beweis |
| **VERFALLEN** | Wirksamkeit durch Zeit/Ereignis erloschen (z. B. befristete Vollmacht abgelaufen) | Wie ERSTARRT, aber mit dokumentiertem Verfallsgrund |

**Zulässige Übergänge (Gesamtmatrix, Typklasse filtert Teilmengen):**

```
ENTWURF ──feststellen──▶ WIRKSAM ──sperren──▶ VERSIEGELT
   │                        │  ▲                   │
   │                        │  └──reaktivieren──┐  │ Ereignis/
   │                        ▼                   │  │ Verfassungsnotweg
   └──verwerfen──▶ (Löschung)  RUHEND ◀──────────┘  ▼
                        │      └────reaktivieren──▶ (urspr. Zustand)
                        ▼
                    ERSTARRT / VERFALLEN (Terminalzustände)
```

**Verbindliche Übergangsregeln:**
1. Jeder Übergang ist ein **signiertes Ereignis** mit: Akteur, Grundlage (welche Autorisierung), Zeitpunkt, Grund (freitext + Typcode), Vorgängerzustand. Ohne Ereignis kein Übergang; ohne Übergang keine Änderung.
2. **Einweg-Übergänge** (nicht umkehrbar): ENTWURF→WIRKSAM (Erhebung), →ERSTARRT, →VERFALLEN, T5→T1/T3 (Typwechsel). Einweg-Übergänge erfordern erhöhte Bestätigung (AAV-05, Mehrpersonenregel optional, mindestens Zwei-Faktor-Bestätigung des Hoheitsträgers mit Wartebedenkzeit für T1/T3: 24–72 h Widerrufsfenster vor Endgültigkeit).
3. **Konfliktregel bei parallelen Übergängen:** Der Zustandsautomat kennt keine Gleichzeitigkeit. Übergänge werden total geordnet (Historienkette, AAV-05). Ein zweiter Übergang auf denselben Ausgangszustand schlägt fehl und erzeugt einen Konfliktfall (AAV-07) statt stiller Überschreibung.
4. **Ereignis-Übergänge** (Tod, Volljährigkeit, Fristablauf) sind dem System gleichrangig mit Personen-Übergängen: Sie brauchen dieselbe Beweisdokumentation (welches Ereignis, welche Quelle, welche Prüfung).

---

## 3. FREIGABEN, SPERREN, WIDERRUFE, DELEGATIONEN

### AAV-04: Das Autorisierungsmodell

**Entscheidung:**
Autorisierung an einem Artefakt ist selbst ein versioniertes Objekt mit Lebenszyklus – keine Zeile in einer Berechtigungstabelle. Jede Autorisierung hat: **Subjekt** (wer), **Rolle** (siehe unten), **Umfang** (lesen / mitwirken / verfügen / verwalten), **Geltungsbereich** (ganzes Artefakt / benannte Teile), **Bedingungen** (Zeit, Ereignis, Widerrufbarkeit), **Historie**.

**Geschlossene Rollenmenge:**

| Rolle | Kann | Entsteht durch |
|---|---|---|
| **Hoheitsträger** | alles, inkl. Vertragsänderung an seinen Freigaben, Widerruf, Löschungsanordnung | Erstellung / Ereignis (Volljährigkeit) – nie durch Delegation |
| **Verfügungsberechtigter** | handeln im definierten Umfang, auch bei ruhender Hoheit (wenn vorgesehen) | ausdrückliche Delegation des Hoheitsträgers, schriftäquivalent dokumentiert |
| **Mitwirkender** | Inhalte beisteuern im ENTWURF, keine Zustandswechsel | Freigabe durch Hoheitsträger |
| **Lesender** | lesen im freigegebenen Umfang | Freigabe oder Ereignisregel (z. B. Todesfall-Freigabe) |
| **Zeuge/Bestätigender** | Existenz und Integrität bestätigen (Gegenzeichnung), kein Inhaltszugriff über die Bestätigung hinaus | Einladung + Annahme |
| **Berufsträger (extern)** | befristeter, protokollierter Übergabezugriff (Anwalt, Notar, Arzt) | Übergabeereignis (IL-51), mit Zweckbindung und automatischem Verfall |
| **Amtsverwahrer (ZONVAA)** | ausschließlich AAV-06-Notgriffe, jeder Griff einzeln begründet und öffentlich aggregiert rechenschaftspflichtig | Verfassung, nie durch Geschäftsentscheidung |

**Freigaben:**
- Freigaben sind immer **positiv, granular und widerrufbar**. Es gibt keine impliziten Freigaben („Familie sieht alles") – nur benannte.
- Freigaben haben einen **Verfalls-Default**: Ohne ausdrückliche Befristung verfallen Lese- und Mitwirkungsfreigaben nach 24 Monaten und müssen erneuert werden (Bestätigung durch den Hoheitsträger). Begründung: Zugriffsrechte, die nie altern, werden zur stillen Gefahr; Menschen vergessen, was sie einmal freigegeben haben.
- Der Hoheitsträger erhält eine jederzeit abrufbare **Freigabe-Übersicht in Menschensprache** („Diese 4 Personen können das sehen, davon läuft diese eine in 3 Monaten ab").

**Sperren:**
- Zwei Arten: **Hoheitssperre** (Hoheitsträger versiegelt eigenes Artefakt, z. B. T3) und **Ereignissperre** (System sperrt bei definiertem Ereignis, z. B. Tod).
- Es gibt **keine Fremdsperre**: Niemand außer dem Hoheitsträger kann ein wirksames Artefakt sperren – außer über den Verfassungsnotweg (AAV-06). Diese Regel ist der zentrale Missbrauchsschutz gegenüber ZONVAA selbst und gegenüber Dritten mit Zugriffswünschen (Familienmitglieder, Behörden, Partner).

**Widerrufe:**
- Widerruf ist ein **Grundrecht des Hoheitsträgers**: jederzeit, ohne Begründungspflicht, mit sofortiger Wirkung für die Zukunft.
- Ausnahme-Fenster: Bei Einweg-Übergängen (AAV-03.2) gilt das Bedenkzeitfenster umgekehrt als Widerrufsfenster – innerhalb von 24–72 h ist der Übergang widerrufbar, danach endgültig.
- Widerruf löscht nicht die Historie (Revisionssicherheit geht vor Vergessen-Wollen an dieser Stelle); er beendet Wirkung und Zugriff. Gelöscht wird nur, was die Löschungsanordnung (AAV-08) ausdrücklich erfasst.

**Delegationen:**
- Delegation ist immer **enge-Default**: Umfang, Dauer, Bereich müssen benannt sein; „Generalvollmacht im System" existiert nicht als Default, sondern nur als bewusst bestätigte, mit Warnung versehene Option.
- Delegationen sind **nicht weiterdelegierbar** (keine Subdelegation). Ein Verfügungsberechtigter kann keine Verfügungsberechtigten ernennen.
- Delegationen **ruhen automatisch** bei Ruhen des delegierenden Artefakts und **erlöschen** bei Erstarrung, Verfall oder Tod des Delegierenden – es sei denn, ein T3-Artefakt ordnet ausdrücklich ein Übergreifen in den Todesfall an (dann und nur dann: Fortgeltung als beschränkte Nachlass-Verfügung).
- **Pflicht zur Lebenslage-Prüfung:** Delegationen an Personen, mit denen ein erkennbarer Interessenkonflikt besteht (z. B. Erbe delegiert Zugriff auf Testament des künftigen Erblassers), lösen eine Warnpflicht des Guardians aus – keine Sperre, aber eine dokumentierte Nachfrage (Kohärenz mit IL-61 Interessenkonflikt-Regel).

### AAV-05: Mehrpersonenfreigaben

**Entscheidung:**
Mehrpersonenanforderungen werden über **Quoren** modelliert, nicht über geteilte Hoheit:

1. **Quorum-Typen (geschlossen):**
   - **Gegenzeichnung (2-Augen):** Übergang wirksam nur mit Bestätigung einer zweiten, benannten Rolle (z. B. Zeuge).
   - **M-von-N-Quorum:** Für definierte Übergänge (z. B. Entsiegelung einer Verfügung) müssen M von N benannten Personen zustimmen. N≤7 (Bindung an die Erkenntnis aus GOV-20: größere Gremien erzeugen Patt- und Käuflichkeitsrisiken).
   - **Kettengenehmigung:** Reihenfolgegebundene Zustimmung (z. B. erst Berufsträger, dann Hoheitsträger).
2. **Quoren gelten pro Übergang, nicht pro Artefakt pauschal.** Der Zustandsvertrag benennt, welcher Übergang welches Quorum braucht. Default für Standardübergänge: keine Quore (Hoheitsträger allein). Quore sind Schutz, nicht Alltag – Alltagsquoren erzeugen Abstimmungsmüdigkeit und dann Leichtfertigkeit.
3. **Verhinderungsregel:** Ist ein Quorumsmitglied dauerhaft verhindert (Tod, Ausfall), gilt eine im Vertrag vordefinierte Ersatzregel (benannter Stellvertreter oder Absenkung M-1, deklariert bei Vertragsstellung). Fehlt die Ersatzregel, greift **nicht** das System ein – sondern der dokumentierte Konfliktweg (AAV-07). Das System improvisiert niemals Mehrheiten.
4. **Enthaltung zählt als Nicht-Zustimmung.** Es gibt kein „passiert automatisch nach Frist". Schweigen darf niemals Wirksamkeit erzeugen (Prinzip: Zustimmung ist ein Akt, kein Ausbleiben).
5. **Zeugen sind keine Mitentscheider:** Gegenzeichnung bestätigt Identität/Vollzug, nicht inhaltliche Zustimmung. Die Vermischung beider Rollen ist ein klassischer Missbrauchsweg (Zeuge „stimmt zu") und ist verboten.

---

## 4. REVISIONSSICHERHEIT

### AAV-06: Historie, Beweis und der Verfassungsnotweg

**Entscheidung:**

1. **Append-only-Historie:** Jede Änderung, jeder Übergang, jede Autorisierung, jeder Zugriff (auch lesend, durch jede Rolle inklusive ZONVAA-Personal) ist ein verketteter, manipulationssicherer Eintrag. Vergangenheit ist physikalisch nicht editierbar – nicht „per Policy verboten", sondern konstruktiv ausgeschlossen.
2. **Beweisfähigkeit als Designziel:** Die Historie muss so geführt sein, dass sie in einem Rechtsstreit nach 30 Jahren rekonstruierbar und prüfbar ist: unabhängig verifizierbare Integrität (Hash-Verkettung o. ä.), Zeitnachweise, menschenlesbare Exporte (Offenformat IL-21). ZONVAA darf nicht der einzige sein, der die Historie lesen kann – sonst ist die Historie im Zweifel wertlos.
3. **Zugriff auf die Historie:** Der Hoheitsträger sieht seine volle Historie. Externe (Erben, Gerichte) sehen sie nur im Rahmen der Verfügung oder gesetzlicher Pflichten. ZONVAA-Mitarbeitende sehen Historien nur im Vier-Augen-Verfahren mit nutzersehbarem Log (IL-30.3).
4. **Der Verfassungsnotweg (Amtsverwahrung):** Es existiert genau ein Weg, auf dem ZONVAA ohne Hoheitsträger auf ein Artefakt einwirken darf: Gefahr im Verzug für Leib, Leben oder Kindeswohl (C1/Art. 3), oder gerichtliche Anordnung. Bedingungen, kumulativ:
   - schriftliche Einzelfallbegründung durch zwei unabhängige Amtsverwahrer (Vier-Augen),
   - zeitlich befristeter, minimalster Eingriff (lesen statt ändern, versiegeln statt löschen),
   - automatische Benachrichtigung des Vertrauensrats (manipulationssichere Pipeline, GOV-30A),
   - Benachrichtigung des Betroffenen, sobald dies die Gefahrenabwehr nicht gefährdet,
   - Eintrag ins öffentliche aggregierte Rechenschaftsregister (IL-62) und ins permanente Register (GOV-31).
   Jeder andere Eingriff – auch „zum Schutz des Nutzers", auch „technisch nötig", auch auf Bitten von Angehörigen – ist Verfassungsbruch.

---

## 5. KONFLIKTE ZWISCHEN BETEILIGTEN

### AAV-07: Das Konfliktkaskaden-Modell

**Entscheidung:**
Konflikte sind Normalfälle (Erbe, Scheidung, Betreuung) und werden in einer festen Eskalationskaskade behandelt. Kernprinzip: **Das System entscheidet Konflikte nicht inhaltlich. Es hält Zustände fest, dokumentiert und leitet an legitime Instanzen weiter.**

| Stufe | Konflikttyp | Systemverhalten |
|---|---|---|
| **K1 – Rollenkonflikt** | Zwei Autorisierungen beanspruchen denselben Übergang | Totale Ordnung der Historie; der spätere Übergang scheitert sichtbar, kein stilles Überschreiben |
| **K2 – Quorums-Patt** | Quorum nicht erreichbar, keine Ersatzregel | Artefakt bleibt im aktuellen Zustand (Stillstand ist der sichere Default); Benachrichtigung aller Beteiligten mit Frist; danach K3 |
| **K3 – Beteiligtenstreit** | Personen widersprechen sich über Rechte/Verhalten (z. B. Bevollmächtigter handelt mutmaßlich gegen Interesse des Hoheitsträgers) | Der Hoheitsträger kann jederzeit widerrufen (sein Grundrecht). Kann er es nicht (Geschäftsunfähigkeit, Abwesenheit): **Schlichtungspfad** – dokumentierte Vermittlung durch den Guardian (ohne Entscheidungsmacht!), Hinweis auf reale Instanzen (Betreuungsgericht, Anwalt). Das System darf den Streit nicht durch Aktion „lösen" |
| **K4 – Rechtsstreit** | Gerichtliche Klärung läuft oder ist erkennbar unvermeidlich | **Justiziabilitätsmodus:** betroffenes Artefakt wird befristet versiegelt (Erhaltung des Beweisstands), Historie exportierbar für legitime Instanzen, keinerlei inhaltliche Änderung bis Klärung oder Verjährungsfrist |
| **K5 – Missbrauchsverdacht** | Hinweise auf Nötigung, Ausnutzung (z. B. plötzliche Delegationsflut bei vulnerablen Hoheitsträgern) | Guardian-Pflicht zur dokumentierten Nachfrage; optionaler Schutzmodus: erhöhte Bestätigungsschwellen + Benachrichtigung einer zu Lebzeiten benannten Vertrauensperson; bei Klasse-A-Signalen: Notfall-Override (IL-50) |

**Verbindliche Nebenregeln:**
- **Neutralitätsregel bei verbundenen Konten (IL-61):** Betrifft ein Konflikt mehrere ZONVAA-Nutzer (z. B. Erben, die beide Kunden sind), begleitet der Guardian jede Partei ausschließlich in deren Interesse und vermittelt nicht zwischen ihnen. Artefaktseitig gilt: Keine Partei erhält durch den Konflikt Zugriff auf Inhalte der anderen.
- **Kein Schiedsrichter-Guardian:** Der Guardian darf niemals Schlichtungssprüche sprechen. Seine Rolle endet bei Strukturieren, Dokumentieren, Weiterleiten. (Kohärenz zu IL-51: Navigator, nicht Berufsträger.)
- **Dokumentationspflicht:** Jeder Konflikt K2+ erzeugt einen Konfliktakt im Artefakt (wer, was, welcher Stand, welcher Pfad). Konflikte sind Teil der Artefaktgeschichte, keine Support-Tickets am Rand.

---

## 6. EINORDNUNG IN DIE GESAMTARCHITEKTUR

### AAV-08: Verortung in Constitution, Governance, Institution und Runtime

**Entscheidung (Schichtenabbildung):**

| Schicht | Was davon in diesem Vertrag liegt | Bindung |
|---|---|---|
| **C1 Verfassung** | Prinzipien, die der Zustandsvertrag operationalisiert: Datenhoheit (Art. 2) → Hoheitsmodell AAV-02; Sicherheit (Art. 3) → Verfassungsnotweg AAV-06; Wahrhaftigkeit (Art. 5) → Revisionssicherheit; Freiheit (Art. 6) → Widerrufsgrundrecht, kein Lock-in | Der Zustandsvertrag darf C1 nie verletzen; Zweifelsfälle gehen an den Vertrauensrat |
| **C2 Vertrauensordnung / Governance** | Typklassen (Änderung = C2-Verfahren), Quoren-Maxima, Verfalls-Defaults, Notweg-Bedingungen, Rechenschaftsflüsse (Register, Vertrauensbericht) | Änderungen an diesem ADR nur per GOV-40/C2; Vetodomäne 2 (Daten) und 4 (Kontinuität) |
| **Institution Layer (IL)** | Treuhand (IL-30), Hoheitsstufen (IL-31 → abgebildet als Artefakt-Attribute), Übergabe (IL-51 → Rolle Berufsträger), Tod (IL-60 → Erstarrung/T3), Export/Sunset (IL-21 → T4-Artefakte und Historienexport) | Dieses ADR ist die *operationale Ausformung* der IL-Datenschicht; IL bleibt führend |
| **Conversation Layer** | Der Guardian erzeugt, schlägt vor, erinnert, fragt nach (K5, Delegationswarnungen) – er **vollzieht** Zustandswechsel niemals eigenmächtig. Jeder Übergang braucht eine menschliche Autorisierung oder ein deklariertes Ereignis | Trennung Dramaturgie ↔ Zustandsvertrag: Das Gespräch darf Vertrauen bilden, nie Rechte bewegen |
| **Runtime (Implementierung, außerhalb dieses ADR)** | Persistenz der Historie, Signatur-/Hash-Mechanik, Verfallsläufer, Benachrichtigungspipeline, Export-Engine | Dieses ADR legt *keine* Technologie fest; es legt Eigenschaften fest, gegen die jede Implementierung auditierbar ist (GOV-30, Stufe C) |

**Ableitungsregel für die Runtime:** Jede künftige Implementierung muss gegen eine **Eigenschaftsliste** (nicht gegen diesen Prosatext) geprüft werden. Die Eigenschaftsliste (Append-only, totale Ordnung, keine Fremdsperre, Verfalls-Defaults, Notweg-Bedingungen …) wird als eigenes, versioniertes Prüfartefakt (T4) geführt – Runtime-Änderungen, die eine Eigenschaft verletzen, sind per Definition Verfassungsverstoß und lösen GOV-31 aus.

---

## 7. LANGZEITSTABILITÄT UND MISSBRAUCHSSCHUTZ

### AAV-09: 50-Jahre-Festigkeit

**Entscheidung:**
1. **Vertragsversionierung mit Ewigkeits-Lesbarkeit:** Zustandsverträge sind versioniert. Alte Versionen müssen von jeder künftigen Runtime **lesbar und ausführbar** bleiben (Kompatibilitätspflicht rückwärts, analog zur Beziehungsschicht IL-22). Ein Vertrag von 2026 muss im Jahr 2076 noch korrekt interpretiert werden. Migrationen dürfen Lesbarkeit schaffen, niemals Bedeutung ändern.
2. **Semantische Stabilität:** Zustände, Rollen und Übergänge haben unveränderliche Bedeutungskerne (z. B. ERSTARRT bedeutet immer: unveränderbar, terminal). Erweiterungen sind erlaubt, Bedeutungsverschiebungen sind Verfassungsbruch. (Spiegelung der GOV-40-Ewigkeitslogik auf Artefaktebene.)
3. **Sunset-Festigkeit:** Artefakte samt Verträgen und Historien sind vollständig im Nutzerexport (IL-21) enthalten – der Zustandsvertrag ist so spezifiziert, dass ein Nachfolgeträger oder der Nutzer selbst ihn **ohne ZONVAA-Software** interpretieren kann (deklarativ, dokumentiert, menschenlesbar neben maschinenlesbar).
4. **Verfalls-Ökonomie:** Alles in diesem System altert: Freigaben (24 Monate), Delegationen (befristet), Quoren (Ersatzregeln), Artefakte selbst (Prüf- und Erneuerungszyklen für T1: Der Guardian erinnert, dass Lebensdokumente alle ~3–5 Jahre oder bei Lebensereignissen überprüft werden sollten). **Nichts darf durch Vergessen wirksam bleiben.** Vergessen ist der größte Feind langfristiger Rechtssicherheit.

### AAV-10: Missbrauchsschutz-Matrix

**Entscheidung:** Die folgenden Angriffs-/Missbrauchswege sind benannt, und je ist der Abwehrmechanismus im Vertrag verankert (nicht in der Kulanz):

| Missbrauchsweg | Abwehr |
|---|---|
| **ZONVAA selbst sperrt/ändert/löst Artefakte** (geschäftlich motiviert, Erpressung, „Fehlkonfiguration") | Keine Fremdsperre (AAV-04); Amtsverwahrung nur im Notweg mit Registerpflicht; Treuhandkonstruktion IL-30 |
| **Angehörige drängen auf Zugriff** („Er wollte das sicher so") | Kein Zugriff ohne Verfügung; Wunschdenken Dritter ist kein Ereignis; Guardian verweist auf reale Instanzen |
| **Bevollmächtigter missbraucht Delegation** | Enge-Default, Widerrufsgrundrecht, K5-Schutzmodus, Delegationswarnung bei Interessenkonflikt |
| **Nötigung des Hoheitsträgers** (Übergänge unter Druck) | Bedenkzeitfenster bei Einweg-Übergängen, erhöhte Bestätigung, K5-Vertrauensperson, Guardian-Nachfragepflicht |
| **Stille Rechteanhäufung** (vergessene Freigaben) | Verfalls-Defaults, Freigabe-Übersicht in Menschensprache, Erneuerungspflicht |
| **Quorums-Kaperung** (Mehrheit erkauft/erpresst) | N≤7, Ersatzregeln deklariert, Enthaltung ≠ Zustimmung, kein System-Improvisieren |
| **Historienfälschung** (nachträgliche „Korrektur") | Append-only, konstruktive Nicht-Editierbarkeit, unabhängige Verifizierbarkeit |
| **Typeninflation als Regelumgehung** („neuer Artefakttyp ohne die Schutzregeln") | Geschlossene Typologie, neue Typen nur per C2-Verfahren |
| **Implementierungsdrift** (Runtime tut still etwas anderes als der Vertrag) | Eigenschaftsliste als Prüfartefakt, GOV-30 Audits Stufe A+C mit technischer Verifikation |
| **Vorgetäuschte Ereignisse** (falscher Todesnachweis, gefälschte Volljährigkeit) | Ereignis-Übergänge brauchen prüfbare Quellen und dokumentierte Prüfung; Fehlauslösung ist registrierbarer Vertrauensverstoß mit Wiederherstellungspfad (aus der Historie rekonstruierbar) |
| **Nachfolger-Verfall** (künftige Generation lockert Regeln „modernisierend") | Semantische Stabilität, C2-Änderungspfad mit Rat + Fristen, Ewigkeitsbedeutungen |

---

## Bewusst in Kauf genommene Nachteile

| Entscheidung | Preis |
|---|---|
| Genau ein Hoheitsträger pro Artefakt | Gemeinsame Dokumente (Ehepaar-Vollmacht) brauchen zwei verknüpfte Artefakte statt eines bequemen gemeinsamen; Mehraufwand für echte juristische Klarheit |
| Verfalls-Defaults (24 Monate) | Nutzer müssen Freigaben erneuern – Reibung, gelegentlicher Frust; bewusst gewählt gegen stille Gefahr |
| Kein System-Improvisieren bei Patt | Konflikte können Artefakte monatelang „einfrieren"; unbequem, aber der einzige neutrale Default |
| Bedenkzeitfenster bei Einweg-Übergängen | Verzögert dringende Dokumente um 24–72 h; in Kauf genommen als Nötigungsschutz (Notfallwege über Klasse-A bleiben unberührt) |
| Append-only trotz Widerrufswunsch | Nutzer können ihre Vergangenheit nicht tilgen, nur ihre Wirkung beenden; erfordert ehrliche Kommunikation, erzeugt gelegentlich Unverständnis |
| Verfassungsnotweg existiert überhaupt | Jede Notausnahme ist ein potenzieller Missbrauchsweg; Alternative (null Notzugriff, auch bei Lebensgefahr) wurde als ethisch schlimmer bewertet – daher maximale Eingriffsbedingungen statt Verzicht |

## Offene Punkte (Folge-ADRs)

1. **Eigenschaftsliste als Prüfartefakt (T4):** formale, versionierte Aufstellung aller auditierbaren Eigenschaften dieses Vertrags – Voraussetzung für GOV-30-Audits.
2. **Ereignisquellen-Register:** welche externen Ereignisse (Sterberegister, Volljährigkeit, Betreuungsanordnung) mit welcher Beweisqualität anerkannt werden – rechtslandabhängig, Verknüpfung zu LTS-31 (Instanzen).
3. **Bedenkzeitfenster-Differenzierung:** 24–72 h ist eine Spanne; Festlegung je Typklasse und Übergang (mit Begründung; Suizidgefährdungs-Kontexte brauchen möglicherweise andere Fenster als Vollmachten).
4. **Verknüpfung geteilter Artefakte** (Ehepaar/Familie): Referenzierungsmodell zwischen getrennten Hoheitsartefakten, ohne Hoheitsvermischung.
5. **Wiederherstellungspfad nach Fehlereignis:** formaler Ablauf zur Rekonstruktion des rechtmäßigen Zustands aus der Historie (Fehlauslösung Todesfall etc.).
6. **Quoren-UX:** Wie ein Laie ein M-von-N-Quorum versteht, einrichtet und durchläuft, ohne es aus Frustration zu umgehen – Zusammenarbeit mit Conversation Design.
7. **Konfliktakt-Taxonomie:** standardisierte Typcodes für Konfliktgründe, damit Konflikte über Jahrzehnte statistisch auswertbar bleiben (Forschung, Sentinel, Vertrauensbericht).

---

## Schlussformel

Der Artefakt- und Autorisierungszustandsvertrag ist die Stelle, an der ZONVAAs Verfassung **physisch** wird. Alles, was die Institution verspricht – Hoheit, Treuhand, Widerruf, Erstarrung, Rechenschaft – existiert nur dann wirklich, wenn es in Zuständen, Übergängen und Historien ausgedrückt ist, die kein Geschäftsdruck, kein Nachfolger und kein Angreifer still verändern kann.

Die Architektur folgt einer einzigen obersten Regel, aus der alles andere abgeleitet ist:

**Das System darf niemals mächtiger sein als der Vertrag – und der Vertrag gehört dem Menschen.**

---

*Dieses Dokument ist Teil der C2-Vertrauensordnung. Änderungen nur nach GOV-40 bzw. dem C2-Verfahren. Berührt Vetodomänen 2 und 4 (GOV-22).*

## Binding accepted content
- Typisierte, versionierte Artefaktzustände
- Explizite, granulare, zweckgebundene, nachvollziehbare und widerrufbare Autorisierung
- Strikte Trennung zwischen Gespräch und autorisierter Handlung
- Keine impliziten Familien-, Rollen- oder Zugriffsrechte
- Isolierte personengebundene Kontexte
- Sichtbare Konflikte ohne automatische Parteinahme
- Keine stille Überschreibung paralleler Zustandsänderungen
- Auditierbare Zustandsübergänge
- Exportierbare und langfristig interpretierbare Historien

## Binding modifications
- Genau ein verantwortlicher Hoheitsträger pro Artefakt; mehrere autorisierte Beteiligte bleiben möglich.
- Irreversibilität wird je Übergangstyp definiert.
- C2 regelt Prinzipien, Rollen, Vetos und Prüfpflichten.
- C3 regelt konkrete Fristen, Gesten, Quoren und technische Verfahren.
- Historien werden nach Datenklasse unterschieden: unveränderbar, aufbewahrungspflichtig, löschbar oder anonymisierbar.
- Widerrufe wirken sofort, soweit keine dokumentierte rechtliche oder technische Bindung entgegensteht.
- Notfall- und automatische Ereignisübergänge werden separat behandelt.
- Unbestätigte Rechtswirkungs- und Kryptografiebegriffe werden entfernt oder neutral formuliert.
- Nicht vorhandene Referenzen werden ersetzt oder entfernt.

## Explicitly rejected content
- Zwingende Drei-Sekunden-Geste
- Verpflichtende Biometrie-, SMS- oder Token-Vorgaben
- Unbestätigte Zero-Knowledge-, Signatur- oder Verschlüsselungsbehauptungen
- Pauschale rechtliche Wirksamkeits- oder Beweisgarantien
- Automatische externe Notfall- oder Amtsmaßnahmen
- Absolute Unlöschbarkeit sämtlicher Historien

## Deferred content
- None

## Rationale
Der gemeinsame Kern stärkt Nutzerhoheit, Nachvollziehbarkeit und die Trennung zwischen Gespräch und Handlung. Technische, rechtliche und operative Details benötigen gesonderte Prüfung.

## Existing binding sources
- C1-CONSTITUTION
- MDR-0001-guardian-conversation-and-continuity
- C2-GOVERNANCE-CHARTER
- SPEC-INSTITUTION
- SPEC-INTERACTION
- ADR-0002-knowledge-system
- ADR-0003-runtime-journal
- ADR-0004-runtime-architecture
- ADR-0005-decision-engine
- ADR-0006-execution-engine
- ADR-0007-knowledge-priority
- ADR-0008-identity-first
- ADR-0009-memory-architecture
- ADR-0010-goal-engine
- ADR-0011-goal-evaluation-contract
- ADR-0012-why-assessment-model
- ADR-0013-decision-why-integration
- ADR-0014-goal-aware-orchestration
- ADR-0015-goal-application-service
- ADR-0016-decision-journal
- ADR-0017-knowledge-proposal-execution
- ADR-0018-life-decisions
- ADR-0019-life-decisions-domain-model
- ADR-0020-codex-context-and-handover
- ADR-0021-mission-context-workflow-integration
- ADR-0022-power-of-attorney-workflow
- ADR-0025-institution-layer
- ADR-0027-governance-architecture
- ADR-0028-architecture-integrator-agent
- ADR-0029-architecture-workflow-orchestrator
- C3-OPERATIVE-RULES

## Existing affected documents
- constitution/constitution.md
- governance/charter.md
- institution/institution.md
- interaction/interaction.md
- knowledge/adr/ADR-0002-knowledge-system.md
- knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md

## Protection goals and constraints
- C1, MDR-0001 und bestehende verbindliche Schichtverträge dürfen nicht automatisch überschrieben werden.
- Der Entwurf ist ein Proposal und trotz eigener Statusangabe nicht ratifiziert.
- Konkrete Rechtsfolgen, Fristen, Quoren, Kryptografie und externe Ereignisquellen benötigen gesonderte Bestätigung und Prüfung.

## Non-goals
- Do not implement rejected or deferred elements.
- Do not call external AI services or use network access.
- Do not create UI unless explicitly accepted above.
- Do not weaken C1, MDR-0001, C2, Institution, or Interaction guarantees.
- Do not treat Integrator recommendations as authority.

## Required verification
- Add focused tests for every accepted invariant and modified boundary.
- Preserve and run the complete existing test suite.
- Run `python3 -m builder.main doctor`.
- Run `git diff --check` and inspect `git status --short`.
- Review the full architecture diff for conflicts and unintended changes.
- Create JSON and Markdown handover files.


## Workflow commit

Implement all confirmed sections as one coherent work package.
Run the required complete tests and Doctor checks once after the integrated change.
Create one commit only after all checks pass.
Suggested message: `Integrate confirmed architecture workflow`

Do not push.
