# supekku.scripts.lib.diagnostics.checks.lifecycle

Lifecycle hygiene checks.

Detects in-progress deltas that have been stale beyond a configurable
threshold.

## Constants

- `CATEGORY`
- `DEFAULT_STALENESS_DAYS`

## Functions

- `check_lifecycle(ws) -> list[DiagnosticResult]`: Check for stale in-progress deltas.
