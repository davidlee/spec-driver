"""Sync preference persistence via workflow.toml.

Manages the spec auto-creation preference, stored in [sync] section of
workflow.toml.  Falls back to the legacy marker file for backward compat
and migrates on first persist.
"""

from __future__ import annotations

from pathlib import Path

import tomlkit

from .config import load_workflow_config
from .paths import SPEC_DRIVER_DIR

_LEGACY_MARKER = "enable_spec_autocreate"
_WORKFLOW_TOML = "workflow.toml"


def _toml_path(root: Path) -> Path:
  return root / SPEC_DRIVER_DIR / _WORKFLOW_TOML


def _legacy_marker_path(root: Path) -> Path:
  return root / SPEC_DRIVER_DIR / _LEGACY_MARKER


def spec_autocreate_enabled(root: Path) -> bool:
  """Check whether spec auto-creation is enabled for this repo.

  Reads from workflow.toml [sync] spec_autocreate.  If that is false/absent,
  checks for the legacy marker file as a backward-compat fallback.
  """
  config = load_workflow_config(root)
  if config.get("sync", {}).get("spec_autocreate", False):
    return True
  return _legacy_marker_path(root).exists()


def persist_spec_autocreate(root: Path) -> None:
  """Persist spec auto-creation preference to workflow.toml.

  Writes [sync] spec_autocreate = true via tomlkit (round-trip preserving).
  If the legacy marker file exists, removes it after successful write.
  """
  toml_path = _toml_path(root)

  if toml_path.exists():
    doc = tomlkit.parse(toml_path.read_text(encoding="utf-8"))
  else:
    doc = tomlkit.document()

  if "sync" not in doc:
    doc.add("sync", tomlkit.table())
  doc["sync"]["spec_autocreate"] = True

  toml_path.parent.mkdir(parents=True, exist_ok=True)
  toml_path.write_text(tomlkit.dumps(doc), encoding="utf-8")

  # Remove legacy marker if present
  marker = _legacy_marker_path(root)
  if marker.exists():
    marker.unlink()
