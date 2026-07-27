# ENTSCHEIDUNGSVORLAGE

## Empfehlung
ADOPT

## Kernaussage
Proposal artifact-authorization-kimi-contract was compared with the loaded architecture. 0 aligned, 114 additive, 0 conflicting, and 3 duplicate elements were identified. The recommendation is advisory. Only the Chief Architect may decide.

## Übernehmen
- ZONVAA Artefakt- & Autorisierungszustandsvertrag – Architekturentscheidung
- **Status:** ENTSCHIEDEN (zur Ratifizierung) **Rang:** C2-Vertrauensordnung, technisch-institutionelles ADR **Einordnung:** Dieses Dokument definiert den institutionellen Vertrag, nach dem ZONVAA mit *Dingen von dauerhaftem Wert* umgeht: Vorsorgevollmachten, Nachlassmappen, Freigaben, Gesprächsprotokolle, Verfügungen. Es übersetzt die Verfassung (C1) und den Institution Layer in ein Zustandsmodell – ohne Implementierung festzulegen. **Leitprinzip:** Ein Artefakt in ZONVAA ist kein Datensatz. Es ist ein **Rechtsobjekt mit Lebenszyklus, Eigentümern, Zeugen und Geschichte**. Die Architektur muss jedes Artefakt so behandeln, als könnte es eines Tages vor einem Gericht, einem Notar oder einer trauernden Familie liegen – denn genau das wird passieren.
- ---
- AAV-00: Grundsatzentscheidung – Zustandsvertrag statt Dateiverwaltung
- **Kontext:** Klassische Systeme behandeln Dokumente als Dateien mit Zugriffsrechten: erstellen, bearbeiten, löschen, teilen. Für ZONVAA ist das unzureichend und gefährlich, weil seine Artefakte rechtliche und existenzielle Bedeutung tragen (Vollmachten, Verfügungen, Nachlassdokumente). „Bearbeiten" und „Löschen" sind hier keine technischen, sondern rechtliche Ereignisse – mit Beteiligten, Fristen, Widerrufen und Beweiswert.
- **Entscheidung:** Jedes Artefakt in ZONVAA unterliegt einem **typisierten Zustandsvertrag**: Eine deklarative, revisionssichere Spezifikation, die festlegt
- welcher **Typ** das Artefakt hat (und damit welche Regeln gelten),
- in welchem **Zustand** es sich befindet,
- welche **Zustandswechsel** zulässig sind, durch wen, unter welchen Bedingungen,
- wer welche **Autorisierung** hält, und wie sie entsteht, delegiert, ruht oder erlischt.
- Der Zustandsvertrag ist **Teil des Artefakts selbst**, nicht eine externe Konfiguration. Ein Artefakt ohne seinen Vertrag ist ungültig; ein Vertrag ohne Artefakt ist wirkungslos.
- **Verworfene Alternativen:**
- *Generisches ACL-/Rollensystem:* Kann nicht ausdrücken, dass eine Patientenverfügung nach Tod „erstarrbar" sein muss oder eine Vollmacht ruhen kann. Verworfen.
- *Freie Workflow-Engine pro Artefakt:* Beliebigkeit zerstört Prüfbarkeit und Langzeitstabilität. Verworfen; die Typologie ist absichtlich geschlossen (AAV-01).
- 1. DEFINITION UND EIGENTUM EINES ARTEFAKTS
- AAV-01: Definition und Typologie
- **Definition:** Ein Artefakt ist eine versionierte, identifizierbare, einem oder mehreren Hoheitsträgern zugeordnete Einheit aus (a) Inhalt, (b) Zustandsvertrag, (c) Historie. Artefakte sind unveränderbar in ihrer Vergangenheit und veränderbar nur durch definierte Zustandswechsel in ihrer Gegenwart.
- **Geschlossene Typologie (Typklassen):**
- Die Typklasse bestimmt den zulässigen Zustandsraum. Kein Artefakt kann seine Typklasse wechseln, außer durch die ausdrücklich definierte **Erhebung** (T5 → T1/T3), die unwiderruflich ist.
- Neue Typklassen entstehen nur durch C2-Verfahren (GOV-40). Das verhindert Typeninflation als Hintertür um Regeln.
- AAV-02: Eigentum und Hoheit
- **Entscheidung:** ZONVAA unterscheidet drei Ebenen, die in klassischen Systemen vermischt werden:
- **Hoheit (Souveränität):** liegt grundsätzlich bei genau **einer Person** – dem Hoheitsträger. Sie umfasst: Zustandswechsel autorisieren, Freigaben erteilen und widerrufen, Löschung/Übergabe anordnen, den Vertrag lesen. Hoheit ist **nicht teilbar**. Mehrpersonenkonstellationen werden über Beteiligtenrollen gelöst (AAV-04), nicht über geteilte Hoheit. Begründung: Geteilte Hoheit erzeugt unlösbare Patt-Zustände und juristische Unklarheit im Ernstfall; ZONVAA folgt dem Prinzip „eine Verantwortung, ein Träger" (Kohärenz mit IL-61: Der Guardian gehört immer einer Person).
- **Verfügung (Operative Befugnis):** kann an Bevollmächtigte delegiert werden (AAV-03), bleibt aber jederzeit widerrufbar und erlischt spätestens mit der Hoheit.
- **Verwahrung (Custody):** ZONVAA ist Treuhänder (IL-30), niemals Hoheitsträger – mit einer einzigen, verfassungsverankerten Ausnahme: der **Amtsverwahrung** im Notfall (AAV-06).
- **Sonderregeln:**
- **Geschäftsunfähigkeit des Hoheitsträgers:** Hoheit ruht (geht nicht über). Vorher ernannte Verfügungsberechtigte treten ein, sofern das Artefakt dies vorsieht. ZONVAA entscheidet niemals selbst über Geschäftsfähigkeit – Auslöser sind ausschließlich externe, prüfbare Ereignisse (ärztliches Zeugnis, Betreuungsanordnung), deren Erkennungsregeln im Zustandsvertrag stehen.
- **Tod des Hoheitsträgers:** Hoheit erlischt. Artefakte gehen in den Erstarrungszustand; was dann geschieht, bestimmt ausschließlich die zu Lebzeiten hinterlegte Verfügung (T3) oder, in deren Abwesenheit, der Default (Löschung nach Fristen, IL-60).
- **Minderjährige:** Hoheit bei den gesetzlichen Vertretern, aber mit **Reiferegelung**: Bei Erreichen der Volljährigkeit geht die Hoheit automatisch und vollständig auf die Person über; die bisherigen Träger verlieren jeden Zugriff, der nicht neu erteilt wird.
- 2. ZUSTÄNDE UND ZULÄSSIGE ZUSTANDSWECHSEL
- AAV-03: Der Kern-Zustandsautomat
- **Entscheidung:** Alle Artefakte aller Typklassen durchlaufen Teilmengen eines einheitlichen Zustandsraums. Einheitlichkeit ist Pflicht: Nur ein gemeinsamer Zustandsraum erlaubt 50 Jahre lang prüfbare, vorhersagbare Systematik statt wachsender Sonderlogik.
- **Kernzustände:**
- **Zulässige Übergänge (Gesamtmatrix, Typklasse filtert Teilmengen):**
- ENTWURF ──feststellen──▶ WIRKSAM ──sperren──▶ VERSIEGELT │                        │  ▲                   │ │                        │  └──reaktivieren──┐  │ Ereignis/ │                        ▼                   │  │ Verfassungsnotweg └──verwerfen──▶ (Löschung)  RUHEND ◀──────────┘  ▼ │      └────reaktivieren──▶ (urspr. Zustand) ▼ ERSTARRT / VERFALLEN (Terminalzustände)
- **Verbindliche Übergangsregeln:**
- Jeder Übergang ist ein **signiertes Ereignis** mit: Akteur, Grundlage (welche Autorisierung), Zeitpunkt, Grund (freitext + Typcode), Vorgängerzustand. Ohne Ereignis kein Übergang; ohne Übergang keine Änderung.
- **Einweg-Übergänge** (nicht umkehrbar): ENTWURF→WIRKSAM (Erhebung), →ERSTARRT, →VERFALLEN, T5→T1/T3 (Typwechsel). Einweg-Übergänge erfordern erhöhte Bestätigung (AAV-05, Mehrpersonenregel optional, mindestens Zwei-Faktor-Bestätigung des Hoheitsträgers mit Wartebedenkzeit für T1/T3: 24–72 h Widerrufsfenster vor Endgültigkeit).
- **Konfliktregel bei parallelen Übergängen:** Der Zustandsautomat kennt keine Gleichzeitigkeit. Übergänge werden total geordnet (Historienkette, AAV-05). Ein zweiter Übergang auf denselben Ausgangszustand schlägt fehl und erzeugt einen Konfliktfall (AAV-07) statt stiller Überschreibung.
- **Ereignis-Übergänge** (Tod, Volljährigkeit, Fristablauf) sind dem System gleichrangig mit Personen-Übergängen: Sie brauchen dieselbe Beweisdokumentation (welches Ereignis, welche Quelle, welche Prüfung).
- 3. FREIGABEN, SPERREN, WIDERRUFE, DELEGATIONEN
- AAV-04: Das Autorisierungsmodell
- **Entscheidung:** Autorisierung an einem Artefakt ist selbst ein versioniertes Objekt mit Lebenszyklus – keine Zeile in einer Berechtigungstabelle. Jede Autorisierung hat: **Subjekt** (wer), **Rolle** (siehe unten), **Umfang** (lesen / mitwirken / verfügen / verwalten), **Geltungsbereich** (ganzes Artefakt / benannte Teile), **Bedingungen** (Zeit, Ereignis, Widerrufbarkeit), **Historie**.
- **Geschlossene Rollenmenge:**
- Freigaben sind immer **positiv, granular und widerrufbar**. Es gibt keine impliziten Freigaben („Familie sieht alles") – nur benannte.
- Freigaben haben einen **Verfalls-Default**: Ohne ausdrückliche Befristung verfallen Lese- und Mitwirkungsfreigaben nach 24 Monaten und müssen erneuert werden (Bestätigung durch den Hoheitsträger). Begründung: Zugriffsrechte, die nie altern, werden zur stillen Gefahr; Menschen vergessen, was sie einmal freigegeben haben.
- Der Hoheitsträger erhält eine jederzeit abrufbare **Freigabe-Übersicht in Menschensprache** („Diese 4 Personen können das sehen, davon läuft diese eine in 3 Monaten ab").
- **Sperren:**
- Zwei Arten: **Hoheitssperre** (Hoheitsträger versiegelt eigenes Artefakt, z. B. T3) und **Ereignissperre** (System sperrt bei definiertem Ereignis, z. B. Tod).
- Es gibt **keine Fremdsperre**: Niemand außer dem Hoheitsträger kann ein wirksames Artefakt sperren – außer über den Verfassungsnotweg (AAV-06). Diese Regel ist der zentrale Missbrauchsschutz gegenüber ZONVAA selbst und gegenüber Dritten mit Zugriffswünschen (Familienmitglieder, Behörden, Partner).
- **Widerrufe:**
- Widerruf ist ein **Grundrecht des Hoheitsträgers**: jederzeit, ohne Begründungspflicht, mit sofortiger Wirkung für die Zukunft.
- Ausnahme-Fenster: Bei Einweg-Übergängen (AAV-03.2) gilt das Bedenkzeitfenster umgekehrt als Widerrufsfenster – innerhalb von 24–72 h ist der Übergang widerrufbar, danach endgültig.
- Widerruf löscht nicht die Historie (Revisionssicherheit geht vor Vergessen-Wollen an dieser Stelle); er beendet Wirkung und Zugriff. Gelöscht wird nur, was die Löschungsanordnung (AAV-08) ausdrücklich erfasst.
- **Delegationen:**
- Delegation ist immer **enge-Default**: Umfang, Dauer, Bereich müssen benannt sein; „Generalvollmacht im System" existiert nicht als Default, sondern nur als bewusst bestätigte, mit Warnung versehene Option.
- Delegationen sind **nicht weiterdelegierbar** (keine Subdelegation). Ein Verfügungsberechtigter kann keine Verfügungsberechtigten ernennen.
- Delegationen **ruhen automatisch** bei Ruhen des delegierenden Artefakts und **erlöschen** bei Erstarrung, Verfall oder Tod des Delegierenden – es sei denn, ein T3-Artefakt ordnet ausdrücklich ein Übergreifen in den Todesfall an (dann und nur dann: Fortgeltung als beschränkte Nachlass-Verfügung).
- **Pflicht zur Lebenslage-Prüfung:** Delegationen an Personen, mit denen ein erkennbarer Interessenkonflikt besteht (z. B. Erbe delegiert Zugriff auf Testament des künftigen Erblassers), lösen eine Warnpflicht des Guardians aus – keine Sperre, aber eine dokumentierte Nachfrage (Kohärenz mit IL-61 Interessenkonflikt-Regel).
- AAV-05: Mehrpersonenfreigaben
- **Entscheidung:** Mehrpersonenanforderungen werden über **Quoren** modelliert, nicht über geteilte Hoheit:
- **Quorum-Typen (geschlossen):**
- **Gegenzeichnung (2-Augen):** Übergang wirksam nur mit Bestätigung einer zweiten, benannten Rolle (z. B. Zeuge).
- **M-von-N-Quorum:** Für definierte Übergänge (z. B. Entsiegelung einer Verfügung) müssen M von N benannten Personen zustimmen. N≤7 (Bindung an die Erkenntnis aus GOV-20: größere Gremien erzeugen Patt- und Käuflichkeitsrisiken).
- **Kettengenehmigung:** Reihenfolgegebundene Zustimmung (z. B. erst Berufsträger, dann Hoheitsträger).
- **Quoren gelten pro Übergang, nicht pro Artefakt pauschal.** Der Zustandsvertrag benennt, welcher Übergang welches Quorum braucht. Default für Standardübergänge: keine Quore (Hoheitsträger allein). Quore sind Schutz, nicht Alltag – Alltagsquoren erzeugen Abstimmungsmüdigkeit und dann Leichtfertigkeit.
- **Verhinderungsregel:** Ist ein Quorumsmitglied dauerhaft verhindert (Tod, Ausfall), gilt eine im Vertrag vordefinierte Ersatzregel (benannter Stellvertreter oder Absenkung M-1, deklariert bei Vertragsstellung). Fehlt die Ersatzregel, greift **nicht** das System ein – sondern der dokumentierte Konfliktweg (AAV-07). Das System improvisiert niemals Mehrheiten.
- **Enthaltung zählt als Nicht-Zustimmung.** Es gibt kein „passiert automatisch nach Frist". Schweigen darf niemals Wirksamkeit erzeugen (Prinzip: Zustimmung ist ein Akt, kein Ausbleiben).
- **Zeugen sind keine Mitentscheider:** Gegenzeichnung bestätigt Identität/Vollzug, nicht inhaltliche Zustimmung. Die Vermischung beider Rollen ist ein klassischer Missbrauchsweg (Zeuge „stimmt zu") und ist verboten.
- 4. REVISIONSSICHERHEIT
- AAV-06: Historie, Beweis und der Verfassungsnotweg
- **Append-only-Historie:** Jede Änderung, jeder Übergang, jede Autorisierung, jeder Zugriff (auch lesend, durch jede Rolle inklusive ZONVAA-Personal) ist ein verketteter, manipulationssicherer Eintrag. Vergangenheit ist physikalisch nicht editierbar – nicht „per Policy verboten", sondern konstruktiv ausgeschlossen.
- **Beweisfähigkeit als Designziel:** Die Historie muss so geführt sein, dass sie in einem Rechtsstreit nach 30 Jahren rekonstruierbar und prüfbar ist: unabhängig verifizierbare Integrität (Hash-Verkettung o. ä.), Zeitnachweise, menschenlesbare Exporte (Offenformat IL-21). ZONVAA darf nicht der einzige sein, der die Historie lesen kann – sonst ist die Historie im Zweifel wertlos.
- **Zugriff auf die Historie:** Der Hoheitsträger sieht seine volle Historie. Externe (Erben, Gerichte) sehen sie nur im Rahmen der Verfügung oder gesetzlicher Pflichten. ZONVAA-Mitarbeitende sehen Historien nur im Vier-Augen-Verfahren mit nutzersehbarem Log (IL-30.3).
- **Der Verfassungsnotweg (Amtsverwahrung):** Es existiert genau ein Weg, auf dem ZONVAA ohne Hoheitsträger auf ein Artefakt einwirken darf: Gefahr im Verzug für Leib, Leben oder Kindeswohl (C1/Art. 3), oder gerichtliche Anordnung. Bedingungen, kumulativ:
- schriftliche Einzelfallbegründung durch zwei unabhängige Amtsverwahrer (Vier-Augen),
- zeitlich befristeter, minimalster Eingriff (lesen statt ändern, versiegeln statt löschen),
- automatische Benachrichtigung des Vertrauensrats (manipulationssichere Pipeline, GOV-30A),
- Benachrichtigung des Betroffenen, sobald dies die Gefahrenabwehr nicht gefährdet,
- Eintrag ins öffentliche aggregierte Rechenschaftsregister (IL-62) und ins permanente Register (GOV-31).
- Jeder andere Eingriff – auch „zum Schutz des Nutzers", auch „technisch nötig", auch auf Bitten von Angehörigen – ist Verfassungsbruch.
- 5. KONFLIKTE ZWISCHEN BETEILIGTEN
- AAV-07: Das Konfliktkaskaden-Modell
- **Entscheidung:** Konflikte sind Normalfälle (Erbe, Scheidung, Betreuung) und werden in einer festen Eskalationskaskade behandelt. Kernprinzip: **Das System entscheidet Konflikte nicht inhaltlich. Es hält Zustände fest, dokumentiert und leitet an legitime Instanzen weiter.**
- **Verbindliche Nebenregeln:**
- **Neutralitätsregel bei verbundenen Konten (IL-61):** Betrifft ein Konflikt mehrere ZONVAA-Nutzer (z. B. Erben, die beide Kunden sind), begleitet der Guardian jede Partei ausschließlich in deren Interesse und vermittelt nicht zwischen ihnen. Artefaktseitig gilt: Keine Partei erhält durch den Konflikt Zugriff auf Inhalte der anderen.
- **Kein Schiedsrichter-Guardian:** Der Guardian darf niemals Schlichtungssprüche sprechen. Seine Rolle endet bei Strukturieren, Dokumentieren, Weiterleiten. (Kohärenz zu IL-51: Navigator, nicht Berufsträger.)
- **Dokumentationspflicht:** Jeder Konflikt K2+ erzeugt einen Konfliktakt im Artefakt (wer, was, welcher Stand, welcher Pfad). Konflikte sind Teil der Artefaktgeschichte, keine Support-Tickets am Rand.
- 6. EINORDNUNG IN DIE GESAMTARCHITEKTUR
- AAV-08: Verortung in Constitution, Governance, Institution und Runtime
- **Entscheidung (Schichtenabbildung):**
- **Ableitungsregel für die Runtime:** Jede künftige Implementierung muss gegen eine **Eigenschaftsliste** (nicht gegen diesen Prosatext) geprüft werden. Die Eigenschaftsliste (Append-only, totale Ordnung, keine Fremdsperre, Verfalls-Defaults, Notweg-Bedingungen …) wird als eigenes, versioniertes Prüfartefakt (T4) geführt – Runtime-Änderungen, die eine Eigenschaft verletzen, sind per Definition Verfassungsverstoß und lösen GOV-31 aus.
- 7. LANGZEITSTABILITÄT UND MISSBRAUCHSSCHUTZ
- AAV-09: 50-Jahre-Festigkeit
- **Vertragsversionierung mit Ewigkeits-Lesbarkeit:** Zustandsverträge sind versioniert. Alte Versionen müssen von jeder künftigen Runtime **lesbar und ausführbar** bleiben (Kompatibilitätspflicht rückwärts, analog zur Beziehungsschicht IL-22). Ein Vertrag von 2026 muss im Jahr 2076 noch korrekt interpretiert werden. Migrationen dürfen Lesbarkeit schaffen, niemals Bedeutung ändern.
- **Semantische Stabilität:** Zustände, Rollen und Übergänge haben unveränderliche Bedeutungskerne (z. B. ERSTARRT bedeutet immer: unveränderbar, terminal). Erweiterungen sind erlaubt, Bedeutungsverschiebungen sind Verfassungsbruch. (Spiegelung der GOV-40-Ewigkeitslogik auf Artefaktebene.)
- **Sunset-Festigkeit:** Artefakte samt Verträgen und Historien sind vollständig im Nutzerexport (IL-21) enthalten – der Zustandsvertrag ist so spezifiziert, dass ein Nachfolgeträger oder der Nutzer selbst ihn **ohne ZONVAA-Software** interpretieren kann (deklarativ, dokumentiert, menschenlesbar neben maschinenlesbar).
- **Verfalls-Ökonomie:** Alles in diesem System altert: Freigaben (24 Monate), Delegationen (befristet), Quoren (Ersatzregeln), Artefakte selbst (Prüf- und Erneuerungszyklen für T1: Der Guardian erinnert, dass Lebensdokumente alle ~3–5 Jahre oder bei Lebensereignissen überprüft werden sollten). **Nichts darf durch Vergessen wirksam bleiben.** Vergessen ist der größte Feind langfristiger Rechtssicherheit.
- AAV-10: Missbrauchsschutz-Matrix
- **Entscheidung:** Die folgenden Angriffs-/Missbrauchswege sind benannt, und je ist der Abwehrmechanismus im Vertrag verankert (nicht in der Kulanz):
- Bewusst in Kauf genommene Nachteile
- Offene Punkte (Folge-ADRs)
- **Eigenschaftsliste als Prüfartefakt (T4):** formale, versionierte Aufstellung aller auditierbaren Eigenschaften dieses Vertrags – Voraussetzung für GOV-30-Audits.
- **Ereignisquellen-Register:** welche externen Ereignisse (Sterberegister, Volljährigkeit, Betreuungsanordnung) mit welcher Beweisqualität anerkannt werden – rechtslandabhängig, Verknüpfung zu LTS-31 (Instanzen).
- **Bedenkzeitfenster-Differenzierung:** 24–72 h ist eine Spanne; Festlegung je Typklasse und Übergang (mit Begründung; Suizidgefährdungs-Kontexte brauchen möglicherweise andere Fenster als Vollmachten).
- **Verknüpfung geteilter Artefakte** (Ehepaar/Familie): Referenzierungsmodell zwischen getrennten Hoheitsartefakten, ohne Hoheitsvermischung.
- **Wiederherstellungspfad nach Fehlereignis:** formaler Ablauf zur Rekonstruktion des rechtmäßigen Zustands aus der Historie (Fehlauslösung Todesfall etc.).
- **Quoren-UX:** Wie ein Laie ein M-von-N-Quorum versteht, einrichtet und durchläuft, ohne es aus Frustration zu umgehen – Zusammenarbeit mit Conversation Design.
- **Konfliktakt-Taxonomie:** standardisierte Typcodes für Konfliktgründe, damit Konflikte über Jahrzehnte statistisch auswertbar bleiben (Forschung, Sentinel, Vertrauensbericht).
- Schlussformel
- Der Artefakt- und Autorisierungszustandsvertrag ist die Stelle, an der ZONVAAs Verfassung **physisch** wird. Alles, was die Institution verspricht – Hoheit, Treuhand, Widerruf, Erstarrung, Rechenschaft – existiert nur dann wirklich, wenn es in Zuständen, Übergängen und Historien ausgedrückt ist, die kein Geschäftsdruck, kein Nachfolger und kein Angreifer still verändern kann.
- Die Architektur folgt einer einzigen obersten Regel, aus der alles andere abgeleitet ist:
- **Das System darf niemals mächtiger sein als der Vertrag – und der Vertrag gehört dem Menschen.**
- *Dieses Dokument ist Teil der C2-Vertrauensordnung. Änderungen nur nach GOV-40 bzw. dem C2-Verfahren. Berührt Vetodomänen 2 und 4 (GOV-22).*

## Ändern
- None

## Ablehnen
- None

## Konflikte
- None

## Betroffene Architektur
- INTERACTION
- INSTITUTION
- GOVERNANCE
- RUNTIME
- CROSS_LAYER
- constitution/constitution.md
- governance/charter.md
- institution/institution.md
- interaction/interaction.md
- knowledge/adr/ADR-0002-knowledge-system.md
- knowledge/mdr/MDR-0001-guardian-conversation-and-continuity.md

## Entscheidung erforderlich
- Confirm the non-binding ADOPT recommendation for proposal artifact-authorization-kimi-contract.
