import errno
import os
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, List, Optional, Tuple

from execution.repository import confirmed_repository_root

_SECURE_DIR_FD_SUPPORTED = all(
    function in os.supports_dir_fd
    for function in (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
)


class ExecutionError(RuntimeError):
    """A document group failed, with an inspectable rollback outcome."""

    def __init__(
        self,
        message: str,
        *,
        error_type: str,
        completed_steps: List[str],
        rolled_back_steps: List[str],
        remaining_resources: List[str],
        rollback_errors: List[str],
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.completed_steps = completed_steps
        self.rolled_back_steps = rolled_back_steps
        self.remaining_resources = remaining_resources
        self.rollback_errors = rollback_errors

    def as_execution_result(self) -> dict:
        return {
            "status": "failed",
            "completed_steps": self.completed_steps,
            "rolled_back_steps": self.rolled_back_steps,
            "remaining_resources": self.remaining_resources,
            "error": {
                "type": self.error_type,
                "message": str(self),
                "rollback_errors": self.rollback_errors,
            },
        }


@dataclass(frozen=True)
class _CreatedResource:
    parts: Tuple[str, ...]
    device: int
    inode: int


class ExecutionEngine:
    """Bereitet genehmigte Pläne für die Ausführung vor."""

    def prepare(
        self,
        plan: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                **step,
                "execution_status": "pending",
            }
            for step in plan
        ]

    def execute(
        self,
        plan: list[dict[str, Any]],
        *,
        _test_repository_root: Optional[Path] = None,
    ) -> list[dict[str, Any]]:
        self._require_secure_platform()
        root = confirmed_repository_root(_test_repository_root)
        validated_targets = self._validate_document_steps(plan)
        root_fd = os.open(
            str(root),
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        created_files: List[_CreatedResource] = []
        created_directories: List[_CreatedResource] = []
        completed_steps: List[str] = []
        try:
            self._preflight(validated_targets, root_fd)
            for _, parts, content in validated_targets:
                parent_fd = self._open_or_create_directories(
                    root_fd,
                    parts[:-1],
                    created_directories,
                )
                try:
                    file_fd = os.open(
                        parts[-1],
                        os.O_WRONLY
                        | os.O_CREAT
                        | os.O_EXCL
                        | os.O_NOFOLLOW,
                        0o644,
                        dir_fd=parent_fd,
                    )
                    stat = os.fstat(file_fd)
                    resource = _CreatedResource(parts, stat.st_dev, stat.st_ino)
                    created_files.append(resource)
                    try:
                        output_file = os.fdopen(file_fd, "w", encoding="utf-8")
                    except BaseException:
                        os.close(file_fd)
                        raise
                    with output_file:
                        output_file.write(content)
                    completed_steps.append("/".join(parts))
                finally:
                    os.close(parent_fd)
        except (OSError, UnicodeError, ValueError) as exc:
            if (
                isinstance(exc, ValueError)
                and not created_files
                and not created_directories
            ):
                raise
            rolled_back, remaining, rollback_errors = self._rollback(
                root_fd,
                created_files,
                created_directories,
            )
            detail = "Document group could not be written: {}".format(exc)
            if rollback_errors:
                detail += "; rollback incomplete: {}".format(
                    "; ".join(rollback_errors)
                )
            raise ExecutionError(
                detail,
                error_type=type(exc).__name__,
                completed_steps=completed_steps,
                rolled_back_steps=rolled_back,
                remaining_resources=remaining,
                rollback_errors=rollback_errors,
            ) from exc
        finally:
            os.close(root_fd)

        completed_steps = {id(step) for step, _, _ in validated_targets}
        return [
            {
                **step,
                "execution_status": (
                    "completed" if id(step) in completed_steps else "pending"
                ),
            }
            for step in plan
        ]

    def _validate_document_steps(
        self,
        plan: list[dict[str, Any]],
    ) -> list:
        validated = []
        targets = set()
        for step in plan:
            if not (
                step.get("agent") == "document"
                and step.get("action") == "create"
            ):
                continue

            target_value = step.get("target")
            content = step.get("content")
            if not isinstance(target_value, str) or not target_value:
                raise ValueError("document.create target must be a relative path")
            if not isinstance(content, str):
                raise ValueError("document.create content must be a string")

            relative = Path(target_value)
            if relative.is_absolute() or PureWindowsPath(target_value).is_absolute():
                raise ValueError("Absolute document paths are not allowed")
            if ".." in relative.parts:
                raise ValueError("Document path traversal is not allowed")
            if len(relative.parts) < 2 or relative.parts[0] != "knowledge":
                raise ValueError("Document targets must be below knowledge/")
            parts = tuple(relative.parts)
            if parts in targets:
                raise ValueError(
                    "Duplicate document target: {}".format(target_value)
                )
            targets.add(parts)
            validated.append((step, parts, content))

        for target in targets:
            if any(
                target != other and target == other[: len(target)]
                for other in targets
            ):
                raise ValueError(
                    "Document target conflicts with a parent target: {}".format(
                        "/".join(target)
                    )
                )
        return validated

    def _require_secure_platform(self) -> None:
        required_flags = ("O_NOFOLLOW", "O_EXCL", "O_CREAT", "O_DIRECTORY")
        if any(not hasattr(os, flag) for flag in required_flags):
            raise RuntimeError(
                "Secure document creation is not supported on this platform"
            )
        if not _SECURE_DIR_FD_SUPPORTED:
            raise RuntimeError(
                "Secure dir_fd operations are not supported on this platform"
            )

    def _preflight(self, validated_targets: list, root_fd: int) -> None:
        for _, parts, _ in validated_targets:
            parent_fd = self._open_existing_prefix(root_fd, parts[:-1])
            if parent_fd is None:
                continue
            try:
                try:
                    os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise ValueError(
                    "Document target already exists: {}".format("/".join(parts))
                )
            finally:
                os.close(parent_fd)

    def _open_existing_prefix(
        self,
        root_fd: int,
        parts: Tuple[str, ...],
    ) -> Optional[int]:
        current_fd = os.dup(root_fd)
        for part in parts:
            try:
                next_fd = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=current_fd,
                )
            except FileNotFoundError:
                os.close(current_fd)
                return None
            except OSError as exc:
                os.close(current_fd)
                if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                    raise ValueError("Symlink document paths are not allowed") from exc
                raise
            os.close(current_fd)
            current_fd = next_fd
        return current_fd

    def _open_or_create_directories(
        self,
        root_fd: int,
        parts: Tuple[str, ...],
        created: List[_CreatedResource],
    ) -> int:
        current_fd = os.dup(root_fd)
        traversed: Tuple[str, ...] = ()
        for part in parts:
            traversed += (part,)
            try:
                next_fd = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=current_fd,
                )
            except FileNotFoundError:
                os.mkdir(part, 0o755, dir_fd=current_fd)
                next_fd = os.open(
                    part,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=current_fd,
                )
                stat = os.fstat(next_fd)
                created.append(
                    _CreatedResource(traversed, stat.st_dev, stat.st_ino)
                )
            except OSError as exc:
                if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                    raise ValueError("Symlink document paths are not allowed") from exc
                raise
            finally:
                os.close(current_fd)
            current_fd = next_fd
        return current_fd

    def _rollback(
        self,
        root_fd: int,
        files: List[_CreatedResource],
        directories: List[_CreatedResource],
    ) -> Tuple[List[str], List[str], List[str]]:
        rolled_back: List[str] = []
        remaining: List[str] = []
        errors: List[str] = []
        for resource, is_directory in [
            *((resource, False) for resource in reversed(files)),
            *((resource, True) for resource in reversed(directories)),
        ]:
            name = "/".join(resource.parts)
            try:
                parent_fd = self._open_existing_prefix(root_fd, resource.parts[:-1])
                if parent_fd is None:
                    raise OSError("parent directory is no longer available")
                try:
                    current = os.stat(
                        resource.parts[-1],
                        dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                    if (
                        current.st_dev != resource.device
                        or current.st_ino != resource.inode
                    ):
                        raise OSError("resource identity changed")
                    operation = os.rmdir if is_directory else os.unlink
                    operation(resource.parts[-1], dir_fd=parent_fd)
                finally:
                    os.close(parent_fd)
                rolled_back.append(name)
            except (OSError, ValueError) as exc:
                remaining.append(name)
                errors.append("{}: {}".format(name, exc))
        return rolled_back, remaining, errors
