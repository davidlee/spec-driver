"""Registry management for tracking and organizing change artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from .backlog import find_repo_root
from .change_artifacts import ChangeArtifact, load_change_artifact
from .paths import get_registry_dir

if TYPE_CHECKING:
  from pathlib import Path

_KIND_TO_DIR = {
  "delta": "deltas",
  "revision": "revisions",
  "audit": "audits",
}

_KIND_TO_PREFIX = {
  "delta": "DE-",
  "revision": "RE-",
  "audit": "AUD-",
}


class ChangeRegistry:
  """Registry for managing change artifacts of specific types."""

  def __init__(self, *, root: Path | None = None, kind: str) -> None:
    if kind not in _KIND_TO_DIR:
      msg = f"Unsupported change artifact kind: {kind}"
      raise ValueError(msg)
    self.kind = kind
    self.root = find_repo_root(root)
    self.directory = self.root / "change" / _KIND_TO_DIR[kind]
    self.output_path = get_registry_dir(self.root) / f"{_KIND_TO_DIR[kind]}.yaml"

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
      except ValueError:
        # Print validation error and continue with remaining artifacts
        continue
      if not artifact:
        continue
      artifacts[artifact.id] = artifact
    return artifacts

  def sync(self) -> None:
    """Synchronize registry file with artifacts found in directory."""
    artifacts = self.collect()
    serialised = {
      _KIND_TO_DIR[self.kind]: {
        artifact_id: artifact.to_dict(self.root)
        for artifact_id, artifact in sorted(artifacts.items())
      },
    }
    self.output_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(serialised, sort_keys=False)
    self.output_path.write_text(text, encoding="utf-8")


__all__ = ["ChangeRegistry"]
