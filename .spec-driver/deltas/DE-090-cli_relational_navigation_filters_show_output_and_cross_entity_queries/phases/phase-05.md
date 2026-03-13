---
id: IP-090.PHASE-05
slug: 090-cli_relational_navigation_filters_show_output_and_cross_entity_queries-phase-05
name: IP-090 Phase 05 — P4 reverse reference filtering
created: '2026-03-14'
updated: '2026-03-14'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-05
plan: IP-090
delta: DE-090
objective: >-
  Implement generic reverse reference filtering (--referenced-by / --not-referenced-by)
  on list commands, add convenience aliases (--unaudited, --unimplemented), and provide
  a shared load_all_artifacts() helper in cli/common.py.
entrance_criteria:
  - Phase 04 complete (P3 domain collectors landed, commit b5597c7)
  - DR-090 §P4 design approved
exit_criteria:
  - collect_reverse_reference_targets() and partition_by_reverse_references() in query.py
  - load_all_artifacts() in cli/common.py
  - --referenced-by / --not-referenced-by flags on list deltas, list requirements, list audits
  - --unaudited alias on list deltas
  - --unimplemented alias on list requirements
  - VT-090-P4-1 through VT-090-P4-7 passing
  - lint clean (ruff + pylint)
verification:
  tests:
    - VT-090-P4-1
    - VT-090-P4-2
    - VT-090-P4-3
    - VT-090-P4-4
    - VT-090-P4-5
    - VT-090-P4-6
    - VT-090-P4-7
  evidence: []
tasks:
  - id: 5.1
    description: "Add collect_reverse_reference_targets() and partition_by_reverse_references() to query.py"
  - id: 5.2
    description: "Add load_all_artifacts() shared helper to cli/common.py"
  - id: 5.3
    description: "Add --referenced-by / --not-referenced-by flags to list deltas"
  - id: 5.4
    description: "Add --referenced-by / --not-referenced-by flags to list requirements"
  - id: 5.5
    description: "Add --referenced-by / --not-referenced-by flags to list audits"
  - id: 5.6
    description: "Add --unaudited convenience alias to list deltas"
  - id: 5.7
    description: "Add --unimplemented convenience alias to list requirements"
  - id: 5.8
    description: "Write tests for all VT-090-P4-* entries"
risks:
  - description: "load_all_artifacts registry loading may have import issues"
    mitigation: "Use lazy imports matching existing common.py patterns"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-05
```

# Phase 05 — P4 Reverse Reference Filtering

## 1. Objective
Implement generic reverse reference filtering infrastructure and CLI surface:
- Query functions: `collect_reverse_reference_targets()`, `partition_by_reverse_references()`
- Shared helper: `load_all_artifacts()` in `cli/common.py`
- CLI flags: `--referenced-by <type>` / `--not-referenced-by <type>` (mutually exclusive)
- Convenience aliases: `--unaudited` (list deltas), `--unimplemented` (list requirements)

## 2. Links & References
- **Delta**: DE-090
- **Design Revision Sections**: DR-090 §P4-1 (query infra), §P4-2 (CLI flags), §P4-3 (aliases)
- **Specs / PRODs**: PROD-010.FR-005
- **Design Decisions**: DEC-090-10, DEC-090-11

## 3. Entrance Criteria
- [x] Phase 04 complete (P3 domain collectors landed, commit b5597c7)
- [x] DR-090 §P4 design approved

## 4. Exit Criteria / Done When
- [x] `collect_reverse_reference_targets()` and `partition_by_reverse_references()` working
- [x] `load_all_artifacts()` in `cli/common.py`
- [x] `--referenced-by` / `--not-referenced-by` on list deltas, requirements, audits
- [x] `--unaudited` on list deltas
- [x] `--unimplemented` on list requirements
- [x] VT-090-P4-1 through VT-090-P4-7 passing
- [x] Lint clean

## 5. Verification
- `pytest supekku/scripts/lib/relations/query_test.py -v`
- `pytest supekku/cli/list_test.py -v`
- `just` (full suite)

## 6. Assumptions & STOP Conditions
- Assumes P3 collectors (phase 04) are working and committed
- STOP if: registry loading in `load_all_artifacts()` reveals circular imports

## 7. Tasks & Progress

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [x] | 5.1 | Query infra: `collect_reverse_reference_targets()`, `partition_by_reverse_references()` | query.py |
| [x] | 5.2 | `load_all_artifacts()` helper | cli/common.py |
| [x] | 5.3 | `--referenced-by` / `--not-referenced-by` on list deltas | list.py |
| [x] | 5.4 | Same flags on list requirements | list.py |
| [x] | 5.5 | Same flags on list audits | list.py |
| [x] | 5.6 | `--unaudited` alias on list deltas | list.py |
| [x] | 5.7 | `--unimplemented` alias on list requirements | list.py |
| [x] | 5.8 | Tests for VT-090-P4-1 through P4-7 | query_test.py, list_test.py |
