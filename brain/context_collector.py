from pathlib import Path
import subprocess


class ContextCollector:
    """Sammelt bestätigte Projektinformationen für Agenten."""

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
    }

    IMPORTANT_FILES = [
        "README.md",
        "constitution/constitution.md",
        "foundation/vision.md",
        "foundation/mission.md",
        "foundation/values.md",
        "foundation/manifest.md",
        "builder/main.py",
        "agents/architect.md",
        "agents/handover.md",
        "agents/role_agent.py",
        "agents/tasks.py",
        "brain/context_collector.py",
        "brain/context_analyzer.py",
        "commands/handover.py",
        "commands/doctor.py",
        "commands/init.py",
        "commands/build.py",
        "commands/release.py",
        "commands/role.py",
    ]

    def _run_command(self, command: list[str]) -> str:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return result.stderr.strip() or "Befehl fehlgeschlagen."

        return result.stdout.strip() or "Keine Ausgabe."

    def _read_file(self, file_path: Path) -> str:
        if not file_path.exists():
            return "Datei nicht vorhanden."

        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    def _collect_sessions(self, project_root: Path) -> dict[str, str]:
        sessions_directory = project_root / "knowledge" / "sessions"

        if not sessions_directory.exists():
            return {}

        session_files = sorted(
            sessions_directory.glob("*.md"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        return {
            str(path.relative_to(project_root)): self._read_file(path)
            for path in session_files
        }

    def collect(self) -> dict:
        project_root = Path.cwd()

        files = sorted(
            str(path.relative_to(project_root))
            for path in project_root.rglob("*")
            if path.is_file()
            and not any(
                part in self.IGNORED_DIRECTORIES
                for part in path.parts
            )
        )

        important_files = {
            relative_path: self._read_file(
                project_root / relative_path
            )
            for relative_path in self.IMPORTANT_FILES
        }

        return {
            "project_root": str(project_root),
            "files": files,
            "important_files": important_files,
            "sessions": self._collect_sessions(project_root),
            "git": {
                "branch": self._run_command(
                    ["git", "branch", "--show-current"]
                ),
                "status": self._run_command(
                    [
                        "git",
                        "status",
                        "--short",
                        "--untracked-files=all",
                    ]
                ),
                "recent_commits": self._run_command(
                    ["git", "log", "-5", "--oneline"]
                ),
            },
        }
