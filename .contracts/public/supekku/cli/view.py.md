# supekku.cli.view

View commands for rendering artifacts to stdout (or pager with -p).

## Constants

- `app`

## Functions

- @app.command(adr) `view_adr(decision_id, pager, root) -> None`: View ADR.
- @app.command(audit) `view_audit(audit_id, pager, root) -> None`: View audit.
- @app.command(backlog) `view_backlog(item_id, pager, root) -> None`: View a backlog item (issue, problem, improvement, or risk).
- @app.command(card) `view_card(card_id, anywhere, pager, root) -> None`: View card.
- @app.command(delta) `view_delta(delta_id, pager, root) -> None`: View delta.
- @app.command(drift) `view_drift(ledger_id, pager, root) -> None`: View drift ledger.
- @app.command(improvement) `view_improvement(improvement_id, pager, root) -> None`: View improvement.
- @app.command(inferred, hidden=True) `view_inferred(ctx, pager, root) -> None`: View an artifact by inferring its type from the ID.
- @app.command(issue) `view_issue(issue_id, pager, root) -> None`: View issue.
- @app.command(memory) `view_memory(memory_id, pager, root) -> None`: View memory record.
- @app.command(plan) `view_plan(plan_id, pager, root) -> None`: View implementation plan.
- @app.command(policy) `view_policy(policy_id, pager, root) -> None`: View policy.
- @app.command(problem) `view_problem(problem_id, pager, root) -> None`: View problem.
- @app.command(requirement) `view_requirement(req_id, pager, root) -> None`: View requirement's spec file.
- @app.command(revision) `view_revision(revision_id, pager, root) -> None`: View revision.
- @app.command(risk) `view_risk(risk_id, pager, root) -> None`: View risk.
- @app.command(spec) `view_spec(spec_id, pager, root) -> None`: View specification.
- @app.command(standard) `view_standard(standard_id, pager, root) -> None`: View standard.
