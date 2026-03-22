"""Shared utilities for change artifact creation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from supekku.scripts.lib.core.paths import get_templates_dir


def _get_template_path(name: str, repo_root: Path | None = None) -> Path:
  """Get path to template file in user's .spec-driver/templates directory."""
  return get_templates_dir(repo_root) / name


@dataclass(frozen=True)
class ChangeArtifactCreated:
  """Result information from creating a change artifact."""

  artifact_id: str
  directory: Path
  primary_path: Path
  extras: list[Path]


def _next_identifier(base_dir: Path, prefix: str) -> str:
  highest = 0
  if base_dir.exists():
    for entry in base_dir.iterdir():
      match = re.search(rf"{prefix}-(\d{{3,}})", entry.name)
      if match:
        try:
          highest = max(highest, int(match.group(1)))
        except ValueError:
          continue
  return f"{prefix}-{highest + 1:03d}"


def _ensure_directory(path: Path) -> None:
  path.mkdir(parents=True, exist_ok=True)
