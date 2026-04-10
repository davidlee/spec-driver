---
id: IP-131-P01
slug: "131-show_delta_phase_table_missing_objective_enrich_from_phase_file-phase-01"
name: IP-131 Phase 01
created: "2026-04-10"
updated: "2026-04-10"
status: draft
kind: phase
plan: IP-131
delta: DE-131
---

# Phase 1 — Implementation & verification

## 1. Objective

Implement [DR-131](../DR-131.md): enrich `show delta` phase objectives from on-disk phase files when the plan dict lacks them, and propagate `objective` into `plan.overview` when `create_phase` writes it in frontmatter.

## 2. Links & References

- **Delta**: [DE-131](../DE-131.md)
- **Design revision**: [DR-131](../DR-131.md) (DEC-131-001 — enrichment; DEC-131-002 — plan append; DEC-131-003 — precedence)
- **Specs**: PROD-006.FR-003 (phase summaries with objectives)
- **Code**: `supekku/scripts/lib/formatters/change_formatters.py`, `supekku/scripts/lib/changes/phase_creation.py`

## 3. Entrance Criteria

- [x] IP-131 refined and aligned with DR-131
- [x] Phase created via `spec-driver create phase` (this sheet)
- [ ] DR-131 approved or consciously executed under draft (project policy)

## 4. Exit Criteria / Done When

- [ ] `_enrich_phase_data()` fills `objective` per DR-131 §4 when dict empty (frontmatter, then `phase.overview`)
- [ ] `_update_plan_overview_phases()` appends `objective` when non-empty in phase frontmatter dict
- [ ] VT-131-\* unit tests in place and passing (`just test` / `just`)
- [ ] VA-131-show-delta recorded (e.g. `show delta` on a delta with phase objectives)
- [ ] `supekku:verification.coverage@v1` on IP-131 updated for completed VT/VA where applicable

## 5. Verification

- **Unit**: `change_formatters_test` — enrichment from frontmatter, from `phase.overview`, no-clobber when dict has objective
- **Unit**: `creation_test` (or focused test) — plan.overview row includes objective when passed through `create_phase` / `_update_plan_overview_phases`
- **Repo**: `just` (lint + tests) green
- **VA-131-show-delta**: `uv run spec-driver show delta DE-115` (or another delta with structured phase objectives); paste brief result into [notes.md](../notes.md)

## 6. Assumptions & STOP Conditions

- **Assumptions**: Reuse single `phase_content` read in `_enrich_phase_data`; do not change `artifacts.py` merge rules
- **STOP**: If loader or formatter precedence conflicts with DR-106 / ADR-010 — `/consult` before merging sources in persistence layer

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ]    | 1.1 | Implement `_enrich_phase_data` objective resolution (FM → `phase.overview`; no clobber) | [ ] | DR-131 §4 |
| [ ]    | 1.2 | Extend `_update_plan_overview_phases` + thread from `create_phase` | [ ] | DR-131 §4 |
| [ ]    | 1.3 | Add formatter unit tests (VT-131-enrich-\*) | [ ] | Temp dirs + `ChangeArtifact` |
| [ ]    | 1.4 | Add creation/plan-append tests (VT-131-plan-append) | [ ] | |
| [ ]    | 1.5 | Run `just`; fix lint on touched files | [ ] | |
| [ ]    | 1.6 | VA-131-show-delta + update IP coverage / notes | [ ] | |

### Task details

- **1.1** — **Files**: `change_formatters.py`. Parse frontmatter with existing helpers (`load_markdown_file` split or `PhaseSheet`); `extract_phase_overview` for fallback. Only when stripped dict objective is empty.
- **1.2** — **Files**: `phase_creation.py`. Append `objective` key to new plan row when `phase_frontmatter` has non-empty string; keep duplicate-detection behaviour unchanged unless trivial fix is required.
- **1.3 / 1.4** — Mirror scenarios in DR-131 §5 and §11 adversarial notes (single read, first line in table).

## 8. Risks & mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Test fixtures diverge from real delta layout | Clone patterns from `change_formatters_test` / `creation_test` | open |

## 9. Decisions & outcomes

- _(Record implementation decisions during `/execute-phase`.)_

## 10. Findings / research notes

- _(Spelunking notes during execution.)_

## 11. Wrap-up checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP verification.coverage + notes updated
- [ ] Hand-off: close delta or follow-up if scope creeps
