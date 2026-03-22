# supekku.cli.workflow_test

Tests for workflow CLI commands (DR-102 §5).

Tests phase start, workflow status, block/unblock via CliRunner.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

## Classes

### BlockUnblockTest

Test `spec-driver block` / `spec-driver unblock`.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_block_already_blocked_fails(self) -> None`
- `test_block_transitions_to_blocked(self) -> None`
- `test_block_with_reason(self) -> None`
- `test_block_without_state_fails(self) -> None`
- `test_unblock_not_blocked_fails(self) -> None`
- `test_unblock_restores_previous_state(self) -> None`
- `test_workflow_status_shows_blocked(self) -> None`

### PhaseStartTest

Test `spec-driver phase start`.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_auto_discovers_latest_phase(self) -> None`
- `test_creates_state_yaml(self) -> None`
- `test_explicit_phase_override(self) -> None`
- `test_frontmatter_tolerates_no_status_field(self) -> None`: phase start succeeds when phase file lacks frontmatter status.
- `test_idempotent_when_already_implementing(self) -> None`
- `test_no_phases_dir_with_explicit_phase(self) -> None`: phase start works with --phase even if phases/ is empty.
- `test_records_plan_info(self) -> None`
- `test_unknown_delta_fails(self) -> None`
- `test_updates_phase_frontmatter_to_in_progress(self) -> None`: phase start writes 'in-progress' to phase sheet frontmatter (DE-104).

### TopLevelBlockTest

Verify block/unblock work as top-level commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_block_is_top_level(self) -> None`: block is accessible as `spec-driver block`, not `spec-driver workflow block`.
- `test_unblock_is_top_level(self) -> None`

### WorkflowStatusTest

Test `spec-driver workflow status`.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_displays_phase_info(self) -> None`
- `test_displays_status(self) -> None`
- `test_no_state_reports_gracefully(self) -> None`
