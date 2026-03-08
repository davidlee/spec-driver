# Notes for DE-064

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

### Observations

- `workspace` commands are registered as top-level, not under a `workspace` subgroup — the `workspace.py` module is just the file organization, not the CLI namespace
- The `_check_binary()` helper in deps.py is a good reusable pattern for any "is X in PATH?" diagnostic
- Skills exposure check correctly handles missing target dirs and reports skipped skills by name
