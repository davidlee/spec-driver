# DE-100 Implementation Notes

## Phase 1 — Complete

### Changes

**Model** (`supekku/scripts/lib/changes/registry.py`):

- Added `tags: list[str] = field(default_factory=list)` to `PlanSummary`
- Populated from frontmatter in `discover_plans()`

**CLI** (`supekku/cli/list.py`):

- Made `--tag` repeatable (`list[str] | None`) on ADRs, policies, standards
- Moved tag filtering inline (out of `registry.filter()`) for repeatable OR support
- Added `--tag`/`-t` to: backlog, specs, deltas, changes, requirements, revisions, audits, plans
- Threaded `--tag` through sub-kind wrappers: issues, problems, improvements, risks

**Tests** (`supekku/cli/test_cli.py`):

- 44 new tests in `TestTagFiltering` class
- Flag acceptance (15 commands × long + short flags)
- Help text (15 commands)
- Repeatable OR logic (ADRs)
- AND interaction with --status
- No-match returns empty

### Design decisions applied

- DEC-100-01: Kept `--tag` — no rename (verb context disambiguates)
- DEC-100-02: Cards and drift excluded (no frontmatter tags)
- DEC-100-03: Repeatable with OR logic, ANDed with other filters
- DEC-100-04: No `ChangeRegistry.filter(tag=)` — no CLI consumer
- DEC-100-05: All taggable models have explicit `tags` field — no `getattr` fallback

### Observations

- Pre-existing test failure: `common_test.py::TestResolveArtifactBacklog::test_raises_not_found_for_missing_backlog` — unrelated to this delta
- Pre-existing lint warnings (22) in other files — none in our changed files
- ADR list commands have a pre-existing quirk: `--status` only applies when no structured filters are used (status goes through `registry.iter(status=...)` in else branch). Not introduced by this delta.
