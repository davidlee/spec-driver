"""Tests for sequential ID generation."""


from supekku.scripts.lib.core.ids import next_sequential_id


class TestNextSequentialId:
  """Tests for next_sequential_id."""

  def test_empty_collection_returns_001(self):
    assert next_sequential_id([], "ADR") == "ADR-001"

  def test_single_match_returns_next(self):
    assert next_sequential_id(["ADR-003"], "ADR") == "ADR-004"

  def test_multiple_entries_returns_highest_plus_one(self):
    names = ["ADR-001", "ADR-005", "ADR-003"]
    assert next_sequential_id(names, "ADR") == "ADR-006"

  def test_non_matching_entries_ignored(self):
    names = ["README.md", "ADR-002", "notes.txt"]
    assert next_sequential_id(names, "ADR") == "ADR-003"

  def test_no_matching_entries_returns_001(self):
    names = ["README.md", "notes.txt"]
    assert next_sequential_id(names, "ADR") == "ADR-001"

  def test_zero_padded_to_three_digits(self):
    assert next_sequential_id(["POL-001"], "POL") == "POL-002"

  def test_high_numbers_not_truncated(self):
    assert next_sequential_id(["STD-999"], "STD") == "STD-1000"

  def test_no_separator(self):
    names = ["T001", "T042", "T010"]
    assert next_sequential_id(names, "T", separator="") == "T043"

  def test_no_separator_empty(self):
    assert next_sequential_id([], "T", separator="") == "T001"

  def test_names_with_slug_suffix_still_match(self):
    names = ["DE-001-some-slug", "DE-003-another-slug"]
    assert next_sequential_id(names, "DE") == "DE-004"

  def test_prefix_with_special_chars_escaped(self):
    """Prefixes containing regex metacharacters are handled safely."""
    names = ["X.Y-001"]
    assert next_sequential_id(names, "X.Y") == "X.Y-002"

  def test_iterator_consumed(self):
    """Accepts any iterable, not just lists."""
    assert next_sequential_id(iter(["DL-005"]), "DL") == "DL-006"

  def test_entries_with_different_prefix_ignored(self):
    names = ["POL-010", "STD-020"]
    assert next_sequential_id(names, "POL") == "POL-011"
