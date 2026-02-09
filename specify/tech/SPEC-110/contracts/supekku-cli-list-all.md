# supekku.cli.list

List commands for specs, deltas, and changes.

Thin CLI layer: parse args → load registry → filter → format → output
Display formatting is delegated to supekku.scripts.lib.formatters

## Constants

- `_PLURAL_TO_SINGULAR` - Singular command aliases - dynamically register
- `app`

## Functions

- @app.command(adrs) `list_adrs(root, status, tag, spec, delta, requirement_filter, policy, standard, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List Architecture Decision Records (ADRs) with optional filtering.

The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
- @app.command(backlog) `list_backlog(root, kind, status, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager) -> None`: List backlog items with optional filtering.

By default, items are sorted by priority (registry order → severity → ID) and
resolved/implemented items are excluded. Use --all to include all statuses.
Use --order to sort by: id, severity, status, or kind.

Use --prioritize to open the filtered items in your editor for interactive reordering.
After saving, the registry will be updated with your new ordering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID and title fields.
- @app.command(cards) `list_cards(root, lane, all_lanes, regexp, case_insensitive, format_type, json_output) -> None`: List kanban cards with optional filtering.

By default, hides cards in done/ and archived/ lanes. Use --all to show everything.
The --regexp flag does pattern matching on ID and title fields.
- @app.command(changes) `list_changes(root, kind, substring, status, applies_to, regexp, case_insensitive, format_type, json_output, truncate, paths, relations, applies, plan) -> None`: List change artifacts (deltas, revisions, audits) with optional filters.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(deltas) `list_deltas(root, ids, status, implements, regexp, case_insensitive, format_type, json_output, truncate, details) -> None`: List deltas with optional filtering and status grouping.

The --regexp flag filters on ID, name, and slug fields.
The --implements flag filters by requirement ID (reverse relationship query).
- @app.command(improvements) `list_improvements(root, status, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager) -> None`: List backlog improvements with optional filtering.

Shortcut for: list backlog --kind improvement

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(issues) `list_issues(root, status, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager) -> None`: List backlog issues with optional filtering.

Shortcut for: list backlog --kind issue

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(policies) `list_policies(root, status, tag, spec, delta, requirement_filter, standard, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List policies with optional filtering.

The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
- @app.command(problems) `list_problems(root, status, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager) -> None`: List backlog problems with optional filtering.

Shortcut for: list backlog --kind problem

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(requirements) `list_requirements(root, spec, status, kind, category, verified_by, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List requirements with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on UID, label, title, and category fields.
The --category flag does substring matching on category field.
The --verified-by flag filters by verification artifact (supports glob patterns).
Use --case-insensitive (-i) to make regexp and category filters case-insensitive.
- @app.command(revisions) `list_revisions(root, status, spec, substring, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List revisions with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
- @app.command(risks) `list_risks(root, status, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager) -> None`: List backlog risks with optional filtering.

Shortcut for: list backlog --kind risk

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(specs) `list_specs(root, kind, status, substring, package_filter, package_path, for_path, informed_by, regexp, case_insensitive, format_type, json_output, truncate, paths, packages) -> None`: List SPEC/PROD artifacts with optional filtering.

The --filter flag does substring matching (case-insensitive).
The --regexp flag does pattern matching on ID, slug, and name fields.
The --informed-by flag filters by ADR ID (reverse relationship query).
- @app.command(standards) `list_standards(root, status, tag, spec, delta, requirement_filter, policy, regexp, case_insensitive, format_type, json_output, truncate) -> None`: List standards with optional filtering.

The --regexp flag filters on title and summary fields.
Other flags filter on specific structured fields (status, tags, references).
