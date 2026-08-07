# ZONVAA – Business Workspace Handover v1

Status: **KURATIERTE DOKUMENTARISCHE ÜBERGABE – KEIN ADR – KEINE GOVERNANCE- ODER ARCHITEKTURENTSCHEIDUNG**

## 1. Zweck dieser Übergabe

Dieses Dokument übergibt den gegenwärtig bestätigten ZONVAA-Projektstand an
einen neuen ChatGPT-Business-Workspace. Es ist eine Navigations- und
Arbeitsgrundlage. Es ersetzt weder das Repository noch ADRs, Governance,
kanonische Dokumente oder die Git-Historie. Bei Widerspruch gilt die jeweils
zuständige kanonische Repository-Quelle.

Die Übergabe trennt sechs Aussagearten:

- **KANONISCH / RATIFIZIERT:** durch zuständige Verfassungs-, MDR-, ADR- oder
  Governance-Quellen getragen.
- **BESTÄTIGTER IMPLEMENTIERUNGSSTAND:** durch Code, Tests und aktuellen
  Produktstatus nachgewiesen.
- **NICHT NORMATIVER FORSCHUNGSSTAND:** dokumentierte Forschung ohne
  Architektur- oder Produktfreigabe.
- **PRODUKTHYPOTHESE:** noch zu prüfende Produktidee.
- **OFFENE FRAGE:** im Repository nicht entschieden oder nicht belegt.
- **VERWORFEN / ÜBERHOLT:** historischer Stand ohne gegenwärtige
  Zuständigkeit.

## 2. ZONVAA in einem Satz

ZONVAA unterstützt Menschen dabei, wichtige Informationen, offene Fragen und
Entscheidungsgrundlagen verständlich zu ordnen, unter ihrer Kontrolle zu
halten und verantwortliche menschliche Entscheidungen vorzubereiten.

Diese Arbeitsbeschreibung behauptet weder, ZONVAA kenne die Bedeutung eines
Menschen, noch dass Bewahren immer richtig sei oder das System menschliche
Verantwortung übernehmen könne.

## 3. Gründervision und belegte Leitlinien

### Bestätigt

- ZONVAA ist breiter als Vorsorge und Nachlass. Die vorhandenen
  Foundation-Dokumente sprechen von persönlichem, familiärem, beruflichem und
  gesellschaftlichem Wissen; `Life Decisions` umfasst mehrere Vorsorge- und
  Lebensbereiche.
- Der Mensch bleibt Ursprung, kontrollierende und verantwortliche Instanz.
  ZONVAA ersetzt weder Menschen noch fachliche, moralische oder rechtliche
  Verantwortung.
- Nutzer bestimmen möglichst den Speicherort ihrer Originaldateien. ZONVAA
  ist kein zentraler Besitzer dieser Originale; Verarbeitung und Weitergabe
  benötigen ausdrückliche Freigaben.
- Nicht-Nutzung ist zulässig. Aufbewahrung, Wiederkehr oder Bindung dürfen
  nicht durch Schuldgefühl, künstliche Dringlichkeit oder Lock-in erzwungen
  werden. Löschung, Offboarding und ausdrücklich geregelte Übergabe bleiben
  unterscheidbar.
- Empfänger und Mitbetroffene werden nicht aus Beziehungen abgeleitet.
  Gemeinsame Sichtbarkeit verlangt begrenzte Freigabe, Berechtigung,
  Provenienz und Widerrufsmöglichkeit. ZONVAA entscheidet in Konflikten nicht,
  welche Person recht hat.
- Sprache darf Unsicherheit, Hypothesen und Widersprüche nicht in Tatsachen
  verwandeln. Für Guardian Conversation und Continuity ist MDR-0001 die
  verbindliche Detailquelle.

### Nicht als gegenwärtige Gründervision bestätigt

Das Repository bezeichnet die Vorsorgevollmacht als ersten produktnahen
Gesprächsfall und als ersten registrierten Kernbereich eines ruhenden
Kandidaten. Die konkrete Aussage „Vorsorgevollmacht war Stresstest, nicht
Produktziel“ ist im versionierten Repository jedoch nicht belegt und wird
deshalb nicht als Entscheidung übernommen. Ebenso ist „Sprache ist
ausschließlich Darstellung“ gegenwärtig nur ein Verfassungskern des **ruhenden**
Life-Domain-Model-Kandidaten, keine aktivierte globale Produktregel.

## 4. Fünf Ebenen

1. **Gründervision – Warum?** Vorhandene Vision-, Mission- und
   Guardian-Grundlagen beschreiben menschliche Selbstwirksamkeit,
   Nutzerhoheit, verantwortliche Entscheidungen und Wissenskontinuität. Ein
   konsolidiertes neues Dokument `foundational-vision-v1.md` existiert noch
   nicht.
2. **Kanonisches Glossar – Worüber?** P1 hat ausschließlich Struktur,
   Pflegevorschlag und Begriffskandidaten analysiert. Es existiert noch kein
   kanonisches Glossar und kein kanonisierter P1-Glossareintrag.
3. **Architektur – Wie?** ADRs und MDRs bestimmen Strukturen und Grenzen. Die
   B2-Verfassungsfamilie ist abgeschlossen und endet ohne Runtime.
4. **Governance – Wer darf was?** Governance-Artefakte trennen Gutachten,
   Architekturentscheidung, Ratifizierung, Implementierungsfreigabe,
   Implementierung sowie getrennte Commit- und Push-Freigaben.
5. **Implementierung – Wie wird es gebaut?** Code und Tests setzen nur
   ausdrücklich freigegebene Scopes um. Implementierung erzeugt keine eigene
   Architektur- oder Governancebefugnis.

Keine Ebene darf aus einer nachgeordneten Ebene rückwirkend neu definiert
werden. Insbesondere ist ein Glossar weder ADR noch Governance-Regel oder
Ontologie.

## 5. Architekturstand

### B2-Verfassungsfamilie

**KANONISCH / RATIFIZIERT und im jeweiligen Scope abgeschlossen:**

| Baustein | Aktueller Stand |
| --- | --- |
| ADR-0059 Data Corridor und Consent Boundary | ratifiziert, implementiert und validiert; direkter historischer Ratifizierungsnachweis bleibt Kategorie 3 |
| ADR-0060 Authority, Grant und Authorization | ratifiziert, freigegeben, implementiert und validiert |
| ADR-0061 Provider Identity und Capability Descriptor | ratifiziert, freigegeben, implementiert und validiert |
| ADR-0062 Provider Authorization | ratifiziert, freigegeben, implementiert und validiert |
| ADR-0063 Purpose Binding und UODL Mapping | ratifiziert, freigegeben, implementiert und validiert |
| ADR-0064/0064-A1 Governance Decision und Incident Evidence | ratifiziert, freigegeben, implementiert und validiert; geschlossene Taxonomien |
| ADR-0065 Capability Invocation | ratifiziert, freigegeben, implementiert und validiert; ausschließlich nicht ausführend |
| ADR-0066 Runtime Air Gap | ratifiziert, ausschließlich dokumentarisch freigegeben, deklaratorisch vollendet und validiert; bewusst keine technische Komponente |

Die Schutzkette lautet:

```text
B2 Data Corridor
→ B2 Authority und Grant
→ B2 Provider Identity
→ B2 Provider Authorization
→ B2 Purpose Binding
→ B2 UODL Mapping
→ B2 Capability Invocation
→ B2 Invocation Resolution Snapshot
→ CONTROLLED_STOP
→ ENDE
```

Der Schutzfluss ist monoton begrenzend. Purpose und UODL dürfen nur identisch
oder nachweisbar enger werden. Fehlende, unwirksame oder nicht vergleichbare
Bindungen enden fail closed. Eine positive Invocation Decision ist keine
Ausführungsfreigabe. ADR-0064/0064-A1 bilden eine getrennte Governance- und
Evidenzebene und ersetzen weder Authorization noch Invocation.

**Gesperrt:** B2 Runtime, Runtime Readiness, Invocation-zu-Runtime-Bridge,
automatische Provider-Ausführung, Tool-/API-/MCP-/Agent-Ausführung,
Observation innerhalb der B2-Kette, personenbezogene Verarbeitung sowie
Key-Custody- oder Inhaltszugriffsöffnung. ADR-0067 ist nicht begonnen.

## 6. Ruhende Kandidaten

### Guardian Accountability & Explanation

Registriert, nicht geplant, nicht implementiert und nicht freigegeben. Der
Kandidat könnte später vorhandene Evidenz lesbar projizieren, dürfte aber
nichts entscheiden oder als zweite Wahrheit erzeugen. Aktivierungsbedingungen
sind produktive B2-Runtime, reale Rechenschaftspflichten und ein dokumentierter
Aktivierungsbeschluss. Diese Voraussetzungen sind nicht erfüllt.

### Guardian Life Domain Model

Registriert, nicht geplant, nicht implementiert und nicht freigegeben. Der
Kandidat hält die mögliche spätere Trennung typisierter,
jurisdiktionstreuer Lebensobjekte von sprachlicher Darstellung fest. Er
definiert heute weder Rechtsobjekte, Datenmodell noch Produktworkflow.
Aktivierungsbedingungen sind produktive B2-Runtime, stabile
Conversation-Architektur und ein dokumentierter Aktivierungsbeschluss.

### Guardian Key Custody / Key Master

Nur als ruhender Kandidat und geschlossene Grenze in ADR-0066 dokumentiert.
Kein Key-Custody-, Entschlüsselungs- oder Inhaltszugriffspfad ist geöffnet.
Der Kandidat ist nicht aktiviert, nicht geplant und nicht implementiert.

## 7. Human Foundation Research

**BEWUSST NICHT WEITERVERFOLGT:** Im versionierten Repository existieren keine
Artefakte, welche die früher erwogene Folge

```text
Foundational Human Foundation
→ Stress Test
→ Human Journey Foundation
→ Transition Grammar Validation
→ Full Human Journey Validations
```

als abgeschlossenen Forschungsweg belegen. Die aktuelle Gründerklärung stellt
zusätzlich klar, dass diese Forschungsrichtung bewusst nicht nachgezogen oder
operationalisiert werden soll. Sie ist keine zu schließende Wissenslücke und
wird nicht als Projektstand oder notwendige Grundlage übernommen. Diese
Scope-Klarstellung ist kein Architektur-, Governance- oder Produktbeschluss.

Belegt sind stattdessen:

- `Guardian Research` als nicht abschließende, falsifizierende
  Forschungsregel für Autonomie, Würde, Selbstwirksamkeit, Transparenz und
  manipulative Muster;
- MDR-0001 als beschlossene Conversation- und Continuity-Quelle;
- produktnahe, typisierte Validierungen für Vorsorgevollmacht,
  Patientenverfügung und den Pflegefall in der Familie;
- eine anonymisierte Family-Care-Szenariomatrix und eine End-to-End-
  Referenzreise, die bestehende Verträge prüfen, aber keinen Produktservice und
  keine Freitextinterpretation erzeugen.

Diese Validierungen bestätigen kontrollierte Fragen, sichtbare Unknowns,
Hypothesen und Widersprüche, explizite Revisionen und Fachgrenzen. Sie sind
kein Beleg für eine allgemeine Theorie menschlicher Übergänge.

## 8. Human Transition Grammar

**VERWORFEN / NICHT WEITERVERFOLGT:** Eine „Human Transition Grammar v0.4“
sowie G1–G8 und Q1–Q7 sind im aktuellen versionierten Repository nicht
dokumentiert. Nach ausdrücklicher Gründerklärung sollen diese Richtung,
philosophische Meta-Modelle und eine operative Rolle „Product Philosopher“
nicht wieder aufgenommen werden. Der neue Workspace darf sie weder
rekonstruieren noch kanonisieren, implementieren, als Produktlogik verwenden
oder als fehlende Voraussetzung darstellen.

## 9. Produktverständnis

Verbindliches Arbeitsprinzip des Development Orchestrators:

> Innen maximal präzise. Außen maximal verständlich.

### Bestätigte produktnahe Bausteine

- Guardian Understanding und Clarification;
- Vorsorgevollmacht-Conversation, Journey, Professional-Review-Vorbereitung
  und UI-neutrale Experience;
- Patientenverfügungs-Preparation, Conversation, Journey,
  Professional-Review-Vorbereitung und UI-neutrale Experience;
- fachübergreifender Pflegefall in der Familie einschließlich Scenario
  Validation, End-to-End-Referenzreise und internem Review-Werkzeug;
- Guardian Answer Boundary, Source Chain, Classification und die begrenzten
  B1/B2/B3-Antwortpakete;
- B1 Read-only Provider Runtime und nachgelagerte, technisch begrenzte
  Betriebsnachweise; daraus folgt keine B2-Runtime.

### Dokumentierte Themenbereiche, aber keine allein daraus beschlossenen Produkte

`Life Decisions` nennt Testament und Nachlass, Vorsorgevollmacht,
Patientenverfügung, Betreuungsverfügung, Notfallzuständigkeiten,
Familienvermögen, Immobilien- und Unternehmensnachfolge, digitale Konten und
Nachlass, persönliche Wünsche und Familienwissen. Erinnerungen, Geschichten,
Werte und Weitergabe erscheinen in Vision-/Continuity-Quellen.

### Aktuell weiterverfolgte Produkthypothesen

Die aktuelle Gründerklärung hält einen für normale Menschen verständlichen
**Notfallordner** als möglichen einfachen und wirtschaftlich relevanten
Einstieg offen. Er fragt in Alltagssprache, was wichtige Menschen wissen
sollen, wenn etwas passiert. Denkbare Inhalte sind persönliche Wünsche,
Ansprechpartner, Vorsorgeinformationen, Vollmacht, Patientenverfügung,
Beerdigungswünsche, persönliche Hinweise, Familienwissen und relevante
Dokumentzusammenhänge. Dies ist weder ein fertiges Produkt noch ein
beschlossener Funktionsumfang. Repositoryseitig bestätigt sind nur einzelne
angrenzende Life-Decisions-Bausteine und Themenbereiche.

**„ZONVAA für das Leben“** bleibt Forschungs- und Produkthypothese. Die
menschliche Beobachtung kann plausibel sein; nicht validiert sind ein
eigenständiger Produktbedarf, ausreichende Differenzierung, regelmäßige
Nutzung, Zahlungsbereitschaft und die Plausibilität eines Jahresabos.

Konkrete Musikfunktionen und weitere persönliche Inhalte werden nicht aus
Beispielen zu Produktumfang oder Datenmodell erhoben.

## 10. Drei Nutzungsperspektiven

**PRODUKTHYPOTHESE / EINFACHE AUSSENSICHT:**

- **Heute:** mögliche Unterstützung im normalen Leben;
- **Wenn etwas passiert:** Vorsorge-, Notfall- und Orientierungssituationen;
- **Für später:** Erinnerungen, Familienwissen, Wünsche und ausdrücklich
  geregelte Weitergabe.

Diese Perspektiven sind keine drei beschlossenen Produkte und dürfen nicht zu
technischen Silos, Architekturgrenzen oder automatischen Datenklassen werden.
Sie sind eine mögliche verständliche Orientierung für unterschiedliche
menschliche Nutzungssituationen. Ihre Tragfähigkeit ist nicht validiert.

## 11. Marketing- und Markenhypothesen

**Spiegel → Frage → Lösung** ist eine aktuelle Marketinghypothese: zuerst eine
reale menschliche Situation sichtbar machen, dann zur eigenen Reflexion
einladen und erst danach ZONVAA als mögliche einfache Unterstützung zeigen.
Sie ist kein Markenbeschluss und keine Gesprächs- oder Produktarchitektur.
Unzulässig bleiben emotionale Manipulation, behauptete Gedanken anderer
Menschen, Beziehungsbewertung, Kommunikationsdruck und künstliche Angst.

Die Arbeitsformulierung **„Für die Dinge im Leben, über die wir viel zu selten
sprechen.“** ist ausschließlich eine mögliche Marken- und
Kommunikationsrichtung. Sie ist nicht beschlossen.

Repositoryseitig belegt bleibt der davon getrennte Conversation-Grundsatz:
zuerst zuhören, knapp spiegeln und Verständnis zeigen, erst danach höchstens
eine natürliche Richtung sowie später Orientierung oder Werkzeuge anbieten.

### Wirtschaftliche Realität

ZONVAA muss langfristig wirtschaftlich tragfähig sein. Eine emotional
plausible oder resonante Idee ist deshalb noch kein Produkt. Forschung und
Kundentests müssen emotionale Resonanz, tatsächlichen Bedarf, wiederkehrenden
Nutzen und Zahlungsbereitschaft getrennt prüfen. Diese Übergabe erfindet weder
Marktgrößen noch Preise, Umsatzprognosen oder Abo-Eignung.

## 12. Development Orchestrator

**BESTÄTIGTER IMPLEMENTIERUNGSSTAND:** Der Development Orchestrator v1 ist ein
internes Entwicklungswerkzeug, kein Teil der ZONVAA-Produkt-Runtime. Er
verarbeitet einen strukturierten Gründerauftrag über einen deterministischen
Plan, begrenzten Kontext, Research Agent, Review Agent und höchstens zwei
Research-/Review-Zyklen zu einem kompakten Decision Brief.

- **Research Agent:** trennt Evidenz, Befund, Unsicherheit und offene Fragen.
- **Review Agent:** bewertet Auftragserfüllung, Evidenz, Scope, Einfachheit und
  nötige Gründerentscheidungen; Ergebnis `ACCEPT`, `REVISE` oder `ESCALATE`.
- **Context Loader:** liest nur ausdrücklich erlaubte, zielrelevante
  Repository-Dateien und begrenzt Anzahl und Zeichenzahl.
- **Context Approval:** vorgeschlagene Quellen werden mit Grund, Umfang und
  Kürzungsstatus sichtbar; eine Freigabe gilt nur für den Run und nur für die
  ausdrücklich gewählte Teilmenge.
- **Cost/Usage Guard:** begrenzt Schritte und Iterationen, übernimmt nur
  verlässlich gemeldete Kosten und erfindet keine Preise.
- **Run Persistence:** speichert Request, Plan, Research, Review, Handover,
  Decision Brief und Usage lokal unter einer Run-ID.
- **Boundary Guard:** erlaubt Schreibzugriffe ausschließlich unter
  `internal/development-orchestrator/**`, blockiert Traversal und Symlink-
  Escapes und prüft nach Runs den Git-Status fail closed.
- **Modellkonfiguration:** Research und Review verwenden explizit `gpt-4.1`;
  kein stilles SDK-Defaultmodell und keine Fallback-Kaskade.
- **Validierungsstand:** Unit-, Contract-, Boundary-, CLI- und Offline-Eval-
  Nachweise sind versioniert. Das README bezeichnet Live-Verhalten weiterhin
  als credentialabhängigen separaten Smoke-Test; ein darüber hinausgehender
  Live-Erfolg ist nicht als kanonisches Repository-Artefakt belegt.

Es existiert keine Commit- oder Push-Automation.

## 13. MCP Front Door

Die dünne lokale STDIO-MCP-Schicht verwendet den vorhandenen Orchestrator und
dupliziert keine Agentenlogik.

Servername laut Integrationsdokumentation: `zonvaa-development-orchestrator`.

Exponierte Tools:

- `submit_work`
- `get_run_status`
- `get_decision_brief`
- `approve_context`
- `list_pending_decisions`

Es gibt keine Shell, kein Commit-/Push-Tool, keine generische Dateisystem-
freigabe und keine dynamische Agentenerzeugung. Context Approval ist
runspezifisch. Der lokale STDIO-Protokollpfad und die Tooloberfläche sind
durch Repository-Tests validiert. Die persönliche Clientregistrierung liegt
absichtlich außerhalb des Repositorys und wird hier nicht als portable
Workspace-Evidenz behauptet.

Browser-ChatGPT kann den lokalen Prozess nicht direkt erreichen. Eine
entfernte Verbindung würde einen gesondert autorisierten, authentifizierten
HTTPS-Streamable-HTTP-Endpunkt beziehungsweise eine ChatGPT-App-/Connector-
Registrierung benötigen. Hosting, Tunnel, Remote-Authentifizierung und diese
Anbindung sind nicht implementiert.

## 14. Zielarbeitsweise

```text
Nutzer / Gründer
→ zentrale strategische Gesprächsebene
→ Development Orchestrator
→ spezialisierte, begrenzte Agenten
→ Development Orchestrator
→ zentrale Gesprächsebene
→ Nutzer / Gründer
```

Der Gründer gibt Richtung, Ideen, Entscheidungen und Freigaben. Er soll nicht
Dispatcher, Copy/Paste-Schnittstelle oder technischer Run-Operator sein.
Interne Research-, Review- und zulässige Revisionsschritte benötigen keine
manuelle Zwischenübergabe.

## 15. Rollen

- **Institutionsgründer / Nutzer:** trifft tatsächliche institutionelle und
  fachliche Entscheidungen innerhalb der dokumentierten Zuständigkeit.
- **Chief Architect:** formuliert Architekturaufträge, bewertet Ergebnisse
  und bleibt Architekturentscheidungsinstanz.
- **Codex:** implementiert, testet und berichtet im ausdrücklich
  freigegebenen Scope; Commit und Push benötigen getrennte Freigaben.
- **Gutachterrolle / Reviewer:** analysiert und empfiehlt, erzeugt aber keine
  Architektur-, Ratifikations- oder Freigabewirkung.
- **Development Orchestrator:** koordiniert Research, Review, Revision,
  Evidenz und Decision Brief ohne Gründerentscheidungen zu übernehmen.
- **Research Agent / Review Agent:** arbeiten in ihren im Orchestrator-README
  definierten Rollen.

Eine eigenständige Rolle „Product Philosopher“ ist im aktuellen Repository
nicht dokumentiert und wird nicht eingeführt.

## 16. Arbeitsprinzipien

- falsifizierend statt bestätigungsorientiert forschen;
- Primärquellen und kanonische Repository-Quellen bevorzugen;
- Fakten, Interpretation, Hypothese, Entscheidung und unbekannten Stand
  sichtbar trennen;
- keine Quellen, Gefühle, Nachweise, Rechenschaft oder Repository-Zustände
  erfinden;
- keine Architektur aus einer Produktidee und keine Produktentscheidung aus
  Forschung ableiten;
- Scope nicht automatisch erweitern;
- den Gründer nur bei echten Richtungs-, Freigabe-, Sicherheits- oder
  Konfliktentscheidungen einbinden;
- externe Kontextübertragung minimieren und runspezifisch freigeben;
- bei fehlender Evidence fail closed arbeiten;
- unnötige menschliche Koordination vermeiden, ohne menschliche
  Entscheidungshoheit zu ersetzen.

## 17. Git- und Repository-Stand

- Repository: `/Users/michaelgiese/Documents/ZONVAA/zonvaa-builder-reset-v2`
- Branch: `builder-reset-v2`
- HEAD vor Erstellung: `02ce907f49b4dc981056e2868dad32cf047fcd3c`
- Remote-HEAD vor Erstellung: `02ce907f49b4dc981056e2868dad32cf047fcd3c`
- Ahead/Behind vor Erstellung: `0/0`

Der historische Recovery-Stash `stash@{0}` mit OID
`f1e6f58aedf31d8617c83b68f9ea899c9aae9e43` ist ein erhaltener,
nichtkanonischer Recovery-Stand einer partiellen ADR-0064-Implementierung. Er
ist keine Arbeitsgrundlage dieser Übergabe.

## 18. Was der neue Workspace nicht tun darf

- ZONVAA trotz zuständiger Grundlagen neu definieren;
- Vorsorgevollmacht aus dem ersten produktnahen Fall zum Gesamtprodukt machen;
- nicht belegte Human-Foundation- oder Transition-Grammar-Modelle
  rekonstruieren oder implementieren;
- Forschungsbegriffe oder P1-Kandidaten kanonisieren;
- ruhende Kandidaten aktivieren;
- B2 Runtime, Runtime Readiness oder ADR-0067 öffnen;
- personenbezogene Inhalte als ZONVAA-Besitz behandeln;
- technische Repräsentation mit menschlicher Bedeutung gleichsetzen;
- Forschung als Entscheidung oder plausible Erzählung als Validierung
  darstellen;
- den Gründer wieder zur manuellen Agenten- oder Kontextschnittstelle machen;
- Commit, Push, Kontextübertragung oder institutionelle Wirkung still
  autorisieren.

## 19. Offene nächste Schritte

Repositoryseitig belastbar offen sind:

1. Eine konsolidierte Gründervision und ein kanonisches Glossar benötigen
   eigene spätere Aufträge; P1 hat nur ihre Struktur vorbereitet.
2. Die persönliche lokale MCP-Registrierung ist nicht Teil des Repositorys.
   Für einen neuen Workspace muss die tatsächlich verfügbare Tooloberfläche
   geprüft werden, bevor eine direkte Orchestrator-Nutzung behauptet wird.
3. Eine ChatGPT-Browser-/Business-Workspace-Verbindung zum lokalen MCP ist
   nicht implementiert. Ein Secure MCP Tunnel ist weder beschlossen noch
   gebaut. ChatGPT Developer Mode, Hosting, Authentifizierung und Connector-
   Einrichtung dürfen nur anhand aktueller Produktverfügbarkeit und mit
   gesonderter Sicherheitsentscheidung verfolgt werden.
4. ADR-0067 und jede neue Verfassungsfamilie benötigen einen neuen
   institutionellen Beschluss, eigene Governance und eigene Architektur. Sie
   folgen nicht automatisch.

Die drei Nutzungsperspektiven, die Marketing- und Markenrichtung, „ZONVAA für
das Leben“ und ein Notfallordner bleiben ausdrücklich offene, aktuell
weiterverfolgte Produkt- beziehungsweise Kommunikationshypothesen. Die
Gründerklärung hält ihren Prüfstatus fest, ersetzt aber weder Research noch
Kundenvalidierung oder Produktentscheidung.

## 20. Quellenindex

| Quelle | Status / Zuständigkeit | Relevanz |
| --- | --- | --- |
| [`AGENTS.md`](../../AGENTS.md) | kanonischer Arbeitskontext | Rollen, Repository- und Git-Arbeitsweise |
| [`foundation/vision.md`](../../foundation/vision.md), [`mission.md`](../../foundation/mission.md), [`values.md`](../../foundation/values.md), [`manifest.md`](../../foundation/manifest.md) | vorhandene Foundation-Quellen; teilweise breiter oder älter als der aktuelle Fachstand | Vision, Mission, Werte; nicht als neue konsolidierte Gründervision umgedeutet |
| [`MDR-0001`](../mdr/MDR-0001-guardian-conversation-and-continuity.md) | beschlossen; alleinige Detailquelle für Conversation und Continuity | Guardian, Autorisierung, Nutzerhoheit, Nicht-Nutzung, Übergabe und Konfliktgrenzen |
| [`Guardian Philosophy`](../guardian/philosophy.md) | verbindliche nutzergerichtete Grundlage | Selbstwirksamkeit, sichtbarer Guardian, S-V-N-P und Manipulationsverbot |
| [`Guardian Research`](../guardian/guardian_research.md) | Forschungsgrundlage | falsifizierende Arbeitsweise und Evidenzgrenzen |
| [`Life Decisions`](life-decisions.md) | aktueller fachlicher Produktbereich | bestätigte produktnahe Fälle, Themen- und Datenprinzipien |
| [`Current Product Status`](current-product-status.md) | kanonischer aktueller Produktstatus | Implementierungsinventar und gegenwärtige Grenzen |
| [`B2 Completion Report`](../../governance/b2-constitution-v1.0-completion-report.md) | evidenzbasierter Abschlussbericht, kein ADR | konsolidierter Status ADR-0059 bis ADR-0066 |
| [`B2 Readiness`](../../governance/b2-readiness-statement.md), [`Architecture Map`](../../governance/architecture-map.md), [`Future B2 Package Map`](../../governance/future-b2-package-map.md) | Governance-/Statusdokumentation | Gate-Historie, Grenzen, ruhende Kandidaten und kein automatischer Folgeschritt |
| [`Institutional Approval Process`](../../governance/institutional-approval-process.md) | kanonischer Prozess | getrennte institutionelle Schritte und Rollen |
| [`Accountability Candidate`](../../governance/guardian-accountability-explanation-candidate.md), [`Life Domain Candidate`](../../governance/guardian-life-domain-model-candidate.md), [`ADR-0066`](../adr/ADR-0066-guardian-b2-runtime-air-gap-constitution-v1.md) | registrierte ruhende Kandidaten bzw. ratifizierte Air-Gap-Verfassung | Kandidatenstatus und Aktivierungsgrenzen |
| [`P1 Documentation Structure`](p1-foundational-documentation-structure-proposal.md), [`P1 Glossary Governance`](p1-canonical-glossary-governance-proposal.md), [`P1 Entry/Prioritization`](p1-canonical-glossary-entry-and-prioritization-proposal.md) | ausdrücklich nicht normative Vorschläge | korrekter Glossarstatus und vorgesehene Dokumentationsgrenzen |
| [`Development Orchestrator README`](../../internal/development-orchestrator/README.md) | Implementierungsdokumentation | Workflow, Agenten, Boundary, Modelle, Runs und MCP |
| [`Single Front Door Assessment`](../../internal/development-orchestrator/docs/single-front-door-integration-assessment.md) | nicht normative Integrationsbewertung | lokaler MCP-Pfad und fehlende Browser-/Remote-Verbindung |
