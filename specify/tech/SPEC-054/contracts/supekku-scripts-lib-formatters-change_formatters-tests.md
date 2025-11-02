# supekku.scripts.lib.formatters.change_formatters

Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.

## Functions

- `_format_affects(artifact) -> list[str]`: Format affects section for revisions (similar to applies_to for deltas).
- `_format_applies_to(artifact) -> list[str]`: Format applies_to section if present.
- `_format_change_basic_fields(artifact) -> list[str]`: Format basic change artifact fields.
- `_format_file_path_for_change(artifact, root) -> list[str]`: Format file path section for change artifact.
- `_format_plan_overview(artifact) -> list[str]`: Format plan overview section if present.
- `_format_relations(artifact) -> list[str]`: Format relations section if present.
- `_format_revision_basic_fields(artifact) -> list[str]`: Format basic revision artifact fields.
- `format_change_list_item(artifact) -> str`: Format change artifact as basic list item: id, kind, status, name.

Args:
  artifact: Change artifact to format

Returns:
  Tab-separated string: "{id}\t{kind}\t{status}\t{name}"
- `format_change_list_json(changes) -> str`: Format change artifacts as JSON array.

Args:
  changes: List of ChangeArtifact objects

Returns:
  JSON string with structure: {"items": [...]}
- `format_change_list_table(changes, format_type, no_truncate) -> str`: Format change artifacts as table, JSON, or TSV.

Args:
  changes: List of ChangeArtifact objects to format
  format_type: Output format (table|json|tsv)
  no_truncate: If True, don't truncate long fields

Returns:
  Formatted string in requested format
- `format_change_with_context(artifact) -> str`: Format change artifact with related specs, requirements, and phases.

Provides detailed context including:
- Basic info (id, kind, status, name)
- Related specs
- Requirements
- Plan phases with objectives

Args:
  artifact: Change artifact to format

Returns:
  Multi-line formatted string with indented context
- `format_delta_details(artifact, root) -> str`: Format delta details as multi-line string for display.

Args:
  artifact: ChangeArtifact to format
  root: Repository root for relative path calculation (optional)

Returns:
  Formatted string with all delta details
- `format_phase_summary(phase, max_objective_len) -> str`: Format a single phase with truncated objective.

Args:
  phase: Phase dictionary with 'phase'/'id' and 'objective' fields
  max_objective_len: Maximum length for objective before truncation

Returns:
  Formatted string: "{phase_id}" or "{phase_id}: {objective}"
- `format_revision_details(artifact, root) -> str`: Format revision details as multi-line string for display.

Args:
  artifact: ChangeArtifact to format (must be kind='revision')
  root: Repository root for relative path calculation (optional)

Returns:
  Formatted string with all revision details
