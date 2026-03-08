# Notes for DE-064

## Phase 2 — Remaining checks (refs, registries, lifecycle)

### Done

- `diagnostics/checks/refs.py`: delegates to `validate_workspace()`, translates `ValidationIssue` level→status (error→fail, warning→warn, info→pass). Wraps validator call in try/except for resilience.
- `diagnostics/checks/registries.py`: loads 5 registries (specs, deltas, revisions, audits, decisions) via `Workspace` accessors and `.collect()`. Reports item counts on success, error details on failure.
- `diagnostics/checks/lifecycle.py`: finds in-progress deltas, parses `updated` date, compares against configurable staleness threshold (default 5 days from `load_workflow_config`). Handles missing/unparseable dates gracefully.
- `diagnostics/checks/__init__.py`: registered all 3 new checks in CHECK_REGISTRY (total: 6 categories)

### Test coverage

- 23 new tests across 3 test files, all passing
- Full suite: 3143 passed, 2 pre-existing failures (unchanged)

### Verification

- `just lint`: clean
- `just pylint-files` on new files: 9.64/10 (3 `broad-exception-caught` — intentional for diagnostic resilience)
- `just test`: 3143 pass, 2 pre-existing fail, 3 skip
- Smoke test: `spec-driver doctor` runs all 6 categories successfully

### Remaining for Phase 3

- JSON output polish (already implemented in Phase 1 but may need verification)
- `--check` filter verification (already working)
- `--verbose` verification (already working)
- Full lint pass on entire codebase
- Verification documentation

## Phase 1 — Model, runner, first checks, CLI wiring

### Done

- `diagnostics/models.py`: `DiagnosticResult`, `CategorySummary`, `worst_status`
- `diagnostics/runner.py`: `run_checks()`, `overall_exit_code()`, `CHECK_REGISTRY`
- `diagnostics/checks/deps.py`: python, git/jj, go, gomarkdoc, zig, zigmarkdoc, node, ts-doc-extract
- `diagnostics/checks/structure.py`: .spec-driver root, 7 required subdirs, orphaned bundle detection
- `diagnostics/checks/config.py`: workflow.toml, CLAUDE.md, skills allowlist, agents dir, per-target skill exposure
- `formatters/diagnostic_formatters.py`: text output (with verbose toggle) and JSON output
- `cli/workspace.py`: `doctor` command with `--check`, `--json`, `--verbose`, `--root`
- `cli/main.py`: registered as top-level `doctor` command
- Updated `specs/package_utils_test.py`: added `diagnostics/checks` to leaf packages, `diagnostics` to parent packages; made count assertion dynamic

### Adaptations from plan

- **3 checks instead of 2**: added `config` category in Phase 1 (was planned for Phase 2) since user requested skills exposure checking during implementation
- **deps expanded**: added go, gomarkdoc, zig, zigmarkdoc checks per user request — used `_check_binary()` helper to DRY the pattern
- **Command registration**: `doctor` is a top-level command (like `validate`, `install`), not `workspace doctor` — workspace commands are registered directly on the main app, not as a subgroup
- **Python version check simplified**: ruff UP036 flagged the `>= 3.11` branch as dead code since pyproject.toml already requires 3.11+; reduced to just reporting version

### Test coverage

- 62 new tests across 7 test files, all passing
- Full suite: 3120 passed, 2 pre-existing failures (unrelated: `test_main_help` string mismatch, `test_show_problem_default`)

### Verification

- `just lint`: clean
- `just pylint-files` on all new files: 10.00/10
- `just test`: 3120 pass, 2 pre-existing fail, 3 skip

### Uncommitted

All work is uncommitted.

### Remaining for Phase 2

- `refs` check (delegate to WorkspaceValidator)
- `registries` check (load all registries, check ID uniqueness)
- `lifecycle` check (stuck in-progress deltas > N days, default 5)

### Out-of-scope follow-ups

- **IMPR-012**: Silent ID deduplication detection in registries check — filesystem-level collision where two source paths produce the same artifact ID. Deferred from Phase 2.

### Observations

- `workspace` commands are registered as top-level, not under a `workspace` subgroup — the `workspace.py` module is just the file organization, not the CLI namespace
- The `_check_binary()` helper in deps.py is a good reusable pattern for any "is X in PATH?" diagnostic
- Skills exposure check correctly handles missing target dirs and reports skipped skills by name
