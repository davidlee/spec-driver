---
id: IP-089.PHASE-01
slug: 089-no_separate_install_requirements_for_tui-phase-01
name: IP-089 Phase 01
created: '2026-03-10'
updated: '2026-03-10'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-089.PHASE-01
plan: IP-089
delta: DE-089
objective: >-
  Merge TUI dependencies into main install and remove conditional import gates.
entrance_criteria:
  - DE-089 accepted
exit_criteria:
  - TUI deps in [project.dependencies]
  - tui extras group removed or aliased
  - conditional imports cleaned up
  - uv lock refreshed
  - lints pass
  - TUI commands work without extras
verification:
  tests: []
  evidence:
    - VA-089-01
tasks:
  - id: '1.1'
    description: Move TUI deps from optional-dependencies to dependencies
  - id: '1.2'
    description: Remove or alias tui extras group
  - id: '1.3'
    description: Remove conditional/guarded TUI imports
  - id: '1.4'
    description: Refresh uv.lock and verify install
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-089.PHASE-01
```

# Phase 01 — Merge TUI deps and clean up

## 1. Objective
Move TUI dependencies from optional extras into the main dependency list. Remove conditional import guards. Verify clean install.

## 2. Links & References
- **Delta**: DE-089
- **Issue**: ISSUE-049

## 3. Entrance Criteria
- [x] DE-089 scoped

## 4. Exit Criteria / Done When
- [x] TUI deps moved to `[project.dependencies]`
- [x] `tui` extras group removed
- [x] Conditional TUI imports cleaned up
- [x] `uv lock` refreshed
- [x] Lints pass (ruff zero warnings)
- [x] TUI commands work from default install

## 5. Verification
- VA: Confirm `uv run spec-driver` TUI commands work without `[tui]` extras

## 7. Tasks & Progress

| Status | ID | Description |
| --- | --- | --- |
| [x] | 1.1 | Move TUI deps from `optional-dependencies.tui` to `dependencies` |
| [x] | 1.2 | Remove `tui` extras group and dev self-ref |
| [x] | 1.3 | Remove conditional/guarded TUI imports (main.py, app.py, event_listener.py) |
| [x] | 1.4 | Refresh `uv.lock`, verify install, lint, 3814 tests pass |
