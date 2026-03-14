"""Canonical frontmatter writer with YAML round-trip formatting.

Provides primitives for reading, mutating, and writing YAML frontmatter
using a deterministic ``CompactDumper`` that produces idempotent output.
Body content (including code-fenced YAML blocks) passes through untouched.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.core.spec_utils import (
  dump_markdown_file,
  load_markdown_file,
)

# ---------------------------------------------------------------------------
# CompactDumper — canonical YAML formatting
# ---------------------------------------------------------------------------

# Threshold for flow-style list rendering.  Lists whose total rendered
# item-character count (plus separators) stays below this limit are emitted
# in compact flow style ``[a, b, c]``; longer or complex lists use block
# style.
_FLOW_LIST_WIDTH_LIMIT = 80


# Date-string pattern: double-quote to match prettier convention.
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class CompactDumper(yaml.SafeDumper):
  """YAML dumper producing compact, prettier-compatible frontmatter.

  - Short scalar lists render as flow-style ``[a, b, c]``.
  - Long lists and lists containing dicts render as block-style.
  - Sequences always indent under their parent key (no indentless).
  - Date-like strings are double-quoted.
  """

  def increase_indent(  # noqa: D102
    self,
    flow: bool = False,
    indentless: bool = False,  # noqa: ARG002
  ) -> None:
    # Never use indentless sequences — always indent under parent key.
    # This matches prettier's YAML formatter behaviour.
    return super().increase_indent(flow=flow, indentless=False)


def _represent_str(dumper: CompactDumper, data: str) -> yaml.Node:
  """Double-quote date-pattern strings to match prettier convention."""
  if _DATE_RE.match(data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
  return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def _represent_list(dumper: CompactDumper, data: list) -> yaml.Node:
  """Flow-style for short scalar lists, block-style otherwise."""
  use_flow = (
    all(isinstance(x, (str, int, float, bool)) for x in data)
    and sum(len(str(x)) for x in data) + 2 * len(data) < _FLOW_LIST_WIDTH_LIMIT
  )
  return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=use_flow)


CompactDumper.add_representer(str, _represent_str)
CompactDumper.add_representer(list, _represent_list)


def dump_frontmatter_yaml(data: dict[str, Any]) -> str:
  """Render a frontmatter dict as canonical YAML text (no ``---`` markers).

  Uses ``CompactDumper`` for deterministic, idempotent output.
  """
  return yaml.dump(
    data,
    Dumper=CompactDumper,
    sort_keys=False,
    allow_unicode=True,
    width=10000,
  ).strip()


# ---------------------------------------------------------------------------
# Core mutator primitive
# ---------------------------------------------------------------------------


def update_frontmatter(
  path: Path,
  mutator: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
  """Load frontmatter, apply *mutator*, bump ``updated``, and write back.

  Body content (including code-fenced YAML blocks) passes through
  untouched.  The frontmatter is re-serialised with ``CompactDumper``
  for canonical formatting.

  Args:
    path: Path to the artifact markdown file (must exist).
    mutator: Callable that modifies the frontmatter dict in-place.

  Returns:
    The mutated frontmatter dict.

  Raises:
    FileNotFoundError: If *path* does not exist.
  """
  if not path.exists():
    msg = f"File not found: {path}"
    raise FileNotFoundError(msg)

  frontmatter_data, body = load_markdown_file(path)
  mutator(frontmatter_data)
  frontmatter_data["updated"] = date.today().isoformat()
  dump_markdown_file(path, frontmatter_data, body)
  return frontmatter_data


# ---------------------------------------------------------------------------
# Scalar field operations (backward-compatible wrappers)
# ---------------------------------------------------------------------------


def update_frontmatter_status(path: Path, status: str) -> bool:
  """Update ``status`` and ``updated`` date in artifact frontmatter.

  Args:
    path: Path to the artifact markdown file (must exist).
    status: New status value (must be non-empty after stripping).

  Returns:
    True if a ``status`` field was found and updated.
    False if no ``status`` field exists in the frontmatter.

  Raises:
    FileNotFoundError: If *path* does not exist.
    ValueError: If *status* is empty or whitespace-only.
  """
  if not status or not status.strip():
    msg = "Status must not be empty"
    raise ValueError(msg)

  if not path.exists():
    msg = f"File not found: {path}"
    raise FileNotFoundError(msg)

  frontmatter_data, body = load_markdown_file(path)
  if "status" not in frontmatter_data:
    return False

  frontmatter_data["status"] = status
  frontmatter_data["updated"] = date.today().isoformat()
  dump_markdown_file(path, frontmatter_data, body)
  return True


@dataclass
class FieldUpdateResult:
  """Result of a frontmatter field update operation."""

  updated: set[str] = field(default_factory=set)
  """Fields that existed in frontmatter and were replaced."""

  inserted: set[str] = field(default_factory=set)
  """Fields that were missing from frontmatter and added."""


def update_frontmatter_fields(
  path: Path,
  updates: dict[str, str],
) -> FieldUpdateResult:
  """Update multiple frontmatter fields.

  For each key in *updates*, sets the field to the given value.
  Tracks which fields already existed (updated) vs were new (inserted).

  Args:
    path: Path to the artifact markdown file (must exist).
    updates: Mapping of field name to new value string.

  Returns:
    FieldUpdateResult with sets of updated and inserted field names.

  Raises:
    FileNotFoundError: If *path* does not exist.
    ValueError: If *updates* is empty.
  """
  if not updates:
    msg = "Updates must not be empty"
    raise ValueError(msg)

  if not path.exists():
    msg = f"File not found: {path}"
    raise FileNotFoundError(msg)

  frontmatter_data, body = load_markdown_file(path)
  existing_keys = set(frontmatter_data.keys())

  for key, value in updates.items():
    frontmatter_data[key] = value

  frontmatter_data["updated"] = date.today().isoformat()
  dump_markdown_file(path, frontmatter_data, body)

  updated_keys = set(updates.keys()) & existing_keys
  inserted_keys = set(updates.keys()) - existing_keys
  return FieldUpdateResult(updated=updated_keys, inserted=inserted_keys)


# ---------------------------------------------------------------------------
# List field operations
# ---------------------------------------------------------------------------


@dataclass
class ListUpdateResult:
  """Result of a frontmatter list field operation."""

  field: str
  """Field name that was operated on."""

  added: list[str] = field(default_factory=list)
  """Items actually added (were not already present)."""

  removed: list[str] = field(default_factory=list)
  """Items actually removed (were present)."""

  final: list[str] = field(default_factory=list)
  """Resulting list after the operation."""


def add_frontmatter_list_items(
  path: Path,
  field_name: str,
  items: list[str],
  *,
  sort: bool = True,
) -> ListUpdateResult:
  """Add items to a frontmatter list field.

  Creates the field if absent.  Deduplicates items.  Optionally sorts
  the resulting list (default: True).

  Args:
    path: Path to the artifact markdown file (must exist).
    field_name: Frontmatter field name (e.g. ``"tags"``).
    items: Items to add.
    sort: Whether to sort the resulting list.

  Returns:
    ListUpdateResult describing what changed.

  Raises:
    FileNotFoundError: If *path* does not exist.
    ValueError: If *items* is empty.
  """
  if not items:
    msg = "Items must not be empty"
    raise ValueError(msg)

  added: list[str] = []

  def _mutate(fm: dict[str, Any]) -> None:
    current = fm.get(field_name)
    if not isinstance(current, list):
      current = []
    existing = set(current)
    for item in items:
      if item not in existing:
        current.append(item)
        existing.add(item)
        added.append(item)
    if sort:
      current.sort()
    fm[field_name] = current

  result_fm = update_frontmatter(path, _mutate)
  final = result_fm.get(field_name, [])
  return ListUpdateResult(
    field=field_name,
    added=added,
    removed=[],
    final=list(final),
  )


def remove_frontmatter_list_items(
  path: Path,
  field_name: str,
  items: list[str],
) -> ListUpdateResult:
  """Remove items from a frontmatter list field.

  Missing items are silently ignored.  The field is retained (as an
  empty list) even when all items are removed.

  Args:
    path: Path to the artifact markdown file (must exist).
    field_name: Frontmatter field name (e.g. ``"tags"``).
    items: Items to remove.

  Returns:
    ListUpdateResult describing what changed.

  Raises:
    FileNotFoundError: If *path* does not exist.
    ValueError: If *items* is empty.
  """
  if not items:
    msg = "Items must not be empty"
    raise ValueError(msg)

  removed: list[str] = []

  def _mutate(fm: dict[str, Any]) -> None:
    current = fm.get(field_name)
    if not isinstance(current, list):
      fm[field_name] = []
      return
    to_remove = set(items)
    for item in current:
      if item in to_remove:
        removed.append(item)
    fm[field_name] = [x for x in current if x not in to_remove]

  result_fm = update_frontmatter(path, _mutate)
  final = result_fm.get(field_name, [])
  return ListUpdateResult(
    field=field_name,
    added=[],
    removed=removed,
    final=list(final),
  )


__all__ = [
  "CompactDumper",
  "FieldUpdateResult",
  "ListUpdateResult",
  "add_frontmatter_list_items",
  "dump_frontmatter_yaml",
  "remove_frontmatter_list_items",
  "update_frontmatter",
  "update_frontmatter_fields",
  "update_frontmatter_status",
]
