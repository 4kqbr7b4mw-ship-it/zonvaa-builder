import json
import platform
import subprocess
from pathlib import Path


class ProjectState:
    """Sammelt und speichert den technischen Projektzustand."""

    STATE_FILE = Path("knowledge/runtime/current_state.json")

    def _command(self, command: list[str]) -> str:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()

    def collect(self) -> dict:
        state = {
            "python_version": platform.python_version(),
            "pytest_version": self._command(
                ["python3", "-m", "pytest", "--version"]
            ).split()[1],
            "git_branch": self._command(
                ["git", "branch", "--show-current"]
            ),
            "git_commit": self._command(
                ["git", "rev-parse", "--short", "HEAD"]
            ),
            "git_clean": (
                self._command(["git", "status", "--short"]) == ""
            ),
        }

        self.save(state)
        return state

    def save(self, state: dict) -> None:
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self) -> dict:
        if not self.STATE_FILE.exists():
            return {}

        return json.loads(
            self.STATE_FILE.read_text(encoding="utf-8")
        )
