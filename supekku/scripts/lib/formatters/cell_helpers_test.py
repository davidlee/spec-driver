"""Tests for cell_helpers — Rich-compatible cell formatting."""

from datetime import date, datetime

from supekku.scripts.lib.formatters.cell_helpers import (
  format_date_cell,
  format_tags_cell,
)

# --- format_tags_cell ---


class TestFormatTagsCell:
  """Tests for format_tags_cell."""

  def test_none_returns_empty(self):
    assert format_tags_cell(None) == ""

  def test_empty_list_returns_empty(self):
    assert format_tags_cell([]) == ""

  def test_single_tag(self):
    assert format_tags_cell(["foo"]) == "[#d79921]foo[/#d79921]"

  def test_multiple_tags(self):
    result = format_tags_cell(["alpha", "beta", "gamma"])
    assert result == "[#d79921]alpha, beta, gamma[/#d79921]"

  def test_custom_style(self):
    result = format_tags_cell(["x"], style="bold red")
    assert result == "[bold red]x[/bold red]"

  def test_empty_tuple_returns_empty(self):
    assert format_tags_cell(()) == ""


# --- format_date_cell ---


class TestFormatDateCell:
  """Tests for format_date_cell."""

  def test_none_returns_default_missing(self):
    assert format_date_cell(None) == "—"

  def test_none_with_custom_missing(self):
    assert format_date_cell(None, missing="N/A") == "N/A"

  def test_date_object(self):
    assert format_date_cell(date(2026, 3, 8)) == "2026-03-08"

  def test_datetime_object(self):
    dt = datetime(2026, 3, 8, 14, 30, 0)
    assert format_date_cell(dt) == "2026-03-08"

  def test_custom_format(self):
    result = format_date_cell(date(2026, 3, 8), fmt="%d/%m/%Y")
    assert result == "08/03/2026"

  def test_custom_format_and_missing(self):
    assert format_date_cell(None, missing="–", fmt="%d/%m/%Y") == "–"
