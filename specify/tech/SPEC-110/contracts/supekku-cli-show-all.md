# supekku.cli.show

Show commands for displaying detailed information about artifacts.

## Constants

- `app`

## Functions

- @app.command(adr) `show_adr(decision_id, root) -> None`: Show detailed information about a specific decision/ADR.
- @app.command(delta) `show_delta(delta_id, root) -> None`: Show detailed information about a delta.
- @app.command(requirement) `show_requirement(req_id, root) -> None`: Show detailed information about a requirement.
- @app.command(revision) `show_revision(revision_id, root) -> None`: Show detailed information about a revision.
- @app.command(spec) `show_spec(spec_id, root) -> None`: Show detailed information about a specification.
