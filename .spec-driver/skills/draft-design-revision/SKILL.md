---
name: draft-design-revision
description: Draft or refine a design revision (DR) for a delta. Use it when a DR needs concrete design shaping, explicit question triage, and section-by-section validation before implementation planning.
---
You are translating delta intent into implementable design.

Inputs:
- `DE-XXX.md`
- Existing `DR-XXX.md` (or scaffolded design artifact)
- Relevant specs/requirements

Process:
1. Read delta + relevant specs first.
2. Before drafting sections, explicitly triage the design surface:
   - open questions that must be resolved
   - risks and underspecified areas
   - assumptions you are carrying
   - critical design decisions that shape the rest of the DR
3. Work through unresolved design questions one at a time when needed:
   - suggest options with tradeoffs
   - recommend one with reasoning
   - capture the accepted direction back into the DR before moving on
4. Draft or revise the DR section by section rather than dumping a full design at once:
   - Current behavior vs target behavior
   - Code impact summary (paths + intended changes)
   - Verification alignment (what evidence must change/add)
   - Design decisions and remaining open questions
5. When a section shapes later sections, present it for validation before treating the rest of the draft as settled.
6. Prefer concrete design detail over hand-wavey prose:
   - likely structs/types
   - function or module responsibilities
   - data flow boundaries
   - verification impact
7. Keep design declarative; do not write execution checklists here.
8. If meaningful tradeoffs or uncertainty remain unresolved, stop and `/consult`.
9. Hand off to `/plan-phases` once DR is coherent.

Guardrails:
- The design revision is canon for design intent.
- If DR and plan conflict, reconcile via DR first.
- Do not present "the whole design" as settled before the foundational sections
  and decisions have been validated.
- Do not hide unresolved assumptions inside polished prose; name them explicitly.
- Do not confuse detailed design with implementation planning.

Outcomes:
- DR gives a clear, defensible target design for implementation.
- Foundational questions are closed or made explicit before downstream planning.
- The DR evolves through short feedback loops instead of one large speculative draft.
- Verification impact is explicit before coding starts.
