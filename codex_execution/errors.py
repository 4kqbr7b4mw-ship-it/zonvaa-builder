import re
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence, Tuple

from codex_execution.models import (
    ExecutionFailure,
    ExecutionFailureKind,
    ExecutionStep,
)


_MAX_CAPTURE = 12000
_SECRET_PATTERNS = (
    re.compile(
        r"(?i)(authorization\s*:\s*(?:bearer|basic)\s+)[^\s,;]+"
    ),
    re.compile(
        r"(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|"
        r"password|passwd|secret|credential)\s*[=:]\s*)"
        r"([^\s,;]+)"
    ),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
)
_SECRET_ARGUMENT_NAMES = (
    "authorization",
    "credential",
    "password",
    "passwd",
    "secret",
    "token",
    "api-key",
    "api_key",
)


def redact(value: object, sensitive_values: Sequence[str] = ()) -> str:
    """Redact bounded diagnostic text; stdin and environments are never read."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = str(value)
    for secret in sensitive_values:
        if isinstance(secret, str) and secret:
            text = text.replace(secret, "[REDACTED]")
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    if len(text) > _MAX_CAPTURE:
        text = text[:_MAX_CAPTURE] + "\n[TRUNCATED]"
    return text


class ExecutionBridgeError(RuntimeError):
    def __init__(self, failure: ExecutionFailure) -> None:
        if not isinstance(failure, ExecutionFailure):
            raise TypeError("failure must be ExecutionFailure")
        self.failure = failure
        super().__init__(
            "{}: {}: {}".format(
                failure.step.value,
                failure.exception_type,
                failure.exception_message,
            )
        )


def redact_arguments(
    arguments: Sequence[str],
    sensitive_values: Sequence[str] = (),
) -> Tuple[str, ...]:
    redacted = []
    hide_next = False
    for argument in arguments:
        lowered = argument.lower()
        if hide_next:
            redacted.append("[REDACTED]")
            hide_next = False
            continue
        redacted.append(redact(argument, sensitive_values))
        if any(
            lowered.rstrip("=").endswith(name)
            for name in _SECRET_ARGUMENT_NAMES
        ) and "=" not in argument:
            hide_next = True
    return tuple(redacted)


def failure_from_exception(
    error: BaseException,
    *,
    step: ExecutionStep,
    occurred_at: datetime,
    cwd: Path,
    execution_id: Optional[str] = None,
    arguments: Sequence[str] = (),
    sensitive_values: Sequence[str] = (),
    kind: Optional[ExecutionFailureKind] = None,
) -> ExecutionFailure:
    program = arguments[0] if arguments else None
    argv = redact_arguments(arguments[1:], sensitive_values)
    if kind is None:
        if isinstance(error, FileNotFoundError):
            if program is None:
                kind = ExecutionFailureKind.INPUT_NOT_FOUND
            elif not cwd.is_dir():
                kind = ExecutionFailureKind.WORKING_DIRECTORY_NOT_FOUND
            else:
                kind = ExecutionFailureKind.EXECUTABLE_NOT_FOUND
        elif isinstance(error, (TimeoutError, subprocess.TimeoutExpired)):
            kind = ExecutionFailureKind.TIMEOUT
        elif isinstance(error, OSError):
            kind = ExecutionFailureKind.PROCESS_START_FAILED
        else:
            kind = ExecutionFailureKind.INTERNAL_ERROR
    cause = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    return ExecutionFailure(
        kind=kind,
        step=step,
        program=redact(program, sensitive_values) if program else None,
        arguments=argv,
        working_directory=redact(str(cwd), sensitive_values),
        exit_code=None,
        stdout="",
        stderr="",
        exception_type=type(error).__name__,
        exception_message=redact(error, sensitive_values),
        technical_cause=redact(cause, sensitive_values),
        occurred_at=occurred_at,
        execution_id=execution_id,
    )


def process_failure(
    *,
    step: ExecutionStep,
    occurred_at: datetime,
    cwd: Path,
    arguments: Sequence[str],
    exit_code: int,
    stdout: object,
    stderr: object,
    execution_id: Optional[str],
    sensitive_values: Sequence[str] = (),
) -> ExecutionFailure:
    return ExecutionFailure(
        kind=ExecutionFailureKind.PROCESS_EXIT_NONZERO,
        step=step,
        program=redact(arguments[0], sensitive_values),
        arguments=redact_arguments(arguments[1:], sensitive_values),
        working_directory=redact(str(cwd), sensitive_values),
        exit_code=exit_code,
        stdout=redact(stdout, sensitive_values),
        stderr=redact(stderr, sensitive_values),
        exception_type="ProcessExitError",
        exception_message="Process exited with code {}.".format(exit_code),
        technical_cause=(
            "The process started successfully and returned a non-zero "
            "exit code."
        ),
        occurred_at=occurred_at,
        execution_id=execution_id,
    )
