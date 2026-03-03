---
id: IP-036.PHASE-03
slug: 036-frontmatter_metadata_compaction_and_canonicalization_controls-phase-03
name: IP-036 Phase 03 - Generalized Framework Pilot
created: '2026-03-03'
updated: '2026-03-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-036.PHASE-03
plan: IP-036
delta: DE-036
objective: >-
  Implement a shared compaction profile mechanism that uses FieldMetadata
  persistence annotations to omit default/derived fields during write,
  and pilot it on delta frontmatter.
entrance_criteria:
  - Phase 1 complete (FieldMetadata persistence fields, memory/delta annotations)
exit_criteria:
  - Compaction function uses FieldMetadata persistence + default_value to decide field omission
  - Delta frontmatter round-trips through compact write without semantic loss
  - Existing files parse unchanged (read-side tolerance)
  - Measurable metadata reduction on delta corpus
  - All tests pass, linters clean
verification:
  tests:
    - VT-036-003: Delta compaction round-trip fidelity, default-omit fields stripped
  evidence:
    - Before/after delta frontmatter size comparison
    - Test output from just test
tasks:
  - id: "2.1"
    description: Implement compact_frontmatter() using BlockMetadata persistence annotations
    status: pending
  - id: "2.2"
    description: Write round-trip tests for delta compaction
    status: pending
  - id: "2.3"
    description: Integrate compaction into sync write path for deltas (if applicable)
    status: pending
  - id: "2.4"
    description: Measure before/after size on delta corpus
    status: pending
risks:
  - description: Compaction strips fields that downstream consumers expect
    mitigation: Round-trip tests; read-side tolerance; full mode always available
  - description: applies_to default_value shape mismatch (has prod key not in default)
    mitigation: Equality check against default_value, not structural subset
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-036.PHASE-03
```

# Phase 2 - Generalized Framework Pilot

## 1. Objective
Implement a shared compaction profile mechanism that uses `FieldMetadata.persistence` and `default_value` to omit default/derived fields during write, and pilot it on delta frontmatter (DEC-036-003).

## 2. Links & References
- **Delta**: DE-036
- **Design Revision**: DR-036 §4 (code impact), §7 (DEC-036-003, DEC-036-004)
- **Phase 0**: phases/phase-01.md §10.3 (delta canonical/derived matrix), §10.5 (compaction semantics)
- **Phase 1**: phases/phase-02.md (FieldMetadata extension, persistence annotations)
- **Key code**: `frontmatter_metadata/delta.py`, `blocks/metadata/schema.py`

## 3. Entrance Criteria
- [x] Phase 1 complete (FieldMetadata has persistence + default_value; delta fields annotated)

## 4. Exit Criteria / Done When
- [ ] `compact_frontmatter(data, metadata)` function implemented
- [ ] Compaction respects all four persistence classifications (canonical/derived/optional/default-omit)
- [ ] Delta frontmatter round-trips without semantic loss
- [ ] Existing delta files parse unchanged
- [ ] Before/after size measurement on delta corpus
- [ ] All tests pass, linters clean

## 5. Verification
- `just test` — all tests pass
- `just lint` + `just pylint` — zero warnings
- Round-trip tests: compact then parse, assert semantic equivalence
- VA-036-001 prep: before/after byte count on delta corpus

## 6. Assumptions & STOP Conditions
- Assumes `default_value` equality check is sufficient (no deep structural matching needed)
- STOP if: compaction function needs to understand nested block semantics beyond top-level field matching

## 7. Tasks & Progress

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [ ] | 2.1 | Implement compact_frontmatter() | Pure function using BlockMetadata |
| [ ] | 2.2 | Round-trip tests for delta compaction | Confirm no semantic loss |
| [ ] | 2.3 | Integrate into sync write path (if applicable) | May be deferred to P3 |
| [ ] | 2.4 | Before/after size measurement on delta corpus | VA-036-001 evidence |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Compaction strips fields downstream consumers expect | Round-trip tests; full mode fallback | Open |
| `applies_to` default shape mismatch (`prod` key absent from default) | Equality check, not structural subset | Open |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to Phase 3 (Verification & Rollout)
