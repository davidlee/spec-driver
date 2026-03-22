# supekku.cli.workflow_review_test

Tests for review CLI commands (DR-102 §3.3, §3.4, §5, §8).

Tests review prime, review complete, and review teardown.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

## Classes

### ReviewCompleteTest

Test `spec-driver review complete`.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_auto_teardown_on_approved(self) -> None`: Default policy tears down reviewer state on approved.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_fails_when_not_reviewing(self) -> None`: Cannot complete review when not in reviewing state.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_increments_round_number(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_records_reviewer_role(self) -> None`
- `test_rejects_invalid_status(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_transitions_to_approved(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_transitions_to_changes_requested(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_with_summary(self) -> None`

### ReviewPrimeTest

Test `spec-driver review prime`.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_creates_bootstrap_markdown(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_creates_review_index(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_domain_map_includes_delta_docs(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_domain_map_includes_phase_sheets(self) -> None`
- `test_fails_without_state(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_records_source_handoff(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_rerun_updates_cache_key(self) -> None`: Re-running review prime updates the cache key.

### ReviewTeardownTest

Test `spec-driver review teardown`.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_deletes_findings_too(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_deletes_reviewer_state(self) -> None`
- `test_teardown_with_no_state(self) -> None`
- `test_teardown_without_delta_fails(self) -> None`

### WriteOrderTest

Test write ordering per DR-102 §5.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_review_complete_creates_findings_and_updates_state(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_review_prime_creates_both_files(self) -> None`

### \_ReviewTestBase

Common setup for review tests.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_create_handoff_and_accept_as_reviewer(self, delta_id) -> None`: Create handoff to reviewer and accept it.
- `_start_phase(self, delta_id) -> None`
