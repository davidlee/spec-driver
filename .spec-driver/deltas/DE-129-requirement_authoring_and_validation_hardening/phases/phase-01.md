---
id: IP-129-P01
slug: "129-requirement_authoring_and_validation_hardening-phase-01"
name: IP-129 Phase 01 — Parser hardening
created: "2026-03-28"
updated: "2026-03-28"
status: completed
kind: phase
plan: IP-129
delta: DE-129
---

# Phase 1 — Parser Hardening

## 1. Objective

Add three diagnostic capabilities to the requirement parser: frontmatter requirements detection, ID collision detection, and mismatch threshold relaxation. Expose `count_requirement_like_lines()` as public API. All changes are in `requirements/parser.py` with unit tests.

## 2. Links & References

- **Delta**: DE-129
- **Design Revision Sections**: DR-129 §1.1, §1.2
- **Specs / PRODs**: SPEC-122.FR-004 (extraction pattern)
- **Support Docs**: `mem.concept.spec-driver.requirement-lifecycle`

## 3. Entrance Criteria

- [x] DR-129 approved (two adversarial passes)
- [x] IP-129 phase overview agreed

## 4. Exit Criteria / Done When

- [x] `_has_frontmatter_requirement_definitions()` implemented and tested
- [x] Collision detection via `seen_uids` tracking implemented and tested
- [x] Mismatch threshold changed from `== 0` to `<` and tested
- [x] `count_requirement_like_lines()` public API added and tested
- [x] All existing parser tests still pass (30/30)
- [x] Lint clean (ruff check + format)

## 5. Verification

- `uv run pytest supekku/scripts/lib/requirements/parser_test.py -v`
- `just check` (lint on changed files)
- Evidence: test output in notes

## 6. Assumptions & STOP Conditions

- Assumptions: `_records_from_content` generator interface does not need to change (collision tracking is internal state)
- STOP when: if `SyncStats` passing is needed for warning counting in this phase (it should be phase 2 — parser changes here use `logger` only)

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 1.1 | `_has_frontmatter_requirement_definitions()` helper | [P] | DR §1.1 |
| [x] | 1.2 | Wire frontmatter check into `_records_from_frontmatter()` | | After 1.1 |
| [x] | 1.3 | Collision tracking in `_records_from_content()` | [P] | DR §1.2 |
| [x] | 1.4 | Mismatch threshold: `== 0` → `<` | [P] | One-line change |
| [x] | 1.5 | `count_requirement_like_lines()` public API | [P] | DR §1.7 (retained for future use) |
| [x] | 1.6 | Unit tests for all new behaviour | | 15 new tests, all passing |
| [x] | 1.7 | Lint + existing test pass | | 45/45 pass, ruff clean |

### Task Details

- **1.1 `_has_frontmatter_requirement_definitions()`**
  - **Files**: `supekku/scripts/lib/requirements/parser.py`
  - **Approach**: Pure function, takes `Mapping`, returns `list[dict]`. Checks for `requirements:` key that is a list of dicts with `id` or `description` keys.
  - **Testing**: (a) list of dicts with `id` → returns entries; (b) dict with `primary`/`collaborators` → returns []; (c) no key → returns []

- **1.2 Wire frontmatter check**
  - **Files**: `supekku/scripts/lib/requirements/parser.py`
  - **Approach**: Call helper in `_records_from_frontmatter()` before delegating to `_records_from_content()`. Log at `logger.info()` with actionable message (per DR §1.8 log discipline — per-item diagnostics at info, not warning).
  - **Testing**: Integration with `_records_from_frontmatter` — verify log output via `caplog`

- **1.3 Collision tracking**
  - **Files**: `supekku/scripts/lib/requirements/parser.py`
  - **Approach**: Add `seen_uids: dict[str, str]` (uid → source line) inside `_records_from_content()`. Before yielding, check if uid already in seen_uids. If so, log collision at `logger.info()` with both lines and compound-ID guidance.
  - **Testing**: (a) two lines → same UID → warning + both lines; (b) sequential IDs → no warning; (c) compound IDs → collision with guidance message

- **1.4 Mismatch threshold**
  - **Files**: `supekku/scripts/lib/requirements/parser.py`
  - **Approach**: Change `if requirement_like_lines and extracted_count == 0:` to `if requirement_like_lines and extracted_count < len(requirement_like_lines):`
  - **Testing**: (a) 19 like-lines, 1 extracted → warning; (b) 3 like-lines, 3 extracted → no warning

- **1.5 `count_requirement_like_lines()`**
  - **Files**: `supekku/scripts/lib/requirements/parser.py`
  - **Approach**: Public function `count_requirement_like_lines(body: str) -> int` that counts lines passing `_is_requirement_like_line()`. Add to `__all__` or module exports if applicable.
  - **Testing**: Basic count test with mixed definition and cross-reference lines

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Collision detection changes generator yield semantics | It doesn't — still yields all records, just logs on duplicates | Mitigated by design |

## 9. Decisions & Outcomes

- 2026-03-28 — Per-item diagnostics at `logger.info()` level (DR §1.8, ext. review F3)

## 10. Findings / Research Notes

- Collision detection: the generator still yields duplicate records (doesn't suppress them). This is correct — the caller's dict handles dedup via overwrite. The warning is purely diagnostic.
- Mismatch threshold change: `extracted_count < len(requirement_like_lines)` naturally handles the old `== 0` case and also catches partial-extraction scenarios.
- Frontmatter detection wired at `logger.info()` per DR §1.8 log-level discipline.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 45/45 tests pass, ruff clean
- [x] Notes updated
- [ ] Hand-off notes to phase 2
