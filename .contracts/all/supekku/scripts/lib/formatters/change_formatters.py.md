# supekku.scripts.lib.formatters.change_formatters

Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.

## Constants

- `_EMPTY_CELL`
- `_PHASE_SEQ_FROM_ID`

## Functions

- `_enrich_phase_data(phase, artifact, root) -> dict[Tuple[str, Any]]`: Enrich phase data with file path and task completion stats.

Checks for phase.tracking@v1 block first (structured data), then falls back
to regex-based checkbox parsing for backward compatibility.

Args:
  phase: Phase dictionary
  artifact: Parent delta artifact
  root: Repository root for relative paths

Returns:
  Enriched phase dictionary with tasks/criteria in checkbox format
- `_format_affects(artifact) -> list[str]`: Format affects section for revisions (similar to applies_to for deltas).
- `_format_applies_to(artifact) -> list[str]`: Format applies_to section if present.
- `_format_audit_basic_fields(artifact) -> list[str]`: Format basic audit artifact fields.
- `_format_audit_gate_cell(audit_gate) -> str`: Render DR-138 §8.1 Audit Gate column. Empty when default (``auto``).
- `_format_audit_glyph(delta_id, audited_delta_ids) -> str`: Render DR-138 §8.1 Audit column. Glyph keys on delta_id (DEC-138-13).
- `_format_change_basic_fields(artifact) -> list[str]`: Format basic change artifact fields.
- `_format_delta_reverse_lookups(linked_audits, linked_revisions) -> list[str]`: Format reverse lookup section for delta details.

Args:
  linked_audits: List of (id, name) tuples for audits referencing this delta.
  linked_revisions: List of (id, name) for revisions referencing this delta.

Returns:
  Lines for the reverse lookup section, or empty if none.
- `_format_file_path_for_change(artifact, root) -> list[str]`: Format file path section for change artifact.
- `_format_other_files(artifact, root) -> list[str]`: Format other files in delta bundle.
- `_format_phases_cell(plan) -> str`: Render DR-138 §8.1 Phases column: completed/total or em-dash if no plan.
- `_format_plan_overview(artifact, root) -> list[str]`: Format plan overview section if present.
- `_format_relations(artifact) -> list[str]`: Format relations section if present.
- `_format_revision_basic_fields(artifact) -> list[str]`: Format basic revision artifact fields.
- `_format_specs_cell(applies_to) -> str`: Render DR-138 §8.1 Specs column: ``N (first-id)`` or em-dash if empty.
- `_phase_sequence_digits_from_id(phase_id) -> <BinOp>`: Return two-digit sequence from phase id (hyphen or dotted spelling).
- `_plan_list_to_json(plans) -> str`: Serialize plans to JSON.
- `_prepare_change_row(change) -> list[str]`: Prepare a single change artifact row with styling.
- `_prepare_change_tsv_row(change) -> list[str]`: Prepare a single change artifact as a plain TSV row.
- `_prepare_plan_row(plan) -> list[str]`: Prepare a plan row with styling for rich table display.
- `_prepare_plan_tsv_row(plan) -> list[str]`: Prepare a plan row for TSV output (no markup).
- `_resolve_phase_objective_from_file_body(phase_content) -> <BinOp>`: Structured objective from phase file body: frontmatter first, then phase.overview.

Display-time enrichment (DE-131 / DR-131): does not merge conflicting sources;
returns the first non-empty value per canonical precedence.
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
