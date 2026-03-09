---
id: IP-087.PHASE-01
slug: 087-cross_artifact_tui_fuzzy_search_with_relational_weighting-phase-01
name: Search core — SearchEntry, index builder, scorer
created: '2026-03-10'
updated: '2026-03-10'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-087.PHASE-01
plan: IP-087
delta: DE-087
objective: >-
  Create the SearchEntry model, self-contained index builder, and weighted
  scorer as pure functions with full test coverage. No TUI code in this phase.
entrance_criteria:
  - DR-087 accepted with all design decisions resolved
exit_criteria:
  - SearchEntry dataclass defined with searchable_fields and relation_targets
  - build_search_index(root) produces entries for all artifact types
  - score_entry(query, search_entry) applies tiered weights correctly
  - Per-tag scoring works (not joined string)
  - VT-087-001, VT-087-002, VT-087-003 passing
  - just check green
verification:
  tests:
    - VT-087-001
    - VT-087-002
    - VT-087-003
  evidence: []
tasks:
  - id: '1.1'
    summary: SearchEntry dataclass and field/weight constants
  - id: '1.2'
    summary: Index builder — _extract_searchable_fields, _extract_relation_targets, build_search_index
  - id: '1.3'
    summary: Scorer — score_entry with tiered weights
  - id: '1.4'
    summary: Tests for all of the above
risks:
  - description: getattr fragility on heterogeneous records
    mitigation: Test against all ArtifactType values with mock records
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-087.PHASE-01
```

# Phase 01 — Search core

## 1. Objective
Create the `supekku/tui/search/` package with `SearchEntry`, index builder, and scorer as pure functions. No TUI widget code — this phase is entirely testable without Textual.

## 2. Links & References
- **Delta**: [DE-087](../DE-087.md)
- **Design Revision**: [DR-087](../DR-087.md) — DEC-087-01 (SearchEntry), DEC-087-02 (weights), DEC-087-05 (self-contained builder)
- **Specs**: PROD-010, PROD-015
- **Reused code**: `artifact_view._REGISTRY_FACTORIES`, `artifact_view.adapt_record`, `relations.query.collect_references`

## 3. Entrance Criteria
- [x] DR-087 accepted with all design decisions resolved

## 4. Exit Criteria / Done When
- [x] `supekku/tui/search/__init__.py` exists
- [x] `SearchEntry` dataclass with `entry`, `searchable_fields`, `relation_targets`
- [x] `build_search_index(root=)` produces entries for all registry types
- [x] `score_entry(query, search_entry)` applies weights: ID 1.0, title 0.7, relation 0.5, attr 0.4
- [x] Tags produce per-tag entries (`tag.0`, `tag.1`), not joined string
- [x] VT-087-001, VT-087-002, VT-087-003 passing
- [x] `just check` green (tests + both linters)

## 5. Verification
- `just test` — all new tests pass
- `just lint` — zero warnings on new files
- `just pylint-files supekku/tui/search/*.py` — no new warnings
- VT-087-001: scorer weight tests
- VT-087-002: index builder tests (mock registries for all types)
- VT-087-003: ranking invariant — own-ID at moderate match beats relation-target at perfect match

## 6. Assumptions & STOP Conditions
- **Assumption**: `_REGISTRY_FACTORIES` from `artifact_view.py` can be imported and called independently of `ArtifactSnapshot`
- **Assumption**: All registry `collect()` methods return `dict[str, record]` per ADR-009
- **STOP**: If any registry's `collect()` signature diverges from ADR-009 convention, consult before adapting

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | SearchEntry dataclass + constants | [ ] | |
| [x] | 1.2 | Index builder | [ ] | |
| [x] | 1.3 | Scorer | [ ] | |
| [x] | 1.4 | Tests | [ ] | 32 tests passing |

### Task Details

- **1.1 SearchEntry dataclass + constants**
  - **Files**: `supekku/tui/search/__init__.py`, `supekku/tui/search/index.py`
  - **Design**: Frozen dataclass per DEC-087-01. Named weight constants per POL-002. Named field constants for `searchable_fields` keys.
  - **Constants**:
    ```python
    WEIGHT_OWN_ID = 1.0
    WEIGHT_TITLE = 0.7
    WEIGHT_RELATION_TARGET = 0.5
    WEIGHT_ATTRIBUTE = 0.4
    FIELD_ID = "id"
    FIELD_TITLE = "title"
    FIELD_STATUS = "status"
    _FRONTMATTER_ATTRS = ("kind", "slug", "category", "c4_level", "tags")
    ```

- **1.2 Index builder**
  - **Files**: `supekku/tui/search/index.py`
  - **Design**: `build_search_index(*, root: Path) -> list[SearchEntry]`. Iterates `_REGISTRY_FACTORIES`, calls `collect()`, `adapt_record()`, `_extract_searchable_fields()`, `_extract_relation_targets()`. See DR-087 DEC-087-05 code sketch.
  - **Key detail**: Tags are split to per-tag entries. `collect_references()` from relation query layer for targets.

- **1.3 Scorer**
  - **Files**: `supekku/tui/search/scorer.py`
  - **Design**: `score_entry(query: str, entry: SearchEntry) -> float`. Uses `textual.fuzzy.Matcher`. Scores each field × weight, each relation target × WEIGHT_RELATION_TARGET. Returns max.
  - **Convenience**: `search(query: str, index: list[SearchEntry], *, limit: int = 50) -> list[SearchEntry]` — score, filter >0, sort descending, truncate.

- **1.4 Tests**
  - **Files**: `supekku/tui/search/scorer_test.py`, `supekku/tui/search/index_test.py`
  - **VT-087-001**: Scorer applies weights correctly; field priority ordering; zero-score entries excluded
  - **VT-087-002**: Index builder produces entries for all artifact types; tags split to per-tag entries; frontmatter attrs extracted; relation targets collected
  - **VT-087-003**: Own-ID moderate match (e.g. "DE-08" vs "DE-087") outranks perfect relation-target match (e.g. "DE-085" referenced by another artifact)
