---
id: IMPR-032
name: Dispatch plan flags cross-phase state dependencies
created: "2026-04-17"
updated: "2026-04-17"
status: idea
kind: improvement
relations:
  - type: relates_to
    target: DE-132
---

# Dispatch plan flags cross-phase state dependencies

## Context

Source: vk DE-105 field analysis (DR-132 amendment appendix). Recommendation
R4.

When a phase depends on a prior phase's state restructure (types, schemas,
module layout — not just feature completion), the dispatch skill should
flag this explicitly in the dispatch plan so the user is aware that
cross-phase state visibility is load-bearing.

## Why this is deferred from DR-132

Once DEC-132-02's clarified isolation rules land (DR-132 §9), cross-phase
state dependencies are handled *mechanically*: sequential batches run in
the main tree and see the prior phase's commits. R1 branch-point
verification catches the case where a parallel batch accidentally forks
stale.

R4 is a user-awareness feature layered on top. It is not a correctness
fix — it is an aid for the orchestrator to explain the dispatch plan and
for the user to sanity-check the isolation selection.

## Design surface

Open questions:
- How is "state dependency" detected?
  - Parse phase sheet entrance criteria for keywords (brittle)
  - Diff of prior phase's committed files against current phase's
    touched files (heuristic — requires file scope metadata on tasks)
  - Explicit `state_dependency: true|false` annotation on phase sheets
    (cleanest but requires /plan-phases authoring change — see IMPR-028)
- Where does the warning surface?
  - In the dispatch plan output (step 4)
  - As a check that forces user approval before proceeding

## Acceptance sketch

- Dispatch plan surface includes a "State dependencies" section when
  prior-phase state is relevant to current-phase execution
- Mechanism is deterministic, not heuristic (prefer explicit annotation
  over inference)

## Dependencies

- IMPR-028 (explicit phase sheet annotations from /plan-phases) likely
  a precondition for clean implementation
