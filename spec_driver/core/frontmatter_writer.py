"""Canonical frontmatter writer with YAML round-trip formatting.

Provides primitives for reading, mutating, and writing YAML frontmatter.
Delegates emission to `spec_driver.core.yaml_emit.emit_yaml_block` so the
no-comment emit path stays a single source of truth (POL-001). `CompactDumper`
is re-exported as an alias of the canonical `_FrontmatterDumper`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .spec_utils import (
  dump_markdown_file_update,
  load_markdown_file,
)
from .yaml_emit import (
  _FrontmatterDumper as CompactDumper,
)
from .yaml_emit import emit_yaml_block


def dump_frontmatter_yaml(data: dict[str, Any]) -> str:
  """Render a frontmatter dict as canonical YAML text (no ``---`` markers).

  Thin delegation to `emit_yaml_block` (no-comment path).
  """
  return emit_yaml_block(data)


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
  dump_markdown_file_update(path, frontmatter_data, body)
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
  dump_markdown_file_update(path, frontmatter_data, body)
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
  dump_markdown_file_update(path, frontmatter_data, body)

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
