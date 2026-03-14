---
id: IP-073.PHASE-03
slug: 073-standardize_show_output_selectors-phase-03
name: "resolve links improvements"
created: "2026-03-09"
updated: "2026-03-09"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-073.PHASE-03
plan: IP-073
delta: DE-073
objective: >-
  Add --verbose, --path, and --id flags to resolve links for scoped
  resolution and missing-target diagnostics.
entrance_criteria:
  - Phase 2 complete and committed
exit_criteria:
  - --verbose reports missing targets with containing file paths
  - --path scopes resolution to a single file
  - --id scopes resolution to a single memory record
  - all flags composable with --dry-run and --link-mode
  - tests pass, lint clean
verification:
  tests:
    - VT-073-03: resolve links --verbose/--path/--id
  evidence: []
tasks:
  - id: 3.1
    description: "Add --verbose flag with missing target + file reporting"
  - id: 3.2
    description: "Add --path flag for single-file scoped resolution"
  - id: 3.3
    description: "Add --id flag (convenience wrapper over --path)"
  - id: 3.4
    description: "Tests for all new flags"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-073.PHASE-03
```

# Phase 3 - Resolve links improvements

## 1. Objective

Add `--verbose`, `--path`, and `--id` flags to `resolve links`.

## 2. Links & References

- **Delta**: DE-073
- **Design Revision**: DR-073 §7
- **Key files**: `supekku/cli/resolve.py`

## 3. Entrance Criteria

- [x] Phase 2 complete and committed (7559102)

## 4. Exit Criteria / Done When

- [x] `resolve links --verbose` reports missing targets with file locations
- [x] `resolve links --path <file>` scopes to a single file
- [x] `resolve links --id <mem-id>` scopes to a single memory record
- [x] All flags composable with `--dry-run` and `--link-mode`
- [x] Tests pass, lint clean

## 7. Tasks & Progress

| Status | ID  | Description                                                   |
| ------ | --- | ------------------------------------------------------------- |
| [x]    | 3.1 | --verbose: track and report missing targets with source files |
| [x]    | 3.2 | --path: scope resolution to a single file                     |
| [x]    | 3.3 | --id: resolve memory ID to path, delegate to --path logic     |
| [x]    | 3.4 | Tests for all new flags                                       |
