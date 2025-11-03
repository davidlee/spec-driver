# supekku.cli.list

List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters

## Constants

- `app`

## Functions

- @app.command(adrs) `list_adrs(root, status, tag, spec, delta, requirement_filter, policy, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List Architecture Decision Records (ADRs) with optional filtering.

The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
- @app.command(backlog) `list_backlog(root, kind, status, substring, regexp, case_insensitive, format_type, truncate) -> None`: List backlog items with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
- @app.command(changes) `list_changes(root, kind, substring, status, applies_to, regexp, case_insensitive, format_type, json_output, truncate, paths, relations, applies, plan) -> None`: List change artifacts (deltas, revisions, audits) with optional filters.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(deltas) `list_deltas(root, ids, status, regexp, case_insensitive, format_type, json_output, truncate, details) -> None`: List deltas with optional filtering and status grouping.

The --regexp flag filters on ID, name, and slug fields.
- @app.command(requirements) `list_requirements(root, spec, status, kind, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List requirements with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on UID, label, and title fields.
- @app.command(revisions) `list_revisions(root, status, spec, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List revisions with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(specs) `list_specs(root, kind, status, substring, package_filter, package_path, for_path, regexp, case_insensitive, format_type, json_output, truncate, paths, packages) -> None`: List SPEC/PROD artifacts with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
