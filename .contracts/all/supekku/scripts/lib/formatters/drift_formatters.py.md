# supekku.scripts.lib.formatters.drift_formatters

Drift ledger display formatters.

Pure formatting functions with no business logic.
Formatters take DriftLedger/DriftEntry objects and return formatted strings.

## Functions

- `_drift_list_to_json(ledgers) -> str`: Serialize drift ledgers to JSON.
- `_entry_to_dict(entry) -> dict`: Serialize a DriftEntry to a JSON-friendly dict.
- `_format_entry_summary(entry) -> str`: Format a single entry as a one-line summary.
- `_prepare_drift_row(ledger) -> list[str]`: Prepare a Rich-markup table row for a drift ledger.
- `_prepare_drift_tsv_row(ledger) -> list[str]`: Prepare a plain TSV row for a drift ledger.
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
