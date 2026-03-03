"""Workflow configuration loading from .spec-driver/workflow.toml."""

from __future__ import annotations

import copy
import tomllib
import warnings
from pathlib import Path

from .paths import SPEC_DRIVER_DIR

DEFAULT_CONFIG: dict = {
  "ceremony": "pioneer",
  "tool": {
    "exec": "uv run spec-driver",
  },
  "verification": {
    "command": "just check",
  },
  "cards": {
    "enabled": True,
    "root": "kanban",
    "lanes": ["backlog", "next", "doing", "finishing", "done"],
    "id_prefix": "T",
  },
  "docs": {
    "artefacts_root": "doc/artefacts",
    "plans_root": "doc/plans",
  },
  "policy": {
    "adrs": True,
    "policies": False,
    "standards": False,
  },
  "contracts": {
    "enabled": True,
    "root": ".contracts",
  },
  "bootstrap": {
    "doctrine_path": ".spec-driver/doctrine.md",
  },
  "authoring": {
    "engine": "superpowers",
  },
  "skills": {
    "targets": ["claude", "codex"],
  },
  "integration": {
    "agents_md": True,
    "claude_md": False,
  },
}


def load_workflow_config(repo_root: Path) -> dict:
  """Load workflow configuration from .spec-driver/workflow.toml.

  Reads the TOML file and deep-merges with defaults so that missing
  sections and keys are always present.

  Args:
    repo_root: Repository root path.

  Returns:
    Configuration dict with all sections populated.
    On missing file or invalid TOML, returns defaults.
  """
  toml_path = repo_root / SPEC_DRIVER_DIR / "workflow.toml"

  if not toml_path.exists():
    return copy.deepcopy(DEFAULT_CONFIG)

  try:
    raw = toml_path.read_bytes()
    user_config = tomllib.loads(raw.decode("utf-8"))
  except tomllib.TOMLDecodeError:
    warnings.warn(
      f"Invalid TOML in {toml_path}; using defaults.",
      UserWarning,
      stacklevel=2,
    )
    return copy.deepcopy(DEFAULT_CONFIG)

  return _merge_defaults(user_config)


def _merge_defaults(user_config: dict) -> dict:
  """Deep-merge user config over DEFAULT_CONFIG.

  Top-level scalars are replaced; nested dicts are merged key-by-key
  (one level deep — matches the flat-section TOML schema).
  """
  result = copy.deepcopy(DEFAULT_CONFIG)

  for key, default_val in DEFAULT_CONFIG.items():
    if key not in user_config:
      continue
    if isinstance(default_val, dict):
      result[key] = {**default_val, **user_config[key]}
    else:
      result[key] = user_config[key]

  return result


__all__ = [
  "DEFAULT_CONFIG",
  "load_workflow_config",
]
