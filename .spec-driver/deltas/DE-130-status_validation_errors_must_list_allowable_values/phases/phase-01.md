---
id: IP-130-P01
slug: "130-status_validation_errors_must_list_allowable_values-phase-01"
name: IP-130 Phase 01 – patch status validation messages
created: "2026-04-10"
updated: "2026-04-10"
status: draft
kind: phase
plan: IP-130
delta: DE-130
---

# Phase 01 – Patch status validation messages to enumerate allowable values

## 1. Objective

Fix three status-rejection messages that omit the set of allowable values, so every message tells the caller exactly what values are accepted.

## 2. Links & References

- **Delta**: DE-130
- **Design Revision**: DR-130 § Code Impact Summary
- **Files**: `requirements/coverage.py`, `validation/validator.py`, `changes/completion.py`

## 3. Entrance Criteria

- [x] DR-130 approved
- [x] Three affected call sites confirmed (no others outstanding)

## 4. Exit Criteria / Done When

- [ ] All three messages include allowable values derived from the in-scope constant
- [ ] `just test` passes with no failures
- [ ] `just lint` passes with zero warnings

## 5. Verification

- `just test` — confirm no regressions; assertions on old message text updated
- `just lint` — zero warnings on edited files

## 6. Assumptions & STOP Conditions

- Assumptions: no callers parse these message strings for programmatic use (they are user-facing warnings/errors only)
- STOP when: any message string is parsed/matched programmatically outside tests — raise with user before changing

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|---|---|---|---|---|
| [ ] | 1.1 | Fix `coverage.py` warning | [ ] | Append `; valid: {sorted(VALID_COVERAGE_STATUSES)}` |
| [ ] | 1.2 | Fix `validator.py` phase status warning | [ ] | Append `; valid: {sorted(valid_statuses)}` |
| [ ] | 1.3 | Fix `completion.py` delta status error | [ ] | Derive from `valid_statuses` set |
| [ ] | 1.4 | Update any test assertions on old message text | [ ] | Run tests first to find breakages |
| [ ] | 1.5 | Lint and full test run | [ ] | `just` |

### Task Details

- **1.1 coverage.py** (`supekku/scripts/lib/requirements/coverage.py:148`)
  - Append `f"; valid: {sorted(VALID_COVERAGE_STATUSES)}"` to the f-string continuation.
  - `VALID_COVERAGE_STATUSES` already imported.

- **1.2 validator.py** (`supekku/scripts/lib/validation/validator.py:552`)
  - Change `f"Non-canonical phase status: '{status}'"` → `f"Non-canonical phase status: '{status}'; valid: {sorted(valid_statuses)}"`.
  - `valid_statuses` is the parameter already in scope.

- **1.3 completion.py** (`supekku/scripts/lib/changes/completion.py:364-365`)
  - Change hardcoded `"Expected status: draft or in-progress"` → `f"Expected status: {', '.join(sorted(valid_statuses))}"`.
  - `valid_statuses = {"draft", "in-progress"}` is defined two lines above.

- **1.4 Test assertions**
  - Run `just test` after fixes; update any assertions that match on old message strings.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|---|---|---|
| Test assertions on old message text | Find by running tests after patch; update | open |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] `just` passes clean
- [ ] Phase status set to completed
- [ ] DE-130 notes updated
