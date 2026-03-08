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

## Phase 2 — `view` refactor + `read` alias (next)

### Scope
- Remove default pager from `view`; render via glow → rich → raw stdout
- `--pager/-p` flag for opt-in paged display ($PAGER → glow -p → rich --pager → ov → less → more)
- `read` as alias for `view`
- Reduce `view.py` duplication (~16 near-identical subcommands)

## Phase 3 — `resolve links` improvements (after phase 2)

### Scope
- `--verbose`: report missing targets with containing files
- `--path <file>` / `--id <mem-id>`: scoped resolution
