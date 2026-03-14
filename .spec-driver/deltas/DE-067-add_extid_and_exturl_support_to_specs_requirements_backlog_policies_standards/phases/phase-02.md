---
id: IP-067.PHASE-02
slug: 067-formatters-and-cli
name: IP-067 Phase 02 - Formatters and CLI
created: "2026-03-08"
updated: "2026-03-08"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-067.PHASE-02
plan: IP-067
delta: DE-067
objective: >-
  Wire ext_id/ext_url into list/show/JSON formatters and add --external
  CLI flag to list commands.
entrance_criteria:
  - PHASE-01 complete
exit_criteria:
  - list --external shows ext_id column for all artifact types
  - show displays ext_id/ext_url when present
  - JSON output includes ext_id/ext_url
  - Tests pass, just check green
verification:
  tests:
    - VT-067-002
  evidence: []
tasks:
  - id: "2.1"
    description: Add ext_id/ext_url to JSON output in all formatters
  - id: "2.2"
    description: Add ext_id/ext_url to detail (show) formatters
  - id: "2.3"
    description: Add show_external param to list table formatters
  - id: "2.4"
    description: Add --external/-e flag to CLI list commands
  - id: "2.5"
    description: Write formatter and CLI tests
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-067.PHASE-02
```

# Phase 2 – Formatters and CLI

## 1. Objective

Wire ext_id/ext_url into all formatter outputs (JSON, detail, list table) and
add `--external`/`-e` flag to CLI list commands.

## 2. Links & References

- **Delta**: DE-067
- **Phase 1**: phases/phase-01.md (models and schema — complete)
- **Specs**: PROD-004, SPEC-116

## 3. Entrance Criteria

- [x] PHASE-01 complete — all models have ext_id/ext_url fields

## 4. Exit Criteria / Done When

- [x] JSON formatters include ext_id/ext_url when present
- [x] Detail (show) formatters display external refs when present
- [x] List table formatters accept `show_external` param
- [x] CLI list commands accept `--external`/`-e` flag
- [x] Tests cover all formatter changes (50 new tests across 6 test files)
- [x] `just check` passes (3335 tests, ruff clean)

## 7. Tasks & Progress

| Status | ID  | Description                                 | Parallel? | Notes                        |
| ------ | --- | ------------------------------------------- | --------- | ---------------------------- |
| [x]    | 2.1 | Add ext_id/ext_url to JSON output           | [P]       | All 6 formatters             |
| [x]    | 2.2 | Add ext_id/ext_url to detail formatters     | [P]       | All 6 show commands          |
| [x]    | 2.3 | Add show_external param to list formatters  |           | Table + TSV column insertion |
| [x]    | 2.4 | Add --external/-e flag to CLI list commands |           | 7 list commands wired        |
| [x]    | 2.5 | Write tests                                 |           | 50 tests across 6 test files |

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (VT-067-002: 50 tests in 6 formatter test files)
- [x] Hand-off notes to close-change
