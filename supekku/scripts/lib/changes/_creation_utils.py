"""Shared utilities for change artifact creation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from supekku.scripts.lib.core.ids import next_sequential_id
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
  names = [e.name for e in base_dir.iterdir()] if base_dir.exists() else []
  return next_sequential_id(names, prefix)


def _ensure_directory(path: Path) -> None:
  path.mkdir(parents=True, exist_ok=True)
