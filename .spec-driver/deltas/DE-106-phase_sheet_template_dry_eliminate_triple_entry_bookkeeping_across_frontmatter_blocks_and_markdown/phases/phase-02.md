---
id: IP-106-P02
slug: "106-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown-phase-02"
name: "Phase 02 — Template + formatter + remaining compatibility"
created: "2026-03-22"
updated: "2026-03-22"
status: completed
kind: phase
plan: IP-106
delta: DE-106
objective: >-
  Update phase template to remove block scaffolding. Harden compatibility
  in artifacts.py. Update formatter and list_changes fallback paths.
entrance_criteria:
  - Phase 1 complete
  - Pydantic go/no-go decided
exit_criteria:
  - New phases created without phase.overview or phase.tracking blocks
  - Phase template emits frontmatter + markdown body only
  - Formatter task completion stats work via regex fallback
  - list_changes reads canonical frontmatter fields
  - "Validation updated: no warning for block-free new phases"
---

# Phase 02 — Template + formatter + remaining compatibility

## 1. Objective

Remove block scaffolding from new phase creation so phases author structured data once (frontmatter) and execution detail once (markdown body). Verify all downstream consumers remain compatible.

## 2. Links & References

- **Delta**: DE-106
- **Design Revision**: DR-106 §3a (field analysis), §9 (rollout sequencing)
- **Specs**: PROD-006.FR-001, PROD-006.FR-003, PROD-006.FR-004, PROD-006.FR-005
- **Phase 1**: phase-01.md (completed — delivered PhaseSheet model + frontmatter creation + fallback reader)

## 3. Entrance Criteria

- [x] Phase 1 complete (PhaseSheet model, create_phase frontmatter, artifacts.py fallback)
- [x] Pydantic go decision made (37ms import, all legacy phases parse)

## 4. Exit Criteria / Done When

- [x] New phases created without phase.overview or phase.tracking blocks
- [x] Phase template emits frontmatter + markdown body only
- [x] Formatter task completion stats work via regex fallback
- [x] list_changes reads canonical frontmatter fields
- [x] Validation updated: no warning for block-free new phases

## 5. Verification

- `just check` — all tests passing, lint clean
- Manual: `spec-driver create phase --plan IP-106 "test phase"` produces block-free output
- Manual: `spec-driver show delta DE-106` displays both legacy (P01) and new (P02) phases correctly

## 6. Assumptions & STOP Conditions

- Assumptions: regex fallback for task stats in `_enrich_phase_data()` already works — just needs verification
- STOP when: any existing test relying on block content fails in a way that suggests deeper coupling

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| ------ | --- | ----------- | ----- |
| [x]    | 2.1 | Remove block scaffolding from phase template | Removed `{{ phase_overview_block }}` and `{{ phase_tracking_block }}` |
| [x]    | 2.2 | Stop emitting blocks in `create_phase()` | Removed block rendering calls and imports |
| [x]    | 2.3 | Update/fix tests for block removal | 5 tests updated: assertions check frontmatter, not block content |
| [x]    | 2.4 | Verify regex fallback in `_enrich_phase_data()` | 412 formatter tests pass; regex fallback handles new format |
| [x]    | 2.5 | Verify `list_changes` reads frontmatter fields | Delegates to `load_change_artifact()` → `PhaseSheet` (Phase 1) |
| [x]    | 2.6 | Suppress validator warning for new-format phases | Check `plan`+`delta` in frontmatter; 11 phase validator tests pass |
| [x]    | 2.7 | End-to-end verification | 635 relevant tests pass, lint clean |

### Task Details

- **2.1 Remove block scaffolding from phase template**
  - Remove `{{ phase_overview_block }}` and `{{ phase_tracking_block }}` template variables
  - Template should emit frontmatter + markdown body only

- **2.2 Stop emitting blocks in create_phase()**
  - Remove calls to `render_phase_overview_block()` and `render_phase_tracking_block()`
  - Frontmatter population (Phase 1) replaces them

- **2.3 Update tests**
  - `test_create_phase_copies_criteria_from_plan` checks for block content — update expectations
  - Any other tests asserting block presence in newly-created phases

- **2.4 Verify regex fallback**
  - `_enrich_phase_data()` regex fallback handles `[x]`/`[ ]` task stats from markdown
  - Should work unchanged after block removal

- **2.5 Verify list_changes**
  - Confirm it reads `objective`, `entrance_criteria`, `exit_criteria` from frontmatter

- **2.6 Suppress validator warning**
  - For phases with `plan`+`delta` in frontmatter, don't warn about missing `phase.overview` block

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Tests coupled to block content | Update assertions to match new format | open |
| Regex fallback may have edge cases | Test with real phase content | open |

## 9. Decisions & Outcomes

- `2026-03-22` — Block render functions (`render_phase_overview_block`, `render_phase_tracking_block`) kept in `plan.py` for legacy reading; only creation-side removed.
- `2026-03-22` — Validator uses `plan`+`delta` presence as the canonical frontmatter signal (matches `PhaseSheet.has_canonical_fields()`).

## 10. Findings / Research Notes

- `_enrich_phase_data()` regex fallback (`^- \[x\]` / `^- \[(x| )\]`) works for new-format phases out of the box — no changes needed.
- `list_changes` delegates to `load_change_artifact()` which already uses `PhaseSheet` from Phase 1. No direct phase field access in `list.py`.
- The pre-existing `test_finds_all_leaf_packages_in_supekku` failure is unrelated (hardcoded count doesn't match current repo state).
- Phase-02.md itself was created by the old code (before this change) so it has blocks. Future phases will be block-free.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (test counts in task table)
- [x] Notes updated
- [ ] Hand-off notes to Phase 3
