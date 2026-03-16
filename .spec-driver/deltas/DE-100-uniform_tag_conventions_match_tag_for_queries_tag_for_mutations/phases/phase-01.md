---
id: IP-100.PHASE-01
slug: "100-add-tag-filtering-to-all-list-commands"
name: "Add --tag filtering to all list commands"
created: "2026-03-17"
updated: "2026-03-17"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-100.PHASE-01
plan: IP-100
delta: DE-100
objective: >-
  Add repeatable --tag/-t filtering to all list commands for frontmatter-bearing entities.
  Make existing --tag on ADRs/policies/standards repeatable. Add tags to PlanSummary model.
entrance_criteria:
  - DR-100 approved
exit_criteria:
  - All taggable list commands have --tag/-t (repeatable, OR logic)
  - PlanSummary has tags field populated from frontmatter
  - Existing tests updated for repeatable --tag
  - New tests for all added commands
  - just check green
verification:
  tests:
    - CLI tests for --tag on each added command
    - Repeatable OR logic tests (multiple tags)
    - AND interaction with --status, --filter
  evidence: []
tasks:
  - id: "1.1"
    description: "Add tags to PlanSummary model and populate in discover_plans()"
  - id: "1.2"
    description: "Make --tag repeatable (list[str]) on list adrs/policies/standards"
  - id: "1.3"
    description: "Add --tag to list backlog (+ sub-kind wrappers)"
  - id: "1.4"
    description: "Add --tag to list specs, list requirements"
  - id: "1.5"
    description: "Add --tag to list deltas, list changes, list revisions, list audits, list plans"
  - id: "1.6"
    description: "Tests and verification"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-100.PHASE-01
```

# Phase 1 — Add --tag filtering to all list commands

## 1. Objective

Add repeatable `--tag`/`-t` filtering (OR logic, ANDed with other filters) to all `list` commands for frontmatter-bearing entities. Single phase — the work is mechanical and uniform.

## 2. Links & References

- **Delta**: DE-100
- **Design Revision**: DR-100 (approved)
- **Spec**: PROD-010 – CLI UX

## 3. Entrance Criteria

- [x] DR-100 approved

## 4. Exit Criteria / Done When

- [x] All taggable list commands have `--tag`/`-t` (repeatable, OR logic)
- [x] `PlanSummary` has `tags: list[str]` populated from frontmatter
- [x] Existing tests updated for repeatable `--tag`
- [x] New tests for all added commands (44 tests)
- [x] Lint clean on changed files; pre-existing failures only in full suite

## 5. Tasks & Progress

| Status | ID  | Description | P? | Notes |
|--------|-----|-------------|-----|-------|
| [x] | 1.1 | Add `tags` to `PlanSummary` model; populate in `discover_plans()` | | Done |
| [x] | 1.2 | Make `--tag` repeatable on `list adrs/policies/standards` | | Type → `list[str] \| None`; tag filtering moved inline |
| [x] | 1.3 | Add `--tag` to `list backlog` + thread through `list issues/problems/improvements/risks` | | Done |
| [x] | 1.4 | Add `--tag` to `list specs`, `list requirements` | [P] | Done |
| [x] | 1.5 | Add `--tag` to `list deltas`, `list changes`, `list revisions`, `list audits`, `list plans` | [P] | Done |
| [x] | 1.6 | Tests: repeatable OR, multi-tag, no-match, AND with --status/--filter | | 44 tests, all pass |

### Task Details

#### 1.1 — PlanSummary.tags

- **File**: `supekku/scripts/lib/changes/registry.py`
- **Change**: Add `tags: list[str] = field(default_factory=list)` to `PlanSummary`. In `discover_plans()`, populate from `fm.get("tags", [])`.

#### 1.2 — Make --tag repeatable on ADRs/policies/standards

- **File**: `supekku/cli/list.py` (functions `list_adrs`, `list_policies`, `list_standards`)
- **Change**: `tag` param type `str | None` → `list[str] | None`. Move tag filtering from `registry.filter(tag=...)` to inline: `if tag: items = [i for i in items if any(t in i.tags for t in tag)]`

#### 1.3 — Add --tag to list backlog + sub-kind wrappers

- **File**: `supekku/cli/list.py` (functions `list_backlog`, `list_issues`, `list_problems`, `list_improvements`, `list_risks`)
- **Change**: Add `tag` param. Inline filter. Thread through sub-kind wrapper calls.

#### 1.4 — Add --tag to list specs, list requirements

- **File**: `supekku/cli/list.py` (functions `list_specs`, `list_requirements`)
- **Change**: Add `tag` param. Inline filter.

#### 1.5 — Add --tag to list deltas/changes/revisions/audits/plans

- **File**: `supekku/cli/list.py` (functions `list_deltas`, `list_changes`, `list_revisions`, `list_audits`, `list_plans`)
- **Change**: Add `tag` param. Inline filter. `list_plans` depends on 1.1 (PlanSummary.tags).

#### 1.6 — Tests

- Update existing `--tag` tests for ADRs/policies/standards to cover repeatable OR
- New CLI tests for each added command: single tag, multi-tag OR, no-match, AND with --status

## 6. Assumptions & STOP Conditions

- All taggable models already have `tags: list[str]` except `PlanSummary` — verify before implementing.
- STOP if any model is missing `tags` field — fix model first.

## 7. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] `just check` green
- [ ] Notes updated
