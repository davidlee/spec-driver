# supekku.scripts.lib.formatters.spec_formatters

Specification (SPEC/PROD) display formatters.

Pure formatting functions with no business logic.
Formatters take Spec objects and return formatted strings for display.

## Functions

- `format_package_list(packages) -> str`: Format list of packages as comma-separated string.

Args:
  packages: List of package paths

Returns:
  Comma-separated string of packages
- `format_spec_list_item(spec) -> str`: Format spec as tab-separated list item with optional columns.

Args:
  spec: Specification object to format
  include_path: Include file path instead of slug (default: False)
  include_packages: Include package list (default: False)
  root: Repository root for relative path calculation (required if include_path=True)

Returns:
  Tab-separated string: "{id}\t{slug|path}[\t{packages}]"
- `format_spec_list_json(specs) -> str`: Format specs as JSON array.

Args:
  specs: List of Spec objects

Returns:
  JSON string with structure: {"items": [...]}
- `format_spec_list_table(specs, format_type, no_truncate, include_packages) -> str`: Format specs as table, JSON, or TSV.

Args:
  specs: List of Spec objects to format
  format_type: Output format (table|json|tsv)
  no_truncate: If True, don't truncate long fields
  include_packages: Include package list in output

Returns:
  Formatted string in requested format
