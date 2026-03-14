# Notes for DE-028

## Status

Phase 1 complete. All 6 tasks done. 1660 tests pass, `just` green (9.67/10 pylint).

Remaining wrap-up:

- RE-016 actions update
- Manual smoke test
- Delta completion (`uv run spec-driver complete delta DE-028`)

## Continuation Prompt

```
DE-028 (sync defaults: contracts-first, opt-in spec creation) — Phase 1 is complete.

Read:
- change/deltas/DE-028-sync_defaults_contracts_first_opt_in_spec_creation/DE-028.md (delta)
- change/deltas/DE-028-sync_defaults_contracts_first_opt_in_spec_creation/phases/phase-01.md (phase sheet)

All tasks done (1.1–1.6). Files changed:
- supekku/scripts/lib/core/sync_preferences.py — marker read/write (7 tests)
- supekku/scripts/sync_specs.py — process_source_unit: generate_contracts + create_specs params
- supekku/cli/sync.py — preference resolution, backward compat heuristic, flag passthrough
- supekku/cli/sync_defaults_test.py — 5 VTs (VT-SYNC-DEFAULTS-001–005)

Wrap-up remaining: RE-016 action update, manual smoke test, delta completion.
```

## Implementation Log

### Tasks 1.1–1.3 (previous session)

- sync_preferences module + 7 tests
- generate_contracts param on process_source_unit
- CLI flag wiring (tri-state --specs, --contracts/--no-contracts)

### Task 1.4 — Preference resolution

- Entry guard: `if specs:` → `if resolved_specs or contracts:`
- Resolution: explicit flag > marker > False
- `_sync_specs` gains `create_specs` + `generate_contracts` keyword params
- `process_source_unit` gains `create_specs` — returns skipped when False and no existing spec
- Mirror tree rebuild gated on `generate_contracts`
- Hint message to stderr when specs off

### Task 1.5 — Backward compat

- Lazy RegistryV2 import + load when registry exists and no marker
- `any(registry.languages.values())` — language-agnostic check
- Writes marker + stderr message before preference resolution

### Task 1.6 — Integration tests

- New file `supekku/cli/sync_defaults_test.py`, 5 VTs
- Typer CliRunner mixes stderr into output (no `mix_stderr` option)
- VT-002 exercises two sequential invocations for persistence
- 1660 total tests (was 1655)
