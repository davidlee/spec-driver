# Notes for DE-028

## Continuation Prompt

```
Continue implementation of DE-028 (sync defaults: contracts-first, opt-in spec creation).

Tasks 1.1–1.3 are complete. Remaining: 1.4, 1.5, 1.6.

Read these files for full context:
- change/deltas/DE-028-sync_defaults_contracts_first_opt_in_spec_creation/DE-028.md (delta)
- change/deltas/DE-028-sync_defaults_contracts_first_opt_in_spec_creation/phases/phase-01.md (phase sheet with task details + observations from 1.1–1.3)

Summary of what's done:
- 1.1: `supekku/scripts/lib/core/sync_preferences.py` — spec_autocreate_enabled() and persist_spec_autocreate() with 7 tests
- 1.2: `supekku/scripts/sync_specs.py` — process_source_unit() has generate_contracts: bool = True param gating adapter.generate()
- 1.3: `supekku/cli/sync.py` — --specs is now bool | None = None (tri-state, --specs/--no-specs), --contracts/--no-contracts added (bool = True). sync_test.py updated for new default. `contracts` param exists but is not yet used in the function body.

What remains:
- 1.4: Preference resolution in sync() body. Connect tri-state --specs to sync_preferences module. When --specs is explicitly True, call persist_spec_autocreate(). When None, check spec_autocreate_enabled(). Pass resolved value + contracts flag through to _sync_specs and then to process_source_unit. The `contracts` flag should gate the mirror tree rebuild at the end of _sync_specs (line ~514) as well.
- 1.5: Backward compat. Before preference resolution, check if registry_v2.json has entries. If yes and no marker exists, treat as implicit opt-in + write marker + log message. This goes early in sync() body after root/registry_path are established.
- 1.6: Integration tests (VT-SYNC-DEFAULTS-001 through 005). See phase sheet for test descriptions. Likely a new file supekku/cli/sync_defaults_test.py.

Key design constraints (see DE-028 §4 + §10):
- Do NOT introduce "if no spec, skip contracts" outside process_source_unit — that constraint is local to current output resolution, not a system rule.
- Do NOT wire --contracts through sync preferences / marker. Only spec creation has opt-in/persist semantics.
- The `contracts` flag gates intent; the fact that contracts currently need a spec dir to write to is a capability constraint in process_source_unit, not a flag-level concern.

All tests pass (1655/1655), both linters clean as of end of 1.3.
```
