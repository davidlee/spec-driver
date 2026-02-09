"""Tests for string utility functions."""

from __future__ import annotations

import pytest

from supekku.scripts.lib.core.strings import slugify


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
