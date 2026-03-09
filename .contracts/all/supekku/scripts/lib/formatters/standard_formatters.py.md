# supekku.scripts.lib.formatters.standard_formatters

Standard display formatters.

Pure formatting functions with no business logic.
Formatters take StandardRecord objects and return formatted strings for display.

## Functions

- `_format_artifact_references(standard) -> list[str]`: Format references to other artifacts (specs, requirements, etc).
- `_format_basic_fields(standard) -> list[str]`: Format basic standard fields (id, title, status).
- `_format_people(standard) -> list[str]`: Format people-related fields (owners).
- `_format_related_items(standard) -> list[str]`: Format related policies and standards.
- `_format_relationships(standard) -> list[str]`: Format standard relationship fields (supersedes, superseded_by).
- `_format_tags_and_backlinks(standard) -> list[str]`: Format tags and backlinks.
- `_format_timestamps(standard) -> list[str]`: Format timestamp fields if present.
- `_prepare_standard_row(standard) -> list[str]`: Prepare a single standard row with styling.

Returns:
  List of formatted cell values [id, title, tags, status, updated]
- `_prepare_standard_tsv_row(standard) -> list[str]`: Prepare a single standard as a plain TSV row (no markup).
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
  show_external: If True, show ext_id column after ID

Returns:
  Formatted string in requested format
