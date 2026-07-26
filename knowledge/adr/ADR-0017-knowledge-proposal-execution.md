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

Bei einem Schreibfehler werden ausschließlich Ressourcen zurückgerollt, deren Erzeugung im aktuellen Lauf mit Geräte- und Inode-Identität protokolliert wurde. Rollback-Fehler werden zusammen mit möglicherweise verbliebenen Ressourcen im strukturierten Ausführungsergebnis gemeldet. Ein mit `--record` angeforderter Apply-Lauf wird auch im Fehlerfall nach Entscheidung und Planung journalisiert; Dokumentinhalte werden dabei nicht in den Plan des Decision Records kopiert.

Diese Mechanismen verhindern, dass ein ausgetauschter Symlink den Schreibzugriff auf das Symlink-Ziel umleitet. Sie bilden jedoch keine dateisystemweite Transaktion: Ein Prozess mit ausreichenden Dateisystemrechten kann einen bereits geöffneten Verzeichnisbestandteil gleichzeitig innerhalb des Repositorys umbenennen oder auf demselben Dateisystem aus dem Repository verschieben. Der Deskriptor bleibt sicher an das ursprünglich geöffnete Verzeichnis gebunden, die erzeugte Datei kann danach aber unter dem verschobenen Verzeichnis liegen. Diese durch Python 3.9 und die verwendeten POSIX-Schnittstellen nicht vollständig schließbare Grenze wird nicht als Race-Freiheit behauptet. Ein unvollständiger Rollback wird ausdrücklich als solcher ausgewiesen und niemals als atomarer Erfolg dargestellt.

## Konsequenzen

- Bestehende Goal-Läufe bleiben ohne `--apply` nicht schreibend.
- Planung und Ausführung bleiben getrennt und maschinenlesbar.
- Dokumentgruppen werden vor jeder Änderung vollständig validiert.
- Bestehendes Wissen wird niemals überschrieben.
- Fehlgeschlagene Apply-Läufe bleiben mit `--record` nachvollziehbar.
- Git-Automatisierung bleibt ausdrücklich außerhalb dieses Schritts.
