# supekku.scripts.lib.formatters.change_formatters

Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.

## Functions

- `format_audit_details(artifact, root) -> str`: Format audit details as multi-line string for display.

Args:
  artifact: ChangeArtifact to format (must be kind='audit')
  root: Repository root for relative path calculation (optional)

Returns:
  Formatted string with all audit details
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
- `format_change_list_table(changes, format_type, truncate) -> str`: Format change artifacts as table, JSON, or TSV.

Args:
  changes: List of ChangeArtifact objects to format
  format_type: Output format (table|json|tsv)
  truncate: If True, truncate long fields to fit terminal width
  show_external: If True, show ext_id column after ID
  show_refs: If True, show refs column (count in table, pairs in TSV)

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
  linked_audits: List of (id, name) for audits referencing this delta.
  linked_revisions: List of (id, name) for revisions referencing this delta.

Returns:
  Formatted string with all delta details
- `format_delta_details_json(artifact, root) -> str`: Format delta details as JSON with all file paths included.

Args:
  artifact: ChangeArtifact to format
  root: Repository root for relative path calculation (optional)

Returns:
  JSON string with complete delta information including all paths
- `format_delta_list_json(deltas) -> str`: JSON output per DR-138 §8.4 — full ``applies_to`` + full ``plan``.
- `format_delta_list_row(artifact) -> dict[Tuple[str, str]]`: Render one delta as a column-keyed cell dict (DR-138 §8.2).

Pure function — caller renders via Rich table, TSV, or JSON. POL-003
boundary: takes primitive input (no registry access); the CLI orchestrator
builds ``audited_delta_ids`` once per invocation.
- `format_delta_list_table(deltas) -> str`: Render the enriched delta list per DR-138 §8.1–§8.4.

``--external`` / ``--refs`` are preserved column flags (§8.3 flag
preservation); ``--tags`` is the new opt-in for the legacy Tags column
(§8.5).
- `format_phase_summary(phase, max_objective_len) -> str`: Format a single phase with truncated objective.

Args:
  phase: Phase dictionary with 'phase'/'id' and 'objective' fields
  max_objective_len: Maximum length for objective before truncation

Returns:
  Formatted string: "{phase_id}" or "{phase_id}: {objective}"
- `format_plan_details(plan_data, root, path) -> str`: Format plan details as multi-line string for display.

Args:
  plan_data: Plan frontmatter dictionary.
  root: Repository root for relative path calculation (optional).
  path: Plan file path (optional).

Returns:
  Formatted string with plan details.
- `format_plan_list_table(plans, format_type, truncate) -> str`: Format plans as table, JSON, or TSV.

Args:
  plans: Plan frontmatter dictionaries.
  format_type: Output format (table|json|tsv).
  truncate: If True, truncate long fields.

Returns:
  Formatted string in requested format.
- `format_revision_details(artifact, root) -> str`: Format revision details as multi-line string for display.

Args:
  artifact: ChangeArtifact to format (must be kind='revision')
  root: Repository root for relative path calculation (optional)

Returns:
  Formatted string with all revision details
