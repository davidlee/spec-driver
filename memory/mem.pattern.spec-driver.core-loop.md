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
summary: 'The canonical spec-driver loop: capture → revision intent → delta/design/plan
  → implement → audit/contracts → spec reconciliation → closure. Ceremony determines
  which steps are required.'
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
capture → revision intent → scope → design → plan → implement → audit/contracts → spec reconcile → close
```

Each step corresponds to a primitive artefact:

1. **Capture** — need for change enters the [[mem.concept.spec-driver.backlog]]
   (issue, problem, improvement, or risk)
2. **Revision intent** — a [[mem.concept.spec-driver.revision]] captures
   intended requirement/spec changes (often introducing new requirements)
3. **Scope** — a [[mem.concept.spec-driver.delta]] declares and bounds code
   change work against that intent
4. **Design** — a [[mem.concept.spec-driver.design-revision]] translates
   intent into concrete code-level design
5. **Plan** — an [[mem.concept.spec-driver.plan]] breaks work into verifiable
   phases with entrance/exit criteria
6. **Implement** — agent or developer executes the plan, writing code and tests
7. **Audit/contracts** — [[mem.concept.spec-driver.audit]] plus
   [[mem.concept.spec-driver.contract]] establish observed truth
8. **Spec reconcile** — patch specs/coverage to match audit findings and
   contracts
9. **Close** — complete delta and verify owning records are coherent

## Ceremony Shortcuts

Not every step is required. [[mem.concept.spec-driver.posture]] determines
which are active:

- **Pioneer**: card → implement → done (minimal loop)
- **Settler**: backlog → delta → implement → audit/reconcile → close
- **Town Planner**: full revision-driven loop above (often policy-gated)

See `docs/commands-workflow.md` §5 for the complete permutation table.

## Closure Contract

When work completes, update the **owning record** — the artefact that tracks
the requirement or work item. See [[mem.pattern.spec-driver.delta-completion]]
for the operational checklist.
