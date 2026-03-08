"""Drift ledger display formatters.

Pure formatting functions with no business logic.
Formatters take DriftLedger/DriftEntry objects and return formatted strings.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.column_defs import DRIFT_COLUMNS, column_labels
from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_list_table,
)
from supekku.scripts.lib.formatters.theme import get_drift_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.drift.models import DriftEntry, DriftLedger


def format_drift_list_table(
  ledgers: Sequence[DriftLedger],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format drift ledgers as table, JSON, or TSV.

  Args:
    ledgers: Drift ledgers to format.
    format_type: Output format (table|json|tsv).
    truncate: If True, truncate long fields to fit terminal width.

  Returns:
    Formatted string in requested format.
  """
  return format_list_table(
    ledgers,
    columns=column_labels(DRIFT_COLUMNS),
    title="Drift Ledgers",
    prepare_row=_prepare_drift_row,
    prepare_tsv_row=_prepare_drift_tsv_row,
    to_json=_drift_list_to_json,
    format_type=format_type,
    truncate=truncate,
  )


def _prepare_drift_row(ledger: DriftLedger) -> list[str]:
  """Prepare a Rich-markup table row for a drift ledger."""
  ledger_id = f"[drift.id]{ledger.id}[/drift.id]"
  status_style = get_drift_status_style(ledger.status)
  status_styled = f"[{status_style}]{ledger.status}[/{status_style}]"
  entry_count = str(len(ledger.entries))
  delta = ledger.delta_ref or ""
  return [ledger_id, ledger.name, status_styled, entry_count, delta, ledger.updated]


def _prepare_drift_tsv_row(ledger: DriftLedger) -> list[str]:
  """Prepare a plain TSV row for a drift ledger."""
  return [
    ledger.id,
    ledger.name,
    ledger.status,
    str(len(ledger.entries)),
    ledger.delta_ref,
    ledger.updated,
  ]


def _drift_list_to_json(ledgers: Sequence[DriftLedger]) -> str:
  """Serialize drift ledgers to JSON."""
  items = []
  for ledger in ledgers:
    items.append(
      {
        "id": ledger.id,
        "name": ledger.name,
        "status": ledger.status,
        "entries": len(ledger.entries),
        "delta_ref": ledger.delta_ref,
        "created": ledger.created,
        "updated": ledger.updated,
      }
    )
  return format_as_json(items)


def format_drift_details(ledger: DriftLedger) -> str:
  """Format a single drift ledger with full details.

  Args:
    ledger: DriftLedger to format.

  Returns:
    Multi-line formatted string with ledger metadata and entry summaries.
  """
  lines = [
    f"ID: {ledger.id}",
    f"Name: {ledger.name}",
    f"Status: {ledger.status}",
    f"Path: {ledger.path}",
  ]
  if ledger.delta_ref:
    lines.append(f"Delta: {ledger.delta_ref}")
  if ledger.created:
    lines.append(f"Created: {ledger.created}")
  if ledger.updated:
    lines.append(f"Updated: {ledger.updated}")

  lines.append(f"Entries: {len(ledger.entries)}")

  if ledger.body:
    lines.append("")
    lines.append(ledger.body)

  if ledger.entries:
    lines.append("")
    lines.append("--- Entries ---")
    for entry in ledger.entries:
      lines.append(_format_entry_summary(entry))

  return "\n".join(lines)


def _format_entry_summary(entry: DriftEntry) -> str:
  """Format a single entry as a one-line summary."""
  parts = [f"  {entry.id}: {entry.title}"]
  if entry.status:
    parts.append(f"[{entry.status}]")
  if entry.severity:
    parts.append(f"({entry.severity})")
  if entry.entry_type:
    parts.append(f"<{entry.entry_type}>")
  return " ".join(parts)


def _entry_to_dict(entry: DriftEntry) -> dict:
  """Serialize a DriftEntry to a JSON-friendly dict."""
  result: dict = {
    "id": entry.id,
    "title": entry.title,
    "status": entry.status,
    "entry_type": entry.entry_type,
  }
  # Optional scalar fields
  for field in (
    "severity",
    "topic",
    "owner",
    "assessment",
    "resolution_path",
    "resolution_ref",
  ):
    value = getattr(entry, field)
    if value:
      result[field] = value
  if entry.affected_artifacts:
    result["affected_artifacts"] = entry.affected_artifacts
  if entry.sources:
    result["sources"] = [
      {"kind": s.kind, "ref": s.ref, "note": s.note} for s in entry.sources
    ]
  if entry.claims:
    result["claims"] = [
      {"kind": c.kind, "text": c.text, "label": c.label} for c in entry.claims
    ]
  return result


def format_drift_details_json(ledger: DriftLedger) -> str:
  """Format a drift ledger as JSON with full entry details.

  Args:
    ledger: DriftLedger to format.

  Returns:
    JSON string with ledger and entries.
  """
  output = {
    "id": ledger.id,
    "name": ledger.name,
    "status": ledger.status,
    "path": str(ledger.path),
    "delta_ref": ledger.delta_ref,
    "created": ledger.created,
    "updated": ledger.updated,
    "entries": [_entry_to_dict(e) for e in ledger.entries],
  }
  return json.dumps(output, indent=2, default=str)
