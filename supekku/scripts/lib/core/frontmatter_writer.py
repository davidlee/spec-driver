"""Safe line-level frontmatter status updates.

Provides a shared primitive for updating the ``status`` and ``updated``
fields in YAML frontmatter without a full YAML round-trip, preserving
all other file content byte-for-byte.
"""

from __future__ import annotations

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


__all__ = ["update_frontmatter_status"]
