"""Sync preference persistence via marker files.

Manages persisted sync preferences stored under .spec-driver/.
Currently supports a single preference: spec auto-creation opt-in.
"""

from __future__ import annotations

from pathlib import Path

MARKER_FILENAME = "enable_spec_autocreate"
_SPEC_DRIVER_DIR = ".spec-driver"


def spec_autocreate_enabled(root: Path) -> bool:
  """Check whether spec auto-creation is enabled for this repo."""
  return (root / _SPEC_DRIVER_DIR / MARKER_FILENAME).exists()


def persist_spec_autocreate(root: Path) -> None:
  """Persist spec auto-creation preference as a marker file."""
  spec_driver_dir = root / _SPEC_DRIVER_DIR
  spec_driver_dir.mkdir(parents=True, exist_ok=True)
  (spec_driver_dir / MARKER_FILENAME).touch()
