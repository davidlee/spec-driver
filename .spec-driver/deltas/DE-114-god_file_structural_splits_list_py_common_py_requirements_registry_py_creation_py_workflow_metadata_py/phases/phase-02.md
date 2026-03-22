---
id: IP-114-P02
slug: "114-god_file_structural_splits_list_py_common_py_requirements_registry_py_creation_py_workflow_metadata_py-phase-02"
name: "Lib: split creation.py and workflow_metadata.py"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
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

- [ ] `changes/creation.py` ≤400 lines, re-exports all public symbols
- [ ] `_creation_utils.py`, `revision_creation.py`, `delta_creation.py`, `audit_creation.py`, `phase_creation.py` exist
- [ ] `blocks/workflow_metadata.py` ≤180 lines, re-exports all public symbols
- [ ] 7 schema files exist under `blocks/` (`state_schema.py`, `handoff_schema.py`, `review_index_schema.py`, `review_findings_schema.py`, `sessions_schema.py`, `notes_bridge_schema.py`, `phase_bridge_schema.py`)
- [ ] `ruff check supekku` — zero new errors
- [ ] `pytest supekku` — all tests pass
- [ ] No file >500 lines

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
| [ ]    | 2.1  | Extract `_creation_utils.py`                             |           | ~40 lines                                   |
| [ ]    | 2.2  | Extract `revision_creation.py`                           | [P]       | ~75 lines                                   |
| [ ]    | 2.3  | Extract `delta_creation.py`                              | [P]       | ~140 lines                                  |
| [ ]    | 2.4  | Extract `audit_creation.py`                              | [P]       | ~80 lines                                   |
| [ ]    | 2.5  | Extract `phase_creation.py`                              |           | ~320 lines — all phase helpers + create_phase |
| [ ]    | 2.6  | Slim `creation.py` with re-exports                       |           | Depends on 2.1–2.5                          |
| [ ]    | 2.7  | Lint + test after creation.py split                      |           | Gate before workflow_metadata               |
| [ ]    | 2.8  | Extract `state_schema.py`                                |           | ~215 lines, includes `_artifact_block`      |
| [ ]    | 2.9  | Extract `handoff_schema.py`                              | [P]       | ~290 lines                                  |
| [ ]    | 2.10 | Extract `review_index_schema.py`                         | [P]       | ~370 lines, includes `_finding_*` chain     |
| [ ]    | 2.11 | Extract `review_findings_schema.py`                      | [P]       | ~175 lines, includes `_round_entry`         |
| [ ]    | 2.12 | Extract `sessions_schema.py`                             | [P]       | ~76 lines                                   |
| [ ]    | 2.13 | Extract `notes_bridge_schema.py`                         | [P]       | ~64 lines                                   |
| [ ]    | 2.14 | Extract `phase_bridge_schema.py`                         | [P]       | ~185 lines, includes `_placeholder_renderer`|
| [ ]    | 2.15 | Slim `workflow_metadata.py` with re-exports + registration |         | Depends on 2.8–2.14                         |
| [ ]    | 2.16 | Extract phase tests to `phase_creation_test.py`          |           | Optional partial test split                 |
| [ ]    | 2.17 | Lint + test after workflow_metadata split                |           | Final gate                                  |

## 8. Risks & Mitigations

| Risk                                                | Mitigation                                                     | Status    |
| --------------------------------------------------- | -------------------------------------------------------------- | --------- |
| Schema registration depends on import order         | Registration loop stays in slim file, imports schema constants | mitigated |
| `_finding_disposition` chain shared across schemas   | Chain moves with review_index_schema (sole consumer of chain)  | mitigated |

## 9. Decisions & Outcomes

- 2026-03-22 — Do creation.py first (simpler), then workflow_metadata.py
- 2026-03-22 — Single-consumer helpers move with their schema (DEC-114-05)

## 10. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Phase 03 sheet created
- [ ] Delta/plan updated
