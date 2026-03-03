---
name: draft-design-revision
description: Draft or refine a design revision (DR) for a delta, capturing current vs target behavior, code impacts, and verification alignment.
---
You are translating delta intent into implementable design.

Inputs:
- `DE-XXX.md`
- Existing `DR-XXX.md` (or scaffolded design artifact)
- Relevant specs/requirements

Process:
1. Read delta + relevant specs first.
2. Open the DR and fill/refresh:
   - Current behavior vs target behavior
   - Code impact summary (paths + intended changes)
   - Verification alignment (what evidence must change/add)
   - Design decisions and open questions
3. Keep design declarative; do not write execution checklists here.
4. If meaningful tradeoffs or uncertainty appear, stop and `/consult`.
5. Hand off to `/plan-phases` once DR is coherent.

Guardrails:
- The design revision is canon for design intent.
- If DR and plan conflict, reconcile via DR first.

Outcomes:
- DR gives a clear, defensible target design for implementation.
- Verification impact is explicit before coding starts.
