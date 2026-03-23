---
id: IP-125-P03
slug: "125-enforce_explicit_module_boundaries_and_coupling_constraints-phase-03"
name: "Pilot migration: relations and backlink seam"
created: "2026-03-24"
updated: "2026-03-24"
status: completed
kind: phase
plan: IP-125
delta: DE-125
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-125-P03
plan: IP-125
delta: DE-125
objective: >-
  Move relations modules into spec_driver/domain/relations/, extract backlink
  computation into a generic relations helper, and leave re-export shims in
  the legacy locations so existing consumers are not broken.
entrance_criteria:
  - Phase 2 completed with contract, pilot targets, and seam specification
  - Domain Internal Layers contract passing in import-linter
  - Domain subpackage stubs exist under spec_driver/domain/
exit_criteria:
  - relations/query.py, manager.py, graph.py live under spec_driver/domain/relations/
  - Re-export shims in supekku/scripts/lib/relations/ forward to new locations
  - build_backlinks() generic helper exists in spec_driver/domain/relations/backlinks.py
  - PolicyRegistry._build_backlinks uses the new helper (no lazy sibling import)
  - StandardsRegistry._build_backlinks uses the new helper (no lazy sibling import)
  - All existing tests pass without modification (or with minimal import updates)
  - import-linter lint passes (both contracts)
verification:
  tests:
    - uv run pytest supekku/scripts/lib/relations/ -v
    - uv run pytest supekku/scripts/lib/policies/registry_test.py -v
    - uv run pytest supekku/scripts/lib/standards/registry_test.py -v
  evidence:
    - uvx import-linter lint output
    - pytest output for relations, policies, standards
tasks:
  - Move query.py to spec_driver/domain/relations/
  - Move graph.py to spec_driver/domain/relations/
  - Move manager.py to spec_driver/domain/relations/
  - Create re-export shims in legacy locations
  - Implement build_backlinks() generic helper
  - Refactor PolicyRegistry._build_backlinks to use helper
  - Refactor StandardsRegistry._build_backlinks to use helper
  - Verify all tests and contracts pass
risks:
  - relations.manager may be too tightly coupled to core for a clean move
  - Re-export shims may mask import issues that surface later
  - Backlink extraction may reveal additional coupling not visible in static analysis
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-125-P03
files:
  references:
    - pyproject.toml
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/DR-125.md
    - .spec-driver/deltas/DE-125-enforce_explicit_module_boundaries_and_coupling_constraints/phases/phase-02.md
  context:
    - supekku/scripts/lib/relations/query.py
    - supekku/scripts/lib/relations/manager.py
    - supekku/scripts/lib/relations/graph.py
    - supekku/scripts/lib/policies/registry.py
    - supekku/scripts/lib/standards/registry.py
    - spec_driver/domain/relations/__init__.py
entrance_criteria:
  - item: "Phase 2 completed with contract, pilot targets, and seam specification"
    completed: false
  - item: "Domain Internal Layers contract passing in import-linter"
    completed: true
  - item: "Domain subpackage stubs exist under spec_driver/domain/"
    completed: true
exit_criteria:
  - item: "relations modules live under spec_driver/domain/relations/"
    completed: true
  - item: "Re-export shims in legacy locations"
    completed: true
  - item: "build_backlinks() generic helper exists"
    completed: true
  - item: "PolicyRegistry uses new helper"
    completed: true
  - item: "StandardsRegistry uses new helper"
    completed: true
  - item: "All tests pass"
    completed: true
  - item: "import-linter lint passes"
    completed: true
tasks:
  - id: "1"
    description: "Move query.py to spec_driver/domain/relations/"
    status: completed
  - id: "2"
    description: "Move graph.py to spec_driver/domain/relations/"
    status: completed
  - id: "3"
    description: "Move manager.py to spec_driver/domain/relations/"
    status: completed
  - id: "4"
    description: "Create re-export shims in legacy locations"
    status: completed
  - id: "5"
    description: "Implement build_backlinks() generic helper"
    status: completed
  - id: "6"
    description: "Refactor PolicyRegistry._build_backlinks to use helper"
    status: completed
  - id: "7"
    description: "Refactor StandardsRegistry._build_backlinks to use helper"
    status: completed
  - id: "8"
    description: "Verify all tests and contracts pass"
    status: completed
```

# Phase 3 — Pilot migration: relations and backlink seam

## 1. Objective

Execute the first code-moving pilot: relocate the three relations modules into
`spec_driver/domain/relations/`, extract the duplicated backlink computation
pattern into a generic helper in the same package, and refactor both
`PolicyRegistry` and `StandardsRegistry` to use it instead of lazy-importing
sibling registries.

## 2. Links & References

- **Delta**: [DE-125](../DE-125.md)
- **Design Revision**: [DR-125](../DR-125.md) §3.2 (domain ordering), §3.3 (registry rule), §5.2
- **Phase 2 findings**: [phase-02.md](./phase-02.md) §10
- **Pilot modules**:
  - `supekku/scripts/lib/relations/query.py` → `spec_driver/domain/relations/query.py`
  - `supekku/scripts/lib/relations/graph.py` → `spec_driver/domain/relations/graph.py`
  - `supekku/scripts/lib/relations/manager.py` → `spec_driver/domain/relations/manager.py`
- **Backlink seam targets**:
  - `supekku/scripts/lib/policies/registry.py` — `_build_backlinks()`
  - `supekku/scripts/lib/standards/registry.py` — `_build_backlinks()`

## 3. Entrance Criteria

- [x] Domain Internal Layers contract passing in import-linter
- [x] Domain subpackage stubs exist under `spec_driver/domain/`
- [ ] Phase 2 completed (pending phase-complete)

## 4. Exit Criteria / Done When

- [x] `query.py`, `graph.py`, `manager.py` live under `spec_driver/domain/relations/`
- [x] Re-export shims in `supekku/scripts/lib/relations/` forward to new locations
- [x] `build_backlinks()` generic helper exists in `spec_driver/domain/relations/backlinks.py`
- [x] `PolicyRegistry._build_backlinks` uses the new helper (no lazy sibling import)
- [x] `StandardsRegistry._build_backlinks` uses the new helper (no lazy sibling import)
- [x] All existing tests pass (4656 passed)
- [x] `import-linter lint` passes (both contracts)

## 5. Verification

- `uvx import-linter lint`
- `uv run pytest supekku/scripts/lib/relations/ -v`
- `uv run pytest supekku/scripts/lib/policies/registry_test.py -v`
- `uv run pytest supekku/scripts/lib/standards/registry_test.py -v`
- `uv run spec-driver validate`

## 6. Assumptions & STOP Conditions

- **Assumption**: `manager.py`'s dependency on `core.frontmatter_schema` and
  `core.spec_utils` is acceptable for a `domain.relations` module because those
  are lower-layer core utilities.
- **Assumption**: re-export shims are sufficient to avoid a flag-day for all
  consumers.
- **STOP**: If `manager.py` turns out to be generic frontmatter mutation
  infrastructure rather than domain relations logic, reclassify it to `core`
  before moving.
- **STOP**: If backlink extraction reveals that the caller needs registry
  instantiation logic that belongs in orchestration, define that boundary before
  proceeding.

## 7. Tasks & Progress

| Status | ID  | Description                                              | Notes                                                     |
| ------ | --- | -------------------------------------------------------- | --------------------------------------------------------- |
| [x]    | 3.1 | Move `query.py` to `spec_driver/domain/relations/`      | Verbatim copy, pure stdlib                                |
| [x]    | 3.2 | Move `graph.py` to `spec_driver/domain/relations/`      | Split: pure graph model moved, workspace collection stays |
| [x]    | 3.3 | Move `manager.py` to `spec_driver/domain/relations/`    | Keeps supekku.scripts.lib.core imports for now             |
| [x]    | 3.4 | Create re-export shims in legacy locations               | All consumers unaffected                                  |
| [x]    | 3.5 | Implement `build_backlinks()` generic helper             | + `build_backlinks_multi()`, 11 tests                     |
| [x]    | 3.6 | Refactor `PolicyRegistry._build_backlinks`               | Uses `build_backlinks()`, still lazy-imports DecisionReg   |
| [x]    | 3.7 | Refactor `StandardsRegistry._build_backlinks`            | Uses `build_backlinks_multi()`, collects sources first    |
| [x]    | 3.8 | Verify all tests and contracts pass                      | 4656 passed, 2 contracts kept, ruff clean                 |

### Task Details

- **3.1–3.3 Module moves**
  - Copy module to new location, update internal imports to use `spec_driver.core`
    instead of `supekku.scripts.lib.core`.
  - Update `spec_driver/domain/relations/__init__.py` to re-export the public API.

- **3.4 Re-export shims**
  - Replace module contents in `supekku/scripts/lib/relations/` with re-exports
    from `spec_driver.domain.relations.*`.
  - Preserve `__all__` and public names so downstream code is unaffected.

- **3.5 `build_backlinks()` helper**
  - Generic function that clears existing backlinks on targets, iterates source
    records, and populates reverse maps keyed by category.
  - Signature: `build_backlinks(targets, sources, category, clear=True)`.
  - Sources are `Iterable[tuple[source_id, Iterable[target_id]]]`.

- **3.6–3.7 Registry refactoring**
  - Each registry's `_build_backlinks` becomes a thin wrapper that calls the
    generic helper with pre-collected source data.
  - The **caller** (likely `sync()` or orchestration) is responsible for
    collecting source records before passing them in, eliminating the need for
    lazy sibling-registry imports inside the method.

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                       | Status |
| ------------------------------------------------------ | ------------------------------------------------ | ------ |
| `manager.py` is generic infrastructure, not domain     | Check classification before moving               | open   |
| Re-export shims mask import issues                     | Run full test suite, not just relations tests     | open   |
| Backlink extraction reveals deeper orchestration needs | Define boundary before proceeding (STOP)         | open   |

## 9. Decisions & Outcomes

- `2026-03-24` — Split `graph.py` rather than moving it wholesale. The pure graph
  model, `build_reference_graph_from_artifacts()`, and query functions moved to
  `spec_driver/domain/relations/graph.py`. The workspace-dependent collection
  functions (`build_reference_graph()`, `_collect_all_artifacts()`, etc.) stay in
  the legacy location because they instantiate multiple registries and Workspace —
  that's orchestration-level glue, not domain relations.
- `2026-03-24` — `PolicyRegistry` still lazy-imports `DecisionRegistry` to collect
  source data. The backlink *computation* is now generic, but the *data collection*
  remains a registry concern until orchestration owns the sync workflow. This is
  an acceptable intermediate state — the coupling is now explicit and narrow.
- `2026-03-24` — `StandardsRegistry` uses `build_backlinks_multi()` to handle two
  source categories (decisions + policies) in one call with a single clear pass.

## 10. Findings / Research Notes

- `query.py` moved cleanly with zero changes — it's pure stdlib.
- `manager.py` still imports from `supekku.scripts.lib.core.*` because those core
  modules haven't migrated yet. This is fine — the domain package structure is
  established even if some downward imports still use legacy paths.
- `graph.py` split revealed that `_collect_all_artifacts` is really orchestration:
  it instantiates `BacklogRegistry`, `DriftLedgerRegistry`, `MemoryRegistry`, and
  walks `Workspace` properties. Moving that to `spec_driver.orchestration` is
  natural future work.
- The backlink pattern was identical in both registries except for number of source
  categories. `build_backlinks_multi()` handles the multi-category case cleanly.
- Re-export shims work transparently — all 4656 tests pass without any consumer
  changes.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
