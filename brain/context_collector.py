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
