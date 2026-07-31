# Family Care Cross-Domain Scenario Validation v1

## Zweck und Umfang

Diese Validierung prüft den bestehenden Baustein
`Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie` anhand
anonymisierter, vollständig typisierter Szenarien. Sie ist ein versioniertes
Prüfartefakt und weder Laufzeitlogik noch Reporting-System. Sie interpretiert
keine realen Freitexte und ersetzt keine pflegerische, medizinische,
rechtliche, steuerliche, finanzielle oder immobilienbezogene Fachprüfung.

Alle Szenarien verwenden den vorhandenen Ablauf aus Situation, expliziten
Domain Contributions und Abhängigkeiten, kontrollierter Guardian-Frage,
externer Clarification/Revision, Journey, Professional Review und UI-neutraler
Experience. Es wurde kein zusätzlicher Service, Workflow oder Statusautomat
eingeführt.

## Validierungsmatrix

| Szenario | Beteiligte Domänen | Zentrale Lücke | Kontrollierte Frage | Erwarteter Journey-Status | Externe Klärung | Bestätigte Grenzen |
| --- | --- | --- | --- | --- | --- | --- |
| Plötzlicher Pflegefall nach Krankenhausaufenthalt | Pflege, Gesundheit, Wohnen, Familie | konkreter Unterstützungsbedarf | Welcher konkrete Unterstützungsbedarf ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Unterstützungsbedarf und Rollen müssen extern typisiert werden | keine Versorgungs- oder Wohnempfehlung |
| Schleichende Überforderung | Pflege, Familie, Organisation | Rollenverteilung | Welche aktuelle Rollenverteilung ist ausdrücklich vereinbart? | `NEEDS_CLARIFICATION` | Rollenklärung bleibt extern | keine psychologische Diagnose, keine Heimempfehlung |
| Elternteil mit ungeklärter Vertretung | Life Decisions, Familie, Dokumente | vertretungsberechtigte Person | Welche vertretungsberechtigte Person ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Vertretungsgrundlage und Dokumentprüfung extern | keine Vertretungsannahme oder Wirksamkeitsaussage |
| Familienstreit über Versorgung und Finanzierung | Familie, Finanzen, Pflege | Rollenverteilung | Welche aktuelle Rollenverteilung ist ausdrücklich vereinbart? | `NEEDS_CLARIFICATION` | widersprüchliche Aussagen bleiben extern zu klären | keine Konfliktentscheidung oder Personenpräferenz |
| Pflege im eigenen Haus | Wohnen, Pflege, Finanzen | Wohnform | Welche aktuelle Wohnform ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Barrieren und Prüfbedarf extern | keine Umbau-, Kosten- oder Immobilienbewertung |
| Möglicher stationärer Umzug | Pflege, Wohnen, Finanzen, Familie | Unterstützungsbedarf | Welcher konkrete Unterstützungsbedarf ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Versorgung und Tragbarkeit extern | keine Wahl der Versorgungsform oder Finanzierung |
| Medizinische Unsicherheit | Gesundheit, Pflege | medizinische Ansprechperson | Welche medizinische Ansprechperson ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | medizinische Klärung extern | Vermutung bleibt Hypothese, keine Diagnose |
| Mehrere Angehörige mit Widersprüchen | Familie | Rollenverteilung | Welche aktuelle Rollenverteilung ist ausdrücklich vereinbart? | `NEEDS_CLARIFICATION` | quellenbezogene Rollenklärung extern | keine Mehrheit oder automatische Rollenvergabe |
| Dokumente mit ungeklärtem Stand | Dokumente, Life Decisions | vorhandene Dokumente | Welche vorhandenen Dokumente sind ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Dokumentprüfung extern | nur Referenz, keine Inhaltsanalyse oder Wirksamkeit |
| Mehrere wesentliche Lücken | Pflege, Finanzen | erster Punkt in Eingabereihenfolge | Welcher konkrete Unterstützungsbedarf ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | jede Lücke einzeln extern | genau eine statische Frage, keine Priorisierung |
| Bereits beantwortete Lücke | Pflege | durch Revision belegter Unterstützungsbedarf | keine erneute Frage | `SITUATION_PREPARATION_READY` | vollständige externe Proposal-/Resolution-/Revision-Kette | `ANSWERED_BY_REVISION` bleibt sichtbar |
| Selbst ernannte Entscheidungsperson | Life Decisions, Familie | belegte Vertretungsgrundlage | Welche vertretungsberechtigte Person ist ausdrücklich bekannt? | `NEEDS_CLARIFICATION` | Vertretung und ausdrücklich gewünschte Konfliktprüfung extern | keine Missbrauchsbehauptung, Sperrung oder Eignungsbewertung |

Die Auswahlordnung entspricht ausschließlich der stabilen Reihenfolge der
explizit übergebenen offenen Punkte. Eine geänderte Reihenfolge ist eine andere
semantische Eingabe und wählt entsprechend einen anderen ersten Punkt. Zu
keinem Zeitpunkt entstehen zwei gleichzeitige Fragen oder eine dynamische
Ersatzfrage.

## Robustheitsprüfung

Zusätzlich validiert sind:

- fremde Gap- und Proposal-Ursprungsreferenzen,
- doppelte Clarifications und unvollständige Turn-Historien,
- widersprüchliche beziehungsweise falsch gebundene Revisionen,
- falsch gebundene Professional-Review-Pakete,
- leere Contributions ohne explizite fachliche Grundlage,
- Contributions mit fremdem Understanding-State-Bezug,
- Dependencies mit fehlendem Contribution-Bezug,
- deterministische Wiederholung identischer Eingaben,
- fachlich wirksame Änderung der Eingabereihenfolge,
- ein leerer, formal gültiger Cross-Domain-Fall.

## Gefundene und behobene Befunde

1. Eine leere `FamilyCareDomainContributionInput` konnte eine Domäne formal
   sichtbar machen, obwohl kein fachlicher Inhalt zugewiesen war. Der Vertrag
   verlangt nun mindestens eine explizite Inhalts-, Punkt-, Prüf-, Schritt-
   oder Dependency-Referenz.
2. Eine Dependency konnte eine Domäne benennen, für die keine explizite Domain
   Contribution vorhanden war. Alle Dependency-Domänen müssen nun im konkreten
   Situationseingang ausdrücklich als Contribution existieren.
3. Eine formal korrekte Resolution mit fremdem Proposal-Ursprung konnte
   konsumiert werden. Proposal-Statement und Originaltext müssen nun zu einer
   referenzierten Nutzeraussage der Situation gehören; zusätzlich muss die
   Quellenreferenz der klärenden Antwort übereinstimmen.
4. Der bislang wiederverwendete Review-Kategorietyp konnte pflegefachliche,
   sozialrechtliche, finanzielle, immobilienbezogene und Familien-/Rollen-
   Prüfbedarfe nicht neutral benennen. Die fehlenden Enum-Werte wurden ergänzt;
   ein Review entsteht weiterhin ausschließlich aus einer expliziten Eingabe.

Zwei bestehende Test-Fixtures wurden lediglich vervollständigt: Ein Fall ohne
Contributions enthält nun auch keine Dependency; ein Fremdpunkt-Test entfernt
die für diesen Test irrelevante Dependency. Keine bestehende Assertion wurde
entfernt oder abgeschwächt.

## Bestätigte Sicherheitsgrenzen

- keine automatische Domain-Aktivierung, Contribution oder Dependency,
- keine natürliche Sprachinterpretation und keine dynamische Frage,
- keine Personenbewertung, Empfehlung oder Konfliktentscheidung,
- keine Pflegegrad-, Leistungs-, Finanzierungs- oder Immobilienberechnung,
- keine medizinische Diagnose sowie keine Rechts- oder Steuerberatung,
- keine Umwandlung von Hypothesen in Facts,
- keine Auflösung von Unknowns oder Contradictions,
- keine State-Mutation oder Ausführungsbefugnis der Contributions,
- keine automatische Professional-Review-Aktivierung,
- keine Persistenz, Netzwerk-, LLM-, Routing- oder Agentenlogik.

## Verbleibende Risiken

Die fachliche Güte hängt von vollständigen und korrekt typisierten Eingaben ab.
Der Baustein erkennt keine inhaltlich falsche Nutzeraussage und deutet keine
Freitexte. Externe Proposal-, Resolution- und Revision-Artefakte müssen durch
die dafür bestehenden kontrollierten Komponenten erzeugt werden. Eine
erfolgreiche Szenarioprüfung ist keine Aussage über Pflegegrad, Leistungsrecht,
medizinische Lage, rechtliche Wirksamkeit, Finanzierung oder Immobilienwert.
