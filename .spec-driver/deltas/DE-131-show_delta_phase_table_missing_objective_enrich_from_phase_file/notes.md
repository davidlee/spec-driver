# Notes for DE-131

## 2026-04-10 — Execution

- **DR-131** approved; **DE-131** → `in-progress`; **`spec-driver phase start DE-131`**.
- **Implementation**: `_enrich_phase_data` + `_resolve_phase_objective_from_file_body`; `_update_plan_overview_phases(..., objective=...)` from `create_phase`; `_phase_sequence_digits_from_id` for `IP-*-Pnn` → `phase-nn.md`.
- **Resilience**: Invalid frontmatter / `phase.overview` YAML must not break `show delta` (regression fixed after `ShowRelatedFlagTest`).

### VA-131-show-delta

- `uv run spec-driver show delta DE-106` — Objective column populated from phase content (multi-line objectives wrap in table).
- `uv run spec-driver show delta DE-115` — Objective remains `-` for listed phases where structured objective is not present in phase files (expected; no § heading parse in scope).
