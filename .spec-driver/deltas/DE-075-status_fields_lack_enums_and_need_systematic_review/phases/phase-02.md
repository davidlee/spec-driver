---
id: IP-075.PHASE-02
slug: "075-status_fields_lack_enums_and_need_systematic_review-phase-02"
name: "IP-075 Phase 02: theme alignment and backlog migration"
created: "2026-03-09"
updated: "2026-03-21"
status: completed
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
  items on disk to unified status values. Consolidate backlog theme keys
  from per-kind to unified.
entrance_criteria:
  - Phase 1 complete — all constants defined and registered
exit_criteria:
  - theme.py mappings match enums exactly (no phantoms, no gaps)
  - All backlog items on disk use unified status values
  - No legacy per-kind status values remain in frontmatter
  - get_backlog_status_style and callers updated for unified keys
  - All tests passing, linters clean
verification:
  tests: []
  evidence:
    - VA-075-01
    - VA-075-02
tasks:
  - id: "2.1"
    description: "Theme: remove spec.status.live"
  - id: "2.2"
    description: "Theme: add adr.status.superseded"
  - id: "2.3"
    description: "Theme: remove policy.status.active, add policy.status.required"
  - id: "2.4"
    description: "Theme: remove memory.status.deprecated and memory.status.obsolete"
  - id: "2.5"
    description: "Theme: consolidate backlog per-kind keys to backlog.status.*"
  - id: "2.6"
    description: "Theme: update get_backlog_status_style to use backlog.status.{status}"
  - id: "2.7"
    description: "Migrate: captured → open (PROB-004)"
  - id: "2.8"
    description: "Migrate: closed → resolved (ISSUE-036)"
  - id: "2.9"
    description: "Migrate: implemented → resolved (ISSUE-040, ISSUE-025, ISSUE-022, ISSUE-015, IMPR-001 through IMPR-004, IMPR-008, IMPR-009)"
  - id: "2.10"
    description: "Migrate: idea → open (IMPR-005 through IMPR-007, IMPR-010 through IMPR-012)"
  - id: "2.11"
    description: "Verify: on-disk scan confirms no orphaned values (VA-075-02)"
  - id: "2.12"
    description: "Update theme_test.py for new keys"
risks:
  - description: Backlog migration touches many files
    mitigation: Small set (~17 files); enumerated and verified in phase planning
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-075.PHASE-02
```

# Phase 2 — Theme alignment and backlog migration

## 1. Objective

Make theme.py colour mappings match defined enums exactly. Migrate backlog items on disk from legacy per-kind statuses to the unified lifecycle. Consolidate backlog theme keys from `backlog.{kind}.{status}` to `backlog.status.{status}`.

## 2. Links & References

- **Delta**: DE-075
- **Design Revision**: DR-075 — DEC-075-01 through DEC-075-05
- **Phase 1 commit**: `344c9d7`

## 3. Entrance Criteria

- [x] Phase 1 complete — all lifecycle.py files exist, ENUM_REGISTRY populated, tests passing

## 4. Exit Criteria / Done When

- [x] `theme.py` — remove `spec.status.live`, `policy.status.active`, `memory.status.deprecated`, `memory.status.obsolete`
- [x] `theme.py` — add `adr.status.superseded`, `policy.status.required`
- [x] `theme.py` — replace per-kind backlog keys with unified `backlog.status.*`
- [x] `get_backlog_status_style()` simplified to `(status)` → `backlog.status.{status}`
- [x] All backlog items migrated per mapping below
- [x] VA-075-01: theme audit confirms 1:1 alignment with enums
- [x] VA-075-02: on-disk scan confirms no orphaned values
- [x] `just check` passes

## 5. Verification

- VA-075-01: Compare theme keys against enum members
- VA-075-02: `grep -r '^status:' .spec-driver/backlog/` — all values in unified set
- `just test` — no regressions
- `just lint` — clean

## 6. Theme changes summary

### Removals (phantom entries — styled but not in any enum)

- `spec.status.live` (DEC-075-01: archaic synonym of `active`)
- `policy.status.active` (DEC-075-02: replaced by `required`)
- `memory.status.deprecated` (DEC-075-03: use `archived`)
- `memory.status.obsolete` (DEC-075-03: use `archived` or `superseded`)

### Additions (gap entries — in enum but not styled)

- `adr.status.superseded` (DEC-075-04)
- `policy.status.required` (DEC-075-02)

### Backlog consolidation

Replace per-kind keys:

```
backlog.issue.open         → backlog.status.open
backlog.issue.in-progress  → backlog.status.in-progress
backlog.issue.resolved     → backlog.status.resolved
backlog.issue.closed       → (remove — not a valid status)
backlog.problem.captured   → (remove — not a valid status)
backlog.problem.analyzed   → (remove — not a valid status)
backlog.problem.addressed  → (remove — not a valid status)
backlog.improvement.idea   → (remove — not a valid status)
backlog.improvement.planned → (remove — not a valid status)
backlog.improvement.implemented → (remove — not a valid status)
backlog.risk.suspected     → (remove — not a valid status)
backlog.risk.confirmed     → (remove — not a valid status)
backlog.risk.mitigated     → (remove — not a valid status)
```

New unified keys:

```
backlog.status.open         #cc241d  (red — needs attention)
backlog.status.triaged      #00b8ff  (sky blue — assessed)
backlog.status.in-progress  #d79921  (yellow — active)
backlog.status.resolved     #8ec07c  (green — done)
backlog.status.accepted     #7c7876  (mid grey — risk-specific, acknowledged)
backlog.status.expired      #3c3836  (dark grey — risk-specific, stale)
```

### `get_backlog_status_style` change

- Old: `get_backlog_status_style(kind, status)` → `backlog.{kind}.{status}`
- New: `get_backlog_status_style(status)` → `backlog.status.{status}`
- Update caller in `backlog_formatters.py`

## 7. Backlog migration mapping

| Old status    | New status | Items                                                                                                  |
| ------------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| `captured`    | `open`     | PROB-004                                                                                               |
| `closed`      | `resolved` | ISSUE-036                                                                                              |
| `implemented` | `resolved` | ISSUE-040, ISSUE-025, ISSUE-022, ISSUE-015, IMPR-001, IMPR-002, IMPR-003, IMPR-004, IMPR-008, IMPR-009 |
| `idea`        | `open`     | IMPR-005, IMPR-006, IMPR-007, IMPR-010, IMPR-011, IMPR-012                                             |

Items already valid (no change): `open`, `in-progress`, `resolved`

## 8. Tasks & Progress

| Status | ID   | Description                                                  | Notes                                                  |
| ------ | ---- | ------------------------------------------------------------ | ------------------------------------------------------ |
| [x]    | 2.1  | Remove `spec.status.live`                                    | done                                                   |
| [x]    | 2.2  | Add `adr.status.superseded`                                  | dark grey (#3c3836)                                    |
| [x]    | 2.3  | Replace `policy.status.active` with `policy.status.required` | done                                                   |
| [x]    | 2.4  | Remove `memory.status.deprecated`, `memory.status.obsolete`  | done                                                   |
| [x]    | 2.5  | Replace per-kind backlog keys with `backlog.status.*`        | 6 unified keys                                         |
| [x]    | 2.6  | Update `get_backlog_status_style` signature and caller       | (kind, status) → (status)                              |
| [x]    | 2.7  | Migrate PROB-004: `captured` → `open`                        | done                                                   |
| [x]    | 2.8  | Migrate ISSUE-036: `closed` → `resolved`                     | done                                                   |
| [x]    | 2.9  | Migrate 10 items: `implemented` → `resolved`                 | done                                                   |
| [x]    | 2.10 | Migrate 6 items: `idea` → `open`                             | done                                                   |
| [x]    | 2.11 | VA-075-02: on-disk scan                                      | PASS — 60 values, all in {open, in-progress, resolved} |
| [x]    | 2.12 | Update theme_test.py                                         | updated parametrized style names                       |
