# Notes for DE-011

## Phase 1 — Enhanced Filtering (complete)

### What was delivered
- `core/filters.py`: `parse_multi_value_filter()` pure utility
- Multi-value filters on all 6 list commands (deltas, specs, requirements, changes, revisions, adrs)
- Reverse relationship queries: `--implements`, `--verified-by`, `--informed-by`
- Glob pattern matching via `fnmatch` on `--verified-by`
- Verification filters: `--vstatus`, `--vkind` on `list requirements`
- `coverage_entries` field on `RequirementRecord` for vstatus/vkind filtering

### Key decisions
- Comma separator for multi-value (consistent with common CLI tools)
- `--verified-by` searches BOTH `verified_by` AND `coverage_evidence` fields
- Reverse queries applied FIRST (narrow before other filters)
- AND logic for combining multiple filter flags
- `fnmatch` for glob patterns (standard, already used in codebase)

### Files modified
- `supekku/scripts/lib/core/filters.py` — new module
- `supekku/scripts/lib/core/__init__.py` — export
- `supekku/cli/list.py` — all list commands updated
- `supekku/scripts/lib/changes/registry.py` — `find_by_implements()`
- `supekku/scripts/lib/requirements/registry.py` — `find_by_verified_by()`, `find_by_verification_status()`, `find_by_verification_kind()`, `coverage_entries` population
- `supekku/scripts/lib/specs/registry.py` — `find_by_informed_by()`
- `supekku/scripts/lib/specs/models.py` — `informed_by` property

### Test files
- `supekku/scripts/lib/core/filters_test.py` — 18 utility tests
- `supekku/cli/test_cli.py` — ~100 new CLI tests (multi-value, reverse, vstatus/vkind, backward compat)
- `supekku/scripts/lib/changes/registry_test.py` — 11 reverse query tests
- `supekku/scripts/lib/requirements/registry_test.py` — 34 reverse + verification tests
- `supekku/scripts/lib/specs/registry_test.py` — 10 reverse query tests

### Performance
All reverse queries <0.4s on current registry sizes (~30 deltas, ~160 requirements).

## Phase 2 — Self-Documentation (pending)

### Scope
- PROD-010.FR-006: Schema enum introspection (`schema show enums.<artifact>.<field>`)
- PROD-010.FR-007: Enhanced help text with output format examples

### Context for next implementer
- Multi-value filter patterns established — reference `core/filters.py` for consistency
- Registry query methods available for introspection in enum commands
- Test patterns established for CLI flag additions
- `list.py` is getting large (~1100 lines) — consider extracting sub-modules if Phase 2 adds significantly
