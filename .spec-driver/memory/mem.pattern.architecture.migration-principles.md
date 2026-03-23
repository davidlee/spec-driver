---
id: mem.pattern.architecture.migration-principles
name: "Migration principles from DE-125 pilot"
kind: memory
status: active
memory_type: pattern
created: '2026-03-24'
updated: '2026-03-24'
verified: '2026-03-24'
confidence: high
tags:
- architecture
- migration
- principles
summary: >-
  Three rules for migration deltas: classify before migrating, optimise for
  graph centrality not module count, use Workspace as canonical orchestration root.
scope:
  globs:
  - spec_driver/**
  - supekku/scripts/lib/**
provenance:
  sources:
  - DE-125
---

# Migration principles from DE-125 pilot

## Rules

1. **Treat core/ as a classification problem before a migration problem.**
   Modules like `artifact_view.py` and `enums.py` make the outer layer contract
   look valid while remaining false in practice. Reclassify misplaced modules
   first; move them second. See [[mem.fact.architecture.core-misplaced-modules]].

2. **Optimise for moves that reduce graph centrality, not module count.**
   203 legacy modules exist. Moving them one-by-one is geological. Target moves
   that break high-centrality coupling nodes — files that many other modules
   depend on or that reach across many areas. A single reclassification of
   `artifact_view.py` (11 registry imports) has more architectural leverage than
   moving 10 leaf modules.

3. **Use Workspace as the canonical orchestration root unless evidence says
   otherwise.** DE-125 Phase 4 proved Workspace already owns sync ordering,
   cross-registry composition, and data flow. Future migration work should
   route orchestration responsibility through Workspace rather than creating
   parallel composition surfaces.

## Context

DE-125 moved 10 modules and extracted a backlink seam across 4 phases. The pilot
proved the layer contracts and migration pattern work, but also showed that
incremental module-by-module migration doesn't scale. These principles distil
the strategic lessons for subsequent deltas.

## Related

- [[DE-125]] — originating delta
- [[mem.pattern.architecture.domain-migration]] — tactical migration recipe
- [[mem.fact.architecture.core-misplaced-modules]] — core audit prerequisite
