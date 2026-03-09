"""Memory display formatters.

Pure formatting functions with no business logic.
Formatters take MemoryRecord objects and return formatted strings for display.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.cell_helpers import (
  format_date_cell,
  format_tags_cell,
)
from supekku.scripts.lib.formatters.column_defs import MEMORY_COLUMNS, column_labels
from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_list_table,
)
from supekku.scripts.lib.formatters.theme import get_memory_status_style

if TYPE_CHECKING:
  from supekku.scripts.lib.memory.links import LinkGraphNode
  from supekku.scripts.lib.memory.models import MemoryRecord
  from supekku.scripts.lib.memory.staleness import StalenessInfo


# --- Detail view ---


def _format_detail_lines(record: MemoryRecord) -> list[str]:
  """Build lines for a memory detail view, omitting empty optional fields."""
  lines = [
    f"ID: {record.id}",
    f"Name: {record.name}",
    f"Status: {record.status}",
    f"Type: {record.memory_type}",
  ]

  if record.confidence:
    lines.append(f"Confidence: {record.confidence}")

  lines.extend(_format_dates(record))

  if record.summary:
    lines.append(f"Summary: {record.summary}")
  if record.tags:
    lines.append(f"Tags: {', '.join(record.tags)}")
  if record.owners:
    lines.append(f"Owners: {', '.join(record.owners)}")
  if record.audience:
    lines.append(f"Audience: {', '.join(record.audience)}")
  if record.visibility:
    lines.append(f"Visibility: {', '.join(record.visibility)}")
  if record.requires_reading:
    lines.append(f"Requires reading: {', '.join(record.requires_reading)}")

  lines.extend(_format_scope(record.scope))
  lines.extend(_format_priority(record.priority))
  lines.extend(_format_provenance(record.provenance))
  lines.extend(_format_relations(record.relations))
  lines.extend(_format_links(record.links))

  lines.append(f"Path: {record.path}")
  return lines


def _format_dates(record: MemoryRecord) -> list[str]:
  """Format date fields if present."""
  lines: list[str] = []
  for label, value in [
    ("Created", record.created),
    ("Updated", record.updated),
    ("Verified", record.verified),
    ("Review by", record.review_by),
  ]:
    if value:
      lines.append(f"{label}: {value.isoformat()}")
  return lines


def _format_scope(scope: dict) -> list[str]:
  """Format scope dict as indented sub-lines."""
  if not scope:
    return []
  lines = ["Scope:"]
  for key in ("paths", "globs", "commands", "languages", "platforms"):
    values = scope.get(key, [])
    if values:
      lines.append(f"  {key}: {', '.join(values)}")
  return lines


def _format_priority(priority: dict) -> list[str]:
  """Format priority dict as indented sub-lines."""
  if not priority:
    return []
  lines = ["Priority:"]
  if "severity" in priority:
    lines.append(f"  severity: {priority['severity']}")
  if "weight" in priority:
    lines.append(f"  weight: {priority['weight']}")
  return lines


def _format_provenance(provenance: dict) -> list[str]:
  """Format provenance dict as indented sub-lines."""
  if not provenance:
    return []
  sources = provenance.get("sources", [])
  if not sources:
    return []
  lines = ["Provenance:"]
  for src in sources:
    kind = src.get("kind", "")
    ref = src.get("ref", "")
    note = src.get("note", "")
    entry = f"  {kind}: {ref}"
    if note:
      entry += f" ({note})"
    lines.append(entry)
  return lines


def _format_links(links: dict) -> list[str]:
  """Format links dict as indented sub-lines."""
  if not links:
    return []
  out = links.get("out", [])
  missing = links.get("missing", [])
  if not out and not missing:
    return []
  lines = ["Links:"]
  for entry in out:
    target_id = entry.get("id", "")
    kind = entry.get("kind", "")
    label = entry.get("label")
    display = f"{target_id} ({kind})"
    if label:
      display += f" [{label}]"
    lines.append(f"  → {display}")
  for entry in missing:
    raw = entry.get("raw", "")
    lines.append(f"  ? {raw} (unresolved)")
  return lines


def _format_relations(relations: list[dict]) -> list[str]:
  """Format relations list as indented entries."""
  if not relations:
    return []
  lines = ["Relations:"]
  for rel in relations:
    rel_type = rel.get("type", "")
    target = rel.get("target", "")
    entry = f"  {rel_type} → {target}"
    annotation = rel.get("annotation", "")
    if annotation:
      entry += f" ({annotation})"
    lines.append(entry)
  return lines


def format_memory_details(record: MemoryRecord) -> str:
  """Format a memory record as multi-line detail string.

  Args:
    record: MemoryRecord to format.

  Returns:
    Human-readable detail string.
  """
  return "\n".join(_format_detail_lines(record))


# --- List views ---


def _prepare_memory_row(record: MemoryRecord) -> list[str]:
  """Prepare a single row for the memory table."""
  mem_id = f"[memory.id]{record.id}[/memory.id]"
  status_style = get_memory_status_style(record.status)
  status = f"[{status_style}]{record.status}[/{status_style}]"

  return [
    mem_id,
    status,
    record.memory_type,
    record.name,
    record.confidence or "",
    format_tags_cell(record.tags),
    format_date_cell(record.updated),
  ]


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate column widths for memory table based on terminal width."""
  # ID + Status + Type + Name(flex) + Confidence + Tags(flex) + Updated
  fixed = 8 + 10 + 10 + 10 + 10
  flex = max(terminal_width - fixed, 20)
  name_width = int(flex * 0.6)
  tags_width = flex - name_width
  return {3: name_width, 5: tags_width}


def _prepare_memory_tsv_row(record: MemoryRecord) -> list[str]:
  """Prepare a single memory record as a plain TSV row (no markup)."""
  return [
    record.id,
    record.status,
    record.memory_type,
    record.name,
    record.confidence or "",
    format_date_cell(record.updated, missing="N/A"),
  ]


def format_memory_list_table(
  records: Sequence[MemoryRecord],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format memory records as table, JSON, or TSV.

  Args:
    records: List of MemoryRecord objects.
    format_type: Output format (table|json|tsv).
    truncate: If True, truncate long fields.

  Returns:
    Formatted string in requested format.
  """
  return format_list_table(
    records,
    columns=column_labels(MEMORY_COLUMNS),
    title="Memory Records",
    prepare_row=_prepare_memory_row,
    prepare_tsv_row=_prepare_memory_tsv_row,
    to_json=format_memory_list_json,
    format_type=format_type,
    truncate=truncate,
    column_widths=_calculate_column_widths,
  )


def format_memory_list_json(records: Sequence[MemoryRecord]) -> str:
  """Format memory records as JSON array.

  Args:
    records: List of MemoryRecord objects.

  Returns:
    JSON string with structure: {"items": [...]}.
  """
  items = []
  for record in records:
    item: dict = {
      "id": record.id,
      "name": record.name,
      "status": record.status,
      "memory_type": record.memory_type,
      "path": record.path,
      "created": record.created,
      "updated": record.updated,
    }
    if record.tags:
      item["tags"] = record.tags
    if record.confidence:
      item["confidence"] = record.confidence
    if record.summary:
      item["summary"] = record.summary
    if record.links:
      item["links"] = record.links

    items.append(item)

  return format_as_json(items)


# --- Staleness views ---


_TIER_LABELS = {
  "attested": "scoped, attested",
  "unattested": "scoped, unattested",
  "unscoped": "unscoped",
}

_STALENESS_HEADER = (
  f"{'ID':<36} {'Confidence':<12} {'Verified':<12} {'Stale':<10} {'Scope'}"
)


def format_staleness_table(
  infos: Sequence[StalenessInfo],
  records: Mapping[str, MemoryRecord],
) -> str:
  """Format staleness info as a three-tier plain-text table.

  Tiers:
    1. Scoped + attested — sorted by commits_since descending
    2. Scoped + unattested — sorted by days_since descending
    3. Unscoped — sorted by days_since descending

  Empty tiers are omitted.

  Args:
    infos: StalenessInfo list from compute_batch_staleness.
    records: Mapping of memory_id → MemoryRecord for metadata.

  Returns:
    Formatted multi-tier string, or empty string if no infos.
  """
  if not infos:
    return ""

  attested, unattested, unscoped = _partition_tiers(infos)
  lines: list[str] = [_STALENESS_HEADER]

  if attested:
    attested.sort(
      key=lambda i: i.commits_since or 0,
      reverse=True,
    )
    lines.append(f"── {_TIER_LABELS['attested']} ──")
    for info in attested:
      lines.append(_format_staleness_row(info, records))

  if unattested:
    unattested.sort(
      key=lambda i: i.days_since or 0,
      reverse=True,
    )
    lines.append(f"── {_TIER_LABELS['unattested']} ──")
    for info in unattested:
      lines.append(_format_staleness_row(info, records))

  if unscoped:
    unscoped.sort(
      key=lambda i: i.days_since or 0,
      reverse=True,
    )
    lines.append(f"── {_TIER_LABELS['unscoped']} ──")
    for info in unscoped:
      lines.append(_format_staleness_row(info, records))

  return "\n".join(lines)


def _partition_tiers(
  infos: Sequence[StalenessInfo],
) -> tuple[
  list[StalenessInfo],
  list[StalenessInfo],
  list[StalenessInfo],
]:
  """Split staleness infos into three tiers."""
  attested: list[StalenessInfo] = []
  unattested: list[StalenessInfo] = []
  unscoped: list[StalenessInfo] = []

  for info in infos:
    if not info.has_scope:
      unscoped.append(info)
    elif info.verified_sha:
      attested.append(info)
    else:
      unattested.append(info)

  return attested, unattested, unscoped


def _format_staleness_row(
  info: StalenessInfo,
  records: Mapping[str, MemoryRecord],
) -> str:
  """Format a single staleness row."""
  record = records.get(info.memory_id)
  confidence = (record.confidence or "") if record else ""
  verified = info.verified_date.isoformat() if info.verified_date else "—"

  stale = _format_stale_cell(info)
  scope = _format_scope_cell(info)

  return f"{info.memory_id:<36} {confidence:<12} {verified:<12} {stale:<10} {scope}"


def _format_stale_cell(info: StalenessInfo) -> str:
  """Format the staleness indicator cell."""
  if info.has_scope and info.verified_sha and info.commits_since is not None:
    return f"{info.commits_since}\u2191"
  if info.days_since is not None:
    suffix = ", no sha" if info.has_scope else ""
    return f"({info.days_since}d{suffix})"
  return "—"


def _format_scope_cell(info: StalenessInfo) -> str:
  """Format the scope summary cell."""
  if info.scope_paths:
    return ", ".join(info.scope_paths[:3])
  return ""


# --- Graph views ---


def format_link_graph_table(nodes: Sequence[LinkGraphNode]) -> str:
  """Format link graph nodes as a compact table.

  Columns: depth, id, name, type.

  Args:
    nodes: List of LinkGraphNode objects (BFS order).

  Returns:
    Formatted table string. Empty string if no nodes.
  """
  if not nodes:
    return ""

  lines = []
  for node in nodes:
    indent = "  " * node.depth
    lines.append(f"{node.depth}  {indent}{node.id}\t{node.name}\t{node.memory_type}")
  return "\n".join(lines)


def format_link_graph_tree(nodes: Sequence[LinkGraphNode]) -> str:
  """Format link graph nodes as an indented tree.

  Each depth level is indented by two spaces. Shows id and name.

  Args:
    nodes: List of LinkGraphNode objects (BFS order).

  Returns:
    Formatted tree string. Empty string if no nodes.
  """
  if not nodes:
    return ""

  lines = []
  for node in nodes:
    indent = "  " * node.depth
    type_suffix = f" ({node.memory_type})" if node.memory_type else ""
    lines.append(f"{indent}{node.id} — {node.name}{type_suffix}")
  return "\n".join(lines)


def format_link_graph_json(nodes: Sequence[LinkGraphNode]) -> str:
  """Format link graph nodes as JSON array.

  Args:
    nodes: List of LinkGraphNode objects.

  Returns:
    JSON string with list of node dicts.
  """
  items = [
    {
      "id": n.id,
      "name": n.name,
      "depth": n.depth,
      "memory_type": n.memory_type,
    }
    for n in nodes
  ]
  return json.dumps(items, indent=2)
