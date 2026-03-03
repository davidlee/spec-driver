---
id: mem.pattern.spec-driver.core-loop
name: Core Development Loop
kind: memory
status: active
memory_type: pattern
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- workflow
- core-loop
- seed
summary: 'The spec-driver development loop: capture → specify → scope → design → plan
  → implement → verify → archive. Ceremony determines which steps are required.'
priority:
  severity: high
  weight: 10
provenance:
  sources:
  - kind: doc
    note: Development Workflow section
    ref: supekku/about/README.md
  - kind: doc
    note: Command-level operational flows
    ref: supekku/about/processes.md
  - kind: doc
    note: Allowable permutations
    ref: docs/commands-workflow.md
---

# Core Development Loop

## The Full Cycle

```
capture → specify → scope → design → plan → implement → verify → archive
```

Each step corresponds to a primitive artefact:

1. **Capture** — need for change enters the [[mem.concept.spec-driver.backlog]]
   (issue, problem, improvement, or risk)
2. **Specify** — desired end-state defined in [[mem.concept.spec-driver.spec]]
   documents (SPEC/PROD); or existing specs updated via
   [[mem.concept.spec-driver.revision]]
3. **Scope** — a [[mem.concept.spec-driver.delta]] declares the intent to
   modify the system, referencing specs and requirements
4. **Design** — a [[mem.concept.spec-driver.design-revision]] translates
   intent into concrete code-level design
5. **Plan** — an [[mem.concept.spec-driver.plan]] breaks work into verifiable
   phases with entrance/exit criteria
6. **Implement** — agent or developer executes the plan, writing code and tests
7. **Verify** — [[mem.concept.spec-driver.audit]] reconciles realised changes
   against specs; [[mem.concept.spec-driver.contract]] generation confirms
   observed API surface
8. **Archive** — delta and related artefacts are closed; evergreen specs
   reflect the new state

## Ceremony Shortcuts

Not every step is required. [[mem.concept.spec-driver.posture]] determines
which are active:

- **Pioneer**: card → implement → done (steps 1, 6 only)
- **Settler**: backlog → delta → implement → closure (steps 1, 3, 6, 7-8)
- **Town Planner**: full cycle (all steps)

See `docs/commands-workflow.md` §5 for the complete permutation table.

## Closure Contract

When work completes, update the **owning record** — the artefact that tracks
the requirement or work item. See [[mem.pattern.spec-driver.delta-completion]]
for the operational checklist.
