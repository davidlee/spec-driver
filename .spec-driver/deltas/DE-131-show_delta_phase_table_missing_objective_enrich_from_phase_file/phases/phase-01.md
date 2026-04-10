---
id: IP-131-P01
slug: "131-show_delta_phase_table_missing_objective_enrich_from_phase_file-phase-01"
name: IP-131 Phase 01
created: "2026-04-10"
updated: "2026-04-10"
status: in-progress
kind: phase
plan: IP-131
delta: DE-131
---

# Phase 1 — Implementation & verification

## 1. Objective

Implement [DR-131](../DR-131.md): enrich `show delta` phase objectives from on-disk phase files when the plan dict lacks them, and propagate `objective` into `plan.overview` when `create_phase` writes it in frontmatter.

## 2. Links & References

- **Delta**: [DE-131](../DE-131.md)
- **Design revision**: [DR-131](../DR-131.md) (approved; DEC-131-001 — enrichment; DEC-131-002 — plan append; DEC-131-003 — precedence)
- **Specs**: PROD-006.FR-003 (phase summaries with objectives)
- **Code**: `supekku/scripts/lib/formatters/change_formatters.py`, `supekku/scripts/lib/changes/phase_creation.py`

## 3. Entrance Criteria

- [x] IP-131 refined and aligned with DR-131
- [x] Phase created via `spec-driver create phase` (this sheet)
- [x] DR-131 approved; `spec-driver phase start DE-131` run

## 4. Exit Criteria / Done When

- [x] `_enrich_phase_data()` fills `objective` per DR-131 §4 when dict empty (frontmatter, then `phase.overview`)
- [x] `_update_plan_overview_phases()` appends `objective` when non-empty in phase frontmatter dict
- [x] VT-131-\* unit tests in place and passing (`pytest` targeted + full suite via `just quickcheck`)
- [x] VA-131-show-delta recorded in [notes.md](../notes.md)
- [x] `supekku:verification.coverage@v1` on IP-131 updated for completed VT/VA

## 5. Verification

- **Unit**: `TestPhaseObjectiveEnrichmentDE131` in `change_formatters_test.py`; `test_update_plan_overview_phases_appends_objective` in `creation_test.py`
- **Repo**: `just quickcheck` (or `just`) after final lint fix
- **VA-131**: `show delta DE-106` (objectives present); `show delta DE-115` (still “-” without structured objective — expected)

## 6. Assumptions & STOP Conditions

- **Assumptions**: Reuse single `phase_content` read in `_enrich_phase_data`; do not change `artifacts.py` merge rules
- **STOP**: If loader or formatter precedence conflicts with DR-106 / ADR-010 — `/consult` before merging sources in persistence layer

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [x]    | 1.1 | Implement `_enrich_phase_data` objective resolution (FM → `phase.overview`; no clobber) | [ ] | `_resolve_phase_objective_from_file_body` |
| [x]    | 1.2 | Extend `_update_plan_overview_phases` + thread from `create_phase` | [ ] | optional `objective=` |
| [x]    | 1.3 | Add formatter unit tests (VT-131-enrich-\*) | [ ] | |
| [x]    | 1.4 | Add creation/plan-append tests (VT-131-plan-append) | [ ] | |
| [x]    | 1.5 | Run `just quickcheck`; fix lint on touched files | [ ] | |
| [x]    | 1.6 | VA-131-show-delta + update IP coverage / notes | [ ] | |

### Implementation sequence (executed)

1. **`_phase_sequence_digits_from_id`** — Map `IP-*-Pnn` and `*.PHASE-nn` to `phase-nn.md` (fixes hyphen IDs previously resolving to wrong files).
2. **`_resolve_phase_objective_from_file_body`** — `frontmatter.loads` + `PhaseSheet` → `extract_phase_overview`; tolerate corrupt markdown / invalid overview YAML.
3. **`_enrich_phase_data`** — After task stats, set `objective` when dict empty.
4. **`_update_plan_overview_phases`** — `objective=` kw-only; `create_phase` passes trimmed string from `phase_frontmatter`.

### Task details

- **1.1** — **Files**: `change_formatters.py`. Parse via `frontmatter.loads(phase_content)` (same buffer as tracking read).
- **1.2** — **Files**: `phase_creation.py`. Append `{"id", "objective"?}`; duplicate-id early-return behaviour preserved.

## 8. Risks & mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Test fixtures diverge from real delta layout | Patterns from existing formatter/creation tests | closed |
| Bad phase.overview breaks CLI | Catch `ValueError` + broad frontmatter parse guard | closed |

## 9. Decisions & outcomes

- `2026-04-10` — Approved DR-131; implemented display enrichment without changing `load_change_artifact()` merge semantics (DEC-131-001).

## 10. Findings / research notes

- `ShowRelatedFlagTest` required defensive parsing: malformed `phase.overview` in repo deltas raised from `extract_phase_overview` once overview became part of objective resolution.

## 11. Wrap-up checklist

- [x] Exit criteria satisfied (`just quickcheck` green)
- [x] Verification evidence stored (IP coverage + notes)
- [ ] Phase `completed` via `spec-driver phase complete` when user ready to close execution slice
- [ ] Hand-off: `/audit-change` / complete delta when policy satisfied
