# supekku.scripts.lib.formatters.change_formatters

Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.

## Functions

- `format_change_list_item(artifact) -> str`: Format change artifact as basic list item: id, kind, status, name.

Args:
  artifact: Change artifact to format

Returns:
  Tab-separated string: "{id}\t{kind}\t{status}\t{name}"
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
- `format_phase_summary(phase, max_objective_len) -> str`: Format a single phase with truncated objective.

Args:
  phase: Phase dictionary with 'phase'/'id' and 'objective' fields
  max_objective_len: Maximum length for objective before truncation

Returns:
  Formatted string: "{phase_id}" or "{phase_id}: {objective}"
