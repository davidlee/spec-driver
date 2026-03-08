# Notes for DE-067

## Phase 1 — Models and Schema (complete)

- Added `ext_id: str = ""` and `ext_url: str = ""` to all 6 domain models:
  Spec (as properties reading from frontmatter.data), BacklogItem, ChangeArtifact,
  RequirementRecord, PolicyRecord, StandardRecord
- Wired frontmatter extraction in registries (backlog, policy, standard, change)
- Confirmed frontmatter passthrough: `validate_frontmatter()` preserves unknown
  fields in `data` dict — no schema changes needed
- Added `EXT_ID_COLUMN` to `column_defs.py`
- Tests: Spec roundtrip (via SpecRegistry), BacklogItem construction,
  ChangeArtifact load/to_dict
- Commit: `c1a333a`

## Phase 2 — Formatters and CLI (complete)

- **JSON output**: ext_id/ext_url in all 6 JSON formatters (conditional)
- **Detail (show) formatters**: `External: {ext_id} ({ext_url})` line in all 6
- **List table formatters**: `show_external: bool = False` kwarg, ExtID column
  insertion in table + TSV output
- **CLI**: `ExternalOption` type alias in `common.py`, `--external`/`-e` on 7
  list commands
- **Tests**: 50 new tests across 6 formatter test files (VT-067-002)
- 3335 tests pass, ruff clean
- Commits: `85cc169` (code+tests), `c03e9ad` (workflow artefacts)

### Deferred

- Sub-commands `list_issues`/`list_problems`/`list_improvements`/`list_risks`
  not wired with `--external` (they share `format_backlog_list_table` which
  already supports it; only the CLI param is missing). Low priority.
- `list_revisions` similarly not wired.
