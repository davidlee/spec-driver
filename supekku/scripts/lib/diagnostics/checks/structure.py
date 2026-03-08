"""Workspace directory structure checks."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.paths import (
  get_backlog_dir,
  get_decisions_dir,
  get_deltas_dir,
  get_memory_dir,
  get_registry_dir,
  get_spec_driver_root,
  get_tech_specs_dir,
  get_templates_dir,
)
from supekku.scripts.lib.diagnostics.models import DiagnosticResult

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.workspace import Workspace

CATEGORY = "structure"

# (label, path-getter) for required subdirectories
_REQUIRED_DIRS: list[tuple[str, Callable[..., Path]]] = [
  ("specs/tech", get_tech_specs_dir),
  ("deltas", get_deltas_dir),
  ("decisions", get_decisions_dir),
  ("backlog", get_backlog_dir),
  ("memory", get_memory_dir),
  ("registry", get_registry_dir),
  ("templates", get_templates_dir),
]


def check_structure(ws: Workspace) -> list[DiagnosticResult]:
  """Check workspace directory structure for expected directories and orphans."""
  results: list[DiagnosticResult] = []
  root = ws.root
  sd_root = get_spec_driver_root(root)

  if not sd_root.is_dir():
    results.append(
      DiagnosticResult(
        category=CATEGORY,
        name="spec-driver-root",
        status="fail",
        message=".spec-driver/ directory not found",
        suggestion="Run: spec-driver workspace install",
      )
    )
    return results

  results.append(
    DiagnosticResult(
      category=CATEGORY,
      name="spec-driver-root",
      status="pass",
      message=".spec-driver/ exists",
    )
  )

  for label, getter in _REQUIRED_DIRS:
    dir_path = getter(root)
    if dir_path.is_dir():
      results.append(
        DiagnosticResult(
          category=CATEGORY, name=label, status="pass", message=f"{label}/ exists"
        )
      )
    else:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=label,
          status="warn",
          message=f"{label}/ directory missing",
          suggestion="Run: spec-driver workspace install",
        )
      )

  results.extend(_check_orphaned_bundles(get_deltas_dir(root), "delta"))
  return results


def _check_orphaned_bundles(
  parent_dir: Path, artifact_type: str
) -> list[DiagnosticResult]:
  """Find bundle directories that lack a primary markdown file."""
  results: list[DiagnosticResult] = []
  if not parent_dir.is_dir():
    return results

  for entry in sorted(parent_dir.iterdir()):
    if not entry.is_dir():
      continue
    md_files = list(entry.glob("*.md"))
    has_primary = any(
      f.stem.split("-")[0] in ("DE", "RE", "AUD", "DR", "IP") for f in md_files
    )
    if not has_primary and md_files:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=f"orphan-{entry.name}",
          status="warn",
          message=f"Possible orphaned {artifact_type} bundle: {entry.name}",
        )
      )
    elif not md_files:
      results.append(
        DiagnosticResult(
          category=CATEGORY,
          name=f"orphan-{entry.name}",
          status="warn",
          message=f"Empty {artifact_type} bundle directory: {entry.name}",
        )
      )

  return results
