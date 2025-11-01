# supekku.scripts.complete_delta

Complete a delta and transition associated requirements to live status.

## Constants

- `ROOT`

## Functions

- `build_parser() -> argparse.ArgumentParser`: Build argument parser.
- `collect_requirements_to_update(_delta_id, delta, workspace)`: Collect and validate requirements associated with the delta.

Returns tuple of (requirements_to_update, error_occurred).
- `complete_delta(delta_id) -> int`: Complete a delta and transition requirements to live status.

Args:
    delta_id: Delta identifier (e.g., DE-004)
    dry_run: Preview changes without applying them
    force: Skip all prompts
    skip_sync: Skip spec sync prompt/check
    update_requirements: If True (default), update requirements to 'live' status
                       in revision source files (persistent). Creates completion
                       revision for untracked requirements. If False, only marks
                       delta as completed without updating requirements.

Returns:
    Exit code (0 for success, non-zero for errors) - Rationale: Main workflow orchestration with multiple validation/error-handling paths
- `display_actions(_delta, requirements_to_update, update_requirements) -> None`: Display actions that will be performed.
- `display_dry_run_requirements(requirements_to_update, update_requirements) -> None`: Display requirements that would be updated in dry-run mode.
- `display_preview(_delta_id, _delta, requirements_to_update, dry_run) -> None`: Display preview of changes to be made.
- `handle_already_completed_delta(delta_id, requirements_to_update, workspace, dry_run, force, update_requirements) -> int`: Handle the case where delta is already completed.

Ensures requirements are in the correct state (idempotent operation).
Returns exit code. - Rationale: Workflow orchestration requires multiple control flags
- `main(argv) -> int`: Main entry point.
- `prompt_spec_sync(skip_sync, dry_run, force) -> bool`: Prompt for spec sync and optionally run it.

Returns True if successful or skipped, False if sync failed.
- `prompt_yes_no(question, default) -> bool`: Prompt user for yes/no answer.
- `run_spec_sync() -> bool`: Run spec sync command and return success status.
- `update_delta_frontmatter(delta_path, _delta_id) -> bool`: Update delta status in frontmatter to 'completed'.

Returns True if successful, False otherwise.
- `update_requirements_in_revision_sources(delta_id, requirement_ids, workspace) -> bool`: Update requirement lifecycle status in revision source files (persistent).

Returns True if successful, False on error. - user interaction, and updates
- `update_requirements_status(requirements_to_update, requirements_registry, silent) -> None`: Update requirement statuses to live (registry only - ephemeral).
- `validate_delta_status(_delta_id, delta, force, dry_run) -> tuple[Tuple[bool, bool]]`: Validate delta status is appropriate for completion.

Returns tuple of (should_continue, already_completed).
