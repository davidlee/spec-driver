"""Dual-validation tests for audit frontmatter metadata.

Tests that the metadata-driven validator handles audit-specific fields
correctly. Finding/disposition validation moved to block-level tests
(audit_findings_test.py) after DE-141 P04.
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
  """Run metadata validator (strict mode) and return error strings."""
  validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
  return [str(e) for e in validator.validate(data, strict=True)]


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

  def test_valid_audit_with_spec_refs(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "mode": "conformance",
        "delta_ref": "DE-021",
        "spec_refs": ["PROD-004", "SPEC-114"],
      }
    )

  def test_valid_audit_with_code_scope(self) -> None:
    self._assert_both_valid(
      {
        **_BASE,
        "code_scope": ["supekku/scripts/lib/blocks/"],
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

  def test_findings_in_fm_rejected_strict(self) -> None:
    """After DE-141, findings in FM is an unknown key under strict."""
    errors = _new_errors(
      {
        **_BASE,
        "findings": [{"id": "FIND-001", "description": "T", "outcome": "drift"}],
      }
    )
    self.assertTrue(
      any("findings" in e.lower() for e in errors),
      f"Expected rejection of FM findings key: {errors}",
    )


if __name__ == "__main__":
  unittest.main()
