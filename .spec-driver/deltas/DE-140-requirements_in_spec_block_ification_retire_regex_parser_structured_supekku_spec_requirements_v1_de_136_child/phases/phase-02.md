---
id: IP-140-P02
slug: "140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child-phase-02"
name: "IP-140 Phase 02 — Block-first reading pipeline"
created: "2026-05-23"
updated: "2026-05-23"
status: draft
kind: phase
plan: IP-140
delta: DE-140
---

# Phase 02 — Block-first Reading Pipeline

## 1. Objective

Wire `extract_spec_requirements()` into the requirement parser so block-sourced requirements flow through the registry. Block path is authoritative when present; regex fallback for legacy specs. `source_kind` tracking for auditing.

## 2. Links & References

- **Delta**: DE-140
- **Design Revision**: DR-140 §5 (Reading Pipeline), §4 (Code Impact — modified files)
- **Specs**: PROD-004.FR-001, PROD-004.FR-002
- **Exemplars**:
  - Parser: `supekku/scripts/lib/requirements/parser.py`
  - Registry: `supekku/scripts/lib/requirements/registry.py`
  - Block infra (P01): `supekku/scripts/lib/blocks/spec_requirements.py`

## 3. Entrance Criteria

- [x] P01 complete — block extraction, validation, rendering all working
- [x] DR-140 §5 reviewed

## 4. Exit Criteria / Done When

- [x] `records_from_spec()` public API exists in parser.py
- [x] Block-first path: block present → records from block, no regex
- [x] Regex fallback: no block → existing regex path
- [x] `source_kind` set to `"block"` or `"prose"` per path
- [x] Breakout metadata merge runs regardless of source
- [x] RequirementRecord field mapping correct (lifecycle→status, kind canonicalized, UID derived)
- [x] Registry calls `records_from_spec()` instead of `_records_from_frontmatter()`
- [x] All 8 VTs passing (VT-140-009 through -014, -025, -026)
- [x] Existing requirement tests still pass (regression)
- [x] `just lint` clean on modified files

## 5. Verification

| VT | Description |
|----|-------------|
| VT-140-009 | Block-first — block present, regex not called |
| VT-140-010 | Regex fallback — no block, records from regex |
| VT-140-011 | Mutual exclusion — never both for same spec |
| VT-140-012 | RequirementRecord field mapping — lifecycle→status, kind, UID |
| VT-140-013 | Breakout metadata merge for both sources |
| VT-140-014 | source_kind tracking — block vs prose |
| VT-140-025 | Orphaned breakout files tolerated |
| VT-140-026 | Block-only fields (description, acceptance_criteria) absent from registry |

Commands: `just test`, `just lint`, `just pylint-files supekku/scripts/lib/requirements/parser.py supekku/scripts/lib/requirements/registry.py`

## 6. Assumptions & STOP Conditions

- Assumes `_records_from_content()` and `_load_breakout_metadata()` are stable
- Assumes RequirementRecord dataclass is unchanged (no new fields for block-only data)
- STOP if: registry `sync()` callers rely on `_records_from_frontmatter()` directly beyond what's shown

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 2.1 | Add `records_from_spec()` to parser.py — block-first with regex fallback | | Core change |
| [x] | 2.2 | Wire registry.py to call `records_from_spec()` | | After 2.1 |
| [x] | 2.3 | Write parser tests (VT-140-009, -010, -011, -012, -013, -014) | | After 2.1 |
| [x] | 2.4 | Write edge case tests (VT-140-025, -026) | | After 2.1 |
| [x] | 2.5 | Regression check — existing tests pass | | After all |
| [x] | 2.6 | Lint pass on modified files | | After all |

### Task Details

- **2.1 — records_from_spec()**
  - **Files**: `supekku/scripts/lib/requirements/parser.py` (MODIFY)
  - **Design**: DR-140 §5
  - **API**: `records_from_spec(spec_id, frontmatter, body, spec_path, repo_root, *, stats=None) -> Iterator[RequirementRecord]`
  - **Logic**:
    1. Try `extract_spec_requirements(body)` — None → regex, Block → block path, ValueError → log + regex fallback (pre-flip behavior)
    2. Block path: validate via `validate_spec_requirements()`, build RequirementRecord per entry (lifecycle→status, canonicalize kind, derive UID)
    3. Regex path: delegate to existing `_records_from_content()` with `source_kind="prose"`
    4. Breakout merge runs on both paths
    5. Set `source_kind` and `source_type` on records

- **2.2 — Registry wiring**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` (MODIFY)
  - **Change**: Replace `_records_from_frontmatter()` calls with `records_from_spec()`. Both spec-ingestion paths (via spec_registry and raw spec_dirs) must use same entrypoint.

- **2.3–2.4 — Tests**
  - Test file: new `supekku/scripts/lib/requirements/parser_block_test.py` or extend existing test
  - Mock/fixture specs with blocks vs prose-only
  - Verify mutual exclusion, field mapping, source_kind, breakout merge

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Breaking existing sync behavior | Run full test suite before/after | |
| Registry has multiple entry points for spec ingestion | Audit both paths in sync() | |

## 9. Decisions & Outcomes

(populated during execution)

## 10. Findings / Research Notes

(populated during execution)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to P03/P04/P05
