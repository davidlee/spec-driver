---
id: IP-141-P01
slug: "141-audit_artefact_metadata_propagation_findings_block_strict_outcome_enum_list_enrichment_de_136_child-phase-01"
name: "IP-141 Phase 01 — Block schema, canonical loader, ChangeArtifact model"
created: "2026-05-28"
updated: "2026-05-28"
status: completed
kind: phase
plan: IP-141
delta: DE-141
---

# Phase 1 — Block schema, canonical loader, ChangeArtifact model

## 1. Objective

Deploy `supekku:audit.findings@v1` block infrastructure: render, extract, canonical dual-path loader, block schema registration, and `ChangeArtifact` model extension with `mode`/`delta_ref` fields. This phase produces no user-visible changes but establishes the foundation all subsequent phases build on.

## 2. Links & References

- **Delta**: DE-141
- **Design Revision**: DR-141 §3.1–§3.3 (block schema + parser + loader), DEC-141-06, DEC-141-07
- **Specs / PRODs**: PROD-004.FR-001
- **Precedent**: `supekku/scripts/lib/blocks/spec_requirements.py`, `blocks/delta_relationships.py`
- **Exemplars**: existing block extractors for return type, error handling, registration pattern

## 3. Entrance Criteria

- [x] DR-141 authored and adversarially reviewed
- [x] IP-141 created with phase overview
- [x] DE-141 status set to `in-progress`

## 4. Exit Criteria / Done When

- [x] `render_audit_findings_block()` produces valid code-fenced block
- [x] `extract_audit_findings()` parses block from body; raises on duplicates/malformed/mismatch
- [x] `load_audit_findings()` canonical loader: block-first, FM-fallback
- [x] Block schema registered in block registry
- [x] `ChangeArtifact` has optional `mode`, `delta_ref` fields; populated from FM at load
- [x] VT-141-BLOCK-001 through -004 and VT-141-TRANSITION-001/-002 passing (20 tests)
- [x] All existing tests still pass (5209 passed)
- [x] Lint clean

## 5. Verification

- `uv run python -m pytest supekku/scripts/lib/blocks/audit_findings_test.py -x`
- `uv run python -m pytest supekku/scripts/lib/changes/artifacts_test.py -x` (if exists)
- `uv run python -m pytest supekku -x -q` (full suite)
- `uv run ruff check supekku/scripts/lib/blocks/audit_findings.py supekku/scripts/lib/changes/artifacts.py`

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - Existing block patterns (spec_requirements, delta_relationships) are the right template
  - `ChangeArtifact` can grow optional fields without breaking downstream (default None)
  - Block schema registry follows import side-effect pattern
- **STOP when**:
  - Block registry mechanism differs from assumed pattern → investigate before proceeding
  - `ChangeArtifact` changes break registry serialization → consult

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 1.1 | Create `blocks/audit_findings.py`: render + extract + register | [ ] | DR-141 §3.1–§3.2 |
| [x] | 1.2 | Add `load_audit_findings()` canonical dual-path loader | [ ] | DR-141 §3.2, DEC-141-06 |
| [x] | 1.3 | Extend `ChangeArtifact` with `mode`, `delta_ref` fields | [P] | DR-141 §5.0, DEC-141-07 |
| [x] | 1.4 | Write tests: VT-141-BLOCK-001..004, VT-141-TRANSITION-001..002 | [ ] | After 1.1 + 1.2 |
| [x] | 1.5 | Full test suite + lint pass | [ ] | Gate: 5209 passed, ruff clean |

### Task Details

- **1.1 Create `blocks/audit_findings.py`**
  - **Design / Approach**: Follow `blocks/spec_requirements.py` pattern. `AUDIT_FINDINGS_MARKER = "supekku:audit.findings@v1"`. Regex detection, YAML parse, typed return. Duplicate blocks → `ValueError`. Malformed YAML → `ValueError`. Block `audit` field != artifact id → `ValueError`. Register in block schema registry via module-level side-effect.
  - **Files**: `supekku/scripts/lib/blocks/audit_findings.py` (NEW)
  - **Testing**: VT-141-BLOCK-001 (round-trip), -002 (empty), -003 (errors), -004 (id mismatch)

- **1.2 Add `load_audit_findings()`**
  - **Design / Approach**: Canonical loader in same module. Signature: `load_audit_findings(body: str, fm: dict | None = None) -> list[dict]`. Try `extract_audit_findings(body)` first → return findings list. If None and `fm` provided → return `fm.get("findings", [])`. This is the single entry point all callers will use.
  - **Files**: `supekku/scripts/lib/blocks/audit_findings.py` (extend)
  - **Testing**: VT-141-TRANSITION-001 (block wins), -002 (FM fallback)

- **1.3 Extend `ChangeArtifact`**
  - **Design / Approach**: Add `mode: str | None = None` and `delta_ref: str | None = None` to dataclass. In `load_change_artifact()`, populate from FM: `mode=str(frontmatter.get("mode", "")).strip() or None`, same for `delta_ref`. Add to `to_dict()` conditionally.
  - **Files**: `supekku/scripts/lib/changes/artifacts.py` (MODIFY)
  - **Testing**: Existing artifact tests + new case for audit artifact with mode/delta_ref

- **1.4 Write tests**
  - **Files**: `supekku/scripts/lib/blocks/audit_findings_test.py` (NEW)
  - **Testing**: 6 VTs covering block round-trip, empty, errors, mismatch, dual-path loader

- **1.5 Full test suite + lint**
  - **Testing**: `uv run python -m pytest supekku -x -q` + `uv run ruff check supekku`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Block registry pattern differs from assumed | Check spec_requirements.py registration first | resolved — pattern confirmed |
| ChangeArtifact serialization changes break registry | to_dict only adds fields when non-None | resolved — tests pass |

## 9. Decisions & Outcomes

- Followed spec_requirements.py pattern (single-block-per-module, frozen dataclass)
- `validate_audit_field()` as standalone function (not embedded in extract) per block-class-data-taxonomy memory
- `_yaml_str()` helper handles special YAML characters in rendered output

## 10. Findings / Research Notes

- Block registry registration pattern: import at module bottom with `# noqa: E402`, same as spec_requirements.py
- `yaml.dump()` appends `\n...\n` to some strings — stripped in `_yaml_str()`
- Disposition refs rendered as proper YAML list (not inline flow-style) to avoid parse errors
- No audit_findings_metadata.py needed for P01 — metadata=None in schema registration; P03 (strict enforcement) will add if needed
- Commit: `05cc140e`

## 11. Wrap-up Checklist

- [x] Exit criteria (§4) satisfied
- [x] Verification evidence stored (20 tests, 5209 suite, ruff clean)
- [x] Hand-off notes for P02/P03: P01 block module ready, `load_audit_findings()` available for caller migration. P02 (list enrichment) and P03 (strict enforcement) can proceed in parallel.
