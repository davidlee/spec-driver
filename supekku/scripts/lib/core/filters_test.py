"""Tests for core filter utilities."""

from supekku.scripts.lib.core.filters import parse_multi_value_filter


class TestParseMultiValueFilter:
  """Test multi-value filter parsing utility."""

  def test_parse_none_returns_empty_list(self):
    """None value should return empty list."""
    assert parse_multi_value_filter(None) == []

  def test_parse_empty_string_returns_empty_list(self):
    """Empty string should return empty list."""
    assert parse_multi_value_filter("") == []

  def test_parse_whitespace_only_returns_empty_list(self):
    """Whitespace-only string should return empty list."""
    assert parse_multi_value_filter("   ") == []

  def test_parse_single_value(self):
    """Single value should return list with one item."""
    assert parse_multi_value_filter("draft") == ["draft"]

  def test_parse_single_value_with_whitespace(self):
    """Single value with surrounding whitespace should be trimmed."""
    assert parse_multi_value_filter("  draft  ") == ["draft"]

  def test_parse_two_values(self):
    """Two comma-separated values should return list with two items."""
    assert parse_multi_value_filter("draft,in-progress") == ["draft", "in-progress"]

  def test_parse_two_values_with_spaces(self):
    """Two values with spaces after comma should be trimmed."""
    assert parse_multi_value_filter("draft, in-progress") == ["draft", "in-progress"]

  def test_parse_three_values(self):
    """Three comma-separated values should work correctly."""
    result = parse_multi_value_filter("draft,in-progress,completed")
    assert result == ["draft", "in-progress", "completed"]

  def test_parse_three_values_with_varied_spacing(self):
    """Values with inconsistent spacing should all be trimmed."""
    result = parse_multi_value_filter("draft, in-progress ,  completed")
    assert result == ["draft", "in-progress", "completed"]

  def test_parse_ignores_trailing_comma(self):
    """Trailing comma should not create empty value."""
    assert parse_multi_value_filter("draft,") == ["draft"]

  def test_parse_ignores_leading_comma(self):
    """Leading comma should not create empty value."""
    assert parse_multi_value_filter(",draft") == ["draft"]

  def test_parse_ignores_multiple_commas(self):
    """Multiple consecutive commas should not create empty values."""
    assert parse_multi_value_filter("draft,,in-progress") == ["draft", "in-progress"]

  def test_parse_preserves_hyphenated_values(self):
    """Hyphenated values like 'in-progress' should be preserved."""
    result = parse_multi_value_filter("in-progress,on-hold")
    assert result == ["in-progress", "on-hold"]

  def test_parse_preserves_case(self):
    """Case should be preserved (not normalized)."""
    result = parse_multi_value_filter("Draft,IN-PROGRESS,Completed")
    assert result == ["Draft", "IN-PROGRESS", "Completed"]

  def test_parse_complex_real_world_example(self):
    """Real-world CLI usage: status filter with multiple values."""
    result = parse_multi_value_filter("draft, in-progress, blocked")
    assert result == ["draft", "in-progress", "blocked"]
    assert len(result) == 3

  def test_parse_does_not_split_on_other_separators(self):
    """Only comma should be treated as separator, not space or semicolon."""
    result = parse_multi_value_filter("draft in-progress")
    assert result == ["draft in-progress"]  # Space not a separator

  def test_parse_handles_numeric_values(self):
    """Numeric values should work (e.g., for priority filters)."""
    result = parse_multi_value_filter("1,2,3")
    assert result == ["1", "2", "3"]

  def test_parse_handles_special_characters(self):
    """Values with special characters (except comma) should be preserved."""
    result = parse_multi_value_filter("VT-001,VA-002")
    assert result == ["VT-001", "VA-002"]
