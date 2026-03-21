# supekku.scripts.lib.workflow.state_machine_test

Tests for workflow state machine (DR-102 §4).

Validates all transitions, rejection of invalid transitions,
claim guard semantics, and edge cases.

## Constants

- `_C`
- `_S`

## Classes

### BlockUnblockTest

Block/unblock transitions (DR-102 §4).

**Inherits from:** unittest.TestCase

#### Methods

- `test_block_already_blocked_fails(self) -> None`
- `test_block_from_any_non_blocked_state(self) -> None`
- `test_unblock_not_blocked_fails(self) -> None`
- `test_unblock_restores_previous_state(self) -> None`
- `test_unblock_without_previous_state_fails(self) -> None`

### ClaimGuardTest

Claim guard semantics (DR-102 §4).

**Inherits from:** unittest.TestCase

#### Methods

- `test_claim_error_message(self) -> None`
- `test_different_identity_raises(self) -> None` - Should not raise
- `test_same_identity_is_idempotent(self) -> None` - Should not raise
- `test_unclaimed_allows_claim(self) -> None`

### InvalidTransitionTest

Invalid transitions are rejected.

**Inherits from:** unittest.TestCase

#### Methods

- `test_accept_handoff_requires_to_role(self) -> None`
- `test_approved_rejects_create_handoff(self) -> None`
- `test_implementing_rejects_accept_handoff(self) -> None`
- `test_planned_rejects_create_handoff(self) -> None`
- `test_reviewing_rejects_phase_start(self) -> None`

### TransitionErrorTest

TransitionError carries context.

**Inherits from:** unittest.TestCase

#### Methods

- `test_error_has_current_and_command(self) -> None`

### TransitionTableTest

Valid transitions from DR-102 §4.

**Inherits from:** unittest.TestCase

#### Methods

- `test_accept_handoff_to_implementing(self) -> None`
- `test_accept_handoff_to_implementing_for_architect(self) -> None`
- `test_accept_handoff_to_implementing_for_operator(self) -> None`
- `test_accept_handoff_to_reviewing(self) -> None`
- `test_changes_requested_to_awaiting_handoff(self) -> None`
- `test_implementing_to_awaiting_handoff(self) -> None`
- `test_planned_to_implementing(self) -> None`
- `test_review_complete_approved(self) -> None`
- `test_review_complete_changes_requested(self) -> None`

### WorkflowStateEnumTest

WorkflowState enum values match DR-102 §4.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_seven_states(self) -> None`
