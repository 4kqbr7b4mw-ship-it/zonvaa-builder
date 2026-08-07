"""Small explicit repository context loader with deterministic limits."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Tuple

from .boundary import BoundaryGuard, BoundaryViolation
from .schemas import ContextBundle, ContextDocument


class ProjectContextLoader:
    def __init__(
        self,
        guard: BoundaryGuard,
        max_files: int = 8,
        max_file_characters: int = 12_000,
        max_total_characters: int = 40_000,
    ) -> None:
        self.guard = guard
        self.max_files = max_files
        self.max_file_characters = max_file_characters
        self.max_total_characters = max_total_characters

    def load(self, goal: str, allowed_context: Iterable[str]) -> ContextBundle:
        candidates = self._rank(goal, allowed_context)
        documents: List[ContextDocument] = []
        total = 0
        for relative in candidates[: self.max_files]:
            path = self.guard.resolve_read_path(relative)
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise BoundaryViolation("context file is not readable text") from error
            remaining = self.max_total_characters - total
            if remaining <= 0:
                break
            limit = min(self.max_file_characters, remaining)
            truncated = len(content) > limit
            content = content[:limit]
            total += len(content)
            documents.append(
                ContextDocument(
                    path=str(path.relative_to(self.guard.repository_root)),
                    content=content,
                    truncated=truncated,
                )
            )
        return ContextBundle(
            documents=documents,
            selected_paths=[document.path for document in documents],
            total_characters=total,
        )

    @staticmethod
    def _rank(goal: str, allowed_context: Iterable[str]) -> List[str]:
        keywords = set(re.findall(r"[a-z0-9_-]{3,}", goal.lower()))
        unique: List[Tuple[int, str]] = []
        seen = set()
        for value in allowed_context:
            if value in seen:
                continue
            seen.add(value)
            path_words = set(re.findall(r"[a-z0-9_-]{3,}", value.lower()))
            score = len(keywords.intersection(path_words))
            unique.append((score, value))
        return [value for _, value in sorted(unique, key=lambda item: (-item[0], item[1]))]
