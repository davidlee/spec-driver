---
id: IP-103.PHASE-01
slug: "103-handover_and_review_orchestration-phase-01"
name: Schema definitions and registration
created: "2026-03-21"
updated: "2026-03-21"
status: in_progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-103.PHASE-01
plan: IP-103
delta: DE-103
objective: >-
  Define metadata-driven validators for all 7 workflow/bridge schemas from
  DR-102 §3/§7 and register them in the block schema registry.
entrance_criteria:
  - DR-102 approved (yes)
  - Open questions resolved (yes — DEC-103-001, DEC-103-002)
exit_criteria:
  - All 7 schemas defined as BlockMetadata instances
  - MetadataValidator produces correct errors for invalid input
  - MetadataValidator accepts valid input for all schemas
  - Schemas registered and visible via `spec-driver list schemas`
  - Lint clean, tests passing
verification:
  tests:
    - VT-103-001 schema validation tests
  evidence: []
tasks:
  - id: T01
    description: Create workflow schema metadata module
  - id: T02
    description: Create bridge schema metadata module
  - id: T03
    description: Register schemas in block schema registry
  - id: T04
    description: Add side-effect import in cli/schema.py
  - id: T05
    description: Write tests for all schema validation
  - id: T06
    description: Lint and verify
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-103.PHASE-01
```

# Phase 01 — Schema definitions and registration

## 1. Objective

Define metadata-driven validators for all 7 schemas from DR-102 (5 workflow
artifacts + 2 bridge blocks) and register them in the block schema registry
so they appear in `spec-driver list schemas` and `spec-driver show schema`.

## 2. Links & References

- **Delta**: DE-103
- **Design Revision**: DR-102 §3 (artifact schemas), §7 (bridge sections), §10 (validation rules)
- **Specs**: PROD-011
- **Existing pattern**: `supekku/scripts/lib/blocks/plan_metadata.py`

## 3. Entrance Criteria

- [x] DR-102 approved
- [x] Open questions resolved (DEC-103-001, DEC-103-002)

## 4. Exit Criteria / Done When

- [ ] All 7 schemas defined as `BlockMetadata` instances with correct required/optional/enum fields
- [ ] `MetadataValidator` produces correct errors for invalid input
- [ ] `MetadataValidator` accepts valid input for all schemas
- [ ] Schemas registered and visible via `spec-driver list schemas`
- [ ] Lint clean, all tests passing

## 5. Verification

- `uv run pytest supekku/scripts/lib/blocks/workflow_metadata_test.py -v`
- `uv run ruff check supekku/scripts/lib/blocks/workflow_metadata.py supekku/scripts/lib/blocks/workflow_metadata_test.py`
- `uv run spec-driver list schemas` — verify workflow schemas appear

## 6. Assumptions & STOP Conditions

- Assumptions: The existing `BlockMetadata`/`FieldMetadata`/`MetadataValidator` system is sufficient for these schemas. DR-102 schemas use nested objects with nested records — the metadata system supports this via `properties` and `items`.
- STOP when: `FieldMetadata` cannot express a DR-102 constraint (e.g., cross-field uniqueness for finding IDs). Log gap and proceed with what's expressible.

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | T01 | Create `workflow_metadata.py` — 5 workflow schema definitions | state, handoff, review-index, review-findings, sessions |
| [ ] | T02 | Add bridge schema definitions | notes-bridge, phase-bridge |
| [ ] | T03 | Register all 7 schemas in block schema registry | Via `register_block_schema` at module level |
| [ ] | T04 | Add side-effect import in `cli/schema.py` | So schemas are registered when CLI lists them |
| [ ] | T05 | Write `workflow_metadata_test.py` | Valid/invalid cases for all 7 schemas |
| [ ] | T06 | Lint and verify | ruff, pytest, `list schemas` |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Nested record constraints (uniqueness) not expressible in FieldMetadata | Document gap; defer cross-field uniqueness to command-level validation | open |

## 9. Decisions & Outcomes

_To be filled during implementation._

## 10. Findings / Research Notes

_To be filled during implementation._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to Phase 02
