# supekku.scripts.lib.requirements.coverage

Requirement coverage tracking and drift detection.

## Functions

- `_apply_coverage_blocks(records, spec_files, delta_files, plan_files, audit_files) -> None`: Apply verification coverage blocks to update requirement lifecycle.

Extracts coverage blocks from all artifact types, rebuilds coverage
fields from current sources (not accumulated), and derives status.

Coverage fields are cleared first so that removed coverage blocks
correctly result in empty evidence — the registry is a derived
projection (ADR-008 §5), not a persistent accumulator.

Terminal-status requirements (deprecated, superseded, retired) are
not overwritten by coverage-derived status.

- `_check_coverage_drift(req_id, entries) -> None`: Check for coverage drift and emit warnings.

Detects when the same requirement has conflicting coverage statuses
across different artifacts (spec vs IP vs audit).

- `_compute_status_from_coverage(entries) -> <BinOp>`: Compute requirement status from aggregated coverage entries.

Only entries with statuses in VALID_COVERAGE_STATUSES are considered.
Unknown statuses are silently ignored (warnings are emitted at the
ingestion boundary in \_apply_coverage_blocks).

Applies precedence rules:

- ANY 'failed' or 'blocked' → in-progress (needs attention)
- ALL 'verified' → active
- ANY 'in-progress' → in-progress
- ALL 'planned' → pending
- MIXED → in-progress

Returns None if no entries or unable to determine.

- `_extract_coverage_entries(files, coverage_map) -> None`: Extract coverage entries from a set of artifact files into coverage_map.

Entries with unknown statuses are still recorded (for transparency in
coverage_entries) but a warning is emitted. The downstream
\_compute_status_from_coverage() independently filters unknown statuses
so they never influence derived requirement state.
