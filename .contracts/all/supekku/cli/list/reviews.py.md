# supekku.cli.list.reviews

List revisions and audits commands.

## Functions

- @app.command(audits) `list_audits(root, status, spec, delta, tag, substring, regexp, case_insensitive, format_type, json_output, referenced_by, not_referenced_by, truncate, external) -> None`: List audits with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
The --referenced-by/--not-referenced-by flags filter by reverse references.
- @app.command(revisions) `list_revisions(root, status, spec, delta, tag, substring, regexp, case_insensitive, format_type, json_output, truncate, external) -> None`: List revisions with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
