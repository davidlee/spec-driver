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
