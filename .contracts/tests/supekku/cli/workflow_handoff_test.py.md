# supekku.cli.workflow_handoff_test

Tests for create handoff / accept handoff CLI commands (DR-102 §4/§5).

Tests handoff creation, payload assembly, claim guard,
write ordering, and re-run safety.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

## Classes

### AcceptHandoffTest

Test `spec-driver accept handoff`.

**Inherits from:** \_HandoffTestBase

#### Methods

- `test_accept_defaults_identity_to_user(self) -> None`
- `test_accept_not_awaiting_fails(self) -> None`: Cannot accept handoff when not in awaiting_handoff state.
- `test_accept_transitions_to_implementing(self) -> None`
- `test_accept_transitions_to_reviewing(self) -> None`
- `test_accept_without_handoff_fails(self) -> None`
- `test_claim_guard_idempotent_same_identity(self) -> None`
- `test_claim_guard_rejects_different_identity(self) -> None`
- `_create_handoff(self, to_role, delta_id) -> None`

### CreateHandoffTest

Test `spec-driver create handoff`.

**Inherits from:** \_HandoffTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_assembles_required_reading(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=feat-x) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=True) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=True) `test_captures_git_state(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_clears_claimed_by(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_creates_handoff_yaml(self) -> None`
- `test_fails_from_planned_state(self) -> None`: Cannot create handoff before phase start.
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_infers_review_activity_for_reviewer(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_rerun_is_idempotent(self) -> None`: Re-running create handoff overwrites cleanly.
- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_transitions_to_awaiting_handoff(self) -> None`

### WriteOrderTest

Test write ordering per DR-102 §5.

**Inherits from:** \_HandoffTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_branch, return_value=main) @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) @patch(supekku.scripts.lib.core.git.has_staged_changes, return_value=False) @patch(supekku.scripts.lib.core.git.has_uncommitted_changes, return_value=False) `test_handoff_written_before_state(self) -> None`: handoff.current.yaml must be written before state.yaml.

### \_HandoffTestBase

Common setup for handoff tests.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_start_phase(self, delta_id) -> None`
