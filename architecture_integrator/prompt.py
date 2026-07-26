from architecture_integrator.models import (
    ArchitectureAnalysis,
    ChiefArchitectDecision,
)


class CodexPromptBuilder:
    """Creates implementation work only from an explicit confirmed decision."""

    def build(
        self,
        analysis: ArchitectureAnalysis,
        decision: ChiefArchitectDecision,
    ) -> str:
        if not isinstance(analysis, ArchitectureAnalysis):
            raise TypeError("analysis must be ArchitectureAnalysis")
        if not isinstance(decision, ChiefArchitectDecision):
            raise TypeError(
                "A confirmed ChiefArchitectDecision is required"
            )
        if analysis.proposal.proposal_id != decision.proposal_id:
            raise ValueError(
                "Decision proposal_id does not match the analysis"
            )
        proposal = analysis.proposal
        commit_message = "Integrate {} architecture".format(
            self._slug_words(proposal.title)
        )
        return "\n".join(
            (
                "# CODEX ARCHITECTURE IMPLEMENTATION ORDER",
                "",
                "## Authority",
                "Chief Architect decision `{}` by `{}`: `{}`.".format(
                    decision.decision_id,
                    decision.decided_by,
                    decision.decision.value,
                ),
                "Architecture Integrator advised; the Chief Architect "
                "decided; Codex implements only this confirmed scope.",
                "",
                "## Proposal",
                "- ID: `{}`".format(proposal.proposal_id),
                "- Title: {}".format(proposal.title),
                "- Source: {} ({})".format(
                    proposal.source,
                    proposal.source_role.value,
                ),
                "- Requested scope: {}".format(proposal.requested_scope),
                "- Affected layers: {}".format(
                    ", ".join(
                        layer.value for layer in proposal.related_layers
                    )
                ),
                "",
                "## Complete submitted architecture content",
                proposal.content,
                "",
                "## Binding accepted content",
                self._items(decision.accepted_elements),
                "",
                "## Binding modifications",
                self._items(decision.modified_elements),
                "",
                "## Explicitly rejected content",
                self._items(decision.rejected_elements),
                "",
                "## Deferred content",
                self._items(decision.deferred_elements),
                "",
                "## Rationale",
                decision.rationale,
                "",
                "## Existing binding sources",
                self._items(analysis.applicable_norms),
                "",
                "## Existing affected documents",
                self._items(analysis.affected_documents),
                "",
                "## Protection goals and constraints",
                self._items(proposal.known_constraints),
                "",
                "## Non-goals",
                "- Do not implement rejected or deferred elements.",
                "- Do not call external AI services or use network access.",
                "- Do not create UI unless explicitly accepted above.",
                "- Do not weaken C1, MDR-0001, C2, Institution, or "
                "Interaction guarantees.",
                "- Do not treat Integrator recommendations as authority.",
                "",
                "## Required verification",
                "- Add focused tests for every accepted invariant and "
                "modified boundary.",
                "- Preserve and run the complete existing test suite.",
                "- Run `python3 -m builder.main doctor`.",
                "- Run `git diff --check` and inspect `git status --short`.",
                "- Review the full architecture diff for conflicts and "
                "unintended changes.",
                "- Create JSON and Markdown handover files.",
                "",
                "## Commit",
                "Commit only after all checks pass.",
                "Suggested message: `{}`".format(commit_message),
                "",
                "Do not push.",
            )
        )

    def _items(self, values: tuple) -> str:
        return "\n".join("- {}".format(value) for value in values) or "- None"

    def _slug_words(self, value: str) -> str:
        words = "".join(
            char if char.isalnum() or char.isspace() else " "
            for char in value
        ).split()
        return " ".join(words[:8]) or "confirmed"
