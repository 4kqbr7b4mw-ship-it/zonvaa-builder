from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable, Optional, Sequence, Tuple


CommandRunner = Callable[[Sequence[str], Path], subprocess.CompletedProcess]


@dataclass(frozen=True)
class GitSnapshot:
    repository_path: str
    branch: str
    local_head: str
    remote_head: str
    divergence: str
    working_tree: str
    status_entries: Tuple[str, ...]


def _run_command(
    arguments: Sequence[str],
    repository: Path,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        tuple(arguments),
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )


class ChatHandover:
    def __init__(
        self,
        repository: Path,
        runner: CommandRunner = _run_command,
    ) -> None:
        self.repository = repository.resolve()
        self.runner = runner
        self.agents_path = self.repository / "AGENTS.md"
        self.status_path = (
            self.repository
            / "knowledge"
            / "project"
            / "current-product-status.md"
        )

    def render(self) -> str:
        working_context = self._section(
            self.agents_path,
            "Kanonischer Arbeitskontext",
        )
        active_repository = self._section(
            self.status_path,
            "Aktives Repository",
        )
        completed = self._section(
            self.status_path,
            "Abgeschlossene Produktbausteine",
        )
        current = self._section(
            self.status_path,
            "Aktueller fachlicher Stand",
        )
        boundaries = self._section(
            self.status_path,
            "Bewusste Produktgrenzen",
        )
        next_step = self._section(
            self.status_path,
            "Nächster noch nicht begonnener Schritt",
        )
        expected_branch = self._bullet_value(
            active_repository,
            "Erwarteter Branch",
        )
        snapshot = self._git_snapshot(expected_branch)

        lines = [
            "# ZONVAA V2 Chat-Übergabe",
            "",
            "## Repository",
            "",
            "- Pfad: `{}`".format(snapshot.repository_path),
            "- Branch: `{}`".format(snapshot.branch),
            "- Lokaler HEAD: `{}`".format(snapshot.local_head),
            "- Remote-HEAD: `{}`".format(snapshot.remote_head),
            "- Ahead/Behind: {}".format(snapshot.divergence),
            "- Arbeitsbaum: {}".format(snapshot.working_tree),
        ]
        if expected_branch and snapshot.branch != expected_branch:
            lines.append(
                "- Branch-Abweichung: erwartet `{}`, tatsächlich `{}`".format(
                    expected_branch,
                    snapshot.branch,
                )
            )
        if snapshot.status_entries:
            lines.extend(
                ["- Git-Status:"]
                + [
                    "  - `{}`".format(entry)
                    for entry in snapshot.status_entries
                ]
            )
        lines.extend(
            [
                "",
                "## Kanonische Arbeitsweise",
                "",
                working_context,
                "",
                "## Abgeschlossene Produktbausteine",
                "",
                completed,
                "",
                "## Aktueller fachlicher Stand",
                "",
                current,
                "",
                "## Bewusste Produktgrenzen",
                "",
                boundaries,
                "",
                "## Nächster noch nicht begonnener Schritt",
                "",
                next_step,
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    def _git_snapshot(self, expected_branch: Optional[str]) -> GitSnapshot:
        root = self._git_value(("git", "rev-parse", "--show-toplevel"))
        branch = self._git_value(
            ("git", "branch", "--show-current"),
            empty="DETACHED HEAD oder nicht ermittelbar",
        )
        local_head = self._git_value(("git", "rev-parse", "HEAD"))
        status_result = self.runner(
            ("git", "status", "--short", "--untracked-files=all"),
            self.repository,
        )
        if status_result.returncode == 0:
            status_entries = tuple(
                line
                for line in status_result.stdout.splitlines()
                if line
            )
            working_tree = (
                "sauber" if not status_entries else "nicht sauber"
            )
        else:
            status_entries = ()
            working_tree = "nicht ermittelbar"

        branch_for_remote = branch
        if branch.startswith("DETACHED"):
            branch_for_remote = expected_branch or ""
        remote_ref = (
            "refs/remotes/origin/{}".format(branch_for_remote)
            if branch_for_remote
            else ""
        )
        remote_head = "nicht verfügbar"
        divergence = "nicht verfügbar"
        if remote_ref:
            remote_result = self.runner(
                ("git", "rev-parse", "--verify", remote_ref + "^{commit}"),
                self.repository,
            )
            if remote_result.returncode == 0 and remote_result.stdout.strip():
                remote_head = remote_result.stdout.strip()
                divergence_result = self.runner(
                    (
                        "git",
                        "rev-list",
                        "--left-right",
                        "--count",
                        remote_ref + "...HEAD",
                    ),
                    self.repository,
                )
                values = divergence_result.stdout.split()
                if divergence_result.returncode == 0 and len(values) == 2:
                    divergence = "{} behind / {} ahead".format(
                        values[0],
                        values[1],
                    )

        return GitSnapshot(
            repository_path=root,
            branch=branch,
            local_head=local_head,
            remote_head=remote_head,
            divergence=divergence,
            working_tree=working_tree,
            status_entries=status_entries,
        )

    def _git_value(
        self,
        arguments: Sequence[str],
        empty: str = "nicht ermittelbar",
    ) -> str:
        result = self.runner(arguments, self.repository)
        if result.returncode != 0:
            return "nicht ermittelbar"
        return result.stdout.strip() or empty

    @staticmethod
    def _section(path: Path, heading: str) -> str:
        content = path.read_text(encoding="utf-8")
        marker = "## {}".format(heading)
        lines = content.splitlines()
        try:
            start = lines.index(marker) + 1
        except ValueError:
            raise ValueError(
                "Missing canonical section {!r} in {}".format(
                    heading,
                    path,
                )
            )
        section = []
        for line in lines[start:]:
            if line.startswith("## "):
                break
            section.append(line)
        result = "\n".join(section).strip()
        if not result:
            raise ValueError(
                "Canonical section {!r} is empty in {}".format(
                    heading,
                    path,
                )
            )
        return result

    @staticmethod
    def _bullet_value(section: str, label: str) -> Optional[str]:
        prefix = "- {}:".format(label)
        for line in section.splitlines():
            if line.startswith(prefix):
                return line[len(prefix):].strip().strip("`")
        return None
