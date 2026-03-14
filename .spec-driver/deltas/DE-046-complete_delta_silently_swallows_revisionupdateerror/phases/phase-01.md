---
id: IP-046.PHASE-01
slug: "046-fix-silent-failure"
name: IP-046 Phase 01 - Fix silent failure and diff-based validation
created: "2026-03-05"
updated: "2026-03-05"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-046.PHASE-01
plan: IP-046
delta: DE-046
objective: >-
  Fix silent RevisionUpdateError handling in complete_delta.py and implement
  diff-based validation in updater.py so targeted updates tolerate pre-existing
  validation issues.
entrance_criteria:
  - DR-046 reviewed
  - Existing tests passing (just check)
exit_criteria:
  - All error paths in complete_delta.py print to stderr
  - update_requirement_lifecycle_status uses diff-based validation
  - VT-046-001/002/003 verified
  - just check green
verification:
  tests:
    - VT-046-001
    - VT-046-002
    - VT-046-003
  evidence: []
tasks:
  - id: "1.1"
    description: Fix silent RevisionUpdateError catch in complete_delta.py
  - id: "1.2"
    description: Audit all error paths in complete_delta.py for missing stderr output
  - id: "1.3"
    description: Implement diff-based validation in updater.py
  - id: "1.4"
    description: Write tests for error output and diff-based validation
risks:
  - description: Diff-based validation too permissive
    mitigation: Only exempt errors present before update; verify with test
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-046.PHASE-01
```

# Phase 1 – Fix silent failure and diff-based validation

## 1. Objective

Eliminate silent failure in `complete delta` and make targeted lifecycle updates
resilient to pre-existing validation issues in revision blocks.

## 2. Links & References

- **Delta**: [DE-046](../DE-046.md)
- **Design Revision**: [DR-046](../DR-046.md)
- **Files**:
  - `supekku/scripts/complete_delta.py` — error handling
  - `supekku/scripts/lib/changes/updater.py` — diff-based validation

## 3. Entrance Criteria

- [x] DR-046 reviewed
- [x] Existing tests passing (18/18 in scope)

## 4. Exit Criteria / Done When

- [x] All `return False` / `return 1` paths in `complete_delta.py` print to stderr
- [x] `update_requirement_lifecycle_status` uses diff-based validation
- [x] VT-046-001: test confirming stderr output on RevisionUpdateError
- [x] VT-046-002: test confirming update succeeds with pre-existing errors
- [x] VT-046-003: existing tests still pass (22/22)
- [x] `just check` green (3 pre-existing failures unrelated to scope)

## 5. Tasks & Progress

| Status | ID  | Description                                                    | Notes                                                                                                                                                          |
| ------ | --- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [x]    | 1.1 | Fix silent `except RevisionUpdateError` in `complete_delta.py` | L307-308: now prints error to stderr                                                                                                                           |
| [x]    | 1.2 | Audit all error paths in `complete_delta.py`                   | Fixed 7 silent paths: delta not found, requirements error, sync failure, revision update error, update failure, frontmatter failure, already-completed handler |
| [x]    | 1.3 | Implement diff-based validation in `updater.py`                | DEC-046-01: validates before+after, only rejects new errors                                                                                                    |
| [x]    | 1.4 | Write tests                                                    | VT-046-001 (stderr output), VT-046-002 (pre-existing errors tolerated), VT-046-003 (22 tests pass)                                                             |

## 6. Assumptions & STOP Conditions

- **Assumption**: Pre-existing errors in revision blocks are common enough to warrant tolerance
- **STOP when**: Change scope expands beyond the two target files
