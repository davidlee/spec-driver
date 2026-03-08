# Notes for DE-073

## Phase 1 — `--content-type/-c` on `show` (complete)

### Done
- `ContentType` enum + `ContentTypeOption` annotated type in `common.py`
- `extract_yaml_frontmatter()` helper in `common.py`
- `emit_artifact()` extended with `content_type` param; overrides bool flags with warning
- `-c` added to all 15 `show` subcommands (9 via `emit_artifact` passthrough, 6 inline)
- 11 new tests (unit + CLI integration); 171 pass across common_test + show_test

### Rough edges / follow-up
- `show_requirement` and `show_card` not updated — they have non-standard
  inline logic (registry-based path resolution, `anywhere` flag). Low priority;
  could be refactored to `emit_artifact` first.
- `show_template` excluded — generates content, doesn't read a file.
- Inline subcommands (spec, delta, adr, policy, standard) duplicate the
  content-type dispatch pattern. Migrating them to `emit_artifact` would
  eliminate this but is a separate refactor.

### Verification
- `just lint` — clean
- `just test` — 3414 passed, 2 failed (pre-existing, unrelated)

### Commits
- Uncommitted

## Phase 2 — `view` refactor + `read` alias (complete)

### Done
- `render_file()`: glow → rich → raw stdout (no pager by default)
- `render_file_paged()`: $PAGER → glow -p → ov → less → more
- `PagerOption` annotated type (`--pager/-p`)
- `_view_artifact()` shared helper collapses 14 near-identical subcommands
- `view.py` reduced from 432 → ~260 lines; eliminated all direct registry imports
  except CardRegistry (lazy import for `--anywhere` flag)
- `read` registered as second `add_typer` of same app instance — zero code duplication
- `requirement` and `card` now use `resolve_artifact()` via `_view_artifact()`
  (requirement formerly had inline path resolution; card retains `--anywhere`)
- All 16 subcommands + inferred now accept `--pager/-p`
- 41 view tests (17 new), 3446 total passing

### Verification
- `just lint` — clean
- `just test` — 3446 passed, 2 failed (pre-existing, unrelated)

## Phase 3 — `resolve links` improvements (complete)

### Done
- `--verbose/-v`: reports each missing target with all containing file paths
- `--path <file>`: scopes resolution to a single memory file
- `--id <mem-id>`: convenience wrapper — resolves memory ID to path, delegates
- `--path` and `--id` are mutually exclusive; both composable with `--dry-run`/`--link-mode`
- `missing_detail` tracking in stats dict (target → list of source rel paths)
- 9 new tests (unit + CLI integration); 3455 total passing

### Verification
- `just lint` — clean
- `just test` — 3455 passed, 2 failed (pre-existing, unrelated)
