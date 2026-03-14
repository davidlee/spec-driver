---
id: IP-050.PHASE-02
slug: "050-normalise_registry_api_surface_for_consistent_artifact_access-phase-02"
name: IP-050 Phase 02 - Group C registries
created: "2026-03-07"
updated: "2026-03-07"
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-050.PHASE-02
plan: IP-050
delta: DE-050
objective: >-
  Add ADR-009 standard surface to RequirementsRegistry, CardRegistry, and
  BacklogRegistry. Higher risk than Phase 1 due to constructor changes
  (Requirements) and semantic concessions (Card lane≠status).
entrance_criteria:
  - Phase 1 complete
exit_criteria:
  - RequirementsRegistry exposes find(), collect(), iter(), filter() + root keyword
  - CardRegistry exposes find(), collect(), iter(lane=), filter(lane=)
  - BacklogRegistry exposes find_item() convenience function
  - Constructor backward-compat verified for RequirementsRegistry and CardRegistry
  - All existing tests pass
  - New unit tests for every added method
  - just lint + just pylint pass
verification:
  tests:
    - VT-050-01 (partial — Requirements, Card, Backlog)
    - VT-050-02 (regression)
    - VT-050-03 (constructor backward-compat)
  evidence: []
tasks:
  - id: 2.1
    description: RequirementsRegistry — add find(), collect(), iter(), filter(), root keyword
  - id: 2.2
    description: CardRegistry — add find(), collect(), iter(lane=), filter(lane=)
  - id: 2.3
    description: BacklogRegistry — add find_item() convenience function
  - id: 2.4
    description: Tests for all new methods
risks:
  - description: RequirementsRegistry constructor overload complexity
    mitigation: add root keyword alongside existing registry_path positional
  - description: CardRegistry lane≠status semantic mismatch
    mitigation: iter(lane=) / filter(lane=) per DEC-050-05
```

# Phase 2 — Group C Registries (Requirements + Card + Backlog)

## 1. Objective

Add ADR-009 standard API surface to the remaining registries. These have higher
structural risk than Phase 1 due to constructor differences and semantic
concessions.

## 2. Tasks & Progress

| Status | ID  | Description                                                        | Notes                              |
| ------ | --- | ------------------------------------------------------------------ | ---------------------------------- |
| [x]    | 2.1 | RequirementsRegistry: find(), collect(), iter(), filter(), root kw | done                               |
| [x]    | 2.2 | CardRegistry: find(), collect(), iter(lane=), filter(lane=)        | done                               |
| [x]    | 2.3 | BacklogRegistry: find_item() convenience function                  | done                               |
| [x]    | 2.4 | Tests for all new methods                                          | 27 new tests                       |
| [x]    | 2.5 | Lint + full test suite                                             | 2700 pass, ruff clean, pylint 9.54 |
