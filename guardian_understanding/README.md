# Guardian Understanding Proposal and Clarification Layers

Understanding Proposals are possible interpretations, not truths. They are
explicitly non-authoritative, do not represent facts, and cannot change an
`UnderstandingState`.

An `UnderstandingOperation` describes one possible state change. A proposal
wraps exactly one unchanged operation with its originating user statement,
source reference, and rationale. An `UnderstandingRevision` is created only
after a concrete proposal is explicitly selected; the existing deterministic
Understanding Model v2 remains the sole revision mechanism.

A later semantic component may create proposals only. It must never write to
the Understanding State or invoke a revision without explicit proposal
selection.

## Clarification Resolution v1

A clarifying user answer is preserved as source material; it is not
automatically interpreted. The original proposal set describes possible
unchanged `UnderstandingOperation` values, its understanding question asks for
clarification, and an immutable `ClarificationResolution` records the explicit
human classification of the answer. Only `SELECT_PROPOSAL` delegates exactly
one existing operation through `GuardianUnderstandingProposalService.apply()`
to the existing `GuardianUnderstandingService.advance()` revision mechanism.

`REJECT_PROPOSALS` records concrete rejected alternatives without changing the
state. `KEEP_OPEN` preserves the alternatives and requires exactly one next
understanding question. `CLOSE_WITHOUT_CHANGE` closes the proposal set without
running an operation. Proposal, question, answer, resolution, selected
operation and resulting `UnderstandingRevision` remain separately traceable.

A later semantic component may prepare typed resolution suggestions only. It
must not choose a resolution, select a proposal, or activate a revision.

## Guardian Answer Boundary Contracts v1

ADR-0047 ergänzt das Understanding Model um interne, unveränderliche
Antwortgrenzen für allgemeine Orientierung (`B1`), persönliche Vorbereitung
(`B2`) und die zwingende fachliche Nicht-Bestätigung (`B3`). Die Betriebsart
ist ausschließlich bereits typisiertes Sicherheits- und Auditmetadatum.

`GuardianAnswerBoundaryValidator` prüft deterministisch, dass Schutz nur
gleich bleibt oder erhöht wird, B2 keine fachliche Einzelfallentscheidung
zulässt und B3 eine kontrollierte klare Nicht-Bestätigung enthält. Sämtliche
Fähigkeiten zum Ändern von States, Artefakten, Resolutionen, Rechten,
Freigaben, Journey-Status oder Quellenketten sowie Aktivierung, Workflow und
Routing müssen ausdrücklich verboten bleiben. Der Validator interpretiert
keine Sprache, klassifiziert keine Anfrage und führt nichts aus.

## Guardian Source Chain Contracts v1

Der unveränderliche T4-Vertrag bildet alle zwölf Pflichtfelder aus ADR-0047
§ 7 explizit ab: Quelle und Herausgeber; Quellenart und Autorität; Referenz;
Abrufzeitpunkt; Veröffentlichungs- oder Versionsstand; gestützte Aussage;
Rechtsraum oder Geltungsbereich; deklarierte Widersprüche; Unsicherheitsstatus;
Neuprüfungsbedarf; Guardian-Antwort- und Gesprächskontext; Provenienz.

Widersprüche sind ausschließlich bereits bereitgestellte Referenzen. Weder
Zeitpunkt, Version, Quellenart noch Widerspruch erzeugen automatisch Vorrang,
Ablösung, Bewertung oder Statusänderung. Der Validator prüft nur Typen und
Struktur. Er recherchiert und persistiert nicht, besitzt keine Ausführungsmacht
und ist zur Laufzeit nicht mit B1, B2 oder B3 verbunden.

## Guardian Classification Contract v1

Der unveränderliche Klassifikationsnachweis beschreibt ausschließlich eine
bereits bereitgestellte Zuordnung. Er verwendet `AnswerOperatingMode` und die
kanonische Schutzordnung direkt aus den Answer Boundary Contracts; es gibt
weder eine zweite B-Stufen-Enum noch eine parallele Eskalationsmatrix.

Eine nicht leere Kandidatenmenge hält Unsicherheit typisiert fest. Der
Validator verlangt ihre höchste Schutzstufe als wirksame Stufe und wahrt eine
bereitgestellte Mindeststufe. Der Bereitsteller-Nachweis dokumentiert nur die
Herkunft, nicht Autorität oder Berechtigung. Es existieren keine Interpretation,
Klassifikations-Runtime, B1-/B2-/B3-Aktivierung oder Ausführungsmacht.

## Guardian Answer Foundation Integration v1

Die drei Vertragsfamilien bleiben eigenständig und werden nur deklarativ
verbunden: Ein Boundary Contract kann genau eine Classification-ID referenzieren;
eine Classification kann mehrere eindeutige Source-Chain-IDs referenzieren.
Es gibt keine Rückreferenzen, Registry, Historienauflösung oder Ladefunktion.

Der Integrationsvalidator prüft ausschließlich bereitgestellte IDs, optional
vollständige Source-Chain-Mengen und die Boundary-Schutzstufe über die kanonische
Ordnung aus `answer_boundary.py`. Er gibt dasselbe Integrationsobjekt mit
denselben Vertragsobjekten zurück und klassifiziert, interpretiert, aktiviert,
normalisiert oder persistiert nichts.

## Guardian Controlled Orientation Package v1

Eine kontrollierte B1-Orientierung beschreibt ausschließlich bereits
bereitgestellte Inhalte. Sie generiert, formuliert, übersetzt, verbessert oder
interpretiert keinen Text. Ein vollständiger Nachweis verlangt exakt eine
wirksame B1-Classification, eine B1-Boundary und mindestens eine vollständig
bereitgestellte, in Classification und Orientierung identisch referenzierte
Source Chain.

Allgemeine B1-Orientierung darf Begriffe und allgemeine Abläufe erklären,
typische Optionen oder Risiken darstellen, Unsicherheit und Quellenstände
sichtbar machen sowie zu persönlicher Vorbereitung oder professioneller
Prüfung überleiten. Sie darf keine persönliche Einzelfallentscheidung,
individuelle Rechts-, Steuer-, Finanz- oder medizinische Entscheidung,
Handlungsempfehlung, professionelle Bestätigung oder Ausführung darstellen.
Da v1 keine natürliche Sprache auswertet, sichert die vorgelagerte typisierte
B1-Classification diese Grenze; die Textfelder werden nur strukturell auf
nicht leere, unveränderte Werte geprüft.

Der Provider-Nachweis dokumentiert nur die Herkunft und erteilt keine
Autorisierung. Der fachliche Prüfstatus ist rein deklarativ; nur eine als
durchgeführt deklarierte Prüfung benötigt eine Referenz, bestätigt aber weder
Richtigkeit noch Qualifikation. Der Baustein recherchiert und persistiert
nicht, besitzt keine Antwort-Runtime und keine Ausführungsmacht.

## Guardian Personal Preparation Package v1

Eine persönliche B2-Vorbereitung strukturiert ausschließlich bereits
bereitgestellte persönliche Angaben: bekannte Tatsachen, offene Fragen,
nebeneinander zu prüfende Optionen, Unsicherheiten und Themen für eine
professionelle Prüfung. Sie darf außerdem dokumentieren, welche Unterlagen oder
Informationen noch benötigt werden. Sie extrahiert oder erzeugt diese Inhalte
nicht und wählt, priorisiert oder bewertet keine Option.

Der vollständige Nachweis verlangt exakt eine B2-Classification und eine
B2-Boundary sowie eine vollständig identische Source-Chain-Menge. Eine bereits
validierte B1 Controlled Orientation kann optional rein deklarativ referenziert
werden; sie ist keine Voraussetzung und wird weder geladen, kopiert noch in
B2-Inhalte umgewandelt. Textfelder werden ausschließlich strukturell, nicht
semantisch validiert.

B2 darf keine konkrete Rechtsgestaltung empfehlen, individuelle Steuer-,
Finanzierungs-, medizinische oder sonstige professionelle Einzelfallentscheidung
treffen, einen Vertrag als unterschriftsreif bestätigen, persönliche Risiken
abschließend bewerten oder Handlungen ausführen und freigeben. Provider-Herkunft
und Fachprüfstatus bleiben rein deklarativ und erzeugen weder Autorisierung noch
Richtigkeitsbestätigung. Der Baustein besitzt keine Recherche, Runtime,
Persistenz, Aktivierung oder Zustandsänderungsmacht.
