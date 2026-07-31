# Guardian Understanding Proposal and Clarification Layers

Understanding Proposals are possible interpretations, not truths. They are
explicitly non-authoritative, do not represent facts, and cannot change an
`UnderstandingState`.

An `UnderstandingOperation` describes one possible state change. A proposal
wraps exactly one unchanged operation with its originating user statement,
source reference, and rationale. An `UnderstandingRevision` is created only
after a concrete proposal is explicitly selected; the existing deterministic
Understanding Model v2 remains the sole revision mechanism.

A later semantic component may create proposals only. It must never write to
the Understanding State or invoke a revision without explicit proposal
selection.

## Clarification Resolution v1

A clarifying user answer is preserved as source material; it is not
automatically interpreted. The original proposal set describes possible
unchanged `UnderstandingOperation` values, its understanding question asks for
clarification, and an immutable `ClarificationResolution` records the explicit
human classification of the answer. Only `SELECT_PROPOSAL` delegates exactly
one existing operation through `GuardianUnderstandingProposalService.apply()`
to the existing `GuardianUnderstandingService.advance()` revision mechanism.

`REJECT_PROPOSALS` records concrete rejected alternatives without changing the
state. `KEEP_OPEN` preserves the alternatives and requires exactly one next
understanding question. `CLOSE_WITHOUT_CHANGE` closes the proposal set without
running an operation. Proposal, question, answer, resolution, selected
operation and resulting `UnderstandingRevision` remain separately traceable.

A later semantic component may prepare typed resolution suggestions only. It
must not choose a resolution, select a proposal, or activate a revision.
