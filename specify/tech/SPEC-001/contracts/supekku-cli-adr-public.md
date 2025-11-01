# supekku.cli.adr

ADR (Architecture Decision Record) management commands.

## Constants

- `app`

## Functions

- @app.command(list) `list_decisions(root, status, tag, spec, delta, requirement, policy) -> None`: List decisions with optional filtering.
- @app.command(new) `new(title, root, status, author, author_email) -> None`: Create a new ADR with the next available ID.
- @app.command(show) `show(decision_id, root) -> None`: Show detailed information about a specific decision.
- @app.command(sync) `sync(root) -> None`: Sync decision registry from ADR files.
