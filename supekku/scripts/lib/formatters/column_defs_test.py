"""Tests for shared column definitions (VT-053-column-defs)."""

from __future__ import annotations

from supekku.scripts.lib.formatters.column_defs import (
  ADR_COLUMNS,
  BACKLOG_COLUMNS,
  CARD_COLUMNS,
  CHANGE_COLUMNS,
  MEMORY_COLUMNS,
  PHASE_COLUMNS,
  PLAN_COLUMNS,
  POLICY_COLUMNS,
  REQUIREMENT_COLUMNS,
  SPEC_COLUMNS,
  STANDARD_COLUMNS,
  ColumnDef,
  column_labels,
)

ALL_COLUMN_SETS = {
  "spec": SPEC_COLUMNS,
  "adr": ADR_COLUMNS,
  "change": CHANGE_COLUMNS,
  "plan": PLAN_COLUMNS,
  "requirement": REQUIREMENT_COLUMNS,
  "backlog": BACKLOG_COLUMNS,
  "card": CARD_COLUMNS,
  "memory": MEMORY_COLUMNS,
  "policy": POLICY_COLUMNS,
  "standard": STANDARD_COLUMNS,
  "phase": PHASE_COLUMNS,
}


class TestColumnDef:
  """ColumnDef is a simple metadata container."""

  def test_creation(self):
    col = ColumnDef(label="ID", field="id", style_key="spec.id")
    assert col.label == "ID"
    assert col.field == "id"
    assert col.style_key == "spec.id"

  def test_style_key_optional(self):
    col = ColumnDef(label="Name", field="name")
    assert col.style_key is None

  def test_frozen(self):
    col = ColumnDef(label="ID", field="id")
    try:
      col.label = "Changed"  # type: ignore[misc]
      assert False, "Should be frozen"  # noqa: B011
    except AttributeError:
      pass


class TestColumnLabels:
  """column_labels extracts label list."""

  def test_spec_labels(self):
    labels = column_labels(SPEC_COLUMNS)
    assert labels == ["ID", "Name", "Tags", "Status"]

  def test_adr_labels(self):
    labels = column_labels(ADR_COLUMNS)
    assert labels == ["ID", "Title", "Tags", "Status", "Updated"]

  def test_change_labels(self):
    labels = column_labels(CHANGE_COLUMNS)
    assert labels == ["ID", "Name", "Tags", "Status"]

  def test_requirement_labels(self):
    labels = column_labels(REQUIREMENT_COLUMNS)
    assert labels == ["Spec", "Label", "Category", "Title", "Tags", "Status"]

  def test_backlog_labels(self):
    labels = column_labels(BACKLOG_COLUMNS)
    assert labels == ["ID", "Kind", "Title", "Tags", "Status", "Severity"]

  def test_card_labels(self):
    labels = column_labels(CARD_COLUMNS)
    assert labels == ["ID", "Lane", "Title", "Created"]

  def test_memory_labels(self):
    labels = column_labels(MEMORY_COLUMNS)
    assert labels == ["ID", "Status", "Type", "Name", "Confidence", "Tags", "Updated"]

  def test_policy_labels(self):
    labels = column_labels(POLICY_COLUMNS)
    assert labels == ["ID", "Title", "Tags", "Status", "Updated"]

  def test_standard_labels(self):
    labels = column_labels(STANDARD_COLUMNS)
    assert labels == ["ID", "Title", "Tags", "Status", "Updated"]


class TestAllColumnSetsExist:
  """Every artifact type has a column definition."""

  def test_all_sets_non_empty(self):
    for name, cols in ALL_COLUMN_SETS.items():
      assert len(cols) > 0, f"{name} columns should not be empty"

  def test_all_sets_have_id_or_label(self):
    """Every column set should have an identifying column."""
    for name, cols in ALL_COLUMN_SETS.items():
      field_names = [c.field for c in cols]
      has_id = "id" in field_names or "label" in field_names
      assert has_id, f"{name} columns should have an id/label field"

  def test_column_labels_match_existing_formatters(self):
    """Regression: labels must match what existing formatters use."""
    # These are the exact column lists from the formatters, verified by grep
    assert column_labels(SPEC_COLUMNS) == ["ID", "Name", "Tags", "Status"]
    assert column_labels(ADR_COLUMNS) == ["ID", "Title", "Tags", "Status", "Updated"]
    assert column_labels(CHANGE_COLUMNS) == ["ID", "Name", "Tags", "Status"]
    assert column_labels(BACKLOG_COLUMNS) == [
      "ID",
      "Kind",
      "Title",
      "Tags",
      "Status",
      "Severity",
    ]
    assert column_labels(CARD_COLUMNS) == ["ID", "Lane", "Title", "Created"]
    assert column_labels(MEMORY_COLUMNS) == [
      "ID",
      "Status",
      "Type",
      "Name",
      "Confidence",
      "Tags",
      "Updated",
    ]
    assert column_labels(POLICY_COLUMNS) == [
      "ID",
      "Title",
      "Tags",
      "Status",
      "Updated",
    ]
    assert column_labels(STANDARD_COLUMNS) == [
      "ID",
      "Title",
      "Tags",
      "Status",
      "Updated",
    ]
    assert column_labels(REQUIREMENT_COLUMNS) == [
      "Spec",
      "Label",
      "Category",
      "Title",
      "Tags",
      "Status",
    ]
    assert column_labels(PLAN_COLUMNS) == ["ID", "Status", "Name", "Delta"]
