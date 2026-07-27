# ZONVAA Work Plans

Für längere Arbeitspakete wird dieser Plan während der Umsetzung aktualisiert.
Er dokumentiert bestätigte Fakten und ersetzt keine ADR.

## Abgeschlossener Plan: Typisierter Artefakt- und Autorisierungszustandsvertrag

### Ziel und Nicht-Ziele

Die bestätigte Chief-Architect-Entscheidung aus
`workflow-81d7ba505f25f885` als kleinen, versionierten und typisierten
Artefakt-/Autorisierungsvertrag integrieren. Gespräch und Handlung,
Hoheitsträger und Beteiligte, Zustandswechsel, Autorisierung sowie
datenklassengerechte Historien bleiben explizit getrennt. Keine UI,
Persistenz, Kryptografie, Rechtswirkungsbehauptung, Notfallautomatik oder
fachliche Workflow-Änderung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `9e84c51` war erfolgreich; der Arbeitsbaum
  enthält ausschließlich den bestätigten, uncommittierten Architecture
  Workflow.
- MDR-0001 und Interaction 1.1 definieren Artefakt- und
  Autorisierungsgrenzen, aber noch kein ausführbares typisiertes
  Zustandsmodell.
- Runtime und Mission Context weisen Constitution, Governance, Institution
  und Interaction nach; ein eigener Artefaktvertrags-Nachweis fehlt.
- `DocumentArtifact` ist ausschließlich ein Schreibplan-Objekt und darf nicht
  zum fachlichen Artefaktzustandsmodell erweitert werden.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Workflow-Entscheidungen, bestehende Schichten und Tests
  prüfen.
- [x] Typisierte unveränderliche Zustands-, Autorisierungs- und
  Historienmodelle erstellen.
- [x] Versionierten Vertrag laden und in Runtime/Preflight nachweisen.
- [x] ADR und abgeleitete Interaction-Dokumentation konsistent aktualisieren.
- [x] Fokussierte und vollständige Tests, Doctor und Diff prüfen.
- [x] JSON-/Markdown-Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Der Vertrag wird als eigene technische Komponente unterhalb der bestehenden
  Interaction-Grenze modelliert; er bildet keine neue Architekturschicht.
- Das bestehende `execution.DocumentArtifact` bleibt unverändert, da es
  ausschließlich sichere Dokumenterzeugung beschreibt.
- C2-Eigenschaften und C3-Ausführungsparameter werden im Modell explizit
  getrennt; konkrete Werte bleiben offen.

### Risiken und Teststrategie

- Zustandsnamen dürfen keine rechtliche Wirksamkeit behaupten.
- Historienklassifikation darf weder pauschale Unlöschbarkeit noch stille
  Löschung erlauben.
- Tests prüfen stabile Enums, Unveränderlichkeit, eindeutige IDs,
  Hoheitsträger, Autorisierungs- und Übergangsinvarianten, Loader-Integrität,
  Runtime- und Preflight-Nachweis sowie bestehende Rückwärtskompatibilität.

### Abweichungen und Abschlusszustand

Der unterbrochene Zwischenstand enthielt bereits Paketgerüst, Vertrag und
Plan, aber noch keine Runtime-/Preflight-Integration, ADR oder Tests. Bei der
Prüfung wurde zusätzlich korrigiert, dass ein späterer Widerruf eine zuvor
ordnungsgemäß autorisierte historische Transition nicht nachträglich
ungültig machen darf.

Der Vertrag ist nun als unveränderliches Python-3.9-Modell, versionierte
Markdown-Quelle, Loader, Runtime-Kontext und Mission-Context-1.4-Nachweis
vollständig. Er führt keine Transition aus. Bestehende explizite Test-Runtimes
wurden ausschließlich um denselben kanonischen Vertragskontext ergänzt.
479 Tests bestehen; Doctor, Preflight und `git diff --check` sind erfolgreich.

## Abgeschlossener Plan: Architecture Workflow Orchestrator

### Ziel und Nicht-Ziele

Den Architecture Integrator als verbindlichen Standardprozess für einen oder
mehrere Entwürfe orchestrieren: Proposal, Analyse, Entscheidungsvorlage,
bestätigte Chief-Architect-Entscheidung und eigenständiger Codex-Auftrag
werden getrennt und reproduzierbar persistiert. Keine automatische
Architekturentscheidung, Repository-Integration, Produktänderung, Ausführung,
Commit-Erzeugung oder externe KI.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `b4db8a5` war erfolgreich.
- ADR-0028 und das Paket `architecture_integrator` definieren typisierte,
  unveränderliche Proposals, Analysen, Entscheidungen und Prompt-Erzeugung.
- Die bestehende CLI kann genau ein Proposal analysieren und aus einer
  passenden bestätigten Entscheidung einen Prompt erzeugen.
- Es gibt noch keinen mehrstufigen Workflow, keinen Multi-Proposal-Lauf und
  keine getrennte, reproduzierbare Workflow-Ablage.

### Arbeitsschritte und Fortschritt

- [x] Integrator-, IO-, Prompt-, CLI-, ADR- und Testverträge vollständig prüfen.
- [x] Unveränderlichen Workflow-Status und atomare lokale Ablage
  implementieren.
- [x] Multi-Proposal-Orchestrierung und Chief-Decision-Gate ergänzen.
- [x] CLI-Unterbefehle, ADR und Dokumentation aktualisieren.
- [x] Fokussierte und vollständige Tests, Doctor und Diff prüfen.
- [x] Handover erzeugen und vorgegebenen Commit vorbereiten.

### Entscheidungen und Begründungen

- Der Workflow erweitert den vorhandenen Integrator und dupliziert weder
  Analyse noch Prompt-Erzeugung.
- Workflow-Artefakte liegen ausschließlich unter
  `knowledge/architecture_workflows/<workflow_id>/` und bleiben von
  verbindlichen MDRs und ADRs getrennt.
- Workflow-IDs entstehen deterministisch aus den kanonischen Proposal-Inhalten;
  Proposal-Reihenfolge wird über stabile IDs kanonisiert.
- Der Prozess wartet über persistierten Zustand: Ohne je ein passendes
  Chief-Decision-Objekt pro Proposal gibt es keinen Codex-Prompt.

### Risiken und Teststrategie

- Eine strukturvalide Entscheidung authentifiziert weiterhin nicht die reale
  Identität des Chief Architect.
- Workflow-Artefakte sind Nachweise und keine Architekturpublikation.
- Tests prüfen Gesamtfluss, mehrere Proposals, fehlende Entscheidungen,
  deterministische IDs/Artefakte, atomare Ablage und unveränderte
  Architekturquellen.

### Abweichungen und Abschlusszustand

Der Workflow orchestriert beliebig viele eindeutig identifizierte Proposals
über den bestehenden Integrator, persistiert alle Stufen getrennt und erzeugt
erst nach je einer passenden Chief-Architect-Entscheidung einen gemeinsamen
Codex-Auftrag. Workflow-IDs binden Proposal- und Analyseinhalt einschließlich
Architekturquellen-Hashes; identische Läufe werden wiederaufgenommen.
Write-once-Artefakte, kanonische Pfade und Symlink-Grenzen verhindern stille
Überschreibung. Der Workflow startet weder Codex noch Tests, Commit oder
externe Dienste. 450 Tests bestehen; Doctor und `git diff --check` sind
erfolgreich.

## Abgeschlossener Plan: Architecture Integrator Agent

### Ziel und Nicht-Ziele

Einen deterministischen, rein beratenden Architecture Integrator einführen,
der den verbindlichen Architekturkontext priorisiert lädt, externe Entwürfe
nachvollziehbar vergleicht, eine nicht bindende Entscheidungsvorlage erzeugt
und nur aus einer expliziten Chief-Architect-Entscheidung einen
eigenständigen Codex-Auftrag ableitet. Keine automatische Freigabe, keine
externen KI-Aufrufe, keine Produkt- oder Workflow-Änderung und keine
Repository-Mutation durch die Analyse.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `449d12b` war erfolgreich.
- Runtime lädt Constitution, Governance, Institution, Interaction und die
  vorhandenen Knowledge-Bereiche; `knowledge/mdr` wird noch nicht durch den
  KnowledgeManager entdeckt.
- MDR-0001 ist verbindliche Detailquelle, ADR-0023/0024/0026 sind historisch.
- Es gibt keinen Integrator, kein typisiertes Proposal-/Analyse-/
  Chief-Decision-Modell und keinen Architecture-CLI-Zweig.
- Handover, atomare lokale Ausgabe und unveränderliche Dataclass-/Enum-Muster
  sind vorhanden und werden wiederverwendet.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Runtime, KnowledgeManager, Normquellen, CLI und Testkonventionen
  prüfen.
- [x] Typisierte Modelle, Kontext-Lader und deterministische Analyse
  implementieren.
- [x] Entscheidungsvorlage und bestätigungsgebundene Prompt-Erzeugung
  ergänzen.
- [x] CLI, ADR, Übersicht und Beispiele dokumentieren.
- [x] Fokussierte und vollständige Tests, Doctor und Diff prüfen.
- [x] Handover erzeugen und vorgegebenen Commit vorbereiten.

### Entscheidungen und Begründungen

- RuntimeManager und KnowledgeManager bleiben Quellen des geladenen Zustands;
  der Integrator führt keinen parallelen Architekturspeicher ein.
- Normative Priorität wird als explizite, stabile Enum-Reihenfolge modelliert.
- Konflikte werden nur aus nachvollziehbarer textlicher Gegenläufigkeit
  markiert und niemals automatisch aufgelöst; nicht belegbare Beziehungen
  bleiben Ergänzung oder offene Frage.
- Analyse bleibt read-only und gibt deterministisches JSON sowie eine kompakte
  Vorlage aus.

### Risiken und Teststrategie

- Lexikalisch deterministische Analyse ersetzt keine menschliche semantische
  Architekturentscheidung; geringe Konfidenz und offene Fragen müssen dies
  sichtbar machen.
- Historische ADRs dürfen Kontext liefern, aber keine aktuelle Normwirkung
  erhalten.
- Tests prüfen Priorität, Hashes, Konflikt/Additiv/Redundanz, Unveränderlichkeit,
  fehlende Quellen, Prompt-Gate, Determinismus und unveränderte Quelldateien.

### Abweichungen und Abschlusszustand

Der Architecture Integrator lädt C1, MDR, C2, Spezifikationen, aktuelle ADRs,
C3, historische ADRs und den letzten Handover in stabiler Priorität. Er
erzeugt ausschließlich eine nicht bindende, nachvollziehbare Analyse und
eine kompakte Entscheidungsvorlage. Ein eigenständiger Codex-Auftrag entsteht
nur aus einem validierten Chief-Architect-Entscheidungsobjekt. MDR-0001 bleibt
priorisierte Detailquelle; Analyse und CLI verändern keine Architekturquelle.
442 Tests bestehen, Doctor und `git diff --check` sind erfolgreich.

## Abgeschlossener Plan: Guardian Master Decision Record

### Ziel und Nicht-Ziele

Gemini Conversation/Interaction und Kimi Guardian Continuity in
`MDR-0001` vollständig zu einem einzigen verbindlichen Architekturstand
konsolidieren. Redundanzen zusammenführen, Bedeutungen erhalten und mögliche
Spannungen ausdrücklich auflösen. Keine Produktcode-, Runtime-, UI-,
Workflow-, Persistenz- oder Sicherheitsimplementierung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `8ff19cd` war erfolgreich.
- Der Gemini-Entwurf ist in ADR-0026 und `interaction/interaction.md`
  verarbeitet, aber nicht vollständig als alleinige Quelle erhalten.
- Der Kimi-Entwurf ist als `knowledge/guardian/continuity.md` und
  Guardian-Foundation-Querverweis dokumentiert.
- ADR-0023, ADR-0024 und ADR-0026 sowie Guardian- und Interaction-Dokumente
  enthalten überlappende verbindliche Aussagen.
- Ein MDR-Verzeichnis und Master Decision Record existieren noch nicht.

### Arbeitsschritte und Fortschritt

- [x] Gemini-, Kimi-, Guardian-, Interaction-, Institution-, Governance- und
  Constitution-Quellen vollständig prüfen.
- [x] MDR-0001 vollständig und mit Herkunftsmatrix erstellen.
- [x] Widersprüche und Spannungen dokumentieren, ohne neue Regeln zu
  erfinden.
- [x] Constitution, ADR-Status und Querverweise auf MDR-0001 umstellen.
- [x] Dokumentationsverträge und betroffene Tests konsistent aktualisieren.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover erzeugen und vorgegebenen Commit vorbereiten.

### Entscheidungen und Begründungen

- MDR-0001 wird einzige verbindliche Detailquelle für Guardian Conversation
  und Continuity.
- Historische ADRs und Guardian-Dateien bleiben als Herkunftsnachweis
  erhalten, verlieren aber eigenständige normative Wirkung.
- C1-Schutzziele und Institution-Garantien bleiben höherrangige Grenzen;
  ihre Detailauslegung für diesen Bereich verweist auf MDR-0001.
- Der technische Interaction-Vertrag bleibt Runtime-Nachweis, wird aber als
  abgeleitete Projektion des MDR gekennzeichnet.

### Risiken und Teststrategie

- Die Konsolidierung darf keine Quelle verkürzen oder durch stärkere
  Formulierungen neue Implementierungsversprechen erzeugen.
- Portabilität und Löschung müssen Nutzerhoheit, gebundene Nachweise und
  ausdrücklich autorisiertes digitales Vermächtnis gleichzeitig erhalten.
- Dokumentstatus, Versionen, Loader-Integrität und alle bestehenden Tests
  werden geprüft; Produktcode bleibt unverändert.

### Abweichungen und Abschlusszustand

MDR-0001 konsolidiert Gemini Conversation/Interaction und Kimi Guardian
Continuity vollständig, dokumentiert fünf Spannungsfelder als aufgelöst und
ist nun die einzige verbindliche Detailquelle. ADR-0023, ADR-0024 und
ADR-0026 bleiben historische Nachweise; Interaction 1.1 ist eine abgeleitete
Runtime-Projektion. Constitution 2.1, Institution 1.3 und Governance 1.1
verweisen ohne Regelduplikation auf den MDR. Es wurde keine Produkt- oder
Runtime-Logik implementiert. 425 Tests bestehen; Doctor und
`git diff --check` sind erfolgreich.

## Abgeschlossener Plan: Governance Architecture

### Ziel und Nicht-Ziele

Die bestehende Constitution in eine klare Normhierarchie aus C1
Schutzverfassung, C2 Governance Charter und C3 operativen Regeln überführen.
Governance-Organe, begrenzte Vetorechte, Audits, Eskalationen,
Nutzerbeteiligung und Trägerschutz verbindlich definieren. Keine konkrete
Rechtsform, Organbesetzung, Quote, Amtszeit, Frist oder technische
Audit-/Whistleblower-Plattform implementieren.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `2a76fc6` war erfolgreich.
- Constitution 1.4 vermischt dauerhafte Garantien mit Rollen,
  Arbeitsabläufen, Runtime- und Kommunikationsregeln.
- Institution 1.1 enthält Governance als langfristige Garantie, aber keine
  Organe oder Prüfmechanismen.
- Guardian Foundation und Interaction 1.0 schützen Nutzerhoheit,
  Kontinuität, Offboarding und Autorisierung.
- Es existiert keine konkurrierende Governance Charter oder
  Governance-Runtime.

### Arbeitsschritte und Fortschritt

- [x] Constitution, Guardian, Institution, Interaction, Runtime und ADRs prüfen.
- [x] C1, C2 und C3 ohne Regelverlust trennen und versionieren.
- [x] Typisierten Governance-Vertrag und strukturellen Loader erstellen.
- [x] Runtime und Mission Context minimal integrieren.
- [x] ADR, Modell-, Loader-, Runtime- und Preflight-Tests ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- C1 wird auf dauerhafte Negativ-Garantien und Schutzziele reduziert.
- Bestehende Arbeits-, Runtime- und Kommunikationsregeln bleiben in einem
  versionierten C3-Register erhalten, statt gelöscht oder in C1 versteinert
  zu werden.
- C2 operationalisiert die bestehende Institution-Governance-Garantie und
  bildet keine zweite Institution.
- Runtime hält einen unveränderlichen Governance-Kontext; konkrete Organe
  oder Verfahren werden nicht implementiert.

### Risiken und Teststrategie

- Die Entflechtung darf keine bestehende Arbeits- oder Guardian-Regel
  stillschweigend verlieren.
- Gesellschafts-, Haftungs-, Insolvenz- und Auditwirkung bleiben ohne
  fachliche Prüfung ausdrücklich unbestätigt.
- Exakte Normstufen, Schutzziele, Organe, Vetodomänen, Hashes,
  Boot-Reihenfolge und Preflight-Integrität werden deterministisch getestet.
- Operative Workflows erhalten keine Governance-Inhalte oder neuen Rechte.

### Abweichungen und Abschlusszustand

Constitution 2.0 enthält ausschließlich C1-Negativ-Garantien und
Schutzziele. Governance Charter 1.0 definiert C2; das C3-Register erhält
bestehende operative Regeln in ihren bisherigen Quellen. Institution 1.2,
Runtime und Mission Context 1.3 weisen Governance strukturell nach, ohne
Organe oder Rechtswirkung vorzutäuschen. 419 Tests bestehen; Doctor und
`git diff --check` sind erfolgreich. Konkrete Rechtsform, Besetzung,
Quoren, Fristen, Audits und technische Hinweisgeberkanäle bleiben offen.

## Abgeschlossener Plan: Conversation & Interaction Architecture

### Ziel und Nicht-Ziele

Eine verbindliche, versionierte Conversation/Interaction-Ebene zwischen
Guardian und Institution etablieren. Sie definiert Gesprächsraum,
Institution Board, Artefakt- und Autorisierungsgrenzen sowie
Mehrparteien-, Inaktivitäts-, Offboarding- und Systemgrenzen. Keine UI,
Conversation Runtime, Kryptografie, externe Aktion oder fachliche
Workflow-Änderung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `8e2aa5f` war erfolgreich.
- Guardian Foundation und ADR-0023/0024 definieren Haltung und sichtbares
  Gespräch, aber keinen typisierten Interaction-Vertrag.
- Institution 1.0 definiert langfristige Garantien und Runtime weist deren
  Integrität im Mission Context 1.1 nach.
- Institution Board, Artefaktübergang, Autorisierungsgrenze und gemeinsame
  Entscheidungsräume sind noch nicht als eigene Ebene gebunden.
- Es existiert keine UI- oder Conversation-Engine-Implementierung, die
  erweitert werden könnte.

### Arbeitsschritte und Fortschritt

- [x] Primärquelle, Guardian Foundation, Institution und Constitution prüfen.
- [x] Kanonischen Interaction-Vertrag und typisiertes Modell erstellen.
- [x] Institution-Vertrag und Schichtenfolge widerspruchsfrei aktualisieren.
- [x] Runtime und Mission Context minimal integrieren.
- [x] ADR, Modell-, Loader-, Runtime- und Preflight-Tests ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Conversation/Interaction ist eine Vertrags- und Grenzebene, keine
  ausführende Conversation Engine oder UI.
- Das Institution Board ist die strukturierte Handlungsebene der Interaktion,
  nicht der Institution Layer und keine zweite Guardian-Persona.
- Artefakte vermitteln bestätigten Kontext, aber weder Vollmacht noch
  fachliche Wirksamkeit.
- Runtime bleibt Single Source of Truth und lädt einen unveränderlichen
  Interaction-Kontext zusätzlich zum Institution-Kontext.

### Risiken und Teststrategie

- Die Begriffe Board, Safe und Graph dürfen keine nicht implementierte UI,
  Persistenz oder Kryptografie behaupten.
- Personen- und Mehrparteienisolation ist zunächst verbindlicher Vertrag,
  noch keine technische Zugriffskontrolle.
- Exakte Vertragselemente, Hash, Loader-Vollständigkeit, Boot-Reihenfolge und
  Preflight-Integrität werden deterministisch getestet.
- Bestehende Goal- und Life-Decisions-Workflows erhalten keine neuen
  Kontextinhalte.

### Abweichungen und Abschlusszustand

Die neue Ebene ist als versionierter Interaction-Vertrag, unveränderlicher
Kontext und verpflichtender Runtime-/Preflight-Nachweis umgesetzt. Die
Institution wurde auf Version 1.1 und die Constitution auf Version 1.4
fortgeschrieben; bestehende Guardian-Prinzipien und operative Workflows
bleiben unverändert. Konkrete UI-, Kryptografie-, Autorisierungs-, Lösch- und
Notfallmechanismen wurden bewusst nicht implementiert. 379 Tests bestehen;
Doctor und `git diff --check` sind erfolgreich.

## Abgeschlossener Plan: Main mit Origin synchronisieren

### Ziel und Nicht-Ziele

Den lokalen `main` linear mit `origin/main` synchronisieren, ohne lokale
Guardian- oder Institution-Architekturcommits zu verlieren. Kein Push, keine
Architekturänderung und keine funktionale Implementierung.

### Geprüfter Ausgangszustand

- Arbeitsbaum auf `main` war sauber.
- Lokaler Ausgangscommit war `7890203`.
- Gemeinsame Basis war `7886bbb`.
- `main` war vier Commits voraus und drei Commits hinter `origin/main`.
- `origin/main` endete nach aktuellem Fetch auf `74c2326`.

### Arbeitsschritte und Fortschritt

- [x] Remote aktualisieren und Divergenz vollständig prüfen.
- [x] Backup-Branch `backup/main-pre-sync-7890203` erstellen.
- [x] Vier lokale Commits linear auf `origin/main` rebasen.
- [x] Patch-Äquivalenz mit `git range-diff` prüfen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und sauberen Abschluss erzeugen.

### Entscheidungen und Begründungen

- Rebase statt Merge, weil alle vier lokalen Commits eigenständig,
  patch-äquivalent und konfliktfrei auf die drei Remote-Commits anwendbar
  waren.
- Der Backup-Branch bewahrt die ursprünglichen Commit-IDs unverändert.
- Es war keine Konfliktlösung und keine Architekturinterpretation nötig.

### Risiken und Teststrategie

- Ein späterer Push muss als normaler Fast-Forward von `origin/main` erfolgen.
- `git range-diff` bestätigt vier patch-identische lokale Commits.
- Der Baum gegenüber dem Backup enthält zusätzlich ausschließlich neun
  Guardian-Foundation-Dokumente aus `origin/main`.
- 352 Tests bestehen; Doctor und `git diff --check` sind erfolgreich.

### Abweichungen und Abschlusszustand

Keine Konflikte oder Abweichungen. Der synchronisierte Architekturstand endet
auf `9ec3566`, ist gegenüber `origin/main` null Commits hinter und vier Commits
voraus. Es wurde nicht gepusht.

## Abgeschlossener Plan: Institution Layer

### Ziel und Nicht-Ziele

Eine eigenständige, unveränderliche Institution-Ebene zwischen Guardian und
Runtime etablieren. Sie enthält ausschließlich langfristige Systemgarantien
für Governance, Nutzerhoheit, Guardian Continuity, Transparenz, Verantwortung,
Schutz, Würde und Vertrauen. Keine Fachlogik, UI, Workflow- oder
Monetarisierungsfunktion.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `9221193` war erfolgreich.
- WHY, Constitution, Values und ADRs enthalten einzelne Schutz- und
  Vertrauensregeln, aber keinen eigenständigen Garantievertrag.
- Runtime lädt Identity, Constitution und Knowledge zentral; eine
  Institution-Ebene fehlt.
- Guardian ist architektonisch definiert, aber noch keine
  Laufzeitkomponente.
- Es existiert keine parallele Governance- oder Policy-Struktur.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Identity, Constitution, Runtime, Preflight und ADRs prüfen.
- [x] Kanonischen Institution-Vertrag und typisiertes Modell erstellen.
- [x] Institution Layer in Runtime und Mission Context integrieren.
- [x] Constitution und neue Architekturentscheidung konsistent ergänzen.
- [x] Modell-, Loader-, Runtime- und Preflight-Tests ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Institution ist ein eigener, versionierter Garantievertrag; Identity und
  Constitution bleiben unverändert in ihrer jeweiligen Verantwortung.
- Runtime bleibt Single Source of Truth und lädt genau einen unveränderlichen
  `InstitutionContext`.
- Mission Context muss die geladene Institution strukturell nachweisen, damit
  kein freigegebener Workflow ohne Garantien startet.
- Garantien definieren Grenzen, aber keine operative Entscheidung oder
  Ausführung.

### Risiken

- Institution darf nicht zu einer zweiten Constitution oder Policy Engine
  anwachsen.
- „Vertrauen nicht verbrauchen“ benötigt konkrete Architekturtests, darf aber
  nicht als behauptete Messgröße dargestellt werden.

### Teststrategie

- Exakte, stabile Garantietypen und unveränderlicher Kontext.
- Fehlende, unvollständige oder ungültige Institution verhindert Boot.
- Runtime lädt Identity vor Institution und Institution vor operativem
  Kontext.
- Preflight enthält und validiert Institution.
- Vollständige Regression, Doctor, Python 3.9 und `git diff --check`.

### Abweichungen und Abschlusszustand

Der Institution Layer ist als kanonischer Vertrag, typisierter Kontext und
verbindlicher Runtime-Boot-Schritt umgesetzt. Der Mission Context 1.1 weist
Version, Hash und Garantien nach, ohne den Vertrag an operative Komponenten
weiterzureichen. 352 Tests bestehen; Doctor und `git diff --check` sind
erfolgreich. Eine operative Policy Engine war wegen der bewusst
nicht-operativen Garantieebene nicht erforderlich.

## Abgeschlossener Plan: Guardian First, Workflow Second

### Ziel und Nicht-Ziele

Die aus dem Conversation Lab abgeleitete Guardian-First-Erkenntnis als
verbindliche Ergänzung zu ADR-0023 verankern. Interne Entscheidungsräume
bleiben im Alltag unsichtbar, müssen auf Wunsch aber nachvollziehbar,
korrigierbar und ablehnbar sein. Keine Implementierung, UI, Produktlogik oder
Workflow-Änderung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `c37adbd` war erfolgreich.
- Constitution 1.1 und ADR-0023 priorisieren bereits Guardian und S-V-N-P.
- Das Conversation Lab unterscheidet Bedarf, Entscheidungsraum und
  Workflow-Match im Hintergrund.
- Die bisherige Regel „unsichtbar“ definiert noch nicht verbindlich das Recht
  auf spätere Erklärung, Korrektur und Ablehnung.
- ADR-0023 bleibt gültig; die neue Entscheidung präzisiert ihre
  Transparenzgrenze.

### Arbeitsschritte und Fortschritt

- [x] Preflight, ADR-0023, Constitution und Lab-Regeln prüfen.
- [x] Ergänzende Architekturentscheidung ADR-0024 dokumentieren.
- [x] Verbindliche Transparenzrechte in der Constitution verankern.
- [x] Lab-Dokumentation widerspruchsfrei aktualisieren.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- ADR-0024 ergänzt ADR-0023 und ersetzt sie ausdrücklich nicht.
- Entscheidungsräume entstehen als vorläufige Hypothesen vor jeder
  Workflow-Prüfung.
- Unsichtbarkeit bedeutet störungsfreie Alltagserfahrung, nicht Geheimhaltung
  oder Black Box.
- Ein neuer Workflow entsteht niemals dynamisch im Gespräch, sondern erst
  nach ausreichendem Verständnis und einer späteren Architekturentscheidung.

### Risiken

- Transparenz darf den natürlichen Gesprächseinstieg nicht in einen
  technischen Audit-Dialog verwandeln.
- Vorläufige Hypothesen dürfen nicht als bestätigte Selbstaussage des Menschen
  gespeichert oder verwendet werden.

### Teststrategie

- Dokumente auf Rangfolge und Widerspruch zu ADR-0023 prüfen.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

ADR-0024 ergänzt ADR-0023 ausdrücklich und definiert Guardian First,
Entscheidungsraum-Hypothesen vor Workflow-Prüfung sowie „im Alltag
unsichtbar, auf Wunsch transparent“. Constitution 1.2 verankert
Korrektur-, Ablehnungs-, Wahl- und Nachvollziehbarkeitsrechte. Das Lab wurde
konsistent präzisiert. Es gab keine Implementierung oder Workflow-Änderung.
334 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Guardian Conversation Lab

### Ziel und Nicht-Ziele

ADR-0023 mit 100 anonymisierten, deterministischen Gesprächssimulationen
fachlich validieren und daraus Style Guide, Regeln, Anti-Patterns, Taxonomie
und offene Fragen ableiten. Keine UI, Sprachschnittstelle, Fachberatung,
Workflow-Änderung oder neue Laufzeitkomponente.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `2850492` war erfolgreich.
- Constitution 1.1 und ADR-0023 definieren S-V-N-P verbindlich.
- Es gibt noch kein Conversation Lab, keine Simulationsmatrix und keinen
  automatisierten Abdeckungstest.
- Es existiert keine geeignete generische Lab- oder Conversation-Struktur.
  Projektwissen und Sources sind die vorhandenen Ablagen für Dokumentation und
  maschinenlesbare Testdaten.

### Arbeitsschritte und Fortschritt

- [x] Preflight, ADR-0023, Knowledge-Struktur und Testkonventionen prüfen.
- [x] Deterministische Matrix mit 100 diversen Fällen erstellen.
- [x] Style Guide, Regeln, Taxonomie und Anti-Patterns dokumentieren.
- [x] Stabile S-V-N-P-, Datenschutz- und Abdeckungsregeln testen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Das Lab bleibt Test- und Wissensartefakt; Produktcode wird nur bei einem
  belegten Modellmangel verändert.
- Hintergrundklassifikation bleibt unsichtbare Metadaten und erzeugt keinen
  Workflow.
- Qualität wird über explizite Kriterien und Coverage-Invarianten geprüft,
  nicht durch LLM-Selbsteinschätzung.

### Risiken

- Simulationen beweisen kein reales Nutzervertrauen und ersetzen keine spätere
  Forschung mit freiwilligen Teilnehmenden.
- Regelbasierte Tests können Gesprächsqualität nur strukturell, nicht
  semantisch vollständig bewerten.

### Teststrategie

- Exakt 100 eindeutige Fälle mit breiter Themen-, Stil-, Alters-, Bildungs-
  und Emotionsabdeckung.
- Keine Workflow-Sichtbarkeit, Fachberatung, Preislogik oder sensiblen Daten.
- Zusammenfassung, Anschlussfrage, Klassifikation, Risiken und Verbesserung
  sind pro Fall explizit.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

Die Matrix enthält 100 eindeutige Einstiege über 25 Themen, vier
Kommunikationsstile, fünf Altersgruppen, vier sprachliche Bildungskontexte,
acht emotionale Zustände, alle Bedarfsklassen sowie bekannte, neue und nicht
vorhandene Entscheidungsräume. Neun deterministische Lab-Tests prüfen
Abdeckung, S-V-N-P-Grenzen, Datenschutz und unsichtbares Workflow-Routing.
Kein Produktcode und kein fachlicher Workflow mussten geändert werden.
334 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Guardian Conversation Principles

### Ziel und Nicht-Ziele

S-V-N-P als verbindliche Reihenfolge für Guardian-Interaktion,
Gesprächsführung und UX in die bestehende Identity- und
Constitution-Architektur einordnen. Keine UI, kein neuer Workflow, keine
fachliche Life-Decisions-Änderung und keine Monetarisierungsimplementierung.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `7886bbb` war erfolgreich.
- WHY priorisiert den Menschen und Vertrauen bereits vor Wachstum.
- Constitution regelt Kommunikation, enthält aber keine menschengeführte
  Gesprächsreihenfolge.
- Manifest und Values beginnen fachliche Entscheidungsarbeit mit Ziel und
  Nutzen; sie unterscheiden den Gesprächseinstieg noch nicht ausdrücklich vom
  internen Entscheidungszyklus.
- Es existiert keine Guardian- oder Conversation-ADR und keine parallele
  Interaction-Architektur.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Identity-Dokumente, ADRs und Interaktionsregeln prüfen.
- [x] Constitution um das verbindliche Kernprinzip erweitern.
- [x] Guardian Conversation Principles als ADR dokumentieren.
- [x] Values konsistent abgrenzen und Verhaltensbeispiele ergänzen.
- [x] Vollständige Tests, Doctor und `git diff --check` ausführen.
- [x] Handover und geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- S-V-N-P wird unterhalb des WHY und innerhalb der Constitution verankert; es
  entsteht keine zweite Philosophie.
- Die Reihenfolge gilt für sichtbare Interaktion und UX. Bestehende Goal-,
  Decision- und Workflow-Architektur darf nach hinreichendem Verständnis im
  Hintergrund vorbereitet werden.
- Sympathie bedeutet respektvolle menschliche Anschlussfähigkeit, nicht
  Manipulation oder erzwungene Zustimmung.

### Risiken

- „Hinreichendes Vertrauen“ ist kontextabhängig und darf nicht durch ein
  mechanisches Pflichtdialog-Schema vorgetäuscht werden.
- Fachlich notwendige Sicherheitswarnungen dürfen nicht aus Höflichkeit
  verzögert werden.

### Teststrategie

- Dokumente auf Widersprüche, Rangfolge und klare Grenzen prüfen.
- Vollständige Regression, Doctor und `git diff --check`.

### Abweichungen und Abschlusszustand

S-V-N-P ist in Constitution 1.1 verbindlich und durch ADR-0023 in die
Identity-First-Architektur eingeordnet. Values grenzt den menschlichen
Gesprächseinstieg vom internen Goal- und Entscheidungszyklus ab. Es wurden
keine UI, kein Workflow, keine Preislogik und keine Life-Decisions-Fachregel
implementiert. 325 Tests, Doctor und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Power of Attorney Workflow Validation

### Ziel und Nicht-Ziele

Den bestehenden Vorsorgevollmacht-Workflow mit acht realistischen,
anonymisierten Fällen sowie Missbrauchs- und Grenzanfragen fachlich
validieren. Nur belegte Modellmängel korrigieren. Keine Persistenz,
Dokumentanalyse, Rechtsberatung, Netzwerk- oder Cloudfunktion.

### Geprüfter Ausgangszustand

- Preflight auf `main` und Commit `c64854d` war erfolgreich.
- Der Workflow erzeugt eine unveränderliche, ID-basierte Übersicht und gibt
  keine Personenbezeichnungen, Dokumentreferenzen oder Dokumentinhalte aus.
- Professionelle Prüfungen werden nicht automatisch abgeleitet.
- Zwei belegbare Lücken bestehen: eine unklare Einzel-/Gesamtvertretung kann
  nicht explizit modelliert werden; mehrere relevante Dokumentreferenzen
  können nicht vollständig an die Dokumentprüfung gebunden werden.
- Eine abgeschlossene Fachprüfung akzeptiert bisher jeden bestätigten Fakt,
  nicht ausschließlich eine professionell bestätigte Abschlussgrundlage.

### Arbeitsschritte und Fortschritt

- [x] Preflight, Architektur und bestehende Tests prüfen.
- [x] Acht anonymisierte Fall-Fixtures und Erwartungsmatrix erstellen.
- [x] Belegte Modelllücken minimal schließen.
- [x] Missbrauchs- und Grenztests ergänzen.
- [x] Fokussierte und vollständige Prüfungen ausführen.
- [x] Validierungsdokument, Handover und Commit abschließen.

### Entscheidungen und Begründungen

- Die Validierung erweitert ausschließlich bestehende Workflow-Modelle und
  Tests; es entsteht keine zweite Fach- oder Workflow-Architektur.
- Unklare Vertretungsart erhält einen expliziten `unknown`-Status mit
  verpflichtender Frage.
- Weitere vorhandene Vollmachten werden als zusätzliche ID-Referenzen an
  derselben Dokumentprüfung modelliert.
- Ein Prüfabschluss benötigt einen `professionally_confirmed` Fakt.

### Risiken

- Freitext kann nicht vollständig semantisch klassifiziert werden. Er wird
  deshalb nicht in die maschinenlesbare Ausgabe übernommen.
- Der Workflow erkennt keine Dokumentwidersprüche selbst; sie müssen als
  explizite Fragen und Unsicherheiten erfasst werden.

### Teststrategie

- Acht Fallkonstellationen mit expliziten erwarteten IDs und Statuswerten.
- Missbrauchsanfragen dürfen keine verbotene Aussage in der Ausgabe bewirken.
- Invarianten für unklare Vertretung, mehrere Dokumente und Prüfabschluss.
- Regression, Doctor, Python 3.9 und `git diff --check`.

### Abweichungen und Abschlusszustand

Die acht Fallkonstellationen und sechs Missbrauchskategorien wurden gegen den
tatsächlichen Workflow ausgeführt. Drei belegte Modelllücken wurden ohne neue
Architekturschicht geschlossen: unbekannte Vertretungsart, zusätzliche
Dokumentreferenzen und professionell bestätigte Abschlussgrundlage. Die
vollständige Regression umfasst 325 erfolgreiche Tests. Doctor,
Python-3.9-Kompilierung und `git diff --check` waren erfolgreich.

## Abgeschlossener Plan: Power of Attorney Preparation Workflow

### Ziel und Nicht-Ziele

Den ersten realen Life-Decisions-Workflow für die strukturierte Vorbereitung
und Überprüfung einer Vorsorgevollmacht auf dem bestehenden Goal Application
Service aufbauen. Keine Rechtsberatung, Wirksamkeitsprüfung,
Dokumenterstellung, Persistenz, Cloud- oder Netzwerkfunktion.

### Geprüfter Ausgangszustand

- `LifeDecisionCase` bildet Teilnehmer, Dokumentreferenzen, Fakten, Fragen,
  Unsicherheiten, Fachprüfungen, Decision Records und Review Schedules bereits
  als unveränderliches Aggregat mit stabilen IDs ab.
- Der Goal Application Service erzwingt Mission Context und führt über
  Orchestrator, Decision Engine, Planner und Execution Engine.
- Es existiert kein generischer Intake-, Checklist- oder Recommendation-
  Workflow. Die vorhandene Goal-Kette und das Life-Decisions-Aggregat sind die
  Erweiterungspunkte.
- Der Goal-CLI-Pfad unterstützt bereits typisierte optionale Artefakte und
  maschinenlesbare Ergebnisse.

### Arbeitsschritte und Fortschritt

- [x] Preflight und vollständige Bestandsaufnahme durchführen.
- [x] Fachlich neutrale Workflow-Eingabe und Invarianten modellieren.
- [x] Workflow mit Goal Application Service integrieren.
- [x] Bestehenden Goal-CLI-Pfad minimal erweitern.
- [x] Fach-, Sicherheits-, CLI- und Regressionstests ergänzen.
- [x] ADR, vollständige Prüfung, Handover und Commit abschließen.

### Entscheidungen und Begründungen

- Der neue Domänenworkflow wird im bestehenden Paket `life_decisions`
  implementiert und komponiert den vorhandenen Goal Application Service.
- `LifeDecisionCase` bleibt das Aggregat; Workflow-Modelle referenzieren seine
  Objekte nur über IDs.
- Die Ausgabe enthält ausschließlich stabile IDs und Statuswerte.
- Fehlende oder unbekannte Angaben erzeugen Fragen und Unsicherheiten, niemals
  erfundene Fakten.

### Risiken

- Professionelle Prüfbedarfe dürfen nur explizit vorgegeben oder aus klaren
  nutzerkontrollierten Statuswerten abgeleitet werden.
- Personenbezeichnungen und Dokumentinhalte dürfen nicht in Ergebnis,
  Decision Journal oder Handover gelangen.

### Teststrategie

- Vollständige, fehlende und ungeprüfte Fälle sowie Konflikte.
- Aggregatfremde und doppelte IDs.
- Fachprüfungs- und Unsicherheitssemantik.
- Determinismus, Unveränderlichkeit, Mission-Context-Gate und CLI.
- Vollständige Regression, Doctor, Preflight und `git diff --check`.

### Abweichungen und Abschlusszustand

Keine parallele Workflow- oder Persistenzarchitektur wurde benötigt. Der
Workflow nutzt den bestehenden Goal-CLI-Pfad; `--apply`, `--record` und
Knowledge-Artefakte bleiben für diesen fachlichen Pfad bewusst ausgeschlossen.
Die vollständige Regression umfasst 307 erfolgreiche Tests. Doctor,
Python-3.9-Kompilierung und `git diff --check` waren erfolgreich. ADR-0022
dokumentiert die neue verbindliche Workflow-Grenze.

## Abgeschlossener Plan: Mission Context Workflow Integration

### Ziel und Nicht-Ziele

Den bestehenden Goal Application Service durch einen validierten Mission
Context sperren und dessen minimale Workflow-Sicht explizit bis zum
Orchestrator übergeben. Keine neue Fachlogik, kein neuer Workflow, keine
Netzwerk-, Cloud-, UI- oder Datenbankfunktion.

### Geprüfter Ausgangszustand

- Der Preflight erzeugt einen `MissionContext`, wurde aber vom Goal-Workflow
  noch nicht verwendet.
- `GoalApplicationService` injiziert bereits dieselbe Runtime in Collector,
  Goal Engine und Orchestrator.
- Der Orchestrator übergibt technischen Kontext, GoalContext, Identity und
  WHY-Assessment an die Decision Engine und ruft Planner sowie Execution Engine
  ausschließlich nach Freigabe auf.
- Planner und Execution Engine benötigen keinen vollständigen Mission Context.

### Arbeitsschritte und Fortschritt

- [x] Verpflichtenden Preflight ausführen und Mission Context prüfen.
- [x] Application-, Orchestrator-, Decision- und Execution-Verträge lesen.
- [x] Mission Context tief unveränderlich und zeitlich validierbar machen.
- [x] Goal Application Service durch Preflight-Validierung sperren.
- [x] Minimale typisierte Workflow-Sicht an den Orchestrator übergeben.
- [x] CLI- und Fehlerpfade integrieren.
- [x] Fokussierte Tests ausführen.
- [x] Vollständige Tests ausführen.
- [x] Handover erzeugen.
- [x] Geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Der bestehende Goal Application Service bildet die kleinste reale
  vollständige Kette und wird erweitert.
- Der vollständige Mission Context bleibt am Application-Service-Rand.
  Der Orchestrator erhält nur unveränderliche Git- und Herkunftsmetadaten.
- Decision Engine erhält weiterhin ausschließlich ihren technischen Kontext
  und Goal-Vertrag; Planner und Execution Engine erhalten keinen überflüssigen
  Projektkontext.
- Ein WorkflowContext kann nur aus einem MissionContext abgeleitet werden.

### Risiken

- Zeitliche Gültigkeit ist auf fünf Minuten begrenzt; lange Pausen vor dem
  Start eines Runs verlangen einen neuen Preflight.
- Bestehende direkte Legacy-Orchestrator-Aufrufe bleiben kompatibel; nur der
  Goal-basierte Pfad verlangt den WorkflowContext.

### Teststrategie

- Erfolgreicher vollständiger Goal-Workflow.
- Fehlender, strukturell ungültiger und veralteter Mission Context.
- Tiefe Unveränderlichkeit und deterministische Ableitung.
- Minimale Kontextweitergabe pro Komponente.
- Vollständige Regression, Doctor, Preflight und `git diff --check`.

### Abweichungen und Abschlusszustand

Keine Abweichung vom gewählten Goal-Workflow. Die vollständige Integration,
Fehlerpfade und Kontextgrenzen sind umgesetzt. 292 Tests, Doctor, produktiver
Preflight und `git diff --check` waren erfolgreich. Der lokale Handover ist
erzeugt und gehört zum geprüften Abschlusscommit. Es wurde nicht gepusht.

## Abgeschlossener Plan: Codex Context and Handover

### Ziel

Verbindlichen lokalen Preflight und einen deterministischen, lokalen Staffelstab
auf Basis der bestehenden Runtime- und Knowledge-Architektur bereitstellen.

### Nicht-Ziele

- Keine Netzwerk-, Cloud-, Datenbank- oder UI-Funktion.
- Keine Änderung fachlicher Domänenmodelle.
- Kein automatischer Commit oder Push.

### Geprüfter Ausgangszustand

- `RuntimeManager` lädt Constitution, Knowledge, letzte Session, Project State,
  Verified Facts, Identity und Goal Engine.
- `ContextCollector` und `ContextAnalyzer` verdichten Runtime- und Git-Kontext.
- `KnowledgeManager` kennt ADRs, Protokolle, Handovers, Projektwissen, Sessions,
  Quellen und Verified Facts.
- `ProjectState` persistiert lokalen Laufzeit- und Git-Zustand.
- Der bestehende `handover`-Command erzeugt Session-Markdown über einen
  Netzwerkaufruf; ein lokaler, strukturierter Handover-Vertrag fehlt.
- Ein `preflight`-Command, Root-`AGENTS.md` und Planformat fehlen.

### Arbeitsschritte und Fortschritt

- [x] Bestehende Architektur, ADRs, Runtime, Wissen und Tests prüfen.
- [x] Preflight und Mission Context auf der Runtime ergänzen.
- [x] Deterministischen Handover-Vertrag und atomaren Writer ergänzen.
- [x] Root-`AGENTS.md` und Architekturentscheidung dokumentieren.
- [x] Fehlerfälle, CLI und Rückwärtskompatibilität testen.
- [x] Vollständige Prüfung durchführen.
- [x] Finalen Handover erzeugen.
- [x] Geprüften Commit erzeugen.

### Entscheidungen und Begründungen

- Bestehende `RuntimeManager`-, `KnowledgeManager`-, `ContextCollector`- und
  `knowledge/handovers`-Struktur wird erweitert; es entsteht kein zweiter Store.
- Der neue Handover ist lokal und deterministisch. Der bisherige
  netzwerkabhängige Agentenaufruf ist für den verbindlichen Staffelstab
  ungeeignet.
- Maschinenlesbare JSON- und menschenlesbare Markdown-Sicht teilen denselben
  validierten Datensatz.

### Risiken

- Runtime-Initialisierung schreibt derzeit Project State und muss bei
  strukturellen Fehlern verständlich abbrechen.
- Git- und Teststatus sind Laufzeitdaten; fehlende Werte dürfen nicht erfunden
  werden.

### Teststrategie

- Unit-Tests für Mission Context, Validierung und atomare Handover-Ausgabe.
- CLI-Tests für erfolgreichen und strukturell fehlerhaften Preflight.
- Bestehende vollständige Testsuite, Doctor und `git diff --check`.

### Abweichungen

- Der bestehende modellbasierte Handover wurde nicht parallel beibehalten:
  ADR-0020 ersetzt ihn bewusst durch den lokalen deterministischen Vertrag.
- Statt einer einzelnen Mischdatei entstehen JSON und Markdown aus demselben
  Record, damit Maschinen- und Menschenlesbarkeit jeweils eindeutig bleiben.

### Abschlusszustand

Preflight, lokaler Handover-Vertrag, Arbeitsregeln, Planformat,
Architekturdokumentation und Tests sind umgesetzt. Die vollständige Suite
bestand mit 282 Tests; Doctor, produktiver Preflight und `git diff --check`
waren erfolgreich. Der lokale Handover gehört zum abschließenden Commit; es
wurde kein Push ausgeführt.
