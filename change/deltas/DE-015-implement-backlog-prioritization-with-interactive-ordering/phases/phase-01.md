---
id: IP-015.PHASE-01
slug: 015-implement-backlog-prioritization-with-interactive-ordering-phase-01
name: IP-015 Phase 01
created: '2025-11-04'
updated: '2025-11-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-015.PHASE-01
plan: IP-015
delta: DE-015
objective: >-
  Create backlog registry infrastructure with sync command to initialize and maintain ordered list of backlog item IDs
entrance_criteria:
  - IP-015 approved
  - Research findings reviewed
exit_criteria:
  - Registry YAML schema defined at .spec-driver/registry/backlog.yaml
  - sync backlog command working
  - Registry read/write functions implemented and tested
  - VT-015-002 tests passing
  - Lint checks pass
verification:
  tests:
    - VT-015-002
  evidence:
    - sync command output
    - generated registry file
tasks:
  - 1.1 Define registry YAML schema
  - 1.2 Implement registry read/write functions
  - 1.3 Create sync backlog command
  - 1.4 Write comprehensive tests
  - 1.5 Run lint and fix issues
risks:
  - Registry file conflicts with concurrent edits (low impact, document limitation)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-015.PHASE-01
status: in-progress
started: '2025-11-04'
tasks_completed: 6
tasks_total: 8
last_updated: '2025-11-04'
notes: |
  Tasks 1.1-1.6 complete: Unit tests passing
  - Registry infrastructure complete and tested
  - 9 new unit tests added (VT-015-002)
  - All 12 tests passing in 0.07s ✓
  - Test coverage: load, save, sync (init, preserve, append, prune, mixed)
  - Pylint score: 10.00/10 ✓
  - Ready for CLI integration tests (task 1.7) or final lint (task 1.8)
```

# Phase 1 - Registry Infrastructure

## 1. Objective

Create the foundational backlog registry system that stores an ordered list of backlog item IDs. Implement a `sync backlog` command that discovers items from the filesystem and initializes/updates the registry file.

## 2. Links & References
- **Delta**: [DE-015](../DE-015.md)
- **Research**: [research-findings.md](../../../../backlog/improvements/IMPR-002-backlog-prioritization-with-interactive-ordering-and-delta-integration/research-findings.md)
- **Current backlog code**: `supekku/scripts/lib/backlog/registry.py`
- **Existing registry examples**: `.spec-driver/registry/decisions.yaml`, `.spec-driver/registry/requirements.yaml`

## 3. Entrance Criteria
- [x] IP-015 approved
- [x] Research findings document reviewed
- [x] Current backlog code structure understood

## 4. Exit Criteria / Done When
- [x] Registry file `.spec-driver/registry/backlog.yaml` created with schema
- [x] `sync backlog` command implemented and working (via `spec-driver sync --backlog`)
- [ ] Registry read/write functions tested
- [ ] All tests passing (`just test`)
- [ ] Lint checks passing (`just lint`, `just pylint`)
- [x] Registry correctly handles: new items (append), deleted items (prune), existing items (preserve order)

## 5. Verification

**Tests (VT-015-002):**
- Unit tests for registry read/write functions
- Tests for sync command: initialization, updates, orphan pruning
- Edge cases: empty backlog, missing registry, corrupted YAML

**Commands:**
```bash
# Run tests
just test

# Lint checks
just lint
just pylint

# Manual verification
uv run spec-driver sync backlog
cat .spec-driver/registry/backlog.yaml
uv run spec-driver list backlog  # should still work (registry not yet used for ordering)
```

**Evidence:**
- Test output showing all VT-015-002 tests passing
- Generated `backlog.yaml` file with correct schema
- Sync command output showing discovered items

## 6. Assumptions & STOP Conditions

**Assumptions:**
- Registry schema mirrors decisions.yaml pattern (ordered list in YAML)
- Sync is manual operation (not auto-triggered)
- Single-user tool (no file locking needed initially)
- Existing `discover_backlog_items()` provides correct item list

**STOP when:**
- Tests fail repeatedly despite fixes (may indicate design flaw)
- Registry format needs significant redesign (escalate to user)
- Discovered items don't match expectations (verify filesystem scanning logic)

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Define registry YAML schema | [ ] | Created .spec-driver/registry/backlog.yaml |
| [x] | 1.2 | Implement registry read function | [ ] | load_backlog_registry() complete |
| [x] | 1.3 | Implement registry write function | [ ] | save_backlog_registry() complete |
| [x] | 1.4 | Implement sync logic | [ ] | sync_backlog_registry() complete |
| [x] | 1.5 | Add sync command to CLI | [ ] | --backlog flag added to sync |
| [x] | 1.6 | Write unit tests | [P] | 9 new tests, all passing |
| [ ] | 1.7 | Write integration tests | [ ] | After 1.5 complete |
| [ ] | 1.8 | Run lint and fix issues | [ ] | Final cleanup |

### Task Details

**1.1 - Define registry YAML schema** ✅
- **Design**: Simple ordered list, similar to requirements registry but minimal
  ```yaml
  ordering:
    - ISSUE-003
    - IMPR-002
    - ISSUE-005
  ```
- **Files**: `.spec-driver/registry/backlog.yaml` created
- **Testing**: Manual YAML validation - structure confirmed
- **Observations**:
  - Kept schema minimal - just ordered list of IDs
  - Added header comments documenting purpose and usage
  - Initialized with empty list (will populate via sync command)
  - Follows same pattern as other registries but simpler structure
- **Commits**: Ready to commit after phase tracking updated

**1.2 - Implement registry read function** ✅
- **Design**: `load_backlog_registry(root: Path) -> list[str]`
  - Return list of IDs in order
  - Return empty list if file doesn't exist
  - Raise error if YAML is invalid
- **Files**: `supekku/scripts/lib/backlog/registry.py:89-114`
- **Testing**: Unit tests with temp files (task 1.6)
- **Observations**:
  - Defensive parsing: returns empty list if file missing or malformed
  - Uses yaml.safe_load for security
  - Validates data structure before returning
  - Auto-detects repo root if not provided

**1.3 - Implement registry write function** ✅
- **Design**: `save_backlog_registry(ordering: list[str], root: Path | None)`
  - Write ordered list to YAML
  - Create parent directories if needed
  - Atomic write via Path.write_text
- **Files**: `supekku/scripts/lib/backlog/registry.py:117-142`
- **Testing**: Unit tests verify file contents (task 1.6)
- **Observations**:
  - Creates registry directory if missing
  - Uses yaml.safe_dump with sort_keys=False to preserve order
  - Direct write (not temp file) - acceptable for this use case
  - Added to __all__ exports for public API

**1.4 - Implement sync logic** ✅
- **Design**: `sync_backlog_registry(root: Path | None) -> dict[str, int]`
  - Call `discover_backlog_items()` to get all items
  - Load existing registry (if exists)
  - Merge: preserve order for existing items, append new items sorted by ID
  - Prune: remove IDs not in discovered items
  - Save updated registry
  - Return statistics dict: total, added, removed, unchanged
- **Files**: `supekku/scripts/lib/backlog/registry.py:145-189`
- **Testing**: Unit tests with various scenarios (task 1.6)
- **Observations**:
  - Clean merge algorithm: filter existing order, append sorted new items
  - Returns useful stats for CLI display
  - Handles empty registry (all items are "new")
  - Handles orphaned items gracefully (pruned from order)
  - Set operations make logic clear and efficient

**1.5 - Add sync command to CLI** ✅
- **Design**: Add `--backlog` flag to `spec-driver sync` command
  - Follows existing pattern from `--adr` flag
  - Calls `_sync_backlog()` helper which calls `sync_backlog_registry()`
  - Prints summary: total, added, removed, unchanged
- **Files**: `supekku/cli/sync.py:82-88, 165-173, 553-565`
- **Testing**: Manual test successful - synced 18 items ✓
- **Observations**:
  - Integrated into main sync command (not separate subcommand)
  - Follows thin CLI pattern - delegates to domain
  - Displays useful stats from sync operation
  - Works alongside --adr, --specs flags
  - Command: `spec-driver sync --backlog`
  - Registry file generated at .spec-driver/registry/backlog.yaml

**1.6 - Write unit tests** ✅
- **Design**: Comprehensive unit tests for VT-015-002
  - Test load/save roundtrip
  - Test malformed YAML handling
  - Test sync initialization (empty registry)
  - Test sync preserves existing order
  - Test sync appends new items
  - Test sync prunes orphaned items
  - Test sync with mixed changes
- **Files**: `supekku/scripts/lib/backlog/registry_test.py`
- **Testing**: 9 new tests added (12 total, all passing) ✓
- **Observations**:
  - Uses existing _make_repo() test fixture
  - Tests cover all edge cases: empty, malformed, wrong structure
  - Validates merge algorithm thoroughly
  - Pylint score: 10.00/10 ✓
  - pytest: 12/12 passed in 0.07s ✓

**1.7 - Write integration tests**
- **Design**: `supekku/cli/sync_test.py` - add backlog sync tests
  - End-to-end sync command
  - Verify registry file created
  - Verify correct content
- **Files**: `supekku/cli/sync_test.py`
- **Testing**: `just test`

**1.8 - Run lint and fix issues**
- **Design**: Run both linters, fix all issues
- **Commands**: `just lint`, `just pylint`
- **Testing**: Both must pass with zero warnings

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Registry file conflicts during concurrent edits | Document as single-user limitation; add file locking in future if needed | Accepted |
| YAML parsing errors with malformed registry | Defensive parsing with clear error messages; validate in tests | Mitigated |
| Sync merge logic incorrect (items lost/duplicated) | Comprehensive unit tests covering all merge scenarios | Mitigated |

## 9. Decisions & Outcomes

- **2025-11-04** - Registry schema: Use simple ordered list (`ordering: [IDs...]`) rather than dict with metadata. Simpler and sufficient for Phase 1.
- **2025-11-04** - Sync is manual operation via `sync backlog` command. Auto-sync can be added later based on usage patterns.

## 10. Findings / Research Notes

- Existing registries (`decisions.yaml`, `requirements.yaml`) use different schemas but similar YAML structure
- `discover_backlog_items()` returns items sorted by ID (line 320 of registry.py) - we'll preserve this for new items
- CLI sync commands follow pattern: thin wrapper calling domain function, print summary
- Test pattern: use `tmp_path` fixture for file operations

## 11. Wrap-up Checklist

- [ ] All exit criteria satisfied
- [ ] VT-015-002 tests passing and evidence captured
- [ ] Generated registry file validated manually
- [ ] Lint checks passing (both ruff and pylint)
- [ ] Code committed with clear commit message
- [ ] Phase tracking updated in IP-015
- [ ] Hand-off notes prepared for Phase 2 (priority ordering logic)
