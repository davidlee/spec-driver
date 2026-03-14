# supekku.cli.edit

Edit commands for opening artifacts in an editor or updating status.

## Constants

- `StatusOption`
- `TagOption`
- `UntagOption`
- `app`

## Functions

- @app.command(adr) `edit_adr(decision_id, status, tag, untag, root) -> None`: Edit ADR in editor.
- @app.command(audit) `edit_audit(audit_id, status, tag, untag, root) -> None`: Edit audit in editor.
- @app.command(backlog) `edit_backlog(item_id, status, tag, untag, root) -> None`: Edit a backlog item (issue, problem, improvement, or risk).
- @app.command(card) `edit_card(card_id, status, tag, untag, anywhere, root) -> None`: Edit card in editor.
- @app.command(delta) `edit_delta(delta_id, status, tag, untag, root) -> None`: Edit delta in editor.
- @app.command(drift) `edit_drift(ledger_id, status, tag, untag, root) -> None`: Edit drift ledger in editor.
- @app.command(improvement) `edit_improvement(improvement_id, status, tag, untag, root) -> None`: Edit improvement in editor.
- @app.command(issue) `edit_issue(issue_id, status, tag, untag, root) -> None`: Edit issue in editor.
- @app.command(memory) `edit_memory(memory_id, status, tag, untag, verify, root) -> None`: Edit memory record in editor.
- @app.command(plan) `edit_plan(plan_id, status, tag, untag, root) -> None`: Edit implementation plan in editor.
- @app.command(policy) `edit_policy(policy_id, status, tag, untag, root) -> None`: Edit policy in editor.
- @app.command(problem) `edit_problem(problem_id, status, tag, untag, root) -> None`: Edit problem in editor.
- @app.command(requirement) `edit_requirement(req_id, status, tag, untag, root) -> None`: Edit requirement's spec file in editor.
- @app.command(revision) `edit_revision(revision_id, status, tag, untag, root) -> None`: Edit revision in editor.
- @app.command(risk) `edit_risk(risk_id, status, tag, untag, root) -> None`: Edit risk in editor.
- @app.command(spec) `edit_spec(spec_id, status, tag, untag, root) -> None`: Edit specification in editor.
- @app.command(standard) `edit_standard(standard_id, status, tag, untag, root) -> None`: Edit standard in editor.
