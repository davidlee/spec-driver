---
id: notes
---

# DE-101 Implementation Notes

## Changes

### `supekku/scripts/lib/requirements/registry.py`

Added `_is_requirement_like_line()` helper function that distinguishes
requirement *definitions* from *cross-references*. Two cross-reference
patterns are now excluded from the "requirement-like" heuristic:

1. **"per" citations**: `per FR-007`, `per PROD-004.FR-007` — the word
   "per" before an ID signals a cross-reference.
2. **Parenthetical-only mentions**: When all FR/NF IDs on a line appear
   inside parentheses (e.g. `(PROD-004.FR-007)`), the line is citing
   requirements, not defining them.

Supporting module-level regexes added:
- `_REQUIREMENT_CROSSREF` — matches `per <ID>` patterns
- `_REQUIREMENT_IN_PARENS` — matches `(<ID>)` patterns
- `_BARE_REQUIREMENT_ID` — base pattern for any FR/NF-xxx mention

The `_records_from_content()` method now uses `_is_requirement_like_line()`
instead of the raw `\b(FR|NF)-\d{3}\b` scan.

### `supekku/scripts/lib/requirements/registry_test.py`

Added two test classes:

- `TestIsRequirementLikeLine` (19 tests): unit tests for the heuristic,
  covering definitions, cross-references, edge cases.
- `TestRecordsFromContentCrossRefSuppression` (1 test): integration test
  verifying that a spec containing only cross-references does not trigger
  the extraction warning.

## Status

Implementation complete. All 124 requirement tests pass. Lint clean.
Delta is still `draft` — needs close-out.

## New Agent Instructions

### Task card
- **Delta**: DE-101
- **Notes**: `.spec-driver/deltas/DE-101-fix_requirement_extraction_false_positive_warnings_on_cross_references/notes.md`
- **Delta file**: `.spec-driver/deltas/DE-101-fix_requirement_extraction_false_positive_warnings_on_cross_references/DE-101.md`

### Key files
- `supekku/scripts/lib/requirements/registry.py` — the fix (lines ~80–115 for regexes/helper, ~1205 for call site)
- `supekku/scripts/lib/requirements/registry_test.py` — new tests at end of file

### Commit-state guidance
Three dirty items in worktree:
1. `supekku/scripts/lib/requirements/registry.py` (modified — the fix)
2. `supekku/scripts/lib/requirements/registry_test.py` (modified — new tests)
3. `.spec-driver/deltas/DE-101-*/` (untracked — delta artefacts)

Per repo doctrine, `.spec-driver` changes and code can go together or separately.
A single commit is fine here: `fix(DE-101): suppress false-positive requirement-like warnings on cross-references`.

### Loose ends
- DE-101 status is still `draft`. It should be moved to `completed` via `/close-change`.
- The DR-101 and IP-101 files were auto-created but not populated (unnecessary for this fix size). They can be left as-is or cleaned up during close.
- No spec or memory updates needed — this is a pure bugfix with no architectural implications.

### Pre-existing test failures
3 failures and 9 errors in the full suite are pre-existing and unrelated:
- `test_raises_not_found_for_missing_backlog`
- `test_creates_directory_if_missing`
- `test_generate_propagates_gomarkdoc_error`
- 9 errors in `memory/creation_test.py`
