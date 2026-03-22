# supekku.scripts.lib.workflow.state_machine

Workflow state machine with explicit CLI-driven transitions.

Implements the 7-state machine from DR-102 §4.  All transitions are
triggered by explicit CLI commands — no implicit triggers.

States:
  planned, implementing, awaiting_handoff, reviewing,
  changes_requested, approved, blocked.

Design authority: DR-102 §4.

## Constants

- `_ACCEPT_HANDOFF_SOURCES` - States from which ACCEPT_HANDOFF is valid
- `_BLOCK_EXCLUDED` - States that cannot be blocked (already terminal or transitional)
- `_C`
- `_S` - ---------------------------------------------------------------------------

## Functions

- `apply_transition(current, command) -> TransitionResult`: Apply a transition command to the current state.

Args:
  current: Current workflow state.
  command: Transition command to apply.
  to_role: Target role (required for ACCEPT_HANDOFF).
  previous_state: State before blocking (required for UNBLOCK).

Returns:
  TransitionResult with previous and new states.

Raises:
  TransitionError: If the transition is invalid.
- `check_claim(current_claimant, requested_by) -> None`: Check the claim guard for handoff acceptance.

Args:
  current_claimant: Current claimed_by value (None if unclaimed).
  requested_by: Identity requesting the claim.

Raises:
  ClaimError: If claimed by a different identity.

No-op if unclaimed or same identity (idempotent).

## Classes

### ClaimError

Raised when a claim guard check fails.

**Inherits from:** Exception

#### Methods

- `__init__(self, current_claimant, requested_by) -> None`

### TransitionCommand

CLI commands that trigger state transitions (DR-102 §4/§5).

**Inherits from:** StrEnum

### TransitionError

Raised when a state transition is invalid.

**Inherits from:** Exception

#### Methods

- `__init__(self, current, command, message) -> None`

### TransitionResult

Result of a successful state transition.

### WorkflowState

Workflow orchestration states (DR-102 §4).

**Inherits from:** StrEnum
