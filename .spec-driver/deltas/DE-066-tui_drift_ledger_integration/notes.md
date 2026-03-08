# Notes for DE-066

## Status

All phases complete. Delta ready for closure.

## Completed

- Phase 1: wired DRIFT_LEDGER into ArtifactType, metadata tables, registry factory, path mapping
- 8 new tests (enum, metadata, factory, adapt, snapshot, path mapping)
- `just check` green: 3293 tests, ruff clean, pylint 9.71

## Key files

- `supekku/scripts/lib/core/artifact_view.py` — enum, metadata, factory, path mapping
- `supekku/scripts/lib/core/artifact_view_test.py` — 7 new tests
- `supekku/tui/edge_cases_test.py` — 1 new test (drift path mapping)

## Design notes

- No custom adapter needed — DriftLedger has `id`, `name`, `status`, `path` (same shape as other records)
- `_STATUS_ATTR` and `_ID_ATTR` use defaults (no entry needed — only CARD and REQUIREMENT override)
- `_TITLE_ATTR` explicitly set to `"name"` for clarity, though it's the default
- Single new `import-outside-toplevel` pylint message from `_make_drift_registry` — consistent with all other factory functions
