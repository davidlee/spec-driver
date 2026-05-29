"""Validation tests for the completed revision frontmatter metadata (DE-142 P02).

DEC-CONSULT-01 (user-approved 2026-05-29): revision FM is the **narrow** DR §5
shape — Base 7 + ``relations`` + ``tags`` + ``ext_id``/``ext_url`` only.
Deliberately tighter than audit/delta (which keep the full BASE spread): the
universal-cut keys (``lifecycle``/``auditers``/``source``/``owners``/``summary``)
and the hand-rolled scope keys (``source_specs``/``destination_specs``/
``requirements``/``aliases``) reject under strict. Verified zero corpus lossage —
no revision in the 42-record corpus carries the omitted keys.

Tests target ``MetadataValidator`` (the single canonical block-validation
surface) directly, not the legacy ``validate_frontmatter`` — the new validator
is authoritative for the DE-142 VTs.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator

from .revision import REVISION_FRONTMATTER_METADATA

_BASE = {
  "id": "RE-001",
  "name": "Test Revision",
  "slug": "test-revision",
  "kind": "revision",
  "status": "draft",
  "created": "2026-01-15",
  "updated": "2026-01-15",
}

# DEC-CONSULT-01 narrow shape: every key NOT in {Base 7, relations, tags,
# ext_id, ext_url} rejects under strict. Single source of truth for VT-142-FM-002.
_CUT_KEYS: dict[str, object] = {
  "source_specs": ["PROD-004"],
  "destination_specs": ["PROD-004"],
  "requirements": ["PROD-004.FR-007"],
  "aliases": [],
  "lifecycle": "implementation",
  "auditers": ["qa"],
  "source": "docs/x.md",
  "owners": ["alice"],
  "summary": "one-line overview",
}


def _new_errors(data: dict) -> list[str]:
  """Strict-mode validation error strings from the canonical validator."""
  validator = MetadataValidator(REVISION_FRONTMATTER_METADATA)
  return [str(e) for e in validator.validate(data, strict=True)]


class RevisionFrontmatterValidationTest(unittest.TestCase):
  """VT-142-FM-001 / VT-142-FM-002: narrow revision FM class."""

  # -- VT-142-FM-001: valid (narrow) field set accepted under strict --

  def test_minimal_valid(self) -> None:
    self.assertEqual(_new_errors({**_BASE}), [])

  def test_relations_valid(self) -> None:
    self.assertEqual(
      _new_errors({**_BASE, "relations": [{"type": "implements", "target": "DE-138"}]}),
      [],
    )

  def test_tags_valid(self) -> None:
    self.assertEqual(_new_errors({**_BASE, "tags": ["metadata"]}), [])

  def test_ext_id_and_url_valid(self) -> None:
    self.assertEqual(
      _new_errors({**_BASE, "ext_id": "GH-1", "ext_url": "https://example/1"}),
      [],
    )

  # -- VT-142-FM-002: cut keys rejected under strict --

  def test_cut_keys_rejected_strict(self) -> None:
    for key, value in _CUT_KEYS.items():
      with self.subTest(key=key):
        errors = _new_errors({**_BASE, key: value})
        self.assertTrue(
          any(key in e.lower() for e in errors),
          f"Expected strict rejection of cut key {key!r}: {errors}",
        )


class RevisionFrontmatterBesideBlockTest(unittest.TestCase):
  """VT-142-DERIVE-002: ``applies_to`` / scope keys beside the change block.

  ``applies_to`` is *derived* at load (DEC-142-05 / DEC-138-10), never stored.
  The narrow class declares no ``applies_to`` field, so it is an unknown key:
  rejected under strict (the post-flip gate), tolerated under ``strict=False``
  (transition window). No kind-specific check code is added — the generic
  declared-fields check covers revision once the field set omits the key
  (R-142-04 resolved MINOR).
  """

  def test_applies_to_beside_block_strict_error(self) -> None:
    data = {**_BASE, "applies_to": {"specs": ["PROD-004"], "requirements": []}}
    self.assertTrue(
      any("applies_to" in e.lower() for e in _new_errors(data)),
      "applies_to in FM must be an unknown-key strict error",
    )

  def test_applies_to_beside_block_tolerated_when_not_strict(self) -> None:
    data = {**_BASE, "applies_to": {"specs": ["PROD-004"]}}
    tolerant = MetadataValidator(REVISION_FRONTMATTER_METADATA).validate(
      data, strict=False
    )
    self.assertEqual(list(tolerant), [])


if __name__ == "__main__":
  unittest.main()
