---
id: IP-036.PHASE-03
slug: 036-frontmatter_metadata_compaction_and_canonicalization_controls-phase-03
name: IP-036 Phase 03 - Generalized Framework Pilot
created: '2026-03-03'
updated: '2026-03-03'
status: complete
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
    status: complete
  - id: "2.2"
    description: Write round-trip tests for delta compaction
    status: complete
  - id: "2.3"
    description: Integrate compaction into sync write path for deltas (if applicable)
    status: complete
    notes: >-
      Resolved via `spec-driver compact delta` CLI command (8be91c4).
      Standalone command rather than sync flag — keeps sync read-only on source files.
  - id: "2.4"
    description: Measure before/after size on delta corpus
    status: complete
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
- [x] `compact_frontmatter(data, metadata)` function implemented
- [x] Compaction respects all four persistence classifications (canonical/derived/optional/default-omit)
- [x] Delta frontmatter round-trips without semantic loss
- [x] Existing delta files parse unchanged
- [x] Before/after size measurement on delta corpus
- [x] All tests pass, linters clean

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
| [x] | 2.1 | Implement compact_frontmatter() | Pure function in `compaction.py`, 25 tests |
| [x] | 2.2 | Round-trip tests for delta compaction | 8 delta-specific round-trip tests |
| [x] | 2.3 | Integrate into sync write path (if applicable) | Resolved: `spec-driver compact delta` CLI command (8be91c4) |
| [x] | 2.4 | Before/after size measurement on delta corpus | 37/37 files reducible, 7.1% avg, 26% max |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Compaction strips fields downstream consumers expect | Round-trip tests; full mode fallback | Mitigated |
| `applies_to` default shape mismatch (`prod` key absent from default) | Equality check, not structural subset | Mitigated (tested) |

## 9. Decisions & Outcomes

- **Placement**: `compact_frontmatter()` lives in `core/frontmatter_metadata/compaction.py` — near metadata definitions, pure function of `BlockMetadata` + data dict.
- **Task 2.3 resolved**: Added `spec-driver compact delta` CLI command (`supekku/cli/compact.py`, 8be91c4). Thin CLI delegates to `compact_frontmatter()`. Supports `--dry-run`, targeted delta ID, `--root` for testing.
- **`aliases` field**: Not in delta metadata definitions — passes through compaction as unknown field. Consistent with P1 finding (annotate when/if defined).

## 10. Findings / Research Notes

### Delta corpus compaction measurement
- **Corpus**: 37 delta files
- **All 37 files** have reduction potential
- **Total reduction**: 1011 bytes (7.1% of frontmatter)
- **Range**: 0.3% (DE-032, DE-033 — minimal defaults) to 26% (DE-021 — mostly empty defaults)
- **Primary savings**: `relations: []`, `applies_to: {specs: [], requirements: []}`, empty optional arrays (`owners`, `tags`, `risk_register`, `context_inputs`)
- **Note**: Delta frontmatter is relatively small (avg ~386 bytes) so absolute savings are modest; the value is in noise reduction and diff cleanliness.

### Implementation details
- `compact_frontmatter(data, metadata, mode="compact")` — 42 lines of code, pure function
- Helper `_should_keep(persistence, value, default_value)` implements the four-rule semantics table
- Unknown fields (not in metadata) pass through — safe for forward compatibility
- `mode="full"` returns a shallow copy unchanged — no-op for non-compacting paths

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (§10)
- [x] Notes updated
- [x] Hand-off: doc alignment (frontmatter-schema.md, processes.md) + memory record delegated to next agent
