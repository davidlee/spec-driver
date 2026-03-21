# supekku.cli.workflow_phase_complete_test

Tests for phase complete CLI command (DR-102 §5, §6, §7).

Tests phase completion, auto-handoff emission, bridge block integration.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

## Classes

### PhaseBridgeIntegrationTest

Test phase-bridge block integration with phase complete.

**Inherits from:** _PhaseCompleteTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_bridge_handoff_ready_false_suppresses(self) -> None`: Phase-bridge with handoff_ready: false suppresses auto-handoff.
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_bridge_handoff_ready_true(self) -> None`: Phase-bridge with handoff_ready triggers handoff.
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_idempotent_rerun(self) -> None`: Re-running phase complete with already-complete phase still works.

### PhaseCompleteBasicTest

Test basic phase complete behaviour.

**Inherits from:** _PhaseCompleteTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_auto_handoff_by_default(self) -> None`: Default policy emits handoff on phase complete.
- `test_fails_when_not_implementing(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_marks_phase_complete(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_no_handoff_flag(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_to_role_override(self) -> None`

### _PhaseCompleteTestBase

Common setup.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_start_phase(self, delta_id) -> None`
