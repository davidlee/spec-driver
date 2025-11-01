# supekku.scripts.lib.formatters.decision_formatters

Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.

## Functions

- `_calculate_column_widths(terminal_width) -> dict[Tuple[int, int]]`: Calculate optimal column widths for decision table.

Args:
  terminal_width: Available terminal width

Returns:
  Dictionary mapping column index to max width
- `_format_artifact_references(decision) -> list[str]`: Format references to other artifacts (specs, requirements, etc).
- `_format_as_table(decisions, truncate) -> str`: Format decisions as a rich table.

Args:
  decisions: Decisions to format
  truncate: Whether to truncate columns to fit terminal

Returns:
  Rendered table string
- `_format_basic_fields(decision) -> list[str]`: Format basic decision fields (id, title, status).
- `_format_decision_as_tsv_rows(decisions) -> list[list[str]]`: Convert decisions to TSV row format.
- `_format_people(decision) -> list[str]`: Format people-related fields (authors, owners).
- `_format_related_items(decision) -> list[str]`: Format related decisions and policies.
- `_format_relationships(decision) -> list[str]`: Format decision relationship fields (supersedes, superseded_by).
- `_format_tags_and_backlinks(decision) -> list[str]`: Format tags and backlinks.
- `_format_timestamps(decision) -> list[str]`: Format timestamp fields if present.
- `_prepare_decision_row(decision) -> list[str]`: Prepare a single decision row with styling.

Args:
  decision: Decision to format

Returns:
  List of formatted cell values [id, title, status, updated]
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
