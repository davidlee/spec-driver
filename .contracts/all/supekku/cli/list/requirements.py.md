# supekku.cli.list.requirements

List requirements command.

## Functions

- @app.command(requirements) `list_requirements(root, spec, status, kind, category, verified_by, vstatus, vkind, substring, regexp, case_insensitive, format_type, json_output, implemented_by, referenced_by, not_referenced_by, unimplemented, source_kind, tag, truncate, external) -> None`: List requirements with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on UID, label, title, and category fields.
The --category flag does substring matching on category field.
The --verified-by flag filters by verification artifact (supports glob patterns).
The --implemented-by flag filters to requirements a delta implements.
Use --case-insensitive (-i) to make regexp and category filters case-insensitive.

Examples:
list requirements -k FR,NF # Multi-value kind filter
list requirements --verified-by "VT-CLI-\*" # Glob pattern match
list requirements --vstatus verified --json # Verification status filter
list requirements --spec SPEC-110 --vkind VT # Combined filters
list requirements --source-kind issue # Filter by source
list requirements --implemented-by DE-090 # Requirements delta implements
list requirements --unimplemented # Requirements without a delta
list requirements --referenced-by delta # Requirements referenced by deltas
