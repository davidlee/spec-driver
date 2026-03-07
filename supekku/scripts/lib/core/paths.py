"""Central path configuration for spec-driver directories.

This module provides a single source of truth for all spec-driver workspace paths,
making it easy to change directory names or structure without hunting through code.

All content directories resolve as direct children of .spec-driver/ (DE-049).
"""

from __future__ import annotations

import warnings
from pathlib import Path

from .repo import find_repo_root

# --- spec-driver internal directory ---

SPEC_DRIVER_DIR = ".spec-driver"

# --- Content subdirectories (direct children of .spec-driver/) ---

TECH_SPECS_SUBDIR = "tech"
PRODUCT_SPECS_SUBDIR = "product"
DECISIONS_SUBDIR = "decisions"
POLICIES_SUBDIR = "policies"
STANDARDS_SUBDIR = "standards"

DELTAS_SUBDIR = "deltas"
REVISIONS_SUBDIR = "revisions"
AUDITS_SUBDIR = "audits"

BACKLOG_DIR = "backlog"
MEMORY_DIR = "memory"

# --- Subdirectories within backlog/ ---

ISSUES_SUBDIR = "issues"
PROBLEMS_SUBDIR = "problems"
IMPROVEMENTS_SUBDIR = "improvements"
RISKS_SUBDIR = "risks"

# --- Config key → module constant name mapping ---

_CONFIG_KEY_TO_CONSTANT: dict[str, str] = {
  "backlog": "BACKLOG_DIR",
  "memory": "MEMORY_DIR",
  "tech_specs": "TECH_SPECS_SUBDIR",
  "product_specs": "PRODUCT_SPECS_SUBDIR",
  "decisions": "DECISIONS_SUBDIR",
  "policies": "POLICIES_SUBDIR",
  "standards": "STANDARDS_SUBDIR",
  "deltas": "DELTAS_SUBDIR",
  "revisions": "REVISIONS_SUBDIR",
  "audits": "AUDITS_SUBDIR",
  "issues": "ISSUES_SUBDIR",
  "problems": "PROBLEMS_SUBDIR",
  "improvements": "IMPROVEMENTS_SUBDIR",
  "risks": "RISKS_SUBDIR",
}

# Snapshot of original defaults for reset_paths()
_ORIGINAL_DEFAULTS: dict[str, str] = {
  const: globals()[const] for const in _CONFIG_KEY_TO_CONSTANT.values()
}


def init_paths(config: dict) -> None:
  """Override module-level directory constants from config["dirs"].

  Safe to skip — helpers fall back to compiled defaults when not called.
  Warns on unrecognized keys (catches removed keys, typos, reparenting surprises).
  """
  dirs = config.get("dirs", {})
  for key in dirs:
    if key not in _CONFIG_KEY_TO_CONSTANT:
      warnings.warn(
        f"Unknown [dirs] key '{key}' in config — ignored",
        UserWarning,
        stacklevel=2,
      )
  for config_key, const_name in _CONFIG_KEY_TO_CONSTANT.items():
    if config_key in dirs:
      globals()[const_name] = dirs[config_key]


def reset_paths() -> None:
  """Restore all directory constants to their original compiled defaults."""
  for const_name, default_val in _ORIGINAL_DEFAULTS.items():
    globals()[const_name] = default_val


# --- spec-driver internal helpers ---


def _resolve_root(repo_root: Path | None) -> Path:
  return find_repo_root(repo_root) if repo_root is None else repo_root


def get_spec_driver_root(repo_root: Path | None = None) -> Path:
  """Get the spec-driver configuration directory."""
  return _resolve_root(repo_root) / SPEC_DRIVER_DIR


def get_registry_dir(repo_root: Path | None = None) -> Path:
  """Get the registry directory for YAML registry files."""
  return get_spec_driver_root(repo_root) / "registry"


def get_templates_dir(repo_root: Path | None = None) -> Path:
  """Get the templates directory for spec templates."""
  return get_spec_driver_root(repo_root) / "templates"


def get_about_dir(repo_root: Path | None = None) -> Path:
  """Get the about directory for documentation."""
  return get_spec_driver_root(repo_root) / "about"


def get_agents_dir(repo_root: Path | None = None) -> Path:
  """Get the agents directory for generated agent guidance."""
  return get_spec_driver_root(repo_root) / "agents"


def get_package_skills_dir() -> Path:
  """Get the bundled skills directory within the supekku package."""
  import supekku  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

  return Path(supekku.__file__).parent / "skills"


# --- Workspace content directory helpers ---
# All resolve as direct children of .spec-driver/ (DE-049, DEC-049-02).


def get_tech_specs_dir(repo_root: Path | None = None) -> Path:
  """Get the technical specifications directory."""
  return get_spec_driver_root(repo_root) / TECH_SPECS_SUBDIR


def get_product_specs_dir(repo_root: Path | None = None) -> Path:
  """Get the product specifications directory."""
  return get_spec_driver_root(repo_root) / PRODUCT_SPECS_SUBDIR


def get_decisions_dir(repo_root: Path | None = None) -> Path:
  """Get the architecture decisions directory."""
  return get_spec_driver_root(repo_root) / DECISIONS_SUBDIR


def get_policies_dir(repo_root: Path | None = None) -> Path:
  """Get the policies directory."""
  return get_spec_driver_root(repo_root) / POLICIES_SUBDIR


def get_standards_dir(repo_root: Path | None = None) -> Path:
  """Get the standards directory."""
  return get_spec_driver_root(repo_root) / STANDARDS_SUBDIR


def get_deltas_dir(repo_root: Path | None = None) -> Path:
  """Get the deltas directory."""
  return get_spec_driver_root(repo_root) / DELTAS_SUBDIR


def get_revisions_dir(repo_root: Path | None = None) -> Path:
  """Get the revisions directory."""
  return get_spec_driver_root(repo_root) / REVISIONS_SUBDIR


def get_audits_dir(repo_root: Path | None = None) -> Path:
  """Get the audits directory."""
  return get_spec_driver_root(repo_root) / AUDITS_SUBDIR


def get_backlog_dir(repo_root: Path | None = None) -> Path:
  """Get the backlog directory."""
  return get_spec_driver_root(repo_root) / BACKLOG_DIR


def get_memory_dir(repo_root: Path | None = None) -> Path:
  """Get the memory directory."""
  return get_spec_driver_root(repo_root) / MEMORY_DIR


def get_run_dir(repo_root: Path | None = None) -> Path:
  """Get the runtime state directory (.spec-driver/run/)."""
  return get_spec_driver_root(repo_root) / "run"


__all__ = [
  "AUDITS_SUBDIR",
  "BACKLOG_DIR",
  "DECISIONS_SUBDIR",
  "DELTAS_SUBDIR",
  "IMPROVEMENTS_SUBDIR",
  "ISSUES_SUBDIR",
  "MEMORY_DIR",
  "POLICIES_SUBDIR",
  "PROBLEMS_SUBDIR",
  "PRODUCT_SPECS_SUBDIR",
  "REVISIONS_SUBDIR",
  "RISKS_SUBDIR",
  "SPEC_DRIVER_DIR",
  "STANDARDS_SUBDIR",
  "TECH_SPECS_SUBDIR",
  "get_about_dir",
  "get_agents_dir",
  "get_audits_dir",
  "get_backlog_dir",
  "get_decisions_dir",
  "get_deltas_dir",
  "get_memory_dir",
  "get_package_skills_dir",
  "get_policies_dir",
  "get_product_specs_dir",
  "get_registry_dir",
  "get_run_dir",
  "get_revisions_dir",
  "get_spec_driver_root",
  "get_standards_dir",
  "get_tech_specs_dir",
  "get_templates_dir",
  "init_paths",
  "reset_paths",
]
