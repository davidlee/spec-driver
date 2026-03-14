# supekku.scripts.lib.formatters.policy_formatters

Policy display formatters.

Pure formatting functions with no business logic.
Formatters take PolicyRecord objects and return formatted strings for display.

## Functions

- `_format_artifact_references(policy) -> list[str]`: Format references to other artifacts (specs, requirements, etc).
- `_format_basic_fields(policy) -> list[str]`: Format basic policy fields (id, title, status).
- `_format_people(policy) -> list[str]`: Format people-related fields (owners).
- `_format_related_items(policy) -> list[str]`: Format related policies and standards.
- `_format_relationships(policy) -> list[str]`: Format policy relationship fields (supersedes, superseded_by).
- `_format_tags_and_backlinks(policy) -> list[str]`: Format tags and backlinks.
- `_format_timestamps(policy) -> list[str]`: Format timestamp fields if present.
- `_prepare_policy_row(policy) -> list[str]`: Prepare a single policy row with styling.

Returns:
  List of formatted cell values [id, title, tags, status, updated]
- `_prepare_policy_tsv_row(policy) -> list[str]`: Prepare a single policy as a plain TSV row (no markup).
- `format_policy_details(policy) -> str`: Format policy details as multi-line string for display.

Args:
  policy: PolicyRecord object to format

Returns:
  Formatted string with all policy details
- `format_policy_list_json(policies) -> str`: Format policies as JSON array.

Args:
  policies: List of PolicyRecord objects

Returns:
  JSON string representation
- `format_policy_list_table(policies, format_type, truncate) -> str`: Format policies as table, JSON, or TSV.

Args:
  policies: List of PolicyRecord objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields (default: False, show full content)
  show_external: If True, show ext_id column after ID

Returns:
  Formatted string in requested format
