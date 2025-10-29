"""Registry management for tracking and organizing change artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from .backlog import find_repo_root
from .change_artifacts import ChangeArtifact, load_change_artifact

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
            raise ValueError(f"Unsupported change artifact kind: {kind}")
        self.kind = kind
        self.root = find_repo_root(root)
        self.directory = self.root / "change" / _KIND_TO_DIR[kind]
        self.output_path = (
            self.root / "supekku" / "registry" / f"{_KIND_TO_DIR[kind]}.yaml"
        )

    def collect(self) -> dict[str, ChangeArtifact]:
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
            except ValueError as exc:
                # Print validation error and continue with remaining artifacts
                print(f"Error loading {selected}: {exc}", file=sys.stderr)
                continue
            if not artifact:
                continue
            artifacts[artifact.id] = artifact
        return artifacts

    def sync(self) -> None:
        artifacts = self.collect()
        serialised = {
            _KIND_TO_DIR[self.kind]: {
                artifact_id: artifact.to_dict(self.root)
                for artifact_id, artifact in sorted(artifacts.items())
            }
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(serialised, sort_keys=False)
        self.output_path.write_text(text, encoding="utf-8")


__all__ = ["ChangeRegistry"]
