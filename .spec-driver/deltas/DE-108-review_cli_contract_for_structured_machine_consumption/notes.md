# Notes for DE-108

## Implementation Summary

All 3 phases complete.

### P01 — Foundation (common.py)

- `EXIT_PRECONDITION=2`, `EXIT_GUARD_VIOLATION=3`
- `cli_json_success()`, `cli_json_error()`, `emit_json_and_exit()`
- CLI-generic naming per DEC-108-001
- 9 tests

### P02 — Existing commands (workflow.py)

- `review prime --format json` with action enum (created/rebuilt/refreshed), full SHA, bootstrap/judgment status
- `review complete --format json` with outcome, state transition, guard violation (exit 3)
- `review teardown --format json` with removed files list
- `_prime_action()` helper, `_do_teardown()` returns list
- 10 tests

### P03 — New commands + finding disposition

- `workflow status --format json` with bootstrap/judgment status, findings summary, staleness inputs
- `review finding resolve/defer/waive/supersede --format json` via shared `_disposition_finding()`
- `review finding list` (new command) with `--round N` filter
- Finding not found → EXIT_PRECONDITION (2)
- 9 tests

### Key discoveries during implementation

- `review finding` subgroup already existed with per-action commands — no `add`/`dispose` needed
- `update_finding_disposition()`, `find_finding()` already in review_io.py — no new IO helpers needed
- `typer.Exit` is `click.exceptions.Exit` (inherits RuntimeError) — use `.args[0]` for exit code in tests
- Test fixture needed `spec_driver_installed_version` in workflow.toml to suppress stderr warning
- Full SHA change required updating staleness comparison to use `full_head` consistently

### Test summary

- 63 review tests (44 existing + 19 new JSON tests)
- 118 common tests (9 new envelope tests)
- 6 integration tests — all passing
- 202 total across touched test files
