"""Tests for workflow state machine (DR-102 §4).

Validates all transitions, rejection of invalid transitions,
claim guard semantics, and edge cases.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.workflow.state_machine import (
  ClaimError,
  TransitionCommand,
  TransitionError,
  TransitionResult,
  WorkflowState,
  apply_transition,
  check_claim,
)

_S = WorkflowState
_C = TransitionCommand


class TransitionTableTest(unittest.TestCase):
  """Valid transitions from DR-102 §4."""

  def test_planned_to_implementing(self) -> None:
    result = apply_transition(_S.PLANNED, _C.PHASE_START)
    assert result == TransitionResult(_S.PLANNED, _S.IMPLEMENTING, _C.PHASE_START)

  def test_implementing_to_awaiting_handoff(self) -> None:
    result = apply_transition(_S.IMPLEMENTING, _C.CREATE_HANDOFF)
    assert result.new_state == _S.AWAITING_HANDOFF

  def test_changes_requested_to_awaiting_handoff(self) -> None:
    result = apply_transition(_S.CHANGES_REQUESTED, _C.CREATE_HANDOFF)
    assert result.new_state == _S.AWAITING_HANDOFF

  def test_accept_handoff_to_implementing(self) -> None:
    result = apply_transition(
      _S.AWAITING_HANDOFF,
      _C.ACCEPT_HANDOFF,
      to_role="implementer",
    )
    assert result.new_state == _S.IMPLEMENTING

  def test_accept_handoff_to_implementing_for_architect(self) -> None:
    result = apply_transition(
      _S.AWAITING_HANDOFF,
      _C.ACCEPT_HANDOFF,
      to_role="architect",
    )
    assert result.new_state == _S.IMPLEMENTING

  def test_accept_handoff_to_implementing_for_operator(self) -> None:
    result = apply_transition(
      _S.AWAITING_HANDOFF,
      _C.ACCEPT_HANDOFF,
      to_role="operator",
    )
    assert result.new_state == _S.IMPLEMENTING

  def test_accept_handoff_to_reviewing(self) -> None:
    result = apply_transition(
      _S.AWAITING_HANDOFF,
      _C.ACCEPT_HANDOFF,
      to_role="reviewer",
    )
    assert result.new_state == _S.REVIEWING

  def test_review_complete_changes_requested(self) -> None:
    result = apply_transition(
      _S.REVIEWING,
      _C.REVIEW_COMPLETE_CHANGES_REQUESTED,
    )
    assert result.new_state == _S.CHANGES_REQUESTED

  def test_review_complete_approved(self) -> None:
    result = apply_transition(_S.REVIEWING, _C.REVIEW_COMPLETE_APPROVED)
    assert result.new_state == _S.APPROVED


class BlockUnblockTest(unittest.TestCase):
  """Block/unblock transitions (DR-102 §4)."""

  def test_block_from_any_non_blocked_state(self) -> None:
    for state in _S:
      if state == _S.BLOCKED:
        continue
      result = apply_transition(state, _C.BLOCK)
      assert result.new_state == _S.BLOCKED
      assert result.previous_state == state

  def test_block_already_blocked_fails(self) -> None:
    with self.assertRaises(TransitionError) as ctx:
      apply_transition(_S.BLOCKED, _C.BLOCK)
    assert "already blocked" in str(ctx.exception)

  def test_unblock_restores_previous_state(self) -> None:
    for prev in _S:
      if prev == _S.BLOCKED:
        continue
      result = apply_transition(
        _S.BLOCKED,
        _C.UNBLOCK,
        previous_state=prev,
      )
      assert result.new_state == prev

  def test_unblock_not_blocked_fails(self) -> None:
    with self.assertRaises(TransitionError) as ctx:
      apply_transition(_S.IMPLEMENTING, _C.UNBLOCK, previous_state=_S.PLANNED)
    assert "not currently blocked" in str(ctx.exception)

  def test_unblock_without_previous_state_fails(self) -> None:
    with self.assertRaises(TransitionError):
      apply_transition(_S.BLOCKED, _C.UNBLOCK)


class InvalidTransitionTest(unittest.TestCase):
  """Invalid transitions are rejected."""

  def test_planned_rejects_create_handoff(self) -> None:
    with self.assertRaises(TransitionError):
      apply_transition(_S.PLANNED, _C.CREATE_HANDOFF)

  def test_implementing_rejects_accept_handoff(self) -> None:
    with self.assertRaises(TransitionError):
      apply_transition(_S.IMPLEMENTING, _C.ACCEPT_HANDOFF, to_role="reviewer")

  def test_reviewing_rejects_phase_start(self) -> None:
    with self.assertRaises(TransitionError):
      apply_transition(_S.REVIEWING, _C.PHASE_START)

  def test_approved_rejects_create_handoff(self) -> None:
    with self.assertRaises(TransitionError):
      apply_transition(_S.APPROVED, _C.CREATE_HANDOFF)

  def test_accept_handoff_requires_to_role(self) -> None:
    with self.assertRaises(TransitionError) as ctx:
      apply_transition(_S.AWAITING_HANDOFF, _C.ACCEPT_HANDOFF)
    assert "to_role required" in str(ctx.exception)


class TransitionErrorTest(unittest.TestCase):
  """TransitionError carries context."""

  def test_error_has_current_and_command(self) -> None:
    err = TransitionError(_S.PLANNED, _C.CREATE_HANDOFF, "test detail")
    assert err.current == _S.PLANNED
    assert err.command == _C.CREATE_HANDOFF
    assert "test detail" in str(err)
    assert "planned" in str(err)


class ClaimGuardTest(unittest.TestCase):
  """Claim guard semantics (DR-102 §4)."""

  def test_unclaimed_allows_claim(self) -> None:
    check_claim(None, "agent-1")  # Should not raise

  def test_same_identity_is_idempotent(self) -> None:
    check_claim("agent-1", "agent-1")  # Should not raise

  def test_different_identity_raises(self) -> None:
    with self.assertRaises(ClaimError) as ctx:
      check_claim("agent-1", "agent-2")
    assert ctx.exception.current_claimant == "agent-1"
    assert ctx.exception.requested_by == "agent-2"

  def test_claim_error_message(self) -> None:
    err = ClaimError("agent-1", "agent-2")
    assert "agent-1" in str(err)
    assert "agent-2" in str(err)


class WorkflowStateEnumTest(unittest.TestCase):
  """WorkflowState enum values match DR-102 §4."""

  def test_all_seven_states(self) -> None:
    assert len(WorkflowState) == 7
    expected = {
      "planned",
      "implementing",
      "awaiting_handoff",
      "reviewing",
      "changes_requested",
      "approved",
      "blocked",
    }
    assert {s.value for s in WorkflowState} == expected


if __name__ == "__main__":
  unittest.main()
