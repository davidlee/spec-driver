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
tasks_completed: 1
tasks_total: 8
last_updated: '2025-11-04'
notes: |
  Task 1.1 complete: Registry YAML schema defined at .spec-driver/registry/backlog.yaml
  Simple ordered list structure chosen for minimal complexity
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
- [ ] Registry file `.spec-driver/registry/backlog.yaml` created with schema
- [ ] `sync backlog` command implemented and working
- [ ] Registry read/write functions tested
- [ ] All tests passing (`just test`)
- [ ] Lint checks passing (`just lint`, `just pylint`)
- [ ] Registry correctly handles: new items (append), deleted items (prune), existing items (preserve order)

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
| [WIP] | 1.2 | Implement registry read function | [ ] | Load + parse YAML |
| [ ] | 1.3 | Implement registry write function | [ ] | Generate + write YAML |
| [ ] | 1.4 | Implement sync logic | [ ] | Discover → merge → write |
| [ ] | 1.5 | Add sync command to CLI | [ ] | Wire to supekku/cli/sync.py |
| [ ] | 1.6 | Write unit tests | [P] | Can parallel with 1.5 |
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

**1.2 - Implement registry read function**
- **Design**: `load_backlog_registry(root: Path) -> list[str]`
  - Return list of IDs in order
  - Return empty list if file doesn't exist
  - Raise error if YAML is invalid
- **Files**: `supekku/scripts/lib/backlog/registry.py`
- **Testing**: Unit tests with temp files
- **Observations**: Handle missing file gracefully

**1.3 - Implement registry write function**
- **Design**: `save_backlog_registry(root: Path, ordering: list[str])`
  - Write ordered list to YAML
  - Create parent directories if needed
  - Atomic write (temp file + rename)
- **Files**: `supekku/scripts/lib/backlog/registry.py`
- **Testing**: Unit tests verify file contents

**1.4 - Implement sync logic**
- **Design**: `sync_backlog_registry(root: Path)`
  - Call `discover_backlog_items()` to get all items
  - Load existing registry (if exists)
  - Merge: preserve order for existing items, append new items
  - Prune: remove IDs not in discovered items
  - Save updated registry
- **Files**: `supekku/scripts/lib/backlog/registry.py`
- **Testing**: Unit tests with various scenarios
- **Observations**: Merge logic is key - test thoroughly

**1.5 - Add sync command to CLI**
- **Design**: Add `sync_backlog()` command to `supekku/cli/sync.py`
  - Follow existing pattern from `sync_decisions()`
  - Call `sync_backlog_registry()`
  - Print summary of changes
- **Files**: `supekku/cli/sync.py`
- **Testing**: Integration test
- **Observations**: Keep CLI thin - delegate to domain

**1.6 - Write unit tests**
- **Design**: `supekku/scripts/lib/backlog/registry_test.py`
  - Test read/write functions
  - Test sync merge logic
  - Test orphan pruning
  - Test edge cases (empty, missing file, corrupt YAML)
- **Files**: `supekku/scripts/lib/backlog/registry_test.py`
- **Testing**: `just test`
- **Parallel**: Yes, can write tests while implementing CLI

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
