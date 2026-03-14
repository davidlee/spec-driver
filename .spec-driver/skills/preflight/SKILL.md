---
name: preflight
description: Use after routing has already happened, when the next step is bounded up-front research to understand a substantive task, surface unknowns and tensions, and assess readiness without drifting into implementation or open-ended exploration.
---

This is NOT the first routing skill for work in a spec-driver repo.

If you have not already chosen the governing skill path, stop and use
`/using-spec-driver` first.

Use `/preflight` only after routing has already established that the immediate
need is bounded up-front research before proceeding.

In other words: `/using-spec-driver` routes into `/preflight` when appropriate.
`/preflight` does not replace `/using-spec-driver`.

You're about to begin work on something: $ARGUMENTS

First: you need to understand what it entails. Your immediate task is to
correctly decide how much effort to spend on this preliminary research.

Too little is as bad as too much. You must estimate where the goldilocks zone is,
and arrive with maximum tokens intact.

You may be expected to:

- clarify a vague task
- methodically diagnose a fault
- write or critique a thorough and considered design doc which fits the
  implementation surface
- execute a thoroughly prepared plan with efficiency
- preserve your own context by delegating to sub-agents

Do not use this skill to decide whether the task belongs to `/spec-driver`,
`/scope-delta`, `/execute-phase`, or another governing skill. That decision
must already be made.

If you can't tell whether `/preflight` is appropriate, you probably need
`/using-spec-driver`, not this skill.

Learn **just enough to ask the user the right clarifying questions**. These
might include: how deeply should you research? what remains ambiguous? which
assumptions are safe enough to carry forward?

If you chase the questions which arise as you go, you'll disappear like a
helium balloon into the open sky.

Instead:

1. Read the material in front of you
2. Take stock of relevant `/retrieving-memories` and `/doctrine`
3. Confirm your stopping conditions before you expand the search
4. Decide **up front**, out loud:

- what, concretely, you need to know.
- when, concretely, you will stop even if you don't have all the answers.

5. Remain curious and collect further questions, but don't run off after them.
6. Stop when you reach your stopping conditions.
7. Before declaring readiness, produce a critical assessment with these headings:

- confirmed inputs
- assumptions you would carry into the next step
- unresolved questions, risks, or dependencies
- tensions or ambiguities (including any apparent contradictions between artifacts, or design & implementation surface)

8. If the task is implementation-bound, do not conclude "ready to proceed", "no blockers", or equivalent unless you explicitly state one of:

- no open questions remain after reading the governing artefacts
- open questions remain, but they are consciously accepted as implementation assumptions

9. Treat scope-shaping uncertainty as important even when it is not a hard blocker.
   Call out things like interaction semantics, ownership of mappings/constants, phase-boundary ambiguity, widget/API choice, or design-vs-discretion gaps.
10. Present any significant discoveries, open questions, unresolved tradeoffs to the user.
11. Indicate the next governing step; suggest the next skill or workflow transition, or further investigation required.

Repeat this process to clarify further, if the user indicates to.

## Guidance

Breadth first: start broad and high level, drill down as necessary.

Search order:

- provided artifact(s)
- related / linked files, documents, artifacts
- related governance (ADRs, standards, policies)
- related specs
- `/retrieving-memories`
- contracts
- related artifacts (provisional: may be out of date)
- code

## Guardrails:

- Do not let `/preflight` steal the job of `/using-spec-driver`.
- Do not treat bounded research as permission to start implementation.
- Do not widen scope just because new curiosities appear.
- Do not confuse "I can start coding" with "the materials are ready". Readiness
  means you have surfaced the remaining unknowns and either resolved them or
  named them as conscious assumptions.

Do not begin implementation without acknowledgement from the user.
