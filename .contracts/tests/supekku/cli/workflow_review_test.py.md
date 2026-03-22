# supekku.cli.workflow_review_test

Tests for review CLI commands (DR-102 §3.3, §3.4, §5, §8).

Tests review prime, review complete, and review teardown.

## Functions

- `_create_delta_bundle(root, delta_id, slug, plan_id, phases) -> Path`: Create a minimal delta bundle for testing.

## Classes

### FindingDispositionJsonTest

Tests for review finding disposition commands with --format json.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_disposition_not_found_json(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_resolve_json(self) -> None`

### FindingListJsonTest

Tests for review finding list command.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_list_human_output(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_list_json_all_rounds(self) -> None`
- `test_list_json_no_findings(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_list_json_round_filter(self) -> None`

### ReviewCompleteJsonTest

Tests for review complete --format json.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_complete_json_changes_requested(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_complete_json_guard_violation(self) -> None`: Approve with open blocking finding → exit 3, guard_violation.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_complete_json_invalid_status(self) -> None`: Invalid status value → exit 2, precondition.
- `test_complete_json_precondition_no_state(self) -> None`

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

### ReviewEndToEndTest

End-to-end: prime → complete(changes_requested) → resolve → re-prime → approve.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_multi_round_with_disposition_and_approval(self) -> None`: VT-109-009: Full multi-round review lifecycle.

### ReviewFindingDeferTest

Test `spec-driver review finding defer`.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_defer_blocking_with_backlog_ref(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_defer_with_rationale(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_defer_without_rationale_fails(self) -> None`

### ReviewFindingResolveTest

Test `spec-driver review finding resolve`.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_finding_not_found_shows_available_ids(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_overwrites_existing_disposition(self) -> None`: Re-dispositioning overwrites previous (latest wins).
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_resolve_blocking_finding(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_resolve_non_blocking_without_resolved_at(self) -> None`: Non-blocking findings can be resolved without --resolved-at.

### ReviewFindingSupersedeTest

Test `spec-driver review finding supersede`.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_supersede_finding(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_supersede_without_superseded_by_fails(self) -> None`

### ReviewFindingWaiveTest

Test `spec-driver review finding waive`.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_waive_blocking_requires_authority_user(self) -> None`: Waiving a blocking finding requires --authority user.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_waive_with_authority_user(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_waive_with_rationale(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_waive_without_rationale_fails(self) -> None`

### ReviewGuardEnforcementTest

Test review complete --status approved enforces can_approve() guard.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_approve_allowed_with_user_waive(self) -> None`: User-waived blocking finding with rationale allows approval.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_approve_blocked_by_agent_waive(self) -> None`: Agent-waived blocking finding still blocks approval.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_approve_blocked_by_open_blocking_finding(self) -> None`: Cannot approve with undispositioned blocking findings.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_approve_succeeds_after_resolving_blocking(self) -> None`: Approve succeeds when all blocking findings are resolved.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_changes_requested_ignores_guard(self) -> None`: changes_requested does not require guard to pass.

### ReviewJudgmentStatusTest

Test judgment_status written to review-index.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_complete_writes_judgment_to_index(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_prime_sets_judgment_in_progress(self) -> None`

### ReviewPrimeJsonTest

Tests for review prime --format json.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_prime_json_full_sha(self) -> None`: JSON output uses full 40-char SHA (DEC-108-002).
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_prime_json_no_stderr(self) -> None`: JSON mode produces no stderr output.
- `test_prime_json_precondition_no_state(self) -> None`: No workflow state → exit 2, precondition error.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_prime_json_success(self) -> None`

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

### ReviewSummaryTest

Test --summary wired into round metadata.

**Inherits from:** \_FindingTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_no_summary_omits_key(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_summary_stored_in_round(self) -> None`

### ReviewTeardownJsonTest

Tests for review teardown --format json.

**Inherits from:** \_ReviewTestBase

#### Methods

- `test_teardown_json_nothing_to_delete(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_teardown_json_success(self) -> None`

### ReviewTeardownTest

Test `spec-driver review teardown`.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_deletes_findings_too(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_deletes_reviewer_state(self) -> None`
- `test_teardown_with_no_state(self) -> None`
- `test_teardown_without_delta_fails(self) -> None`

### WorkflowStatusJsonTest

Tests for workflow status --format json.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_status_json_no_review_index(self) -> None`: Status without review → cold bootstrap, not_started judgment.
- `test_status_json_no_state(self) -> None`: No workflow state → precondition error.
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_status_json_with_review(self) -> None`: Status with primed review shows full review state.

### WriteOrderTest

Test write ordering per DR-102 §5.

**Inherits from:** \_ReviewTestBase

#### Methods

- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_review_complete_creates_findings_and_updates_state(self) -> None`
- @patch(supekku.scripts.lib.core.git.get_head_sha, return_value=<BinOp>) `test_review_prime_creates_both_files(self) -> None`

### \_FindingTestBase

Base for tests needing findings with blocking/non-blocking items.

**Inherits from:** \_ReviewTestBase

#### Methods

- @staticmethod `_finding(finding_id, title, summary) -> dict`: Build a minimal finding dict that passes schema validation.
- `_setup_review_with_findings(self, delta_id, blocking, non_blocking) -> Path`: Set up a delta in reviewing state with v2 findings.

### \_ReviewTestBase

Common setup for review tests.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `_create_handoff_and_accept_as_reviewer(self, delta_id) -> None`: Create handoff to reviewer and accept it.
- `_start_phase(self, delta_id) -> None`
