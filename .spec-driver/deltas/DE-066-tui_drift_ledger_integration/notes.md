# Notes for DE-066

## Status

Delta scoped. Ready for planning (`/plan-phases`).

## Assessment

This is a mechanical integration — wiring DE-065's `DriftLedgerRegistry` into
the existing `ArtifactType`/`ArtifactSnapshot` system used by the TUI. No new
abstractions or design decisions needed. DR skipped (pure wiring, no design
surface).

## Integration points (from artifact_view.py)

1. `ArtifactType` enum — add `DRIFT_LEDGER = "drift_ledger"` in Operational group
2. `ARTIFACT_TYPE_META` — add `ArtifactTypeMeta("Drift Ledger", "Drift Ledgers", _OPS)`
3. `_TITLE_ATTR` — add mapping (DriftLedger uses `name`)
4. `_STATUS_ATTR` — add mapping (DriftLedger uses `status`)
5. `_ID_ATTR` — add mapping (DriftLedger uses `id`)
6. `_REGISTRY_FACTORIES` — add factory for `DriftLedgerRegistry`
7. `path_to_artifact_type()` — add `DRIFT_SUBDIR` → `ArtifactType.DRIFT_LEDGER`
8. Possibly: snapshot `_iter_records()` adapter if DriftLedgerRegistry interface differs

## Key files

- `supekku/scripts/lib/core/artifact_view.py` — all enum/meta/factory wiring
- `supekku/scripts/lib/drift/registry.py` — existing registry (DE-065)
- `supekku/tui/` — should just work once artifact_view.py is wired
