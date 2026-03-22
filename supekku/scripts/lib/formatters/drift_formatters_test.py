"""Tests for drift_formatters module."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from supekku.scripts.lib.drift.models import (
  Claim,
  DriftEntry,
  DriftLedger,
  Source,
)
from supekku.scripts.lib.formatters.drift_formatters import (
  format_drift_details,
  format_drift_details_json,
  format_drift_list_table,
)


def _make_entry(
  entry_id: str = "DL-047.001",
  title: str = "Test drift entry",
  **kwargs,
) -> DriftEntry:
  return DriftEntry(id=entry_id, title=title, **kwargs)


def _make_ledger(
  ledger_id: str = "DL-047",
  name: str = "Test ledger",
  entries: list[DriftEntry] | None = None,
  **kwargs,
) -> DriftLedger:
  defaults = {
    "status": "open",
    "path": Path(".spec-driver/drift/DL-047-test.md"),
    "created": "2026-03-08",
    "updated": "2026-03-08",
  }
  defaults.update(kwargs)
  return DriftLedger(
    id=ledger_id,
    name=name,
    entries=entries or [],
    **defaults,  # type: ignore[invalid-argument-type]
  )


class TestFormatDriftListTable(unittest.TestCase):
  """Tests for format_drift_list_table."""

  def test_empty_list_table(self) -> None:
    result = format_drift_list_table([], format_type="table")
    assert "Drift Ledgers" in result
    assert isinstance(result, str)

  def test_empty_list_json(self) -> None:
    result = format_drift_list_table([], format_type="json")
    data = json.loads(result)
    assert data["items"] == []

  def test_empty_list_tsv(self) -> None:
    result = format_drift_list_table([], format_type="tsv")
    assert result == ""

  def test_single_ledger_table(self) -> None:
    ledger = _make_ledger()
    result = format_drift_list_table([ledger], format_type="table")
    assert "DL-047" in result
    assert "Test ledger" in result

  def test_single_ledger_json(self) -> None:
    ledger = _make_ledger(delta_ref="DE-047")
    result = format_drift_list_table([ledger], format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "DL-047"
    assert data["items"][0]["delta_ref"] == "DE-047"

  def test_single_ledger_tsv(self) -> None:
    ledger = _make_ledger()
    result = format_drift_list_table([ledger], format_type="tsv")
    assert "DL-047" in result
    assert "Test ledger" in result

  def test_entry_count_in_table(self) -> None:
    entries = [_make_entry(f"DL-047.{i:03d}") for i in range(3)]
    ledger = _make_ledger(entries=entries)
    result = format_drift_list_table([ledger], format_type="json")
    data = json.loads(result)
    assert data["items"][0]["entries"] == 3

  def test_multiple_ledgers(self) -> None:
    ledgers = [
      _make_ledger("DL-001", "First"),
      _make_ledger("DL-002", "Second"),
    ]
    result = format_drift_list_table(ledgers, format_type="json")
    data = json.loads(result)
    assert len(data["items"]) == 2

  def test_truncate_option(self) -> None:
    ledger = _make_ledger(name="A" * 200)
    result = format_drift_list_table([ledger], format_type="table", truncate=True)
    assert isinstance(result, str)


class TestFormatDriftDetails(unittest.TestCase):
  """Tests for format_drift_details."""

  def test_basic_details(self) -> None:
    ledger = _make_ledger()
    result = format_drift_details(ledger)
    assert "ID: DL-047" in result
    assert "Name: Test ledger" in result
    assert "Status: open" in result
    assert "Entries: 0" in result

  def test_details_with_delta_ref(self) -> None:
    ledger = _make_ledger(delta_ref="DE-047")
    result = format_drift_details(ledger)
    assert "Delta: DE-047" in result

  def test_details_without_delta_ref(self) -> None:
    ledger = _make_ledger(delta_ref="")
    result = format_drift_details(ledger)
    assert "Delta:" not in result

  def test_details_with_body(self) -> None:
    ledger = _make_ledger(body="Some context about this ledger.")
    result = format_drift_details(ledger)
    assert "Some context about this ledger." in result

  def test_details_with_entries(self) -> None:
    entries = [
      _make_entry(
        "DL-047.001",
        "Entry one",
        status="resolved",
        severity="blocking",
        entry_type="contradiction",
      ),
      _make_entry(
        "DL-047.002",
        "Entry two",
        status="open",
        entry_type="stale_claim",
      ),
    ]
    ledger = _make_ledger(entries=entries)
    result = format_drift_details(ledger)
    assert "--- Entries ---" in result
    assert "DL-047.001: Entry one" in result
    assert "[resolved]" in result
    assert "(blocking)" in result
    assert "<contradiction>" in result
    assert "DL-047.002: Entry two" in result

  def test_entry_summary_minimal(self) -> None:
    """Entry summary with only id and title."""
    entry = _make_entry("DL-001.001", "Just a title", status="")
    ledger = _make_ledger(entries=[entry])
    result = format_drift_details(ledger)
    assert "DL-001.001: Just a title" in result

  def test_details_timestamps(self) -> None:
    ledger = _make_ledger(created="2026-01-01", updated="2026-03-08")
    result = format_drift_details(ledger)
    assert "Created: 2026-01-01" in result
    assert "Updated: 2026-03-08" in result


class TestFormatDriftDetailsJson(unittest.TestCase):
  """Tests for format_drift_details_json."""

  def test_basic_json(self) -> None:
    ledger = _make_ledger()
    result = format_drift_details_json(ledger)
    data = json.loads(result)
    assert data["id"] == "DL-047"
    assert data["name"] == "Test ledger"
    assert data["entries"] == []

  def test_json_with_entries(self) -> None:
    entries = [
      _make_entry(
        "DL-047.001",
        "Test entry",
        status="resolved",
        entry_type="contradiction",
        severity="blocking",
        sources=[Source(kind="spec", ref="SPEC-009", note="old claim")],
        claims=[Claim(kind="assertion", text="X contradicts Y", label="A")],
        affected_artifacts=["SPEC-009"],
      ),
    ]
    ledger = _make_ledger(entries=entries)
    result = format_drift_details_json(ledger)
    data = json.loads(result)
    assert len(data["entries"]) == 1
    entry = data["entries"][0]
    assert entry["id"] == "DL-047.001"
    assert entry["status"] == "resolved"
    assert entry["severity"] == "blocking"
    assert len(entry["sources"]) == 1
    assert entry["sources"][0]["kind"] == "spec"
    assert len(entry["claims"]) == 1

  def test_json_omits_empty_optional_fields(self) -> None:
    ledger = _make_ledger(entries=[_make_entry()])
    result = format_drift_details_json(ledger)
    data = json.loads(result)
    entry = data["entries"][0]
    assert "severity" not in entry
    assert "topic" not in entry
    assert "owner" not in entry

  def test_json_includes_path(self) -> None:
    ledger = _make_ledger()
    result = format_drift_details_json(ledger)
    data = json.loads(result)
    assert "path" in data


if __name__ == "__main__":
  unittest.main()
