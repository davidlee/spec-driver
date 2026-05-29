"""Per-item action × field-presence rule tests for revision change blocks.

Covers the conditional rules declared on the ``requirements[]`` item
(DE-142 P01): move→{origin,destination}, introduce/modify→{destination},
retire→none. Kept separate from ``revision_metadata_test.py`` to hold that
module under its line ceiling.
"""

from __future__ import annotations

import unittest

from .revision_metadata import validate_revision_change


class RequirementActionConditionalRuleTest(unittest.TestCase):
  """Per-item action × field-presence rules on requirements[] (DE-142 P01)."""

  def _validate(self, requirement: dict) -> list[str]:
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [requirement],
    }
    return validate_revision_change(data)

  def test_move_missing_origin_errors(self):
    """VT-142-BLOCK-001: move without origin errors on requirements[0].origin."""
    errors = self._validate(
      {
        "requirement_id": "SPEC-100.FR-001",
        "kind": "functional",
        "action": "move",
        "destination": {"spec": "SPEC-100"},
      }
    )
    assert any(
      "requirements[0].origin" in e and "is required when action=move" in e
      for e in errors
    ), errors

  def test_move_missing_destination_errors(self):
    """VT-142-BLOCK-001: move without destination errors on destination."""
    errors = self._validate(
      {
        "requirement_id": "SPEC-100.FR-001",
        "kind": "functional",
        "action": "move",
        "origin": [{"kind": "spec", "ref": "SPEC-200"}],
      }
    )
    assert any(
      "requirements[0].destination" in e and "is required when action=move" in e
      for e in errors
    ), errors

  def test_introduce_missing_destination_errors(self):
    """VT-142-BLOCK-002: introduce without destination errors."""
    errors = self._validate(
      {
        "requirement_id": "SPEC-100.FR-001",
        "kind": "functional",
        "action": "introduce",
      }
    )
    assert any(
      "requirements[0].destination" in e and "is required when action=introduce" in e
      for e in errors
    ), errors

  def test_modify_missing_destination_errors(self):
    """VT-142-BLOCK-002: modify without destination errors."""
    errors = self._validate(
      {
        "requirement_id": "SPEC-100.FR-001",
        "kind": "functional",
        "action": "modify",
      }
    )
    assert any(
      "requirements[0].destination" in e and "is required when action=modify" in e
      for e in errors
    ), errors

  def test_retire_requires_nothing(self):
    """VT-142-BLOCK-002: retire triggers no conditional requirement."""
    errors = self._validate(
      {
        "requirement_id": "SPEC-100.FR-001",
        "kind": "functional",
        "action": "retire",
      }
    )
    assert not any("is required when action=" in e for e in errors), errors

  def test_re042_modify_shape_no_conditional_error(self):
    """VT-142-BLOCK-003: RE-042 modify+destination, no origin → no rule error.

    RE-042 carries pre-existing pattern drift (PROD-/DE- IDs do not match the
    SPEC-/RE- patterns); that is out of scope here (P04 sweep). The conditional
    rules must not add an origin/destination-required error for this shape.
    """
    errors = self._validate(
      {
        "requirement_id": "PROD-004.FR-007",
        "kind": "functional",
        "action": "modify",
        "summary": "Metadata definitions MUST support classification",
        "destination": {"spec": "PROD-004", "requirement_id": "PROD-004.FR-007"},
        "lifecycle": {"introduced_by": "DE-138", "status": "active"},
      }
    )
    assert not any("is required when action=" in e for e in errors), errors


if __name__ == "__main__":
  unittest.main()
