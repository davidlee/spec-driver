"""Central path configuration for spec-driver directories.

This module provides a single source of truth for all spec-driver workspace paths,
making it easy to change directory names or structure without hunting through code.
"""

from __future__ import annotations

from pathlib import Path

from .repo import find_repo_root

# --- spec-driver internal directory ---

SPEC_DRIVER_DIR = ".spec-driver"

# --- Workspace root directories ---

SPECS_DIR = "specify"
CHANGES_DIR = "change"
BACKLOG_DIR = "backlog"
MEMORY_DIR = "memory"

# --- Subdirectories within SPECS_DIR ---

TECH_SPECS_SUBDIR = "tech"
PRODUCT_SPECS_SUBDIR = "product"
DECISIONS_SUBDIR = "decisions"
POLICIES_SUBDIR = "policies"
STANDARDS_SUBDIR = "standards"

# --- Subdirectories within CHANGES_DIR ---

DELTAS_SUBDIR = "deltas"
REVISIONS_SUBDIR = "revisions"
AUDITS_SUBDIR = "audits"

# --- Subdirectories within BACKLOG_DIR ---

ISSUES_SUBDIR = "issues"
PROBLEMS_SUBDIR = "problems"
IMPROVEMENTS_SUBDIR = "improvements"
RISKS_SUBDIR = "risks"

# --- Config key → module constant name mapping ---

_CONFIG_KEY_TO_CONSTANT: dict[str, str] = {
  "specs": "SPECS_DIR",
  "changes": "CHANGES_DIR",
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
  """
  dirs = config.get("dirs", {})
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


# --- Workspace directory helpers: specify/ ---


def get_specs_dir(repo_root: Path | None = None) -> Path:
  """Get the specifications root directory."""
  return _resolve_root(repo_root) / SPECS_DIR


def get_tech_specs_dir(repo_root: Path | None = None) -> Path:
  """Get the technical specifications directory."""
  return get_specs_dir(repo_root) / TECH_SPECS_SUBDIR


def get_product_specs_dir(repo_root: Path | None = None) -> Path:
  """Get the product specifications directory."""
  return get_specs_dir(repo_root) / PRODUCT_SPECS_SUBDIR


def get_decisions_dir(repo_root: Path | None = None) -> Path:
  """Get the architecture decisions directory."""
  return get_specs_dir(repo_root) / DECISIONS_SUBDIR


def get_policies_dir(repo_root: Path | None = None) -> Path:
  """Get the policies directory."""
  return get_specs_dir(repo_root) / POLICIES_SUBDIR


def get_standards_dir(repo_root: Path | None = None) -> Path:
  """Get the standards directory."""
  return get_specs_dir(repo_root) / STANDARDS_SUBDIR


# --- Workspace directory helpers: change/ ---


def get_changes_dir(repo_root: Path | None = None) -> Path:
  """Get the changes root directory."""
  return _resolve_root(repo_root) / CHANGES_DIR


def get_deltas_dir(repo_root: Path | None = None) -> Path:
  """Get the deltas directory."""
  return get_changes_dir(repo_root) / DELTAS_SUBDIR


def get_revisions_dir(repo_root: Path | None = None) -> Path:
  """Get the revisions directory."""
  return get_changes_dir(repo_root) / REVISIONS_SUBDIR


def get_audits_dir(repo_root: Path | None = None) -> Path:
  """Get the audits directory."""
  return get_changes_dir(repo_root) / AUDITS_SUBDIR


# --- Workspace directory helpers: backlog/ ---


def get_backlog_dir(repo_root: Path | None = None) -> Path:
  """Get the backlog root directory."""
  return _resolve_root(repo_root) / BACKLOG_DIR


# --- Workspace directory helpers: memory/ ---


def get_memory_dir(repo_root: Path | None = None) -> Path:
  """Get the memory directory."""
  return _resolve_root(repo_root) / MEMORY_DIR


__all__ = [
  "AUDITS_SUBDIR",
  "BACKLOG_DIR",
  "CHANGES_DIR",
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
  "SPECS_DIR",
  "SPEC_DRIVER_DIR",
  "STANDARDS_SUBDIR",
  "TECH_SPECS_SUBDIR",
  "get_about_dir",
  "get_agents_dir",
  "get_audits_dir",
  "get_backlog_dir",
  "get_changes_dir",
  "get_decisions_dir",
  "get_deltas_dir",
  "get_memory_dir",
  "get_package_skills_dir",
  "get_policies_dir",
  "get_product_specs_dir",
  "get_registry_dir",
  "get_revisions_dir",
  "get_spec_driver_root",
  "get_specs_dir",
  "get_standards_dir",
  "get_tech_specs_dir",
  "get_templates_dir",
  "init_paths",
  "reset_paths",
]
