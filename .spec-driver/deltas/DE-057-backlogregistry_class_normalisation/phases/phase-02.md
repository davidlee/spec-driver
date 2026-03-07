---
id: IP-057.PHASE-02
slug: 057-backlogregistry_class_normalisation-phase-02
name: IP-057 Phase 02 - Integration
created: '2026-03-07'
updated: '2026-03-07'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-057.PHASE-02
plan: IP-057
delta: DE-057
objective: >-
  Remove artifact_view.py shim, update CLI consumers, fix operational gaps
entrance_criteria:
  - Phase 1 complete (BacklogRegistry class + status sets tested)
exit_criteria:
  - _collect_backlog() shim removed from artifact_view.py
  - BacklogRegistry in _REGISTRY_FACTORIES via standard factory
  - _load_type() special-case for BACKLOG removed
  - CLI consumers use BacklogRegistry (common.py, list.py, sync.py, create.py)
  - ISSUE-026 fixed (dry_run threaded)
  - ISSUE-034 fixed (link resolver supports backlog)
  - ISSUE-043 mitigated (ID validation callback)
  - VT-057-artifact-view, -sync-dryrun, -link-resolver, -from-backlog pass
  - VT-057-regression passes
  - just passes
verification:
  tests:
    - VT-057-artifact-view
    - VT-057-sync-dryrun
    - VT-057-link-resolver
    - VT-057-from-backlog
    - VT-057-regression
  evidence: []
tasks:
  - id: '2.1'
    description: Remove artifact_view.py shim, add factory
  - id: '2.2'
    description: Update cli/common.py resolvers
  - id: '2.3'
    description: Update cli/list.py to use BacklogRegistry
  - id: '2.4'
    description: Fix ISSUE-026 — dry_run threading in sync.py
  - id: '2.5'
    description: Fix ISSUE-034 — link resolver backlog support
  - id: '2.6'
    description: Fix ISSUE-043 — --from-backlog validation callback
  - id: '2.7'
    description: Write/update tests for all integration changes
risks:
  - description: Shim removal changes error behaviour
    mitigation: Test per-record error placeholders explicitly (DEC-057-09)
  - description: common.py resolver regresses kind scoping
    mitigation: Preserve kind validation and ambiguity handling
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-057.PHASE-02
```

# Phase 2 - Integration

## 1. Objective

Wire `BacklogRegistry` into all consumers, remove the artifact_view.py shim,
and fix the three operational gaps (ISSUE-026, -034, -043).

## 2. Links & References

- **Delta**: DE-057
- **Design Revision**: DR-057 (DEC-057-06, -07, -09)
- **Code**:
  - `supekku/scripts/lib/core/artifact_view.py` (shim removal)
  - `supekku/cli/common.py` (resolver update)
  - `supekku/cli/list.py` (list_backlog update)
  - `supekku/cli/sync.py` (dry_run fix)
  - `supekku/cli/create.py` (--from-backlog fix)
  - `supekku/cli/resolve.py` (link resolver)

## 3. Entrance Criteria

- [ ] Phase 1 complete — BacklogRegistry class tested and passing
- [ ] Module-level wrappers verified working

## 4. Exit Criteria / Done When

- [ ] `_collect_backlog()` deleted from `artifact_view.py`
- [ ] `_load_type()` no longer has `BACKLOG` special-case
- [ ] `_REGISTRY_FACTORIES[ArtifactType.BACKLOG]` = `_make_backlog_registry`
- [ ] `_resolve_backlog()` in common.py uses `BacklogRegistry(root=root)`
      with kind scoping and ambiguity detection preserved
- [ ] `list_backlog()` uses `BacklogRegistry` + `DEFAULT_HIDDEN_STATUSES`
- [ ] `_sync_backlog(dry_run=...)` threads param; no writes when True
- [ ] `_build_artifact_index()` includes backlog items
- [ ] `--from-backlog` has `_validate_backlog_id` callback
- [ ] All VTs pass, `just` passes

## 5. Verification

- `VT-057-artifact-view`: Extend `artifact_view_test.py`
  - BacklogRegistry appears in `_REGISTRY_FACTORIES`
  - `ArtifactSnapshot` loads backlog via standard path (no shim)
  - Malformed backlog item produces ArtifactEntry with error field
    (DEC-057-09 — not silently skipped)
- `VT-057-sync-dryrun`: In `sync_test.py` or inline
  - `_sync_backlog(root, dry_run=True)` returns stats but no files written
- `VT-057-link-resolver`: In resolver test file
  - `[[ISSUE-016]]`, `[[PROB-002]]`, `[[IMPR-009]]`, `[[RISK-001]]` resolve
  - Unknown backlog ID returns missing link
- `VT-057-from-backlog`: In `create_test.py`
  - `--from-backlog ISSUE-001` works normally
  - `--from-backlog --spec` raises BadParameter with clear message
  - `--from-backlog xyzzy` raises BadParameter
- `VT-057-regression`: All existing backlog tests pass unchanged
- Run: `just test`, `just lint`, `just pylint`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Phase 1 BacklogRegistry.collect() returns dict compatible with
    `_collect_safe()` expectations
  - Link resolver follows same pattern as existing `_collect_*` functions
- STOP when:
  - artifact_view.py tests reveal subtle dependencies on shim error behaviour
  - common.py resolver has callers depending on `find_backlog_items_by_id()`
    returning a list (ambiguity case)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Remove artifact_view.py shim, add factory | | DEC-057-09 |
| [ ] | 2.2 | Update cli/common.py resolvers | | Preserve kind scoping |
| [ ] | 2.3 | Update cli/list.py | | Use DEFAULT_HIDDEN_STATUSES |
| [ ] | 2.4 | Fix ISSUE-026 — dry_run in sync.py | [P] | Independent |
| [ ] | 2.5 | Fix ISSUE-034 — link resolver | [P] | Independent |
| [ ] | 2.6 | Fix ISSUE-043 — --from-backlog callback | [P] | DEC-057-07 |
| [ ] | 2.7 | Write/update tests | | After 2.1-2.6 |
| [ ] | 2.8 | Lint + full test pass | | After all above |

### Task Details

- **2.1 Remove artifact_view.py shim**
  - **Files**: `supekku/scripts/lib/core/artifact_view.py`
  - **Approach**: Delete `_collect_backlog()` function. Remove
    `if art_type == ArtifactType.BACKLOG:` branch in `_load_type()`. Add
    `_make_backlog_registry` factory function. Add entry to
    `_REGISTRY_FACTORIES`. Verify error behaviour: malformed items now go
    through `_collect_safe()` → per-record error placeholders (DEC-057-09).
  - **Testing**: VT-057-artifact-view

- **2.2 Update cli/common.py resolvers**
  - **Files**: `supekku/cli/common.py`
  - **Approach**: `_resolve_backlog()` uses `BacklogRegistry(root=root)`.
    **Must preserve**: kind scoping (filter by kind when kind is specified),
    ambiguity detection (multiple matches → AmbiguousArtifactError).
    Use keyword-only `root=root` per ADR-009.
  - **Testing**: Existing resolver tests + VT-057-regression

- **2.3 Update cli/list.py**
  - **Files**: `supekku/cli/list.py`
  - **Approach**: Replace `discover_backlog_items()` with
    `BacklogRegistry(root=repo_root)`. Replace hardcoded
    `["resolved", "implemented"]` with `DEFAULT_HIDDEN_STATUSES` import.
    Ensure no behaviour change to default list output.
  - **Testing**: VT-057-regression

- **2.4 Fix ISSUE-026 — dry_run threading**
  - **Files**: `supekku/cli/sync.py`,
    `supekku/scripts/lib/backlog/registry.py`
  - **Approach**: Add `dry_run: bool = False` param to `_sync_backlog()`.
    Thread to `sync_backlog_registry()`. When `dry_run=True`: discover
    items, compute stats, but skip `save_backlog_registry()` call.
  - **Testing**: VT-057-sync-dryrun

- **2.5 Fix ISSUE-034 — link resolver**
  - **Files**: `supekku/cli/resolve.py`
  - **Approach**: Add `_collect_backlog_items(root, index)` following
    existing `_collect_decisions()` pattern. Call from
    `_build_artifact_index()`. Keys: item IDs (ISSUE-016, PROB-002, etc.).
    Values: `(relative_path, kind)`.
  - **Testing**: VT-057-link-resolver

- **2.6 Fix ISSUE-043 — --from-backlog validation**
  - **Files**: `supekku/cli/create.py`
  - **Approach**: Add `_validate_backlog_id()` callback to `--from-backlog`
    option. Replace `discover_backlog_items()` with
    `BacklogRegistry(root=root).find()`. This is a **mitigation**, not a
    root cause fix (DEC-057-07).
  - **Testing**: VT-057-from-backlog

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Shim removal error behaviour change | Test per-record placeholders explicitly (DEC-057-09) | open |
| common.py drops kind scoping | Preserve kind validation in resolver (adversarial review finding) | open |
| --from-backlog still greedy for --help | Acknowledged as Click limitation; mitigation only (DEC-057-07) | accepted |

## 9. Decisions & Outcomes

- 2026-03-07 - All design decisions pre-resolved in DR-057

## 10. Findings / Research Notes

- artifact_view.py `_collect_safe()` emits per-record error entries vs
  current shim's log-and-skip. Intentional behaviour improvement (DEC-057-09).
- Tasks 2.4, 2.5, 2.6 are independent of each other and of 2.1-2.3.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 3
