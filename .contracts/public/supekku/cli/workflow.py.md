# supekku.cli.workflow

Workflow orchestration CLI commands.

Thin CLI layer for the workflow control plane (DR-102 §5).
Delegates to domain logic in `supekku.scripts.lib.workflow`.

Commands:
phase start — initialise workflow/state.yaml (planned → implementing)
workflow status — read and display human-readable workflow state
block / unblock — transition to/from blocked
create handoff — write handoff.current.yaml, transition to awaiting_handoff
accept handoff — claim + transition to implementing/reviewing
review prime — generate review-index.yaml + review-bootstrap.md
review complete — write review-findings.yaml, transition state
review teardown — delete reviewer state files

## Constants

- `accept_app`
- `phase_app`
- `review_app` - ---------------------------------------------------------------------------
- `workflow_app` - ---------------------------------------------------------------------------

## Functions

- @accept_app.command(handoff) `accept_handoff_command(delta, identity, root) -> None`: Accept a pending handoff, claiming it with identity guard.
- @workflow_app.command(block) `block_command(delta, reason, root) -> None`: Block a delta's workflow.
- `create_handoff_command(delta, to_role, next_kind, next_summary, root) -> None`: Create a structured handoff, transitioning to awaiting_handoff.
- @phase_app.command(complete) `phase_complete_command(delta, to_role, no_handoff, root) -> None`: Mark the current phase as complete. Emits handoff per policy/bridge.
- @phase_app.command(start) `phase_start(delta, phase, root) -> None`: Initialise workflow/state.yaml for a delta (planned → implementing).
- @review_app.command(complete) `review_complete_command(delta, status, summary, root) -> None`: Complete a review round, writing findings and transitioning state.
- @review_app.command(prime) `review_prime_command(delta, root) -> None`: Generate review-index.yaml + review-bootstrap.md from current state.

Evaluates staleness of existing cache, rebuilds or incrementally
updates as appropriate per DR-102 §8.

- @review_app.command(teardown) `review_teardown_command(delta, root) -> None`: Delete reviewer state files (review-index, findings, bootstrap).
- @workflow_app.command(unblock) `unblock_command(delta, root) -> None`: Unblock a delta's workflow, restoring previous state.
- @workflow_app.command(status) `workflow_status(delta, root) -> None`: Display human-readable workflow state for a delta.
