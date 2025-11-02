"""Stub spec detection logic.

Detects whether a spec file is a stub (auto-generated) vs manually modified.
"""

from pathlib import Path

import yaml


def is_stub_spec(spec_path: Path) -> bool:
  """Detect if spec is a stub based on status and line count.

  Uses two-stage detection:
  1. Primary: Check if status == "stub" in frontmatter
  2. Fallback: Check if line count ≤ 30 (handles human error/typos)

  Args:
    spec_path: Path to spec file

  Returns:
    True if spec is a stub, False if modified

  Raises:
    FileNotFoundError: If spec_path does not exist
  """
  if not spec_path.exists():
    raise FileNotFoundError(f"Spec file not found: {spec_path}")

  content = spec_path.read_text(encoding="utf-8")

  # Primary: explicit stub status
  # Parse frontmatter manually (avoid strict validation)
  if content.startswith("---\n"):
    try:
      # Find the closing ---
      end_idx = content.find("\n---\n", 4)
      if end_idx != -1:
        frontmatter_text = content[4:end_idx]
        frontmatter = yaml.safe_load(frontmatter_text)
        if isinstance(frontmatter, dict) and frontmatter.get("status") == "stub":
          return True
    except yaml.YAMLError:
      # If frontmatter is invalid, fall through to line count check
      pass

  # Fallback: line count for legacy/human-error tolerance
  # Empirically: auto-generated tech specs = 28 lines
  # Real edits add significant content (356+ lines observed)
  total_lines = content.count("\n") + 1
  return total_lines <= 30
