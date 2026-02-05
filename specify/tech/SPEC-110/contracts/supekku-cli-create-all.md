# supekku.cli.create

Create commands for specs, deltas, requirements, revisions, and ADRs.

## Constants

- `app`

## Functions

- @app.command(adr) `create_adr(title, status, author, author_email, root) -> None`: Create a new ADR with the next available ID.
- @app.command(card) `create_card(description, lane, root) -> None`: Create a new kanban card with the next available ID.
- @app.command(delta) `create_delta_cmd(name, specs, requirements, allow_missing_plan, from_backlog) -> None`: Create a Delta bundle with optional plan scaffolding.

Can create from scratch with a title, or populate from a backlog item
using --from-backlog.
- @app.command(improvement) `create_improvement(title, json_output, root) -> None`: Create a new improvement backlog entry.
- @app.command(issue) `create_issue(title, json_output, root) -> None`: Create a new issue backlog entry.
- @app.command(phase) `create_phase_cmd(name, plan, root) -> None`: Create a new phase for an implementation plan.
- @app.command(policy) `create_policy(title, status, author, author_email, root) -> None`: Create a new policy with the next available ID.
- @app.command(problem) `create_problem(title, json_output, root) -> None`: Create a new problem backlog entry.
- @app.command(requirement) `create_requirement(spec, requirement, title, kind) -> None`: Create a breakout requirement file under a spec.
- @app.command(revision) `create_revision_cmd(name, source_specs, destination_specs, requirements) -> None`: Create a Spec Revision bundle.
- @app.command(risk) `create_risk(title, json_output, root) -> None`: Create a new risk backlog entry.
- @app.command(spec) `create_spec(spec_name, spec_type, testing, json_output) -> None`: Create a new SPEC or PROD document bundle from templates.
- @app.command(standard) `create_standard(title, status, author, author_email, root) -> None`: Create a new standard with the next available ID.
