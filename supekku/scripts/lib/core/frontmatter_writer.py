"""Safe line-level frontmatter field updates.

Provides shared primitives for updating YAML frontmatter fields without
a full YAML round-trip, preserving all other file content byte-for-byte.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


def update_frontmatter_status(path: Path, status: str) -> bool:
  """Update status and updated date in artifact frontmatter.

  Performs a line-level replacement within the YAML frontmatter block,
  writing ``status`` unquoted and ``updated`` single-quoted to match
  project convention.

  Args:
    path: Path to the artifact markdown file (must exist).
    status: New status value (must be non-empty after stripping).

  Returns:
    True if a ``status:`` field was found and updated.
    False if no ``status:`` field exists in the frontmatter.

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

  content = path.read_text(encoding="utf-8")
  lines = content.splitlines()
  today = date.today().isoformat()

  in_frontmatter = False
  updated_lines: list[str] = []
  status_updated = False

  for line in lines:
    if line.strip() == "---":
      in_frontmatter = not in_frontmatter
      updated_lines.append(line)
      continue

    if in_frontmatter and line.startswith("status:"):
      updated_lines.append(f"status: {status}")
      status_updated = True
    elif in_frontmatter and line.startswith("updated:"):
      updated_lines.append(f"updated: '{today}'")
    else:
      updated_lines.append(line)

  if not status_updated:
    return False

  path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
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
  """Update multiple frontmatter fields via line-level replacement.

  For each key in *updates*, finds ``key: ...`` in frontmatter and
  replaces the value. Only operates on simple scalar fields (not
  nested objects or multiline values).

  Fields not found in existing frontmatter are inserted before the
  closing ``---`` marker, in dict iteration order.

  Args:
    path: Path to the artifact markdown file (must exist).
    updates: Mapping of field name to new value string.
      Values are written as-is (caller is responsible for quoting).

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

  content = path.read_text(encoding="utf-8")
  lines = content.splitlines()

  result_lines, found_fields, closing_marker_idx = _replace_fields(lines, updates)
  missing = _insert_missing_fields(
    result_lines,
    updates,
    found_fields,
    closing_marker_idx,
  )

  path.write_text("\n".join(result_lines) + "\n", encoding="utf-8")

  return FieldUpdateResult(updated=found_fields, inserted=set(missing))


def _replace_fields(
  lines: list[str],
  updates: dict[str, str],
) -> tuple[list[str], set[str], int | None]:
  """Replace matching frontmatter fields, tracking which were found."""
  in_frontmatter = False
  result_lines: list[str] = []
  found_fields: set[str] = set()
  closing_marker_idx: int | None = None

  for line in lines:
    if line.strip() == "---":
      if in_frontmatter:
        closing_marker_idx = len(result_lines)
      in_frontmatter = not in_frontmatter
      result_lines.append(line)
      continue

    replaced = (
      _try_replace_line(line, updates, found_fields) if in_frontmatter else None
    )
    result_lines.append(replaced if replaced is not None else line)

  return result_lines, found_fields, closing_marker_idx


def _try_replace_line(
  line: str,
  updates: dict[str, str],
  found_fields: set[str],
) -> str | None:
  """Try to match a frontmatter line against updates. Returns replacement or None."""
  for field_name, value in updates.items():
    if line.startswith(f"{field_name}:"):
      found_fields.add(field_name)
      return f"{field_name}: {value}"
  return None


def _insert_missing_fields(
  result_lines: list[str],
  updates: dict[str, str],
  found_fields: set[str],
  closing_marker_idx: int | None,
) -> list[str]:
  """Insert fields not found during replacement before the closing ---."""
  missing = [k for k in updates if k not in found_fields]
  if missing and closing_marker_idx is not None:
    for offset, field_name in enumerate(missing):
      result_lines.insert(
        closing_marker_idx + offset,
        f"{field_name}: {updates[field_name]}",
      )
  return missing


__all__ = [
  "FieldUpdateResult",
  "update_frontmatter_fields",
  "update_frontmatter_status",
]
