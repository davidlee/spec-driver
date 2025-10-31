# supekku.cli.complete

Complete commands for marking deltas as completed.

## Constants

- `ROOT` - Add parent to path for imports
- `app`

## Functions

- @app.command(delta) `complete_delta(delta_id, dry_run, force, skip_sync, skip_update_requirements) -> None`: Complete a delta and transition associated requirements to live status.

Marks a delta as completed and optionally updates associated requirements
to 'live' status in revision source files.
