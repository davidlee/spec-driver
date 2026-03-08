"""Configuration validity checks.

Validates workflow.toml, CLAUDE.md, skills allowlist, and agent
skill exposure.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.paths import (
  get_spec_driver_root,
)
from supekku.scripts.lib.diagnostics.models import DiagnosticResult

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace

CATEGORY = "config"


def check_config(ws: Workspace) -> list[DiagnosticResult]:
  """Check configuration files and skills exposure."""
  results: list[DiagnosticResult] = []
  root = ws.root
  sd_root = get_spec_driver_root(root)

  results.append(_check_workflow_toml(sd_root))
  results.append(_check_version_staleness(sd_root))
  results.append(_check_claude_md(root))
  results.append(_check_skills_allowlist(sd_root))
  results.append(_check_agents_dir(sd_root))
  results.extend(_check_skills_exposure(root, sd_root))

  return results


def _check_version_staleness(sd_root: Path) -> DiagnosticResult:
  """Warn when workflow.toml version stamp differs from the running package."""
  from supekku.scripts.lib.core.version import get_package_version  # noqa: PLC0415

  wf = sd_root / "workflow.toml"
  if not wf.is_file():
    return DiagnosticResult(
      category=CATEGORY,
      name="version-staleness",
      status="warn",
      message="workflow.toml missing — cannot check version",
      suggestion="Run: spec-driver install",
    )

  try:
    with wf.open("rb") as f:
      data = tomllib.load(f)
  except (tomllib.TOMLDecodeError, OSError):
    return DiagnosticResult(
      category=CATEGORY,
      name="version-staleness",
      status="warn",
      message="workflow.toml unreadable — cannot check version",
    )

  installed = data.get("spec_driver_installed_version")
  current = get_package_version()

  if installed is None:
    return DiagnosticResult(
      category=CATEGORY,
      name="version-staleness",
      status="warn",
      message="no version stamp in workflow.toml",
      suggestion="Run: spec-driver install",
    )

  if installed != current:
    return DiagnosticResult(
      category=CATEGORY,
      name="version-staleness",
      status="warn",
      message=f"installed {installed}, running {current}",
      suggestion="Run: spec-driver install",
    )

  return DiagnosticResult(
    category=CATEGORY,
    name="version-staleness",
    status="pass",
    message=f"version {current} matches workflow.toml",
  )


def _check_workflow_toml(sd_root: Path) -> DiagnosticResult:
  wf = sd_root / "workflow.toml"
  if not wf.is_file():
    return DiagnosticResult(
      category=CATEGORY,
      name="workflow.toml",
      status="warn",
      message="workflow.toml not found",
      suggestion="Run: spec-driver workspace install",
    )
  try:
    with wf.open("rb") as f:
      tomllib.load(f)
    return DiagnosticResult(
      category=CATEGORY,
      name="workflow.toml",
      status="pass",
      message="workflow.toml valid",
    )
  except (tomllib.TOMLDecodeError, OSError) as exc:
    return DiagnosticResult(
      category=CATEGORY,
      name="workflow.toml",
      status="fail",
      message=f"workflow.toml parse error: {exc}",
    )


def _check_claude_md(root: Path) -> DiagnosticResult:
  if (root / "CLAUDE.md").is_file():
    return DiagnosticResult(
      category=CATEGORY,
      name="CLAUDE.md",
      status="pass",
      message="CLAUDE.md present",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name="CLAUDE.md",
    status="warn",
    message="CLAUDE.md not found at repo root",
    suggestion="Create CLAUDE.md with @.spec-driver/AGENTS.md",
  )


def _check_skills_allowlist(sd_root: Path) -> DiagnosticResult:
  allowlist = sd_root / "skills.allowlist"
  if not allowlist.is_file():
    return DiagnosticResult(
      category=CATEGORY,
      name="skills-allowlist",
      status="warn",
      message="skills.allowlist not found",
      suggestion="Run: spec-driver skills sync",
    )
  lines = [
    ln.strip()
    for ln in allowlist.read_text().splitlines()
    if ln.strip() and not ln.strip().startswith("#")
  ]
  if not lines:
    return DiagnosticResult(
      category=CATEGORY,
      name="skills-allowlist",
      status="warn",
      message="skills.allowlist is empty",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name="skills-allowlist",
    status="pass",
    message=f"{len(lines)} skills in allowlist",
  )


def _check_agents_dir(sd_root: Path) -> DiagnosticResult:
  agents = sd_root / "agents"
  if agents.is_dir():
    return DiagnosticResult(
      category=CATEGORY,
      name="agents-dir",
      status="pass",
      message="agents/ directory present",
    )
  return DiagnosticResult(
    category=CATEGORY,
    name="agents-dir",
    status="warn",
    message="agents/ directory missing",
    suggestion="Run: spec-driver workspace install",
  )


def _check_skills_exposure(root: Path, sd_root: Path) -> list[DiagnosticResult]:
  """Check skill symlinks for each agent target."""
  results: list[DiagnosticResult] = []
  canonical = sd_root / "skills"
  if not canonical.is_dir():
    results.append(
      DiagnosticResult(
        category=CATEGORY,
        name="skills-canonical",
        status="warn",
        message="canonical skills dir missing",
        suggestion="Run: spec-driver skills sync",
      )
    )
    return results

  # Installed skill names from canonical dir
  installed = sorted(
    d.name for d in canonical.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()
  )

  results.append(
    DiagnosticResult(
      category=CATEGORY,
      name="skills-installed",
      status="pass",
      message=f"{len(installed)} skills installed",
    )
  )

  # Check each agent target
  target_dirs = {
    "claude": root / ".claude" / "skills",
    "codex": root / ".agents" / "skills",
  }
  for target, target_dir in target_dirs.items():
    if not target_dir.is_dir():
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=f"skills-{target}",
          status="warn",
          message=f"{target} skills dir missing",
          suggestion="Run: spec-driver skills sync",
        )
      )
      continue

    exposed = sorted(
      d.name for d in target_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()
    )
    skipped = sorted(set(installed) - set(exposed))

    if skipped:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=f"skills-{target}",
          status="warn",
          message=(
            f"{len(exposed)} exposed, {len(skipped)} skipped: {', '.join(skipped)}"
          ),
          suggestion="Run: spec-driver skills sync",
        )
      )
    else:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=f"skills-{target}",
          status="pass",
          message=f"{len(exposed)} skills exposed to {target}",
        )
      )

  return results
