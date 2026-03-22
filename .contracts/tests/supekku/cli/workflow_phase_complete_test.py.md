# supekku.cli.workflow_phase_complete_test

Tests for phase complete CLI command (DR-102 §5, §6, §7).

Tests phase completion, auto-handoff emission, bridge block integration.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

Args:
  phase_frontmatter: If True, generate phase files with proper frontmatter
    (status: draft) so update_frontmatter_status can operate on them.

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

### PhaseFrontmatterTest

Test that phase complete updates phase sheet frontmatter (DE-104).

**Inherits from:** _PhaseCompleteTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_phase_complete_tolerates_missing_frontmatter(self) -> None`: Phase complete succeeds when phase file has no frontmatter status.
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_phase_complete_updates_frontmatter_to_completed(self) -> None`: Phase complete writes 'completed' to phase sheet frontmatter (DEC-104-08).
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_state_yaml_still_uses_complete(self) -> None`: state.yaml uses control-plane vocabulary ('complete'), not lifecycle.

### _PhaseCompleteTestBase

Common setup.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_start_phase(self, delta_id) -> None`
