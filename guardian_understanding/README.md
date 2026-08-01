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
