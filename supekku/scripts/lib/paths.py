"""Central path configuration for spec-driver directories.

This module provides a single source of truth for all spec-driver workspace paths,
making it easy to change directory names or structure without hunting through code.
"""

from __future__ import annotations

from pathlib import Path

from .backlog import find_repo_root

# Directory name - single source of truth
# Changed from "supekku" to ".spec-driver" for cleaner repo root
SPEC_DRIVER_DIR = ".spec-driver"


def get_spec_driver_root(repo_root: Path | None = None) -> Path:
  """Get the spec-driver configuration directory.

  Args:
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Path to the spec-driver directory (e.g., repo_root/supekku)
  """
  root = find_repo_root(repo_root) if repo_root is None else repo_root
  return root / SPEC_DRIVER_DIR


def get_registry_dir(repo_root: Path | None = None) -> Path:
  """Get the registry directory for YAML registry files.

  Args:
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Path to the registry directory (e.g., repo_root/supekku/registry)
  """
  return get_spec_driver_root(repo_root) / "registry"


def get_templates_dir(repo_root: Path | None = None) -> Path:
  """Get the templates directory for spec templates.

  Args:
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Path to the templates directory (e.g., repo_root/supekku/templates)
  """
  return get_spec_driver_root(repo_root) / "templates"


def get_about_dir(repo_root: Path | None = None) -> Path:
  """Get the about directory for documentation.

  Args:
    repo_root: Repository root path. If None, will auto-discover.

  Returns:
    Path to the about directory (e.g., repo_root/supekku/about)
  """
  return get_spec_driver_root(repo_root) / "about"


__all__ = [
  "SPEC_DRIVER_DIR",
  "get_about_dir",
  "get_registry_dir",
  "get_spec_driver_root",
  "get_templates_dir",
]
