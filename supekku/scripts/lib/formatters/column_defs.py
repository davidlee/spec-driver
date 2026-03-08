"""Shared column metadata per artifact type.

Single source of truth for "what columns to show" in list views.
Consumed by both CLI formatters and TUI list views (DEC-053-02).

Each definition maps an artifact type to its list-view columns.
Column order is display order.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnDef:
  """Column definition for a list view."""

  label: str
  field: str
  style_key: str | None = None


# --- Per-artifact-type column definitions ---

SPEC_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="spec.id"),
  ColumnDef(label="Name", field="name"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
]

ADR_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="adr.id"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Updated", field="updated"),
]

CHANGE_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="change.id"),
  ColumnDef(label="Name", field="name"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
]

PLAN_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="change.id"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Name", field="name"),
  ColumnDef(label="Delta", field="delta"),
]

REQUIREMENT_COLUMNS = [
  ColumnDef(label="Spec", field="spec"),
  ColumnDef(label="Label", field="label", style_key="requirement.id"),
  ColumnDef(label="Category", field="category", style_key="requirement.category"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
]

BACKLOG_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="backlog.id"),
  ColumnDef(label="Kind", field="kind"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Severity", field="severity"),
]

CARD_COLUMNS = [
  ColumnDef(label="ID", field="id"),
  ColumnDef(label="Lane", field="lane"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Created", field="created"),
]

MEMORY_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="memory.id"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Type", field="memory_type"),
  ColumnDef(label="Name", field="name"),
  ColumnDef(label="Confidence", field="confidence"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Updated", field="updated"),
]

POLICY_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="policy.id"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Updated", field="updated"),
]

STANDARD_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="standard.id"),
  ColumnDef(label="Title", field="title"),
  ColumnDef(label="Tags", field="tags"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Updated", field="updated"),
]

DRIFT_COLUMNS = [
  ColumnDef(label="ID", field="id", style_key="drift.id"),
  ColumnDef(label="Name", field="name"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Entries", field="entries"),
  ColumnDef(label="Delta", field="delta_ref"),
  ColumnDef(label="Updated", field="updated"),
]

PHASE_COLUMNS = [
  ColumnDef(label="Phase", field="id"),
  ColumnDef(label="Status", field="status"),
  ColumnDef(label="Objective", field="objective"),
]

# Shared column for external system references (used with --external flag)
EXT_ID_COLUMN = ColumnDef(label="ExtID", field="ext_id")


def column_labels(columns: list[ColumnDef]) -> list[str]:
  """Extract label list from column definitions."""
  return [c.label for c in columns]
