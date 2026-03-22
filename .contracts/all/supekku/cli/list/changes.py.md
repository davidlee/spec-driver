# supekku.cli.list.changes

List changes and plans commands.

## Functions

- @app.command(changes) `list_changes(root, kind, substring, status, applies_to, regexp, case_insensitive, format_type, json_output, truncate, paths, relations, applies, tag, plan, external) -> None`: List change artifacts (deltas, revisions, audits) with optional filters.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(plans) `list_plans(root, status, substring, tag, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List implementation plans with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
