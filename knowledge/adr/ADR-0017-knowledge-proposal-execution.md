# ADR-0017 – Knowledge Proposal Execution

## Status

Beschlossen

## Kontext

Der bestehende Planner beschreibt `document.create`- und `git.sync`-Schritte, während die Execution Engine sie ausschließlich als `pending` vorbereitet. Für strukturierte Wissensvorhaben fehlt ein ausdrücklich freigegebener, sicher begrenzter Dateiausführungspfad. Der bestehende Goal-CLI-Standard darf dabei keine schreibenden Nebenwirkungen erhalten.

## Entscheidung

Goal-Invocations können optional unveränderliche `DocumentArtifact`-Objekte mit Aktion `document.create`, relativem Zielpfad und vollständigem UTF-8-Inhalt enthalten. Der bestehende Planner übersetzt sie in seine vorhandene Planstruktur. Ohne Artefakte bleibt sein bisheriger Plan exakt erhalten.

`ExecutionEngine.prepare()` bleibt unverändert und ist weiterhin der Standard. Ein neuer `execute()`-Pfad wird ausschließlich durch das explizite CLI-Flag `--apply` verwendet. Er führt nur genehmigte `document/create`-Schritte aus; `git/sync` bleibt `pending` und erzeugt weder Commit noch Push.

Vor dem ersten Schreiben validiert die Execution Engine die vollständige Dokumentgruppe. Erlaubt sind ausschließlich relative, neue Dateiziele unterhalb von `knowledge/`; `knowledge` selbst ist kein Dateiziel. Absolute Pfade, Traversal, Repository- oder Symlink-Ausbruch, doppelte Ziele und vorhandene Dateien werden abgelehnt.

Der produktive Repository-Root wird durch `git rev-parse --show-toplevel` ermittelt und zusätzlich über einen gültigen `.git`-Marker bestätigt. Dabei werden sowohl `.git`-Verzeichnisse als auch Worktree-Markerdateien unterstützt. Eine davon getrennte, privat benannte Root-Injektion existiert ausschließlich für isolierte Tests und verlangt ebenfalls einen gültigen Marker.

Die Ausführung öffnet den bestätigten Root als Verzeichnisdeskriptor und traversiert von dort ausschließlich mit relativen `dir_fd`-Operationen. Verzeichnisse werden mit `O_DIRECTORY | O_NOFOLLOW`, Zieldateien mit `O_CREAT | O_EXCL | O_NOFOLLOW` geöffnet. Plattformen ohne diese Fähigkeiten werden abgelehnt; es gibt keinen unsicheren Fallback.

Jede erfolgreiche Ressourcenerzeugung wird unmittelbar laufintern protokolliert. Geräte- und Inode-Identität werden ergänzt, sobald sie sicher ermittelt werden können. Kann die Identität nach erfolgreichem `mkdir()` nicht mehr erfasst werden, wird das Verzeichnis nicht riskant gelöscht, sondern als möglicherweise verbliebene Ressource ausgewiesen. Bei einem Schreibfehler werden ausschließlich sicher dem aktuellen Lauf zugeordnete Ressourcen zurückgerollt. Rollback-Fehler werden zusammen mit möglicherweise verbliebenen Ressourcen im strukturierten Ausführungsergebnis gemeldet.

Descriptorbasierte Operationen verhindern, dass Symlinks beim Traversieren oder Erzeugen verfolgt werden. Sie garantieren jedoch nicht, dass ein bereits geöffneter Verzeichniseintrag während des Laufs am ursprünglichen Pfad bleibt. Deshalb wird nach jedem Schreibschritt der geplante Zielpfad erneut ohne Symlink-Folgen geöffnet und seine Geräte- und Inode-Identität mit der tatsächlich erzeugten Datei verglichen. Scheitert diese Zielverifikation, wird der Schritt nicht als abgeschlossen gemeldet, Rollback wird versucht und eine nicht mehr am Ziel erreichbare Ressource bleibt ausdrücklich sichtbar. Diese Prüfung bildet keine dateisystemweite Transaktion; ein Prozess mit ausreichenden Dateisystemrechten kann das geöffnete Verzeichnis weiterhin verschieben, die Ausführung meldet dies aber nicht mehr als normalen Erfolg.

ADR-0017 ergänzt ADR-0016 ausschließlich für ausdrücklich angeforderte Apply-Aufzeichnungen. Normale Decision Records entstehen weiterhin nach einem vollständig abgeschlossenen Application-Service-Flow. Bei `--apply --record` wird nach vorhandener Entscheidung und Planung auch ein Ausführungsfehler als Failure-Record dokumentiert. Neue Records verwenden Schema-Version `2.0` mit einem stabilen Execution-Objekt: Apply-Status, redigierte Schritte, strukturierter Fehler, Rollback-Ergebnis und möglicherweise verbliebene Ressourcen. Vollständige Dokumentinhalte werden weder im journalisierten Plan noch in Execution-Schritten gespeichert.

Der Apply-Status besitzt die Werte `not_requested`, `not_executed`, `completed` und `failed`. `completed` ist nur zulässig, wenn mindestens ein vorgesehener Dokumentenschritt geschrieben und am geplanten Ziel verifiziert wurde. Eine blockierte Entscheidung oder ein Lauf ohne ausführbaren Dokumentenschritt ist `not_executed`; Fehler in Preflight, Schreiben, Zielverifikation oder Rollback sind `failed`.

## Konsequenzen

- Bestehende Goal-Läufe bleiben ohne `--apply` nicht schreibend.
- Planung und Ausführung bleiben getrennt und maschinenlesbar.
- Dokumentgruppen werden vor jeder Änderung vollständig validiert.
- Bestehendes Wissen wird niemals überschrieben.
- Fehlgeschlagene Apply-Läufe bleiben mit `--record` nachvollziehbar.
- Git-Automatisierung bleibt ausdrücklich außerhalb dieses Schritts.
