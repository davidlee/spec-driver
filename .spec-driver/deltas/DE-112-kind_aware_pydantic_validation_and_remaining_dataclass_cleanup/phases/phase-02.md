---
id: IP-112-P02
slug: "112-kind_aware_pydantic_validation-phase-02"
name: "Phase 02 — Wire kind-aware validation into validator"
created: "2026-03-22"
updated: "2026-03-22"
status: completed
kind: phase
plan: IP-112
delta: DE-112
objective: >-
  Add _validate_memory_frontmatter, _validate_backlog_frontmatter,
  _validate_drift_frontmatter methods to WorkspaceValidator. Wire into
  validate() with top-level traversal methods.
entrance_criteria:
  - Phase 1 complete
exit_criteria:
  - Three new validation methods on WorkspaceValidator
  - Three new traversal methods called from validate()
  - spec-driver validate catches malformed memory/backlog/drift frontmatter
  - New tests for kind-aware validation
  - Existing validator tests pass
  - Lint clean
---

# Phase 02 — Wire kind-aware validation into validator

## Tasks

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 2.1 | Add _validate_memory_frontmatter + _validate_memory_files | Glob mem.*.md, construct MemoryRecord(**fm) |
| [x]    | 2.2 | Add _validate_backlog_frontmatter + _validate_backlog_files | Glob per-kind subdirectory (issues/problems/improvements/risks) |
| [x]    | 2.3 | Add _validate_drift_frontmatter + _validate_drift_files | Glob DL-*.md |
| [x]    | 2.4 | Wire traversal methods into validate() | After phase status checks |
| [x]    | 2.5 | Add tests for kind-aware validation | 7 tests: valid/malformed for each kind + missing-dirs |
| [x]    | 2.6 | Run full validator tests and lint | 4521 passed, lint clean |

### Design notes

- Each `_validate_*_frontmatter(fm, artifact)` method is a focused unit — callable from batch traversal now, extractable to shared helper later for per-invocation hooks
- Use `ValidationError` from pydantic, catch and emit as warning (permissive, consistent with PhaseSheet pattern)
- Import models at function scope or module scope — module scope is fine since validator already imports PhaseSheet
