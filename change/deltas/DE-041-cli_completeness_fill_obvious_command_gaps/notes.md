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

## Pre-existing test failures — FIXED (2026-03-04)

6 tests failed on main before DE-041 changes. Fixed as prerequisites:

1. `resolve_test.py::test_no_op_missing_directory` — test didn't anchor repo root at `tmp_path`, so `find_repo_root` walked up to the real repo. Fix: create `.spec-driver/` dir in tmp_path.
2. 5× `test_cli.py::TestVerificationStatusFilters` — `format_requirement_list_json` omitted `coverage_entries` from JSON output. Filter worked correctly on model objects, but assertions against JSON output failed. Fix: added `coverage_entries` to JSON serialization in `requirement_formatters.py`.

## Phase 1, tasks 1.1–1.3 (2026-03-04)

**Done**: Shared helpers in `supekku/cli/common.py` (tasks 1.1–1.3):
- `ArtifactRef` (frozen dataclass), `ArtifactNotFoundError`, `AmbiguousArtifactError`
- `resolve_artifact()` — dispatch table covering 10 types (spec, delta, revision, audit, adr, policy, standard, requirement, card, memory). Lazy imports to keep CLI startup fast.
- `emit_artifact()` — output-mode dispatch (path/raw/json/formatted) with mutual-exclusivity check. `json_fn` is required per DR-041 §4.1.
- DEC-041-05: requirement ID colon→dot normalization (`SPEC-009:FR-001` → `SPEC-009.FR-001`)

**Tests**: 32 new tests in `common_test.py` (10 data types + 15 resolve + 7 emit). Full suite: 2359 passed, 0 failed.

**Surprises/adaptations**:
- Lazy imports inside `_resolve_*` functions require patching at the source module (`supekku.scripts.lib.*.registry.XRegistry`), not at `supekku.cli.common`. Standard mock behavior for `from X import Y` inside functions.
- `typer.Exit` is `click.exceptions.Exit`, not `SystemExit` — tests must catch `typer.Exit` when calling helpers directly (outside typer runner).
- Policy/standard resolvers: `find()` returns record with string `.path`, needs `Path()` wrapping. Consistent with decision pattern.

**Potential rough edges**:
- `_resolve_requirement` path handling: if `record.path` is empty, falls back to `root`. May need refinement when requirements get standalone files.
- pylint `import-outside-toplevel` warnings (16) from lazy imports — expected, threshold (0.75) not breached.

**Verification**: `just check` green (tests + ruff + pylint). Committed: `722b815`.

## Phase 1, tasks 1.4–1.6 (2026-03-04)

**Done**:
- `find_artifacts()` — dispatch table returning `Iterator[ArtifactRef]` for 10 artifact types. Memory auto-prepends `mem.` prefix. Card uses rglob. Requirement normalizes colon→dot per DEC-041-05.
- `_matches_pattern()` — fnmatch helper (case-insensitive), extracted to common.py for reuse by both `find_artifacts` and future migrated find commands.
- Test coverage gap-fill: added policy/standard resolve tests, dispatch coverage parameterized test, card/requirement find tests. 57 tests in common_test.py total.
- Pre-migration regression tests: 17 tests across show_test (7), view_test (3), edit_test (3), find_test (4). All 4 revision commands × relevant output modes covered.
- `show revision --json` known bug confirmed: test documents current behavior (passes if output is valid JSON, tolerates failure).

**Tests**: 2401 passed, 0 failed (+42 from previous commit).

**Verification**: Full suite green. Committed: `d6c3a6d`.

**Next**: Tasks 1.7 (migrate revision commands + fix --json bug) and 1.8 (final verification).

## Phase 1, task 1.7 — migration + --json bug fix (2026-03-04)

**Done**: Migrated all 4 revision commands to shared helpers:
- `show_revision` → `resolve_artifact` + `emit_artifact` (show.py)
- `view_revision` → `resolve_artifact` + `open_in_pager` (view.py)
- `edit_revision` → `resolve_artifact` + `open_in_editor` (edit.py)
- `find_revision` → `find_artifacts` (find.py)

**Bug fix**: `show revision --json` — was calling `artifact.to_dict()` without
required `repo_root` arg (show.py:152-154). Fixed by passing
`json_fn=lambda r: json.dumps(r.to_dict(root), indent=2)` to `emit_artifact`.
Regression test updated from "known bug" documentation to proper assertion.

**Lines saved**: Each migrated command reduced from ~25-30 lines to ~5-10 lines.
- show_revision: 30 → 11 lines
- view_revision: 25 → 10 lines
- edit_revision: 25 → 10 lines
- find_revision: 20 → 8 lines

**Error handling change**: Migrated commands catch `ArtifactNotFoundError` instead
of broad `(FileNotFoundError, ValueError, KeyError)`. This is intentional —
`resolve_artifact` normalizes all lookup failures into `ArtifactNotFoundError`,
so the broad catch was masking unrelated errors.

**Verification**: All 18 regression tests pass. `just check` green (2384 passed, pylint 9.59/10).
