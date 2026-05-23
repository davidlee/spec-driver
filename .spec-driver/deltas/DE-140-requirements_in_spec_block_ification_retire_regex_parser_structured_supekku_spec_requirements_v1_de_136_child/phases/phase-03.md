---
id: IP-140-P03
slug: "140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child-phase-03"
name: "IP-140 Phase 03 — Validation & Template"
created: "2026-05-23"
updated: "2026-05-23"
status: in-progress
kind: phase
plan: IP-140
delta: DE-140
---

# Phase 03 — Validation & Template

## 1. Objective

Wire spec requirements block validation into WorkspaceValidator, update spec creation to emit empty requirements block, add template placeholder. Foundation for strict-flip enforcement in P05.

## 2. Links & References

- **Delta**: DE-140
- **Design Revision**: DR-140 §7 (Validation & Strict Flip — WorkspaceValidator Wiring)
- **Specs**: PROD-004.FR-001, PROD-004.FR-002
- **Exemplars**:
  - Validator: `supekku/scripts/lib/validation/validator.py` (`_validate_spec_blocks`, `_validate_delta_blocks`)
  - Spec creation: `supekku/scripts/lib/specs/creation.py`
  - Block infra (P01): `supekku/scripts/lib/blocks/spec_requirements.py`

## 3. Entrance Criteria

- [x] P01 complete — block extraction, validation, rendering all working
- [x] DR-140 §7 reviewed

## 4. Exit Criteria / Done When

- [ ] `_validate_spec_requirements_blocks()` wired into WorkspaceValidator
- [ ] Schema validation via `SPEC_REQUIREMENTS_VALIDATOR` with severity-preserving dispatch
- [ ] Spec field cross-validated against artifact ID
- [ ] Strict-mode: trimmed-empty description and blank acceptance_criteria items rejected
- [ ] Spec creation emits empty requirements block (DEC-140-14)
- [ ] Template includes `{{ spec_requirements_block }}` placeholder
- [ ] All 6 VTs passing (VT-140-015, -016, -019, -020, -022, -030)
- [ ] `just lint` clean on modified files
- [ ] `just pylint-files` clean on modified files

## 5. Verification

| VT | Description |
|----|-------------|
| VT-140-015 | WorkspaceValidator — requirements block validated |
| VT-140-016 | WorkspaceValidator — spec field cross-validated |
| VT-140-019 | Spec creation — empty requirements block emitted |
| VT-140-020 | Template includes block placeholder |
| VT-140-022 | Trimmed-empty description and blank acceptance_criteria items rejected |
| VT-140-030 | Scaffolded spec with empty block creates no registry entries |

Commands: `just test`, `just lint`, `just pylint-files supekku/scripts/lib/validation/validator.py supekku/scripts/lib/specs/creation.py`

## 6. Assumptions & STOP Conditions

- Assumes `_validate_spec_blocks()` pattern is the correct model for requirements block validation
- Assumes `SPEC_REQUIREMENTS_VALIDATOR` returns `ValidationError` objects with `.severity`
- STOP if: `validate_spec_requirements()` needs API change to support WorkspaceValidator severity dispatch
- STOP if: template system doesn't support additional block variables cleanly

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 3.1 | Add `_validate_spec_requirements_blocks()` to WorkspaceValidator | | Core validation wiring |
| [ ] | 3.2 | Update `creation.py` to emit empty requirements block | [P] | DEC-140-14 |
| [ ] | 3.3 | Add `{{ spec_requirements_block }}` to template | [P] | After 3.2 |
| [ ] | 3.4 | Write validation tests (VT-140-015, -016, -022) | | After 3.1 |
| [ ] | 3.5 | Write creation/template tests (VT-140-019, -020, -030) | | After 3.2/3.3 |
| [ ] | 3.6 | Lint pass on modified files | | After all |

### Task Details

- **3.1 — _validate_spec_requirements_blocks()**
  - **Files**: `supekku/scripts/lib/validation/validator.py` (MODIFY)
  - **Design**: DR-140 §7
  - **Logic**:
    1. Iterate specs via `self.workspace.specs.all_specs()`
    2. Extract block via `extract_spec_requirements(body)`
    3. ValueError → error
    4. None → no action (pre-flip; post-flip behavior added in P05)
    5. Block present → schema validate via `SPEC_REQUIREMENTS_VALIDATOR.validate()` → `_block_issue()`
    6. Cross-validate `spec` field against artifact ID → error on mismatch
    7. Strict-mode: reject trimmed-empty description, blank acceptance_criteria items

- **3.2 — Spec creation update**
  - **Files**: `supekku/scripts/lib/specs/creation.py` (MODIFY)
  - **Design**: DEC-140-14 — empty block, not sample FR-001
  - **Change**: Import `render_spec_requirements_block`, call with `requirements=None`, pass to template

- **3.3 — Template update**
  - **Files**: `supekku/templates/spec.md` (MODIFY)
  - **Change**: Add `{{ spec_requirements_block }}` variable in section 3

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Validator return type mismatch (str vs ValidationError) | Use VALIDATOR.validate() for schema + inline for custom checks | |
| Template variable rendering order | Follow existing block variable pattern | |

## 9. Decisions & Outcomes

(populated during execution)

## 10. Findings / Research Notes

(populated during execution)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to P04/P05
