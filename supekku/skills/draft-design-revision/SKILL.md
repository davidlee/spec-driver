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
3. Steal the useful parts of brainstorming without importing its full ceremony:
   - keep the loop progressive and section-scoped rather than rewriting the whole file at once
   - prefer concrete code-adjacent detail where it sharpens design intent:
     - example data shapes
     - sketch APIs or function signatures
     - module boundaries and responsibility splits
     - pseudocode or short code samples for tricky seams
4. Work through unresolved design questions one at a time when needed:
   - suggest options with tradeoffs
   - recommend one with reasoning
   - capture the accepted direction back into the DR before moving on
5. Draft or revise the DR section by section rather than dumping a full design at once:
   - Current behavior vs target behavior
   - Code impact summary (paths + intended changes)
   - Verification alignment (what evidence must change/add)
   - Design decisions and remaining open questions
6. When a section shapes later sections, present that section first and treat later sections as provisional until the foundation is coherent.
7. Prefer concrete design detail over hand-wavey prose:
   - likely structs/types
   - function or module responsibilities
   - data flow boundaries
   - verification impact
8. Once the DR feels coherent, perform an adversarial self-review before treating it as done:
   - attack vague sections, hidden assumptions, weak verification, missing code-impact detail, and places where a short sample would remove ambiguity
   - record the findings in the DR or companion delta notes as needed
   - integrate the feedback before offering next steps
9. After integrating DR feedback, reconcile the owning `DE-XXX.md` so scope, risks, acceptance criteria, open questions, and follow-up direction still match the revised DR.
10. After the internal adversarial pass is integrated, offer to print a prompt for an external adversarial reviewer.
11. Only after DR feedback has been integrated and the DE is current should you offer to initiate `/plan-phases` or create IP/phase sheets.
12. Keep design declarative; do not write execution checklists here.
13. If meaningful tradeoffs or uncertainty remain unresolved, stop and `/consult`.

Guardrails:
- The design revision is canon for design intent.
- If DR and plan conflict, reconcile via DR first.
- Do not present "the whole design" as settled before the foundational sections
  and decisions have been validated.
- Do not hide unresolved assumptions inside polished prose; name them explicitly.
- Do not confuse detailed design with implementation planning.
- Do not treat a polished full-file rewrite as progress if the hard design questions
  are still unresolved.
- Do not move on to planning while the delta still tells an older story than the DR.

Outcomes:
- DR gives a clear, defensible target design for implementation.
- Foundational questions are closed or made explicit before downstream planning.
- The DR evolves through short feedback loops instead of one large speculative draft.
- Verification impact is explicit before coding starts.
- The author gets an internal adversarial pass and an optional external challenge
  prompt before planning starts.
- DE and DR stay aligned before IP/phase work begins.
