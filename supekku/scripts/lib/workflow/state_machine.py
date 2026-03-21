"""Workflow state machine with explicit CLI-driven transitions.

Implements the 7-state machine from DR-102 §4.  All transitions are
triggered by explicit CLI commands — no implicit triggers.

States:
  planned, implementing, awaiting_handoff, reviewing,
  changes_requested, approved, blocked.

Design authority: DR-102 §4.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WorkflowState(StrEnum):
  """Workflow orchestration states (DR-102 §4)."""

  PLANNED = "planned"
  IMPLEMENTING = "implementing"
  AWAITING_HANDOFF = "awaiting_handoff"
  REVIEWING = "reviewing"
  CHANGES_REQUESTED = "changes_requested"
  APPROVED = "approved"
  BLOCKED = "blocked"


class TransitionCommand(StrEnum):
  """CLI commands that trigger state transitions (DR-102 §4/§5)."""

  PHASE_START = "phase_start"
  CREATE_HANDOFF = "create_handoff"
  ACCEPT_HANDOFF = "accept_handoff"
  REVIEW_COMPLETE_CHANGES_REQUESTED = "review_complete_changes_requested"
  REVIEW_COMPLETE_APPROVED = "review_complete_approved"
  BLOCK = "block"
  UNBLOCK = "unblock"


class TransitionError(Exception):
  """Raised when a state transition is invalid."""

  def __init__(
    self,
    current: WorkflowState,
    command: TransitionCommand,
    message: str = "",
  ) -> None:
    self.current = current
    self.command = command
    detail = f": {message}" if message else ""
    super().__init__(
      f"invalid transition: cannot apply {command.value} "
      f"in state {current.value}{detail}"
    )


class ClaimError(Exception):
  """Raised when a claim guard check fails."""

  def __init__(self, current_claimant: str, requested_by: str) -> None:
    self.current_claimant = current_claimant
    self.requested_by = requested_by
    super().__init__(
      f"handoff already claimed by '{current_claimant}' "
      f"(requested by '{requested_by}')"
    )


# ---------------------------------------------------------------------------
# Transition table (DR-102 §4)
# ---------------------------------------------------------------------------

_S = WorkflowState
_C = TransitionCommand

_TRANSITIONS: dict[tuple[WorkflowState, TransitionCommand], WorkflowState] = {
  (_S.PLANNED, _C.PHASE_START): _S.IMPLEMENTING,
  (_S.IMPLEMENTING, _C.CREATE_HANDOFF): _S.AWAITING_HANDOFF,
  (_S.CHANGES_REQUESTED, _C.CREATE_HANDOFF): _S.AWAITING_HANDOFF,
  (_S.REVIEWING, _C.REVIEW_COMPLETE_CHANGES_REQUESTED): _S.CHANGES_REQUESTED,
  (_S.REVIEWING, _C.REVIEW_COMPLETE_APPROVED): _S.APPROVED,
}

# States from which ACCEPT_HANDOFF is valid
_ACCEPT_HANDOFF_SOURCES = frozenset({_S.AWAITING_HANDOFF})

# States that cannot be blocked (already terminal or transitional)
_BLOCK_EXCLUDED = frozenset({_S.BLOCKED})


@dataclass
class TransitionResult:
  """Result of a successful state transition."""

  previous_state: WorkflowState
  new_state: WorkflowState
  command: TransitionCommand


def apply_transition(
  current: WorkflowState,
  command: TransitionCommand,
  *,
  to_role: str | None = None,
  previous_state: WorkflowState | None = None,
) -> TransitionResult:
  """Apply a transition command to the current state.

  Args:
    current: Current workflow state.
    command: Transition command to apply.
    to_role: Target role (required for ACCEPT_HANDOFF).
    previous_state: State before blocking (required for UNBLOCK).

  Returns:
    TransitionResult with previous and new states.

  Raises:
    TransitionError: If the transition is invalid.
  """
  # BLOCK: any state except already blocked
  if command == _C.BLOCK:
    if current in _BLOCK_EXCLUDED:
      raise TransitionError(current, command, "already blocked")
    return TransitionResult(
      previous_state=current,
      new_state=_S.BLOCKED,
      command=command,
    )

  # UNBLOCK: must be blocked, restores previous state
  if command == _C.UNBLOCK:
    if current != _S.BLOCKED:
      raise TransitionError(current, command, "not currently blocked")
    if previous_state is None:
      raise TransitionError(
        current, command, "previous_state required for unblock"
      )
    return TransitionResult(
      previous_state=current,
      new_state=previous_state,
      command=command,
    )

  # ACCEPT_HANDOFF: target depends on to_role
  if command == _C.ACCEPT_HANDOFF:
    if current not in _ACCEPT_HANDOFF_SOURCES:
      raise TransitionError(current, command, "not awaiting handoff")
    if to_role is None:
      raise TransitionError(current, command, "to_role required")
    target = _S.REVIEWING if to_role == "reviewer" else _S.IMPLEMENTING
    return TransitionResult(
      previous_state=current,
      new_state=target,
      command=command,
    )

  # Standard transitions from the table
  key = (current, command)
  target = _TRANSITIONS.get(key)
  if target is None:
    raise TransitionError(current, command)

  return TransitionResult(
    previous_state=current,
    new_state=target,
    command=command,
  )


def check_claim(
  current_claimant: str | None,
  requested_by: str,
) -> None:
  """Check the claim guard for handoff acceptance.

  Args:
    current_claimant: Current claimed_by value (None if unclaimed).
    requested_by: Identity requesting the claim.

  Raises:
    ClaimError: If claimed by a different identity.

  No-op if unclaimed or same identity (idempotent).
  """
  if current_claimant is None:
    return
  if current_claimant == requested_by:
    return
  raise ClaimError(current_claimant, requested_by)
