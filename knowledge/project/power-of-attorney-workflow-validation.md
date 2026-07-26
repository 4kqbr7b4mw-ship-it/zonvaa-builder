# Fachliche Validierung: Vorsorgevollmacht-Workflow

## Umfang

Validiert wurde der bestehende Workflow
`power_of_attorney_preparation_review` mit anonymisierten, vollständig lokalen
Modell-Fixtures. Die Prüfung umfasst keine Dokumentanalyse und keine Aussage
über rechtliche Wirksamkeit, Formvorgaben oder individuelle Rechtsfolgen.

## Fallmatrix

| Fall | Erwartetes Verhalten | Tatsächliches Verhalten |
| --- | --- | --- |
| Eine bevollmächtigte Person | Bestätigte Fakten und explizite Prüfung bleiben referenziert; Übersicht ist bereit. | `structured_overview_ready`; stabile Fakt-, Prüfungs-, Termin- und Aktions-IDs. |
| Zwei Bevollmächtigte, Vertretungsart unklar | Unklarheit darf nicht als Einzel- oder Gesamtvertretung bestätigt werden. | `unknown` benötigt eine offene Frage; Status `needs_clarification`. |
| Immobilienvermögen | Immobilienbereich sichtbar; eine ausdrücklich angeforderte notarielle Prüfung bleibt offen. | Immobilien-Fakt und offene notarielle Prüfungs-ID werden ausgegeben; keine pauschale Notarpflicht wird abgeleitet. |
| Alte ungeprüfte Vollmacht | Fehlendes Prüfdatum erzeugt Frage und Aktualitätsunsicherheit. | Beide Referenzen bleiben sichtbar; Status `needs_clarification`. |
| Möglicher Interessenkonflikt | Konflikt darf nicht als widerlegt gelten. | Unsicherheits-ID bleibt erhalten; Status `needs_clarification`. |
| Digitale Konten und Vermögenswerte | Bereich und nutzerdefinierter organisatorischer Schritt bleiben referenziert. | Digitale Bereichs-Fakt-ID und Aktions-ID werden deterministisch ausgegeben. |
| Bereitschaft unklar | Keine bestätigte Bereitschaft erfinden. | Offene Frage statt Faktreferenz; Status `needs_clarification`. |
| Mehrere möglicherweise widersprüchliche Vollmachten | Alle Dokumente mit bestätigter Grundlage demselben Fall zuordnen; Widerspruch nicht selbst auflösen. | Zusätzliches Dokument-/Fakt-ID-Paar wird validiert; Frage und Unsicherheit bleiben sichtbar. |

Jeder Fall wurde zweimal ausgeführt. Die Ergebnisse waren wertgleich und
enthielten ausschließlich stabile IDs und Statuswerte. Speicherreferenzen,
Personenbezeichnungen, Dokumentinhalte und Fall-Freitexte wurden nicht
ausgegeben.

## Missbrauchs- und Grenzprüfung

- Aufforderungen, rechtliche Wirksamkeit zu garantieren oder rechtssichere
  Formulierungen zu liefern, werden nicht in die Ausgabe übernommen.
- Eine pauschale Behauptung notarieller Erforderlichkeit erzeugt keine
  automatische Fachprüfung oder Rechtsaussage.
- Offene Unsicherheiten bleiben trotz einer Aufforderung, sie zu ignorieren,
  im Ergebnis und erzwingen `needs_clarification`.
- Eine abgeschlossene Fachprüfung benötigt jetzt einen
  `professionally_confirmed` Fakt; eine reine Nutzerbestätigung wird
  abgelehnt.
- `data:`-URIs und offensichtlich eingebettete Base64-Inhalte werden bereits
  durch `DocumentReference` abgelehnt.
- Auch missbräuchlicher Freitext eines organisatorischen Schritts wird nicht
  in der maschinenlesbaren Ausgabe gespiegelt.

## Gefundene Schwächen und Korrekturen

1. Die Vertretungsart konnte nur als `individual` oder `joint` angegeben
   werden. `unknown` mit verpflichtender Frage wurde ergänzt.
2. Die Dokumentprüfung konnte nur eine Vollmacht binden. Weitere
   Dokumentreferenzen können nun als eindeutige, fallzugehörige Dokument- und
   Fakt-ID-Paare derselben Prüfung angegeben werden.
3. Jeder bestätigte Fakt konnte einen professionellen Prüfabschluss belegen.
   Zulässig ist nun ausschließlich `professionally_confirmed`.

## Verbleibende Grenzen

- Der Workflow erkennt Freitextabsichten nicht semantisch. Seine
  Sicherheitsgrenze ist, solche Texte weder als Rechtsaussage zu verwenden
  noch in die Ausgabe zu übernehmen.
- Er erkennt keine Widersprüche in Dokumenten und liest keine Dokumente.
  Widersprüche müssen als nutzerkontrollierte Frage und Unsicherheit erfasst
  werden.
- Fachprüfbedarfe und organisatorische Schritte werden nicht automatisch
  empfohlen. Sie bleiben explizite, überprüfbare Eingaben.
- Es gibt keine Persistenz, Dokumenterzeugung, Netzwerk-, Cloud- oder
  UI-Funktion.
