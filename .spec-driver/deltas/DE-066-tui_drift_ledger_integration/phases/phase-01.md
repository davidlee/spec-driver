---
id: IP-066.PHASE-01
slug: 066-tui_drift_ledger_integration-phase-01
name: Wire and verify
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-066.PHASE-01
plan: IP-066
delta: DE-066
objective: >-
  Add DRIFT_LEDGER to ArtifactType, wire registry/metadata/path mapping,
  write tests, verify TUI renders drift ledgers.
entrance_criteria:
  - DE-065 complete (drift primitive exists)
  - artifact_view.py integration surface understood
exit_criteria:
  - DRIFT_LEDGER in ArtifactType enum with metadata
  - DriftLedgerRegistry wired via factory
  - path_to_artifact_type() maps drift paths
  - Unit tests for all wiring points
  - TUI type selector shows "Drift Ledger"
  - just check green
verification:
  tests:
    - VT-066-artifact-type
    - VT-066-path-mapping
  evidence:
    - VA-066-tui-e2e
tasks:
  - id: "1.1"
    description: add DRIFT_LEDGER to ArtifactType enum and metadata tables
  - id: "1.2"
    description: add registry factory and path mapping
  - id: "1.3"
    description: write tests
  - id: "1.4"
    description: verify TUI end-to-end
risks:
  - description: DriftLedger model may lack attributes expected by adapt_record
    mitigation: checked — DriftLedger has id, name, status, path (compatible)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-066.PHASE-01
```

# Phase 1 — Wire and verify

## 1. Objective

Add drift ledgers as a TUI-browsable artifact type by wiring `DriftLedgerRegistry`
into the `ArtifactType`/`ArtifactSnapshot` system in `artifact_view.py`.

## 2. Links & References

- **Delta**: DE-066
- **Dependency**: DE-065 (drift primitive — completed)
- **Key file**: `supekku/scripts/lib/core/artifact_view.py`
- **Registry**: `supekku/scripts/lib/drift/registry.py`

## 3. Entrance Criteria

- [x] DE-065 complete
- [x] `DriftLedgerRegistry.collect()` returns `dict[str, DriftLedger]` (compatible interface)
- [x] `DriftLedger` has `id`, `name`, `status`, `path` attributes

## 4. Exit Criteria / Done When

- [x] `ArtifactType.DRIFT_LEDGER` exists in enum (Operational group)
- [x] `ARTIFACT_TYPE_META`, `_TITLE_ATTR` entries added (STATUS/ID use defaults)
- [x] `_REGISTRY_FACTORIES` entry wired
- [x] `path_to_artifact_type()` maps `DRIFT_SUBDIR`
- [x] Unit tests cover all wiring points (8 new tests)
- [x] TUI shows drift ledgers in type selector
- [x] `just check` green (3293 pass, ruff clean, pylint 9.71)

## 5. Verification

- `just check` — all tests, linters clean
- Manual: `uv run spec-driver tui` — select Drift Ledger, verify DL-047 appears

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `adapt_record()` handles DriftLedger via `_TITLE_ATTR`/`_ID_ATTR` mappings (no special adapter needed)
  - TUI widgets (type selector, list, preview) work generically with any ArtifactType
- STOP when:
  - `adapt_record()` fails on DriftLedger (would need a custom adapter)

## 7. Tasks & Progress

| Status | ID  | Description                                | Parallel? | Notes            |
| ------ | --- | ------------------------------------------ | --------- | ---------------- |
| [x]    | 1.1 | Add DRIFT_LEDGER to enum + metadata tables | —         | done             |
| [x]    | 1.2 | Add registry factory + path mapping        | —         | done             |
| [x]    | 1.3 | Write tests                                | —         | 8 tests          |
| [x]    | 1.4 | Verify TUI end-to-end                      | —         | just check green |

### Task Details

- **1.1 Enum + metadata**
  - Add `DRIFT_LEDGER = "drift_ledger"` to `ArtifactType` in Operational group
  - Add `ArtifactTypeMeta("Drift Ledger", "Drift Ledgers", _OPS)` to `ARTIFACT_TYPE_META`
  - Add `_TITLE_ATTR[DRIFT_LEDGER] = "name"`
  - Add `_STATUS_ATTR` and `_ID_ATTR` entries
  - Lint after changes

- **1.2 Registry factory + path mapping**
  - Add `_make_drift_registry(root)` factory function
  - Add to `_REGISTRY_FACTORIES`
  - Import `DRIFT_SUBDIR` in `path_to_artifact_type()` and add to `_subdir_map`

- **1.3 Tests**
  - Test DRIFT_LEDGER enum membership and metadata
  - Test `path_to_artifact_type()` with drift paths
  - Test `ArtifactSnapshot` loads drift ledgers via factory

- **1.4 TUI verification**
  - `uv run spec-driver tui` — confirm type selector, list, preview

## 8. Risks & Mitigations

| Risk                                                    | Mitigation                                      | Status   |
| ------------------------------------------------------- | ----------------------------------------------- | -------- |
| DriftLedger record shape incompatible with adapt_record | Pre-checked: id, name, status, path all present | resolved |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (3293 tests, linters clean)
- [x] Phase sheet updated with outcomes
