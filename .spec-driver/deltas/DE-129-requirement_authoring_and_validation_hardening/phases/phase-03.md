---
id: IP-129-P03
slug: "129-requirement_authoring_and_validation_hardening-phase-03"
name: "IP-129 Phase 03 — Validator, show, and memory"
created: "2026-03-28"
updated: "2026-03-28"
status: completed
kind: phase
plan: IP-129
delta: DE-129
---

# Phase 3 — Validator, Show, and Memory

## 1. Objective

Add three validator checks (bare-ID warning, implements-target-kind, revision-introduced invariant), zero-entry hint in `show spec`, and memory update. Close out DE-129.

## 2. Links & References

- **Delta**: DE-129
- **Design Revision Sections**: DR-129 §1.4, §1.5, §1.6, §1.7, §1.9
- **Specs / PRODs**: SPEC-122.FR-003, SPEC-125 (validation)
- **Support Docs**: `supekku/scripts/lib/validation/validator.py`, `supekku/cli/show.py`

## 3. Entrance Criteria

- [ ] Phase 2 complete (sync pruning working, `source_type` stamp in place)
- [ ] All sync tests passing

## 4. Exit Criteria / Done When

- [x] `_BARE_REQUIREMENT_PATTERN` and `_SPEC_ID_PATTERN` constants added
- [x] Bare-ID warning in `_validate_change_relations()` applies_to loop (all artifact types)
- [x] Implements-target-kind check fires before generic "not found" error
- [x] Revision-introduced invariant check (source_type=revision + no introduced → warning)
- [x] `show spec` zero-entry hint when registry has 0 requirements
- [x] `mem.concept.spec-driver.requirement-lifecycle` updated with Common Pitfalls
- [x] All validator and show tests pass
- [x] `just check` fully clean (all pre-existing; no new issues)
- [x] DE-129 acceptance criteria satisfied

## 5. Verification

- `uv run pytest supekku/scripts/lib/validation/validator_test.py -v`
- `uv run pytest supekku/cli/ -v -k show` (if show tests exist)
- `uv run spec-driver sync && uv run spec-driver validate` (integration smoke test)
- `just check`

## 6. Assumptions & STOP Conditions

- Assumptions: `re` is not already imported in `validator.py` (confirmed during review). `source_type` field persisted to registry YAML (confirmed — on `RequirementRecord`).
- STOP when: If `source_type` is not being persisted to registry YAML, fix in phase 2 first.

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 3.1 | Add `_BARE_REQUIREMENT_PATTERN` and `_SPEC_ID_PATTERN` constants | [P] | validator.py |
| [x] | 3.2 | Bare-ID warning in applies_to loop | [P] | DR §1.4; all artifact types (ext. review F11) |
| [x] | 3.3 | Implements-target-kind check | [P] | DR §1.5; guard clause before existence check |
| [x] | 3.4 | Revision-introduced invariant check | [P] | DR §1.6; depends on source_type stamp from phase 2 |
| [x] | 3.5 | Zero-entry hint in `show spec` | [P] | DR §1.7; no parser import needed |
| [x] | 3.6 | Memory update — Common Pitfalls section | [P] | DR §1.9 |
| [x] | 3.7 | Unit tests for 3.1–3.5 | | 14 new tests, all passing |
| [x] | 3.8 | Integration smoke: sync → validate → show | | Confirmed clean |
| [x] | 3.9 | Lint + full test pass | | 4711 passed, ruff clean |

### Task Details

- **3.2 Bare-ID warning**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **Approach**: In the `applies_to` loop of `_validate_change_relations()`, before the existence check: if `req` matches `_BARE_REQUIREMENT_PATTERN` (no `.`), emit warning. No `expected_type` gate — fires for deltas, revisions, and audits alike.
  - **Testing**: (a) `FR-013` → warning; (b) `SPEC-012.FR-013` → no warning; (c) `ISSUE-050` → no warning (not requirement-shaped)

- **3.3 Implements-target-kind**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **Approach**: In the relation loop, before `if target not in requirement_ids`: if `rel_type == exp` and target matches `_SPEC_ID_PATTERN`, emit specific warning and `continue` (skip generic error).
  - **Testing**: (a) `implements → SPEC-012` → specific warning; (b) `implements → SPEC-012.FR-001` → normal; (c) `relates_to → SPEC-012` → no warning

- **3.4 Revision-introduced invariant**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **Approach**: In the requirement lifecycle loop (already iterating `requirements.records`), check: if `record.source_type == "revision" and not record.introduced`, emit warning.
  - **Testing**: (a) source_type=revision + introduced=RE-005 → no warning; (b) source_type=revision + introduced=None → warning; (c) source_type="" → no warning

- **3.5 Zero-entry hint**
  - **Files**: `supekku/cli/show.py`, `supekku/scripts/lib/formatters/spec_formatters.py`
  - **Approach**: After computing `fr_count + nf_count + other_req_count`, if total is 0, pass `registry_empty_hint=True` to formatter. Formatter appends info note.
  - **Testing**: (a) 0 entries → hint; (b) ≥1 entry → no hint

- **3.6 Memory update**
  - **Files**: `.spec-driver/memory/mem.concept.spec-driver.requirement-lifecycle.md`
  - **Approach**: Add Common Pitfalls section per DR §1.9. Update `verified` date.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| `re` import adds to validator module | Single stdlib import, minimal | Accepted |
| `source_type` not persisted to YAML | Verified field exists on `RequirementRecord`; confirm during impl | Open |

## 9. Decisions & Outcomes

- 2026-03-28 — Bare-ID check fires for all artifact types (ext. review F11)
- 2026-03-28 — Zero-entry hint instead of body-count cross-check (ext. review F2)

## 10. Findings / Research Notes

(To be filled during implementation)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated
- [x] DE-129 acceptance criteria cross-checked
- [x] Delta ready for close
