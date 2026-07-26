import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

from knowledge.verified_facts import VerifiedFacts


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
        if result.returncode != 0:
            message = result.stderr.strip() or "command failed"
            raise RuntimeError(
                "{}: {}".format(" ".join(command), message)
            )
        return result.stdout.strip()

    def collect(self) -> dict:
        pytest_output = self._command(
            ["python3", "-m", "pytest", "--version"]
        ).split()
        if len(pytest_output) < 2:
            raise RuntimeError("pytest version could not be determined")
        state = {
            "verified_facts": VerifiedFacts().load(),
            "python_version": platform.python_version(),
            "pytest_version": pytest_output[1],
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
        serialized = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
        descriptor, temporary_name = tempfile.mkstemp(
            dir=str(self.STATE_FILE.parent),
            prefix=".current-state-",
            suffix=".tmp",
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self.STATE_FILE)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def load(self) -> dict:
        if not self.STATE_FILE.exists():
            return {}

        return json.loads(
            self.STATE_FILE.read_text(encoding="utf-8")
        )
