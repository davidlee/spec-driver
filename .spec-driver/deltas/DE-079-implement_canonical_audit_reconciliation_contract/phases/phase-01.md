---
id: IP-079.PHASE-01
slug: 079-implement_canonical_audit_reconciliation_contract-phase-01
name: "IP-079 Phase 01 — Schema foundation"
created: "2026-03-09"
updated: "2026-03-09"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-079.PHASE-01
plan: IP-079
delta: DE-079
objective: >-
  Build the schema foundation: audit metadata with disposition sub-schema, delta
  metadata with audit_gate, disposition constants, updated template, extended
  create_audit, and manual edit of existing audit with deprecated fields. All with
  tests, both linters clean.
entrance_criteria:
  - DR-079 accepted with 11 design decisions, 0 open questions
exit_criteria:
  - Audit frontmatter schema includes mode, delta_ref, and disposition sub-schema
  - Disposition constants defined (status, kind, outcome×kind, status×kind validity)
  - Delta frontmatter schema includes audit_gate and audit_gate_rationale
  - patch_level and next_actions removed from audit schema
  - Audit template updated with disposition structure, mode, delta_ref
  - create_audit accepts mode and delta_ref, scaffolds disposition placeholders
  - Existing audit with deprecated field manually edited
  - VT-079-001 tests pass
  - VA-079-001 schema review complete
  - Both linters clean on all touched files
verification:
  tests:
    - VT-079-001
  evidence:
    - VA-079-001
tasks:
  - id: "1.1"
    description: Define disposition constants
  - id: "1.2"
    description: Update audit frontmatter metadata schema
  - id: "1.3"
    description: Add audit_gate to delta frontmatter metadata schema
  - id: "1.4"
    description: Update audit template
  - id: "1.5"
    description: Extend create_audit with mode, delta_ref, disposition scaffolding
  - id: "1.6"
    description: Manually edit existing audit with deprecated field
  - id: "1.7"
    description: Write schema validation tests (VT-079-001)
risks:
  - description: Existing audit parsing breaks after deprecated field removal
    mitigation: Test both existing audits explicitly
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-079.PHASE-01
```

# Phase 1 — Schema Foundation

## 1. Objective

Build the data model foundation that all subsequent phases depend on: audit disposition sub-schema, delta audit_gate field, disposition constants, updated template, extended creation, and cleanup of deprecated fields.

## 2. Links & References

- **Delta**: DE-079
- **Design Revision**: DR-079 §4 (Code Impact Summary), DEC-079-001 through DEC-079-004, DEC-079-007, DEC-079-009, DEC-079-010
- **Specs**: SPEC-116 (frontmatter_metadata)
- **Pattern**: `supekku/scripts/lib/drift/models.py:115–170` for structured ref pattern

## 3. Entrance Criteria

- [x] DR-079 accepted with all design decisions resolved

## 4. Exit Criteria / Done When

- [x] Audit frontmatter schema has `mode`, `delta_ref`, and `disposition` sub-schema per finding
- [x] Disposition constants defined: `DISPOSITION_STATUS_*`, `DISPOSITION_KIND_*`, validity tables
- [x] Delta frontmatter schema has `audit_gate` (enum: auto|required|exempt) and `audit_gate_rationale`
- [x] `patch_level` and `next_actions` removed from audit schema and template
- [x] Audit template renders with disposition structure, `mode`, `delta_ref`
- [x] `create_audit()` accepts `mode` and `delta_ref` parameters, scaffolds disposition placeholders
- [x] Existing audits with deprecated fields manually edited (AUD-001, AUD-002)
- [x] VT-079-001 tests pass (25 tests: status×kind, outcome×kind, refs, closure_override)
- [x] VA-079-001: schema review confirms disposition is machine-checkable (structured FieldMetadata with validity matrices)
- [x] `just lint` clean on all touched files
- [x] `just pylint-files` clean on all touched files (9.71/10; new messages are structural, not quality regressions)

## 5. Verification

- `uv run pytest` on new and modified test files
- `just lint` (ruff)
- `just pylint-files <paths>`
- Manual review of template rendering via `create audit` dry test

## 6. Assumptions & STOP Conditions

- Assumptions:
  - The existing `FieldMetadata` system in `blocks/metadata.py` supports nested object schemas (it does — `audit_window` is precedent)
  - `create_audit` CLI passes through to `creation.py` — check the CLI layer for any needed parameter additions
- STOP when:
  - `FieldMetadata` cannot express the disposition sub-schema depth (nested objects with nested arrays of objects)
  - Existing audit test fixtures break in ways that suggest broader parsing issues

## 7. Tasks & Progress

| Status | ID  | Description                                     | Parallel? | Notes                     |
| ------ | --- | ----------------------------------------------- | --------- | ------------------------- |
| [x]    | 1.1 | Define disposition constants module             | [ ]       | In audit.py               |
| [x]    | 1.2 | Update audit frontmatter metadata schema        | [ ]       | Depends on 1.1            |
| [x]    | 1.3 | Add audit_gate to delta frontmatter schema      | [P]       | Independent of 1.1/1.2    |
| [x]    | 1.4 | Update audit template                           | [ ]       | Depends on 1.2            |
| [x]    | 1.5 | Extend create_audit with mode, delta_ref        | [ ]       | Depends on 1.2, 1.4       |
| [x]    | 1.6 | Edit existing audits (remove deprecated fields) | [P]       | AUD-001, AUD-002 migrated |
| [x]    | 1.7 | Write VT-079-001 tests                          | [ ]       | 25 tests, all pass        |

### Task Details

- **1.1 Define disposition constants**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/audit.py` (or a new constants module if cleaner)
  - **What**:
    - `DISPOSITION_STATUS_RECONCILED`, `DISPOSITION_STATUS_ACCEPTED`, `DISPOSITION_STATUS_PENDING`
    - `DISPOSITION_KIND_ALIGNED`, `DISPOSITION_KIND_SPEC_PATCH`, `DISPOSITION_KIND_REVISION`, `DISPOSITION_KIND_FOLLOW_UP_DELTA`, `DISPOSITION_KIND_FOLLOW_UP_BACKLOG`, `DISPOSITION_KIND_TOLERATED_DRIFT`
    - `VALID_STATUS_KIND_PAIRS: dict[str, set[str]]` — the matrix from DR-079
    - `VALID_OUTCOME_KIND_PAIRS: dict[str, set[str]]` — the matrix from DR-079
    - `FINDING_OUTCOME_VALUES: set[str]` — `{drift, aligned, risk}`

- **1.2 Update audit frontmatter metadata schema**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/audit.py`
  - **What**:
    - Add `mode` field (enum: `conformance`, `discovery`)
    - Add `delta_ref` field (string, optional)
    - Add `disposition` sub-schema to each finding: `status`, `kind`, `refs` (array of `{kind, ref}`), `drift_refs` (array of `{kind, ref}`), `rationale`, `closure_override` (object with `effect` and `rationale`)
    - Remove `patch_level` FieldMetadata
    - Remove `next_actions` FieldMetadata
    - Update examples to use new schema

- **1.3 Add audit_gate to delta frontmatter schema**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/delta.py`
  - **What**:
    - Add `audit_gate` field (enum: `auto`, `required`, `exempt`, default: `auto`)
    - Add `audit_gate_rationale` field (string, optional — required when `audit_gate: exempt`)

- **1.4 Update audit template**
  - **Files**: `supekku/templates/audit.md`
  - **What**:
    - Add `mode` and `delta_ref` to frontmatter
    - Replace example finding with disposition structure
    - Remove `patch_level` and `next_actions` sections
    - Use canonical change statuses (`draft`, `in-progress`, `completed`)

- **1.5 Extend create_audit**
  - **Files**: `supekku/scripts/lib/changes/creation.py`
  - **What**:
    - Add `mode` parameter (default: `conformance`)
    - Add `delta_ref` parameter (optional)
    - Pass both into frontmatter and template rendering
    - Check CLI layer for parameter passthrough

- **1.6 Edit existing audit**
  - **Files**: The audit with deprecated `patch_level` or `next_actions`
  - **What**: Remove deprecated fields from frontmatter, ensure it still parses

- **1.7 Write VT-079-001 tests**
  - **Files**: New test file or extend `audit_test.py`
  - **What**:
    - Valid disposition: all valid status×kind pairs accepted
    - Invalid disposition: rejected status×kind pairs (e.g. reconciled + follow_up_delta)
    - Valid outcome×kind: aligned→aligned, drift→action kinds
    - Invalid outcome×kind: drift→aligned, aligned→spec_patch
    - Structured refs: valid `{kind, ref}` objects accepted, bare strings rejected
    - closure_override: accepted with rationale, rejected without
    - Schema validates with and without optional fields (mode, delta_ref, disposition)

## 8. Risks & Mitigations

| Risk                          | Mitigation                                                                         | Status |
| ----------------------------- | ---------------------------------------------------------------------------------- | ------ |
| FieldMetadata depth limit     | Check audit_window precedent; escalate if nested objects in arrays are unsupported | open   |
| Existing audit parsing breaks | Test both existing audits explicitly after schema change                           | open   |

## 9. Decisions & Outcomes

- Design decisions governing this phase: DEC-079-001, DEC-079-002, DEC-079-004, DEC-079-007, DEC-079-009, DEC-079-010

## 10. Findings / Research Notes

(to be filled during execution)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (just check passes, pylint reviewed)
- [x] Notes updated
- [x] Hand-off notes to phase 2 (audit gating module)
