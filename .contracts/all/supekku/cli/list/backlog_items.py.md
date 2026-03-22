# supekku.cli.list.backlog_items

List drift, issues, problems, improvements, and risks commands.

## Functions

- @app.command(drift) `list_drift(root, status, substring, regexp, case_insensitive, format_type, truncate) -> None`: List drift ledgers.
- @app.command(improvements) `list_improvements(root, status, severity, tag, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog improvements with optional filtering.

Shortcut for: list backlog --kind improvement

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(issues) `list_issues(root, status, severity, tag, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog issues with optional filtering.

Shortcut for: list backlog --kind issue

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(problems) `list_problems(root, status, severity, tag, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog problems with optional filtering.

Shortcut for: list backlog --kind problem

By default, resolved/implemented items are excluded. Use --all to show all.
- @app.command(risks) `list_risks(root, status, severity, tag, substring, json_output, regexp, case_insensitive, format_type, truncate, order, prioritize, show_all, limit, pager, external) -> None`: List backlog risks with optional filtering.

Shortcut for: list backlog --kind risk

By default, resolved/implemented items are excluded. Use --all to show all.
