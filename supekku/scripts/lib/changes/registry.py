"""Registry management for tracking and organizing change artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import yaml
from rich.console import Console

from supekku.scripts.lib.core.paths import (
  get_audits_dir,
  get_deltas_dir,
  get_registry_dir,
  get_revisions_dir,
)
from supekku.scripts.lib.core.repo import find_repo_root

from .artifacts import ChangeArtifact, load_change_artifact

if TYPE_CHECKING:
  from pathlib import Path

_KIND_TO_DIR_NAME = {
  "delta": "deltas",
  "revision": "revisions",
  "audit": "audits",
}

_KIND_TO_DIR_HELPER = {
  "delta": get_deltas_dir,
  "revision": get_revisions_dir,
  "audit": get_audits_dir,
}

_KIND_TO_PREFIX = {
  "delta": "DE-",
  "revision": "RE-",
  "audit": "AUD-",
}


class ChangeRegistry:
  """Registry for managing change artifacts of specific types."""

  def __init__(self, *, root: Path | None = None, kind: str) -> None:
    if kind not in _KIND_TO_DIR_HELPER:
      msg = f"Unsupported change artifact kind: {kind}"
      raise ValueError(msg)
    self.kind = kind
    self.root = find_repo_root(root)
    self.directory = _KIND_TO_DIR_HELPER[kind](self.root)
    self.output_path = get_registry_dir(self.root) / f"{_KIND_TO_DIR_NAME[kind]}.yaml"

  def collect(self) -> dict[str, ChangeArtifact]:
    """Collect all change artifacts from directory.

    Returns:
      Dictionary mapping artifact IDs to ChangeArtifact objects.
    """
    artifacts: dict[str, ChangeArtifact] = {}
    if not self.directory.exists():
      return artifacts
    prefix = _KIND_TO_PREFIX[self.kind]
    for bundle in self.directory.iterdir():
      if bundle.is_dir():
        candidate_files = sorted(bundle.glob("*.md"))
      elif bundle.is_file() and bundle.suffix == ".md":
        candidate_files = [bundle]
      else:
        continue
      selected: Path | None = None
      for file in candidate_files:
        if file.name.startswith(prefix):
          selected = file
          break
      if selected is None and candidate_files:
        selected = candidate_files[0]
      if not selected:
        continue
      try:
        artifact = load_change_artifact(selected)
      except ValueError as e:
        # Print validation error and continue with remaining artifacts
        console = Console(stderr=True)
        rel_path = selected.relative_to(self.root)
        console.print(f"[yellow]WARNING:[/yellow] Skipping {rel_path}: {e}")
        continue
      if not artifact:
        continue
      artifacts[artifact.id] = artifact
    return artifacts

  def sync(self) -> None:
    """Synchronize registry file with artifacts found in directory."""
    artifacts = self.collect()
    serialised = {
      _KIND_TO_DIR_NAME[self.kind]: {
        artifact_id: artifact.to_dict(self.root)
        for artifact_id, artifact in sorted(artifacts.items())
      },
    }
    self.output_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(serialised, sort_keys=False)
    self.output_path.write_text(text, encoding="utf-8")

  def find_by_implements(self, requirement_id: str | None) -> list[ChangeArtifact]:
    """Find change artifacts that implement a specific requirement.

    Args:
      requirement_id: The requirement ID to search for (e.g., "PROD-010.FR-004").
                      Returns empty list if None or empty string.

    Returns:
      List of ChangeArtifact objects that implement the given requirement.
      Returns empty list if requirement_id is None, empty, or no matches found.
    """
    if not requirement_id:
      return []

    artifacts = self.collect()
    matches: list[ChangeArtifact] = []

    for artifact in artifacts.values():
      # Check applies_to field - it's a dict with 'requirements' and 'specs' keys
      if not artifact.applies_to:
        continue

      requirements = artifact.applies_to.get("requirements", [])
      if requirement_id in requirements:
        matches.append(artifact)

    return matches


@dataclass(frozen=True)
class PlanSummary:
  """Summary of an implementation plan for listing and display."""

  id: str
  status: str
  name: str
  slug: str
  path: Path
  updated: str
  delta_id: str
  phases: list[dict[str, Any]] = field(default_factory=list)


def discover_plans(root: Path) -> list[PlanSummary]:
  """Discover all implementation plans by scanning delta directories.

  Scans ``change/deltas/*/IP-*.md``, parses frontmatter and the
  ``plan.overview`` YAML block, and returns sorted ``PlanSummary`` objects.

  Args:
    root: Repository root path.

  Returns:
    List of PlanSummary objects sorted by ID.
  """
  from supekku.scripts.lib.blocks.plan import extract_plan_overview  # noqa: PLC0415
  from supekku.scripts.lib.core.spec_utils import load_markdown_file  # noqa: PLC0415

  deltas_dir = get_deltas_dir(root)
  if not deltas_dir.exists():
    return []

  plans: list[PlanSummary] = []
  for delta_dir in sorted(deltas_dir.iterdir()):
    if not delta_dir.is_dir():
      continue
    for plan_file in sorted(delta_dir.glob("IP-*.md")):
      try:
        frontmatter, body = load_markdown_file(plan_file)
      except Exception:  # noqa: BLE001
        continue

      plan_id = str(frontmatter.get("id", "")).strip()
      if not plan_id:
        continue

      # Extract delta and phases from plan.overview block
      delta_id = ""
      phase_list: list[dict[str, Any]] = []
      overview = extract_plan_overview(body, source_path=plan_file)
      if overview:
        delta_id = str(overview.data.get("delta", ""))
        phase_list = list(overview.data.get("phases", []))

      plans.append(
        PlanSummary(
          id=plan_id,
          status=str(frontmatter.get("status", "")),
          name=str(frontmatter.get("name", "")),
          slug=str(frontmatter.get("slug", "")),
          path=plan_file,
          updated=str(frontmatter.get("updated", "")),
          delta_id=delta_id,
          phases=phase_list,
        )
      )

  return sorted(plans, key=lambda p: p.id)


__all__ = ["ChangeRegistry", "PlanSummary", "discover_plans"]
