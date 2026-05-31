"""Tests for spec_driver.core.string_utils (VT-CC-010)."""

from __future__ import annotations

import pytest

from spec_driver.core.string_utils import CLOSEST_MATCH_CUTOFF, closest_match, slugify

DELTA_STATUS_CANDIDATES = (
  "completed",
  "deferred",
  "draft",
  "in-progress",
  "pending",
)


@pytest.mark.parametrize(
  ("value", "expected"),
  [
    ("complete", "completed"),
    ("pendng", "pending"),
    ("in_progres", "in-progress"),
    ("defered", "deferred"),
    ("draaft", "draft"),
  ],
)
def test_closest_match_catches_canonical_typos(value: str, expected: str) -> None:
  """VT-CC-010: typo inputs return their canonical at cutoff 0.6."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) == expected


@pytest.mark.parametrize(
  "value",
  ["live", "active", "done", "wip"],
)
def test_closest_match_silent_on_semantic_alternatives(value: str) -> None:
  """Semantic alternatives miss the cutoff; they belong in FieldMetadata.aliases."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) is None


@pytest.mark.parametrize("value", ["", "a"])
def test_closest_match_short_circuits_trivial_inputs(value: str) -> None:
  """Inputs shorter than two characters never produce a match."""
  assert closest_match(value, DELTA_STATUS_CANDIDATES) is None


def test_closest_match_accepts_arbitrary_iterable() -> None:
  """Candidates may be any iterable, not just a sequence."""

  def _candidates():
    yield from DELTA_STATUS_CANDIDATES

  assert closest_match("pendng", _candidates()) == "pending"


def test_cutoff_constant_is_advertised() -> None:
  """The module exposes the cutoff value (POL-002 magic-number avoidance)."""
  assert CLOSEST_MATCH_CUTOFF == 0.6


class TestSlugify:
  """Tests for slugify function."""

  def test_basic_title(self) -> None:
    """Simple title converts to slug."""
    assert slugify("Hello World") == "hello_world"

  def test_preserves_numbers(self) -> None:
    """Numbers are preserved in slug."""
    assert slugify("ADR-001") == "adr_001"
    assert slugify("SPEC-123") == "spec_123"

  def test_colon_separator(self) -> None:
    """Colons are normalized to underscores."""
    assert slugify("ADR-001: use spec-driver") == "adr_001_use_spec_driver"
    assert slugify("title: with: colons") == "title_with_colons"

  def test_multiple_special_chars(self) -> None:
    """Multiple special chars collapse to single underscore."""
    assert slugify("Fix bug -- urgent") == "fix_bug_urgent"
    assert slugify("foo___bar") == "foo_bar"
    assert slugify("a::b") == "a_b"
    assert slugify("x--y--z") == "x_y_z"

  def test_mixed_separators(self) -> None:
    """Mixed separators collapse to single underscore."""
    assert slugify("a-_-b") == "a_b"
    assert slugify("foo:- bar") == "foo_bar"
    assert slugify("test+-value") == "test_value"

  def test_strips_leading_trailing(self) -> None:
    """Leading and trailing separators are stripped."""
    assert slugify("-leading") == "leading"
    assert slugify("trailing-") == "trailing"
    assert slugify("--both--") == "both"
    assert slugify("  spaces  ") == "spaces"

  def test_empty_returns_fallback(self) -> None:
    """Empty or separator-only strings return 'item'."""
    assert slugify("") == "item"
    assert slugify("---") == "item"
    assert slugify("   ") == "item"
    assert slugify(":::") == "item"

  def test_unicode_stripped(self) -> None:
    """Non-ASCII characters are stripped."""
    assert slugify("café") == "caf"
    assert slugify("naïve") == "na_ve"

  def test_already_slug(self) -> None:
    """Already-slugified strings pass through."""
    assert slugify("already_a_slug") == "already_a_slug"
    assert slugify("simple") == "simple"

  @pytest.mark.parametrize(
    ("input_val", "expected"),
    [
      ("ADR-001: use spec-driver", "adr_001_use_spec_driver"),
      ("Fix bug -- urgent", "fix_bug_urgent"),
      ("foo___bar", "foo_bar"),
      ("title: with: colons", "title_with_colons"),
      ("ISSUE-027-consolidate-filename", "issue_027_consolidate_filename"),
      ("Make sync dry-run/check", "make_sync_dry_run_check"),
    ],
  )
  def test_real_world_examples(self, input_val: str, expected: str) -> None:
    """Real-world title examples from the codebase."""
    assert slugify(input_val) == expected
