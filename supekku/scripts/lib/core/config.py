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
  "ceremony": "town_planner",
  "strict_mode": False,
  "tool": {
    "exec": "uv run spec-driver",
  },
  "verification": {
    "command": "just check",
  },
  "kanban": {
    "enabled": False,
    "root": "kanban",
    "lanes": ["backlog", "next", "doing", "finishing", "done"],
    "id_prefix": "T",
    "artefacts_root": "docs/artefacts",
    "plans_root": "docs/plans",
  },
  "policy": {
    "adrs": True,
    "policies": True,
    "standards": True,
  },
  "events": {
    "enabled": True,
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
  "skills": {
    "targets": ["claude", "codex"],
  },
  "integration": {
    "agents_md": True,
    "claude_md": True,
  },
  "workflow": {
    "state_dir": "workflow",
    "handoff_boundary": "phase",
    "auto_handoff_on_phase_complete": True,
    "render_continuation_prompt": True,
    "update_notes_new_agent_instructions": True,
    "default_next_role": "implementer",
  },
  "review": {
    "persistent_session": True,
    "bootstrap_cache": True,
    "session_scope": "artifact",
    "teardown_on": ["approved", "abandoned"],
    "recreate_on": ["major_scope_change", "cache_invalid", "session_unrecoverable"],
    "bootstrap": {
      "include_delta": True,
      "include_plan": True,
      "include_active_phase": True,
      "include_notes": True,
      "include_findings": True,
      "include_changed_files": True,
      "max_historical_rounds": 2,
    },
  },
  "dirs": {
    "backlog": "backlog",
    "memory": "memory",
    "tech_specs": "tech",
    "product_specs": "product",
    "decisions": "decisions",
    "policies": "policies",
    "standards": "standards",
    "deltas": "deltas",
    "revisions": "revisions",
    "audits": "audits",
    "issues": "issues",
    "problems": "problems",
    "improvements": "improvements",
    "risks": "risks",
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


def _migrate_legacy_keys(user_config: dict) -> dict:
  """Promote legacy [cards]/[docs] keys to [kanban].

  Existing installs may have ``[cards]`` and/or ``[docs]`` sections.
  Merge them into ``kanban`` so downstream code sees a single key.
  """
  config = dict(user_config)

  if "cards" in config:
    kanban = config.pop("cards")
    existing = config.get("kanban", {})
    config["kanban"] = {**kanban, **existing}

  if "docs" in config:
    docs = config.pop("docs")
    existing = config.get("kanban", {})
    config["kanban"] = {**existing, **docs}

  return config


def _merge_defaults(user_config: dict) -> dict:
  """Deep-merge user config over DEFAULT_CONFIG.

  Top-level scalars are replaced; nested dicts are merged key-by-key
  (one level deep — matches the flat-section TOML schema).

  Legacy ``[cards]`` and ``[docs]`` sections are migrated to ``[kanban]``
  before merging.
  """
  migrated = _migrate_legacy_keys(user_config)
  result = copy.deepcopy(DEFAULT_CONFIG)

  for key, default_val in DEFAULT_CONFIG.items():
    if key not in migrated:
      continue
    if isinstance(default_val, dict):
      result[key] = {**default_val, **migrated[key]}
    else:
      result[key] = migrated[key]

  # Preserve user keys not in defaults (e.g. spec_driver_installed_version)
  for key, val in migrated.items():
    if key not in DEFAULT_CONFIG:
      result[key] = val

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


# ---------------------------------------------------------------------------
# Default workflow.toml template generation
# ---------------------------------------------------------------------------

# Section header comments for the generated template.
# Each entry maps a DEFAULT_CONFIG key to a human-readable explanation.
_SECTION_COMMENTS: dict[str, list[str]] = {
  "_preamble": [
    "spec-driver workflow configuration",
    "",
    "All options below show their defaults.  Uncomment and change any",
    "value to override.  Missing keys always fall back to built-in defaults,",
    "so you only need to include what you want to change.",
    "",
    "Ceremony mode controls governance posture: how much structure agents",
    'apply.  Options: "pioneer" (lightweight), "settler" (moderate),',
    '"town_planner" (full governance).',
  ],
  "strict_mode": [
    "When true, delta completion enforces all coverage gates.",
    "When false (default), agents may use --force to bypass.",
  ],
  "tool": [
    "How to invoke spec-driver.  Detected automatically at install time.",
  ],
  "verification": [
    "Command agents run to verify the project (tests + lint).",
  ],
  "kanban": [
    "Kanban-style task cards for lightweight work tracking.",
    "Disable with enabled = false if you only use deltas.",
    "artefacts_root / plans_root: where design docs and plans live.",
  ],
  "policy": [
    "Toggle governance layers.  ADRs are always recommended.",
    "Enable policies and standards for stricter governance.",
  ],
  "events": [
    "Event logging for spec-driver operations (powers TUI track mode).",
  ],
  "sync": [
    "Controls for the sync subsystem.",
    "spec_autocreate: automatically create unit specs during sync.",
  ],
  "contracts": [
    "Generated API contracts corpus.",
    "root: directory under the repo root (always derived/regenerable).",
  ],
  "bootstrap": [
    "Path to the project doctrine file loaded by agents at boot.",
  ],
  "skills": [
    "Agent skill sync targets.  Each entry is a directory name under",
    "the agent config root (e.g. .claude/, .codex/).",
  ],
  "integration": [
    "Controls @-references injected into root agent config files.",
    "Disable if you manage AGENTS.md / CLAUDE.md yourself.",
  ],
  "workflow": [
    "Workflow orchestration settings (DR-102).",
    "state_dir: subdirectory within delta bundle for workflow YAML files.",
    "handoff_boundary: default trigger boundary (phase | task | manual).",
    "auto_handoff_on_phase_complete: emit handoff when phase completes.",
    "default_next_role: role to hand off to when not otherwise specified.",
  ],
  "review": [
    "Review session and bootstrap cache settings (DR-102 §8/§9).",
    "session_scope: artifact | phase — controls teardown granularity.",
    "bootstrap: controls what is included in reviewer bootstrap cache.",
  ],
  "dirs": [
    "Directory name overrides for spec-driver workspace subdirectories.",
    "All paths are relative to .spec-driver/.  Change these if your",
    "project uses non-standard directory names.",
  ],
}


def _toml_value(val: object) -> str:
  """Format a Python value as a TOML literal."""
  if isinstance(val, bool):
    return "true" if val else "false"
  if isinstance(val, str):
    return f'"{val}"'
  if isinstance(val, int):
    return str(val)
  if isinstance(val, list):
    items = ", ".join(_toml_value(v) for v in val)
    return f"[{items}]"
  return repr(val)  # pragma: no cover


def _prose(text: str) -> str:
  """Format a prose comment (## prefix, not uncommentable)."""
  return f"## {text}" if text else "##"


def _emit_prose(lines: list[str], key: str) -> None:
  """Append prose comments for *key* from ``_SECTION_COMMENTS``."""
  for comment in _SECTION_COMMENTS.get(key, ()):
    lines.append(_prose(comment))


def _emit_section(lines: list[str], key: str, section: dict) -> None:
  """Append a commented-out TOML section."""
  lines.append(f"# [{key}]")
  deferred_subtables: list[tuple[str, dict]] = []
  for sub_key, sub_val in section.items():
    if isinstance(sub_val, dict):
      deferred_subtables.append((sub_key, sub_val))
    else:
      lines.append(f"# {sub_key} = {_toml_value(sub_val)}")
  for sub_key, sub_val in deferred_subtables:
    lines.append(f"# [{key}.{sub_key}]")
    for inner_key, inner_val in sub_val.items():
      lines.append(f"# {inner_key} = {_toml_value(inner_val)}")


def generate_default_workflow_toml(exec_cmd: str = "uv run spec-driver") -> str:
  """Render DEFAULT_CONFIG as a richly-commented TOML template.

  Every option is commented out except ``[tool] exec`` which is set to the
  detected *exec_cmd* value.  Section headers include explanatory comments
  describing purpose and allowed values.

  Args:
    exec_cmd: The detected invocation command for spec-driver.

  Returns:
    A string suitable for writing to ``.spec-driver/workflow.toml``.
  """
  lines: list[str] = []

  # Preamble
  _emit_prose(lines, "_preamble")
  lines.append("")

  for key, default_val in DEFAULT_CONFIG.items():
    if isinstance(default_val, dict):
      _emit_prose(lines, key)
      if key == "tool":
        # [tool] is uncommented — exec is install-specific
        lines.append(f"[{key}]")
        lines.append(f'exec = "{exec_cmd}"')
      else:
        _emit_section(lines, key, default_val)
    else:
      _emit_prose(lines, key)
      lines.append(f"# {key} = {_toml_value(default_val)}")
    lines.append("")

  return "\n".join(lines)


__all__ = [
  "DEFAULT_CONFIG",
  "detect_exec_command",
  "generate_default_workflow_toml",
  "is_strict_mode",
  "load_workflow_config",
]
