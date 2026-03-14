---
id: ISSUE-009
name: Status fields lack enums and need systematic review
created: "2025-11-02"
updated: "2026-03-08"
status: resolved
kind: issue
categories: [architecture, data-model]
severity: p2
impact: maintainability
---

# Status fields lack enums and need systematic review

## Problem

Status fields across core entities (specs, ADRs, deltas, requirements, etc.) are defined as free-form strings without enum constraints. This creates several issues:

1. **No validation**: Any string value can be assigned to status fields
2. **Inconsistency**: Different parts of the codebase may use different status values
3. **Discovery difficulty**: No single source of truth for valid status values
4. **Type safety**: No IDE autocomplete or compile-time checking
5. **Migration risk**: Status value changes require error-prone find/replace

## Current State (updated 2026-03-09)

**All entity types now have domain-level status enums:**

| Entity type               | Enum location                                                         | Source                    |
| ------------------------- | --------------------------------------------------------------------- | ------------------------- |
| Deltas, revisions, audits | `changes/lifecycle.py` → `VALID_STATUSES`                             | Pre-existing              |
| Requirements              | `requirements/lifecycle.py` → `VALID_STATUSES`                        | Pre-existing              |
| Backlog (all kinds)       | `backlog/models.py` → `BACKLOG_BASE_STATUSES` + `RISK_EXTRA_STATUSES` | DE-057 → DE-075 (unified) |
| Specs                     | `specs/lifecycle.py` → `SPEC_STATUSES`                                | DE-075                    |
| ADRs/Decisions            | `decisions/lifecycle.py` → `ADR_STATUSES`                             | DE-075                    |
| Policies                  | `policies/lifecycle.py` → `POLICY_STATUSES`                           | DE-075                    |
| Standards                 | `standards/lifecycle.py` → `STANDARD_STATUSES`                        | DE-075                    |
| Memories                  | `memory/lifecycle.py` → `MEMORY_STATUSES`                             | DE-075                    |

All exposed via `ENUM_REGISTRY` in `core/enums.py`. Theme 1:1 aligned with enums (VA-075-01).

**Frontmatter schema**: still defines `status` as `"pattern": ".+"` — schema-level enum enforcement is a separate delta.

**Backlog migration**: complete — all items use unified statuses (VA-075-02).

## Impact

**Recent example (DE-005)**:

- Changed sync to use `status: "stub"` instead of `status: "draft"`
- Had to manually verify theme.py had a color for "stub"
- Could have accidentally introduced an orphaned status value
- No validation would have caught the error

**Systemic issues**:

- Developers must guess valid status values
- Status value changes require coordinated updates across multiple files
- Theme definitions can diverge from actual usage
- New status values may lack theme colors

## Desired State

1. **Enum definitions**: Central enum definitions for each entity type's status
2. **Validation**: Frontmatter validation enforces enum constraints
3. **Type safety**: Models use enum types, not strings
4. **Documentation**: Enums serve as authoritative documentation
5. **Theme derivation**: Theme definitions derived from enums (not the reverse)

## Remaining Scope

All enum definitions are complete. Remaining work (separate deltas):

- Frontmatter schema enforcement (replace `".+"` patterns with enum constraints)
- Python `Enum` type migration (frozensets → enums)
- Status lifecycle documentation / semantics (PROD-009)

## Acceptance Criteria

- [x] Enum definitions exist for changes, requirements, backlog items
- [x] Enum definitions exist for specs, ADRs, policies, standards, memories (DE-075 phase 1)
- [ ] Frontmatter schema validation enforces enum constraints (separate delta)
- [x] Data models use enum types (frozensets — Python Enum migration deferred)
- [x] Theme.py references enums (DE-075 phase 2 — 1:1 alignment verified)
- [x] Migration strategy for existing documents (DE-075 phase 2 — 17 backlog items migrated)
- [x] Documentation of status semantics and lifecycle (mem.fact.spec-driver.status-enums)

## Audit (2026-03-07)

### Backlog item statuses: schema vs theme vs reality

Frontmatter schemas (`spec-driver schema show frontmatter.{issue,problem,risk}`)
define `status` as free-form string (`"pattern": ".+"`). No enums.

**Theme styles** (`theme.py:68-84`) define colours for these statuses:

| Kind        | Styled statuses                                   |
| ----------- | ------------------------------------------------- |
| issue       | `open`, `in-progress`, `resolved`, `closed`       |
| problem     | `captured`, `analyzed`                            |
| improvement | `idea`, `planned`, `implemented`                  |
| risk        | `suspected` (no style!), `confirmed`, `mitigated` |

**Actually in use** (from backlog items on disk):

| Kind        | Statuses in use                                          |
| ----------- | -------------------------------------------------------- |
| issue       | `open`, `in-progress`, `done`, `resolved`, `implemented` |
| problem     | `captured`                                               |
| improvement | `idea`, `in-progress`                                    |
| risk        | `mitigated`                                              |

**Gaps found**:

- `done` and `implemented` used on issues but not styled
- `in-progress` used on improvements but not styled (only `planned` is)
- `suspected` is the risk default but has no theme style
- `closed` and `analyzed` are styled but never used
- Schema examples hint at statuses (`triaged`, `validated`) that are neither
  styled nor used

### Downstream impact

IMPR-010 proposes that `list backlog -p` checkboxes should reflect item status.
Without defined enums, the checkbox mapping (which statuses are "done"?) is
a design choice with no canonical answer.

## Related

- Discovered during: DE-005 (implement spec backfill)
- Related to: PROD-001 (spec creation), frontmatter validation architecture
- Downstream: IMPR-010 (backlog prioritize UX — status-aware checkboxes)

## Resolution History

**DE-057** — per-kind backlog status frozensets (now superseded by unified set)

**DE-075** — comprehensive enum coverage:

- Phase 1: defined lifecycle constants for specs, ADRs, policies, standards, memories; unified backlog statuses; registered all in ENUM_REGISTRY
- Phase 2: aligned theme.py 1:1 with enums; migrated 17 backlog items to unified statuses
- Phase 3: updated memory, ISSUE-009 acceptance criteria

**Remaining (separate deltas):** frontmatter schema enforcement, Python Enum types
