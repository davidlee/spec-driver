---
id: IP-106-P01
slug: "106-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown-phase-01"
name: Phase 01 — Pydantic spike + creation/reader vertical slice
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-106-P01
plan: IP-106
delta: DE-106
objective: >-
  Define PhaseSheet Pydantic model for canonical phase frontmatter fields. Wire
  minimal create_phase() → artifacts.py round-trip to validate the model against
  real code paths. Go/no-go gates remaining phases.
entrance_criteria:
  - DR-106 approved
  - Existing phase creation and display tests passing
exit_criteria:
  - PhaseSheet Pydantic model defined and tested (or fallback decision made)
  - create_phase() emits plan/delta/objective/criteria in frontmatter
  - artifacts.py reads phase data from frontmatter with block fallback
  - show delta displays new-format phases correctly
  - Legacy block-based phases still display without errors
  - Go/no-go on Pydantic documented in DR-107/notes
```

# Phase 01 — Pydantic spike + creation/reader vertical slice

## 1. Objective

Define a `PhaseSheet` Pydantic model for the canonical phase frontmatter fields (`plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`). Wire a minimal creation→load round-trip: `create_phase()` emits these fields in frontmatter, `artifacts.py` reads them back for `show delta`. This proves the Pydantic model against real code paths and produces a go/no-go for DE-107.

## 2. Links & References

- **Delta**: [DE-106](../DE-106.md)
- **Design Revision**: [DR-106](../DR-106.md) — §3a (field analysis), §9 (phase sequencing), DEC-005/DEC-008
- **Specs**: PROD-006.FR-001, PROD-006.FR-003, PROD-006.FR-004
- **Related**: DE-107 (Pydantic spike), IMPR-022

## 3. Entrance Criteria

- [x] DR-106 approved (3 review passes, 14 findings integrated)
- [ ] Existing phase creation and display tests passing

## 4. Exit Criteria / Done When

- [ ] `PhaseSheet` Pydantic model defined with `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`
- [ ] `create_phase()` emits canonical fields in frontmatter (sources from plan entry or defaults)
- [ ] `artifacts.py` reads phase data from frontmatter first, falls back to `phase.overview` block
- [ ] `show delta` displays new-format phases correctly (phase ID, status, objective)
- [ ] Legacy block-based phases still display without errors (compatibility)
- [ ] Go/no-go on Pydantic documented
- [ ] All tests passing, lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/changes/creation_test.py -x` — phase creation
- `uv run pytest supekku/scripts/lib/changes/artifacts_test.py -x` — artifact loading
- `uv run pytest supekku/scripts/lib/formatters/change_formatters_test.py -x` — display
- `uv run spec-driver show delta DE-104` — real-world legacy compatibility check
- `uv run spec-driver show delta DE-106` — new-format display check
- Pydantic spike: import time measurement, YAML date round-trip test

## 6. Assumptions & STOP Conditions

- Assumes Pydantic can be added as a dependency without unacceptable import time cost
- Assumes `python-frontmatter` YAML output round-trips cleanly with Pydantic model serialization
- STOP if: Pydantic import adds >200ms to CLI cold start — fall back to inline validation
- STOP if: YAML date handling mismatch breaks round-trip fidelity — investigate before proceeding

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | 1.1 | Add pydantic dependency | pyproject.toml |
| [ ] | 1.2 | Define `PhaseSheet` Pydantic model | New file. Fields: plan, delta, objective, entrance_criteria, exit_criteria. Validate against existing `PLAN_FRONTMATTER_METADATA` field semantics. |
| [ ] | 1.3 | Test model against real phase corpus | Parse existing `.spec-driver/deltas/*/phases/*.md` frontmatter through the model. Verify legacy phases pass (fields optional). |
| [ ] | 1.4 | Measure import time impact | Compare CLI cold start before/after pydantic import. Document in notes. |
| [ ] | 1.5 | Go/no-go decision | If negative: fall back to inline dict validation (~30 lines). Document rationale. |
| [ ] | 1.6 | Update `create_phase()` to emit frontmatter fields | Add `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria` to phase frontmatter dict. Source from `_extract_phase_metadata_from_plan()` or defaults. Still emit legacy blocks for now (removed in Phase 2). |
| [ ] | 1.7 | Update `artifacts.py` to prefer frontmatter | In phase loading (~line 175): check frontmatter for `plan`+`delta`; if present, build phase entry from frontmatter. If absent, fall back to `extract_phase_overview()`. Never merge. |
| [ ] | 1.8 | Update/add tests | Creation test: verify frontmatter contains canonical fields. Artifacts test: verify frontmatter-first loading. Compatibility test: verify legacy phases still load via block fallback. |
| [ ] | 1.9 | Verify `show delta` end-to-end | Run against DE-104 (legacy) and DE-106 (new format after 1.6). Both must display correctly. |

### Task Details

- **1.2 PhaseSheet model**
  - Location: `supekku/scripts/lib/changes/models.py` (new) or `supekku/scripts/lib/core/frontmatter_metadata/plan.py` (extend)
  - Must handle: optional fields (legacy phases have no plan/delta in frontmatter), date coercion (PyYAML auto-parses dates), list-of-strings for criteria
  - Consider: `model_config = ConfigDict(extra='ignore')` for forward compatibility

- **1.6 create_phase() changes**
  - Current flow: `_extract_phase_metadata_from_plan()` → `render_phase_overview_block()` + `render_phase_tracking_block()` → template
  - New flow: same extraction → populate frontmatter dict → still render blocks (Phase 2 removes them)
  - Empty plan case: extraction returns `{}` → omit optional fields or emit empty lists

- **1.7 artifacts.py changes**
  - Current: `extract_phase_overview(content)` → `phase_block.data.copy()` → `phases_data.append()`
  - New: check `frontmatter.get("plan")` and `frontmatter.get("delta")`; if both present, build phase entry from frontmatter fields directly. Skip `extract_phase_overview()`. If absent, fall back to current block extraction.
  - Must read frontmatter from phase file — currently only reads block content

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Pydantic import time too high | Measure in 1.4; fallback to inline validation | Open |
| YAML date mismatch (PyYAML auto-parses dates, Pydantic expects strings) | Test round-trip in 1.3; Pydantic validators can handle both | Open |
| Legacy phases fail new frontmatter reading (no plan/delta in FM) | All new fields optional; explicit fallback to block extraction | Open |

## 9. Decisions & Outcomes

_(To be filled during execution)_

## 10. Findings / Research Notes

_(To be filled during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Go/no-go documented
- [ ] Hand-off notes to Phase 2
