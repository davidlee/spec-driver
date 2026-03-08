---
id: IP-070.PHASE-01
slug: 070-registry-sync-and-schema
name: IP-070 Phase 01 - Registry sync and schema completeness
created: '2026-03-08'
updated: '2026-03-08'
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-070.PHASE-01
plan: IP-070
delta: DE-070
objective: >-
  Add ext_id/ext_url to registry YAML serialization for requirements,
  policies, and standards. Add ext_id/ext_url to base frontmatter schema.
  Audit model vs schema field parity.
entrance_criteria:
  - DE-067 complete
exit_criteria:
  - RequirementRecord.to_dict() includes ext_id/ext_url
  - PolicyRecord.to_dict() includes ext_id/ext_url
  - StandardRecord.to_dict() includes ext_id/ext_url
  - Base frontmatter schema includes ext_id/ext_url
  - schema show output reflects ext_id/ext_url
  - Model vs schema parity audit complete (VA)
  - Tests pass, just check green
verification:
  tests:
    - VT-070-001
  evidence: []
tasks:
  - id: "1.1"
    description: Add ext_id/ext_url to RequirementRecord.to_dict()
  - id: "1.2"
    description: Add ext_id/ext_url to PolicyRecord.to_dict()
  - id: "1.3"
    description: Add ext_id/ext_url to StandardRecord.to_dict()
  - id: "1.4"
    description: Add ext_id/ext_url to BASE_FRONTMATTER_METADATA
  - id: "1.5"
    description: Audit model vs schema field parity across all types
  - id: "1.6"
    description: Write tests
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-070.PHASE-01
```

# Phase 1 – Registry sync and schema completeness

## 1. Objective

Fix ext_id/ext_url serialization gaps in 3 registry `to_dict()` methods,
add the fields to the base frontmatter metadata schema, and audit for any
other model ↔ schema field parity gaps.

## 2. Links & References

- **Delta**: DE-070
- **Predecessor**: DE-067 (added ext_id/ext_url to models)
- **Specs**: SPEC-116

## 3. Entrance Criteria

- [x] DE-067 complete

## 4. Exit Criteria / Done When

- [x] RequirementRecord.to_dict() includes ext_id/ext_url
- [x] PolicyRecord.to_dict() includes ext_id/ext_url
- [x] StandardRecord.to_dict() includes ext_id/ext_url
- [x] BASE_FRONTMATTER_METADATA includes ext_id/ext_url
- [x] `schema show` output reflects the new fields
- [x] Model ↔ schema parity audit complete (VA: 2 gaps found — MemoryRecord, DecisionRecord — tracked as follow-up)
- [x] `just check` passes (3372 passed; 2 failures in edit_test.py are DE-068, unrelated)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add ext_id/ext_url to RequirementRecord.to_dict() | [P] | done |
| [x] | 1.2 | Add ext_id/ext_url to PolicyRecord.to_dict() | [P] | done |
| [x] | 1.3 | Add ext_id/ext_url to StandardRecord.to_dict() | [P] | done |
| [x] | 1.4 | Add ext_id/ext_url to BASE_FRONTMATTER_METADATA | | done |
| [x] | 1.5 | Audit model vs schema field parity | | VA: 2 gaps (Memory, Decision) — follow-up |
| [x] | 1.6 | Write tests | | 9 tests across 3 files |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to close-change
