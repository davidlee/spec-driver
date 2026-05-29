"""Tests for shared block ID-pattern constants (VT-142-PATTERN-001).

The broadened constants accept the full corpus ID universe — `PROD-*`/
`ISSUE-*` containers and the `NF` requirement token (DEC-142-08) — while
still rejecting malformed IDs.
"""

from __future__ import annotations

import re

from supekku.scripts.lib.blocks.id_patterns import (
  REQUIREMENT_ID_PATTERN,
  SPEC_ID_PATTERN,
)


class TestRequirementIdPattern:
  """VT-142-PATTERN-001 — requirement_id universe."""

  def _match(self, value: str) -> bool:
    return re.match(REQUIREMENT_ID_PATTERN, value) is not None

  def test_accepts_spec_functional(self) -> None:
    assert self._match("SPEC-122.FR-003")

  def test_accepts_prod_non_functional(self) -> None:
    assert self._match("PROD-007.NF-001")

  def test_accepts_issue_dotted_suffix(self) -> None:
    assert self._match("ISSUE-016.FR-016.001")

  def test_accepts_legacy_nfr_token(self) -> None:
    assert self._match("SPEC-100.NFR-SECURITY")

  def test_accepts_segmented_container(self) -> None:
    assert self._match("SPEC-122-AUTH.FR-001")

  def test_rejects_bare_spec(self) -> None:
    assert not self._match("PROD-014")

  def test_rejects_unknown_prefix(self) -> None:
    assert not self._match("XYZ-100.FR-001")

  def test_rejects_too_few_digits(self) -> None:
    assert not self._match("SPEC-1.FR-1")

  def test_rejects_adr_prefix(self) -> None:
    assert not self._match("ADR-007.FR-001")

  def test_rejects_empty(self) -> None:
    assert not self._match("")


class TestSpecIdPattern:
  """VT-142-PATTERN-001 — spec_id universe."""

  def _match(self, value: str) -> bool:
    return re.match(SPEC_ID_PATTERN, value) is not None

  def test_accepts_prod(self) -> None:
    assert self._match("PROD-014")

  def test_accepts_spec_segmented(self) -> None:
    assert self._match("SPEC-122-AUTH")

  def test_accepts_issue(self) -> None:
    assert self._match("ISSUE-016")

  def test_rejects_requirement_form(self) -> None:
    assert not self._match("SPEC-100.FR-001")

  def test_rejects_adr_prefix(self) -> None:
    assert not self._match("ADR-007")

  def test_rejects_too_few_digits(self) -> None:
    assert not self._match("SPEC-12")

  def test_rejects_empty(self) -> None:
    assert not self._match("")
