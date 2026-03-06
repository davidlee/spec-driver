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

## Phase 2 — Self-Documentation (complete)

### What was delivered
- `core/enums.py`: enum registry with 7 enum paths, sourced from lifecycle constants
- `schema show enums` — lists all available enum paths
- `schema show enums.<artifact>.<field>` — returns sorted JSON array
- Examples sections added to 4 list command docstrings (deltas, specs, requirements, adrs)

### Key decisions
- Top-level imports from lifecycle modules (not lazy) — modules are lightweight
- Hardcoded values for spec.kind, requirement.kind, command.format (no constants exist)
- Plain `print(json.dumps(...))` for enum output (agent-friendly, no Rich formatting)
- Show command help already documented flags adequately — no changes needed

### Files modified
- `supekku/scripts/lib/core/enums.py` — new module (50 lines)
- `supekku/cli/schema.py` — `enums.*` routing + `_show_enums()` handler
- `supekku/cli/list.py` — docstring examples on 4 list commands

### Test files
- `supekku/cli/schema_test.py` — 10 new enum introspection tests (EnumIntrospectionTest)
- `supekku/cli/test_cli.py` — 10 new help text tests (TestHelpTextContent)
