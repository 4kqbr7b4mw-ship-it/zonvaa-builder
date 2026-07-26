import hashlib
import re
from pathlib import Path
from typing import Iterable, Optional, Tuple

from architecture_integrator.models import (
    ArchitectureLayer,
    ContextSource,
    NormLevel,
    SourceStatus,
)
from builder.runtime import RuntimeManager
from constitution.manager import ConstitutionManager


class ArchitectureContextLoader:
    """Builds a deterministic read-only view from the booted Runtime."""

    def __init__(self, runtime: RuntimeManager) -> None:
        if not isinstance(runtime, RuntimeManager):
            raise TypeError(
                "ArchitectureContextLoader runtime must be RuntimeManager"
            )
        self.runtime = runtime

    def load(
        self,
        related_layers: Tuple[ArchitectureLayer, ...],
    ) -> Tuple[ContextSource, ...]:
        if not isinstance(related_layers, tuple) or not all(
            isinstance(layer, ArchitectureLayer) for layer in related_layers
        ):
            raise TypeError("related_layers must contain ArchitectureLayer")
        self._require_runtime()
        sources = [
            self._source(
                "C1-CONSTITUTION",
                ConstitutionManager().path,
                NormLevel.C1_CONSTITUTION,
                self.runtime.constitution or "",
                related_layers,
            )
        ]
        sources.extend(
            self._paths(
                self.runtime.knowledge.get("mdr", ()),
                NormLevel.MDR,
                related_layers,
            )
        )
        governance = self.runtime.governance_context
        assert governance is not None
        sources.append(
            self._source(
                "C2-GOVERNANCE-CHARTER",
                self._relative(governance.charter_source),
                NormLevel.C2_GOVERNANCE,
                governance.charter_content,
                related_layers,
            )
        )
        institution = self.runtime.institution_context
        interaction = self.runtime.interaction_context
        assert institution is not None
        assert interaction is not None
        sources.extend(
            (
                self._source(
                    "SPEC-INSTITUTION",
                    self._relative(institution.source),
                    NormLevel.SPECIFICATION,
                    institution.content,
                    related_layers,
                ),
                self._source(
                    "SPEC-INTERACTION",
                    self._relative(interaction.source),
                    NormLevel.SPECIFICATION,
                    interaction.content,
                    related_layers,
                ),
            )
        )
        current_adrs = []
        historical_adrs = []
        for path in self.runtime.knowledge.get("adr", ()):
            content = path.read_text(encoding="utf-8")
            level = (
                NormLevel.HISTORICAL
                if self._is_historical(content)
                else NormLevel.ADR
            )
            target = historical_adrs if level is NormLevel.HISTORICAL else current_adrs
            target.append(
                self._source(
                    path.stem,
                    self._relative(path),
                    level,
                    content,
                    related_layers,
                )
            )
        sources.extend(current_adrs)
        sources.append(
            self._source(
                "C3-OPERATIVE-RULES",
                self._relative(governance.operative_rules_source),
                NormLevel.C3_OPERATIVE,
                governance.operative_rules_content,
                related_layers,
            )
        )
        sources.extend(historical_adrs)
        if self.runtime.latest_handover is not None:
            path = self.runtime.latest_handover
            sources.append(
                self._source(
                    "LATEST-HANDOVER",
                    self._relative(path),
                    NormLevel.HANDOVER,
                    path.read_text(encoding="utf-8", errors="replace"),
                    related_layers,
                )
            )
        return tuple(
            sorted(
                sources,
                key=lambda item: (
                    item.norm_level.priority,
                    item.source_id,
                    item.path,
                ),
            )
        )

    def _require_runtime(self) -> None:
        missing = []
        for name in (
            "constitution",
            "governance_context",
            "institution_context",
            "interaction_context",
        ):
            if getattr(self.runtime, name) is None:
                missing.append(name)
        if not self.runtime.knowledge:
            missing.append("knowledge")
        if not self.runtime.knowledge.get("mdr"):
            missing.append("knowledge.mdr")
        if missing:
            raise RuntimeError(
                "Architecture context is incomplete: {}".format(
                    ", ".join(missing)
                )
            )

    def _paths(
        self,
        paths: Iterable[Path],
        level: NormLevel,
        related_layers: Tuple[ArchitectureLayer, ...],
    ) -> list:
        return [
            self._source(
                path.stem,
                self._relative(path),
                level,
                path.read_text(encoding="utf-8"),
                related_layers,
            )
            for path in paths
        ]

    def _source(
        self,
        source_id: str,
        path: Path,
        level: NormLevel,
        content: str,
        related_layers: Tuple[ArchitectureLayer, ...],
    ) -> ContextSource:
        content_bytes = content.encode("utf-8")
        return ContextSource(
            source_id=source_id,
            path=path.as_posix(),
            version=self._version(content, source_id),
            content_hash=hashlib.sha256(content_bytes).hexdigest(),
            norm_level=level,
            status=self._status(content, level),
            relevance=self._relevance(
                path.as_posix(),
                content,
                related_layers,
            ),
            content=content,
        )

    def _version(self, content: str, source_id: str) -> str:
        match = re.search(r"^Version:\s*(\S+)\s*$", content, re.MULTILINE)
        if match:
            return match.group(1)
        record = re.match(r"^(MDR|ADR)-(\d+)", source_id)
        return record.group(0) if record else "unversioned"

    def _status(self, content: str, level: NormLevel) -> SourceStatus:
        if level is NormLevel.HISTORICAL:
            return SourceStatus.HISTORICAL
        if level is NormLevel.HANDOVER:
            return SourceStatus.SUPPLEMENTAL
        match = re.search(
            r"^## Status\s*\n+\s*([^\n]+)",
            content,
            re.MULTILINE,
        )
        raw_status = match.group(1).strip() if match else ""
        if not raw_status:
            match = re.search(r"^Status:\s*(.+)$", content, re.MULTILINE)
            raw_status = match.group(1).strip() if match else ""
        normalized = raw_status.casefold()
        if "abgeleitet" in normalized:
            return SourceStatus.DERIVED
        if normalized in {"beschlossen", "verbindlich", "accepted"}:
            return SourceStatus.BINDING
        return SourceStatus.STATUS_MISSING

    def _is_historical(self, content: str) -> bool:
        match = re.search(
            r"^## Status\s*\n+\s*([^\n]+)",
            content,
            re.MULTILINE,
        )
        status = match.group(1).strip().casefold() if match else ""
        return any(
            marker in status
            for marker in ("ersetzt", "historisch", "superseded", "rejected")
        )

    def _relevance(
        self,
        path: str,
        content: str,
        layers: Tuple[ArchitectureLayer, ...],
    ) -> str:
        text = "{}\n{}".format(path, content).casefold()
        matched = [
            layer.value
            for layer in layers
            if layer is ArchitectureLayer.CROSS_LAYER
            or layer.value.casefold() in text
        ]
        return (
            "direct:{}".format(",".join(matched))
            if matched
            else "contextual"
        )

    def _relative(self, path: Path) -> Path:
        resolved = path.resolve()
        try:
            return resolved.relative_to(self.runtime.project_root)
        except ValueError as exc:
            raise ValueError(
                "Architecture source is outside the repository: {}".format(
                    path
                )
            ) from exc
