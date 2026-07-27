import hashlib
import re
from typing import Dict, Iterable, List, Optional, Set, Tuple

from architecture_integrator.loader import ArchitectureContextLoader
from architecture_integrator.feedback import (
    ArchitectureImplementationReview,
    CodexHandoverIntake,
    stable_identifier,
)
from architecture_integrator.models import (
    ArchitectureAnalysis,
    ArchitectureProposal,
    Conflict,
    ContextSource,
    NormLevel,
    Recommendation,
)


class ArchitectureIntegrator:
    """Produces advisory comparisons without granting architecture authority."""

    _NON_NORMATIVE = {NormLevel.HISTORICAL, NormLevel.HANDOVER}
    _NEGATIVE = {
        "kein",
        "keine",
        "keinen",
        "keiner",
        "keines",
        "nicht",
        "niemals",
        "never",
        "no",
        "not",
    }
    _MODAL = {
        "darf",
        "dürfen",
        "muss",
        "müssen",
        "soll",
        "sollen",
        "must",
        "shall",
        "may",
        "be",
        "sein",
        "werden",
        "wird",
        "ist",
        "are",
    }

    def __init__(self, context_loader: ArchitectureContextLoader) -> None:
        if not isinstance(context_loader, ArchitectureContextLoader):
            raise TypeError(
                "ArchitectureIntegrator context_loader must be "
                "ArchitectureContextLoader"
            )
        self.context_loader = context_loader

    def analyze(self, proposal: ArchitectureProposal) -> ArchitectureAnalysis:
        if not isinstance(proposal, ArchitectureProposal):
            raise TypeError("proposal must be ArchitectureProposal")
        sources = self.context_loader.load(proposal.related_layers)
        proposal_statements = self._statements(proposal.content)
        if not proposal_statements:
            raise ValueError("Proposal content has no analyzable statements")

        existing = self._existing_statements(sources)
        aligned: List[str] = []
        additive: List[str] = []
        duplicate: List[str] = []
        conflicts: List[Conflict] = []
        affected_documents: Set[str] = set(proposal.source_references)

        for statement in proposal_statements:
            match = self._best_match(statement, existing)
            if match is None:
                additive.append(statement)
                continue
            source, existing_statement, relation = match
            affected_documents.add(source.path)
            if relation == "duplicate":
                duplicate.append(statement)
            elif relation == "aligned":
                aligned.append(statement)
            else:
                conflicts.append(
                    self._conflict(
                        statement,
                        existing_statement,
                        source,
                    )
                )

        unresolved = []
        loaded_references = {
            value
            for source in sources
            for value in (source.source_id, source.path)
        }
        unresolved.extend(
            "Source reference was not loaded: {}".format(reference)
            for reference in proposal.source_references
            if reference not in loaded_references
        )
        if conflicts:
            unresolved.append(
                "Chief Architect must resolve every normative conflict."
            )
        if additive:
            unresolved.append(
                "Chief Architect must confirm whether additive elements "
                "become binding architecture."
            )
        if not proposal.known_constraints:
            unresolved.append(
                "No source-declared constraints were supplied."
            )
        recommendation = (
            Recommendation.ADOPT_WITH_CHANGES
            if conflicts
            else Recommendation.ADOPT
        )
        decision_required = tuple(
            [
                "{}: adopt, modify, reject, or defer the proposed statement."
                .format(conflict.conflict_id)
                for conflict in conflicts
            ]
            + [
                "Confirm the non-binding {} recommendation for proposal {}."
                .format(recommendation.value, proposal.proposal_id)
            ]
        )
        applicable = tuple(
            source.source_id
            for source in sources
            if source.norm_level not in self._NON_NORMATIVE
            and (
                source.relevance.startswith("direct:")
                or source.norm_level
                in {
                    NormLevel.C1_CONSTITUTION,
                    NormLevel.MDR,
                    NormLevel.C2_GOVERNANCE,
                }
            )
        )
        return ArchitectureAnalysis(
            proposal=proposal,
            loaded_context_sources=sources,
            applicable_norms=applicable,
            proposal_summary=self._summary(
                proposal,
                aligned,
                additive,
                conflicts,
                duplicate,
            ),
            aligned_elements=tuple(aligned),
            additive_elements=tuple(additive),
            conflicting_elements=tuple(conflicts),
            duplicate_elements=tuple(duplicate),
            unresolved_questions=tuple(unresolved),
            affected_layers=proposal.related_layers,
            affected_documents=tuple(sorted(affected_documents)),
            implementation_risks=(
                "Deterministic lexical comparison cannot establish semantic "
                "equivalence beyond explicit textual propositions.",
                "No proposal element is binding until the Chief Architect "
                "confirms a separate decision object.",
            ),
            recommendation=recommendation,
            confidence=self._confidence(
                aligned,
                additive,
                conflicts,
                duplicate,
            ),
            decision_required=decision_required,
        )

    def render_decision_template(
        self,
        analysis: ArchitectureAnalysis,
    ) -> str:
        if not isinstance(analysis, ArchitectureAnalysis):
            raise TypeError("analysis must be ArchitectureAnalysis")
        conflicts = tuple(
            "{} — {} ({}, {})".format(
                item.conflict_id,
                item.conflict_reason,
                item.existing_source,
                item.norm_level.value,
            )
            for item in analysis.conflicting_elements
        )
        return "\n".join(
            (
                "# ENTSCHEIDUNGSVORLAGE",
                "",
                "## Empfehlung",
                analysis.recommendation.value,
                "",
                "## Kernaussage",
                analysis.proposal_summary,
                "",
                "## Übernehmen",
                self._lines(
                    analysis.aligned_elements + analysis.additive_elements
                ),
                "",
                "## Ändern",
                self._lines(
                    tuple(
                        item.suggested_resolution
                        for item in analysis.conflicting_elements
                    )
                ),
                "",
                "## Ablehnen",
                self._lines(()),
                "",
                "## Konflikte",
                self._lines(conflicts),
                "",
                "## Betroffene Architektur",
                self._lines(
                    tuple(
                        layer.value for layer in analysis.affected_layers
                    )
                    + analysis.affected_documents
                ),
                "",
                "## Entscheidung erforderlich",
                self._lines(analysis.decision_required),
            )
        )

    def review_handover(
        self,
        intake: CodexHandoverIntake,
    ) -> ArchitectureImplementationReview:
        """Creates an advisory implementation review without approving it."""
        if not isinstance(intake, CodexHandoverIntake):
            raise TypeError("intake must be CodexHandoverIntake")
        recommendation = (
            "ADOPT_WITH_CHANGES" if intake.deviations else "ADOPT"
        )
        conflicts = tuple(item.message for item in intake.deviations)
        return ArchitectureImplementationReview(
            review_id=stable_identifier(
                "review",
                intake.architecture_run_id,
                intake.execution_id,
                intake.result_commit,
                intake.handover_path,
            ),
            architecture_run_id=intake.architecture_run_id,
            workflow_id=intake.workflow_id,
            execution_id=intake.execution_id,
            attempt_ids=intake.attempt_ids,
            recommendation=recommendation,
            original_decision_ids=intake.decision_ids,
            codex_prompt="prompts/codex-prompt.md",
            implementation_result=(
                "Codex completed the authorized architecture order and "
                "reported a result commit, checks and handover. The "
                "Architecture Integrator reviewed the structured evidence "
                "without approving the implementation."
            ),
            changed_files=intake.changed_files,
            checks=intake.checks,
            commit=intake.result_commit,
            git_status=intake.git_status,
            deviations=intake.deviations,
            open_risks=intake.open_risks,
            conflicts=conflicts,
            decision_required=(
                "Chief Architect must adopt, request changes, reject, or "
                "defer the implementation result.",
            ),
        )

    def _existing_statements(
        self,
        sources: Tuple[ContextSource, ...],
    ) -> Tuple[Tuple[ContextSource, str], ...]:
        result = []
        for source in sources:
            if source.norm_level in self._NON_NORMATIVE:
                continue
            result.extend(
                (source, statement)
                for statement in self._statements(source.content)
            )
        return tuple(result)

    def _best_match(
        self,
        proposed: str,
        existing: Tuple[Tuple[ContextSource, str], ...],
    ) -> Optional[Tuple[ContextSource, str, str]]:
        normalized = self._normalize(proposed)
        polarity, core = self._proposition(proposed)
        candidates = []
        for source, statement in existing:
            existing_normalized = self._normalize(statement)
            existing_polarity, existing_core = self._proposition(statement)
            if normalized == existing_normalized:
                relation = "duplicate"
            elif core and core == existing_core:
                relation = (
                    "aligned"
                    if polarity == existing_polarity
                    else "conflict"
                )
            else:
                continue
            candidates.append(
                (
                    source.norm_level.priority,
                    source.source_id,
                    statement,
                    source,
                    relation,
                )
            )
        if not candidates:
            return None
        _, _, statement, source, relation = min(candidates)
        return source, statement, relation

    def _conflict(
        self,
        proposed: str,
        existing: str,
        source: ContextSource,
    ) -> Conflict:
        digest = hashlib.sha256(
            "{}\n{}\n{}".format(
                proposed,
                existing,
                source.source_id,
            ).encode("utf-8")
        ).hexdigest()[:12]
        return Conflict(
            conflict_id="CONFLICT-{}".format(digest.upper()),
            proposed_statement=proposed,
            existing_statement=existing,
            existing_source=source.path,
            norm_level=source.norm_level,
            conflict_reason=(
                "The proposal and the binding source express opposite "
                "polarity for the same normalized proposition."
            ),
            suggested_resolution=(
                "Do not integrate automatically; the Chief Architect must "
                "retain, modify, reject, or defer the proposed statement."
            ),
            requires_chief_architect_decision=True,
        )

    def _statements(self, content: str) -> Tuple[str, ...]:
        result = []
        paragraph = []
        for raw_line in content.splitlines() + [""]:
            line = raw_line.strip()
            if not line:
                if paragraph:
                    result.append(" ".join(paragraph))
                    paragraph = []
                continue
            if line.startswith("#"):
                if paragraph:
                    result.append(" ".join(paragraph))
                    paragraph = []
                heading = line.lstrip("#").strip()
                if heading:
                    result.append(heading)
                continue
            bullet = re.match(r"^(?:[-*+]|\d+[.)])\s+(.+)$", line)
            if bullet:
                if paragraph:
                    result.append(" ".join(paragraph))
                    paragraph = []
                result.append(bullet.group(1).strip())
            elif not line.startswith(("```", "|", ">")):
                paragraph.append(line)
        return tuple(dict.fromkeys(result))

    def _normalize(self, value: str) -> str:
        return " ".join(
            re.findall(r"[a-z0-9äöüß]+", value.casefold())
        )

    def _proposition(self, value: str) -> Tuple[bool, str]:
        tokens = self._normalize(value).split()
        negative = any(token in self._NEGATIVE for token in tokens)
        core = " ".join(
            token
            for token in tokens
            if token not in self._NEGATIVE and token not in self._MODAL
        )
        return negative, core

    def _summary(
        self,
        proposal: ArchitectureProposal,
        aligned: List[str],
        additive: List[str],
        conflicts: List[Conflict],
        duplicate: List[str],
    ) -> str:
        return " ".join(
            (
                "Proposal {} was compared with the loaded architecture."
                .format(proposal.proposal_id),
                "{} aligned, {} additive, {} conflicting, and {} duplicate "
                "elements were identified.".format(
                    len(aligned),
                    len(additive),
                    len(conflicts),
                    len(duplicate),
                ),
                "The recommendation is advisory.",
                "Only the Chief Architect may decide.",
            )
        )

    def _confidence(
        self,
        aligned: List[str],
        additive: List[str],
        conflicts: List[Conflict],
        duplicate: List[str],
    ) -> float:
        total = len(aligned) + len(additive) + len(conflicts) + len(duplicate)
        explicit = len(aligned) + len(conflicts) + len(duplicate)
        return round(0.5 + (0.45 * explicit / total), 2)

    def _lines(self, values: Iterable[str]) -> str:
        items = tuple(values)
        return "\n".join("- {}".format(item) for item in items) or "- None"
