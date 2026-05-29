"""Tests for audit list formatting.

Covers VT-141-LIST-001, -004, -005.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from supekku.scripts.lib.changes.audit_check import AuditFindingsSummary
from supekku.scripts.lib.formatters.change_formatters import (
  format_audit_list_row,
  format_audit_list_table,
)


def _mock_audit(
  *,
  audit_id: str = "AUD-027",
  name: str = "Audit - DE-140 conformance",
  status: str = "completed",
  mode: str | None = "conformance",
  delta_ref: str | None = "DE-140",
) -> MagicMock:
  a = MagicMock()
  a.id = audit_id
  a.name = name
  a.status = status
  a.mode = mode
  a.delta_ref = delta_ref
  a.kind = "audit"
  a.slug = audit_id.lower()
  a.path = Path(f".spec-driver/audits/{audit_id}/{audit_id}.md")
  a.applies_to = {}
  a.tags = []
  a.ext_id = ""
  return a


SAMPLE_SUMMARY = AuditFindingsSummary(
  total=5, aligned=3, drift=1, risk=1, disposed=4,
)
EMPTY_SUMMARY = AuditFindingsSummary(0, 0, 0, 0, 0)


# ---------------------------------------------------------------------------
# VT-141-LIST-001: Enriched audit list columns
# ---------------------------------------------------------------------------


class TestFormatAuditListRow:
  """VT-141-LIST-001"""

  def test_all_columns_present(self) -> None:
    row = format_audit_list_row(_mock_audit(), SAMPLE_SUMMARY)
    assert set(row.keys()) == {
      "id", "name", "status", "mode",
      "delta_ref", "findings", "disposed",
    }

  def test_mode_glyph_conformance(self) -> None:
    row = format_audit_list_row(
      _mock_audit(mode="conformance"), SAMPLE_SUMMARY,
    )
    assert row["mode"] == "C"

  def test_mode_glyph_discovery(self) -> None:
    row = format_audit_list_row(
      _mock_audit(mode="discovery"), SAMPLE_SUMMARY,
    )
    assert row["mode"] == "D"

  def test_mode_em_dash_when_none(self) -> None:
    row = format_audit_list_row(
      _mock_audit(mode=None), SAMPLE_SUMMARY,
    )
    assert row["mode"] == "–"

  def test_delta_ref_shown(self) -> None:
    row = format_audit_list_row(
      _mock_audit(delta_ref="DE-140"), SAMPLE_SUMMARY,
    )
    assert row["delta_ref"] == "DE-140"

  def test_delta_ref_em_dash_when_none(self) -> None:
    row = format_audit_list_row(
      _mock_audit(delta_ref=None), SAMPLE_SUMMARY,
    )
    assert row["delta_ref"] == "–"

  def test_findings_cell(self) -> None:
    row = format_audit_list_row(_mock_audit(), SAMPLE_SUMMARY)
    assert row["findings"] == "5 (3a/1d/1r)"

  def test_disposed_cell(self) -> None:
    row = format_audit_list_row(_mock_audit(), SAMPLE_SUMMARY)
    assert row["disposed"] == "4/5"

  def test_name_strips_prefix(self) -> None:
    row = format_audit_list_row(
      _mock_audit(name="Audit - Some name"), SAMPLE_SUMMARY,
    )
    assert row["name"] == "Some name"


# ---------------------------------------------------------------------------
# VT-141-LIST-004: JSON output enriched
# ---------------------------------------------------------------------------


class TestFormatAuditListJson:
  """VT-141-LIST-004"""

  def test_json_includes_enriched_fields(self) -> None:
    audit = _mock_audit()
    summaries = {audit.id: SAMPLE_SUMMARY}
    output = format_audit_list_table(
      [audit], summaries, format_type="json",
    )
    data = json.loads(output)
    items = data["items"]
    assert len(items) == 1
    item = items[0]
    assert item["mode"] == "conformance"
    assert item["delta_ref"] == "DE-140"
    assert item["findings_total"] == 5
    assert item["findings_aligned"] == 3
    assert item["findings_drift"] == 1
    assert item["findings_risk"] == 1
    assert item["findings_disposed"] == 4


# ---------------------------------------------------------------------------
# VT-141-LIST-005: TSV output enriched
# ---------------------------------------------------------------------------


class TestFormatAuditListTsv:
  """VT-141-LIST-005"""

  def test_tsv_includes_enriched_columns(self) -> None:
    audit = _mock_audit()
    summaries = {audit.id: SAMPLE_SUMMARY}
    output = format_audit_list_table(
      [audit], summaries, format_type="tsv",
    )
    lines = output.strip().splitlines()
    assert len(lines) == 1
    cells = lines[0].split("\t")
    # 7 columns: ID, Name, Status, Mode, Delta, Findings, Disposed
    assert len(cells) == 7
    assert cells[0] == "AUD-027"
    assert cells[3] == "C"  # mode glyph
    assert cells[4] == "DE-140"  # delta_ref
    assert "3a" in cells[5]  # findings
    assert "4/5" in cells[6]  # disposed
