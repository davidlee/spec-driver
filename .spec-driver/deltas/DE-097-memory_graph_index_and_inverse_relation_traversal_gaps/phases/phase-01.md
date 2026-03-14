---
id: IP-097.PHASE-01
slug: "097-domain-layer-graph-builder-query-api-id-normalizer"
name: "Phase 1: Domain layer — graph builder, query API, ID normalizer"
created: "2026-03-15"
updated: "2026-03-15"
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-097.PHASE-01
plan: IP-097
delta: DE-097
objective: >-
  Build pure domain functions: cross-artifact reference graph builder,
  forward/inverse query API, and registry-aware ID normalizer. All tested
  before CLI wiring in phase 2.
entrance_criteria:
  - DR-097 approved
exit_criteria:
  - graph builder produces correct nodes and edges from workspace
  - forward and inverse queries return correct results
  - ID normalizer resolves padding variants and emits diagnostics
  - all new code lint-clean
  - all tests pass
verification:
  tests:
    - VT-097-graph
    - VT-097-query-forward
    - VT-097-query-inverse
    - VT-097-normalize
    - VT-097-normalize-future
  evidence: []
tasks:
  - id: "1.1"
    description: "ID normalizer in core/artifact_ids.py"
    status: todo
  - id: "1.2"
    description: "GraphEdge and ReferenceGraph data types"
    status: todo
  - id: "1.3"
    description: "Graph builder: _collect_all_artifacts + build_reference_graph"
    status: todo
  - id: "1.4"
    description: "Query functions: query_forward, query_inverse, query_neighbourhood"
    status: todo
  - id: "1.5"
    description: "find_unresolved_references function"
    status: todo
  - id: "1.6"
    description: "Tests for all above"
    status: todo
risks:
  - description: "collect_references may miss fields on some model types"
    mitigation: "Verified in DR review; test with real workspace fixture"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-097.PHASE-01
```

# Phase 1 — Domain layer: graph builder, query API, ID normalizer

## 1. Objective

Build the pure domain layer for cross-artifact reference graph operations. All functions are pure (no CLI, no I/O beyond registry access). Fully tested before CLI integration in phase 2.

## 2. Links & References

- **Delta**: DE-097
- **Design Revision**: DR-097 §4.1 (graph.py), §4.2 (artifact_ids.py)
- **Existing code**: `relations/query.py` (collect_references), `cli/resolve.py` (build_artifact_index), `core/artifact_ids.py`

## 3. Entrance Criteria

- [x] DR-097 approved

## 4. Exit Criteria / Done When

- [ ] `normalize_artifact_id` handles 3-digit and 4-digit padding, emits diagnostics
- [ ] `build_reference_graph` produces correct nodes and edges from workspace state
- [ ] `query_forward` / `query_inverse` / `query_neighbourhood` return correct edges
- [ ] `find_unresolved_references` detects dangling targets
- [ ] All tests pass, lint clean

## 5. Verification

- `pytest supekku/scripts/lib/relations/graph_test.py`
- `pytest supekku/scripts/lib/core/artifact_ids_test.py` (extended)
- `pylint` on new/modified files

## 6. Assumptions & STOP Conditions

- Assumes `collect_references` works on all registry model types (verified in DR)
- STOP if `Workspace` registry access patterns change during implementation

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | ID normalizer: `normalize_artifact_id` + `NormalizationResult` | [P] | Independent of graph work |
| [ ] | 1.2 | Data types: `GraphEdge`, `ReferenceGraph` | | Foundation for 1.3–1.5 |
| [ ] | 1.3 | Graph builder: `_collect_all_artifacts` + `build_reference_graph` | | Depends on 1.2 |
| [ ] | 1.4 | Query API: `query_forward`, `query_inverse`, `query_neighbourhood` | | Depends on 1.2 |
| [ ] | 1.5 | `find_unresolved_references` | | Depends on 1.2 |
| [ ] | 1.6 | Tests for 1.1–1.5 | | TDD — write with each task |

### Task Details

- **1.1 ID normalizer**
  - **Files**: `supekku/scripts/lib/core/artifact_ids.py`
  - **Approach**: Add `NormalizationResult` dataclass and `normalize_artifact_id(raw, known_ids)`. Parse prefix + digits with regex. Try increasing zero-padding against `known_ids`. Return first match with diagnostic if non-canonical.
  - **Testing**: Direct lookup (canonical), 2-digit → 3-digit, 2-digit → 4-digit, no match, already canonical, memory IDs (should not interfere)

- **1.2 Data types**
  - **Files**: `supekku/scripts/lib/relations/graph.py` (new)
  - **Approach**: `GraphEdge(source, target, source_slot, detail)` frozen dataclass. `ReferenceGraph` with nodes dict, edges list, lazy forward/inverse indices, diagnostics list.

- **1.3 Graph builder**
  - **Files**: `supekku/scripts/lib/relations/graph.py`
  - **Approach**: `_collect_all_artifacts(workspace)` iterates all registries. `build_reference_graph(workspace)` calls `collect_references` per artifact, wraps hits as `GraphEdge`, builds indices. Uses `normalize_artifact_id` on edge targets.

- **1.4 Query functions**
  - **Files**: `supekku/scripts/lib/relations/graph.py`
  - **Approach**: Simple dict lookups on forward/inverse indices. `query_neighbourhood` groups by direction.

- **1.5 find_unresolved_references**
  - **Files**: `supekku/scripts/lib/relations/graph.py`
  - **Approach**: Filter edges whose target is not in `graph.nodes`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Some registry `.collect()` returns may not support `collect_references` | Verified in DR; all models expose relevant attrs via getattr | mitigated |

## 9. Decisions & Outcomes

(None yet — record during implementation)

## 10. Findings / Research Notes

(Populate during implementation)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to phase 2
