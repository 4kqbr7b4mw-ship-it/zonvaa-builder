# ADR-0019 – Life Decisions Domain Model

## Status

Beschlossen

## Kontext

ADR-0018 führt Life Decisions als nutzerkontrollierte Intelligenz- und Entscheidungsschicht ein. Phase 1 der Roadmap verlangt eine verbindliche Trennung von Lebensfall, Beteiligten, Dokumentreferenzen, bestätigten Fakten, offenen Fragen, Unsicherheiten, Fachprüfungen, Entscheidungen und Prüfterminen. Ohne typisierte Grenzen könnten Nutzeraussagen, Interpretationen und bestätigte Fakten vermischt oder ungeprüfte Entscheidungen als fachlich bestätigt dargestellt werden.

## Entscheidung

Life Decisions erhält das eigenständige Paket `life_decisions`. Es enthält ausschließlich unveränderliche, Python-3.9-kompatible Dataclasses und stabile String-Enums. Die Domäne besitzt keine Persistenz, keinen Dateisystemzugriff, keine Cloud-, Datenbank-, UI- oder Dokumentgenerator-Funktion.

`LifeDecisionCase` ist das Aggregat für die explizit bereitgestellten Domänenobjekte. Es erzeugt weder Teilnehmerrollen noch Fakten, Fragen, Unsicherheiten oder Entscheidungen automatisch. Verschachtelte Kernwerte werden als unveränderliche Tupel typisierter Objekte geführt. Alle referenzierbaren Objekte besitzen explizite, unveränderte IDs. IDs müssen innerhalb ihrer jeweiligen fachlichen Sammlung eindeutig sein; dieselbe ID darf in verschiedenartigen Sammlungen vorkommen, weil Typ und ID gemeinsam die Referenz bestimmen.

`DocumentReference` speichert nur einen logischen, nutzerkontrollierten Speicherverweis, Analysefreigabe und optionale Integritätsmetadaten. Vollständige Dokumentinhalte sind kein Feld des Domänenmodells. Speicherverweise sind begrenzte, einzeilige Strings ohne umgebende Leerzeichen oder Steuerzeichen. `data:`-URIs, bekannte Dokumentanfänge und offensichtlich Base64-kodierte Blöcke werden abgelehnt. Prüfsummen müssen als hexadezimaler Digest exakt zur gewählten SHA-Variante passen und sind daher ebenfalls kein freier Inhaltskanal. Diese syntaktischen Schranken verhindern bekannte Formen eingebetteter Inhalte, können aber nicht die Bedeutung jedes beliebigen Strings erkennen. Der Speicherverweis löst keinen Zugriff aus und schreibt weder Dateisystem- noch Cloudsemantik vor.

`VerifiedFact` verlangt eine nachvollziehbare Quelle, einen expliziten Bestätigungsstatus und einen Bestätigungszeitpunkt. Unbestätigte Aussagen gehören nicht in diese Klasse. Interpretationen werden nicht automatisch zu Fakten hochgestuft.

`DecisionRecord` referenziert verwendete Fakten, offene Unsicherheiten und notwendige Fachprüfungen ausschließlich über stabile IDs. Das Aggregat lehnt Referenzen ab, die nicht in demselben `LifeDecisionCase` vorhanden sind. So werden fallfremde oder duplizierte vollständige Objekte vermieden.

Der Status `professional_reviews_completed` bedeutet ausschließlich, dass mindestens eine referenzierte Fachprüfung dokumentiert und jede referenzierte Fachprüfung abgeschlossen ist. Er behauptet weder vollständige Klärung noch Entscheidungsreife; offene Unsicherheiten bleiben separat und dürfen weiterhin bestehen. ZONVAA ersetzt keine rechtliche, notarielle, steuerliche, medizinische, finanzielle oder sonstige professionelle Prüfung.

## Grenzen

- Das Modell erteilt keine Rechts-, Steuer-, Medizin- oder Finanzberatung.
- Teilnehmerrollen sind beschreibende Rollen im Lebensfall und keine automatische rechtliche Rollenzuweisung.
- Fachprüfungsstatus bestätigen nur die dokumentierte externe Prüfung; ZONVAA nimmt sie nicht selbst vor.
- Speicherreferenzen sind logisch und von tatsächlichem Dateisystem- oder Cloudzugriff getrennt.
- Das Modell bewertet keine Dokumentwirksamkeit, Vollständigkeit oder Rechtsfolge.
- Es gibt keine automatische Ableitung, Normalisierung oder semantische Bewertung.

## Konsequenzen

- Informationsklassen und fachliche Grenzen sind deterministisch testbar.
- Das Domänenmodell bietet keinen Inhaltskanal; seine syntaktische Referenzprüfung ist keine allgemeine Erkennung sensibler Inhalte.
- Spätere Persistenz- oder Importentscheidungen müssen diese Typ- und Schutzgrenzen erhalten.
- Regionale Rechtsbegriffe und konkrete professionelle Workflows bleiben bewusst späteren Architekturentscheidungen vorbehalten.
