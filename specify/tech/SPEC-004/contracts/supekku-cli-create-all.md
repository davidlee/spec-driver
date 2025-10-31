# supekku.cli.create

Create commands for specs, deltas, requirements, revisions, and ADRs.

## Constants

- `ROOT` - Add parent to path for imports
- `app`

## Functions

- @app.command(adr) `create_adr(title, status, author, author_email, root) -> None`: Create a new ADR with the next available ID.
- @app.command(delta) `create_delta_cmd(name, specs, requirements, allow_missing_plan) -> None`: Create a Delta bundle with optional plan scaffolding.
- @app.command(requirement) `create_requirement(spec, requirement, title, kind) -> None`: Create a breakout requirement file under a spec.
- @app.command(revision) `create_revision_cmd(name, source_specs, destination_specs, requirements) -> None`: Create a Spec Revision bundle.
- @app.command(spec) `create_spec(spec_name, spec_type, testing, json_output) -> None`: Create a new SPEC or PROD document bundle from templates.
