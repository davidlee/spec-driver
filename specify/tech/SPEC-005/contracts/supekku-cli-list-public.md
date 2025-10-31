# supekku.cli.list

List commands for specs, deltas, and changes.

## Constants

- `ROOT` - Add parent to path for imports
- `app`

## Functions

- @app.command(changes) `list_changes(root, kind, substring, status, applies_to, paths, relations, applies, plan) -> None`: List change artifacts (deltas, revisions, audits) with optional filters.
- @app.command(deltas) `list_deltas(root, ids, status, details) -> None`: List deltas with optional filtering and status grouping.
- @app.command(specs) `list_specs(root, kind, substring, package_filter, package_path, for_path, paths, packages) -> None`: List SPEC/PROD artifacts with optional filtering.
