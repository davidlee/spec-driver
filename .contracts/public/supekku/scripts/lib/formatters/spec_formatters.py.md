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
- `format_spec_details(spec, root) -> str`: Format spec details as multi-line string for display.

Args:
  spec: Specification object to format
  root: Repository root for relative path calculation (optional)
  fr_count: Number of functional requirements (from RequirementsRegistry)
  nf_count: Number of non-functional requirements
  other_req_count: Number of other requirements
  delta_count: Number of deltas referencing this spec
  revision_count: Number of revisions referencing this spec
  audit_count: Number of audits referencing this spec
  requirements_list: Expanded requirements list (id, kind_label, title) when
    --requirements flag is used. When provided, replaces the count summary.

Returns:
  Formatted string with all spec details
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
- `format_spec_list_table(specs, format_type, truncate, include_packages) -> str`: Format specs as table, JSON, or TSV.

Args:
  specs: List of Spec objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields to fit terminal width
  include_packages: Include package list in output
  show_external: If True, show ext_id column after ID
  show_refs: If True, show refs column (count in table, pairs in TSV)

Returns:
  Formatted string in requested format
