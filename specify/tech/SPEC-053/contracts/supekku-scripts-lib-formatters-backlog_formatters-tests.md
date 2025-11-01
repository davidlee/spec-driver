# supekku.scripts.lib.formatters.backlog_formatters

Backlog item display formatters.

Pure formatting functions with no business logic.
Formatters take BacklogItem objects and return formatted strings for display.

## Functions

- `format_backlog_details(item) -> str`: Format single backlog item with full details.

Args:
  item: BacklogItem to format

Returns:
  Multi-line formatted string with all backlog item details
- `format_backlog_list_json(items) -> str`: Format backlog items as JSON array.

Args:
  items: List of BacklogItem objects

Returns:
  JSON string with structure: {"items": [...]}
- `format_backlog_list_table(items, format_type, truncate) -> str`: Format backlog items as table, JSON, or TSV.

Args:
  items: List of BacklogItem objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields (default: False, show full content)

Returns:
  Formatted string in requested format
