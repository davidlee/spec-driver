---
id: mem.fact.workflow.disposition-authority-required
name: FindingDisposition authority field is required
kind: memory
status: active
memory_type: fact
created: '2026-03-22'
updated: '2026-03-22'
verified: '2026-03-22'
confidence: high
tags:
- workflow
- sharp-edge
- pydantic
summary: "FindingDisposition requires authority: DispositionAuthority — not optional. Every disposition dict must include it."
scope:
  globs:
    - supekku/scripts/lib/workflow/review_state_machine.py
    - supekku/scripts/lib/workflow/review_io.py
    - supekku/cli/workflow.py
  paths:
    - supekku/scripts/lib/workflow/review_state_machine.py
provenance:
  sources:
    - kind: code
      ref: supekku/scripts/lib/workflow/review_state_machine.py
      note: "FindingDisposition(BaseModel) — authority field is not Optional"
    - kind: commit
      ref: 1fa074fc
      note: "DE-109 Phase 3 — discovered during implementation"
---

# FindingDisposition authority field is required

`FindingDisposition(BaseModel)` declares `authority: DispositionAuthority` as a
**required** field. Unlike `rationale`, `backlog_ref`, `resolved_at`, and
`superseded_by` (all optional), authority must always be provided.

When building disposition dicts for `update_finding_disposition()`, always include
`"authority"`. The CLI disposition commands default to `DispositionAuthority.AGENT`;
`--authority user` overrides for human-gate scenarios (waive on blocking).

Pydantic validation catches omission at write time (via `FindingDisposition.model_validate()`
in `update_finding_disposition()`), but the error surfaces as a write failure, not
a clear "missing authority" message.

See [[DR-109]] §3.4 for the disposition model design.
