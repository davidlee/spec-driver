---
id: IP-075.PHASE-02
slug: 075-status_fields_lack_enums_and_need_systematic_review-phase-02
name: 'IP-075 Phase 02: theme alignment and backlog migration'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-075.PHASE-02
plan: IP-075
delta: DE-075
objective: >-
  Align theme.py colour mappings 1:1 with defined enums. Migrate backlog
  items on disk to unified status values.
entrance_criteria:
  - Phase 1 complete — all constants defined and registered
exit_criteria:
  - theme.py mappings match enums exactly (no phantoms, no gaps)
  - All backlog items on disk use unified status values
  - No legacy per-kind status values remain in frontmatter
  - All tests passing, linters clean
verification:
  tests: []
  evidence:
    - VA-075-01
    - VA-075-02
tasks:
  - id: '2.1'
    description: Audit and update theme.py — specs section
  - id: '2.2'
    description: Audit and update theme.py — ADR section
  - id: '2.3'
    description: Audit and update theme.py — policies section
  - id: '2.4'
    description: Audit and update theme.py — memories section
  - id: '2.5'
    description: Audit and update theme.py — backlog sections (consolidate)
  - id: '2.6'
    description: Migrate backlog item frontmatter to unified statuses
  - id: '2.7'
    description: Verify no orphaned status values on disk
risks:
  - description: Backlog migration touches many files
    mitigation: Small set; manual review each change
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-075.PHASE-02
```

# Phase 2 — Theme alignment and backlog migration

## 1. Objective

Make theme.py colour mappings match defined enums exactly. Migrate backlog items on disk from legacy per-kind statuses to the unified lifecycle.

## 2. Links & References

- **Delta**: DE-075
- **Design Revision**: DR-075 — DEC-075-01 (drop `live`), DEC-075-02 (add `superseded`), DEC-075-03 (drop policy `active`), DEC-075-04 (trim memory tail), DEC-075-05 (unified backlog)

## 3. Entrance Criteria

- [ ] Phase 1 complete — all lifecycle.py files exist, ENUM_REGISTRY populated, tests passing

## 4. Exit Criteria / Done When

- [ ] `theme.py` — remove `spec.status.live`, `policy.status.active`, `memory.status.deprecated`, `memory.status.obsolete`
- [ ] `theme.py` — add `adr.status.superseded`, `policy.status.required`
- [ ] `theme.py` — consolidate backlog status colours to unified set
- [ ] Backlog items migrated: `captured` → `open`, `idea` → `open`, `done`/`implemented`/`verified` → `resolved`, etc.
- [ ] VA-075-01: theme audit confirms 1:1 alignment
- [ ] VA-075-02: on-disk scan confirms no orphaned values
- [ ] `just check` passes

## 5. Verification

- VA-075-01: Compare theme keys against enum members programmatically or by inspection
- VA-075-02: `grep -r '^status:' .spec-driver/backlog/` and confirm all values in unified set
- `just test` — no regressions
- `just lint` — clean

## 6. Assumptions & STOP Conditions

- Assumes phase 1 constants are stable
- STOP if: migration reveals items with status values not anticipated by DR-075

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [ ] | 2.1 | Update theme.py — spec statuses | [P] | Remove `live` |
| [ ] | 2.2 | Update theme.py — ADR statuses | [P] | Add `superseded` |
| [ ] | 2.3 | Update theme.py — policy statuses | [P] | Remove `active`, add `required` |
| [ ] | 2.4 | Update theme.py — memory statuses | [P] | Remove `deprecated`, `obsolete` |
| [ ] | 2.5 | Update theme.py — backlog statuses | [ ] | Consolidate per-kind → unified |
| [ ] | 2.6 | Migrate backlog frontmatter | [ ] | Manual; per DEC-075-05 mapping |
| [ ] | 2.7 | Verify on-disk scan | [ ] | VA-075-02 |
