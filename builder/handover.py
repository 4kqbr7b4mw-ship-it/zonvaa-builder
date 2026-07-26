import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError("{} must be a string".format(field_name))
    if not value.strip():
        raise ValueError("{} must not be empty".format(field_name))
    if value != value.strip() or "\n" in value or "\r" in value:
        raise ValueError("{} must be a trimmed single line".format(field_name))
    if len(value) > 1000:
        raise ValueError("{} is too long".format(field_name))
    return value


def _require_optional_text(
    value: object,
    field_name: str,
) -> Optional[str]:
    if value is None:
        return None
    return _require_text(value, field_name)


def _require_string_tuple(value: object, field_name: str) -> Tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError("{} must be a list".format(field_name))
    result = tuple(
        _require_text(item, "{} item".format(field_name))
        for item in value
    )
    return result


@dataclass(frozen=True)
class CheckResult:
    command: str
    status: str
    result: str

    def __post_init__(self) -> None:
        _require_text(self.command, "CheckResult command")
        _require_text(self.status, "CheckResult status")
        _require_text(self.result, "CheckResult result")
        if self.status not in {"passed", "failed", "not_run"}:
            raise ValueError("CheckResult status is unknown")


@dataclass(frozen=True)
class HandoverRecord:
    timestamp: datetime
    task: str
    starting_commit: str
    ending_commit: Optional[str]
    changed_files: Tuple[str, ...]
    functional_changes: Tuple[str, ...]
    technical_changes: Tuple[str, ...]
    decisions: Tuple[str, ...]
    relevant_adrs: Tuple[str, ...]
    checks: Tuple[CheckResult, ...]
    open_risks: Tuple[str, ...]
    intentionally_not_implemented: Tuple[str, ...]
    recommended_next_step: str
    git_status: Tuple[str, ...]
    push_status: str

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise TypeError("HandoverRecord timestamp must be a datetime")
        if (
            self.timestamp.tzinfo is None
            or self.timestamp.utcoffset() is None
        ):
            raise ValueError("HandoverRecord timestamp must be timezone-aware")
        _require_text(self.task, "HandoverRecord task")
        _require_text(
            self.starting_commit,
            "HandoverRecord starting_commit",
        )
        _require_optional_text(
            self.ending_commit,
            "HandoverRecord ending_commit",
        )
        for field_name, value in (
            ("starting_commit", self.starting_commit),
            ("ending_commit", self.ending_commit),
        ):
            if value is not None and not re.fullmatch(
                r"[0-9a-fA-F]{7,64}",
                value,
            ):
                raise ValueError(
                    "HandoverRecord {} must be a Git commit id".format(
                        field_name
                    )
                )
        for field_name, value in (
            ("changed_files", self.changed_files),
            ("functional_changes", self.functional_changes),
            ("technical_changes", self.technical_changes),
            ("decisions", self.decisions),
            ("relevant_adrs", self.relevant_adrs),
            ("open_risks", self.open_risks),
            (
                "intentionally_not_implemented",
                self.intentionally_not_implemented,
            ),
            ("git_status", self.git_status),
        ):
            if not isinstance(value, tuple):
                raise TypeError(
                    "HandoverRecord {} must be a tuple".format(field_name)
                )
            for item in value:
                _require_text(item, "HandoverRecord {} item".format(field_name))
        if not isinstance(self.checks, tuple) or not all(
            isinstance(check, CheckResult) for check in self.checks
        ):
            raise TypeError("HandoverRecord checks must contain CheckResult")
        _require_text(
            self.recommended_next_step,
            "HandoverRecord recommended_next_step",
        )
        _require_text(self.push_status, "HandoverRecord push_status")
        if self.push_status not in {"not_pushed", "pushed", "unknown"}:
            raise ValueError("HandoverRecord push_status is unknown")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "timestamp": self.timestamp.isoformat(),
            "task": self.task,
            "starting_commit": self.starting_commit,
            "ending_commit": self.ending_commit,
            "changed_files": list(self.changed_files),
            "functional_changes": list(self.functional_changes),
            "technical_changes": list(self.technical_changes),
            "decisions": list(self.decisions),
            "relevant_adrs": list(self.relevant_adrs),
            "checks": [
                {
                    "command": check.command,
                    "status": check.status,
                    "result": check.result,
                }
                for check in self.checks
            ],
            "open_risks": list(self.open_risks),
            "intentionally_not_implemented": list(
                self.intentionally_not_implemented
            ),
            "recommended_next_step": self.recommended_next_step,
            "git_status": list(self.git_status),
            "push_status": self.push_status,
        }


class HandoverWriter:
    def __init__(self, folder: Path = Path("knowledge/handovers")) -> None:
        self.folder = folder

    def write(self, record: HandoverRecord) -> Tuple[Path, Path]:
        self.folder.mkdir(parents=True, exist_ok=True)
        stem = "{}_{}".format(
            record.timestamp.astimezone(timezone.utc).strftime(
                "%Y-%m-%d_%H-%M-%S-%f"
            ),
            self._safe_name(record.task),
        )
        json_path = self.folder / "{}.json".format(stem)
        markdown_path = self.folder / "{}.md".format(stem)
        self._write_new_atomic(
            json_path,
            json.dumps(
                record.to_dict(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        try:
            self._write_new_atomic(markdown_path, self._markdown(record))
        except BaseException:
            json_path.unlink()
            raise
        return json_path, markdown_path

    def _write_new_atomic(self, target: Path, content: str) -> None:
        if target.exists():
            raise FileExistsError(str(target))
        descriptor, temporary_name = tempfile.mkstemp(
            dir=str(target.parent),
            prefix=".handover-",
            suffix=".tmp",
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary_name, target)
            os.unlink(temporary_name)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def _safe_name(self, value: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
        return normalized[:80] or "handover"

    def _markdown(self, record: HandoverRecord) -> str:
        data = record.to_dict()
        sections = [
            "# Handover: {}".format(record.task),
            "",
            "- Timestamp: `{}`".format(data["timestamp"]),
            "- Starting commit: `{}`".format(record.starting_commit),
            "- Ending commit: `{}`".format(
                record.ending_commit or "missing"
            ),
            "- Push status: `{}`".format(record.push_status),
            "",
        ]
        self._section(sections, "Changed files", record.changed_files)
        self._section(
            sections,
            "Functional changes",
            record.functional_changes,
        )
        self._section(
            sections,
            "Technical changes",
            record.technical_changes,
        )
        self._section(sections, "Decisions", record.decisions)
        self._section(sections, "Relevant ADRs", record.relevant_adrs)
        sections.extend(["## Checks", ""])
        if record.checks:
            sections.extend(
                "- `{}`: **{}** — {}".format(
                    check.command,
                    check.status,
                    check.result,
                )
                for check in record.checks
            )
        else:
            sections.append("- Missing")
        sections.append("")
        self._section(sections, "Open risks", record.open_risks)
        self._section(
            sections,
            "Intentionally not implemented",
            record.intentionally_not_implemented,
        )
        sections.extend(
            [
                "## Recommended next step",
                "",
                record.recommended_next_step,
                "",
            ]
        )
        self._section(sections, "Git status", record.git_status)
        return "\n".join(sections)

    def _section(
        self,
        target: list,
        title: str,
        values: Tuple[str, ...],
    ) -> None:
        target.extend(["## {}".format(title), ""])
        target.extend(
            ["- {}".format(value) for value in values] or ["- None"]
        )
        target.append("")


def load_handover_input(path: Path) -> HandoverRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("Handover input must be a JSON object")
    expected = {
        "task",
        "timestamp",
        "starting_commit",
        "ending_commit",
        "changed_files",
        "functional_changes",
        "technical_changes",
        "decisions",
        "relevant_adrs",
        "checks",
        "open_risks",
        "intentionally_not_implemented",
        "recommended_next_step",
        "git_status",
        "push_status",
    }
    missing = expected - set(data)
    unknown = set(data) - expected
    if missing or unknown:
        raise ValueError(
            "Invalid handover fields; missing={}, unknown={}".format(
                sorted(missing),
                sorted(unknown),
            )
        )
    checks = data["checks"]
    if not isinstance(checks, list):
        raise TypeError("checks must be a list")
    if not all(
        isinstance(check, dict)
        and set(check) == {"command", "status", "result"}
        for check in checks
    ):
        raise ValueError("Each check must contain command, status, and result")
    return HandoverRecord(
        timestamp=_parse_timestamp(data["timestamp"]),
        task=_require_text(data["task"], "task"),
        starting_commit=_require_text(
            data["starting_commit"],
            "starting_commit",
        ),
        ending_commit=_require_optional_text(
            data["ending_commit"],
            "ending_commit",
        ),
        changed_files=_require_string_tuple(
            data["changed_files"],
            "changed_files",
        ),
        functional_changes=_require_string_tuple(
            data["functional_changes"],
            "functional_changes",
        ),
        technical_changes=_require_string_tuple(
            data["technical_changes"],
            "technical_changes",
        ),
        decisions=_require_string_tuple(data["decisions"], "decisions"),
        relevant_adrs=_require_string_tuple(
            data["relevant_adrs"],
            "relevant_adrs",
        ),
        checks=tuple(
            CheckResult(
                command=check["command"],
                status=check["status"],
                result=check["result"],
            )
            for check in checks
        ),
        open_risks=_require_string_tuple(
            data["open_risks"],
            "open_risks",
        ),
        intentionally_not_implemented=_require_string_tuple(
            data["intentionally_not_implemented"],
            "intentionally_not_implemented",
        ),
        recommended_next_step=_require_text(
            data["recommended_next_step"],
            "recommended_next_step",
        ),
        git_status=_require_string_tuple(data["git_status"], "git_status"),
        push_status=_require_text(data["push_status"], "push_status"),
    )


def _parse_timestamp(value: object) -> datetime:
    text = _require_text(value, "timestamp")
    try:
        timestamp = datetime.fromisoformat(text)
    except ValueError as error:
        raise ValueError("timestamp must be valid ISO-8601") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return timestamp
