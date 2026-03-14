---
id: IP-033.PHASE-09
slug: 033-memory_records_schema_and_command_surface-phase-09
name: IP-033 Phase 09 - Consolidate Artifact ID Patterns
created: "2026-03-03"
updated: "2026-03-03"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-09
plan: IP-033
delta: DE-033
objective: >-
  Consolidate duplicated artifact ID regex patterns from blocks/revision.py
  and blocks/verification.py into core/artifact_ids.py. Eliminate pattern
  drift and establish single source of truth for ID classification.
entrance_criteria:
  - Phase 8 complete (artifact_ids.py exists with classify_artifact_id)
exit_criteria:
  - verification, phase, subject patterns added to artifact_ids.py
  - revision.py uses artifact_ids instead of local _is_*_id() helpers
  - verification.py uses artifact_ids instead of local regex constants
  - No duplicate ID patterns remain outside core/artifact_ids.py
  - All existing tests pass (no regressions)
  - Lint clean (ruff + pylint)
tasks:
  - id: "9.1"
    description: "Extend artifact_ids.py — add verification, phase, subject patterns"
  - id: "9.2"
    description: "Consolidate revision.py — replace local patterns + helpers"
  - id: "9.3"
    description: "Consolidate verification.py — replace local patterns"
  - id: "9.4"
    description: "Verify all tests pass, lint clean"
risks:
  - description: "Pattern harmonization changes validation strictness"
    mitigation: "Shared patterns are more correct (PROD prefix, 3+ digits); review test diffs"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-09
```

# Phase 9 — Consolidate Artifact ID Patterns

## 1. Objective

Eliminate duplicated artifact ID regex patterns across `blocks/revision.py`
and `blocks/verification.py` by consolidating into `core/artifact_ids.py`.

## 2. Links & References

- **ID classifier**: `supekku/scripts/lib/core/artifact_ids.py`
- **Revision blocks**: `supekku/scripts/lib/blocks/revision.py`
- **Verification blocks**: `supekku/scripts/lib/blocks/verification.py`
- **Phase 8**: created `artifact_ids.py` (34 tests)

## 3. Entrance Criteria

- [x] Phase 8 complete — `artifact_ids.py` exists with `classify_artifact_id()`, `is_artifact_id()`

## 4. Exit Criteria / Done When

- [x] `artifact_ids.py` extended with verification, phase, plan patterns + `is_kind()` helper (51 tests)
- [x] `revision.py` — 6 constants + 6 functions removed, 13 call sites using `is_kind()` (45 tests pass)
- [x] `verification.py` — 4 constants removed, using `is_kind()` + `classify_artifact_id()` (54 tests pass)
- [x] 2104 tests pass (up from 2087)
- [x] ruff clean, pylint 9.61 (no regression)

## 5. Duplication Inventory

### revision.py (6 constants + 6 functions)

| Local             | Shared equivalent            | Delta                                               |
| ----------------- | ---------------------------- | --------------------------------------------------- |
| `_REQUIREMENT_ID` | `ID_PATTERNS["requirement"]` | local misses PROD prefix, uses `\d{3}` not `\d{3,}` |
| `_SPEC_ID`        | `ID_PATTERNS["spec"]`        | local uses `\d{3}` not `\d{3,}`                     |
| `_REVISION_ID`    | `ID_PATTERNS["revision"]`    | identical                                           |
| `_DELTA_ID`       | `ID_PATTERNS["delta"]`       | identical                                           |
| `_AUDIT_ID`       | `ID_PATTERNS["audit"]`       | identical                                           |
| `_BACKLOG_ID`     | `ID_PATTERNS["backlog"]`     | local too permissive (`[A-Z]+`)                     |

### verification.py (4 constants)

| Local              | Shared equivalent            | Delta                          |
| ------------------ | ---------------------------- | ------------------------------ |
| `_REQUIREMENT_ID`  | `ID_PATTERNS["requirement"]` | same as revision.py delta      |
| `_VERIFICATION_ID` | **none** — needs adding      | `V[TAH]-\d{3,}$`               |
| `_SUBJECT_ID`      | **none** — needs adding      | `(SPEC\|PROD\|IP\|AUD)-\d{3,}` |
| `_PHASE_ID`        | **none** — needs adding      | `IP-\d{3,}.PHASE-\d{2}$`       |

## 7. Tasks & Progress

| Status | ID  | Description                 | Notes                                                                                 |
| ------ | --- | --------------------------- | ------------------------------------------------------------------------------------- |
| [x]    | 9.1 | Extend artifact_ids.py      | Added plan, phase, verification patterns + `is_kind()`. 51 tests.                     |
| [x]    | 9.2 | Consolidate revision.py     | Removed 6 constants + 6 `_is_*_id()` functions, 13 call sites → `is_kind()`.          |
| [x]    | 9.3 | Consolidate verification.py | Removed 4 constants. `_SUBJECT_ID` → `classify_artifact_id() in VALID_SUBJECT_KINDS`. |
| [x]    | 9.4 | Verify + lint               | 2104 pass, ruff clean, pylint 9.61 (no regression).                                   |

## 9. Decisions

- `_SUBJECT_ID` composite pattern replaced with `classify_artifact_id() in VALID_SUBJECT_KINDS` — more declarative, easier to extend
- `is_kind()` added as targeted single-kind check — avoids iterating all patterns for known-kind validation
- Pattern harmonization: local patterns that used `\d{3}` (3 digits exactly) now use shared `\d{3,}` (3+ digits); local `_BACKLOG_ID` that accepted any `[A-Z]+` prefix now uses explicit prefixes — both are correctness improvements

## 10. Files Changed

### Modified

- `supekku/scripts/lib/core/artifact_ids.py` + `_test.py` — added plan, phase, verification patterns + `is_kind()`
- `supekku/scripts/lib/blocks/revision.py` — removed 6 regex constants + 6 `_is_*_id()` functions; 13 call sites use `is_kind()`
- `supekku/scripts/lib/blocks/verification.py` — removed 4 regex constants; uses `is_kind()` + `classify_artifact_id()`
