# supekku.cli.show

Show commands for displaying detailed information about artifacts.

## Constants

- `app`

## Functions

- @app.command(adr) `show_adr(decision_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a specific decision/ADR.
- @app.command(audit) `show_audit(audit_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about an audit.
- @app.command(backlog) `show_backlog(item_id, json_output, path_only, raw_output, content_type, root) -> None`: Show a backlog item (issue, problem, improvement, or risk).
- @app.command(card) `show_card(card_id, json_output, path_only, raw_output, anywhere, content_type, root) -> None`: Show detailed information about a specific card.
- @app.command(delta) `show_delta(delta_id, json_output, path_only, raw_output, related, content_type, root) -> None`: Show detailed information about a delta.
- @app.command(drift) `show_drift(ledger_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a drift ledger.
- @app.command(improvement) `show_improvement(improvement_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about an improvement.
- @app.command(inferred, hidden=True) `show_inferred(ctx, json_output, path_only, raw_output, root) -> None`: Show an artifact by inferring its type from the ID.
- @app.command(issue) `show_issue(issue_id, json_output, path_only, raw_output, related, content_type, root) -> None`: Show detailed information about an issue. - noqa: PLR0913
- @app.command(memory) `show_memory(memory_id, json_output, path_only, raw_output, body_only, links_depth, tree, content_type, root) -> None`: Show detailed information about a specific memory record. - noqa: PLR0913
- @app.command(plan) `show_plan(plan_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about an implementation plan.
- @app.command(policy) `show_policy(policy_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a specific policy.
- @app.command(problem) `show_problem(problem_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a problem.
- @app.command(relations) `show_relations(artifact_id, direction, json_output, root) -> None`: Show cross-artifact reference neighbourhood for an artifact.

Displays all artifacts that this ID references (forward) and/or
all artifacts that reference this ID (inverse), grouped by type.

If the ID is not found as a node, still shows any inverse edges
(other artifacts may reference a non-existent ID). Emits a warning
if the ID itself is not a known artifact.

- @app.command(requirement) `show_requirement(req_id, json_output, path_only, raw_output, related, content_type, root) -> None`: Show detailed information about a requirement. - noqa: PLR0913
- @app.command(revision) `show_revision(revision_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a revision.
- @app.command(risk) `show_risk(risk_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a risk.
- @app.command(schema) `show_schema_cmd(block_type, format_type) -> None`: Show schema details for a block type or frontmatter kind.
- @app.command(spec) `show_spec(spec_id, json_output, path_only, raw_output, requirements, related, content_type, root) -> None`: Show detailed information about a specification. - noqa: PLR0913
- @app.command(standard) `show_standard(standard_id, json_output, path_only, raw_output, content_type, root) -> None`: Show detailed information about a specific standard.
- @app.command(template) `show_template(kind, json_output, root) -> None`: Show the specification template for a given kind.
