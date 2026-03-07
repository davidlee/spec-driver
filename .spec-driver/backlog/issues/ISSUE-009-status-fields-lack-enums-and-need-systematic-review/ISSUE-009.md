---
id: ISSUE-009
name: Status fields lack enums and need systematic review
created: '2025-11-02'
updated: '2026-03-07'
status: in-progress
kind: issue
categories:
  - architecture
  - data-model
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

## Current State

**Observed in DE-005 work**:
- Specs: Uses `"draft"`, `"stub"`, `"active"`, `"deprecated"`, `"archived"` (found in theme.py)
- ADRs: Uses `"accepted"`, `"rejected"`, `"deprecated"`, `"revision-required"`, `"proposed"`, `"draft"` (found in theme.py)
- Changes: Uses `"completed"`, `"complete"`, `"in-progress"`, `"pending"`, `"draft"`, `"deferred"` (found in theme.py)
- Requirements: Uses `"live"`, `"in-progress"`, `"pending"`, `"retired"` (found in theme.py)

**No enums found in**:
- `supekku/scripts/lib/core/frontmatter_schema.py` - status defined as `str` (line 33)
- Data models (specs, ADRs, changes, etc.)
- Validation logic

**Theming as documentation**:
Currently `supekku/scripts/lib/formatters/theme.py` serves as the de facto documentation of valid status values through its color mappings, which is backwards.

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

## Scope

Needs systematic review and design for:
- Specs (product & tech)
- ADRs/Decisions
- Deltas
- Revisions
- Audits
- Requirements
- Backlog items (issues, problems, improvements, risks)

## Acceptance Criteria

- [ ] Enum definitions exist for all entity status fields
- [ ] Frontmatter schema validation enforces enum constraints
- [ ] Data models use enum types
- [ ] Theme.py references enums (not hardcoded strings)
- [ ] Migration strategy for existing documents
- [ ] Documentation of status semantics and lifecycle

## Audit (2026-03-07)

### Backlog item statuses: schema vs theme vs reality

Frontmatter schemas (`spec-driver schema show frontmatter.{issue,problem,risk}`)
define `status` as free-form string (`"pattern": ".+"`). No enums.

**Theme styles** (`theme.py:68-84`) define colours for these statuses:

| Kind | Styled statuses |
|------|----------------|
| issue | `open`, `in-progress`, `resolved`, `closed` |
| problem | `captured`, `analyzed` |
| improvement | `idea`, `planned`, `implemented` |
| risk | `suspected` (no style!), `confirmed`, `mitigated` |

**Actually in use** (from backlog items on disk):

| Kind | Statuses in use |
|------|----------------|
| issue | `open`, `in-progress`, `done`, `resolved`, `implemented` |
| problem | `captured` |
| improvement | `idea`, `in-progress` |
| risk | `mitigated` |

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

## Partial Resolution — DE-057 (backlog item statuses only)

DE-057 delivered per-kind status frozensets in `backlog/models.py` (DEC-057-02,
DEC-057-08):
- `ISSUE_STATUSES`, `PROBLEM_STATUSES`, `IMPROVEMENT_STATUSES`, `RISK_STATUSES`
- `BACKLOG_STATUSES` dict for lookup by kind
- `DEFAULT_HIDDEN_STATUSES` for list view exclusion
- `ALL_VALID_STATUSES` union set
- `is_valid_status()` helper with permissive validation (warn on unknown)

**Remaining for full closure:**
- Theme/rendering alignment: `theme.py` status colours don't match the defined
  enums (gaps listed in audit section above)
- Non-backlog entity types (specs, ADRs, deltas, requirements, etc.) still lack
  status enums
- Frontmatter schema validation not yet enforcing enum constraints
- Status: `in-progress` — backlog modelling done, broader scope remains
