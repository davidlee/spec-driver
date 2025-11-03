# supekku.scripts.lib.formatters.policy_formatters

Policy display formatters.

Pure formatting functions with no business logic.
Formatters take PolicyRecord objects and return formatted strings for display.

## Functions

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

Returns:
  Formatted string in requested format
