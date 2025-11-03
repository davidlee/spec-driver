# supekku.cli.complete

Complete commands for marking deltas as completed.

## Constants

- `app`

## Functions

- @app.command(delta) `complete_delta(delta_id, dry_run, force, skip_sync, skip_update_requirements) -> None`: Complete a delta and transition associated requirements to active status.

Marks a delta as completed and optionally updates associated requirements
to 'active' status in revision source files.
