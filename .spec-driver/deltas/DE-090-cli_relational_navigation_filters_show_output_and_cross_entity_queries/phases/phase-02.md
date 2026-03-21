---
id: IP-090.PHASE-02
slug: "090-p1-relational-filters"
name: "P1 relational filters: --delta, --spec, --implemented-by, --related-to"
created: "2026-03-13"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-02
plan: IP-090
delta: DE-090
objective: >-
  Add 5 relational filter flags to list commands: --delta on audits/revisions,
  --spec on deltas, --implemented-by on requirements, --related-to on backlog.
entrance_criteria:
  - Phase 01 complete
exit_criteria:
  - All 5 filter flags working with tests
  - VT-090-P1-4 through VT-090-P1-8 passing
  - Lint clean (ruff + pylint)
  - Existing tests unbroken
verification:
  tests:
    - VT-090-P1-4
    - VT-090-P1-5
    - VT-090-P1-6
    - VT-090-P1-7
    - VT-090-P1-8
  evidence: []
tasks:
  - id: "2.1"
    description: "list audits --delta <ID>"
  - id: "2.2"
    description: "list revisions --delta <ID>"
  - id: "2.3"
    description: "list requirements --implemented-by <ID>"
  - id: "2.4"
    description: "list deltas --spec <ID>"
  - id: "2.5"
    description: "list backlog --related-to <ID>"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-02
```

# Phase 02 — P1 Relational Filters

## 1. Objective

Add 5 relational filter flags to existing list commands, following established patterns (--spec on audits/revisions, --related-to on deltas).

## 2. Links & References

- **Delta**: DE-090
- **Design Revision**: DR-090 §P1 (lines 179–307)
- **Specs**: PROD-010.FR-005
- **Files**: `supekku/cli/list.py`

## 3. Entrance Criteria

- [x] Phase 01 complete

## 4. Exit Criteria / Done When

- [x] `list audits --delta DE-090` filters by relation target
- [x] `list revisions --delta DE-090` filters by relation target
- [x] `list requirements --implemented-by DE-090` filters to delta's implements list
- [x] `list deltas --spec PROD-010` filters by applies_to.specs + relation targets
- [x] `list backlog --related-to DE-090` filters by frontmatter relation targets
- [x] VT-090-P1-4 through VT-090-P1-8 passing
- [x] `just` passes (tests + both linters)

## 5. Verification

- Unit tests in `list_test.py` for each new filter flag
- Each filter tested with matching and non-matching IDs
- Bare numeric ID input tested (e.g. `--delta 90` normalises to `DE-090`)

## 6. Assumptions & STOP Conditions

- `ChangeArtifact.relations` stores dicts with `type`/`target` keys (confirmed in P01)
- `BacklogItem.frontmatter` is a raw dict (confirmed: `dict(frontmatter)`)
- `extract_delta_relationships(body)` takes only text, no source_path kwarg

## 7. Tasks & Progress

| Status | ID  | Description                               | Parallel? | Notes                                             |
| ------ | --- | ----------------------------------------- | --------- | ------------------------------------------------- |
| [x]    | 2.1 | `list audits --delta <ID>`                | [P]       | Done: normalize_id + relations target match       |
| [x]    | 2.2 | `list revisions --delta <ID>`             | [P]       | Done: same pattern as audits                      |
| [x]    | 2.3 | `list requirements --implemented-by <ID>` | [x]       | Done: delta lookup → relationships block → filter |
| [x]    | 2.4 | `list deltas --spec <ID>`                 | [P]       | Done: applies_to.specs + relations targets        |
| [x]    | 2.5 | `list backlog --related-to <ID>`          | [P]       | Done: frontmatter.relations target match          |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |

## 9. Decisions & Outcomes

- DEC-090-04: --delta on audits/revisions checks relations targets only (no delta_ref on ChangeArtifact)
- DEC-090-05: --implemented-by does single-delta lookup, not full reverse index

## 10. Findings / Research Notes

- All 5 filters follow established patterns from existing --spec/--related-to on other commands.
- `--delta` on audits/revisions uses exact match on normalized ID (not substring like --spec).
- `--implemented-by` loads single delta file and parses relationships block — bounded to one file read.
- `--spec` on deltas checks both `applies_to.specs` and `.relations` targets for comprehensive coverage.
- `--related-to` on backlog uses raw frontmatter dict (BacklogItem.frontmatter confirmed as raw dict).
- list.py pylint went from 95→100 messages — 5 new are `import-outside-toplevel` (established pattern for lazy imports in CLI functions).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (3884 tests pass, linters clean)
- [x] Phase tracking block updated
- [x] Hand-off notes to Phase 03

### Hand-off to Phase 03

- All P1 filter flags implemented with 15 new tests.
- `just` passes: 3884 tests, ruff clean, pylint 9.72/10 (no new warnings in changed files beyond established patterns).
- Phase 03 scope: P2 richer show output — requires DR revision before implementation.
- DR-090 needs revision to cover P2 design before Phase 03 can begin.
