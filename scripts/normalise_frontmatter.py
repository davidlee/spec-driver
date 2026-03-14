#!/usr/bin/env python3
"""Normalise .spec-driver/**/*.md frontmatter via CompactDumper.

Body content is preserved as-is. Files without valid frontmatter are skipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.core.spec_utils import (  # noqa: E402
  dump_markdown_file,
  load_markdown_file,
)


def normalise_file(path: Path) -> bool:
  """Normalise one file. Returns True if the file was changed."""
  original = path.read_text(encoding="utf-8")

  try:
    fm, body = load_markdown_file(path)
  except Exception as exc:  # noqa: BLE001
    print(f"  SKIP  {path}  ({exc})", file=sys.stderr)
    return False

  if not fm:
    return False

  dump_markdown_file(path, fm, body)
  normalised = path.read_text(encoding="utf-8")
  return normalised != original


def main() -> None:
  spec_dir = ROOT / ".spec-driver"
  md_files = sorted(spec_dir.rglob("*.md"))
  print(f"Found {len(md_files)} markdown files in .spec-driver/")

  changed = 0
  skipped = 0
  unchanged = 0

  for path in md_files:
    if normalise_file(path):
      changed += 1
    else:
      # Check if it was skipped (no frontmatter) or just unchanged
      try:
        fm, _ = load_markdown_file(path)
        if not fm:
          skipped += 1
        else:
          unchanged += 1
      except Exception:  # noqa: BLE001
        skipped += 1

  print(
    f"\nResults: {changed} changed, {unchanged} unchanged,"
    f" {skipped} skipped (no frontmatter)",
  )


if __name__ == "__main__":
  main()
