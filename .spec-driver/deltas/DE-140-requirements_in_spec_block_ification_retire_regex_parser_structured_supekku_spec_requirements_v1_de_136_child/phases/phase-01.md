---
id: IP-140-P01
slug: "140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child-phase-01"
name: "IP-140 Phase 01 — Block Infrastructure"
created: "2026-05-23"
updated: "2026-05-23"
status: completed
kind: phase
plan: IP-140
delta: DE-140
---

# Phase 01 — Block Infrastructure

## 1. Objective

Create `supekku:spec.requirements@v1` block infrastructure: parser module, metadata definition, validation wrapper, schema registration. Foundation for all subsequent phases.

## 2. Links & References

- **Delta**: DE-140
- **Design Revision**: DR-140 §3 (Block Schema), §4 (Code Impact — new files)
- **Specs**: PROD-004.FR-001, PROD-004.FR-002
- **Exemplars**:
  - Block parser: `supekku/scripts/lib/blocks/verification.py`
  - Metadata: `supekku/scripts/lib/blocks/verification_metadata.py`
  - Spec metadata: `supekku/scripts/lib/blocks/spec_metadata.py`

## 3. Entrance Criteria

- [x] DR-140 accepted and reviewed
- [x] DE-118 (block schema unification) completed
- [x] DE-137 (cross-cutting infrastructure) completed

## 4. Exit Criteria / Done When

- [x] `spec_requirements.py` extracts and renders blocks correctly
- [x] `spec_requirements_metadata.py` validates all field constraints
- [x] Cross-field invariant (ID prefix ↔ kind) enforced
- [x] Duplicate ID detection working
- [x] Duplicate block detection working
- [x] Tolerated aliases (`FR`/`NF`/`NFR`) canonicalize correctly
- [x] Schema registered in block schema registry
- [x] All 11 VTs passing (VT-140-001 through -008, -027, -028)
- [x] `just lint` clean on new files
- [x] `just pylint-files` clean on new files

## 5. Verification

| VT | Description |
|----|-------------|
| VT-140-001 | Block extraction — valid block parses to SpecRequirementsBlock |
| VT-140-002a | No block → returns None |
| VT-140-002b | Malformed YAML → raises ValueError |
| VT-140-003 | Required fields enforced |
| VT-140-004 | Enum constraints (lifecycle, kind) |
| VT-140-005 | Tolerated aliases canonicalized with sunset |
| VT-140-006 | Cross-field invariant — ID prefix matches kind |
| VT-140-007 | Renderer produces valid parseable block YAML |
| VT-140-008 | Schema registry — registered with marker/version/renderer linkage |
| VT-140-027 | Duplicate IDs within block → hard error |
| VT-140-028 | Multiple blocks in one file → hard error |

Commands: `just test`, `just lint`, `just pylint-files supekku/scripts/lib/blocks/spec_requirements.py supekku/scripts/lib/blocks/spec_requirements_metadata.py`

## 6. Assumptions & STOP Conditions

- Assumes existing `BlockMetadata` / `MetadataValidator` / `ToleratedAlias` infrastructure is stable (DE-118/137 completed)
- Assumes `make_block_pattern()` and `register_block_schema()` APIs are unchanged
- STOP if: cross-field invariant requires `ConditionalRule` changes to metadata engine (DR-140 DEC-140-10 says custom wrapper instead)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 1.1 | Create `spec_requirements.py` — constants, dataclass, extract, render | [P] | Follow verification.py pattern |
| [x] | 1.2 | Create `spec_requirements_metadata.py` — BlockMetadata, validator, wrapper | [P] | Follow verification_metadata.py + spec_metadata.py pattern |
| [x] | 1.3 | Write extraction tests (VT-140-001, -002a, -002b, -028) | | After 1.1 |
| [x] | 1.4 | Write metadata/validation tests (VT-140-003, -004, -005, -006, -027) | | After 1.2 |
| [x] | 1.5 | Write renderer test (VT-140-007) | | After 1.1 |
| [x] | 1.6 | Write schema registration test (VT-140-008) | | After 1.1 |
| [x] | 1.7 | Lint pass on new files | | After all |

### Task Details

- **1.1 — spec_requirements.py**
  - **Files**: `supekku/scripts/lib/blocks/spec_requirements.py` (NEW)
  - **Design**: DR-140 §3 — marker `supekku:spec.requirements@v1`, schema `supekku.spec.requirements`, version `1`
  - **Components**:
    - Constants: `REQUIREMENTS_MARKER`, `REQUIREMENTS_SCHEMA`, `REQUIREMENTS_VERSION`
    - `SpecRequirementsBlock` frozen dataclass with `raw_yaml: str`, `data: dict[str, Any]`
    - `_REQUIREMENTS_PATTERN = make_block_pattern(REQUIREMENTS_MARKER)`
    - `extract_spec_requirements(text: str) -> SpecRequirementsBlock | None` — returns None if no block, raises ValueError on malformed YAML. Must detect and error on duplicate blocks.
    - `load_spec_requirements(path: Path) -> SpecRequirementsBlock | None`
    - `render_spec_requirements_block(spec_id: str, *, requirements: list[dict] | None = None) -> str`
    - `register_block_schema()` call at module level

- **1.2 — spec_requirements_metadata.py**
  - **Files**: `supekku/scripts/lib/blocks/spec_requirements_metadata.py` (NEW)
  - **Design**: DR-140 §3 — field definitions, tolerated aliases, cross-field invariant
  - **Components**:
    - `REQUIREMENT_ID_PATTERN = r"^(FR|NF)-\d{3}$"`
    - `SPEC_OWNER_PATTERN = r"^(SPEC|PROD)-\d{3,}$"`
    - `SPEC_REQUIREMENTS_METADATA` — BlockMetadata with all fields per DR-140 §3 table
    - `SPEC_REQUIREMENTS_VALIDATOR = MetadataValidator(SPEC_REQUIREMENTS_METADATA)`
    - `validate_spec_requirements(block, *, spec_id=None, strict=False, accept_tolerated=True) -> list[str]` — canonical validation entry point. Calls validator, then applies:
      - Cross-field invariant: `FR-*` ↔ `functional`, `NF-*` ↔ `non-functional`
      - Duplicate ID check within `requirements` array
      - Optional `spec_id` cross-validation
    - `ToleratedAlias` entries for `kind`: `FR` → `functional`, `NF`/`NFR` → `non-functional`, `sunset_after: "DE-140"`

- **1.3–1.6 — Tests**
  - Test file: `supekku/scripts/lib/blocks/spec_requirements_test.py` (NEW)
  - Or split: `spec_requirements_test.py` + `spec_requirements_metadata_test.py`
  - Test valid extraction, None return, ValueError, renderer round-trip, registry entry, all validation rules, aliases, invariant, duplicates

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Cross-field invariant doesn't fit metadata engine | DEC-140-10: custom wrapper, not ConditionalRule | Mitigated |
| ToleratedAlias sunset semantics unclear | Follow DE-118/137 precedent exactly | |

## 9. Decisions & Outcomes

- DEC-140-10: Cross-field invariant in custom wrapper
- DEC-140-15: Duplicate IDs and duplicate blocks are hard errors
- DEC-140-16: validate_spec_requirements() is canonical validation surface

## 10. Findings / Research Notes

(populated during execution)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Hand-off notes to P02/P03/P04
