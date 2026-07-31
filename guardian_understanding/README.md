# Guardian Understanding Proposal Layer

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
