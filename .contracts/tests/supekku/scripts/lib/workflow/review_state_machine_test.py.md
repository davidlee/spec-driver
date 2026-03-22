# supekku.scripts.lib.workflow.review_state_machine_test

Tests for review lifecycle state machine (DR-109).

Covers: bootstrap derivation (VT-109-001), judgment transitions (VT-109-002),
approval guard + disposition constraints (VT-109-003), status derivation
(VT-109-006), and cross-round collection (VT-109-007).

## Functions

- `_disposition(action, authority) -> FindingDisposition`: Build a FindingDisposition for tests.
- `_finding(finding_id, title, disposition) -> ReviewFinding`: Build a ReviewFinding for tests.
- `_warm_index() -> dict`: Build a minimal valid review-index dict in WARM state.

## Classes

### ApprovalGuardTest

can_approve() (DR-109 §3.3).

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_resolved_can_approve(self) -> None`
- `test_deferred_by_agent_cannot_approve(self) -> None`
- `test_deferred_by_user_with_backlog_ref_can_approve(self) -> None`
- `test_deferred_without_backlog_ref_cannot_approve(self) -> None`
- `test_fix_without_resolved_at_cannot_approve(self) -> None`
- `test_multiple_findings_all_must_pass(self) -> None`
- `test_no_blocking_findings_can_approve(self) -> None`
- `test_open_blocking_cannot_approve(self) -> None`
- `test_superseded_can_approve(self) -> None`
- `test_waive_by_agent_produces_two_reasons(self) -> None`: Agent waive without rationale: both authority and rationale fail.
- `test_waived_by_agent_cannot_approve(self) -> None`
- `test_waived_by_user_with_rationale_can_approve(self) -> None`
- `test_waived_by_user_without_rationale_cannot_approve(self) -> None`

### BootstrapDerivationTest

derive_bootstrap_status() (DR-109 §3.2).

**Inherits from:** unittest.TestCase

#### Methods

- `test_commit_drift_only_returns_reusable(self) -> None`
- `test_current_index_returns_warm(self) -> None`
- `test_deleted_domain_files_returns_invalid(self) -> None`
- `test_dependency_surface_expansion_returns_stale(self) -> None`
- `test_no_index_returns_cold(self) -> None`
- `test_phase_boundary_crossing_returns_stale(self) -> None`
- `test_schema_id_mismatch_returns_invalid(self) -> None`
- `test_schema_version_mismatch_returns_invalid(self) -> None`

### BootstrapEnumTest

BootstrapStatus enum values (DR-109 §3.2).

**Inherits from:** unittest.TestCase

#### Methods

- `test_expected_values(self) -> None`
- `test_five_values(self) -> None`
- `test_warming_not_present(self) -> None`

### BootstrapValidityMatrixTest

Validity matrix assertions (DR-109 §3.2).

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_valid_pairs_covered(self) -> None`: Every pair in VALID_BOOTSTRAP_TRANSITIONS should be reachable.
- `test_cold_to_cold_is_valid(self) -> None`
- `test_cold_to_reusable_is_illegal(self) -> None`
- `test_invalid_to_reusable_is_illegal(self) -> None`
- `test_stale_to_warm_is_valid(self) -> None`
- `test_warm_to_cold_is_illegal(self) -> None`
- `test_warm_to_stale_is_valid(self) -> None`

### CrossRoundCollectionTest

collect_blocking_findings() (DR-109 §3.7).

**Inherits from:** unittest.TestCase

#### Methods

- `test_cross_round_dispositioned_finding_unblocks(self) -> None`: Round 1 finding fixed in-place allows approval.
- `test_cross_round_guard_integration(self) -> None`: Round 1 undispositioned blocking finding blocks approval in round 2.
- `test_disposition_preserved_from_originating_round(self) -> None`: Disposition applied in-place in originating round is collected.
- `test_empty_rounds(self) -> None`
- `test_multi_round_collects_all(self) -> None`
- `test_round_with_no_blocking_key(self) -> None`
- `test_single_round_collects_blocking(self) -> None`

### FindingDispositionModelTest

FindingDisposition Pydantic model.

**Inherits from:** unittest.TestCase

#### Methods

- `test_extra_fields_ignored(self) -> None`
- `test_from_dict(self) -> None`
- `test_minimal_construction(self) -> None`

### JudgmentTransitionTest

apply_review_transition() (DR-109 §3.3).

**Inherits from:** unittest.TestCase

#### Methods

- `test_approved_to_in_progress_rejected(self) -> None`
- `test_changes_requested_to_approved_rejected(self) -> None`
- `test_changes_requested_to_in_progress(self) -> None`
- `test_error_carries_context(self) -> None`
- `test_in_progress_to_approved(self) -> None`
- `test_in_progress_to_changes_requested(self) -> None`
- `test_not_started_to_approved_rejected(self) -> None`
- `test_not_started_to_in_progress(self) -> None`

### ReviewEnumTest

ReviewStatus enum values (DR-109 §3.3).

**Inherits from:** unittest.TestCase

#### Methods

- `test_blocked_not_present(self) -> None`
- `test_four_values(self) -> None`

### ReviewFindingModelTest

ReviewFinding Pydantic model.

**Inherits from:** unittest.TestCase

#### Methods

- `test_extra_fields_ignored(self) -> None`
- `test_from_dict_with_disposition(self) -> None`
- `test_minimal_construction(self) -> None`

### StatusDerivationTest

derive_finding_status() (DR-109 §3.4).

**Inherits from:** unittest.TestCase

#### Methods

- `test_defer_returns_open(self) -> None`
- `test_fix_returns_resolved(self) -> None`
- `test_no_disposition_returns_open(self) -> None`
- `test_supersede_returns_superseded(self) -> None`
- `test_waive_returns_waived(self) -> None`
