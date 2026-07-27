import subprocess
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

from codex_execution.errors import (
    ExecutionBridgeError,
    failure_from_exception,
    redact,
)
from codex_execution.models import ExecutionStep


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
        step: ExecutionStep = ExecutionStep.REPOSITORY_INSPECTION,
        execution_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        sensitive_values: Sequence[str] = (),
    ) -> CommandResult:
        if not isinstance(arguments, (tuple, list)) or not arguments:
            raise TypeError("arguments must be a non-empty sequence")
        if not all(isinstance(item, str) and item for item in arguments):
            raise TypeError("arguments must contain strings")
        try:
            result = subprocess.run(
                list(arguments),
                cwd=str(cwd),
                input=input_text,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            failure = failure_from_exception(
                error,
                step=step,
                occurred_at=datetime.now(timezone.utc),
                cwd=cwd,
                execution_id=execution_id,
                arguments=arguments,
                sensitive_values=sensitive_values,
            )
            raise ExecutionBridgeError(
                replace(
                    failure,
                    stdout=redact(error.stdout, sensitive_values),
                    stderr=redact(error.stderr, sensitive_values),
                )
            ) from error
        except Exception as error:
            raise ExecutionBridgeError(
                failure_from_exception(
                    error,
                    step=step,
                    occurred_at=datetime.now(timezone.utc),
                    cwd=cwd,
                    execution_id=execution_id,
                    arguments=arguments,
                    sensitive_values=sensitive_values,
                )
            ) from error
        return CommandResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
