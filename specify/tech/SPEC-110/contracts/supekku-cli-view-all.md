# supekku.cli.view

View commands for opening artifacts in a pager.

## Constants

- `app`

## Functions

- @app.command(adr) `view_adr(decision_id, root) -> None`: View ADR in pager.
- @app.command(card) `view_card(card_id, anywhere, root) -> None`: View card in pager.
- @app.command(delta) `view_delta(delta_id, root) -> None`: View delta in pager.
- @app.command(policy) `view_policy(policy_id, root) -> None`: View policy in pager.
- @app.command(requirement) `view_requirement(req_id, root) -> None`: View requirement's spec file in pager.
- @app.command(revision) `view_revision(revision_id, root) -> None`: View revision in pager.
- @app.command(spec) `view_spec(spec_id, root) -> None`: View specification in pager.
- @app.command(standard) `view_standard(standard_id, root) -> None`: View standard in pager.
