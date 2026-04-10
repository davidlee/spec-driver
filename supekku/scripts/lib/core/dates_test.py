"""Tests for core date parsing utilities."""

from datetime import date, datetime

import pytest

from supekku.scripts.lib.core.dates import parse_date


class TestParseDate:
  """Tests for parse_date."""

  def test_none_returns_none(self):
    assert parse_date(None) is None

  def test_empty_string_returns_none(self):
    assert parse_date("") is None

  def test_date_object_returned_as_is(self):
    d = date(2025, 3, 15)
    assert parse_date(d) == d

  def test_datetime_object_returns_date_part(self):
    dt = datetime(2025, 3, 15, 10, 30, 0)
    assert parse_date(dt) == date(2025, 3, 15)

  def test_iso_string_parsed(self):
    assert parse_date("2025-03-15") == date(2025, 3, 15)

  def test_iso_string_with_time_parsed(self):
    assert parse_date("2025-03-15 10:30:00") == date(2025, 3, 15)

  def test_slash_format_parsed(self):
    assert parse_date("2025/03/15") == date(2025, 3, 15)

  def test_invalid_string_returns_none(self):
    assert parse_date("not-a-date") is None

  def test_unrecognised_format_returns_none(self):
    assert parse_date("15-03-2025") is None

  @pytest.mark.parametrize("falsy", [0, False, [], {}])
  def test_falsy_non_string_returns_none(self, falsy):
    assert parse_date(falsy) is None
