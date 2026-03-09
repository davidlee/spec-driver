# supekku.scripts.lib.formatters.decision_formatters

Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.

## Functions

- `format_decision_details(decision) -> str`: Format decision details as multi-line string for display.

Args:
  decision: Decision object to format

Returns:
  Formatted string with all decision details
- `format_decision_list_json(decisions) -> str`: Format decisions as JSON array.

Args:
  decisions: List of Decision objects

Returns:
  JSON string with structure: {"items": [...]}
- `format_decision_list_table(decisions, format_type, truncate) -> str`: Format decisions as table, JSON, or TSV.

Args:
  decisions: List of Decision objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields (default: False, show full content)

Returns:
  Formatted string in requested format
