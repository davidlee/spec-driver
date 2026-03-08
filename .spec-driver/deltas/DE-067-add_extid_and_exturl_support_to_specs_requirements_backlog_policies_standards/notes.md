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

## Phase 2 — Formatters and CLI (in progress, uncommitted)

### Done

- **JSON output**: Added ext_id/ext_url to JSON formatters for backlog, spec,
  change, policy, standard, requirement (conditional: omitted when empty)
- **Detail (show) formatters**: Added `External: {ext_id} ({ext_url})` line to
  detail formatters for all 6 artifact types. Uses shared pattern:
  `if item.ext_id:` → append line
- **List table formatters**: Added `show_external: bool = False` kwarg to all
  list table formatters. When True, inserts ExtID column after ID (or after
  Label for requirements). Affects table, TSV output.
  - Formatters using direct table construction (backlog, spec, change,
    requirement): column insertion + row building adjusted inline
  - Formatters using `format_list_table` utility (policy, standard): wrapper
    closures insert ext_id into row prep callbacks
- **CLI**: Added `ExternalOption` type alias in `common.py`. Added
  `external: ExternalOption = False` param to: `list_specs`, `list_deltas`,
  `list_changes`, `list_policies`, `list_standards`, `list_requirements`,
  `list_backlog`
- All 3285 tests pass, ruff clean

### Not yet done

- Sub-commands `list_issues`, `list_problems`, `list_improvements`, `list_risks`
  share backlog formatter but have their own command signatures — not yet wired
  with `--external` (they call `format_backlog_list_table` directly). Low priority
  since main `list backlog` covers them.
- `list_revisions` uses `format_change_list_table` but not yet wired
- No new formatter-level tests for `show_external=True` rendering — existing
  tests pass but don't exercise the new column. Should add before closing.
- `.spec-driver/` changes (phase-02 sheet, IP update) not yet committed — code
  changes also uncommitted. Will commit together.

### Observations

- Policy/standard formatters use the `format_list_table` utility with callbacks,
  which makes column insertion slightly awkward (closures wrapping the row prep).
  Not worth refactoring the utility for this — the closure approach works.
- Pyright diagnostics shown during work were all pre-existing (type issues in
  policy/standard `to_dict` methods, missing module sources for yaml/typer/etc).
  No new issues introduced.

### Open questions

- Should `list_issues`/`list_problems`/etc sub-commands also get `--external`?
  Deferred for now.
