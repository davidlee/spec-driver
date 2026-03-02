"""Tests for memory display formatters."""

from __future__ import annotations

import json
from datetime import date

from supekku.scripts.lib.formatters.memory_formatters import (
  format_memory_details,
  format_memory_list_json,
  format_memory_list_table,
)
from supekku.scripts.lib.memory.models import MemoryRecord


def _make_record(**overrides) -> MemoryRecord:
  """Create a MemoryRecord with sensible defaults, overridable."""
  defaults = {
    "id": "MEM-001",
    "name": "Test Memory",
    "status": "active",
    "memory_type": "fact",
    "path": "/repo/memory/MEM-001-test_memory.md",
    "created": date(2026, 1, 15),
    "updated": date(2026, 2, 1),
  }
  defaults.update(overrides)
  return MemoryRecord(**defaults)


# --- format_memory_details ---


class TestFormatMemoryDetails:
  """Tests for format_memory_details."""

  def test_minimal_record(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "MEM-001" in output
    assert "Test Memory" in output
    assert "active" in output
    assert "fact" in output

  def test_includes_dates(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "2026-01-15" in output
    assert "2026-02-01" in output

  def test_includes_tags(self) -> None:
    record = _make_record(tags=["arch", "python"])
    output = format_memory_details(record)
    assert "arch" in output
    assert "python" in output

  def test_includes_confidence(self) -> None:
    record = _make_record(confidence="high")
    output = format_memory_details(record)
    assert "high" in output

  def test_includes_summary(self) -> None:
    record = _make_record(summary="A brief summary")
    output = format_memory_details(record)
    assert "A brief summary" in output

  def test_includes_path(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "MEM-001-test_memory.md" in output

  def test_omits_empty_optional_fields(self) -> None:
    record = _make_record(confidence=None, tags=[], summary="")
    output = format_memory_details(record)
    assert "Confidence:" not in output
    assert "Tags:" not in output
    assert "Summary:" not in output

  def test_no_dates(self) -> None:
    record = _make_record(created=None, updated=None)
    output = format_memory_details(record)
    # Should still format without error
    assert "MEM-001" in output


# --- format_memory_list_table ---


class TestFormatMemoryListTable:
  """Tests for format_memory_list_table."""

  def test_table_output(self) -> None:
    records = [_make_record(), _make_record(id="MEM-002", name="Other")]
    output = format_memory_list_table(records)
    assert "MEM-001" in output
    assert "MEM-002" in output

  def test_json_format(self) -> None:
    records = [_make_record()]
    output = format_memory_list_table(records, format_type="json")
    parsed = json.loads(output)
    assert "items" in parsed
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["id"] == "MEM-001"

  def test_tsv_format(self) -> None:
    records = [_make_record()]
    output = format_memory_list_table(records, format_type="tsv")
    assert "MEM-001" in output
    assert "\t" in output

  def test_empty_list(self) -> None:
    output = format_memory_list_table([])
    # Should not error; table with no rows
    assert isinstance(output, str)

  def test_table_includes_type_column(self) -> None:
    records = [_make_record(memory_type="pattern")]
    output = format_memory_list_table(records)
    assert "pattern" in output


# --- format_memory_list_json ---


class TestFormatMemoryListJson:
  """Tests for format_memory_list_json."""

  def test_structure(self) -> None:
    records = [_make_record()]
    output = format_memory_list_json(records)
    parsed = json.loads(output)
    assert "items" in parsed
    item = parsed["items"][0]
    assert item["id"] == "MEM-001"
    assert item["name"] == "Test Memory"
    assert item["status"] == "active"
    assert item["memory_type"] == "fact"

  def test_includes_optional_fields(self) -> None:
    records = [_make_record(
      tags=["core"], confidence="high", summary="Brief",
    )]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert item["tags"] == ["core"]
    assert item["confidence"] == "high"
    assert item["summary"] == "Brief"

  def test_empty_list(self) -> None:
    output = format_memory_list_json([])
    parsed = json.loads(output)
    assert parsed["items"] == []
