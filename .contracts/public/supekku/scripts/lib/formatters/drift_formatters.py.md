# supekku.scripts.lib.formatters.drift_formatters

Drift ledger display formatters.

Pure formatting functions with no business logic.
Formatters take DriftLedger/DriftEntry objects and return formatted strings.

## Functions

- `format_drift_details(ledger) -> str`: Format a single drift ledger with full details.

Args:
  ledger: DriftLedger to format.

Returns:
  Multi-line formatted string with ledger metadata and entry summaries.
- `format_drift_details_json(ledger) -> str`: Format a drift ledger as JSON with full entry details.

Args:
  ledger: DriftLedger to format.

Returns:
  JSON string with ledger and entries.
- `format_drift_list_table(ledgers, format_type, truncate) -> str`: Format drift ledgers as table, JSON, or TSV.

Args:
  ledgers: Drift ledgers to format.
  format_type: Output format (table|json|tsv).
  truncate: If True, truncate long fields to fit terminal width.

Returns:
  Formatted string in requested format.
