# Notes for DE-041

## Codebase observations (2026-03-04)

- show.py has 10 commands × ~30 lines each of identical boilerplate
- view.py/edit.py: 8 commands each, ~20 lines identical pattern
- find.py: 8 commands, ~15 lines each
- common.py already has `normalize_id`, `open_in_pager`, `open_in_editor`, `matches_regexp`, reusable Option types
- list.py is 2158 lines (largest CLI file) with 15 commands and highly variable flag sets
- Test coverage: show_test 525L, view_test 232L, edit_test 198L, find_test 199L, list_test 792L
- No revision-specific tests in show_test.py — needed before migration
- IP scaffolding in creation.py:251-298 (within `create_delta`)
- `discover_backlog_items()` in backlog/registry.py does full O(n) scan — `find_backlog_items_by_id()` will use targeted path lookup

## DR review cleanup (2026-03-04)

5 internal contradictions fixed:
1. `list cards --status` removed (cards use `--lane`)
2. show_audit example: added missing `json_fn`
3. VT-emit: removed stale fallback chain wording
4. VT-migration: aligned table with stricter pre-migration requirement
5. `find_backlog_item` → `find_backlog_items_by_id` naming

## Bug fix: _update_plan_overview_phases regex escape (2026-03-04)

`_update_plan_overview_phases` in `creation.py:592` passed the replacement string
directly to `re.sub`, which interprets backslash sequences (`\u`, `\n`, etc.).
Plan files with user-edited content (URLs, unicode) triggered `bad escape \u`.

**Fix**: `pattern.sub(lambda _: new_block, content, count=1)` — lambda avoids
regex interpretation of the replacement string.

**Test**: `test_create_phase_plan_with_backslash_sequences` in `creation_test.py`.

## Pre-existing test failures (not DE-041)

6 tests fail on main before any DE-041 changes:
- `resolve_test.py::TestResolveMemoryLinks::test_no_op_missing_directory`
- 5× `test_cli.py::TestVerificationStatusFilters` (empty `coverage_entries`)
