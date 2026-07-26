# Life Decisions Roadmap

## 1. Domänenmodell und Grenzen

**Ziel:** Begriffe, Verantwortlichkeiten, Informationsklassen und fachliche Grenzen verbindlich definieren.

**Konkrete Ergebnisse:** Domänenlexikon, Akteursmodell, Dokument-/Fakten-/Interpretations-/Entscheidungsabgrenzung, Disclaimer-Vertrag.

**Abnahmekriterien:** Jede Kernentität besitzt Quelle, Version und Prüfstatus; fachliche Beratung ist klar ausgeschlossen.

**Wesentliche Risiken:** Vermischung von Fakten und Interpretation; scheinbare Rechtsberatung.

**Ausgeschlossen:** automatische Wirksamkeitsprüfung und individuelle Rechtsauskunft.

## 2. Nutzerkontrollierter Dokumententresor

**Ziel:** Originale unter Kontrolle des Nutzers referenzieren und schützen.

**Konkrete Ergebnisse:** Speicherort-Abstraktion für lokal, NAS und persönlichen Cloudspeicher; Referenz- und Zugriffskonzept.

**Abnahmekriterien:** Kein Original muss zentral zu ZONVAA kopiert werden; Zugriffe sind explizit und widerrufbar.

**Wesentliche Risiken:** Fehlkonfiguration, Verfügbarkeitsverlust, unklare Besitzverhältnisse.

**Ausgeschlossen:** zentraler ZONVAA-Dokumentbesitz und automatische Migration aller Dateien.

## 3. Dokumentimport und lokale Metadaten

**Ziel:** Freigegebene Dokumente erfassen, ohne Original und Metadaten zu vermischen.

**Konkrete Ergebnisse:** Importvertrag, lokale Metadaten, Prüfsummen, Quelle, Version und Importstatus.

**Abnahmekriterien:** Import ist reproduzierbar; Änderungen am Original werden erkannt; Herkunft bleibt sichtbar.

**Wesentliche Risiken:** veraltete Referenzen, falsche Dateizuordnung, unvollständige Metadaten.

**Ausgeschlossen:** stiller Hintergrundimport und ungefragte Inhaltsanalyse.

## 4. Schwärzung und Datenminimierung

**Ziel:** Externe Verarbeitung auf ausdrücklich notwendige Inhalte begrenzen.

**Konkrete Ergebnisse:** lokale Vorschau, manuelle Schwärzung, Löschung, Freigabeprotokoll und minimierte Exportpakete.

**Abnahmekriterien:** Nutzer sehen und bestätigen jeden extern verarbeiteten Inhalt; Schwärzungen sind vor Versand wirksam.

**Wesentliche Risiken:** unvollständige Schwärzung, Metadatenlecks, irrtümliche Freigaben.

**Ausgeschlossen:** automatische externe Übertragung und irreversible Bearbeitung des Originals.

## 5. Strukturierte Vorsorge-Checklisten

**Ziel:** Themenabhängige Fragen, fehlende Angaben und nächste Schritte nachvollziehbar strukturieren.

**Konkrete Ergebnisse:** versionierte Checklisten für Nachlass, Vollmachten, Verfügungen, Notfälle und digitale Konten.

**Abnahmekriterien:** Antworten bleiben quellenbezogen; fehlende Angaben werden sichtbar; keine Antwort wird erfunden.

**Wesentliche Risiken:** falsche Vollständigkeitssignale, regionale Unterschiede, veraltete Fragen.

**Ausgeschlossen:** automatische Dokumenterstellung mit behaupteter rechtlicher Gültigkeit.

## 6. Fakten-, Quellen- und Unsicherheitsmodell

**Ziel:** Bestätigte Fakten, Behauptungen, Interpretationen und Unsicherheiten strikt trennen.

**Konkrete Ergebnisse:** Provenienzmodell, Confidence-/Prüfstatus, Konflikterkennung und Versionierung.

**Abnahmekriterien:** Jede Aussage ist klassifiziert; Konflikte werden nicht still aufgelöst; fachliche Prüfung ist sichtbar.

**Wesentliche Risiken:** falsche Bestätigung, Quellenverlust, übersehene Widersprüche.

**Ausgeschlossen:** semantische Gewissheit ohne Beleg und automatische Hochstufung zu bestätigten Fakten.

## 7. Vertrauenspersonen und Berechtigungen

**Ziel:** Rollen, Zuständigkeiten und minimal notwendige Zugriffe sicher verwalten.

**Konkrete Ergebnisse:** Vertrauenspersonenmodell, granulare Freigaben, Notfallzugriffskonzept, Widerruf und Auditspur.

**Abnahmekriterien:** Zugriffe sind zweckgebunden, zeitlich nachvollziehbar und widerrufbar; kein impliziter Vollzugriff.

**Wesentliche Risiken:** Identitätsmissbrauch, zu breite Rechte, Konflikte zwischen Beteiligten.

**Ausgeschlossen:** automatische Ernennung von Vertretern und unkontrollierter Familienzugriff.

## 8. Erinnerungen und regelmäßige Überprüfung

**Ziel:** Entscheidungen, Dokumente und Zuständigkeiten aktuell halten.

**Konkrete Ergebnisse:** überprüfbare Termine, Ereignis-Trigger, Erinnerungshistorie und bestätigte Aktualisierungen.

**Abnahmekriterien:** Erinnerungen sind nachvollziehbar und abschaltbar; Aktualisierung verändert keine Originale ohne Freigabe.

**Wesentliche Risiken:** Erinnerungsmüdigkeit, verpasste Ereignisse, falsche Aktualitätsannahmen.

**Ausgeschlossen:** automatische inhaltliche Änderung oder Verlängerung von Dokumenten.

## 9. Vorbereitung fachlicher Beratung

**Ziel:** Offene Fragen, Fakten, Unsicherheiten und gewünschte Entscheidungen für Fachgespräche bündeln.

**Konkrete Ergebnisse:** exportierbare Gesprächsagenda, Quellenliste, Konfliktübersicht und explizite Prüfaufträge.

**Abnahmekriterien:** Ausgabe trennt Nutzerangaben und ZONVAA-Interpretationen; Disclaimer und Prüfstatus sind enthalten.

**Wesentliche Risiken:** missverständliche Zusammenfassungen, fehlender Kontext, Nutzung als Beratungsersatz.

**Ausgeschlossen:** Auswahl oder Beauftragung von Fachleuten und verbindliche Handlungsempfehlungen.

## 10. Sicherheits-, Datenschutz- und Missbrauchstests

**Ziel:** Schutzmechanismen und fachliche Grenzen vor Freigabe systematisch verifizieren.

**Konkrete Ergebnisse:** Threat Model, Berechtigungs-, Lösch-, Redaktions-, Datenabfluss- und Missbrauchstests sowie Incident-Prozess.

**Abnahmekriterien:** Kritische Tests bestehen; Löschungen und Widerrufe sind nachweisbar; bekannte Restrisiken sind dokumentiert.

**Wesentliche Risiken:** Datenabfluss, unbemerkte Wiederverwendung, Social Engineering, unvollständige Löschung.

**Ausgeschlossen:** Produktivfreigabe bei offenen kritischen Sicherheits- oder Datenschutzbefunden.
