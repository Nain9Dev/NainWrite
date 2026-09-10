# Contextual Language Review

The owner requests continued linguistic improvement. The observed synthetic source
`No incluye el alojamiento` was narrowed to hosting without supporting context.
On review the owner confirmed that interpretation depends on context.

- **CTX-001:** When Spanish lodging terminology lacks a supported sense in its
  source block, review shall retain an explicit context question even if both
  auditors accept the candidate. Unchanged Spanish shall also expose the question
  before translation approval.
- **CTX-002:** When the source explicitly qualifies web hosting or accommodation
  for people, the rule shall accept matching terminology and flag the opposite
  interpretation. Unrelated keywords, quoted text or a candidate-added qualifier
  shall not establish source meaning. Conflicting or multiple senses require review.
- **CTX-003:** When generating, reviewing or validating retained evidence, the
  same versioned deterministic rule shall apply; removing its finding shall fail
  evidence validation. Prompts shall explicitly preserve unresolved ambiguity.
- **CTX-004:** When a contextual finding remains, the editorial report shall show
  a plain Spanish clarification question separately from the retained technical
  findings. Showing a question shall not record an answer or approval.

This is a bounded regression for lodging terminology, not a universal ambiguity
detector. Indirect context, metaphor and cross-section references may need human
judgement. A finding is a request to clarify the source, not a licence to invent
facts. Existing literal and modality checks remain unchanged.

External requirements: `[A]` existing local runtimes only; no new dependency,
download or paid service. `[M]` actual source interpretation and final linguistic
approval remain the owner's actions. No output approval is implied by development.
