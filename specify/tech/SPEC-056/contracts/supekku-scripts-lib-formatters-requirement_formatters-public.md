# supekku.scripts.lib.formatters.requirement_formatters

Requirement display formatters.

Pure formatting functions with no business logic.
Formatters take RequirementRecord objects and return formatted strings for display.

## Functions

- `format_requirement_details(requirement) -> str`: Format single requirement with full details.

Args:
  requirement: RequirementRecord to format

Returns:
  Multi-line formatted string with all requirement details
- `format_requirement_list_json(requirements) -> str`: Format requirements as JSON array.

Args:
  requirements: List of RequirementRecord objects

Returns:
  JSON string with structure: {"items": [...]}
- `format_requirement_list_table(requirements, format_type, truncate) -> str`: Format requirements as table, JSON, or TSV.

Args:
  requirements: List of RequirementRecord objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields (default: False, show full content)

Returns:
  Formatted string in requested format
