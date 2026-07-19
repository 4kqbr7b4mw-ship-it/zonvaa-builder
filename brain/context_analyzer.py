from typing import Any


class ContextAnalyzer:
    """Verdichtet gesammelten Projektkontext zu relevanten Fakten."""

    def analyze(
        self,
        project_context: dict[str, Any],
    ) -> dict[str, Any]:
        git = project_context.get("git", {})
        files = project_context.get("files", [])
        sessions = project_context.get("sessions", {})

        changed_files = self._parse_git_status(
            git.get("status", "")
        )

        relevant_files = [
            file_path
            for file_path in files
            if file_path.startswith(
                (
                    "builder/",
                    "commands/",
                    "agents/",
                    "brain/",
                    "config/",
                    "tests/",
                    "knowledge/sessions/",
                )
            )
        ]

        latest_session_path = next(iter(sessions), None)
        latest_session_content = (
            sessions.get(latest_session_path, "")
            if latest_session_path
            else ""
        )

        return {
            "project_root": project_context.get(
                "project_root",
                "Nicht bestätigt",
            ),
            "git": {
                "branch": git.get(
                    "branch",
                    "Nicht bestätigt",
                ),
                "changed_files": changed_files,
                "recent_commits": git.get(
                    "recent_commits",
                    "Nicht bestätigt",
                ),
            },
            "relevant_files": relevant_files,
            "important_files": project_context.get(
                "important_files",
                {},
            ),
            "sessions": sessions,
            "latest_session": {
                "path": latest_session_path or "Nicht vorhanden",
                "content": latest_session_content,
            },
            "summary": {
                "file_count": len(files),
                "relevant_file_count": len(relevant_files),
                "changed_file_count": len(changed_files),
                "session_count": len(sessions),
                "git_dirty": bool(changed_files),
            },
            "risks": self._detect_risks(
                changed_files=changed_files,
                files=files,
            ),
        }

    def _parse_git_status(
        self,
        git_status: str,
    ) -> list[dict[str, str]]:
        if not git_status or git_status == "Keine Ausgabe.":
            return []

        changes = []

        for line in git_status.splitlines():
            if len(line) < 2:
                continue

            status = line[:2].strip()
            path = line[2:].strip()

            changes.append(
                {
                    "status": status,
                    "path": path,
                }
            )

        return changes

    def _detect_risks(
        self,
        changed_files: list[dict[str, str]],
        files: list[str],
    ) -> list[str]:
        risks = []

        if changed_files:
            risks.append(
                "Der aktuelle Arbeitsstand ist noch nicht vollständig versioniert."
            )

        if (
            "roles/architect.md" in files
            and "agents/architect.md" in files
        ):
            risks.append(
                "Rollen liegen gleichzeitig unter roles/ und agents/."
            )

        if "commands/build.py" in files:
            risks.append(
                "Der Build-Command existiert, seine CLI-Registrierung muss geprüft werden."
            )

        if "commands/release.py" in files:
            risks.append(
                "Der Release-Command existiert, sein Inhalt muss geprüft werden."
            )

        return risks
