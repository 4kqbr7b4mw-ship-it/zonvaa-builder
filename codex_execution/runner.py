import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        return "\n".join(
            item for item in (self.stdout.strip(), self.stderr.strip()) if item
        )


class SubprocessCommandRunner:
    """Runs fixed argv lists without a shell."""

    def run(
        self,
        arguments: Sequence[str],
        cwd: Path,
        input_text: Optional[str] = None,
    ) -> CommandResult:
        if not isinstance(arguments, (tuple, list)) or not arguments:
            raise TypeError("arguments must be a non-empty sequence")
        if not all(isinstance(item, str) and item for item in arguments):
            raise TypeError("arguments must contain strings")
        result = subprocess.run(
            list(arguments),
            cwd=str(cwd),
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )
        return CommandResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
