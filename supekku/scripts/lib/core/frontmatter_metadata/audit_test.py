"""Dual-validation tests for audit frontmatter metadata.

Tests that the metadata-driven validator handles audit-specific fields
correctly, including the per-finding disposition contract (DEC-079-001).
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .audit import AUDIT_FRONTMATTER_METADATA

_BASE = {
  "id": "AUD-001",
  "name": "Test Audit",
  "slug": "test-audit",
  "kind": "audit",
  "status": "draft",
  "created": "2025-01-15",
  "updated": "2025-01-15",
}


def _new_errors(data: dict) -> list[str]:
  """Run metadata validator and return error strings."""
  validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
  return [str(e) for e in validator.validate(data)]


class AuditFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for audit-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)
    return old_error, _new_errors(data)

  def _assert_both_valid(self, data: dict) -> None:
    old_error, errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(errors, [], f"New validator rejected: {errors}")

  # -- Valid cases --

  def test_valid_minimal_audit(self) -> None:
    self._assert_both_valid({**_BASE})

  def test_valid_audit_with_mode_and_delta_ref(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "mode": "conformance",
        "delta_ref": "DE-079",
      }
    )

  def test_valid_audit_with_discovery_mode(self) -> None:
    self._assert_both_valid({**_BASE, "mode": "discovery"})

  def test_valid_audit_window(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "audit_window": {"start": "2024-06-01", "end": "2024-06-08"},
      }
    )

  def test_valid_findings_without_disposition(self) -> None:
    """Findings without disposition are valid (backward compat)."""
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test finding",
            "outcome": "drift",
          }
        ],
      }
    )

  def test_valid_finding_with_full_disposition(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "mode": "conformance",
        "delta_ref": "DE-021",
        "findings": [
          {
            "id": "FIND-001",
            "description": "Content reconciler deviates",
            "outcome": "drift",
            "disposition": {
              "status": "reconciled",
              "kind": "spec_patch",
              "refs": [{"kind": "spec", "ref": "SPEC-101"}],
              "drift_refs": [
                {"kind": "drift_entry", "ref": "DL-047.003"},
              ],
              "rationale": "Patched SPEC-101",
            },
          }
        ],
      }
    )

  def test_valid_finding_aligned(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Already aligned",
            "outcome": "aligned",
            "disposition": {
              "status": "reconciled",
              "kind": "aligned",
            },
          }
        ],
      }
    )

  def test_valid_disposition_follow_up_delta_accepted(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Needs follow-up",
            "outcome": "drift",
            "disposition": {
              "status": "accepted",
              "kind": "follow_up_delta",
              "refs": [{"kind": "delta", "ref": "DE-082"}],
              "rationale": "Created DE-082 to handle this",
            },
          }
        ],
      }
    )

  def test_valid_disposition_tolerated_drift(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Known drift, accepted",
            "outcome": "risk",
            "disposition": {
              "status": "accepted",
              "kind": "tolerated_drift",
              "rationale": "Accepted per governance decision",
            },
          }
        ],
      }
    )

  def test_valid_disposition_with_closure_override(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Drift with override",
            "outcome": "drift",
            "disposition": {
              "status": "accepted",
              "kind": "tolerated_drift",
              "rationale": "Known limitation",
              "closure_override": {
                "effect": "warn",
                "rationale": "Low impact, tracked in backlog",
              },
            },
          }
        ],
      }
    )

  def test_valid_finding_with_linked_fields(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "linked_issue": "ISSUE-018",
            "linked_delta": "DE-021",
          }
        ],
      }
    )

  # -- Invalid cases --

  def test_invalid_mode(self) -> None:
    errors = _new_errors({**_BASE, "mode": "invalid"})
    self.assertNotEqual(errors, [])

  def test_invalid_delta_ref_format(self) -> None:
    errors = _new_errors({**_BASE, "delta_ref": "not-a-delta"})
    self.assertNotEqual(errors, [])

  def test_audit_window_missing_start(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "audit_window": {"end": "2024-06-08"},
      }
    )
    self.assertNotEqual(errors, [])

  def test_audit_window_missing_end(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "audit_window": {"start": "2024-06-01"},
      }
    )
    self.assertNotEqual(errors, [])

  def test_finding_missing_required_fields(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [{"id": "FIND-001"}],
      }
    )
    self.assertNotEqual(errors, [])

  def test_finding_invalid_outcome(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "invalid",
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_disposition_missing_status(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {"kind": "spec_patch"},
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_disposition_missing_kind(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {"status": "reconciled"},
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_disposition_invalid_status(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "invalid",
              "kind": "spec_patch",
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_disposition_invalid_kind(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "reconciled",
              "kind": "invalid",
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_closure_override_missing_rationale(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "accepted",
              "kind": "tolerated_drift",
              "closure_override": {"effect": "warn"},
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_closure_override_invalid_effect(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "accepted",
              "kind": "tolerated_drift",
              "closure_override": {
                "effect": "block",
                "rationale": "This should not be valid",
              },
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_ref_missing_kind(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "reconciled",
              "kind": "spec_patch",
              "refs": [{"ref": "SPEC-101"}],
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])

  def test_ref_missing_ref(self) -> None:
    errors = _new_errors(
      {
        **_BASE,
        "findings": [
          {
            "id": "FIND-001",
            "description": "Test",
            "outcome": "drift",
            "disposition": {
              "status": "reconciled",
              "kind": "spec_patch",
              "refs": [{"kind": "spec"}],
            },
          }
        ],
      }
    )
    self.assertNotEqual(errors, [])


if __name__ == "__main__":
  unittest.main()
