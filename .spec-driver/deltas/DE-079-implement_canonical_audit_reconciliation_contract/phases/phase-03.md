---
id: IP-079.PHASE-03
slug: 079-implement_canonical_audit_reconciliation_contract-phase-03
name: IP-079 Phase 03 — Validation rules
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-079.PHASE-03
plan: IP-079
delta: DE-079
objective: >-
  Add audit-specific validation rules to WorkspaceValidator: missing required
  audit for qualifying deltas, undispositioned findings, invalid status×kind
  and outcome×kind pairs, closure_override without rationale, and finding ID
  collisions across multi-audit unions. Surface via spec-driver validate.
entrance_criteria:
  - Phase 2 complete — audit_check.py landed with gate resolution and closure-effect derivation
exit_criteria:
  - _validate_audit_disposition method added to WorkspaceValidator
  - _validate_audit_gate_coverage method added to WorkspaceValidator
  - Missing required audit for qualifying delta surfaces as warning
  - Findings without disposition surface as warning
  - Invalid status×kind pairs surface as error
  - Invalid outcome×kind pairs surface as error
  - closure_override without rationale surfaces as error
  - Finding ID collisions across multi-audit union surface as warning
  - VA-079-003 schema review confirms validation output covers all audit issues
  - Both linters clean on all touched files
verification:
  tests: []
  evidence:
    - VA-079-003
tasks:
  - id: "3.1"
    description: Add _validate_audit_disposition to WorkspaceValidator
  - id: "3.2"
    description: Add _validate_audit_gate_coverage to WorkspaceValidator
  - id: "3.3"
    description: Write validation tests
risks:
  - description: Validator test setup may need extensive mocking for audit frontmatter
    mitigation: Reuse patterns from existing validator_test.py
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-079.PHASE-03
```

# Phase 3 — Validation Rules

## 1. Objective

Add audit-specific validation rules to `WorkspaceValidator` so that `spec-driver validate` surfaces audit disposition issues (invalid pairs, missing dispositions, missing audits for qualifying deltas, and multi-audit collisions).

## 2. Links & References

- **Delta**: DE-079
- **Design Revision**: DR-079 §4 (valid status×kind pairs, valid outcome×kind pairs, closure-effect derivation rules)
- **Design Decisions**: DEC-079-007 (status×kind validity), DEC-079-009 (outcome×kind validity), DEC-079-003 (audit_gate)
- **Specs**: SPEC-125 (validation), PROD-008
- **Pattern**: Existing `_validate_change_relations`, `_validate_spec_taxonomy` methods in `validator.py`

## 3. Entrance Criteria

- [x] Phase 2 complete — audit_check.py landed

## 4. Exit Criteria / Done When

- [ ] `_validate_audit_disposition` checks each audit's findings for:
  - Findings without disposition → warning
  - Invalid status×kind pairs → error
  - Invalid outcome×kind pairs → error
  - `closure_override` without rationale → error
- [ ] `_validate_audit_gate_coverage` checks each qualifying delta for:
  - Missing conformance audit → warning
  - Finding ID collisions across multi-audit union → warning
- [ ] Tests cover all validation rules
- [ ] `spec-driver validate` surfaces audit issues in output
- [ ] `just lint` clean
- [ ] `just pylint-files` clean on touched files

## 5. Verification

- `uv run pytest supekku/scripts/lib/validation/validator_test.py -v`
- `just lint`
- `just pylint-files supekku/scripts/lib/validation/validator.py supekku/scripts/lib/validation/validator_test.py`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Audit frontmatter is accessible via `load_markdown_file` on audit paths (confirmed in phase 2)
  - The constants from `audit.py` (VALID_STATUS_KIND_PAIRS, VALID_OUTCOME_KINDS) are the source of truth for validation
  - `resolve_audit_gate` from `audit_check.py` can be reused for gate resolution
- STOP when:
  - Validator's existing test fixtures conflict with new audit validation (unlikely given additive approach)

## 7. Tasks & Progress

| Status | ID  | Description                        | Parallel? | Notes                  |
| ------ | --- | ---------------------------------- | --------- | ---------------------- |
| [ ]    | 3.1 | Add \_validate_audit_disposition   | [ ]       | Per-finding validation |
| [ ]    | 3.2 | Add \_validate_audit_gate_coverage | [P]       | Per-delta check        |
| [ ]    | 3.3 | Write validation tests             | [ ]       | Depends on 3.1, 3.2    |

### Task Details

- **3.1 \_validate_audit_disposition**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **What**: For each completed audit, load raw frontmatter, iterate findings. Check:
    - Finding has no `disposition` → warning (undispositioned finding)
    - `disposition.status` × `disposition.kind` not in VALID_STATUS_KIND_PAIRS → error
    - `finding.outcome` × `disposition.kind` not in VALID_OUTCOME_KINDS → error
    - `disposition.closure_override` present but missing `rationale` → error
  - **Imports**: VALID_STATUS_KIND_PAIRS, VALID_OUTCOME_KINDS from audit.py; load_markdown_file from spec_utils

- **3.2 \_validate_audit_gate_coverage**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **What**: For each delta, resolve audit_gate. If required, check whether a completed conformance audit with matching delta_ref exists. If not → warning. If multiple audits exist, check for finding ID collisions → warning.
  - **Imports**: resolve_audit_gate from audit_check.py

- **3.3 Tests**
  - **Files**: `supekku/scripts/lib/validation/validator_test.py`
  - **What**: Test each validation rule: undispositioned finding, invalid status×kind, invalid outcome×kind, closure_override without rationale, missing required audit, finding ID collisions.

## 8. Risks & Mitigations

| Risk                              | Mitigation                                   | Status |
| --------------------------------- | -------------------------------------------- | ------ |
| Test fixture complexity           | Follow existing validator_test.py patterns   | open   |
| Validation noise on legacy audits | Only validate completed audits with findings | open   |

## 9. Decisions & Outcomes

- Design decisions governing this phase: DEC-079-003, DEC-079-007, DEC-079-009

## 10. Findings / Research Notes

- `WorkspaceValidator` already loads `audit_registry` at line 42 — no new registry access needed
- Existing pattern: add private `_validate_*` method, call from `validate()`
- `audit_registry.collect()` returns `dict[str, ChangeArtifact]` — need `load_markdown_file(artifact.path)` for raw frontmatter

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to phase 4 (skill rewrite)
