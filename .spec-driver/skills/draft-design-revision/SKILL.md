---
name: draft-design-revision
description: Draft or refine a design revision (DR) for a delta. Use it when a DR needs concrete design shaping, explicit question triage, and section-by-section validation before implementation planning.
---

You are translating delta intent into implementable design.

Inputs:

- `DE-XXX.md`
- Existing `DR-XXX.md` (or scaffolded design artifact)
- Relevant specs/requirements/backlog

## Anti-Pattern: it's too simple ...

It's a trap. Follow the process.

## Checklist

You MUST create a task for each of these items and complete them in order. Each depends on the preceding one:

1. **Explore context** — specs, contracts, memories, files, docs, recent commits. Begin high-level.
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Propose 2-3 approaches** — identify the next unanswered design question; propose options with trade-offs and your recommendation
4. **Present design** — in sections scaled to their complexity, get user approval after each section
5. **Write Design Revision** — save to the delta's DR file and commit
6. **Adversarial Review** — perform a hostile review of the design doc, probing for imprecision and flawed reasoning
7. **Integrate Review Feedback** -- triage and respond to feedback; integrate into DR/DE; repeat until DR approved
7. **Transition to planning** — invoke plan-phases skill to create implementation plan

<Process State Machine>
  <state name="Explore context">
    <transition to="Ask clarifying questions" />
  </state>
  <state name="Ask clarifying questions">
    <transition to="Propose 2-3 approaches" />
  </state>
  <state name="Propose 2-3 approaches">
    <transition to="Present design" />
    <transition to="Ask clarifying questions" />
  </state>
  <state name="Present design">
    <transition to="Write design doc" />
  </state>
  <state name="Write design doc">
    <transition to="Adversarial review" />
  </state>
  <state name="Adversarial review">
    <transition to="Ask clarifying questions" />
    <transition to="Propose 2-3 approaches" />
    <transition to="Present design" />
    <transition to="Write design doc" />
    <transition to="Transition to planning" />
  </state>
  <state name="Transition to planning">
    <transition to="plan-phases skill" />
  </state>
</Process State Machine>

## Process (detail)

### Explore context

1. Read delta + relevant specs, contracts, prior art first.
2. Run `/doctrine` before drafting so relevant ADRs, policies, and standards are in view for this design surface.
3. Before drafting sections, explicitly generate a list of concerns and then triage the design surface:
   - open questions that must be resolved
   - risks and underspecified areas
   - assumptions you are carrying
   - critical design decisions that shape the rest of the DR
   - relevant ADRs, policies, and standards that constrain the design

### Ask clarifying questions

Proceed in a light loop to clarify intent, surface known and unknown unknowns,
and drive towards sufficient clarity to lock a design. ';

Apply this process first to the DE itself (scope) if necessary, then the DR (technical design).

At each step:

1. Summarize:
   - what's already understood
   - carrying assumptions
   - open questions, risks, concerns, dependencies
2. Work through unresolved design questions one at a time. Ask questions one at a time, choosing the most impactful or most naturally related:
   - consider it carefully (implications, related questions)
   - lightly explore related context if necessary, but keep it bounded
   - suggest 2-3 options, with tradeoffs
   - recommend one, with rationale

Operating principles:

- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it
  into multiple questions
- Focus on understanding: purpose, constraints, success criteria, verification
  strategy

Continue in this manner until you have sufficient clarity to begin the DR proper,
and the user has accepted your summary.

Once accapted, ensure the delta artifact (DE-XXX) is consistent with and
reflects your current shared understanding before proceeding.

### Present design

1. Draft or revise the DR section interactively section by section, rather than dumping a full design at once:
   - Current behavior vs target behavior
   - Code impact summary (paths + intended changes)
   - Verification alignment (what evidence must change/add)
   - Design decisions and remaining open questions
2. When a section shapes later sections, present that section first and treat later sections as provisional until the foundation is coherent.
3. Prefer concrete design detail over hand-wavey prose:
   - Current behavior vs target behavior
   - module responsibility boundaries
   - imports, coupling, cohesion analysis
   - structs/types/interfaces/function signatures
   - data structures & algorithms
   - example data shapes
   - data flow boundaries
   - verification impact
   - invariants & boundary conditions
   - samples of critical code, protocols
   - titles / descriptions of key test cases
   - text c4 diagrams
   - Code impact summary (paths + intended changes)
   - Verification alignment (what evidence must change/add)
   - Impact on design decisions and remaining open questions
4. Perform targeted research if required to ensure fit to implementation surface

### Adversarial review

1. Once the DR feels coherent, perform an adversarial self-review before
treating it as done:
   - attack vague sections, hidden assumptions, weak verification, missing
     code-impact detail, and places where a short sample would remove ambiguity
   - attack missing, misread, or weakly applied ADR/policy/standard constraints
   - ensure doctrinal alignment
   - record the findings in the DR or companion delta notes as needed
2. Review for doctrinal alignment.
   - If the doctrine pass exposes governance conflicts, missing authorities, or
     ambiguous constraints, stop and `/consult` rather than normalizing around
     guesswork.
3. Integrate the feedback before offering next steps.
   - Occasionally this might require revisiting earlier steps.
4. After integrating DR feedback, reconcile the owning `DE-XXX.md` so scope,
risks, acceptance criteria, open questions, and follow-up direction still match
the revised DR.
5. After the internal adversarial pass is integrated, you MUST offer the user a
choice:
   1. print a prompt for an external adversarial reviewer.
   2. initiate `/plan-phases` to create IP/phase sheets.
6. Multiple passes of review & feedback may be required before acceptance. Do
not presume approval until it is explicitly granted.

If meaningful tradeoffs or uncertainty remain unresolved, stop and `/consult`.

## Guardrails

The design revision is canon for design intent.

- If DR and plan conflict, reconcile via DR first.
- Do not present "the whole design" as settled before the foundational sections and decisions have been validated.
- Do not hide unresolved assumptions inside polished prose; name them explicitly.
- Do not confuse detailed design with implementation planning.
- Do not treat a polished full-file rewrite as progress if the hard design questions
  are still unresolved.
- Do not move on to planning while the delta still tells an older story than the DR.
- Do not treat governance as optional background reading when the DR makes architectural or workflow choices.

## Outcomes

- DR gives a clear, defensible target design for implementation.
- Foundational questions are closed or made explicit before downstream planning.
- The DR evolves through short feedback loops instead of one large speculative draft.
- Verification impact is explicit before coding starts.
- The author gets an internal adversarial pass and an optional external challenge
  prompt before planning starts.
- DE and DR stay aligned before IP/phase work begins.
- Relevant ADRs, policies, and standards shape both the draft and the critical review.
