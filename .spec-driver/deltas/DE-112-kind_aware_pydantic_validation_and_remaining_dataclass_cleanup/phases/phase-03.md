---
id: IP-112-P03
slug: "112-kind_aware_pydantic_validation-phase-03"
name: "Phase 03 — Fix historical validation noise"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-112
delta: DE-112
objective: >-
  Fix AUD-012 disposition vocabulary, legacy phase frontmatter gaps,
  and IP-109 status format. Reduce validate output to real issues only.
entrance_criteria:
  - Phase 2 complete (new validation wired in, so we can verify cleanup)
exit_criteria:
  - AUD-012 findings use 'reconciled' instead of 'resolved' for aligned dispositions
  - Legacy phase files have kind and status in frontmatter
  - IP-109 phase status uses canonical format
  - spec-driver validate error count drops to 0
  - spec-driver validate warning count drops significantly (legacy audit-gate warnings remain)
  - Lint clean (for any touched .py files)
---

# Phase 03 — Fix historical validation noise

## Tasks

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [ ]    | 3.1 | Fix AUD-012: status 'resolved' → 'reconciled' for aligned findings | 11 findings in YAML blocks |
| [ ]    | 3.2 | Fix legacy phase files: add missing kind/status frontmatter | DE-002, DE-004, DE-028, DE-031, DE-051 |
| [ ]    | 3.3 | Fix IP-109 phase status: 'in_progress' → 'in-progress' | Or use spec-driver validate --fix |
| [ ]    | 3.4 | Run spec-driver validate, confirm noise reduction | |

### Inventory

**AUD-012** (11 errors):
- F-001 through F-011: `disposition.status: resolved` should be `reconciled` for `kind: aligned`

**Legacy phases** (~12 files, 5 deltas):
- DE-002: phase-01, phase-02, phase-03 — missing status and kind
- DE-004: phase-05-*, phase-06-* — missing status and kind
- DE-028: phase-01 — has status but missing kind
- DE-031: phase-01 — missing status and kind
- DE-051: phase-01 — has status but missing kind

**IP-109**: phase-01, phase-02 — `in_progress` → `in-progress`
