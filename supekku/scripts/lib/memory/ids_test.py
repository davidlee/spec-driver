"""Tests for memory ID validation and normalization."""

from __future__ import annotations

import pytest

from supekku.scripts.lib.memory.ids import (
  extract_type_from_id,
  filename_from_id,
  normalize_memory_id,
  validate_memory_id,
)

# --- validate_memory_id ---


class TestValidateMemoryId:
  """Validation: canonical form, rejection, normalization on input."""

  def test_canonical_three_segments(self) -> None:
    assert validate_memory_id("mem.fact.auth") == "mem.fact.auth"

  def test_canonical_four_segments(self) -> None:
    assert validate_memory_id("mem.pattern.cli.skinny") == "mem.pattern.cli.skinny"

  def test_canonical_six_segments(self) -> None:
    result = validate_memory_id("mem.skill.auth.cache.howto.v2")
    assert result == "mem.skill.auth.cache.howto.v2"

  def test_two_segments_minimum(self) -> None:
    assert validate_memory_id("mem.fact") == "mem.fact"

  def test_lowercases_input(self) -> None:
    assert validate_memory_id("mem.FACT.Auth") == "mem.fact.auth"

  def test_hyphens_in_segments(self) -> None:
    result = validate_memory_id("mem.workset.oauth-migration")
    assert result == "mem.workset.oauth-migration"

  def test_digits_in_segments(self) -> None:
    assert validate_memory_id("mem.fact.http.timeout99") == "mem.fact.http.timeout99"

  def test_rejects_missing_mem_prefix(self) -> None:
    with pytest.raises(ValueError, match="must start with 'mem\\.'"):
      validate_memory_id("fact.auth")

  def test_rejects_single_segment(self) -> None:
    with pytest.raises(ValueError, match="must start with 'mem\\.'"):
      validate_memory_id("mem")

  def test_rejects_empty_string(self) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
      validate_memory_id("")

  def test_rejects_whitespace(self) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
      validate_memory_id("   ")

  def test_rejects_empty_segment(self) -> None:
    with pytest.raises(ValueError, match="empty segment"):
      validate_memory_id("mem.fact..auth")

  def test_rejects_uppercase_after_normalize(self) -> None:
    # Should succeed — uppercase is normalized, not rejected
    assert validate_memory_id("mem.Fact.Auth") == "mem.fact.auth"

  def test_rejects_spaces_in_segment(self) -> None:
    with pytest.raises(ValueError, match="invalid.*segment"):
      validate_memory_id("mem.fact.my auth")

  def test_rejects_underscores(self) -> None:
    with pytest.raises(ValueError, match="invalid.*segment"):
      validate_memory_id("mem.fact.my_auth")

  def test_rejects_too_many_segments(self) -> None:
    with pytest.raises(ValueError, match="too many segments"):
      validate_memory_id("mem.a.b.c.d.e.f.g")

  def test_rejects_trailing_dot(self) -> None:
    with pytest.raises(ValueError, match="empty segment"):
      validate_memory_id("mem.fact.")

  def test_rejects_leading_hyphen_in_segment(self) -> None:
    with pytest.raises(ValueError, match="invalid.*segment"):
      validate_memory_id("mem.fact.-auth")

  def test_rejects_trailing_hyphen_in_segment(self) -> None:
    with pytest.raises(ValueError, match="invalid.*segment"):
      validate_memory_id("mem.fact.auth-")


# --- normalize_memory_id ---


class TestNormalizeMemoryId:
  """Normalization: prepend mem. if missing, lowercase."""

  def test_already_canonical(self) -> None:
    assert normalize_memory_id("mem.fact.auth") == "mem.fact.auth"

  def test_prepends_mem_prefix(self) -> None:
    assert normalize_memory_id("fact.auth") == "mem.fact.auth"

  def test_single_segment_shorthand(self) -> None:
    assert normalize_memory_id("fact") == "mem.fact"

  def test_lowercases(self) -> None:
    assert normalize_memory_id("Pattern.CLI.Skinny") == "mem.pattern.cli.skinny"

  def test_canonical_with_uppercase(self) -> None:
    assert normalize_memory_id("mem.Pattern.CLI") == "mem.pattern.cli"

  def test_strips_whitespace(self) -> None:
    assert normalize_memory_id("  fact.auth  ") == "mem.fact.auth"

  def test_rejects_empty(self) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
      normalize_memory_id("")

  def test_validates_after_normalization(self) -> None:
    """Invalid characters still rejected after prefix prepend."""
    with pytest.raises(ValueError, match="invalid.*segment"):
      normalize_memory_id("fact.my_auth")


# --- extract_type_from_id ---


class TestExtractTypeFromId:
  """Type extraction: second segment of canonical ID."""

  def test_three_segment(self) -> None:
    assert extract_type_from_id("mem.fact.auth") == "fact"

  def test_four_segment(self) -> None:
    assert extract_type_from_id("mem.pattern.cli.skinny") == "pattern"

  def test_two_segment(self) -> None:
    assert extract_type_from_id("mem.glossary") == "glossary"

  def test_non_canonical_returns_none(self) -> None:
    assert extract_type_from_id("not-a-memory-id") is None

  def test_old_style_returns_none(self) -> None:
    assert extract_type_from_id("MEM-001") is None


# --- filename_from_id ---


class TestFilenameFromId:
  """Filename derivation from canonical ID."""

  def test_simple(self) -> None:
    assert filename_from_id("mem.fact.auth") == "mem.fact.auth.md"

  def test_four_segment(self) -> None:
    assert filename_from_id("mem.pattern.cli.skinny") == "mem.pattern.cli.skinny.md"

  def test_preserves_hyphens(self) -> None:
    result = filename_from_id("mem.workset.oauth-migration")
    assert result == "mem.workset.oauth-migration.md"
