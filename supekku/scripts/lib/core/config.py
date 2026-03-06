"""Workflow configuration loading from .spec-driver/workflow.toml."""

from __future__ import annotations

import copy
import sys
import tomllib
import warnings
from pathlib import Path
from shutil import which

from .paths import SPEC_DRIVER_DIR

# Markers indicating a transient (non-permanent) install location
_TRANSIENT_PATH_MARKERS = (".venv", ".cache/uv")

DEFAULT_CONFIG: dict = {
  "ceremony": "pioneer",
  "strict_mode": False,
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
  "sync": {
    "spec_autocreate": False,
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
    "claude_md": True,
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


def is_strict_mode(config: dict) -> bool:
  """Return whether strict mode is enabled in the given config."""
  return config.get("strict_mode", False) is True


def _dep_list_mentions(deps: list, name: str = "spec-driver") -> bool:
  """Check if any entry in a dependency list mentions the given package."""
  return any(isinstance(d, str) and name in d for d in deps)


def _is_project_dependency(target_root: Path) -> bool:
  """Check if spec-driver is available as a project dependency.

  Signals checked (strongest first):
    1. .venv/bin/spec-driver exists — already installed locally
    2. pyproject.toml lists it in dependencies or dependency-groups
    3. pyproject.toml [tool.uv.dev-dependencies]
    4. uv.toml dev-dependencies
  """
  # Strongest signal: binary in project venv
  if (target_root / ".venv" / "bin" / "spec-driver").is_file():
    return True

  # Check pyproject.toml
  pyproject = target_root / "pyproject.toml"
  if pyproject.exists():
    try:
      data = tomllib.loads(pyproject.read_bytes().decode("utf-8"))
    except tomllib.TOMLDecodeError:
      data = {}

    # [project.dependencies]
    if _dep_list_mentions(data.get("project", {}).get("dependencies", [])):
      return True
    # [dependency-groups] (PEP 735)
    for group_deps in data.get("dependency-groups", {}).values():
      if isinstance(group_deps, list) and _dep_list_mentions(group_deps):
        return True
    # [tool.uv.dev-dependencies]
    uv_dev = data.get("tool", {}).get("uv", {}).get("dev-dependencies", [])
    if _dep_list_mentions(uv_dev):
      return True

  # Check uv.toml (mirrors [tool.uv] from pyproject.toml)
  uv_toml = target_root / "uv.toml"
  if uv_toml.exists():
    try:
      data = tomllib.loads(uv_toml.read_bytes().decode("utf-8"))
    except tomllib.TOMLDecodeError:
      data = {}
    if _dep_list_mentions(data.get("dev-dependencies", [])):
      return True

  return False


def _is_global_install() -> bool:
  """Check if the running spec-driver binary is a permanent global install.

  Inspects sys.argv[0] to determine whether the binary lives in a
  stable location (nix store, ~/.local/bin, /usr/local/bin, etc.)
  or a transient one (.venv, uv cache).
  """
  try:
    exe = str(Path(sys.argv[0]).resolve())
  except (OSError, ValueError):
    return False
  return not any(marker in exe for marker in _TRANSIENT_PATH_MARKERS)


def detect_exec_command(target_root: Path) -> str:
  """Detect the appropriate invocation command for spec-driver.

  Priority:
    1. Project dependency + uv available → 'uv run spec-driver'
    2. Binary in a permanent PATH location → 'spec-driver'
    3. uvx/uv available → 'uvx spec-driver'
    4. Fallback → 'spec-driver'
  """
  if _is_project_dependency(target_root) and which("uv"):
    return "uv run spec-driver"
  if _is_global_install():
    return "spec-driver"
  if which("uvx") or which("uv"):
    return "uvx spec-driver"
  return "spec-driver"


__all__ = [
  "DEFAULT_CONFIG",
  "detect_exec_command",
  "is_strict_mode",
  "load_workflow_config",
]
