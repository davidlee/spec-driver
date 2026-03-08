---
id: IP-067.PHASE-02
slug: 067-formatters-and-cli
name: IP-067 Phase 02 - Formatters and CLI
created: '2026-03-08'
updated: '2026-03-08'
status: in-progress
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

- [ ] JSON formatters include ext_id/ext_url when present
- [ ] Detail (show) formatters display external refs when present
- [ ] List table formatters accept `show_external` param
- [ ] CLI list commands accept `--external`/`-e` flag
- [ ] Tests cover all formatter changes
- [ ] `just check` passes

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Add ext_id/ext_url to JSON output | [P] | All formatters |
| [ ] | 2.2 | Add ext_id/ext_url to detail formatters | [P] | show commands |
| [ ] | 2.3 | Add show_external param to list formatters | | Table column insertion |
| [ ] | 2.4 | Add --external/-e flag to CLI list commands | | After 2.3 |
| [ ] | 2.5 | Write tests | | After 2.1-2.4 |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to close-change
