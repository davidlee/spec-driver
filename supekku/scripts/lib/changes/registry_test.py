"""Tests for change_registry module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.paths import get_registry_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.relations.manager import add_relation
from supekku.scripts.lib.test_base import RepoTestCase

if TYPE_CHECKING:
  from pathlib import Path


class ChangeRegistryTest(RepoTestCase):
  """Test cases for ChangeRegistry functionality."""

  def _create_repo(self) -> Path:
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_change(
    self,
    root: Path,
    kind: str,
    artifact_id: str,
    relations: list[tuple[str, str]] | None = None,
  ) -> None:
    bundle_dir = root / "change" / kind / f"{artifact_id}-sample"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    path = bundle_dir / f"{artifact_id}.md"
    frontmatter = {
      "id": artifact_id,
      "slug": artifact_id.lower(),
      "name": artifact_id,
      "created": "2024-06-01",
      "updated": "2024-06-02",
      "status": "draft",
      "kind": kind.removesuffix("s"),
      "relations": [],
      "applies_to": {"requirements": ["SPEC-010.FR-001"]},
    }
    dump_markdown_file(path, frontmatter, f"# {artifact_id}\n")
    if relations:
      for relation_type, target in relations:
        add_relation(path, relation_type=relation_type, target=target)

  def test_collect_and_sync_delta_registry(self) -> None:
    """Test collecting and syncing delta artifacts into the registry."""
    root = self._create_repo()
    self._write_change(
      root,
      "deltas",
      "DE-101",
      [("implements", "SPEC-010.FR-001")],
    )

    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()
    assert "DE-101" in artifacts
    artifact = artifacts["DE-101"]
    assert artifact.relations[0]["target"] == "SPEC-010.FR-001"

    registry.sync()
    output = (get_registry_dir(root) / "deltas.yaml").read_text()
    assert "DE-101" in output
    assert "SPEC-010.FR-001" in output


class TestChangeRegistryReverseQueries(RepoTestCase):
  """Test reverse relationship query methods for ChangeRegistry."""

  def _create_repo(self) -> Path:
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_delta_with_requirements(
    self,
    root: Path,
    delta_id: str,
    requirements: list[str],
  ) -> None:
    """Write a delta that implements specific requirements."""
    bundle_dir = root / "change" / "deltas" / f"{delta_id}-sample"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    path = bundle_dir / f"{delta_id}.md"
    frontmatter = {
      "id": delta_id,
      "slug": delta_id.lower(),
      "name": f"Delta {delta_id}",
      "created": "2024-06-01",
      "updated": "2024-06-02",
      "status": "in-progress",
      "kind": "delta",
      "applies_to": {
        "requirements": requirements,
        "specs": [],
      },
    }
    dump_markdown_file(path, frontmatter, f"# {delta_id}\n")

  def test_find_by_implements_single_requirement(self) -> None:
    """Test finding deltas that implement a specific requirement."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["PROD-005.FR-001"])
    self._write_delta_with_requirements(root, "DE-102", ["PROD-005.FR-002"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("PROD-005.FR-001")

    assert isinstance(deltas, list)
    assert len(deltas) == 1
    assert deltas[0].id == "DE-101"

  def test_find_by_implements_multiple_deltas_same_requirement(self) -> None:
    """Test finding multiple deltas implementing same requirement."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["PROD-010.FR-004"])
    self._write_delta_with_requirements(root, "DE-102", ["PROD-010.FR-004", "PROD-010.FR-005"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("PROD-010.FR-004")

    assert isinstance(deltas, list)
    assert len(deltas) == 2
    delta_ids = {d.id for d in deltas}
    assert "DE-101" in delta_ids
    assert "DE-102" in delta_ids

  def test_find_by_implements_spec_requirement(self) -> None:
    """Test finding deltas implementing SPEC requirements."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["SPEC-110.FR-001"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("SPEC-110.FR-001")

    assert isinstance(deltas, list)
    assert len(deltas) == 1
    assert deltas[0].id == "DE-101"

  def test_find_by_implements_nonexistent_requirement(self) -> None:
    """Test finding deltas for non-existent requirement returns empty list."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["PROD-005.FR-001"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("NONEXISTENT.FR-999")

    assert isinstance(deltas, list)
    assert len(deltas) == 0

  def test_find_by_implements_none(self) -> None:
    """Test find_by_implements with None returns empty list."""
    root = self._create_repo()

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements(None)

    assert isinstance(deltas, list)
    assert len(deltas) == 0

  def test_find_by_implements_empty_string(self) -> None:
    """Test find_by_implements with empty string returns empty list."""
    root = self._create_repo()

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("")

    assert isinstance(deltas, list)
    assert len(deltas) == 0

  def test_find_by_implements_returns_change_artifact_objects(self) -> None:
    """Test that find_by_implements returns proper ChangeArtifact objects."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["PROD-005.FR-001"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    deltas = registry.find_by_implements("PROD-005.FR-001")

    assert len(deltas) == 1
    delta = deltas[0]

    # Verify delta has expected attributes from ChangeArtifact
    assert delta.id == "DE-101"
    assert hasattr(delta, "metadata")
    assert hasattr(delta, "status")
    assert delta.status == "in-progress"

  def test_find_by_implements_case_sensitive(self) -> None:
    """Test that requirement ID matching is case-sensitive."""
    root = self._create_repo()
    self._write_delta_with_requirements(root, "DE-101", ["PROD-005.FR-001"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    # Correct case
    deltas_upper = registry.find_by_implements("PROD-005.FR-001")
    # Wrong case
    deltas_lower = registry.find_by_implements("prod-005.fr-001")

    assert len(deltas_upper) == 1
    assert len(deltas_lower) == 0

  def test_find_by_implements_filters_by_status(self) -> None:
    """Test that find_by_implements can be combined with status filtering."""
    root = self._create_repo()

    # Create deltas with different statuses
    bundle_dir = root / "change" / "deltas" / "DE-101-sample"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    path = bundle_dir / "DE-101.md"
    frontmatter = {
      "id": "DE-101",
      "slug": "de-101",
      "name": "Delta DE-101",
      "created": "2024-06-01",
      "updated": "2024-06-02",
      "status": "completed",
      "kind": "delta",
      "applies_to": {"requirements": ["PROD-005.FR-001"], "specs": []},
    }
    dump_markdown_file(path, frontmatter, "# DE-101\n")

    self._write_delta_with_requirements(root, "DE-102", ["PROD-005.FR-001"])

    registry = ChangeRegistry(root=root, kind="delta")
    registry.sync()

    # Get all deltas implementing requirement
    all_deltas = registry.find_by_implements("PROD-005.FR-001")
    assert len(all_deltas) == 2

    # Filter to only in-progress deltas
    in_progress = [d for d in all_deltas if d.status == "in-progress"]
    assert len(in_progress) == 1
    assert in_progress[0].id == "DE-102"


if __name__ == "__main__":
  unittest.main()
