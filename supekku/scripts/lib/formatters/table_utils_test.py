"""Tests for table rendering utilities."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from rich.table import Table

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  calculate_column_widths,
  create_table,
  format_as_json,
  format_as_tsv,
  format_list_table,
  get_terminal_width,
  is_tty,
  render_table,
  truncate_text,
)


class TestTerminalDetection:
  """Test terminal width and TTY detection."""

  def test_get_terminal_width_returns_int(self):
    """Test that get_terminal_width returns a positive integer."""
    width = get_terminal_width()
    assert isinstance(width, int)
    assert width > 0

  def test_is_tty_returns_bool(self):
    """Test that is_tty returns a boolean."""
    result = is_tty()
    assert isinstance(result, bool)


class TestColumnWidthCalculation:
  """Test column width calculation."""

  def test_calculate_column_widths_equal_distribution(self):
    """Test that columns get equal width distribution."""
    widths = calculate_column_widths(terminal_width=100, num_columns=4)
    assert len(widths) == 4
    # Each column should get roughly equal width
    assert all(w > 0 for w in widths.values())

  def test_calculate_column_widths_zero_columns(self):
    """Test handling of zero columns."""
    widths = calculate_column_widths(terminal_width=100, num_columns=0)
    assert not widths

  def test_calculate_column_widths_narrow_terminal(self):
    """Test handling of very narrow terminal."""
    widths = calculate_column_widths(terminal_width=40, num_columns=5)
    assert len(widths) == 5
    # Should still provide minimum width
    assert all(w > 0 for w in widths.values())


class TestTextTruncation:
  """Test text truncation."""

  def test_truncate_text_no_truncation_needed(self):
    """Test that short text is not truncated."""
    text = "Short"
    result = truncate_text(text, max_width=20)
    assert result == "Short"

  def test_truncate_text_exact_width(self):
    """Test text at exact max width."""
    text = "Exactly20Characters!"
    result = truncate_text(text, max_width=20)
    assert result == "Exactly20Characters!"

  def test_truncate_text_long_text(self):
    """Test truncation of long text."""
    text = "This is a very long text that needs truncation"
    result = truncate_text(text, max_width=20)
    assert len(result) == 20
    assert result.endswith("...")
    assert result == "This is a very lo..."

  def test_truncate_text_custom_suffix(self):
    """Test truncation with custom suffix."""
    text = "Long text here"
    result = truncate_text(text, max_width=10, suffix="…")
    assert len(result) == 10
    assert result.endswith("…")

  def test_truncate_text_width_smaller_than_suffix(self):
    """Test handling when max_width is smaller than suffix."""
    text = "Test"
    result = truncate_text(text, max_width=2, suffix="...")
    assert len(result) == 2
    assert result == ".."


class TestTableCreation:
  """Test table creation."""

  def test_create_table_basic(self):
    """Test creating a basic table."""
    table = create_table(columns=["ID", "Name", "Status"])
    assert isinstance(table, Table)
    assert len(table.columns) == 3

  def test_create_table_with_title(self):
    """Test creating table with title."""
    table = create_table(columns=["ID", "Name"], title="Test Table")
    assert table.title == "Test Table"

  def test_create_table_no_header(self):
    """Test creating table without header."""
    table = create_table(columns=["ID", "Name"], show_header=False)
    assert not table.show_header

  def test_create_table_empty_columns(self):
    """Test creating table with no columns."""
    table = create_table(columns=[])
    assert len(table.columns) == 0


class TestRowAddition:
  """Test adding rows to tables."""

  def test_add_row_without_truncation(self):
    """Test adding row without truncation."""
    table = create_table(columns=["ID", "Name"])
    add_row_with_truncation(
      table,
      ["ADR-001", "Very Long Decision Name"],
      no_truncate=True,
    )
    assert len(table.rows) == 1

  def test_add_row_with_truncation(self):
    """Test adding row with truncation."""
    table = create_table(columns=["ID", "Name"])
    max_widths = {0: 10, 1: 15}
    add_row_with_truncation(
      table,
      ["ADR-001", "Very Long Decision Name That Gets Truncated"],
      max_widths=max_widths,
    )
    assert len(table.rows) == 1

  def test_add_row_no_max_widths(self):
    """Test adding row when max_widths is None."""
    table = create_table(columns=["ID", "Name"])
    add_row_with_truncation(table, ["ADR-001", "Name"], max_widths=None)
    assert len(table.rows) == 1

  def test_add_multiple_rows(self):
    """Test adding multiple rows."""
    table = create_table(columns=["ID", "Status"])
    max_widths = {0: 10, 1: 10}
    for i in range(3):
      add_row_with_truncation(
        table,
        [f"ADR-{i:03d}", "active"],
        max_widths=max_widths,
      )
    assert len(table.rows) == 3


class TestTableRendering:
  """Test table rendering."""

  def test_render_table_basic(self):
    """Test rendering a basic table."""
    table = create_table(columns=["ID", "Name"])
    add_row_with_truncation(table, ["001", "Test"], no_truncate=True)
    output = render_table(table)
    assert isinstance(output, str)
    assert "ID" in output
    assert "Name" in output
    assert "001" in output
    assert "Test" in output

  def test_render_empty_table(self):
    """Test rendering an empty table."""
    table = create_table(columns=["ID", "Name"])
    output = render_table(table)
    assert isinstance(output, str)
    assert "ID" in output
    assert "Name" in output


class TestJsonFormatting:
  """Test JSON formatting."""

  def test_format_as_json_basic(self):
    """Test basic JSON formatting."""
    items = [
      {"id": "ADR-001", "status": "accepted"},
      {"id": "ADR-002", "status": "draft"},
    ]
    output = format_as_json(items)
    assert isinstance(output, str)

    # Parse to verify valid JSON
    parsed = json.loads(output)
    assert "items" in parsed
    assert len(parsed["items"]) == 2
    assert parsed["items"][0]["id"] == "ADR-001"

  def test_format_as_json_empty_list(self):
    """Test JSON formatting with empty list."""
    output = format_as_json([])
    parsed = json.loads(output)
    assert parsed["items"] == []

  def test_format_as_json_with_complex_types(self):
    """Test JSON formatting with dates and paths."""
    items = [
      {
        "id": "TEST-001",
        "date": datetime(2025, 1, 1, 12, 0),
        "path": Path("/test/path"),
      },
    ]
    output = format_as_json(items)
    # Should use default=str to handle non-serializable types
    parsed = json.loads(output)
    assert len(parsed["items"]) == 1


class TestTsvFormatting:
  """Test TSV formatting."""

  def test_format_as_tsv_basic(self):
    """Test basic TSV formatting."""
    rows = [
      ["ID", "Name", "Status"],
      ["ADR-001", "Decision 1", "accepted"],
      ["ADR-002", "Decision 2", "draft"],
    ]
    output = format_as_tsv(rows)
    lines = output.split("\n")
    assert len(lines) == 3
    assert lines[0] == "ID\tName\tStatus"
    assert lines[1] == "ADR-001\tDecision 1\taccepted"

  def test_format_as_tsv_empty(self):
    """Test TSV formatting with empty list."""
    output = format_as_tsv([])
    assert output == ""

  def test_format_as_tsv_single_row(self):
    """Test TSV formatting with single row."""
    rows = [["A", "B", "C"]]
    output = format_as_tsv(rows)
    assert output == "A\tB\tC"

  def test_format_as_tsv_with_numeric_values(self):
    """Test TSV formatting with mixed types."""
    rows = [["ID", "Count"], ["TEST-001", 42], ["TEST-002", 0]]
    output = format_as_tsv(rows)
    lines = output.split("\n")
    assert "42" in lines[1]
    assert "0" in lines[2]


class TestFormatListTable:
  """Tests for the generic format_list_table helper."""

  @staticmethod
  def _make_item(item_id: str, name: str, status: str = "active") -> dict:
    return {"id": item_id, "name": name, "status": status}

  @staticmethod
  def _prepare_row(item: dict) -> list[str]:
    return [item["id"], item["name"], item["status"]]

  @staticmethod
  def _prepare_tsv_row(item: dict) -> list[str]:
    return [item["id"], item["name"], item["status"]]

  @staticmethod
  def _to_json(items: list) -> str:
    return json.dumps({"items": [dict(i) for i in items]}, indent=2)

  def _call(self, items, **kwargs):
    defaults = {
      "columns": ["ID", "Name", "Status"],
      "title": "Test Items",
      "prepare_row": self._prepare_row,
      "prepare_tsv_row": self._prepare_tsv_row,
      "to_json": self._to_json,
    }
    defaults.update(kwargs)
    return format_list_table(items, **defaults)

  def test_table_format_renders_columns_and_data(self):
    items = [self._make_item("T-001", "Alpha"), self._make_item("T-002", "Beta")]
    result = self._call(items, format_type="table")
    assert "ID" in result
    assert "Name" in result
    assert "T-001" in result
    assert "Beta" in result

  def test_table_format_is_default(self):
    items = [self._make_item("T-001", "Alpha")]
    result = self._call(items)
    assert "T-001" in result
    assert "Alpha" in result

  def test_json_format_delegates_to_callback(self):
    items = [self._make_item("T-001", "Alpha")]
    result = self._call(items, format_type="json")
    parsed = json.loads(result)
    assert parsed["items"][0]["id"] == "T-001"

  def test_tsv_format_uses_tsv_row_callback(self):
    items = [
      self._make_item("T-001", "Alpha"),
      self._make_item("T-002", "Beta", "draft"),
    ]
    result = self._call(items, format_type="tsv")
    lines = result.split("\n")
    assert len(lines) == 2
    assert lines[0] == "T-001\tAlpha\tactive"
    assert lines[1] == "T-002\tBeta\tdraft"

  def test_empty_items_table(self):
    result = self._call([], format_type="table")
    assert "ID" in result  # headers still rendered

  def test_empty_items_json(self):
    result = self._call([], format_type="json")
    parsed = json.loads(result)
    assert parsed["items"] == []

  def test_empty_items_tsv(self):
    result = self._call([], format_type="tsv")
    assert result == ""

  def test_truncate_false_preserves_all_content(self):
    long_name = "A" * 200
    items = [self._make_item("T-001", long_name)]
    result = self._call(items, format_type="table", truncate=False)
    # Rich wraps long text across lines; verify all chars present (no "...")
    assert "..." not in result
    # Count As in rendered output (stripping table chrome)
    a_count = result.count("A")
    assert a_count == 200

  def test_truncate_true_shortens_content(self):
    long_name = "A" * 200
    items = [self._make_item("T-001", long_name)]
    result = self._call(items, format_type="table", truncate=True)
    # Full string should NOT appear when truncated
    assert long_name not in result

  def test_custom_column_widths(self):
    """Custom column_widths callback is used when provided."""
    custom_called = []

    def custom_widths(terminal_width: int) -> dict[int, int]:
      custom_called.append(terminal_width)
      return {0: 8, 1: 20, 2: 10}

    items = [self._make_item("T-001", "Alpha")]
    self._call(items, format_type="table", truncate=True, column_widths=custom_widths)
    assert len(custom_called) == 1

  def test_custom_column_widths_not_called_without_truncate(self):
    """column_widths callback should not be called when truncate is False."""
    custom_called = []

    def custom_widths(terminal_width: int) -> dict[int, int]:
      custom_called.append(True)
      return {0: 8, 1: 20, 2: 10}

    items = [self._make_item("T-001", "Alpha")]
    self._call(items, format_type="table", truncate=False, column_widths=custom_widths)
    assert len(custom_called) == 0

  def test_title_appears_in_table(self):
    items = [self._make_item("T-001", "Alpha")]
    result = self._call(items, format_type="table", title="My Custom Title")
    assert "My Custom Title" in result


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
