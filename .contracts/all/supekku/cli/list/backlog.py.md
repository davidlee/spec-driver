# supekku.cli.list.backlog

List backlog command.

## Functions

- @app.command(backlog) `list_backlog(root, kind, status, substring, severity, related_to, tag, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog items with optional filtering.

By default, items are sorted by priority (registry order → severity → ID) and
resolved/implemented items are excluded. Use --all to include all statuses.
Use --order to sort by: id, severity, status, or kind.
Use --severity to filter by priority level (e.g. p1, p2, p3).

Use --prioritize to open the filtered items in your editor for interactive reordering.
After saving, the registry will be updated with your new ordering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
