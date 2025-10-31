"""Tests for requirements module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.core.paths import get_registry_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.lifecycle import STATUS_LIVE, STATUS_PENDING
from supekku.scripts.lib.relations.manager import add_relation
from supekku.scripts.lib.requirements.registry import RequirementsRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry


class RequirementsRegistryTest(unittest.TestCase):
  """Test cases for RequirementsRegistry functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _write_spec(self, root: Path, spec_id: str, body: str) -> None:
    spec_dir = root / "specify" / "tech" / f"{spec_id.lower()}-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter = {
      "id": spec_id,
      "slug": spec_id.lower(),
      "name": f"Spec {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    dump_markdown_file(spec_path, frontmatter, body)
    return spec_path

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()
    body = (
      "# SPEC-001\n\n"
      "## 6. Quality & Operational Requirements\n\n"
      "- FR-001: First functional requirement\n"
      "- NF-020: Non functional requirement\n"
    )
    self._write_spec(root, "SPEC-001", body)
    os.chdir(root)
    return root

  def test_sync_creates_entries(self) -> None:
    """Test that syncing from specs creates registry entries for requirements."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)

    stats = registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )
    registry.save()

    assert stats.created == 2
    assert stats.updated == 0
    assert registry_path.exists()
    records = registry.search()
    assert len(records) == 2
    assert records[0].status == STATUS_PENDING

  def _create_change_bundle(
    self,
    root: Path,
    bundle: str,
    file_id: str,
    kind: str,
  ) -> Path:
    bundle_dir = root / "change" / bundle
    bundle_dir.mkdir(parents=True, exist_ok=True)
    file_path = bundle_dir / f"{file_id}.md"
    frontmatter = {
      "id": file_id,
      "slug": file_id.lower(),
      "name": file_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": kind,
      "relations": [],
    }
    dump_markdown_file(file_path, frontmatter, f"# {file_id}\n")
    return file_path

  def test_sync_collects_change_relations(self) -> None:
    """Test syncing collects relations from delta, revision, audit artifacts."""
    root = self._make_repo()
    delta_path = self._create_change_bundle(
      root,
      "deltas/DE-001-example",
      "DE-001",
      "delta",
    )
    revision_path = self._create_change_bundle(
      root,
      "revisions/RE-001-example",
      "RE-001",
      "revision",
    )
    audit_path = self._create_change_bundle(
      root,
      "audits/AUD-001-example",
      "AUD-001",
      "audit",
    )

    add_relation(delta_path, relation_type="implements", target="SPEC-001.FR-001")
    add_relation(
      revision_path,
      relation_type="introduces",
      target="SPEC-001.FR-001",
    )
    add_relation(audit_path, relation_type="verifies", target="SPEC-001.FR-001")

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
      delta_dirs=[root / "change" / "deltas"],
      revision_dirs=[root / "change" / "revisions"],
      audit_dirs=[root / "change" / "audits"],
    )
    registry.save()

    record = registry.records["SPEC-001.FR-001"]
    assert record.implemented_by == ["DE-001"]
    assert record.introduced == "RE-001"
    assert record.verified_by == ["AUD-001"]

    results = registry.search(implemented_by="DE-001")
    assert [r.uid for r in results] == ["SPEC-001.FR-001"]
    assert [r.uid for r in registry.search(introduced_by="RE-001")] == [
      "SPEC-001.FR-001",
    ]
    assert [r.uid for r in registry.search(verified_by="AUD-001")] == [
      "SPEC-001.FR-001",
    ]

  def test_sync_preserves_status(self) -> None:
    """Test that re-syncing preserves manually set requirement statuses."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )
    registry.set_status("SPEC-001.FR-001", STATUS_LIVE)
    registry.save()

    # re-sync after modifying spec body
    spec_path = root / "specify" / "tech" / "spec-001-example" / "SPEC-001.md"
    text = spec_path.read_text(encoding="utf-8")
    text += "- FR-002: Second requirement\n"
    spec_path.write_text(text, encoding="utf-8")

    registry = RequirementsRegistry(registry_path)
    spec_registry.reload()
    stats = registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )
    registry.save()

    assert stats.created == 1
    assert registry.records["SPEC-001.FR-001"].status == STATUS_LIVE

  def test_search_filters(self) -> None:
    """Test that search can filter requirements by text query."""
    root = self._make_repo()
    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )

    results = registry.search(query="non functional")
    assert len(results) == 1
    assert results[0].label.startswith("NF-")

  def test_move_requirement_updates_primary_spec(self) -> None:
    """Test that moving a requirement updates its primary spec and UID."""
    root = self._make_repo()
    self._write_spec(
      root,
      "SPEC-002",
      "# SPEC-002\n\n- FR-002: Second requirement\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )

    new_uid = registry.move_requirement(
      "SPEC-001.FR-001",
      "SPEC-002",
      spec_registry=spec_registry,
    )
    registry.save()

    assert "SPEC-001.FR-001" not in registry.records
    assert new_uid == "SPEC-002.FR-001"
    moved = registry.records[new_uid]
    assert moved.primary_spec == "SPEC-002"
    assert moved.path == "specify/tech/spec-002-example/SPEC-002.md"

  def test_relationship_block_adds_collaborators(self) -> None:
    """Test that spec relationship blocks add collaborator specs to requirements."""
    root = self._make_repo()
    collaborator_body = """```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-002
requirements:
  primary:
    - SPEC-002.FR-001
  collaborators:
    - SPEC-001.FR-001
interactions: []
```

# SPEC-002

- FR-001: Collab requirement
"""
    self._write_spec(root, "SPEC-002", collaborator_body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    spec_registry.reload()
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )

    record = registry.records["SPEC-001.FR-001"]
    assert record.primary_spec == "SPEC-001"
    assert "SPEC-002" in record.specs
    assert "SPEC-001" in record.specs

  def test_delta_relationships_block_marks_implemented_by(self) -> None:
    """Test that delta relationship blocks mark requirements as implemented."""
    root = self._make_repo()

    delta_dir = root / "change" / "deltas" / "DE-002-example"
    delta_dir.mkdir(parents=True, exist_ok=True)
    delta_path = delta_dir / "DE-002.md"
    frontmatter = {
      "id": "DE-002",
      "slug": "example",
      "name": "Delta – Example",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {"specs": ["SPEC-001"], "requirements": []},
    }
    body = (
      "```yaml supekku:delta.relationships@v1\n"
      "schema: supekku.delta.relationships\n"
      "version: 1\n"
      "delta: DE-002\n"
      "revision_links:\n"
      "  introduces:\n"
      "    - RE-001\n"
      "  supersedes: []\n"
      "specs:\n"
      "  primary:\n"
      "    - SPEC-001\n"
      "  collaborators: []\n"
      "requirements:\n"
      "  implements:\n"
      "    - SPEC-001.FR-001\n"
      "  updates: []\n"
      "  verifies: []\n"
      "phases: []\n"
      "```\n\n"
      "# DE-002 – Example\n"
    )
    dump_markdown_file(delta_path, frontmatter, body)

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
      delta_dirs=[root / "change" / "deltas"],
    )

    record = registry.records["SPEC-001.FR-001"]
    assert "DE-002" in record.implemented_by

  def _write_revision_with_block(
    self,
    root: Path,
    revision_id: str,
    block_yaml: str,
  ) -> Path:
    bundle_dir = root / "change" / "revisions" / f"{revision_id.lower()}-bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    revision_path = bundle_dir / f"{revision_id}.md"
    frontmatter = {
      "id": revision_id,
      "slug": revision_id.lower(),
      "name": revision_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "revision",
    }
    body = f"# {revision_id}\n\n```yaml supekku:revision.change@v1\n{block_yaml}\n```\n"
    dump_markdown_file(revision_path, frontmatter, body)
    return revision_path

  def test_revision_block_moves_requirement_and_sets_collaborators(self) -> None:
    """Test that revision blocks can move requirements and set collaborator specs."""
    root = self._make_repo()
    # Additional specs to support destination/collaborator lookups
    self._write_spec(
      root,
      "SPEC-002",
      "# SPEC-002\n\n- FR-100: Placeholder\n",
    )
    self._write_spec(
      root,
      "SPEC-003",
      "# SPEC-003\n",
    )

    registry_path = get_registry_dir(root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)
    spec_registry = SpecRegistry(root)
    registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
    )
    registry.save()

    block_yaml = """schema: supekku.revision.change
version: 1
metadata:
  revision: RE-002
specs: []
requirements:
  - requirement_id: SPEC-002.FR-001
    kind: functional
    action: move
    origin:
      - kind: requirement
        ref: SPEC-001.FR-001
    destination:
      spec: SPEC-002
      requirement_id: SPEC-002.FR-001
      additional_specs:
        - SPEC-003
    lifecycle:
      status: in-progress
      introduced_by: RE-002
"""
    self._write_revision_with_block(root, "RE-002", block_yaml)

    spec_registry.reload()
    stats = registry.sync_from_specs(
      [root / "specify" / "tech"],
      spec_registry=spec_registry,
      revision_dirs=[root / "change" / "revisions"],
    )
    registry.save()

    assert stats.updated >= 1
    assert "SPEC-001.FR-001" not in registry.records
    record = registry.records["SPEC-002.FR-001"]
    assert record.primary_spec == "SPEC-002"
    assert record.specs == ["SPEC-002", "SPEC-003"]
    assert record.status == "in-progress"
    assert record.introduced == "RE-002"
    assert record.path == "specify/tech/spec-002-example/SPEC-002.md"


if __name__ == "__main__":
  unittest.main()
