# supekku.scripts.lib.formatters.standard_formatters

Standard display formatters.

Pure formatting functions with no business logic.
Formatters take StandardRecord objects and return formatted strings for display.

## Functions

- `format_standard_details(standard) -> str`: Format standard details as multi-line string for display.

Args:
  standard: StandardRecord object to format

Returns:
  Formatted string with all standard details
- `format_standard_list_json(standards) -> str`: Format standards as JSON array.

Args:
  standards: List of StandardRecord objects

Returns:
  JSON string representation
- `format_standard_list_table(standards, format_type, truncate) -> str`: Format standards as table, JSON, or TSV.

Args:
  standards: List of StandardRecord objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields (default: False, show full content)

Returns:
  Formatted string in requested format
