---
id: IP-114-P02
slug: "114-god_file_structural_splits_list_py_common_py_requirements_registry_py_creation_py_workflow_metadata_py-phase-02"
name: "Lib: split creation.py and workflow_metadata.py"
created: "2026-03-22"
updated: "2026-03-23"
status: completed
kind: phase
plan: IP-114
delta: DE-114
---

# Phase 02 — Lib: split creation.py and workflow_metadata.py

## 1. Objective

Split `changes/creation.py` (1,056 lines) into 6 files and `blocks/workflow_metadata.py` (1,485 lines) into 8 files. All files ≤500 lines. Zero behaviour change.

## 2. Links & References

- **Delta**: DE-114
- **Design Revision**: DR-114 §4d (creation), §4e (workflow_metadata)
- **Specs**: SPEC-110, SPEC-114

## 3. Entrance Criteria

- [x] Phase 01 complete (CLI layer splits done)
- [x] DR-114 accepted

## 4. Exit Criteria / Done When

- [x] `changes/creation.py` ≤400 lines (276), re-exports all public symbols
- [x] `_creation_utils.py` (41), `revision_creation.py` (98), `delta_creation.py` (170), `audit_creation.py` (102), `phase_creation.py` (497) exist
- [x] `blocks/workflow_metadata.py` ≤251 lines, re-exports all public symbols
- [x] 7 schema files exist under `blocks/` (state 227, handoff 301, review_index 261, review_findings 268, sessions 111, notes_bridge 69, phase_bridge 72)
- [x] `ruff check supekku` — zero new errors
- [x] `pytest supekku` — 4585 passed, 4 skipped
- [x] No file >500 lines

## 5. Verification

- `uv run ruff check supekku/scripts/lib/changes/ supekku/scripts/lib/blocks/` — lint changed files
- `uv run python -m pytest supekku -q` — full suite
- `wc -l` on all new/modified files — size check

## 6. Assumptions & STOP Conditions

- **Assumption**: Re-exports in slim files cover all importers (verified in preflight: 4 workflow importers, 4 creation importers).
- **Assumption**: Schema registration loop in workflow_metadata can stay in slim file and import from schema files.
- **STOP when**: Circular import discovered between schema files.

## 7. Tasks & Progress

| Status | ID   | Description                                              | Parallel? | Notes                                       |
| ------ | ---- | -------------------------------------------------------- | --------- | ------------------------------------------- |
| [x]    | 2.1  | Extract `_creation_utils.py`                             |           | 41 lines                                    |
| [x]    | 2.2  | Extract `revision_creation.py`                           | [P]       | 98 lines                                    |
| [x]    | 2.3  | Extract `delta_creation.py`                              | [P]       | 170 lines                                   |
| [x]    | 2.4  | Extract `audit_creation.py`                              | [P]       | 102 lines                                   |
| [x]    | 2.5  | Extract `phase_creation.py`                              |           | 497 lines — all phase helpers + create_phase |
| [x]    | 2.6  | Slim `creation.py` with re-exports                       |           | 276 lines                                   |
| [x]    | 2.7  | Lint + test after creation.py split                      |           | 4585 passed, ruff clean                     |
| [x]    | 2.8  | Extract `state_schema.py`                                |           | 227 lines, includes `_artifact_block`       |
| [x]    | 2.9  | Extract `handoff_schema.py`                              | [P]       | 301 lines                                   |
| [x]    | 2.10 | Extract `review_index_schema.py`                         | [P]       | 261 lines                                   |
| [x]    | 2.11 | Extract `review_findings_schema.py`                      | [P]       | 268 lines, includes finding chain + _round  |
| [x]    | 2.12 | Extract `sessions_schema.py`                             | [P]       | 111 lines                                   |
| [x]    | 2.13 | Extract `notes_bridge_schema.py`                         | [P]       | 69 lines                                    |
| [x]    | 2.14 | Extract `phase_bridge_schema.py`                         | [P]       | 72 lines, includes `_placeholder_renderer`  |
| [x]    | 2.15 | Slim `workflow_metadata.py` with re-exports + registration |         | 251 lines                                   |
| [-]    | 2.16 | Extract phase tests to `phase_creation_test.py`          |           | Deferred — tests pass as-is                 |
| [x]    | 2.17 | Lint + test after workflow_metadata split                |           | 4585 passed, ruff clean                     |

## 8. Risks & Mitigations

| Risk                                                | Mitigation                                                     | Status    |
| --------------------------------------------------- | -------------------------------------------------------------- | --------- |
| Schema registration depends on import order         | Registration loop stays in slim file, imports schema constants | mitigated |
| `_finding_disposition` chain shared across schemas   | Chain moves with review_index_schema (sole consumer of chain)  | mitigated |

## 9. Decisions & Outcomes

- 2026-03-22 — Do creation.py first (simpler), then workflow_metadata.py
- 2026-03-22 — Single-consumer helpers move with their schema (DEC-114-05)
- 2026-03-22 — Finding chain (`_finding_disposition`, `_finding_item`, `_findings_list`, `_round_entry`) placed in `review_findings_schema.py` (sole consumer), not `review_index_schema.py` as DR-114 table suggested. DR-114's principle (DEC-114-05: single-consumer helpers move with their schema) takes precedence over the table.
- 2026-03-22 — `delta_creation.py` uses deferred import of `_render_plan` from `creation.py` to avoid circular dependency (create_delta calls _render_plan which lives in the slim creation.py).
- 2026-03-22 — Phase test split (2.16) deferred — test class doesn't split cleanly, tests pass as-is.

## 10. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 4585 passed, 4 skipped, 29 warnings (pre-existing)
- [ ] Phase 03 sheet created
- [ ] Delta/plan updated
