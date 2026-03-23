---
id: IP-127-P01
slug: "127-audit_and_reclassify_core_misplaced_integration_hubs-phase-01"
name: "Reclassify artifact_view and enums to orchestration"
created: "2026-03-24"
updated: "2026-03-24"
status: draft
kind: phase
plan: IP-127
delta: DE-127
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-127-P01
plan: IP-127
delta: DE-127
objective: >-
  Move artifact_view.py and enums.py from core/ to orchestration, add re-export
  shims, and verify that core/ has zero cross-area imports afterward.
entrance_criteria:
  - DR-127 classification table reviewed
  - DE-125 migration pattern available (re-export shims, import-linter verification)
exit_criteria:
  - artifact_view.py lives in spec_driver/orchestration/
  - enums.py lives in spec_driver/orchestration/
  - Re-export shims in supekku/scripts/lib/core/ for both modules
  - core/ has zero cross-area imports (verified by script)
  - All tests pass
  - Both import-linter contracts pass
  - ruff clean
verification:
  tests:
    - uv run pytest supekku spec_driver -x
    - uvx import-linter lint
    - uv run ruff check
    - uv run spec-driver validate
  evidence:
    - Cross-area import count script output
    - import-linter output
tasks:
  - Move artifact_view.py to spec_driver/orchestration/
  - Create re-export shim for artifact_view at legacy location
  - Move enums.py to spec_driver/orchestration/
  - Create re-export shim for enums at legacy location
  - Verify core/ has zero cross-area imports
  - Run full verification suite
risks:
  - TUI consumers may have import-time side effects from the move
  - enums.py lifecycle imports may need path adjustments
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-127-P01
files:
  references:
    - .spec-driver/deltas/DE-127-audit_and_reclassify_core_misplaced_integration_hubs/DR-127.md
    - pyproject.toml
  context:
    - supekku/scripts/lib/core/artifact_view.py
    - supekku/scripts/lib/core/enums.py
    - spec_driver/orchestration/__init__.py
    - spec_driver/orchestration/operations.py
entrance_criteria:
  - item: "DR-127 classification table reviewed"
    completed: true
  - item: "DE-125 migration pattern available"
    completed: true
exit_criteria:
  - item: "artifact_view.py lives in spec_driver/orchestration/"
    completed: false
  - item: "enums.py lives in spec_driver/orchestration/"
    completed: false
  - item: "Re-export shims at legacy locations"
    completed: false
  - item: "core/ has zero cross-area imports"
    completed: false
  - item: "All tests pass"
    completed: false
  - item: "Both import-linter contracts pass"
    completed: false
tasks:
  - id: "1"
    description: "Move artifact_view.py to spec_driver/orchestration/"
    status: pending
  - id: "2"
    description: "Create re-export shim for artifact_view at legacy location"
    status: pending
  - id: "3"
    description: "Move enums.py to spec_driver/orchestration/"
    status: pending
  - id: "4"
    description: "Create re-export shim for enums at legacy location"
    status: pending
  - id: "5"
    description: "Verify core/ has zero cross-area imports"
    status: pending
  - id: "6"
    description: "Run full verification suite"
    status: pending
```

# Phase 1 — Reclassify artifact_view and enums to orchestration

## 1. Objective

Move the two misplaced integration hubs out of `core/` and into
`spec_driver/orchestration/`, following the DE-125 migration pattern. After this
phase, `core/` is genuinely foundational with zero cross-area imports.

## 2. Links & References

- **Delta**: [DE-127](../DE-127.md)
- **Design Revision**: [DR-127](../DR-127.md) §3 (classification), §4 (reclassification design)
- **Migration pattern**: [mem.pattern.architecture.domain-migration](../../../memory/mem.pattern.architecture.domain-migration.md)
- **Modules**:
  - `supekku/scripts/lib/core/artifact_view.py` → `spec_driver/orchestration/artifact_view.py`
  - `supekku/scripts/lib/core/enums.py` → `spec_driver/orchestration/enums.py`

## 3. Entrance Criteria

- [x] DR-127 classification table reviewed
- [x] DE-125 migration pattern available (re-export shims, import-linter verification)

## 4. Exit Criteria / Done When

- [ ] `artifact_view.py` lives in `spec_driver/orchestration/`
- [ ] `enums.py` lives in `spec_driver/orchestration/`
- [ ] Re-export shims in `supekku/scripts/lib/core/` for both modules
- [ ] `core/` has zero cross-area imports (verified by script)
- [ ] All tests pass
- [ ] Both import-linter contracts pass
- [ ] ruff clean

## 5. Verification

- Cross-area import audit:
  ```bash
  for f in supekku/scripts/lib/core/*.py; do
    count=$(rg "from supekku.scripts.lib." "$f" 2>/dev/null | grep -v "from supekku.scripts.lib.core" | wc -l)
    [ "$count" -gt 0 ] && echo "FAIL: $(basename $f) has $count cross-area imports"
  done
  ```
- `uvx import-linter lint`
- `uv run pytest supekku spec_driver -x`
- `uv run ruff check`
- `uv run spec-driver validate`

## 6. Assumptions & STOP Conditions

- **Assumption**: `artifact_view.py` can move to orchestration without changing
  the `spec_driver.orchestration.__init__` public API — it's an internal module.
- **Assumption**: `enums.py` lifecycle imports work regardless of where the
  aggregation module lives, since the imports point at leaf modules.
- **STOP**: if import-linter shows a new violation from the move (e.g.
  `orchestration` importing something it shouldn't), investigate before
  proceeding.
- **STOP**: if `artifact_view` types need to be in the public `orchestration`
  API, decide explicitly rather than auto-exporting.

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [ ]    | 1.1 | Move `artifact_view.py` to `spec_driver/orchestration/` | 456 lines, 10 registry imports |
| [ ]    | 1.2 | Create re-export shim at `supekku/scripts/lib/core/artifact_view.py` | 7 TUI consumer sites |
| [ ]    | 1.3 | Move `enums.py` to `spec_driver/orchestration/` | 111 lines, 11 lifecycle imports |
| [ ]    | 1.4 | Create re-export shim at `supekku/scripts/lib/core/enums.py` | 3 consumer sites |
| [ ]    | 1.5 | Verify core/ has zero cross-area imports | Run audit script |
| [ ]    | 1.6 | Run full verification suite | Tests, contracts, lint |

### Task Details

- **1.1 Move artifact_view.py**
  - Copy to `spec_driver/orchestration/artifact_view.py`.
  - The module's registry imports still use legacy paths — that's acceptable
    (same pattern as DE-125 domain modules importing legacy core).
  - Do not add to `spec_driver.orchestration.__init__` unless explicitly decided.

- **1.2 Re-export shim for artifact_view**
  - Replace `supekku/scripts/lib/core/artifact_view.py` with re-exports from
    `spec_driver.orchestration.artifact_view`.
  - Must preserve all public names: `ArtifactType`, `ArtifactGroup`,
    `ArtifactTypeMeta`, `ArtifactEntry`, `ArtifactSnapshot`, and all functions.

- **1.3 Move enums.py**
  - Copy to `spec_driver/orchestration/enums.py`.
  - Lifecycle constant imports stay as-is (they point at domain leaf modules).

- **1.4 Re-export shim for enums**
  - Replace `supekku/scripts/lib/core/enums.py` with re-exports from
    `spec_driver.orchestration.enums`.
  - Must preserve: `ENUM_REGISTRY`, `get_enum_values`, `list_enum_paths`,
    `validate_status_for_entity`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| TUI import-time side effects | Re-export shim + lazy imports already used by TUI | open |
| enums lifecycle paths change during broader migration | Aggregation pattern stable; only paths fragile | open |

## 9. Decisions & Outcomes

_(To be filled during execution)_

## 10. Findings / Research Notes

_(To be filled during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
