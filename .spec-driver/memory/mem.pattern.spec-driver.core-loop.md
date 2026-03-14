---
id: mem.pattern.spec-driver.core-loop
name: Core Development Loop
kind: memory
status: active
memory_type: pattern
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, workflow, core-loop]
summary: "The canonical spec-driver loop is delta-first and observation-led: optional capture or revision trigger -> delta bundle -> implement -> audit/contracts -> revision/spec reconciliation -> closure. Revision-first is a concession path."
priority:
  severity: high
  weight: 10
scope:
  commands:
    - uv run spec-driver create delta
    - uv run spec-driver create phase
  paths:
    - supekku/scripts/lib/changes/creation.py
    - specify/decisions/ADR-004-canonical_workflow_loop.md
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      note: Delta creation and plan scaffolding behavior
      ref: supekku/scripts/lib/changes/creation.py
    - kind: code
      note: Completion flow and coverage gate orchestration
      ref: supekku/scripts/complete_delta.py
    - kind: doc
      note: Canonical and permissive workflow mapping
      ref: change/deltas/DE-038-canonical_workflow_alignment/workflow-research.md
---

# Core Development Loop

## The Full Cycle

```text
[optional capture or revision trigger]
-> delta
  -> [recommended DR]
  -> [optional IP -> just-in-time phase sheets]
-> implement
-> audit/contracts
-> revision from findings
-> spec reconcile
-> close
```

Each step corresponds to a primitive artefact:

1. **Capture** — if needed, change enters the [[mem.concept.spec-driver.backlog]]
   (issue, problem, improvement, or risk)
2. **Scope** — a [[mem.concept.spec-driver.delta]] declares and bounds code
   change work against that intent
3. **Design** — a [[mem.concept.spec-driver.design-revision]] translates
   intent into concrete code-level design
4. **Plan** — an [[mem.concept.spec-driver.plan]] breaks work into verifiable
   phases with entrance/exit criteria when execution scope warrants it
5. **Implement** — agent or developer executes the plan, writing code and tests
6. **Audit/contracts** — [[mem.concept.spec-driver.audit]] plus
   [[mem.concept.spec-driver.contract]] establish observed truth
7. **Revision from findings** — use [[mem.concept.spec-driver.revision]] to
   capture requirement/spec changes discovered during audit and reconciliation
8. **Spec reconcile** — patch specs/coverage to match audit findings,
   contracts
9. **Close** — complete delta and verify owning records are coherent

## Runtime and Concession Paths

Current runtime is permissive; this memory defines the canonical narrative.
[[mem.concept.spec-driver.posture]] determines how strongly teams follow it.

- **Pioneer**: card -> implement -> done (minimal concession path)
- **Settler**: optional backlog -> delta -> implement -> audit/reconcile -> close
- **Town Planner**: may start revision-first for high-governance work, then
  `revision -> delta/DR/IP/phases -> implementation -> audit/contracts -> spec reconciliation -> closure`

Revision-first is valid as a concession path, not the primary default.
Strict canonical lock-in is a future `strict_mode` contract, not current runtime behavior.

## Closure Contract

When work completes, update the **owning record** — the artefact that tracks
the requirement or work item. See [[mem.pattern.spec-driver.delta-completion]]
for the operational checklist and coverage gate details.
