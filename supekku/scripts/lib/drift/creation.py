"""Drift ledger creation.

Creates new drift ledger files with frontmatter and entry heading.
See DR-065 §10 for the creation template.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from supekku.scripts.lib.core.ids import next_sequential_id
from supekku.scripts.lib.core.paths import get_drift_dir
from supekku.scripts.lib.core.strings import slugify


def create_drift_ledger(
  name: str,
  *,
  delta_ref: str = "",
  repo_root: Path | None = None,
) -> Path:
  """Create a new drift ledger file.

  Allocates the next DL-NNN ID by scanning existing files. Creates
  .spec-driver/drift/ directory if needed.

  Args:
    name: Ledger name/title.
    delta_ref: Optional owning delta (e.g. "DE-065").
    repo_root: Repository root (auto-detected if None).

  Returns:
    Path to the created ledger file.

  Raises:
    ValueError: If name is empty.
  """
  if not name.strip():
    msg = "Drift ledger name cannot be empty"
    raise ValueError(msg)

  drift_dir = get_drift_dir(repo_root)
  drift_dir.mkdir(parents=True, exist_ok=True)

  next_id = _next_ledger_id(drift_dir)
  slug = slugify(name)
  filename = f"{next_id}-{slug}.md"
  path = drift_dir / filename

  today = date.today().isoformat()
  content = _render_template(next_id, name, today, delta_ref)
  path.write_text(content)
  return path


def _next_ledger_id(drift_dir: Path) -> str:
  """Determine the next DL-NNN ID by scanning existing files."""
  names = [p.name for p in drift_dir.iterdir()]
  return next_sequential_id(names, "DL")


def _render_template(ledger_id: str, name: str, today: str, delta_ref: str) -> str:
  """Render the drift ledger markdown template (DR-065 §10)."""
  delta_line = f"delta_ref: {delta_ref}" if delta_ref else "delta_ref: ''"
  return f"""---
id: {ledger_id}
name: {name}
created: '{today}'
updated: '{today}'
status: open
kind: drift_ledger
{delta_line}
---

# {ledger_id} — {name}

## Entries

<!-- append entries as ### sections with fenced YAML blocks -->
"""
