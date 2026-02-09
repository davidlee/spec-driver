# supekku.cli.edit

Edit commands for opening artifacts in an editor.

## Constants

- `app`

## Functions

- @app.command(adr) `edit_adr(decision_id, root) -> None`: Edit ADR in editor.
- @app.command(card) `edit_card(card_id, anywhere, root) -> None`: Edit card in editor.
- @app.command(delta) `edit_delta(delta_id, root) -> None`: Edit delta in editor.
- @app.command(policy) `edit_policy(policy_id, root) -> None`: Edit policy in editor.
- @app.command(requirement) `edit_requirement(req_id, root) -> None`: Edit requirement's spec file in editor.
- @app.command(revision) `edit_revision(revision_id, root) -> None`: Edit revision in editor.
- @app.command(spec) `edit_spec(spec_id, root) -> None`: Edit specification in editor.
- @app.command(standard) `edit_standard(standard_id, root) -> None`: Edit standard in editor.
